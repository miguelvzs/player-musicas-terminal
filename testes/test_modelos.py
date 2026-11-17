"""Testes dos modelos: validações, associação, encapsulamento e __str__."""

import unittest

from modelos.album import Album
from modelos.artista import Artista
from modelos.musica import Musica
from modelos.playlist import Playlist
from modelos.reproducao import Reproducao
from utils.tempo import converter_para_segundos, formatar_tempo


def criar_musica(titulo="Loop", duracao=125):
    artista = Artista("Os Bits Errantes", "Brasil", id=1)
    album = Album("8 Bits", artista, 2024, "Chiptune", id=1)
    return Musica(titulo, album, duracao, faixa=1, id=1)


class TestArtista(unittest.TestCase):

    def test_nome_e_pais_sao_limpos(self):
        artista = Artista("  Lua de Silício ", " Portugal ")
        self.assertEqual(artista.get_nome(), "Lua de Silício")
        self.assertEqual(artista.get_pais(), "Portugal")

    def test_nome_vazio_e_recusado(self):
        with self.assertRaises(ValueError):
            Artista("   ")

    def test_str_e_repr(self):
        artista = Artista("DJ Hertz", "Argentina", id=4)
        self.assertEqual(str(artista), "DJ Hertz (Argentina)")
        self.assertEqual(repr(artista), "<Artista id=4>")
        self.assertEqual(str(Artista("Sem País")), "Sem País")

    def test_atributo_fortemente_privado(self):
        artista = Artista("Trio Senoidal")
        with self.assertRaises(AttributeError):
            getattr(artista, "__nome")      # igual a artista.__nome fora da classe
        # O Python só "esconde" trocando o nome (name mangling):
        self.assertEqual(artista._Artista__nome, "Trio Senoidal")

    def test_heranca_de_entidade(self):
        artista = Artista("X")
        self.assertFalse(artista.esta_salva())
        artista.set_id(10)
        self.assertTrue(artista.esta_salva())
        self.assertEqual(artista.get_id(), 10)


class TestAlbumEMusica(unittest.TestCase):

    def test_ano_validado(self):
        artista = Artista("A")
        with self.assertRaises(ValueError):
            Album("Velho demais", artista, 1800)
        with self.assertRaises(ValueError):
            Album("Texto", artista, "abc")
        self.assertIsNone(Album("Sem ano", artista, "").get_ano())

    def test_album_precisa_de_artista(self):
        with self.assertRaises(ValueError):
            Album("Sozinho", None)

    def test_associacao_musica_album_artista(self):
        musica = criar_musica()
        self.assertEqual(musica.get_artista().get_nome(), "Os Bits Errantes")
        self.assertEqual(musica.get_album().get_titulo(), "8 Bits")
        self.assertEqual(str(musica), "Loop - Os Bits Errantes [2:05]")

    def test_duracao_validada(self):
        musica = criar_musica()
        for invalida in (0, -5, "abc", None):
            with self.assertRaises(ValueError):
                musica.set_duracao(invalida)
        self.assertEqual(musica.get_duracao(), 125)   # valor antigo continua

    def test_arquivo_opcional(self):
        musica = criar_musica()
        self.assertFalse(musica.tem_arquivo())
        musica.set_arquivo("  musica.wav ")
        self.assertEqual(musica.get_arquivo(), "musica.wav")
        musica.set_arquivo("")
        self.assertIsNone(musica.get_arquivo())


class TestPlaylistEReproducao(unittest.TestCase):

    def test_playlist_soma_duracoes(self):
        playlist = Playlist("Para codar")
        playlist.adicionar_musica(criar_musica("A", 60))
        playlist.adicionar_musica(criar_musica("B", 75))
        self.assertEqual(playlist.quantidade(), 2)
        self.assertEqual(playlist.duracao_total(), 135)
        self.assertEqual(str(playlist), "Para codar (2 músicas, 2:15)")

    def test_get_musicas_devolve_copia(self):
        playlist = Playlist("P")
        playlist.get_musicas().append(criar_musica())
        self.assertEqual(playlist.quantidade(), 0)

    def test_playlist_nome_obrigatorio(self):
        with self.assertRaises(ValueError):
            Playlist("")

    def test_reproducao_formata_data(self):
        reproducao = Reproducao(criar_musica(), "2026-11-17 23:59:00")
        self.assertEqual(reproducao.data_formatada(), "17/11/2026 23:59")


class TestTempo(unittest.TestCase):

    def test_formatar(self):
        self.assertEqual(formatar_tempo(0), "0:00")
        self.assertEqual(formatar_tempo(205), "3:25")
        self.assertEqual(formatar_tempo(3725), "1:02:05")

    def test_converter(self):
        self.assertEqual(converter_para_segundos("3:25"), 205)
        self.assertEqual(converter_para_segundos("205"), 205)
        for invalido in ("", "abc", "3:75", "0", "1:2:3", "-4"):
            with self.assertRaises(ValueError):
                converter_para_segundos(invalido)


if __name__ == "__main__":
    unittest.main()
