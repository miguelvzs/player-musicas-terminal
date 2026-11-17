"""Modelo Album."""

from datetime import date

from modelos.entidade import Entidade

ANO_MINIMO = 1900


class Album(Entidade):
    """Um álbum de um artista.

    Associação (instância como atributo, Aula 14): o atributo artista guarda
    um OBJETO Artista, e não só o número do artista. Assim dá para fazer
    album.get_artista().get_nome().
    """

    def __init__(self, titulo, artista, ano=None, genero="", id=None):
        super().__init__(id)
        self.__titulo = ""
        self.__artista = None
        self.__ano = None
        self.__genero = ""
        self.set_titulo(titulo)
        self.set_artista(artista)
        self.set_ano(ano)
        self.set_genero(genero)

    def get_titulo(self):
        return self.__titulo

    def set_titulo(self, titulo):
        titulo = str(titulo).strip()
        if titulo == "":
            raise ValueError("O título do álbum não pode ficar vazio.")
        if len(titulo) > 80:
            raise ValueError("O título do álbum pode ter no máximo 80 caracteres.")
        self.__titulo = titulo

    def get_artista(self):
        return self.__artista

    def set_artista(self, artista):
        if artista is None:
            raise ValueError("Todo álbum precisa de um artista.")
        self.__artista = artista

    def get_ano(self):
        return self.__ano

    def set_ano(self, ano):
        """Ano é opcional (None). Se vier, precisa ser um ano possível."""
        if ano is None or ano == "":
            self.__ano = None
            return
        try:
            ano = int(ano)
        except ValueError:
            raise ValueError("O ano precisa ser um número, por exemplo 2024.")
        ano_maximo = date.today().year + 1
        if ano < ANO_MINIMO or ano > ano_maximo:
            raise ValueError(f"O ano precisa estar entre {ANO_MINIMO} e {ano_maximo}.")
        self.__ano = ano

    def get_genero(self):
        return self.__genero

    def set_genero(self, genero):
        if genero is None:
            genero = ""
        genero = str(genero).strip()
        if len(genero) > 40:
            raise ValueError("O gênero pode ter no máximo 40 caracteres.")
        self.__genero = genero

    def __str__(self):
        texto = self.__titulo
        if self.__ano:
            texto += f" ({self.__ano})"
        return f"{texto} - {self.__artista.get_nome()}"
