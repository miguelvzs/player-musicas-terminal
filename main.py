"""Toca Aí - player e gerenciador de músicas no terminal.

Ponto de entrada: python main.py
Opções: --sem-som (não emite som) e --banco=CAMINHO (usa outro arquivo .db).
"""

import os
import sqlite3
import sys

from audio.saidas import criar_saida
from banco import dados_exemplo
from banco.conexao import Banco
from interface.aplicacao import Aplicacao
from utils import tela

PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO_PADRAO = os.path.join(PASTA_PROJETO, "dados", "player.db")

AJUDA = """Uso: python main.py [opções]

  --sem-som          não emite som (a reprodução é simulada, só o tempo anda)
  --banco=CAMINHO    usa outro arquivo de banco (padrão: dados/player.db)
  --ajuda            mostra esta mensagem
"""


def ler_argumentos(argumentos):
    """Lê as opções da linha de comando (lista sys.argv sem o nome do programa)."""
    sem_som = False
    caminho_banco = CAMINHO_BANCO_PADRAO
    for argumento in argumentos:
        if argumento == "--sem-som":
            sem_som = True
        elif argumento.startswith("--banco="):
            caminho_banco = os.path.abspath(argumento.split("=", 1)[1])
        elif argumento in ("--ajuda", "--help", "-h"):
            return None
        else:
            tela.aviso(f"Opção desconhecida ignorada: {argumento}")
    return sem_som, caminho_banco


def main(argumentos=None):
    if argumentos is None:
        argumentos = sys.argv[1:]
    opcoes = ler_argumentos(argumentos)
    if opcoes is None:
        print(AJUDA)
        return
    sem_som, caminho_banco = opcoes
    pasta_dados = os.path.dirname(caminho_banco)

    banco = Banco(caminho_banco)
    app = None
    try:
        banco_novo = not os.path.exists(caminho_banco)
        # Primeiro os .wav de demonstração (parte demorada), depois o banco.
        dados_exemplo.garantir_arquivos_demo(pasta_dados)
        banco.conectar()
        banco.criar_tabelas()
        if banco_novo:
            dados_exemplo.popular(banco, pasta_dados)
            tela.sucesso(f"Banco criado em {caminho_banco} com dados de exemplo (fictícios).")

        app = Aplicacao(banco, criar_saida(sem_som), pasta_dados)
        app.executar()
        print("\nAté a próxima!")
    except KeyboardInterrupt:
        print("\n\nCtrl+C: saindo com segurança. Até a próxima!")
    except EOFError:
        print("\n\nA entrada de dados terminou. Saindo com segurança. Até a próxima!")
    except sqlite3.Error as problema:
        tela.erro(f"Problema no banco de dados: {problema}")
    except OSError as problema:
        tela.erro(f"Problema ao acessar um arquivo: {problema}")
    except Exception as problema:
        # Última rede de segurança: mostra uma mensagem em vez de quebrar.
        tela.erro(f"Erro inesperado ({problema.__class__.__name__}): {problema}")
    finally:
        if app is not None:
            app.encerrar()
        banco.fechar()      # sempre fecha a conexão, aconteça o que acontecer


if __name__ == "__main__":
    # No Windows, se a saída for redirecionada para arquivo, um caractere que
    # não existe na codificação viraria erro. errors="replace" troca por "?".
    for fluxo in (sys.stdin, sys.stdout):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(errors="replace")
    try:
        main()
    except KeyboardInterrupt:
        print("\nAté a próxima!")
