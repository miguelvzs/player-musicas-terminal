"""Repositório da tabela historico_reproducao (histórico e ranking)."""

from modelos.reproducao import Reproducao
from repositorios.base import RepositorioBase
from repositorios.musica_repositorio import (
    COLUNAS_MUSICA,
    JOIN_MUSICA,
    TOTAL_COLUNAS_MUSICA,
    MusicaRepositorio,
)

JOIN_HISTORICO = (
    f"{JOIN_MUSICA} JOIN historico_reproducao "
    "ON historico_reproducao.musica_id = musica.id"
)


class HistoricoRepositorio(RepositorioBase):
    """Guarda cada reprodução e calcula o ranking de mais tocadas."""

    def __init__(self, banco):
        super().__init__(
            banco,
            tabela="historico_reproducao",
            colunas=("musica_id", "tocada_em"),
            consulta=(
                "SELECT historico_reproducao.id, historico_reproducao.tocada_em, "
                f"{COLUNAS_MUSICA} FROM {JOIN_HISTORICO}"
            ),
            ordem="historico_reproducao.tocada_em DESC, historico_reproducao.id DESC",
        )
        self.musicas = MusicaRepositorio(banco)

    def para_tupla(self, reproducao):
        return (reproducao.musica.get_id(), reproducao.tocada_em)

    def para_objeto(self, linha):
        # linha[0] = id, linha[1] = tocada_em, o resto = dados da música
        musica = self.musicas.para_objeto(linha[2:2 + TOTAL_COLUNAS_MUSICA])
        return Reproducao(musica, linha[1], id=linha[0])

    def registrar(self, musica):
        """Chamado pelo Player sempre que uma faixa começa a tocar."""
        return self.inserir(Reproducao(musica))

    def ultimas(self, limite=20):
        sql = f"{self.consulta} ORDER BY {self.ordem} LIMIT ?"
        reproducoes = []
        for linha in self.banco.consultar(sql, (limite,)):
            reproducoes.append(self.para_objeto(linha))
        return reproducoes

    def mais_tocadas(self, limite=10):
        """Ranking: lista de tuplas (Musica, quantas vezes tocou)."""
        sql = (
            f"SELECT {COLUNAS_MUSICA}, COUNT(*) FROM {JOIN_HISTORICO} "
            "GROUP BY musica.id "
            "ORDER BY COUNT(*) DESC, MAX(historico_reproducao.tocada_em) DESC "
            "LIMIT ?"
        )
        ranking = []
        for linha in self.banco.consultar(sql, (limite,)):
            musica = self.musicas.para_objeto(linha[:TOTAL_COLUNAS_MUSICA])
            ranking.append((musica, linha[TOTAL_COLUNAS_MUSICA]))
        return ranking

    def artistas_mais_ouvidos(self, limite=5):
        """Lista de tuplas (nome do artista, quantas reproduções)."""
        sql = (
            f"SELECT artista.nome, COUNT(*) FROM {JOIN_HISTORICO} "
            "GROUP BY artista.id ORDER BY COUNT(*) DESC, artista.nome LIMIT ?"
        )
        return self.banco.consultar(sql, (limite,))

    def tempo_total_ouvido(self):
        """Soma da duração de tudo o que já tocou (em segundos)."""
        linha = self.banco.consultar_um(
            f"SELECT COALESCE(SUM(musica.duracao_segundos), 0) FROM {JOIN_HISTORICO}"
        )
        return linha[0]

    def limpar(self):
        """Apaga todo o histórico. Devolve quantas linhas saíram."""
        cursor = self.banco.executar("DELETE FROM historico_reproducao")
        return cursor.rowcount
