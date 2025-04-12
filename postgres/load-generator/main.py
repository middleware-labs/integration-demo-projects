import psycopg2
import time
import random

def generate_load():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5432
    )
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS demo_load (
        id SERIAL PRIMARY KEY,
        value INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)
    conn.commit()

    print("Generating load... Press Ctrl+C to stop.")
    try:
        while True:
            val = random.randint(1, 1000)
            cursor.execute("INSERT INTO demo_load (value) VALUES (%s);", (val,))
            cursor.execute("SELECT COUNT(*) FROM demo_load;")
            count = cursor.fetchone()[0]
            print(f"Inserted value: {val}, Total rows: {count}")
            conn.commit()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping load generation...")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    generate_load()
