"""Modelo Playlist."""

from datetime import datetime

from modelos.entidade import Entidade
from utils.tempo import formatar_tempo


class Playlist(Entidade):
    """Uma lista de músicas montada pelo usuário.

    Associação: a playlist guarda uma LISTA de objetos Musica (self.__musicas).
    No banco, isso vira a tabela playlist_musica (relação N:N).
    """

    def __init__(self, nome, descricao="", criada_em="", id=None):
        super().__init__(id)
        self.__nome = ""
        self.__descricao = ""
        if not criada_em:
            criada_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.criada_em = criada_em
        self.__musicas = []            # começa vazia (valor padrão, Aula 14)
        self.set_nome(nome)
        self.set_descricao(descricao)

    def get_nome(self):
        return self.__nome

    def set_nome(self, nome):
        nome = str(nome).strip()
        if nome == "":
            raise ValueError("O nome da playlist não pode ficar vazio.")
        if len(nome) > 60:
            raise ValueError("O nome da playlist pode ter no máximo 60 caracteres.")
        self.__nome = nome

    def get_descricao(self):
        return self.__descricao

    def set_descricao(self, descricao):
        if descricao is None:
            descricao = ""
        descricao = str(descricao).strip()
        if len(descricao) > 120:
            raise ValueError("A descrição pode ter no máximo 120 caracteres.")
        self.__descricao = descricao

    def adicionar_musica(self, musica):
        """Coloca a música no fim da lista (em memória; quem grava é o repositório)."""
        self.__musicas.append(musica)

    def get_musicas(self):
        """Devolve uma CÓPIA da lista, para ninguém de fora bagunçar a original."""
        return list(self.__musicas)

    def quantidade(self):
        return len(self.__musicas)

    def duracao_total(self):
        total = 0
        for musica in self.__musicas:
            total += musica.get_duracao()
        return total

    def duracao_total_formatada(self):
        return formatar_tempo(self.duracao_total())

    def __str__(self):
        if self.quantidade() == 1:
            return f"{self.__nome} (1 música, {self.duracao_total_formatada()})"
        return f"{self.__nome} ({self.quantidade()} músicas, {self.duracao_total_formatada()})"
