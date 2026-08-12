# SAP HANA Load Generator

This project runs **SAP HANA Express** in Docker and generates continuous
database load with a Python script, so the
[Middleware SAP HANA integration](https://docs.middleware.io/integrations/saphana-integration)
has real activity to report.

---

## 📦 Requirements

- Docker & Docker Compose
- GNU Make
- **~10 GB disk and 8 GB RAM free.** SAP HANA Express is heavyweight — the
  image alone is 4.5 GB on disk and the running instance uses ~5 GB RSS.
- **x86-64 host.** SAP HANA ships x86-64 only. It will run on arm64 under
  emulation, but very slowly.
- MW Host Agent `v1.21.3` or later. Earlier agents save the integration
  successfully but never receive a collection config.

---

## 🚀 Project Setup

```bash
git clone https://github.com/middleware-labs/integration-demo-projects.git
cd integration-demo-projects/saphana
make all   # starts HANA, waits for it, creates the monitoring user
```

> ⏳ **First boot takes about 10 minutes.** HANA initialises persistence,
> generates PKI/SSFS keys, and creates the tenant on its first run only.
> `make all` blocks until it is healthy. Subsequent boots are much faster.

Watch progress at any time with `make logs`.

Once it finishes, the load generator is already running and inserting rows.

### Available commands

| Command | What it does |
|---|---|
| `make up` | Start HANA + load generator |
| `make wait` | Block until HANA reports healthy |
| `make monitoring-user` | Create the restricted monitoring user (Steps 1–3 of the docs) |
| `make ports` | Show the **real** SQL ports, queried from HANA |
| `make verify` | Prove the monitoring user can read the views, and show demo data |
| `make psql` | Interactive `hdbsql` shell against the tenant |
| `make logs` | Tail container logs |
| `make down` | Stop and remove containers **and the data volume** |

---

## 🔌 Configuring the Middleware integration

### Agent target: `<host>:39041`

In Middleware go to **Installations → All Integrations → Database → SAP HANA**,
select the host running the agent, and add one endpoint:

| Field | Value |
|---|---|
| Name | `saphana-demo` |
| Endpoint URL | `<host>:39041` |
| Username | `OTEL_MONITORING_USER` |
| Password | `HXEHana1` |
| Collection Interval | `10s` |

Then **Save Configuration**.

### ⚠️ Point at `39041`, not `39013`

This is the single easiest thing to get wrong.

| Port | What it is |
|---|---|
| `39013` | SYSTEMDB external SQL entry point — for `hdbsql` and port discovery |
| `39017` | SYSTEMDB nameserver SQL port |
| **`39041`** | **HXE tenant indexserver — this is the agent endpoint** |
| `39015` | **Not in use on this build**, despite being the commonly cited default |

The agent reads only the plain `SYS.*` views of whichever database it connects
to, and it has no database-name setting — it picks the database purely by
port. An endpoint aimed at SYSTEMDB **connects successfully and reports no
error**, but collects the nameserver's own near-empty metrics instead of your
tenant's workload.

Interactive clients like `hdbsql` can connect to 39013 and name a tenant to be
redirected; the agent cannot, because it builds a bare connection string.

These ports were read from the running instance, not assumed. Re-check them
yourself at any time:

```bash
make ports
```

```
DATABASE_NAME  SERVICE_NAME  SQL_PORT
HXE            indexserver   39041
SYSTEMDB       nameserver    39017
```

---

## 🔐 The monitoring user

`make monitoring-user` applies `setup_monitoring_user.sql` to the **tenant**,
which implements Steps 1–3 of the integration docs:

1. `CREATE RESTRICTED USER ... NO FORCE_FIRST_PASSWORD_CHANGE` — without that
   clause HANA demands a password change on first login, which an unattended
   agent cannot perform, so **every** connection fails.
2. `ENABLE CLIENT CONNECT` + `RESTRICTED_USER_JDBC_ACCESS` — a restricted user
   has no SQL connectivity at all until these are granted.
3. A read-only `OTEL_MONITORING` role with `CATALOG READ` plus `SELECT` on the
   19 monitoring views the integration queries.

Confirm it worked:

```bash
make verify
```

That connects **as** `OTEL_MONITORING_USER` and counts rows in the views. A
grant that never applied shows up there as an authorization error on that
specific view, rather than as a silently missing metric later.

> **Password characters matter.** The agent passes the password inside a
> connection URL that gets percent-decoded, so avoid
> `/ ? # % < > [ ] { } | \ ^ ` " ` and spaces. `@` and `:` are safe. `%` is the
> worst offender because it fails *silently* — `%41` decodes to `A`, so the
> agent authenticates with a password you never set. The default here
> (`HXEHana1`) is deliberately alphanumeric.

To change the password, edit `password.json` **and** the value in
`setup_monitoring_user.sql`, then `make down && make all`.

---

## 📊 What the load generator does

`load-generator/main.py` runs five threads against a **column store** table,
`DEMO.SALES_ORDERS`:

- **2 writers** — batch INSERTs of 500 rows (~1,500 rows/sec combined)
- **2 readers** — four query shapes with deliberately different costs:
  aggregation, top-N, point lookup, and a heavy full scan
- **1 sampler** — polls `SYS.M_CS_TABLES` every 30s and logs column store
  memory, record count, delta records, and bytes-per-record

The column store is the point: as HANA merges the delta store into main and
re-optimises the dictionary, bytes-per-record falls in a sawtooth. That is
visible in the sampler log lines and in the `saphana.schema.*` and
`saphana.column.memory.used` metrics.

```bash
docker compose logs -f loadgen
```

```
inserted batch of 500 in 19 ms (26316 rows/s, next id 20242001)
query point_lookup ->  101 rows in     5.2 ms
query full_scan    ->    1 rows in  1471.6 ms
cs_tables DEMO.SALES_ORDERS mem=29981034 bytes records=659500 delta=66500 bytes/record=45.46
```

Tune via environment variables in `docker-compose.yaml`: `WRITER_THREADS`,
`READER_THREADS`, `BATCH_SIZE`, `CS_SAMPLE_INTERVAL`.

---

## 🗄️ Database viewer tools

Connect DBeaver or DataGrip using the SAP HANA driver:

- **Host:** `localhost`, **Port:** `39013`, **Database:** `HXE`
- **User:** `SYSTEM`, **Password:** `HXEHana1`

---

## 🧯 Troubleshooting

**`hdbsql` says "Single Sign-On authentication failed" but the password is right.**
`hdbsql` needs `-d <database>`. Without it the client ignores `-p` entirely and
attempts SSO. The error never mentions the missing database. Always pass
`-d SYSTEMDB` or `-d HXE`.

**`incorrect syntax near "EATE"` followed by `invalid user name` errors.**
Two separate `hdbsql -I` quirks, both handled by `make monitoring-user`:
`-I` treats `--` comment lines as statements, and piping into `-I /dev/stdin`
eats the first two bytes of the stream (so `CREATE` arrives as `EATE`). The
`CREATE USER` then never runs and every following `GRANT` fails. The target
strips comments and copies a real file into the container instead of piping.

**`make monitoring-user` prints "user name already exists".**
Harmless — it means the user was created on an earlier run. The grants are
re-applied regardless and the target still exits 0. Confirm with `make verify`.

**Container exits immediately with `write /proc/sys/kernel/shmmni: invalid argument`.**
The kernel hard-caps `shmmni` at 32768 unless booted with `ipcmni_extend`. The
compose file already sets 32768; don't raise it.

**HANA aborts with `curl: (37) Couldn't open file /hana/password.json`.**
The entrypoint drops to uid 12000 before reading that file, so it must be
world-readable: `chmod 644 password.json`.

**Metrics arrive but look empty or unrelated to the load.**
The endpoint is pointed at SYSTEMDB rather than the tenant. Use `39041`.

**No metrics at all after saving the integration.**
Check the agent version — SAP HANA config is only generated for `v1.21.3`+.

**Startup warns that `move_pages` / `mbind` are not permitted.**
Handled by `cap_add: [SYS_NICE]` in the compose file. These are warnings; boot
continues either way.

**First boot seems stuck.** Give it the full 10 minutes and watch
`make logs` for `Startup finished!`. HANA emits little output for long
stretches during persistence init.
