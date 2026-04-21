import json
import os

def salvar_log_json(dados):
    """Escrita de arquivos: salva a última análise em JSON"""
    with open("ultima_analise.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def apagar_arquivos_locais():
    """Delete de arquivos locais"""
    if os.path.exists("ultima_analise.json"):
        os.remove("ultima_analise.json")
        print("🗑️  Arquivo JSON removido.")
    else:
        print("ℹ️  Nenhum arquivo de log encontrado.")
