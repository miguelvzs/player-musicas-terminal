"""Funções para converter tempo: segundos <-> texto "m:ss"."""

MENSAGEM_FORMATO = "Duração inválida. Use minutos:segundos (ex.: 3:25) ou só os segundos (ex.: 205)."


def formatar_tempo(segundos):
    """Transforma segundos em texto. Ex.: 205 -> "3:25"; 3725 -> "1:02:05"."""
    segundos = int(segundos)
    if segundos < 0:
        segundos = 0
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    resto = segundos % 60
    if horas > 0:
        return f"{horas}:{minutos:02d}:{resto:02d}"
    return f"{minutos}:{resto:02d}"


def converter_para_segundos(texto):
    """Transforma "3:25" ou "205" em 205 segundos.

    Lança ValueError com uma mensagem amigável se o texto não for um tempo
    válido. Quem chama trata com try/except.
    """
    partes = texto.strip().split(":")
    if len(partes) > 2:
        raise ValueError(MENSAGEM_FORMATO)
    try:
        if len(partes) == 2:
            minutos = int(partes[0])
            segundos = int(partes[1])
        else:
            minutos = 0
            segundos = int(partes[0])
    except ValueError:
        raise ValueError(MENSAGEM_FORMATO)

    if minutos < 0 or segundos < 0:
        raise ValueError(MENSAGEM_FORMATO)
    if len(partes) == 2 and segundos > 59:
        raise ValueError("Os segundos devem ficar entre 0 e 59.")
    total = minutos * 60 + segundos
    if total <= 0:
        raise ValueError("A duração precisa ser maior que zero.")
    return total
