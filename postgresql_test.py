import psycopg2

try:
    conn = psycopg2.connect(
        dbname="openpanda",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )
    print("✅ Successfully connected to PostgreSQL database!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
