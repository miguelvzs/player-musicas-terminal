"""Sintetizador no estilo dos videogames de 16 bits (chiptune).

O chip de som desses consoles tocava vários canais ao mesmo tempo. Aqui é igual:
cada Canal toca uma sequência de notas com um timbre (pulso, triângulo ou
bateria de ruído) e a Trilha mistura os canais, aplica um eco curto e grava um
.wav de 16 bits. Só biblioteca padrão: math, random, array e wave.

Notação (a mesma de audio/gerador_wav.py): "NOTA:TEMPOS" separados por espaço,
com R para pausa. Exemplo: "C5:1 E5:0.5 G5:0.5 R:1".
No canal de bateria as "notas" são K (bumbo), S (caixa), H (chimbal) e X (prato).
"""

import array
import math
import random
import sys
import wave

from audio.gerador_wav import duracao_do_wav, frequencia_da_nota

TAXA_AMOSTRAS = 22050       # amostras por segundo (igual às outras músicas do player)
PICO = 0.45                 # volume máximo da mistura: 45% do máximo de 16 bits
CAUDA = 0.6                 # segundos de silêncio no fim, para o eco terminar
TIMBRES = ("pulso", "triangulo", "bateria")
PECAS_DA_BATERIA = ("K", "S", "H", "X")


def ler_notas(texto, bateria=False):
    """Transforma "C5:1 R:0.5" em [("C5", 1.0), ("R", 0.5)], conferindo cada nota."""
    notas = []
    for item in texto.split():
        if ":" not in item:
            raise ValueError(f"Nota sem duração: {item}")
        nome, tempos = item.split(":")
        tempos = float(tempos)
        if tempos <= 0:
            raise ValueError(f"Duração precisa ser maior que zero: {item}")
        if nome != "R":
            if bateria:
                if nome not in PECAS_DA_BATERIA:
                    raise ValueError(f"Peça de bateria desconhecida: {nome}")
            else:
                frequencia_da_nota(nome)        # levanta ValueError se a nota não existir
        notas.append((nome, tempos))
    if not notas:
        raise ValueError("O canal precisa de pelo menos uma nota.")
    return notas


def envelope(total):
    """Volume ao longo da nota: sobe rápido, cai um pouco, segura e solta no fim."""
    soltura = min(int(0.02 * TAXA_AMOSTRAS), total // 3)
    ataque = min(int(0.004 * TAXA_AMOSTRAS), (total - soltura) // 2)
    queda = min(int(0.07 * TAXA_AMOSTRAS), total - soltura - ataque)
    segurar = total - soltura - ataque - queda
    nivel = 0.7
    curva = [i / ataque for i in range(ataque)]
    curva += [1 - (1 - nivel) * i / queda for i in range(queda)]
    curva += [nivel] * segurar
    ultimo = curva[-1] if curva else 1.0
    curva += [ultimo * (1 - i / soltura) for i in range(soltura)]
    return curva


def modelos_de_bateria(semente=16):
    """Gera uma vez os sons da bateria. Mesma semente = mesmo som sempre."""
    sorteio = random.Random(semente)
    taxa = TAXA_AMOSTRAS

    def ruido(total):
        # Como nos chips antigos: cada valor sorteado dura 2 amostras.
        valores = []
        while len(valores) < total:
            valor = sorteio.choice((-1.0, 1.0))
            valores += [valor, valor]
        return valores[:total]

    def agudo(valores):
        # Diferença entre amostras vizinhas: tira o grave e deixa o "tss" do prato.
        return [valores[i] - valores[i - 1] if i else 0.0 for i in range(len(valores))]

    bumbo = []
    fase = 0.0
    for i in range(int(0.13 * taxa)):
        t = i / taxa
        fase += (45 + 105 * math.exp(-t * 30)) / taxa     # frequência cai de 150 para 45 Hz
        bumbo.append(math.sin(2 * math.pi * fase) * math.exp(-t * 18))

    total = int(0.15 * taxa)
    chiado = ruido(total)
    caixa = [0.6 * chiado[i] * math.exp(-i / taxa * 28)
             + 0.4 * math.sin(2 * math.pi * 185 * i / taxa) * math.exp(-i / taxa * 45)
             for i in range(total)]

    total = int(0.045 * taxa)
    chiado = agudo(ruido(total))
    chimbal = [0.35 * chiado[i] * math.exp(-i / taxa * 80) for i in range(total)]

    total = int(1.2 * taxa)
    chiado = agudo(ruido(total))
    prato = [0.3 * chiado[i] * math.exp(-i / taxa * 3.5) for i in range(total)]

    return {"K": bumbo, "S": caixa, "H": chimbal, "X": prato}


class Canal:
    """Uma voz do chip de som: um timbre tocando uma sequência de notas."""

    def __init__(self, timbre, notas, volume=1.0, largura=0.5, legato=0.9):
        if timbre not in TIMBRES:
            raise ValueError(f"Timbre desconhecido: {timbre}. Use um de {TIMBRES}.")
        if not 0 < largura < 1:
            raise ValueError("A largura do pulso precisa estar entre 0 e 1.")
        if volume <= 0:
            raise ValueError("O volume precisa ser maior que zero.")
        self.__timbre = timbre
        self.__notas = ler_notas(notas, bateria=(timbre == "bateria"))
        self.__volume = volume
        self.__largura = largura
        self.__legato = legato

    def get_timbre(self):
        return self.__timbre

    def total_de_tempos(self):
        return sum(tempos for _, tempos in self.__notas)

    def renderizar(self, bpm, tempos, bateria):
        """Devolve as amostras de `tempos` batidas. Se as notas acabarem antes,
        o canal volta ao começo (é assim que o baixo e a bateria fazem o loop)."""
        amostras_por_tempo = 60 / bpm * TAXA_AMOSTRAS
        total = round(tempos * amostras_por_tempo)
        saida = [0.0] * total
        posicao = 0.0
        indice = 0
        while posicao < tempos:
            nome, duracao = self.__notas[indice % len(self.__notas)]
            # Início e fim calculados pela posição em tempos: os canais não se desalinham.
            inicio = round(posicao * amostras_por_tempo)
            fim = min(total, round((posicao + duracao) * amostras_por_tempo))
            if nome != "R" and fim > inicio:
                som = self.__som(nome, fim - inicio, bateria)
                saida[inicio:inicio + len(som)] = som
            posicao += duracao
            indice += 1
        return saida

    def __som(self, nome, total, bateria):
        if self.__timbre == "bateria":
            return [valor * self.__volume for valor in bateria[nome][:total]]
        tocando = max(1, int(total * self.__legato))     # um respiro entre as notas
        passo = frequencia_da_nota(nome) / TAXA_AMOSTRAS
        if self.__timbre == "pulso":
            # Onda de pulso: fica "alta" durante `largura` de cada volta.
            # 50% soa cheio; 25% e 12,5% soam mais finos, bem de videogame.
            largura = self.__largura
            alto, baixo = 2 * (1 - largura), -2 * largura     # média zero, sem estalo
            onda = [alto if (k * passo) % 1.0 < largura else baixo for k in range(tocando)]
        else:
            # Triângulo em 16 degraus, como o canal de baixo dos consoles.
            onda = [round((4 * abs((k * passo) % 1.0 - 0.5) - 1) * 7.5) / 7.5
                    for k in range(tocando)]
        volume = self.__volume
        return [o * e * volume for o, e in zip(onda, envelope(tocando))]


def aplicar_eco(amostras, retorno, atraso_segundos=0.15):
    """Eco com realimentação, como o eco do chip de som do Super Nintendo.
    Processa em blocos do tamanho do atraso: cada bloco só depende do anterior."""
    if retorno <= 0:
        return
    atraso = int(atraso_segundos * TAXA_AMOSTRAS)
    for inicio in range(atraso, len(amostras), atraso):
        fim = min(inicio + atraso, len(amostras))
        amostras[inicio:fim] = [a + retorno * b for a, b in
                                zip(amostras[inicio:fim], amostras[inicio - atraso:fim - atraso])]


class Trilha:
    """Uma música inteira: os canais tocando juntos, repetidos `repeticoes` vezes.

    O primeiro canal (a melodia) define o tamanho de cada volta. `acelerar` deixa
    cada volta mais rápida que a anterior: 0.1 = 10% a mais por volta.
    """

    def __init__(self, canais, bpm=120, repeticoes=1, acelerar=0.0, eco=0.25):
        if not canais:
            raise ValueError("A trilha precisa de pelo menos um canal.")
        if bpm <= 0:
            raise ValueError("O andamento (bpm) precisa ser maior que zero.")
        if repeticoes < 1:
            raise ValueError("A trilha precisa tocar pelo menos uma vez.")
        self.__canais = list(canais)
        self.__bpm = bpm
        self.__repeticoes = repeticoes
        self.__acelerar = acelerar
        self.__eco = eco

    def tempos_por_volta(self):
        return self.__canais[0].total_de_tempos()

    def bpm_da_volta(self, volta):
        return self.__bpm * (1 + self.__acelerar * volta)

    def duracao_estimada(self):
        """Duração em segundos, sem gerar o áudio."""
        segundos = sum(self.tempos_por_volta() * 60 / self.bpm_da_volta(volta)
                       for volta in range(self.__repeticoes))
        return segundos + CAUDA

    def renderizar(self):
        """Devolve a lista de amostras (números entre -1 e 1) da música inteira."""
        bateria = modelos_de_bateria()
        tempos = self.tempos_por_volta()
        mistura = []
        for volta in range(self.__repeticoes):
            bpm = self.bpm_da_volta(volta)
            pistas = [canal.renderizar(bpm, tempos, bateria) for canal in self.__canais]
            mistura += [sum(valores) for valores in zip(*pistas)]
        mistura += [0.0] * int(CAUDA * TAXA_AMOSTRAS)
        aplicar_eco(mistura, self.__eco)
        pico = max(abs(valor) for valor in mistura) or 1.0
        fator = PICO / pico
        return [valor * fator for valor in mistura]

    def gravar(self, caminho):
        """Grava o .wav (mono, 16 bits) e devolve a duração em segundos."""
        # "h" = inteiro de 16 bits com sinal, o mesmo formato do gerador_wav.py.
        dados = array.array("h", (int(valor * 32767) for valor in self.renderizar()))
        if sys.byteorder == "big":
            dados.byteswap()                 # o WAV guarda em little-endian
        with wave.open(caminho, "wb") as arquivo:
            arquivo.setnchannels(1)
            arquivo.setsampwidth(2)          # 2 bytes = 16 bits por amostra
            arquivo.setframerate(TAXA_AMOSTRAS)
            arquivo.writeframes(dados.tobytes())
        return duracao_do_wav(caminho)
