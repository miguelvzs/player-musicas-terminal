"""Saídas de áudio: quem faz o som sair (ou finge que sai).

Herança e polimorfismo (Aula 14): o Player só conhece os métodos tocar(),
pausar(), continuar() e parar(). Ele não sabe se está falando com o pygame,
com o winsound ou com a saída simulada. Cada classe-filha sobrescreve esses
métodos do seu jeito.
"""

import os
import tempfile

from audio.gerador_wav import recortar_wav

# pygame é OPCIONAL (pip install pygame). Se não estiver instalado, segue sem ele.
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"   # esconde a propaganda do pygame
try:
    import pygame
except ImportError:
    pygame = None

# winsound faz parte da biblioteca padrão, mas só existe no Windows.
try:
    import winsound
except ImportError:
    winsound = None


class SaidaAudio:
    """Classe-mãe e também a saída "simulada": não emite som.

    O Player continua contando o tempo e mostrando a barra de progresso,
    então tudo funciona igual, só que em silêncio.
    """

    def __init__(self):
        self.nome = "simulada (sem som)"

    def emite_som(self):
        return False

    def suporta(self, caminho):
        """Diz se esta saída sabe tocar esse tipo de arquivo."""
        return False

    def tocar(self, caminho):
        pass

    def pausar(self):
        pass

    def continuar(self, caminho, segundos):
        pass

    def parar(self):
        pass

    def __str__(self):
        return self.nome


class SaidaWinsound(SaidaAudio):
    """Som de verdade no Windows, sem instalar nada (módulo winsound).

    O winsound não sabe pausar: para "pausar", paramos o som; para
    "continuar", tocamos uma cópia do .wav que começa no ponto da pausa.
    """

    def __init__(self):
        super().__init__()
        if winsound is None:
            raise RuntimeError("winsound só existe no Windows.")
        self.nome = "winsound (Windows, biblioteca padrão)"
        self.__arquivo_trecho = os.path.join(tempfile.gettempdir(), "toca_ai_trecho.wav")

    def emite_som(self):
        return True

    def suporta(self, caminho):
        return caminho.lower().endswith(".wav")

    def tocar(self, caminho):
        # SND_ASYNC: toca "em segundo plano" e devolve o controle na hora.
        winsound.PlaySound(caminho, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)

    def pausar(self):
        self.parar()

    def continuar(self, caminho, segundos):
        self.parar()
        trecho = recortar_wav(caminho, self.__arquivo_trecho, segundos)
        self.tocar(trecho)

    def parar(self):
        winsound.PlaySound(None, 0)   # None = parar o que estiver tocando


class SaidaPygame(SaidaAudio):
    """Som de verdade com a biblioteca opcional pygame (Windows, Linux e Mac)."""

    def __init__(self):
        super().__init__()
        if pygame is None:
            raise RuntimeError("pygame não está instalado.")
        pygame.mixer.init()            # pode falhar se não houver placa de som
        self.nome = "pygame.mixer (biblioteca opcional)"

    def emite_som(self):
        return True

    def suporta(self, caminho):
        caminho = caminho.lower()
        return caminho.endswith(".wav") or caminho.endswith(".ogg") or caminho.endswith(".mp3")

    def tocar(self, caminho):
        pygame.mixer.music.load(caminho)
        pygame.mixer.music.play()

    def pausar(self):
        pygame.mixer.music.pause()

    def continuar(self, caminho, segundos):
        pygame.mixer.music.unpause()

    def parar(self):
        pygame.mixer.music.stop()


def criar_saida(sem_som=False):
    """Escolhe a melhor saída disponível: pygame > winsound > simulada.

    Qualquer problema (biblioteca ausente, computador sem som) cai no
    except e a próxima opção é tentada. No pior caso, fica a simulada.
    """
    if sem_som:
        return SaidaAudio()
    try:
        return SaidaPygame()
    except Exception:
        pass
    try:
        return SaidaWinsound()
    except Exception:
        pass
    return SaidaAudio()
