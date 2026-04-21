from config import PARAMETROS_IDEAIS, NIVEIS_PERDA

def classificar_perda(perda_p):
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
    status, icone, desc_nivel = classificar_perda(perda_p)
    return avaliacoes, status, icone, desc_nivel
