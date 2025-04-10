import os
import time
import psycopg2
from psycopg2.extras import execute_values
import random
from datetime import datetime

# DB config from env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "testdb")
DB_USER = os.getenv("DB_USER", "testuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "testpass")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS load_test (
                id SERIAL PRIMARY KEY,
                value INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()

def insert_fake_data(conn, count=100):
    values = [(random.randint(1, 1000), datetime.now()) for _ in range(count)]
    with conn.cursor() as cur:
        execute_values(cur,
            "INSERT INTO load_test (value, created_at) VALUES %s",
            values
        )
        conn.commit()

def main():
    while True:
        try:
            conn = get_connection()
            print("Connected to DB.")
            create_table(conn)

            while True:
                insert_fake_data(conn, count=100)
                print("Inserted 100 rows.")
                time.sleep(5)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
        finally:
            try:
                conn.close()
            except:
                pass

if __name__ == "__main__":
    main()
