"""Continuous read/write load against SAP HANA Express.

Generates activity that shows up in the Middleware SAP HANA integration:
column store growth and compression, connection counts, transaction volume,
service memory movement, and a mix of query shapes with very different costs.

Three kinds of worker run concurrently:

  writer  - batch INSERTs into DEMO.SALES_ORDERS (a COLUMN table)
  reader  - mixed query shapes: aggregation, top-N, point lookup, full scan
  sampler - polls SYS.M_CS_TABLES and logs column store sizing

Every worker owns its own HANA connection. hdbcli connections are not
thread-safe, and sharing one across threads produces interleaved protocol
frames that surface as spurious "invalid message type" errors.
"""

import logging
import os
import random
import signal
import threading
import time
from datetime import datetime, timedelta

from hdbcli import dbapi

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s [%(threadName)s] %(message)s",
)
log = logging.getLogger("loadgen")

HANA_HOST = os.environ.get("HANA_HOST", "hxe")
# 39013 is the SYSTEMDB entry point; the nameserver redirects to the tenant's
# real SQL port when databaseName is supplied.
HANA_PORT = int(os.environ.get("HANA_PORT", "39013"))
HANA_DATABASE = os.environ.get("HANA_DATABASE", "HXE")
HANA_USER = os.environ.get("HANA_USER", "SYSTEM")
HANA_PASSWORD = os.environ.get("HANA_PASSWORD", "HXEHana1")

WRITER_THREADS = int(os.environ.get("WRITER_THREADS", "2"))
READER_THREADS = int(os.environ.get("READER_THREADS", "2"))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "500"))
CS_SAMPLE_INTERVAL = int(os.environ.get("CS_SAMPLE_INTERVAL", "30"))

SCHEMA = "DEMO"
TABLE = "SALES_ORDERS"

shutdown = threading.Event()

REGIONS = ["EMEA", "APAC", "NA", "LATAM"]
CHANNELS = ["WEB", "RETAIL", "PARTNER", "DIRECT"]
STATUSES = ["OPEN", "SHIPPED", "INVOICED", "CANCELLED"]
PRODUCTS = [f"SKU-{i:05d}" for i in range(1, 501)]
CUSTOMERS = [f"CUST-{i:06d}" for i in range(1, 5001)]


def connect(label):
    """Open a HANA connection, retrying until it succeeds or we shut down.

    Even behind a healthcheck, HANA can refuse connections for a short window
    while the tenant finishes opening, so this retries rather than crashlooping.
    """
    attempt = 0
    while not shutdown.is_set():
        attempt += 1
        try:
            conn = dbapi.connect(
                address=HANA_HOST,
                port=HANA_PORT,
                # Without databaseName the driver stays on SYSTEMDB and the
                # DEMO schema would be created in the wrong database.
                databaseName=HANA_DATABASE,
                user=HANA_USER,
                password=HANA_PASSWORD,
                autocommit=True,
            )
            log.info("%s connected to %s:%s db=%s",
                     label, HANA_HOST, HANA_PORT, HANA_DATABASE)
            return conn
        except Exception as exc:  # noqa: BLE001 - want any driver error here
            delay = min(30, 2 * attempt)
            log.warning("%s connect attempt %d failed (%s); retry in %ds",
                        label, attempt, exc, delay)
            shutdown.wait(delay)
    return None


def reconnect(old_conn, label):
    """Replace a connection that has errored out."""
    try:
        old_conn.close()
    except Exception:  # noqa: BLE001 - closing a dead connection can throw
        pass
    conn = connect(label)
    if conn is None:
        return None, None
    return conn, conn.cursor()


def ensure_schema():
    """Create the DEMO schema and COLUMN table if they do not exist.

    HANA has no CREATE ... IF NOT EXISTS for schemas, so we catch the
    already-exists errors (SQL error 386 / 288) rather than pre-checking.
    """
    conn = connect("bootstrap")
    if conn is None:
        return
    cur = conn.cursor()

    try:
        cur.execute(f"CREATE SCHEMA {SCHEMA}")
        log.info("created schema %s", SCHEMA)
    except dbapi.Error as exc:
        if "386" in str(exc) or "existing" in str(exc).lower():
            log.info("schema %s already exists", SCHEMA)
        else:
            raise

    # COLUMN STORE is the point of the demo: it is what populates
    # M_CS_TABLES and drives the saphana.schema.* / column memory metrics.
    ddl = f"""
        CREATE COLUMN TABLE {SCHEMA}.{TABLE} (
            ORDER_ID      BIGINT        NOT NULL,
            ORDER_TS      TIMESTAMP     NOT NULL,
            CUSTOMER_ID   NVARCHAR(16)  NOT NULL,
            PRODUCT_SKU   NVARCHAR(16)  NOT NULL,
            REGION        NVARCHAR(8)   NOT NULL,
            CHANNEL       NVARCHAR(16)  NOT NULL,
            STATUS        NVARCHAR(16)  NOT NULL,
            QUANTITY      INTEGER       NOT NULL,
            UNIT_PRICE    DECIMAL(12,2) NOT NULL,
            NET_AMOUNT    DECIMAL(14,2) NOT NULL,
            PRIMARY KEY (ORDER_ID)
        )
    """
    try:
        cur.execute(ddl)
        log.info("created COLUMN table %s.%s", SCHEMA, TABLE)
    except dbapi.Error as exc:
        if "288" in str(exc) or "existing" in str(exc).lower():
            log.info("table %s.%s already exists", SCHEMA, TABLE)
        else:
            raise

    cur.close()
    conn.close()


def next_order_id(conn):
    """Continue the ID sequence across restarts so we never collide on the PK."""
    cur = conn.cursor()
    cur.execute(f"SELECT COALESCE(MAX(ORDER_ID), 0) FROM {SCHEMA}.{TABLE}")
    current = cur.fetchone()[0]
    cur.close()
    return int(current) + 1


def make_row(order_id, base_ts):
    qty = random.randint(1, 40)
    price = round(random.uniform(5.0, 900.0), 2)
    return (
        order_id,
        base_ts - timedelta(seconds=random.randint(0, 86400)),
        random.choice(CUSTOMERS),
        random.choice(PRODUCTS),
        random.choice(REGIONS),
        random.choice(CHANNELS),
        random.choice(STATUSES),
        qty,
        price,
        round(qty * price, 2),
    )


def writer_worker(idx):
    """Insert batches continuously."""
    conn = connect(f"writer-{idx}")
    if conn is None:
        return
    cur = conn.cursor()

    # Stagger each writer's ID range so concurrent writers never contend on
    # the same primary key values.
    order_id = next_order_id(conn) + idx * 10_000_000
    sql = (f"INSERT INTO {SCHEMA}.{TABLE} "
           f"(ORDER_ID, ORDER_TS, CUSTOMER_ID, PRODUCT_SKU, REGION, CHANNEL, "
           f"STATUS, QUANTITY, UNIT_PRICE, NET_AMOUNT) "
           f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

    while not shutdown.is_set():
        base_ts = datetime.now()
        rows = [make_row(order_id + n, base_ts) for n in range(BATCH_SIZE)]
        started = time.perf_counter()
        try:
            cur.executemany(sql, rows)
            elapsed_ms = (time.perf_counter() - started) * 1000
            order_id += BATCH_SIZE
            rows_per_sec = BATCH_SIZE / max(elapsed_ms / 1000, 1e-6)
            log.info("inserted batch of %d in %.0f ms (%.0f rows/s, next id %d)",
                     BATCH_SIZE, elapsed_ms, rows_per_sec, order_id)
        except dbapi.Error as exc:
            log.error("insert failed: %s", exc)
            conn, cur = reconnect(conn, f"writer-{idx}")
            if conn is None:
                return
            order_id = next_order_id(conn) + idx * 10_000_000

        shutdown.wait(random.uniform(0.2, 1.0))

    cur.close()
    conn.close()


# Mixed query shapes. Each is (name, sql, needs_random_param).
QUERIES = [
    (
        "aggregation",
        f"SELECT REGION, CHANNEL, COUNT(*) AS ORDERS, SUM(NET_AMOUNT) AS REVENUE "
        f"FROM {SCHEMA}.{TABLE} GROUP BY REGION, CHANNEL",
        False,
    ),
    (
        "top_n",
        f"SELECT TOP 20 PRODUCT_SKU, SUM(QUANTITY) AS UNITS "
        f"FROM {SCHEMA}.{TABLE} GROUP BY PRODUCT_SKU ORDER BY UNITS DESC",
        False,
    ),
    (
        "point_lookup",
        f"SELECT ORDER_ID, CUSTOMER_ID, NET_AMOUNT, STATUS "
        f"FROM {SCHEMA}.{TABLE} WHERE CUSTOMER_ID = ?",
        True,
    ),
    (
        # Deliberately heavy: no index help, forces a full column scan with a
        # computed predicate. This is what makes CPU and scan metrics move.
        "full_scan",
        f"SELECT COUNT(*), AVG(NET_AMOUNT), MAX(UNIT_PRICE * QUANTITY) "
        f"FROM {SCHEMA}.{TABLE} WHERE NET_AMOUNT > (SELECT AVG(NET_AMOUNT) "
        f"FROM {SCHEMA}.{TABLE})",
        False,
    ),
]


def reader_worker(idx):
    """Run mixed query shapes, timing each one."""
    conn = connect(f"reader-{idx}")
    if conn is None:
        return
    cur = conn.cursor()

    while not shutdown.is_set():
        # Full scan is heavy, so run it less often than the cheap shapes —
        # weights keep the mix realistic rather than scan-dominated.
        name, sql, needs_param = random.choices(
            QUERIES, weights=[3, 3, 5, 1], k=1
        )[0]
        started = time.perf_counter()
        try:
            if needs_param:
                cur.execute(sql, (random.choice(CUSTOMERS),))
            else:
                cur.execute(sql)
            rows = cur.fetchall()
            elapsed_ms = (time.perf_counter() - started) * 1000
            log.info("query %-12s -> %4d rows in %7.1f ms",
                     name, len(rows), elapsed_ms)
        except dbapi.Error as exc:
            log.error("query %s failed: %s", name, exc)
            conn, cur = reconnect(conn, f"reader-{idx}")
            if conn is None:
                return

        shutdown.wait(random.uniform(0.5, 2.0))

    cur.close()
    conn.close()


def cs_sampler():
    """Sample SYS.M_CS_TABLES and log column store sizing.

    MEMORY_SIZE_IN_TOTAL / RECORD_COUNT is the headline compression number: as
    HANA merges delta into the main store and re-optimises the dictionary, it
    trends down in a sawtooth. Useful for sanity-checking the schema memory
    metrics the integration reports.
    """
    conn = connect("cs-sampler")
    if conn is None:
        return
    cur = conn.cursor()

    sql = """
        SELECT SCHEMA_NAME, TABLE_NAME, MEMORY_SIZE_IN_TOTAL,
               RECORD_COUNT, RAW_RECORD_COUNT_IN_DELTA
        FROM SYS.M_CS_TABLES
        WHERE SCHEMA_NAME = ?
    """

    while not shutdown.is_set():
        try:
            cur.execute(sql, (SCHEMA,))
            for schema, table, mem_bytes, records, delta_records in cur.fetchall():
                mem_bytes = int(mem_bytes or 0)
                records = int(records or 0)
                delta_records = int(delta_records or 0)

                # Guard the divide: the table has zero rows on first boot.
                if records > 0:
                    bpr = mem_bytes / records
                    log.info("cs_tables %s.%s mem=%d bytes records=%d delta=%d "
                             "bytes/record=%.2f",
                             schema, table, mem_bytes, records, delta_records, bpr)
                else:
                    log.info("cs_tables %s.%s mem=%d bytes records=0 (no bpr yet)",
                             schema, table, mem_bytes)
        except dbapi.Error as exc:
            log.error("M_CS_TABLES sample failed: %s", exc)
            conn, cur = reconnect(conn, "cs-sampler")
            if conn is None:
                return

        shutdown.wait(CS_SAMPLE_INTERVAL)

    cur.close()
    conn.close()


def handle_signal(signum, _frame):
    log.info("received signal %d, shutting down", signum)
    shutdown.set()


def main():
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    ensure_schema()

    threads = []
    for i in range(WRITER_THREADS):
        threads.append(threading.Thread(target=writer_worker, args=(i,),
                                        name=f"writer-{i}", daemon=True))
    for i in range(READER_THREADS):
        threads.append(threading.Thread(target=reader_worker, args=(i,),
                                        name=f"reader-{i}", daemon=True))
    threads.append(threading.Thread(target=cs_sampler, name="cs-sampler",
                                    daemon=True))

    for t in threads:
        t.start()
    log.info("started %d writer(s), %d reader(s), 1 cs-sampler",
             WRITER_THREADS, READER_THREADS)

    while not shutdown.is_set():
        shutdown.wait(1)
    for t in threads:
        t.join(timeout=10)
    log.info("loadgen stopped")


if __name__ == "__main__":
    main()
