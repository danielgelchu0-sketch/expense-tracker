import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("Error: DATABASE_URL not set. Run this on Render or set env variable.")
    exit(1)

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id SERIAL PRIMARY KEY,
        date TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL
    )
''')

conn.commit()
cursor.close()
conn.close()

print("Database initialized successfully on PostgreSQL!")