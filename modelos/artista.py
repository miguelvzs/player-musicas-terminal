"""Modelo Artista."""

from modelos.entidade import Entidade


class Artista(Entidade):
    """Quem canta ou toca as músicas."""

    def __init__(self, nome, pais="", id=None):
        super().__init__(id)          # a classe-mãe cuida do id
        self.__nome = ""              # fortemente privado: só muda por set_nome()
        self.__pais = ""
        self.set_nome(nome)           # já passa pela validação
        self.set_pais(pais)

    def get_nome(self):
        return self.__nome

    def set_nome(self, nome):
        """Valida antes de guardar: nome não pode ficar vazio nem passar de 80 letras."""
        nome = str(nome).strip()
        if nome == "":
            raise ValueError("O nome do artista não pode ficar vazio.")
        if len(nome) > 80:
            raise ValueError("O nome do artista pode ter no máximo 80 caracteres.")
        self.__nome = nome

    def get_pais(self):
        return self.__pais

    def set_pais(self, pais):
        if pais is None:
            pais = ""
        pais = str(pais).strip()
        if len(pais) > 40:
            raise ValueError("O país pode ter no máximo 40 caracteres.")
        self.__pais = pais

    def __str__(self):
        """Texto para o usuário (usado pelo print)."""
        if self.__pais:
            return f"{self.__nome} ({self.__pais})"
        return self.__nome
