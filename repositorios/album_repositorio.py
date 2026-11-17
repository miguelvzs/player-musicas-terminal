"""Repositório da tabela album."""

from modelos.album import Album
from repositorios.artista_repositorio import ArtistaRepositorio
from repositorios.base import RepositorioBase

# Colunas do álbum seguidas das colunas do artista (o JOIN traz as duas tabelas).
COLUNAS_ALBUM = (
    "album.id, album.titulo, album.ano, album.genero, "
    "artista.id, artista.nome, artista.pais"
)
JOIN_ALBUM = "FROM album JOIN artista ON artista.id = album.artista_id"


class AlbumRepositorio(RepositorioBase):
    """CRUD de álbuns. Cada álbum volta do banco já com o objeto Artista dentro."""

    def __init__(self, banco):
        super().__init__(
            banco,
            tabela="album",
            colunas=("titulo", "ano", "genero", "artista_id"),
            consulta=f"SELECT {COLUNAS_ALBUM} {JOIN_ALBUM}",
            ordem="artista.nome COLLATE NOCASE, album.ano, album.titulo",
        )
        # Instância como atributo: reaproveita a conversão de linha -> Artista.
        self.artistas = ArtistaRepositorio(banco)

    def para_tupla(self, album):
        return (
            album.get_titulo(),
            album.get_ano(),
            album.get_genero(),
            album.get_artista().get_id(),
        )

    def para_objeto(self, linha):
        # linha = (album.id, titulo, ano, genero, artista.id, nome, pais)
        artista = self.artistas.para_objeto(linha[4:7])
        return Album(linha[1], artista, ano=linha[2], genero=linha[3], id=linha[0])

    def listar_por_artista(self, artista_id):
        sql = f"{self.consulta} WHERE album.artista_id = ? ORDER BY album.ano, album.titulo"
        albuns = []
        for linha in self.banco.consultar(sql, (artista_id,)):
            albuns.append(self.para_objeto(linha))
        return albuns

    def listar_com_total_de_musicas(self):
        """Lista de tuplas (Album, quantidade de músicas)."""
        sql = (
            f"SELECT {COLUNAS_ALBUM}, COUNT(musica.id) {JOIN_ALBUM} "
            "LEFT JOIN musica ON musica.album_id = album.id "
            f"GROUP BY album.id ORDER BY {self.ordem}"
        )
        resultado = []
        for linha in self.banco.consultar(sql):
            resultado.append((self.para_objeto(linha), linha[7]))
        return resultado
