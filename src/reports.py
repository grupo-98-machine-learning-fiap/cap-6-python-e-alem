from datetime import datetime

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
