import oracledb

try:
    # No Mac/Docker, usamos o modo 'thin' (mais leve, não precisa de Instant Client)
    conn = oracledb.connect(
        user="system",
        password="admin123",
        dsn="localhost:1521/xe"
    )
    print("🚀 Sucesso! conectado ao Oracle no Docker.")
    conn.close()
except Exception as e:
    print(f"❌ Erro na conexão: {e}")