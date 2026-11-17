"""Desenho no terminal: cores, títulos, mensagens, tabelas e barra de progresso.

As cores usam códigos ANSI, que funcionam no Windows Terminal, no PowerShell
e no Linux. Se a saída não for um terminal de verdade (ex.: redirecionada para
arquivo), as cores e a limpeza de tela são desligadas sozinhas.
"""

import os
import sys

NOME_APP = "TOCA AÍ"
LARGURA = 64
LARGURA_MAXIMA_COLUNA = 28

RESET = "\033[0m"
NEGRITO = "\033[1m"
VERMELHO = "\033[31m"
VERDE = "\033[32m"
AMARELO = "\033[33m"
AZUL = "\033[34m"
MAGENTA = "\033[35m"
CIANO = "\033[36m"
CINZA = "\033[90m"


def eh_terminal():
    """True quando a saída é uma janela de terminal (e não um arquivo ou pipe)."""
    try:
        return sys.stdout.isatty()
    except (AttributeError, ValueError):
        return False


CORES_ATIVAS = eh_terminal() and os.environ.get("NO_COLOR") is None
if CORES_ATIVAS and os.name == "nt":
    os.system("")      # "acorda" o suporte a cores ANSI no console do Windows


def colorir(texto, cor):
    if CORES_ATIVAS:
        return f"{cor}{texto}{RESET}"
    return texto


def limpar_tela():
    if eh_terminal():
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")


def titulo(texto):
    linha = "=" * LARGURA
    print(colorir(linha, MAGENTA))
    print(colorir(f"  {NOME_APP}  |  {texto}", NEGRITO))
    print(colorir(linha, MAGENTA))


def subtitulo(texto):
    print()
    print(colorir(f"--- {texto} ---", NEGRITO))


def sucesso(mensagem):
    print(colorir(f"[OK] {mensagem}", VERDE))


def erro(mensagem):
    print(colorir(f"[ERRO] {mensagem}", VERMELHO))


def aviso(mensagem):
    print(colorir(f"[!] {mensagem}", AMARELO))


def info(mensagem):
    print(colorir(mensagem, CIANO))


def discreto(mensagem):
    print(colorir(mensagem, CINZA))


def cortar(texto, limite=LARGURA_MAXIMA_COLUNA):
    """Encurta textos longos para caber na coluna da tabela."""
    texto = str(texto)
    if len(texto) <= limite:
        return texto
    return texto[:limite - 3] + "..."


def montar_linha(valores, larguras, a_direita):
    """Junta os valores de uma linha, cada um completado até a largura da coluna."""
    partes = []
    for i in range(len(valores)):
        if i in a_direita:
            partes.append(valores[i].rjust(larguras[i]))
        else:
            partes.append(valores[i].ljust(larguras[i]))
    return "  " + "  ".join(partes)


def imprimir_tabela(cabecalhos, linhas, a_direita=()):
    """Imprime uma tabela com colunas alinhadas.

    cabecalhos: lista de títulos; linhas: lista de listas;
    a_direita: índices das colunas alinhadas à direita (números).
    """
    textos = []
    for linha in linhas:
        textos.append([cortar(valor) for valor in linha])
    larguras = [len(cabecalho) for cabecalho in cabecalhos]
    for linha in textos:
        for i in range(len(linha)):
            larguras[i] = max(larguras[i], len(linha[i]))

    print(colorir(montar_linha(cabecalhos, larguras, a_direita), NEGRITO))
    print("  " + "  ".join(["-" * largura for largura in larguras]))
    for linha in textos:
        print(montar_linha(linha, larguras, a_direita))


def barra_progresso(fracao, largura=30):
    """Ex.: [=========>--------------------]"""
    fracao = max(0.0, min(1.0, fracao))
    cheios = int(fracao * largura)
    if cheios >= largura:
        return "[" + "=" * largura + "]"
    return "[" + "=" * cheios + ">" + "-" * (largura - cheios - 1) + "]"
