"""Menu de álbuns: CRUD completo da tabela album."""

import sqlite3
from datetime import date

from interface import listagens
from interface.menu_base import MenuBase
from modelos.album import ANO_MINIMO, Album
from utils import entrada, tela
from utils.tempo import formatar_tempo


class MenuAlbuns(MenuBase):

    def __init__(self, app):
        super().__init__(app, "Álbuns")

    def opcoes(self):
        return [
            ("1", "Listar álbuns", self.listar),
            ("2", "Cadastrar álbum", self.cadastrar),
            ("3", "Ver faixas de um álbum", self.ver_faixas),
            ("4", "Editar álbum", self.editar),
            ("5", "Excluir álbum", self.excluir),
        ]

    def listar(self):
        tela.subtitulo("Álbuns cadastrados")
        listagens.mostrar_albuns(self.app.albuns.listar_com_total_de_musicas())

    def escolher_artista(self, rotulo="ID do artista"):
        tela.subtitulo("Artistas")
        listagens.mostrar_artistas(self.app.artistas.listar_com_total_de_albuns())
        print()
        return self.escolher_pelo_id(self.app.artistas, rotulo)

    def cadastrar(self):
        if self.app.artistas.contar() == 0:
            tela.aviso("Cadastre um artista primeiro (menu Artistas).")
            return
        artista = self.escolher_artista("De qual artista é o álbum? ID")
        if artista is None:
            return
        tela.subtitulo(f"Novo álbum de {artista.get_nome()}")
        titulo = entrada.ler_texto("Título do álbum: ")
        ano = entrada.ler_inteiro("Ano de lançamento (Enter para deixar em branco): ",
                                  minimo=ANO_MINIMO, maximo=date.today().year + 1,
                                  permitir_vazio=True)
        genero = entrada.ler_texto("Gênero (Enter para deixar em branco): ", obrigatorio=False)
        album = Album(titulo, artista, ano, genero)
        self.app.albuns.inserir(album)
        tela.sucesso(f'Álbum "{album.get_titulo()}" cadastrado com ID {album.get_id()}.')

    def ver_faixas(self):
        self.listar()
        print()
        album = self.escolher_pelo_id(self.app.albuns, "ID do álbum")
        if album is None:
            return
        musicas = self.app.musicas.listar_por_album(album.get_id())
        tela.subtitulo(str(album))
        listagens.mostrar_musicas(musicas)
        if musicas:
            total = 0
            for musica in musicas:
                total += musica.get_duracao()
            tela.discreto(f"\n  {len(musicas)} faixas, {formatar_tempo(total)} no total.")

    def editar(self):
        self.listar()
        print()
        album = self.escolher_pelo_id(self.app.albuns, "ID do álbum a editar")
        if album is None:
            return
        tela.discreto("Enter mantém o valor atual, que aparece entre colchetes.")
        album.set_titulo(entrada.ler_texto(f"Título [{album.get_titulo()}]: ",
                                           padrao=album.get_titulo()))
        ano_atual = album.get_ano()
        if ano_atual is None:
            ano_atual = ""
        album.set_ano(entrada.ler_opcional_editando("Ano", str(ano_atual)))
        album.set_genero(entrada.ler_opcional_editando("Gênero", album.get_genero()))

        artista_atual = album.get_artista()
        codigo = entrada.ler_inteiro(
            f"ID do artista [{artista_atual.get_id()} = {artista_atual.get_nome()}]: ",
            minimo=1, padrao=artista_atual.get_id())
        if codigo != artista_atual.get_id():
            novo_artista = self.app.artistas.buscar_por_id(codigo)
            if novo_artista is None:
                tela.erro(f"Não existe artista com ID {codigo}. O álbum não foi alterado.")
                return
            album.set_artista(novo_artista)

        self.app.albuns.atualizar(album)
        tela.sucesso("Álbum atualizado.")

    def excluir(self):
        self.listar()
        print()
        album = self.escolher_pelo_id(self.app.albuns, "ID do álbum a excluir")
        if album is None:
            return
        if not entrada.confirmar(f'Excluir o álbum "{album.get_titulo()}"?'):
            tela.discreto("Nada foi excluído.")
            return
        try:
            self.app.albuns.excluir(album.get_id())
        except sqlite3.IntegrityError:
            # A chave estrangeira musica.album_id não deixa apagar.
            tela.erro("Não dá para excluir: este álbum ainda tem músicas. "
                      "Exclua as músicas dele antes (menu Músicas).")
            return
        tela.sucesso(f'Álbum "{album.get_titulo()}" excluído.')
