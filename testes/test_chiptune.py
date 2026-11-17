"""Testes do sintetizador de 16 bits (audio/chiptune.py) e do repertório."""

import os
import shutil
import tempfile
import unittest
import wave

from audio.chiptune import TAXA_AMOSTRAS, Canal, Trilha, ler_notas
from audio.gerador_wav import frequencia_da_nota
from banco import repertorio_16bits


def frequencia_medida(amostras):
    """Conta quantas vezes a onda cruza o zero subindo: dá a frequência em Hz."""
    subidas = sum(1 for i in range(1, len(amostras)) if amostras[i - 1] <= 0 < amostras[i])
    return subidas * TAXA_AMOSTRAS / len(amostras)


class TestNotas(unittest.TestCase):

    def test_le_notas_e_pausas(self):
        self.assertEqual(ler_notas("C5:1 R:0.5 F#4:2"), [("C5", 1.0), ("R", 0.5), ("F#4", 2.0)])

    def test_recusa_nota_desconhecida(self):
        with self.assertRaises(ValueError):
            ler_notas("H5:1")

    def test_recusa_duracao_zero_ou_sem_duracao(self):
        with self.assertRaises(ValueError):
            ler_notas("C5:0")
        with self.assertRaises(ValueError):
            ler_notas("C5")

    def test_bateria_so_aceita_as_pecas_conhecidas(self):
        self.assertEqual(ler_notas("K:1 S:1 H:0.5 X:2", bateria=True)[3], ("X", 2.0))
        with self.assertRaises(ValueError):
            ler_notas("C5:1", bateria=True)


class TestCanalETrilha(unittest.TestCase):

    def setUp(self):
        self.pasta = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.pasta, ignore_errors=True)

    def test_canal_recusa_timbre_e_largura_invalidos(self):
        with self.assertRaises(ValueError):
            Canal("violino", "C5:1")
        with self.assertRaises(ValueError):
            Canal("pulso", "C5:1", largura=1.5)

    def test_pulso_e_triangulo_tocam_a_frequencia_certa(self):
        for timbre, largura in (("pulso", 0.5), ("pulso", 0.25), ("triangulo", 0.5)):
            trilha = Trilha([Canal(timbre, "A4:2", largura=largura)], bpm=60, eco=0)
            trecho = trilha.renderizar()[int(0.2 * TAXA_AMOSTRAS):int(1.2 * TAXA_AMOSTRAS)]
            self.assertAlmostEqual(frequencia_medida(trecho), frequencia_da_nota("A4"), delta=3)

    def test_canal_curto_repete_ate_o_fim_da_volta(self):
        # Melodia de 4 tempos e baixo de 1 tempo: o baixo precisa tocar até o fim.
        trilha = Trilha([Canal("pulso", "R:4"), Canal("triangulo", "C3:1")], bpm=60, eco=0)
        amostras = trilha.renderizar()
        ultimo_tempo = amostras[int(3.1 * TAXA_AMOSTRAS):int(3.8 * TAXA_AMOSTRAS)]
        self.assertGreater(max(abs(v) for v in ultimo_tempo), 0.1)

    def test_acelerar_deixa_cada_volta_mais_curta(self):
        normal = Trilha([Canal("pulso", "C5:4")], bpm=120, repeticoes=2)
        rapida = Trilha([Canal("pulso", "C5:4")], bpm=120, repeticoes=2, acelerar=0.5)
        self.assertLess(rapida.duracao_estimada(), normal.duracao_estimada())

    def test_grava_wav_mono_de_16_bits_igual_toda_vez(self):
        trilha = Trilha([Canal("pulso", "C5:1 E5:1", largura=0.25),
                         Canal("triangulo", "C3:2"),
                         Canal("bateria", "K:0.5 H:0.5 S:0.5 H:0.5")], bpm=120)
        primeiro = os.path.join(self.pasta, "a.wav")
        segundo = os.path.join(self.pasta, "b.wav")
        duracao = trilha.gravar(primeiro)
        trilha.gravar(segundo)
        with wave.open(primeiro, "rb") as arquivo:
            self.assertEqual(arquivo.getnchannels(), 1)
            self.assertEqual(arquivo.getsampwidth(), 2)
            self.assertEqual(arquivo.getframerate(), TAXA_AMOSTRAS)
        self.assertEqual(duracao, round(trilha.duracao_estimada()))
        with open(primeiro, "rb") as a, open(segundo, "rb") as b:
            self.assertEqual(a.read(), b.read())


class TestRepertorio(unittest.TestCase):

    def test_todas_as_trilhas_montam_e_os_canais_se_encaixam(self):
        for dados in repertorio_16bits.TRILHAS:
            with self.subTest(dados["titulo"]):
                trilha = repertorio_16bits.montar_trilha(dados)
                volta = trilha.tempos_por_volta()
                for canal in dados["canais"]:
                    tamanho = sum(float(item.split(":")[1]) for item in canal["notas"].split())
                    # Cada canal tem o tamanho da volta ou cabe um número inteiro de vezes nela.
                    self.assertAlmostEqual(volta / tamanho, round(volta / tamanho))

    def test_titulos_arquivos_e_playlist_coerentes(self):
        titulos = [dados["titulo"] for dados in repertorio_16bits.TRILHAS]
        arquivos = [dados["arquivo"] for dados in repertorio_16bits.TRILHAS]
        self.assertEqual(len(set(arquivos)), len(arquivos))
        self.assertTrue(all(len(titulo) <= 80 for titulo in titulos))
        for _, _, musicas in repertorio_16bits.PLAYLISTS:
            self.assertTrue(set(musicas) <= set(titulos))

    def test_toda_musica_diz_de_onde_veio(self):
        for dados in repertorio_16bits.TRILHAS:
            self.assertTrue(dados["origem"])


if __name__ == "__main__":
    unittest.main()
