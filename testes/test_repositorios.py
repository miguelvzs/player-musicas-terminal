"""Testes do CRUD dos repositórios com um banco SQLite temporário."""

import os
import shutil
import sqlite3
import tempfile
import unittest

from banco.conexao import Banco
from modelos.album import Album
from modelos.artista import Artista
from modelos.musica import Musica
from modelos.playlist import Playlist
from modelos.reproducao import Reproducao
from repositorios.album_repositorio import AlbumRepositorio
from repositorios.artista_repositorio import ArtistaRepositorio
from repositorios.historico_repositorio import HistoricoRepositorio
from repositorios.musica_repositorio import MusicaRepositorio
from repositorios.playlist_repositorio import PlaylistRepositorio


class BaseTesteBanco(unittest.TestCase):
    """Cria um banco novo numa pasta temporária antes de CADA teste e apaga depois."""

    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        self.banco = Banco(os.path.join(self.pasta, "teste.db"))
        self.banco.conectar()
        self.banco.criar_tabelas()
        self.artistas = ArtistaRepositorio(self.banco)
        self.albuns = AlbumRepositorio(self.banco)
        self.musicas = MusicaRepositorio(self.banco)
        self.playlists = PlaylistRepositorio(self.banco)
        self.historico = HistoricoRepositorio(self.banco)

    def tearDown(self):
        self.banco.fechar()           # no Windows, o arquivo só sai depois de fechar
        shutil.rmtree(self.pasta, ignore_errors=True)

    # atalhos para montar dados
    def novo_artista(self, nome="Os Bits Errantes"):
        return self.artistas.inserir(Artista(nome, "Brasil"))

    def novo_album(self, artista=None, titulo="8 Bits de Saudade"):
        if artista is None:
            artista = self.novo_artista()
        return self.albuns.inserir(Album(titulo, artista, 2024, "Chiptune"))

    def nova_musica(self, album=None, titulo="Loop Infinito", duracao=120):
        if album is None:
            album = self.novo_album()
        return self.musicas.inserir(Musica(titulo, album, duracao, faixa=1))


class TestBanco(BaseTesteBanco):

    def test_cria_as_seis_tabelas(self):
        linhas = self.banco.consultar(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")
        nomes = sorted([linha[0] for linha in linhas])
        self.assertEqual(nomes, ["album", "artista", "historico_reproducao", "musica",
                                 "playlist", "playlist_musica"])

    def test_chaves_estrangeiras_ligadas(self):
        self.assertEqual(self.banco.consultar_um("PRAGMA foreign_keys")[0], 1)

    def test_criar_tabelas_de_novo_nao_apaga_dados(self):
        self.novo_artista()
        self.banco.criar_tabelas()
        self.assertEqual(self.artistas.contar(), 1)


class TestArtistaRepositorio(BaseTesteBanco):

    def test_crud_completo(self):
        artista = self.artistas.inserir(Artista("Lua de Silício", "Portugal"))   # Create
        self.assertIsNotNone(artista.get_id())

        lido = self.artistas.buscar_por_id(artista.get_id())                     # Read
        self.assertEqual(lido.get_nome(), "Lua de Silício")
        self.assertEqual(lido.get_pais(), "Portugal")

        lido.set_nome("Lua de Grafeno")                                          # Update
        self.assertTrue(self.artistas.atualizar(lido))
        self.assertEqual(self.artistas.buscar_por_id(artista.get_id()).get_nome(), "Lua de Grafeno")

        self.assertTrue(self.artistas.excluir(artista.get_id()))                 # Delete
        self.assertIsNone(self.artistas.buscar_por_id(artista.get_id()))
        self.assertFalse(self.artistas.excluir(artista.get_id()))

    def test_listar_em_ordem_alfabetica(self):
        self.novo_artista("Zeca")
        self.novo_artista("ana")
        self.novo_artista("Bruno")
        nomes = [artista.get_nome() for artista in self.artistas.listar()]
        self.assertEqual(nomes, ["ana", "Bruno", "Zeca"])
        self.assertEqual(self.artistas.contar(), 3)

    def test_nome_repetido_e_recusado_pelo_banco(self):
        self.novo_artista("DJ Hertz")
        with self.assertRaises(sqlite3.IntegrityError):
            self.novo_artista("DJ Hertz")

    def test_nao_exclui_artista_com_album(self):
        album = self.novo_album()
        artista_id = album.get_artista().get_id()
        with self.assertRaises(sqlite3.IntegrityError):
            self.artistas.excluir(artista_id)
        self.assertIsNotNone(self.artistas.buscar_por_id(artista_id))

    def test_total_de_albuns(self):
        artista = self.novo_artista("Com álbuns")
        self.novo_album(artista, "Um")
        self.novo_album(artista, "Dois")
        self.novo_artista("Sem álbuns")
        totais = {}
        for artista, total in self.artistas.listar_com_total_de_albuns():
            totais[artista.get_nome()] = total
        self.assertEqual(totais, {"Com álbuns": 2, "Sem álbuns": 0})


class TestAlbumRepositorio(BaseTesteBanco):

    def test_crud_e_associacao_com_artista(self):
        artista = self.novo_artista("Trio Senoidal")
        album = self.albuns.inserir(Album("Forró em Dó Maior", artista, 2023, "Forró"))
        lido = self.albuns.buscar_por_id(album.get_id())
        self.assertEqual(lido.get_artista().get_nome(), "Trio Senoidal")   # veio pelo JOIN

        outro = self.novo_artista("DJ Hertz")
        lido.set_artista(outro)
        lido.set_ano(None)
        self.albuns.atualizar(lido)
        relido = self.albuns.buscar_por_id(album.get_id())
        self.assertEqual(relido.get_artista().get_nome(), "DJ Hertz")
        self.assertIsNone(relido.get_ano())

        self.assertTrue(self.albuns.excluir(album.get_id()))
        self.assertEqual(self.albuns.contar(), 0)

    def test_album_com_artista_inexistente_e_recusado(self):
        fantasma = Artista("Fantasma", id=999)
        with self.assertRaises(sqlite3.IntegrityError):
            self.albuns.inserir(Album("Sem dono", fantasma))

    def test_nao_exclui_album_com_musica(self):
        musica = self.nova_musica()
        with self.assertRaises(sqlite3.IntegrityError):
            self.albuns.excluir(musica.get_album().get_id())

    def test_listar_por_artista(self):
        artista = self.novo_artista("A")
        self.novo_album(artista, "Segundo")
        self.novo_album(self.novo_artista("B"), "De outro")
        self.assertEqual(len(self.albuns.listar_por_artista(artista.get_id())), 1)


class TestMusicaRepositorio(BaseTesteBanco):

    def test_crud_completo(self):
        album = self.novo_album()
        musica = self.musicas.inserir(Musica("Commit às 23:59", album, 200, faixa=2,
                                             arquivo="musicas_demo/commit.wav"))
        lida = self.musicas.buscar_por_id(musica.get_id())
        self.assertEqual(lida.get_titulo(), "Commit às 23:59")
        self.assertEqual(lida.get_duracao(), 200)
        self.assertEqual(lida.get_arquivo(), "musicas_demo/commit.wav")
        self.assertEqual(lida.get_artista().get_nome(), "Os Bits Errantes")

        lida.set_titulo("Commit às 00:01")
        lida.set_duracao(61)
        lida.set_arquivo("")
        self.musicas.atualizar(lida)
        relida = self.musicas.buscar_por_id(musica.get_id())
        self.assertEqual(relida.get_titulo(), "Commit às 00:01")
        self.assertEqual(relida.duracao_formatada(), "1:01")
        self.assertIsNone(relida.get_arquivo())

        self.assertTrue(self.musicas.excluir(musica.get_id()))
        self.assertEqual(self.musicas.contar(), 0)

    def test_busca_por_titulo_artista_album_e_genero(self):
        album = self.novo_album()
        self.nova_musica(album, "Loop Infinito")
        self.nova_musica(album, "Exceção Não Tratada")
        self.assertEqual(len(self.musicas.buscar("loop")), 1)
        self.assertEqual(len(self.musicas.buscar("bits errantes")), 2)   # artista
        self.assertEqual(len(self.musicas.buscar("saudade")), 2)         # álbum
        self.assertEqual(len(self.musicas.buscar("chip")), 2)            # gênero
        self.assertEqual(len(self.musicas.buscar("xyz")), 0)

    def test_busca_nao_aceita_sql_injection(self):
        self.nova_musica()
        self.assertEqual(self.musicas.buscar("' OR 1=1 --"), [])
        self.assertEqual(self.musicas.contar(), 1)

    def test_listar_por_album_em_ordem_de_faixa_e_proxima_faixa(self):
        album = self.novo_album()
        self.musicas.inserir(Musica("Segunda", album, 60, faixa=2))
        self.musicas.inserir(Musica("Primeira", album, 60, faixa=1))
        titulos = [m.get_titulo() for m in self.musicas.listar_por_album(album.get_id())]
        self.assertEqual(titulos, ["Primeira", "Segunda"])
        self.assertEqual(self.musicas.proximo_numero_faixa(album.get_id()), 3)
        self.assertEqual(self.musicas.duracao_total(), 120)

    def test_banco_recusa_duracao_invalida(self):
        album = self.novo_album()
        with self.assertRaises(sqlite3.IntegrityError):
            self.banco.executar(
                "INSERT INTO musica (titulo, duracao_segundos, album_id) VALUES (?, ?, ?)",
                ("Zero", 0, album.get_id()))


class TestPlaylistRepositorio(BaseTesteBanco):

    def preparar(self):
        album = self.novo_album()
        self.m1 = self.nova_musica(album, "Um", 60)
        self.m2 = self.nova_musica(album, "Dois", 70)
        self.m3 = self.nova_musica(album, "Três", 80)
        self.playlist = self.playlists.inserir(Playlist("Para codar", "Foco"))
        for musica in (self.m1, self.m2, self.m3):
            self.playlists.adicionar_musica(self.playlist.get_id(), musica.get_id())

    def titulos(self):
        playlist = self.playlists.buscar_por_id(self.playlist.get_id())
        return [musica.get_titulo() for musica in playlist.get_musicas()]

    def test_crud_da_playlist(self):
        playlist = self.playlists.inserir(Playlist("Estudo", "Prova de POO"))
        lida = self.playlists.buscar_por_id(playlist.get_id())
        self.assertEqual(lida.get_nome(), "Estudo")
        self.assertNotEqual(lida.criada_em, "")
        lida.set_descricao("")
        self.playlists.atualizar(lida)
        self.assertEqual(self.playlists.buscar_por_id(playlist.get_id()).get_descricao(), "")
        self.assertTrue(self.playlists.excluir(playlist.get_id()))

    def test_itens_em_ordem_e_sem_repetir(self):
        self.preparar()
        self.assertEqual(self.titulos(), ["Um", "Dois", "Três"])
        self.assertFalse(self.playlists.adicionar_musica(self.playlist.get_id(), self.m1.get_id()))
        playlist = self.playlists.buscar_por_id(self.playlist.get_id())
        self.assertEqual(playlist.duracao_total(), 210)

    def test_remover_renumera(self):
        self.preparar()
        self.assertTrue(self.playlists.remover_musica(self.playlist.get_id(), self.m1.get_id()))
        self.assertEqual(self.titulos(), ["Dois", "Três"])
        posicoes = self.banco.consultar(
            "SELECT posicao FROM playlist_musica WHERE playlist_id = ? ORDER BY posicao",
            (self.playlist.get_id(),))
        self.assertEqual([linha[0] for linha in posicoes], [1, 2])
        self.assertFalse(self.playlists.remover_musica(self.playlist.get_id(), self.m1.get_id()))

    def test_mover(self):
        self.preparar()
        self.playlists.mover_musica(self.playlist.get_id(), self.m3.get_id(), 1)
        self.assertEqual(self.titulos(), ["Três", "Um", "Dois"])
        self.playlists.mover_musica(self.playlist.get_id(), self.m3.get_id(), 99)   # vai pro fim
        self.assertEqual(self.titulos(), ["Um", "Dois", "Três"])

    def test_excluir_playlist_apaga_itens_mas_nao_musicas(self):
        self.preparar()
        self.playlists.excluir(self.playlist.get_id())
        itens = self.banco.consultar_um("SELECT COUNT(*) FROM playlist_musica")[0]
        self.assertEqual(itens, 0)
        self.assertEqual(self.musicas.contar(), 3)

    def test_excluir_musica_tira_da_playlist(self):
        self.preparar()
        self.musicas.excluir(self.m2.get_id())
        self.assertEqual(self.titulos(), ["Um", "Três"])


class TestHistoricoRepositorio(BaseTesteBanco):

    def test_registrar_ranking_e_limpar(self):
        album = self.novo_album()
        muito = self.nova_musica(album, "Muito tocada", 100)
        pouco = self.nova_musica(album, "Pouco tocada", 50)
        for _ in range(3):
            self.historico.registrar(muito)
        self.historico.registrar(pouco)

        ranking = self.historico.mais_tocadas()
        self.assertEqual(ranking[0][0].get_titulo(), "Muito tocada")
        self.assertEqual(ranking[0][1], 3)
        self.assertEqual(ranking[1][1], 1)
        self.assertEqual(self.historico.artistas_mais_ouvidos()[0], ("Os Bits Errantes", 4))
        self.assertEqual(self.historico.tempo_total_ouvido(), 350)
        self.assertEqual(len(self.historico.ultimas(2)), 2)

        self.assertEqual(self.historico.limpar(), 4)
        self.assertEqual(self.historico.mais_tocadas(), [])

    def test_ultimas_em_ordem_da_mais_recente(self):
        musica = self.nova_musica()
        self.historico.inserir(Reproducao(musica, "2026-11-10 10:00:00"))
        self.historico.inserir(Reproducao(musica, "2026-11-16 10:00:00"))
        datas = [r.tocada_em for r in self.historico.ultimas()]
        self.assertEqual(datas, ["2026-11-16 10:00:00", "2026-11-10 10:00:00"])

    def test_excluir_musica_apaga_historico(self):
        musica = self.nova_musica()
        self.historico.registrar(musica)
        self.musicas.excluir(musica.get_id())
        self.assertEqual(self.historico.contar(), 0)


if __name__ == "__main__":
    unittest.main()
