import random
import threading
import oracledb
import json
import time


def check_table_exists(connection, table_name):
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT table_name FROM user_tables WHERE table_name = :table_name", {'table_name': table_name})
        row = cursor.fetchone()
        return row is not None
    except oracledb.DatabaseError as err:
        # Handle potential errors during table existence check (e.g., insufficient privileges)
        print(f"Error checking table existence: {err}")
        return False


def select_data(db_config, table_name, sleep_time):
    connection = None
    try:
        # Connect to the database
        connection = oracledb.connect(user=db_config['username'], password=db_config['password'], host=db_config['host'], port=db_config['port'], service_name=db_config['service_name'])
        cursor = connection.cursor()

        if not check_table_exists(connection, table_name):
            print(f"Table '{table_name}' does not exist on {db_config['host']}. Skipping data selection.")
            return

        employeeid = random.randint(1001, 10000)
        cursor.execute(f"SELECT * FROM {table_name} WHERE ID = {employeeid}")
        # Optionally fetch and process results here (if needed)
        time.sleep(sleep_time)  # Optional sleep between reads (seconds)

        print(f"Successfully performed reads from {table_name} on {db_config['host']}")
    except oracledb.DatabaseError as err:
        print(f"Error selecting data: {err}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    # Load database configurations from credentials.json
    with open('/scripts/config.json') as f:
        db_configs = json.load(f)

    # Adjust these parameters as needed
    table_name = 'EMPLOYEES'
    sleep_time = 1  # Optional sleep time between database connections (seconds)

    threads = []
    for db_name, db_config in db_configs.items():
        thread = threading.Thread(target=select_data, args=(db_config, table_name, sleep_time))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Data selection completed for all databases.")
