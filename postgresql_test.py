import psycopg2

try:
    conn = psycopg2.connect(
        dbname="openpanda",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )
    print("✅ Connexion réussie à la base PostgreSQL !")
    conn.close()
except Exception as e:
    print(f"❌ Échec de connexion : {e}")
