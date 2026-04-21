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

# =============================================================================
# PADRÕES AGRONÔMICOS — Colheita Mecanizada de Cana-de-Açúcar
# Referências: Embrapa Agroenergia, CONSECANA-SP, Stolf (1984)
# =============================================================================
PARAMETROS_IDEAIS = {
    "velocidade": {
        "min": 3.5, "max": 5.5, "ideal": 4.5, "unidade": "km/h",
        "descricao": "Velocidade de deslocamento",
        "impacto": {
            "alto":  "Velocidade elevada fragmenta colmos e aumenta perdas visíveis no solo.",
            "baixo": "Velocidade muito baixa reduz capacidade operacional sem ganho de qualidade."
        }
    },
    "rotacao": {
        "min": 600, "max": 800, "ideal": 700, "unidade": "RPM",
        "descricao": "Rotação do extrator primário",
        "impacto": {
            "alto":  "Rotação excessiva lança cana junto com a palha — perda direta de matéria colhida.",
            "baixo": "Rotação insuficiente acumula palha na carga e reduz qualidade no ATR."
        }
    },
    "altura_corte": {
        "min": 2.0, "max": 5.0, "ideal": 3.0, "unidade": "cm",
        "descricao": "Altura do corte de base",
        "impacto": {
            "alto":  "Corte alto deixa tocos longos — perda de sacarose e dano permanente à soqueira.",
            "baixo": "Corte abaixo do solo danifica gemas basais e compromete a rebrota da soca."
        }
    },
}

# Faixas de severidade proporcionais ao % de perda encontrado
# (0%, 3%): Dentro do padrão da indústria brasileira
# (3%, 8%): Aceitável com ressalvas
# (8%,15%): Problemático — impacto econômico claro
# (15%,25%): Grave — prejuízo de receita significativo
# (25%+):   Inaceitável — indica falha mecânica ou operacional grave
NIVEIS_PERDA = [
    ( 0,  3,  "OTIMIZADO",  "✅", "Operação dentro do padrão agronômico (<3%). Manter configuração."),
    ( 3,  8,  "ATENÇÃO",    "⚠️ ", "Perda moderada (3–8%). Ajustes preventivos evitam agravamento."),
    ( 8, 15,  "ELEVADO",    "🔶", "Perda significativa (8–15%). Intervenção operacional necessária."),
    (15, 25,  "CRÍTICO",    "🔴", "Perda grave (15–25%). Parar, recalibrar e checar desgaste de facas."),
    (25, 100, "EMERGÊNCIA", "🚨", "Perda inaceitável (>25%). Suspender operação para manutenção."),
]


# --- 2. SUBALGORITMOS: FUNÇÕES TÉCNICAS ---

def validar_float(mensagem):
    """Garante consistência: impede que o programa quebre com letras."""
    while True:
        try:
            return float(input(mensagem))
        except ValueError:
            print("❌ Erro: Digite apenas números (use ponto para decimais).")


def _classificar_perda(perda_p):
    """Retorna (status, icone, descricao_nivel) conforme o % de perda real."""
    for minv, maxv, status, icone, desc in NIVEIS_PERDA:
        if minv <= perda_p < maxv:
            return status, icone, desc
    return "EMERGÊNCIA", "🚨", "Perda fora de escala — verificar equipamento imediatamente."


def _avaliar_parametro(nome, valor):
    """
    Compara um valor medido com a faixa ideal e retorna um dicionário
    com desvio calculado, direção do ajuste e sugestão quantificada.
    """
    p = PARAMETROS_IDEAIS[nome]
    resultado = {
        "nome": p["descricao"],
        "valor": valor,
        "unidade": p["unidade"],
        "faixa": f"{p['min']}–{p['max']} {p['unidade']} (ideal: {p['ideal']})",
        "ok": True,
        "acao": None,
        "impacto": None,
        "desvio_pct": 0.0,
    }

    if valor > p["max"]:
        desvio = ((valor - p["max"]) / p["ideal"]) * 100
        alvo   = p["ideal"]
        resultado.update({
            "ok": False,
            "desvio_pct": round(desvio, 1),
            "acao": (f"↓ Reduzir {p['descricao']}: {valor} → {alvo} {p['unidade']}  "
                     f"(+{desvio:.1f}% acima do teto)"),
            "impacto": p["impacto"]["alto"],
        })
    elif valor < p["min"]:
        desvio = ((p["min"] - valor) / p["ideal"]) * 100
        alvo   = p["ideal"]
        resultado.update({
            "ok": False,
            "desvio_pct": round(desvio, 1),
            "acao": (f"↑ Aumentar {p['descricao']}: {valor} → {alvo} {p['unidade']}  "
                     f"(-{desvio:.1f}% abaixo do mínimo)"),
            "impacto": p["impacto"]["baixo"],
        })
    return resultado


def gerar_diagnostico(v, r, c, perda_p):
    """
    Diagnóstico inteligente e proporcional ao % de perda encontrado.
    Avalia cada parâmetro contra padrões agronômicos reais e
    calibra a urgência conforme a severidade da perda.

    Retorna: (lista_avaliacoes, status, icone, descricao_nivel)
    """
    avaliacoes = [
        _avaliar_parametro("velocidade",   v),
        _avaliar_parametro("rotacao",      r),
        _avaliar_parametro("altura_corte", c),
    ]
    status, icone, desc_nivel = _classificar_perda(perda_p)
    return avaliacoes, status, icone, desc_nivel


def formatar_relatorio(id_maq, v, r, c, esp, real, perda_p,
                       avaliacoes, status, icone, desc_nivel):
    """Exibe o relatório completo e inteligente no terminal."""
    L = "=" * 55

    # Estimativa de prejuízo financeiro (preço médio da cana SP ~R$110/t)
    PRECO_TON = 110.0
    toneladas_perdidas = esp - real
    prejuizo_estimado  = toneladas_perdidas * PRECO_TON

    problemas = [a for a in avaliacoes if not a["ok"]]

    print(f"\n{L}")
    print(f"  RELATÓRIO DE COLHEITA — {id_maq}  |  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(L)

    # --- Bloco de severidade ---
    print(f"\n  STATUS GERAL:  {icone}  {status}")
    print(f"  {desc_nivel}")
    print(f"\n  Perda calculada : {perda_p:.2f}%")
    print(f"  Toneladas perdidas: {toneladas_perdidas:.2f} t  "
          f"(~R$ {prejuizo_estimado:,.0f} estimados)")

    # --- Parâmetros operacionais ---
    print(f"\n{'─'*55}")
    print("  AVALIAÇÃO DE PARÂMETROS  (Padrão Embrapa / CONSECANA)")
    print(f"{'─'*55}")
    for a in avaliacoes:
        sinal = "✅" if a["ok"] else "❌"
        print(f"\n  {sinal}  {a['nome']}")
        print(f"      Lido    : {a['valor']} {a['unidade']}")
        print(f"      Faixa   : {a['faixa']}")
        if not a["ok"]:
            print(f"      Desvio  : {a['desvio_pct']}%  |  {a['acao']}")
            print(f"      Impacto : {a['impacto']}")

    # --- Plano de ação ---
    if problemas:
        print(f"\n{'─'*55}")
        print(f"  PLANO DE AÇÃO  ({len(problemas)} ajuste(s) necessário(s))")
        print(f"{'─'*55}")
        prioridade = sorted(problemas, key=lambda x: x["desvio_pct"], reverse=True)
        for i, a in enumerate(prioridade, 1):
            print(f"\n  [{i}] {a['acao']}")
            print(f"      ↳ {a['impacto']}")
        if perda_p >= 15:
            print(f"\n  ⚙️  Checar desgaste das facas do corte de base.")
            print(f"  ⚙️  Inspecionar roletes e correntes do elevador.")
        if perda_p >= 25:
            print(f"\n  🛑  Perda crítica: interromper operação e acionar manutenção.")
    else:
        print(f"\n{'─'*55}")
        print("  ✅  Nenhum ajuste necessário. Operação dentro do padrão.")

    print(f"\n{L}\n")


# --- 3. PERSISTÊNCIA: CRUD NO ORACLE ---

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


# --- 4. MANIPULAÇÃO DE ARQUIVOS (JSON/TXT) ---

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


# --- 5. MENU PRINCIPAL (INTERFACE) ---

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
                    _, icone, _ = _classificar_perda(perda_val)
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