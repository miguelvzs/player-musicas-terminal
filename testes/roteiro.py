"""Roda o programa de verdade (main.py), digitando as respostas de um roteiro.

O roteiro é um arquivo .txt com uma resposta por linha, como se alguém
estivesse digitando. Linhas que começam com # são comentários e são puladas;
linhas em branco valem como "Enter". {PASTA_DADOS} é trocado pela pasta do
banco de teste.

Uso manual (na pasta do projeto):
    python -m testes.roteiro                  # roda testes/roteiro_completo.txt
    python -m testes.roteiro outro_roteiro.txt
"""

import os
import subprocess
import sys
import tempfile

PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(PASTA_PROJETO, "main.py")
ROTEIRO_PADRAO = os.path.join(PASTA_PROJETO, "testes", "roteiro_completo.txt")


def ler_roteiro(caminho, pasta_dados):
    respostas = []
    with open(caminho, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.rstrip("\n")
            if linha.startswith("#"):
                continue
            respostas.append(linha.replace("{PASTA_DADOS}", pasta_dados))
    return respostas


def executar(respostas, pasta_dados, nome_banco="roteiro.db"):
    """Roda o main.py sem som, com o banco na pasta indicada. Devolve (código, saída)."""
    texto = "\n".join(respostas) + "\n"
    ambiente = dict(os.environ)
    ambiente["PYTHONIOENCODING"] = "utf-8"     # acentos iguais em qualquer sistema
    resultado = subprocess.run(
        [sys.executable, MAIN, "--sem-som", "--banco=" + os.path.join(pasta_dados, nome_banco)],
        input=texto.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=PASTA_PROJETO,
        env=ambiente,
        timeout=300,
    )
    saida = resultado.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")
    return resultado.returncode, saida


if __name__ == "__main__":
    caminho = ROTEIRO_PADRAO
    if len(sys.argv) > 1:
        caminho = sys.argv[1]
    pasta = tempfile.mkdtemp()
    codigo, saida = executar(ler_roteiro(caminho, pasta), pasta)
    print(saida)
    print(f"\n[roteiro] código de saída: {codigo}")
    print(f"[roteiro] tem Traceback? {'Traceback' in saida}")
    print(f"[roteiro] banco de teste em: {pasta}")
