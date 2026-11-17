"""Testes de ponta a ponta: o programa inteiro rodando com entradas digitadas por roteiro."""

import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

import main as programa
from testes import roteiro


class TestAplicacaoPeloTerminal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Uma pasta para a classe toda: as músicas de demonstração são geradas uma vez só.
        cls.pasta = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.pasta, ignore_errors=True)

    def test_roteiro_completo_passa_por_todos_os_menus_sem_erro(self):
        respostas = roteiro.ler_roteiro(roteiro.ROTEIRO_PADRAO, self.pasta)
        codigo, saida = roteiro.executar(respostas, self.pasta, "completo.db")
        self.assertEqual(codigo, 0, saida[-2000:])
        self.assertNotIn("Traceback", saida)
        self.assertNotIn("Erro inesperado", saida)
        esperado = [
            "Banco criado em",
            "Opção inválida",
            'Já existe um artista chamado "Banda do Teste"',
            "não é um número inteiro",
            "este artista ainda tem álbuns",
            "este álbum ainda tem músicas",
            "O ano precisa ser um número",
            "Arquivo não encontrado",
            "Duração lida do arquivo: 0:11",
            'Já existe uma playlist chamada "Para codar"',
            '"Commit às 23:59" agora é a número 1.',
            "Modo ouvir",
            "Fim da fila.",
            "Relatório salvo em:",
            "reproduções apagadas. O ranking começa do zero.",
            "Até a próxima!",
        ]
        for trecho in esperado:
            self.assertIn(trecho, saida)

    def test_entrada_que_termina_no_meio_sai_sem_erro(self):
        codigo, saida = roteiro.executar(["4", "2", "Meio Cadastro"], self.pasta, "eof.db")
        self.assertEqual(codigo, 0)
        self.assertNotIn("Traceback", saida)
        self.assertIn("A entrada de dados terminou", saida)

    def test_ctrl_c_sai_com_mensagem_amigavel(self):
        caminho = os.path.join(self.pasta, "ctrl_c.db")
        with mock.patch("builtins.input", side_effect=KeyboardInterrupt):
            with redirect_stdout(io.StringIO()) as tela:
                programa.main(["--sem-som", "--banco=" + caminho])
        self.assertIn("Ctrl+C: saindo com segurança", tela.getvalue())

    def test_ajuda(self):
        with redirect_stdout(io.StringIO()) as tela:
            programa.main(["--ajuda"])
        self.assertIn("--sem-som", tela.getvalue())


if __name__ == "__main__":
    unittest.main()
