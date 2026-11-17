"""Classe-mãe de todos os menus (herança + polimorfismo)."""

import sqlite3

from utils import entrada, tela


class MenuBase:
    """Molde de menu: mostra o título, as opções, lê a escolha e chama o método.

    Cada menu-filho chama super().__init__(app, titulo) e sobrescreve
    opcoes(), devolvendo uma lista de tuplas (tecla, texto, método).
    O laço do menu (executar) é escrito uma vez só, aqui.
    """

    def __init__(self, app, titulo):
        self.app = app                     # associação: acesso aos repositórios e ao player
        self.titulo = titulo
        self.texto_sair = "Voltar"
        self.pausar_depois_da_acao = True  # mostra "Pressione Enter" depois de cada ação

    def opcoes(self):
        """Os menus-filhos sobrescrevem este método."""
        return []

    def antes_das_opcoes(self):
        """Gancho opcional: o menu do player usa para desenhar o painel."""
        pass

    def pode_sair(self):
        """O menu principal sobrescreve para pedir confirmação."""
        return True

    def mostrar_cabecalho(self):
        tela.limpar_tela()
        tela.titulo(self.titulo)
        self.app.mostrar_tocando_agora()

    def executar(self):
        """Laço do menu: repete até o usuário escolher 0."""
        while True:
            self.mostrar_cabecalho()
            self.antes_das_opcoes()
            opcoes = self.opcoes()
            print()
            for tecla, texto, metodo in opcoes:
                print(f"  {tela.colorir(tecla, tela.CIANO)} - {texto}")
            print(f"  {tela.colorir('0', tela.CIANO)} - {self.texto_sair}")

            escolha = entrada.ler_texto("\nEscolha uma opção: ", obrigatorio=False).upper()
            if escolha == "0":
                if self.pode_sair():
                    return
                continue

            metodo_escolhido = None
            for tecla, texto, metodo in opcoes:
                if escolha == tecla:
                    metodo_escolhido = metodo
            if metodo_escolhido is None:
                tela.erro("Opção inválida. Digite um dos números do menu.")
                entrada.pausar()
                continue

            print()
            self.executar_acao(metodo_escolhido)

    def executar_acao(self, metodo):
        """Rede de segurança: nenhum erro de dado ou de banco derruba o programa."""
        try:
            metodo()
        except ValueError as problema:
            tela.erro(str(problema))
        except sqlite3.Error as problema:
            tela.erro(f"Erro no banco de dados: {problema}")
        if self.pausar_depois_da_acao:
            entrada.pausar()

    def escolher_pelo_id(self, repositorio, rotulo):
        """Pede um ID e devolve o objeto do banco, ou None se a pessoa digitar 0."""
        while True:
            codigo = entrada.ler_inteiro(f"{rotulo} (0 para cancelar): ", minimo=0)
            if codigo == 0:
                tela.discreto("Operação cancelada.")
                return None
            objeto = repositorio.buscar_por_id(codigo)
            if objeto is not None:
                return objeto
            tela.erro(f"Não existe registro com ID {codigo}. Confira a lista acima.")
