from datetime import datetime
from utils import validar_float
from core_logic import gerar_diagnostico, classificar_perda
from reports import formatar_relatorio
from database import inserir_registro, listar_historico
from file_manager import salvar_log_json, apagar_arquivos_locais

def menu():
    while True:
        print(f"\n{'='*20} FARMTECH SOLUTIONS {'='*20}")
        print("1. Analisar Telemetria e Resolver Perdas (Create)")
        print("2. Ver Histórico de Colheitas (Read - Oracle)")
        print("3. Limpar Arquivos de Log (Delete - Local)")
        print("4. Sair")

        op = input("\nEscolha uma opção: ").strip()

        if op == "1":
            id_maq = input("ID da Colhedora (ex: JD-7000): ").upper()
            v   = validar_float("Velocidade Atual (km/h): ")
            r   = validar_float("Rotação Extrator (RPM): ")
            c   = validar_float("Altura de Corte (cm): ")
            esp  = validar_float("Toneladas Esperadas: ")
            real = validar_float("Toneladas Realizadas: ")

            # Cálculo de perda proporcional ao valor real encontrado
            perda_p = ((esp - real) / esp) * 100 if esp > 0 else 0.0

            # Diagnóstico inteligente com padrões agronômicos reais
            avaliacoes, status, icone, desc_nivel = gerar_diagnostico(v, r, c, perda_p)

            # Exibe relatório completo no terminal
            formatar_relatorio(id_maq, v, r, c, esp, real, perda_p,
                               avaliacoes, status, icone, desc_nivel)

            # Estrutura para persistência em JSON
            registro_dict = {
                "maquina":          id_maq,
                "timestamp":        datetime.now().isoformat(),
                "status":           status,
                "perda_percentual": round(perda_p, 2),
                "parametros": {
                    "velocidade":    v,
                    "rotacao":       r,
                    "altura_corte":  c,
                    "ton_esperada":  esp,
                    "ton_realizada": real,
                },
                "ajustes_necessarios": [
                    {"parametro": a["nome"], "acao": a["acao"], "impacto": a["impacto"]}
                    for a in avaliacoes if not a["ok"]
                ],
            }

            inserir_registro(id_maq, v, r, c, esp, real, perda_p)
            salvar_log_json(registro_dict)

        elif op == "2":
            dados = listar_historico()
            if not dados:
                print("\nℹ️  Nenhum registro encontrado.")
            else:
                print(f"\n{'─'*45}")
                print(f"  {'ID MÁQUINA':<15} {'% PERDA':>8}   DATA")
                print(f"{'─'*45}")
                for d in dados:
                    perda_val = float(d[1])
                    _, icone, _ = classificar_perda(perda_val)
                    print(f"  {str(d[0]):<15} {perda_val:>7.2f}%  {icone}  {d[2].date()}")
                print(f"{'─'*45}")

        elif op == "3":
            apagar_arquivos_locais()

        elif op == "4":
            print("Encerrando sistema FarmTech...")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()
