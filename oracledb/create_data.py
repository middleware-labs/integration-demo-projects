import string
import threading
import time
import oracledb
import json
import random


def create_table(connection, table_name):
    # Replace with your actual CREATE TABLE statement, including data types and constraints
    sql = f"""
    CREATE TABLE {table_name} (
        id NUMBER,
        name VARCHAR2(50),
        age NUMBER
    )
    """
    cursor = connection.cursor()
    try:
        cursor.execute(sql)
        connection.commit()
        print(f"Table '{table_name}' created successfully.")
    except oracledb.DatabaseError as err:
        # Handle potential errors during table creation
        print(f"Error creating table: {err}")


def check_table_exists(connection, table_name):
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT table_name FROM user_tables WHERE table_name = :table_name", {'table_name': table_name})
        row = cursor.fetchone()
        return row is not None
    except oracledb.DatabaseError as err:
        # Handle potential errors during table existence check
        print(f"Error checking table existence: {err}")
        return False


def generate_data(db_config, table_name, num_rows, sleep_time):
    connection = None
    try:
        connection = oracledb.connect(user=db_config['username'], password=db_config['password'],
                                      host=db_config['host'], port=db_config['port'],
                                      service_name=db_config['service_name'])

        if not check_table_exists(connection, table_name):
            create_table(connection, table_name)  # Create table if it doesn't exist

        # Sample data generation (replace with your actual data structure)
        for _ in range(num_rows):
            id = random.randint(1, 1000)
            name = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10)))
            age = random.randint(20, 60)
            sql = f"INSERT INTO {table_name} (id, name, age) VALUES (:id, :name, :age)"
            cursor = connection.cursor()
            cursor.execute(sql, {'id': id, 'name': name, 'age': age})

        connection.commit()
        print(f"Successfully generated {num_rows} rows for {table_name} on {db_config['host']}")
    except oracledb.DatabaseError as err:
        print(f"Error generating data: {err}")
    finally:
        if connection:
            connection.close()
        time.sleep(sleep_time)  # Optional sleep between threads


if __name__ == "__main__":
    # Load database configurations from config.json
    with open('/scripts/config.json') as f:
        # with open('config.json') as f:
        db_configs = json.load(f)

    # Adjust these parameters as needed
    table_name = 'EMPLOYEES'
    sleep_time = 1  # Optional sleep time between database connections (seconds)

    threads = []
    for db_name, db_config in db_configs.items():
        thread = threading.Thread(target=generate_data,
                                  args=(db_config, table_name, random.randint(50000, 500000), sleep_time))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Data generation completed for all databases.")
