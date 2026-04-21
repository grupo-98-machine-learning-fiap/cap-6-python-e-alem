import oracledb
import json
import os
from datetime import datetime

# --- 1. CONFIGURAÇÕES E ESTADO DO SISTEMA ---
credenciais = {
    "user": "system",
    "password": "admin123",
    "dsn": "localhost:1521/xe"
}

# --- 2. SUBALGORITMOS: FUNÇÕES TÉCNICAS ---

def validar_float(mensagem):
    """Garante consistência: impede que o programa quebre com letras."""
    while True:
        try:
            return float(input(mensagem))
        except ValueError:
            print("❌ Erro: Digite apenas números (use ponto para decimais).")

def gerar_diagnostico(v, r, c):
    """
    Procedimento de Resolução de Perda.
    Retorna uma Tupla (Lista_de_Ações, Status)
    """
    acoes = []
    # Parâmetros baseados na dor de 15% de perda
    if v > 5.0: acoes.append("Reduzir velocidade para 5km/h")
    if r > 800: acoes.append("Diminuir rotação do extrator")
    if c > 5.0: acoes.append("Ajustar facas do corte de base (Baixar)")
    
    status = "CRÍTICO" if len(acoes) > 0 else "OTIMIZADO"
    return (acoes, status)

# --- 3. PERSISTÊNCIA: CRUD NO ORACLE ---

def inserir_registro(maquina, v, r, c, esp, real, perda):
    """CREATE: Insere no banco os dados da telemetria e o prejuízo"""
    try:
        conn = oracledb.connect(**credenciais)
        cursor = conn.cursor()
        sql = """INSERT INTO registros_colheita 
                 (id_maquina, velocidade_real, rotacao_real, altura_real, ton_esperada, ton_realizada, perda_percentual) 
                 VALUES (:1, :2, :3, :4, :5, :6, :7)"""
        cursor.execute(sql, (maquina, v, r, c, esp, real, perda))
        conn.commit()
        print("✅ Registro salvo no Oracle.")
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")
    finally:
        if 'conn' in locals(): conn.close()

def listar_historico():
    """READ: Consulta os registros salvos"""
    try:
        conn = oracledb.connect(**credenciais)
        cursor = conn.cursor()
        cursor.execute("SELECT id_maquina, perda_percentual, data_hora FROM registros_colheita ORDER BY data_hora DESC")
        return cursor.fetchall()
    except Exception as e:
        return []
    finally:
        if 'conn' in locals(): conn.close()

# --- 4. MANIPULAÇÃO DE ARQUIVOS (JSON/TXT) ---

def salvar_log_json(dados):
    """Escrita de arquivos: salva a última intervenção em JSON"""
    with open("ultima_analise.json", "w") as f:
        json.dump(dados, f, indent=4)

def apagar_arquivos_locais():
    """Delete de arquivos locais"""
    if os.path.exists("ultima_analise.json"):
        os.remove("ultima_analise.json")
        print("🗑️ Arquivo JSON removido.")

# --- 5. MENU PRINCIPAL (INTERFACE) ---

def menu():
    while True:
        print(f"\n{'='*15} FARMTECH SOLUTIONS {'='*15}")
        print("1. Analisar Telemetria e Resolver Perdas (Create)")
        print("2. Ver Histórico de Colheitas (Read - Oracle)")
        print("3. Limpar Arquivos de Log (Delete - Local)")
        print("4. Sair")
        
        op = input("Escolha uma opção: ")

        if op == "1":
            id_maq = input("ID da Colhedora (ex: JD-7000): ").upper()
            v = validar_float("Velocidade Atual (km/h): ")
            r = validar_float("Rotação Extrator (RPM): ")
            c = validar_float("Altura de Corte (cm): ")
            esp = validar_float("Toneladas Esperadas: ")
            real = validar_float("Toneladas Realizadas: ")
            
            # Cálculo de perda
            perda_p = ((esp - real) / esp) * 100 if esp > 0 else 0
            
            # Diagnóstico (Procedimento de Resolução)
            ajustes, status = gerar_diagnostico(v, r, c)
            
            # Estrutura de dados: Dicionário para JSON
            registro_dict = {
                "maquina": id_maq,
                "status": status,
                "correcoes": ajustes,
                "perda_percentual": round(perda_p, 2)
            }
            
            # Persistência
            inserir_registro(id_maq, v, r, c, esp, real, perda_p)
            salvar_log_json(registro_dict)
            
            print(f"\n--- RESULTADO: {status} ---")
            print(f"Perda calculada: {perda_p:.2f}%")
            if ajustes:
                print("Ações para reduzir os 15% de perda:")
                for acao in ajustes: print(f"  -> {acao}")

        elif op == "2":
            dados = listar_historico()
            print("\nID MAQUINA | % PERDA | DATA")
            for d in dados: print(f"{d[0]} | debug: {d[1]}% | {d[2].date()}")

        elif op == "3":
            apagar_arquivos_locais()

        elif op == "4":
            print("Encerrando sistema FarmTech...")
            break

if __name__ == "__main__":
    menu()