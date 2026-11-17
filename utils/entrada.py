"""Leitura do teclado sem deixar o programa quebrar (Aula 13: try/except).

Toda função repete a pergunta (while True) até receber um valor válido.
Nada de chamar a função de novo dentro dela mesma: o laço é mais seguro.
"""

from utils import tela
from utils.tempo import converter_para_segundos


def ler_texto(mensagem, obrigatorio=True, padrao=None, maximo=None):
    """Lê um texto. Com 'padrao', Enter vazio devolve o padrão (usado ao editar)."""
    while True:
        texto = input(mensagem).strip()
        if texto == "":
            if padrao is not None:
                return padrao
            if obrigatorio:
                tela.erro("Este campo é obrigatório.")
                continue
        if maximo is not None and len(texto) > maximo:
            tela.erro(f"Use no máximo {maximo} caracteres.")
            continue
        return texto


def ler_opcional_editando(rotulo, atual):
    """Usado ao editar um campo opcional: Enter mantém, "-" apaga."""
    texto = ler_texto(f"{rotulo} [{atual}] (- apaga): ", obrigatorio=False, padrao=atual)
    if texto == "-":
        return ""
    return texto


def ler_inteiro(mensagem, minimo=None, maximo=None, permitir_vazio=False, padrao=None):
    """Lê um número inteiro dentro dos limites. Enter vazio devolve o padrão ou None."""
    while True:
        texto = input(mensagem).strip()
        if texto == "":
            if padrao is not None:
                return padrao
            if permitir_vazio:
                return None
            tela.erro("Digite um número.")
            continue
        try:
            numero = int(texto)
        except ValueError:
            tela.erro(f'"{texto}" não é um número inteiro. Tente de novo.')
            continue
        if minimo is not None and numero < minimo:
            tela.erro(f"O número precisa ser no mínimo {minimo}.")
            continue
        if maximo is not None and numero > maximo:
            tela.erro(f"O número precisa ser no máximo {maximo}.")
            continue
        return numero


def ler_duracao(mensagem, padrao=None):
    """Lê uma duração como 3:25 ou 205 e devolve em segundos."""
    while True:
        texto = input(mensagem).strip()
        if texto == "" and padrao is not None:
            return padrao
        try:
            return converter_para_segundos(texto)
        except ValueError as problema:
            tela.erro(str(problema))


def confirmar(mensagem):
    """Pergunta s/n. Enter vazio conta como "não" (mais seguro para excluir)."""
    while True:
        resposta = input(f"{mensagem} (s/n): ").strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não", ""):
            return False
        tela.erro('Responda "s" para sim ou "n" para não.')


def pausar():
    input(tela.colorir("\nPressione Enter para continuar...", tela.CINZA))
