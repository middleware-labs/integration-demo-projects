import pyodbc
import time
from faker import Faker

SERVER = 'mssql-db-host'
DATABASE = 'master'
USERNAME = 'sa'
PASSWORD = 'Admin@123'
DRIVER = 'ODBC Driver 17 for SQL Server'

CONN_STR = f'DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

MAX_RETRIES = 10

# Retry logic to wait for SQL Server to be ready
for attempt in range(MAX_RETRIES):
    try:
        conn = pyodbc.connect(CONN_STR, timeout=5)
        print("✅ Connected to SQL Server")
        break
    except pyodbc.Error as e:
        print(f"⏳ Waiting for SQL Server... (attempt {attempt + 1}/{MAX_RETRIES})")
        time.sleep(5)
else:
    print("❌ Could not connect to SQL Server after retries")
    raise SystemExit(1)

cursor = conn.cursor()

# Create table and insert fake data
cursor.execute('''
    IF NOT EXISTS (
        SELECT * FROM sysobjects WHERE name='users' and xtype='U'
    )
    CREATE TABLE users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(100),
        email NVARCHAR(100),
        address NVARCHAR(255)
    )
''')
conn.commit()

fake = Faker()
for _ in range(10):
    cursor.execute("INSERT INTO users (name, email, address) VALUES (?, ?, ?)",
                   fake.name(), fake.email(), fake.address())
conn.commit()
conn.close()
print("✅ Inserted fake users successfully.")
