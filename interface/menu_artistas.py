"""Menu de artistas: CRUD completo da tabela artista."""

import sqlite3

from interface import listagens
from interface.menu_base import MenuBase
from modelos.artista import Artista
from utils import entrada, tela


class MenuArtistas(MenuBase):

    def __init__(self, app):
        super().__init__(app, "Artistas")

    def opcoes(self):
        return [
            ("1", "Listar artistas", self.listar),
            ("2", "Cadastrar artista", self.cadastrar),
            ("3", "Ver álbuns de um artista", self.ver_albuns),
            ("4", "Editar artista", self.editar),
            ("5", "Excluir artista", self.excluir),
        ]

    def listar(self):
        tela.subtitulo("Artistas cadastrados")
        listagens.mostrar_artistas(self.app.artistas.listar_com_total_de_albuns())

    def cadastrar(self):
        tela.subtitulo("Novo artista")
        nome = entrada.ler_texto("Nome do artista: ")
        pais = entrada.ler_texto("País (Enter para deixar em branco): ", obrigatorio=False)
        artista = Artista(nome, pais)              # se o nome for inválido, sai ValueError
        try:
            self.app.artistas.inserir(artista)
        except sqlite3.IntegrityError:
            tela.erro(f'Já existe um artista chamado "{artista.get_nome()}".')
            return
        tela.sucesso(f'Artista "{artista.get_nome()}" cadastrado com ID {artista.get_id()}.')

    def ver_albuns(self):
        self.listar()
        print()
        artista = self.escolher_pelo_id(self.app.artistas, "ID do artista")
        if artista is None:
            return
        tela.subtitulo(f"Álbuns de {artista.get_nome()}")
        albuns = self.app.albuns.listar_por_artista(artista.get_id())
        if not albuns:
            tela.aviso("Este artista ainda não tem álbuns.")
            return
        for album in albuns:
            musicas = self.app.musicas.listar_por_album(album.get_id())
            print(f"  [{album.get_id()}] {album}  ({len(musicas)} faixas)")

    def editar(self):
        self.listar()
        print()
        artista = self.escolher_pelo_id(self.app.artistas, "ID do artista a editar")
        if artista is None:
            return
        tela.discreto("Enter mantém o valor atual, que aparece entre colchetes.")
        artista.set_nome(entrada.ler_texto(f"Nome [{artista.get_nome()}]: ",
                                           padrao=artista.get_nome()))
        artista.set_pais(entrada.ler_opcional_editando("País", artista.get_pais()))
        try:
            self.app.artistas.atualizar(artista)
        except sqlite3.IntegrityError:
            tela.erro(f'Já existe outro artista chamado "{artista.get_nome()}".')
            return
        tela.sucesso("Artista atualizado.")

    def excluir(self):
        self.listar()
        print()
        artista = self.escolher_pelo_id(self.app.artistas, "ID do artista a excluir")
        if artista is None:
            return
        if not entrada.confirmar(f'Excluir o artista "{artista.get_nome()}"?'):
            tela.discreto("Nada foi excluído.")
            return
        try:
            self.app.artistas.excluir(artista.get_id())
        except sqlite3.IntegrityError:
            # A chave estrangeira album.artista_id não deixa apagar.
            tela.erro("Não dá para excluir: este artista ainda tem álbuns. "
                      "Exclua (ou troque o artista de) cada álbum antes.")
            return
        tela.sucesso(f'Artista "{artista.get_nome()}" excluído.')
