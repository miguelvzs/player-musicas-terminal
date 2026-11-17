"""Repositório da tabela musica."""

from modelos.musica import Musica
from repositorios.album_repositorio import COLUNAS_ALBUM, AlbumRepositorio
from repositorios.base import RepositorioBase

# 5 colunas da música + 7 do álbum/artista = 12 colunas por linha.
COLUNAS_MUSICA = (
    "musica.id, musica.titulo, musica.duracao_segundos, musica.numero_faixa, musica.arquivo, "
    + COLUNAS_ALBUM
)
TOTAL_COLUNAS_MUSICA = 12
JOIN_MUSICA = (
    "musica JOIN album ON album.id = musica.album_id "
    "JOIN artista ON artista.id = album.artista_id"
)


class MusicaRepositorio(RepositorioBase):
    """CRUD de músicas. Cada música volta com o Album (e o Artista) dentro."""

    def __init__(self, banco):
        super().__init__(
            banco,
            tabela="musica",
            colunas=("titulo", "duracao_segundos", "numero_faixa", "arquivo", "album_id"),
            consulta=f"SELECT {COLUNAS_MUSICA} FROM {JOIN_MUSICA}",
            ordem=(
                "artista.nome COLLATE NOCASE, album.ano, album.titulo, "
                "musica.numero_faixa, musica.titulo"
            ),
        )
        self.albuns = AlbumRepositorio(banco)   # reaproveita linha -> Album

    def para_tupla(self, musica):
        return (
            musica.get_titulo(),
            musica.get_duracao(),
            musica.get_faixa(),
            musica.get_arquivo(),
            musica.get_album().get_id(),
        )

    def para_objeto(self, linha):
        # linha[0:5] = dados da música; linha[5:12] = dados do álbum e do artista
        album = self.albuns.para_objeto(linha[5:12])
        return Musica(linha[1], album, linha[2], faixa=linha[3], arquivo=linha[4], id=linha[0])

    def listar_por_album(self, album_id):
        sql = (
            f"{self.consulta} WHERE musica.album_id = ? "
            "ORDER BY musica.numero_faixa, musica.titulo"
        )
        musicas = []
        for linha in self.banco.consultar(sql, (album_id,)):
            musicas.append(self.para_objeto(linha))
        return musicas

    def listar_por_artista(self, artista_id):
        sql = f"{self.consulta} WHERE artista.id = ? ORDER BY {self.ordem}"
        musicas = []
        for linha in self.banco.consultar(sql, (artista_id,)):
            musicas.append(self.para_objeto(linha))
        return musicas

    def buscar(self, termo):
        """Procura o termo no título, no artista, no álbum ou no gênero (LIKE)."""
        padrao = f"%{termo.strip()}%"
        sql = (
            f"{self.consulta} WHERE musica.titulo LIKE ? OR artista.nome LIKE ? "
            f"OR album.titulo LIKE ? OR album.genero LIKE ? ORDER BY {self.ordem}"
        )
        musicas = []
        for linha in self.banco.consultar(sql, (padrao, padrao, padrao, padrao)):
            musicas.append(self.para_objeto(linha))
        return musicas

    def proximo_numero_faixa(self, album_id):
        """Sugere o número da próxima faixa do álbum (maior + 1)."""
        linha = self.banco.consultar_um(
            "SELECT COALESCE(MAX(numero_faixa), 0) + 1 FROM musica WHERE album_id = ?",
            (album_id,),
        )
        return linha[0]

    def duracao_total(self):
        linha = self.banco.consultar_um("SELECT COALESCE(SUM(duracao_segundos), 0) FROM musica")
        return linha[0]
