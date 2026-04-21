def validar_float(mensagem):
    """Garante consistência: impede que o programa quebre com letras."""
    while True:
        try:
            return float(input(mensagem))
        except ValueError:
            print("❌ Erro: Digite apenas números (use ponto para decimais).")
