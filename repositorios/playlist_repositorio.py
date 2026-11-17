"""Repositório das tabelas playlist e playlist_musica (relação N:N)."""

from modelos.playlist import Playlist
from repositorios.base import RepositorioBase
from repositorios.musica_repositorio import COLUNAS_MUSICA, JOIN_MUSICA, MusicaRepositorio


class PlaylistRepositorio(RepositorioBase):
    """CRUD de playlists e manutenção dos itens (adicionar, remover, mover)."""

    def __init__(self, banco):
        super().__init__(
            banco,
            tabela="playlist",
            colunas=("nome", "descricao", "criada_em"),
            consulta=(
                "SELECT playlist.id, playlist.nome, playlist.descricao, playlist.criada_em "
                "FROM playlist"
            ),
            ordem="playlist.nome COLLATE NOCASE",
        )
        self.musicas = MusicaRepositorio(banco)

    def para_tupla(self, playlist):
        return (playlist.get_nome(), playlist.get_descricao(), playlist.criada_em)

    def para_objeto(self, linha):
        """Sobrescrita: além de montar a Playlist, já carrega as músicas dela.

        Como listar() e buscar_por_id() da classe-mãe chamam para_objeto(),
        as duas passam a devolver playlists completas sem mudar uma linha lá.
        """
        playlist = Playlist(linha[1], linha[2], linha[3], id=linha[0])
        self.carregar_musicas(playlist)
        return playlist

    def carregar_musicas(self, playlist):
        sql = (
            f"SELECT {COLUNAS_MUSICA} FROM {JOIN_MUSICA} "
            "JOIN playlist_musica ON playlist_musica.musica_id = musica.id "
            "WHERE playlist_musica.playlist_id = ? ORDER BY playlist_musica.posicao"
        )
        for linha in self.banco.consultar(sql, (playlist.get_id(),)):
            playlist.adicionar_musica(self.musicas.para_objeto(linha))

    # ----- itens da playlist (tabela playlist_musica) -----

    def ids_das_musicas(self, playlist_id):
        """Ids das músicas da playlist, na ordem das posições."""
        linhas = self.banco.consultar(
            "SELECT musica_id FROM playlist_musica WHERE playlist_id = ? ORDER BY posicao",
            (playlist_id,),
        )
        ids = []
        for linha in linhas:
            ids.append(linha[0])
        return ids

    def contem_musica(self, playlist_id, musica_id):
        return musica_id in self.ids_das_musicas(playlist_id)

    def adicionar_musica(self, playlist_id, musica_id):
        """Coloca a música no fim da playlist. Devolve False se ela já estava lá."""
        ids = self.ids_das_musicas(playlist_id)
        if musica_id in ids:
            return False
        self.banco.executar(
            "INSERT INTO playlist_musica (playlist_id, musica_id, posicao) VALUES (?, ?, ?)",
            (playlist_id, musica_id, len(ids) + 1),
        )
        return True

    def remover_musica(self, playlist_id, musica_id):
        """Tira a música da playlist e fecha o buraco nas posições."""
        cursor = self.banco.executar(
            "DELETE FROM playlist_musica WHERE playlist_id = ? AND musica_id = ?",
            (playlist_id, musica_id),
        )
        if cursor.rowcount == 0:
            return False
        self.__renumerar(playlist_id, self.ids_das_musicas(playlist_id))
        return True

    def mover_musica(self, playlist_id, musica_id, nova_posicao):
        """Muda a música de lugar (posição começa em 1)."""
        ids = self.ids_das_musicas(playlist_id)
        if musica_id not in ids:
            return False
        nova_posicao = max(1, min(nova_posicao, len(ids)))
        ids.remove(musica_id)
        ids.insert(nova_posicao - 1, musica_id)
        self.__renumerar(playlist_id, ids)
        return True

    def __renumerar(self, playlist_id, ids_em_ordem):
        """Regrava as posições 1, 2, 3... numa transação só (commit único)."""
        comandos = []
        posicao = 1
        for musica_id in ids_em_ordem:
            comandos.append((
                "UPDATE playlist_musica SET posicao = ? WHERE playlist_id = ? AND musica_id = ?",
                (posicao, playlist_id, musica_id),
            ))
            posicao += 1
        self.banco.executar_varios(comandos)
