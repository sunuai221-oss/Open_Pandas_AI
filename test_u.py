import psycopg2

try:
    conn = psycopg2.connect(
        dbname="openpandaai",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )
    print("✅ Connexion réussie à la base PostgreSQL !")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS test_utf8 (id SERIAL PRIMARY KEY, val TEXT);")
    cur.execute("INSERT INTO test_utf8 (val) VALUES ('test')")
    conn.commit()
    cur.execute("SELECT * FROM test_utf8;")
    print(cur.fetchall())
    conn.close()
except Exception as e:
    print(f"❌ {type(e).__name__}: {e}")
