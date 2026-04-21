import oracledb
from config import credenciais

def inserir_registro(maquina, v, r, c, esp, real, perda):
    """CREATE: Insere no banco os dados da telemetria e o prejuízo"""
    try:
        conn = oracledb.connect(**credenciais)
        cursor = conn.cursor()
        sql = """INSERT INTO registros_colheita
                 (id_maquina, velocidade_real, rotacao_real, altura_real,
                  ton_esperada, ton_realizada, perda_percentual)
                 VALUES (:1, :2, :3, :4, :5, :6, :7)"""
        cursor.execute(sql, (maquina, v, r, c, esp, real, perda))
        conn.commit()
        print("✅ Registro salvo no Oracle.")
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


def listar_historico():
    """READ: Consulta os registros salvos"""
    try:
        conn = oracledb.connect(**credenciais)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_maquina, perda_percentual, data_hora "
            "FROM registros_colheita ORDER BY data_hora DESC"
        )
        return cursor.fetchall()
    except Exception:
        return []
    finally:
        if 'conn' in locals():
            conn.close()
