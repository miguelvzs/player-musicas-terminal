"""Repositório da tabela artista."""

from modelos.artista import Artista
from repositorios.base import RepositorioBase


class ArtistaRepositorio(RepositorioBase):
    """CRUD de artistas. O CRUD vem da classe-mãe; aqui só o que é de artista."""

    def __init__(self, banco):
        super().__init__(
            banco,
            tabela="artista",
            colunas=("nome", "pais"),
            consulta="SELECT artista.id, artista.nome, artista.pais FROM artista",
            ordem="artista.nome COLLATE NOCASE",
        )

    def para_tupla(self, artista):
        return (artista.get_nome(), artista.get_pais())

    def para_objeto(self, linha):
        # linha = (id, nome, pais)
        return Artista(linha[1], linha[2], id=linha[0])

    def listar_com_total_de_albuns(self):
        """Lista de tuplas (Artista, quantidade de álbuns). LEFT JOIN mostra também quem tem 0."""
        sql = (
            "SELECT artista.id, artista.nome, artista.pais, COUNT(album.id) "
            "FROM artista LEFT JOIN album ON album.artista_id = artista.id "
            "GROUP BY artista.id ORDER BY artista.nome COLLATE NOCASE"
        )
        resultado = []
        for linha in self.banco.consultar(sql):
            resultado.append((self.para_objeto(linha), linha[3]))
        return resultado
