"""Modelo Musica."""

from modelos.entidade import Entidade
from utils.tempo import formatar_tempo


class Musica(Entidade):
    """Uma faixa de um álbum.

    Associação: musica.get_album() devolve o objeto Album, e o álbum conhece
    o Artista. Por isso musica.get_artista() funciona "atravessando" os objetos.
    """

    def __init__(self, titulo, album, duracao, faixa=None, arquivo=None, id=None):
        super().__init__(id)
        self.__titulo = ""
        self.__album = None
        self.__duracao = 0
        self.__faixa = None
        self.__arquivo = None
        self.set_titulo(titulo)
        self.set_album(album)
        self.set_duracao(duracao)
        self.set_faixa(faixa)
        self.set_arquivo(arquivo)

    def get_titulo(self):
        return self.__titulo

    def set_titulo(self, titulo):
        titulo = str(titulo).strip()
        if titulo == "":
            raise ValueError("O título da música não pode ficar vazio.")
        if len(titulo) > 80:
            raise ValueError("O título da música pode ter no máximo 80 caracteres.")
        self.__titulo = titulo

    def get_album(self):
        return self.__album

    def set_album(self, album):
        if album is None:
            raise ValueError("Toda música precisa estar em um álbum.")
        self.__album = album

    def get_artista(self):
        """Atalho: o artista da música é o artista do álbum."""
        return self.__album.get_artista()

    def get_duracao(self):
        """Duração em segundos."""
        return self.__duracao

    def set_duracao(self, segundos):
        """Método que valida (como o atualizar_hodometro da Aula 14)."""
        try:
            segundos = int(segundos)
        except (TypeError, ValueError):
            raise ValueError("A duração precisa ser um número inteiro de segundos.")
        if segundos <= 0:
            raise ValueError("A duração precisa ser maior que zero.")
        if segundos > 3 * 60 * 60:
            raise ValueError("A duração pode ter no máximo 3 horas.")
        self.__duracao = segundos

    def duracao_formatada(self):
        return formatar_tempo(self.__duracao)

    def get_faixa(self):
        return self.__faixa

    def set_faixa(self, faixa):
        if faixa is None or faixa == "":
            self.__faixa = None
            return
        try:
            faixa = int(faixa)
        except ValueError:
            raise ValueError("O número da faixa precisa ser um número inteiro.")
        if faixa <= 0:
            raise ValueError("O número da faixa precisa ser maior que zero.")
        self.__faixa = faixa

    def get_arquivo(self):
        return self.__arquivo

    def set_arquivo(self, arquivo):
        """Caminho do arquivo de áudio. Vazio = música sem áudio (reprodução simulada)."""
        if arquivo is None or str(arquivo).strip() == "":
            self.__arquivo = None
        else:
            self.__arquivo = str(arquivo).strip()

    def tem_arquivo(self):
        return self.__arquivo is not None

    def __str__(self):
        return f"{self.__titulo} - {self.get_artista().get_nome()} [{self.duracao_formatada()}]"
