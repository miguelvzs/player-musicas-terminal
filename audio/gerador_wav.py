"""Gera músicas de demonstração em .wav só com a biblioteca padrão.

Nada de música com direitos autorais: cada "música" é uma melodia simples,
calculada nota por nota com seno (módulo math), empacotada em bytes (struct)
e gravada em arquivo .wav (wave).
"""

import math
import struct
import wave

TAXA_AMOSTRAS = 22050          # amostras por segundo (qualidade de rádio AM, suficiente)
VOLUME = 0.25                  # 25% do volume máximo, para não assustar ninguém

# Distância de cada nota até o Dó, em semitons.
SEMITONS = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
    "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}


def frequencia_da_nota(nota):
    """Converte uma nota como "A4" ou "C#5" em frequência (Hz). A4 = 440 Hz."""
    nome = nota[:-1]
    oitava = int(nota[-1])
    if nome not in SEMITONS:
        raise ValueError(f"Nota desconhecida: {nota}")
    numero = 12 * (oitava + 1) + SEMITONS[nome]       # número MIDI da nota
    return 440.0 * math.pow(2, (numero - 69) / 12)


def valor_da_onda(forma, fase):
    """Valor entre -1 e 1 da onda na fase (em voltas) informada."""
    fracao = fase - math.floor(fase)
    if forma == "quadrada":
        if fracao < 0.5:
            return 0.6
        return -0.6
    if forma == "triangulo":
        return 4 * abs(fracao - 0.5) - 1
    # padrão: seno com um pouco da oitava acima, para soar menos "apito"
    return 0.8 * math.sin(2 * math.pi * fase) + 0.2 * math.sin(4 * math.pi * fase)


ATAQUE = int(TAXA_AMOSTRAS * 0.01)      # 10 ms para o volume subir
SOLTURA = int(TAXA_AMOSTRAS * 0.06)     # 60 ms para o volume descer


def envelope(posicao, total):
    """Sobe rápido no começo e desce no fim da nota, para não dar estalo."""
    if posicao < ATAQUE:
        return posicao / ATAQUE
    if posicao > total - SOLTURA:
        return max(0.0, (total - posicao) / SOLTURA)
    return 1.0


def gerar_wav(caminho, notas, bpm=120, forma="seno", repeticoes=2):
    """Grava um .wav com a melodia e devolve a duração em segundos.

    notas: texto com "NOTA:TEMPOS" separados por espaço. "R" é pausa.
    Exemplo: "C4:1 E4:1 G4:2 R:1"
    """
    segundos_por_tempo = 60 / bpm
    quadros = bytearray()
    for _ in range(repeticoes):
        for item in notas.split():
            nome, tempos = item.split(":")
            total = int(float(tempos) * segundos_por_tempo * TAXA_AMOSTRAS)
            amostras = []
            if nome == "R":
                amostras = [0] * total
            else:
                frequencia = frequencia_da_nota(nome)
                for i in range(total):
                    fase = frequencia * i / TAXA_AMOSTRAS
                    valor = valor_da_onda(forma, fase) * envelope(i, total) * VOLUME
                    amostras.append(int(valor * 32767))
            # "h" = inteiro de 16 bits com sinal; "<" = little-endian (padrão do WAV).
            # Empacota a nota inteira de uma vez: "<5512h" = 5512 inteiros.
            # O * "espalha" a lista, como se cada amostra fosse um argumento.
            quadros += struct.pack(f"<{total}h", *amostras)

    with wave.open(caminho, "wb") as arquivo:
        arquivo.setnchannels(1)           # mono
        arquivo.setsampwidth(2)           # 2 bytes = 16 bits por amostra
        arquivo.setframerate(TAXA_AMOSTRAS)
        arquivo.writeframes(bytes(quadros))
    return duracao_do_wav(caminho)


def duracao_do_wav(caminho):
    """Lê o cabeçalho do .wav e devolve a duração em segundos (arredondada, mínimo 1)."""
    with wave.open(caminho, "rb") as arquivo:
        quadros = arquivo.getnframes()
        taxa = arquivo.getframerate()
    return max(1, round(quadros / taxa))


def recortar_wav(origem, destino, a_partir_de_segundos):
    """Copia o .wav a partir de um ponto. Usado para "continuar" depois de pausar
    quando a saída de áudio não sabe pausar sozinha (winsound)."""
    with wave.open(origem, "rb") as entrada:
        parametros = entrada.getparams()
        inicio = int(a_partir_de_segundos * entrada.getframerate())
        inicio = min(inicio, entrada.getnframes())
        entrada.setpos(inicio)
        dados = entrada.readframes(entrada.getnframes() - inicio)
    with wave.open(destino, "wb") as saida:
        saida.setparams(parametros)
        saida.writeframes(dados)
    return destino
