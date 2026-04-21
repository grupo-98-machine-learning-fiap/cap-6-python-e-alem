# --- CONFIGURAÇÕES E ESTADO DO SISTEMA ---
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
NIVEIS_PERDA = [
    ( 0,  3,  "OTIMIZADO",  "✅", "Operação dentro do padrão agronômico (<3%). Manter configuração."),
    ( 3,  8,  "ATENÇÃO",    "⚠️ ", "Perda moderada (3–8%). Ajustes preventivos evitam agravamento."),
    ( 8, 15,  "ELEVADO",    "🔶", "Perda significativa (8–15%). Intervenção operacional necessária."),
    (15, 25,  "CRÍTICO",    "🔴", "Perda grave (15–25%). Parar, recalibrar e checar desgaste de facas."),
    (25, 100, "EMERGÊNCIA", "🚨", "Perda inaceitável (>25%). Suspender operação para manutenção."),
]
