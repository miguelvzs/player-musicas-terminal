"""Testes do Player (sem som e com um relógio controlado pelo teste)."""

import os
import shutil
import tempfile
import unittest
import wave

from audio.gerador_wav import duracao_do_wav, frequencia_da_nota, gerar_wav, recortar_wav
from audio.player import (PARADO, PAUSADO, REPETIR_DESLIGADO, REPETIR_FAIXA, REPETIR_FILA,
                          TOCANDO, Player)
from audio.saidas import SaidaAudio, criar_saida
from modelos.album import Album
from modelos.artista import Artista
from modelos.musica import Musica


class PlayerDeTeste(Player):
    """Herança no teste: troca o relógio de verdade por um que o teste controla."""

    def __init__(self, saida, historico=None):
        super().__init__(saida, historico)
        self.tempo = 1000.0

    def _agora(self):
        return self.tempo


class HistoricoFalso:
    """Faz o papel do HistoricoRepositorio, só guardando numa lista."""

    def __init__(self):
        self.tocadas = []

    def registrar(self, musica):
        self.tocadas.append(musica.get_titulo())


def criar_musicas(quantidade, duracao=10):
    album = Album("Álbum", Artista("Artista"))
    musicas = []
    for numero in range(1, quantidade + 1):
        musicas.append(Musica(f"M{numero}", album, duracao, id=numero))
    return musicas


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.historico = HistoricoFalso()
        self.player = PlayerDeTeste(SaidaAudio(), self.historico)
        self.musicas = criar_musicas(3)
        self.player.carregar_fila(self.musicas, "Teste")

    def titulo_atual(self):
        return self.player.musica_atual().get_titulo()

    def test_comeca_parado_e_tocar_registra_no_historico(self):
        self.assertEqual(self.player.get_estado(), PARADO)
        self.player.tocar()
        self.assertEqual(self.player.get_estado(), TOCANDO)
        self.assertEqual(self.historico.tocadas, ["M1"])

    def test_posicao_avanca_e_pausa_congela(self):
        self.player.tocar()
        self.player.tempo += 4
        self.assertAlmostEqual(self.player.posicao(), 4)
        self.player.pausar()
        self.player.tempo += 100
        self.assertEqual(self.player.get_estado(), PAUSADO)
        self.assertAlmostEqual(self.player.posicao(), 4)
        self.player.continuar()
        self.player.tempo += 2
        self.assertAlmostEqual(self.player.posicao(), 6)
        self.assertAlmostEqual(self.player.progresso(), 0.6)

    def test_tocar_ou_pausar_alterna(self):
        self.player.tocar_ou_pausar()
        self.assertEqual(self.player.get_estado(), TOCANDO)
        self.player.tocar_ou_pausar()
        self.assertEqual(self.player.get_estado(), PAUSADO)
        self.player.tocar_ou_pausar()
        self.assertEqual(self.player.get_estado(), TOCANDO)
        self.player.parar()
        self.assertEqual(self.player.get_estado(), PARADO)
        self.assertEqual(self.player.posicao(), 0)

    def test_proxima_anterior_e_fim_da_fila(self):
        self.player.tocar()
        self.player.proxima()
        self.assertEqual(self.titulo_atual(), "M2")
        self.player.anterior()
        self.assertEqual(self.titulo_atual(), "M1")
        self.player.proxima()
        self.player.proxima()
        self.assertFalse(self.player.proxima())          # acabou a fila
        self.assertEqual(self.player.get_estado(), PARADO)
        self.assertEqual(self.player.pegar_aviso(), "Fim da fila.")

    def test_anterior_depois_de_3_segundos_volta_ao_inicio(self):
        self.player.pular_para(2)
        self.player.tempo += 5
        self.player.anterior()
        self.assertEqual(self.titulo_atual(), "M2")
        self.assertEqual(self.player.posicao(), 0)

    def test_atualizar_segue_quando_a_musica_acaba(self):
        self.player.tocar()
        self.player.tempo += 9
        self.assertFalse(self.player.atualizar())
        self.player.tempo += 1
        self.assertTrue(self.player.atualizar())
        self.assertEqual(self.titulo_atual(), "M2")
        self.assertEqual(self.historico.tocadas, ["M1", "M2"])

    def test_repetir_fila_volta_ao_comeco(self):
        self.assertEqual(self.player.alternar_repetir(), REPETIR_FILA)
        self.player.pular_para(3)
        self.player.tempo += 10
        self.player.atualizar()
        self.assertEqual(self.titulo_atual(), "M1")

    def test_repetir_faixa_repete_a_mesma(self):
        self.player.alternar_repetir()
        self.assertEqual(self.player.alternar_repetir(), REPETIR_FAIXA)
        self.player.tocar()
        self.player.tempo += 10
        self.player.atualizar()
        self.assertEqual(self.titulo_atual(), "M1")
        self.assertEqual(self.historico.tocadas, ["M1", "M1"])
        self.assertEqual(self.player.alternar_repetir(), REPETIR_DESLIGADO)

    def test_aleatorio_mantem_a_atual_e_as_mesmas_musicas(self):
        musicas = criar_musicas(20)
        self.player.carregar_fila(musicas, "Grande", comecar_em=4)
        self.player.tocar()
        self.player.alternar_aleatorio()
        fila = self.player.get_fila()
        self.assertEqual(fila[0].get_titulo(), "M5")
        self.assertEqual(sorted([m.get_id() for m in fila]), list(range(1, 21)))
        self.player.alternar_aleatorio()                    # desliga: volta à ordem normal
        self.assertEqual([m.get_id() for m in self.player.get_fila()], list(range(1, 21)))
        self.assertEqual(self.titulo_atual(), "M5")

    def test_remover_da_fila(self):
        self.player.pular_para(2)
        self.player.remover_da_fila(2)                      # era a que estava tocando
        self.assertEqual(self.player.get_estado(), PARADO)
        self.assertEqual([m.get_titulo() for m in self.player.get_fila()], ["M1", "M3"])
        self.player.remover_da_fila(1)
        self.assertEqual(self.titulo_atual(), "M3")

    def test_fila_vazia_nao_quebra(self):
        player = PlayerDeTeste(SaidaAudio())
        self.assertFalse(player.tocar())
        self.assertFalse(player.proxima())
        self.assertFalse(player.anterior())
        self.assertFalse(player.atualizar())
        self.assertIsNone(player.musica_atual())
        self.assertEqual(player.progresso(), 0.0)

    def test_saida_sem_som(self):
        self.assertIsInstance(criar_saida(sem_som=True), SaidaAudio)
        self.assertFalse(criar_saida(sem_som=True).emite_som())


class TestGeradorWav(unittest.TestCase):

    def setUp(self):
        self.pasta = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.pasta, ignore_errors=True)

    def test_frequencia_da_nota(self):
        self.assertAlmostEqual(frequencia_da_nota("A4"), 440.0)
        self.assertAlmostEqual(frequencia_da_nota("A5"), 880.0)
        with self.assertRaises(ValueError):
            frequencia_da_nota("H4")

    def test_gera_wav_valido_e_recorta(self):
        caminho = os.path.join(self.pasta, "teste.wav")
        duracao = gerar_wav(caminho, "C4:1 E4:1 G4:2 R:2", bpm=120, repeticoes=1)   # 6 tempos = 3 s
        self.assertEqual(duracao, 3)
        with wave.open(caminho, "rb") as arquivo:
            self.assertEqual(arquivo.getnchannels(), 1)
            self.assertEqual(arquivo.getsampwidth(), 2)
        trecho = recortar_wav(caminho, os.path.join(self.pasta, "trecho.wav"), 1)
        self.assertEqual(duracao_do_wav(trecho), 2)


if __name__ == "__main__":
    unittest.main()
