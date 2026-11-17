"""Menu de playlists: CRUD de playlist e dos itens (tabela playlist_musica)."""

import sqlite3

from interface import listagens
from interface.menu_base import MenuBase
from modelos.playlist import Playlist
from utils import entrada, tela


class MenuPlaylists(MenuBase):

    def __init__(self, app):
        super().__init__(app, "Playlists")

    def opcoes(self):
        return [
            ("1", "Listar playlists", self.listar),
            ("2", "Criar playlist", self.criar),
            ("3", "Ver músicas de uma playlist", self.ver),
            ("4", "Adicionar músicas a uma playlist", self.adicionar_musicas),
            ("5", "Remover música de uma playlist", self.remover_musica),
            ("6", "Mudar a posição de uma música", self.mover_musica),
            ("7", "Renomear / editar descrição", self.editar),
            ("8", "Excluir playlist", self.excluir),
            ("9", "Tocar uma playlist", self.tocar),
        ]

    def listar(self):
        tela.subtitulo("Playlists")
        listagens.mostrar_playlists(self.app.playlists.listar())

    def escolher_playlist(self, rotulo="ID da playlist"):
        self.listar()
        print()
        if self.app.playlists.contar() == 0:
            return None
        return self.escolher_pelo_id(self.app.playlists, rotulo)

    def mostrar_itens(self, playlist):
        tela.subtitulo(f"{playlist.get_nome()} - {playlist.get_descricao() or 'sem descrição'}")
        listagens.mostrar_musicas(playlist.get_musicas(), numerar=True)
        if playlist.quantidade() > 0:
            tela.discreto(f"\n  {playlist}")

    def criar(self):
        tela.subtitulo("Nova playlist")
        nome = entrada.ler_texto("Nome da playlist: ")
        descricao = entrada.ler_texto("Descrição (Enter para deixar em branco): ", obrigatorio=False)
        playlist = Playlist(nome, descricao)
        try:
            self.app.playlists.inserir(playlist)
        except sqlite3.IntegrityError:
            tela.erro(f'Já existe uma playlist chamada "{playlist.get_nome()}".')
            return
        tela.sucesso(f'Playlist "{playlist.get_nome()}" criada com ID {playlist.get_id()}. '
                     "Use a opção 4 para colocar músicas nela.")

    def ver(self):
        playlist = self.escolher_playlist()
        if playlist is not None:
            self.mostrar_itens(playlist)

    def adicionar_musicas(self):
        playlist = self.escolher_playlist("Em qual playlist? ID")
        if playlist is None:
            return
        if self.app.musicas.contar() == 0:
            tela.aviso("Não há músicas cadastradas.")
            return
        tela.subtitulo("Músicas disponíveis")
        listagens.mostrar_musicas(self.app.musicas.listar())
        while True:
            print()
            musica = self.escolher_pelo_id(self.app.musicas, "ID da música para adicionar")
            if musica is None:
                return
            if self.app.playlists.adicionar_musica(playlist.get_id(), musica.get_id()):
                tela.sucesso(f'"{musica.get_titulo()}" adicionada em "{playlist.get_nome()}".')
            else:
                tela.aviso(f'"{musica.get_titulo()}" já está nesta playlist.')
            if not entrada.confirmar("Adicionar outra?"):
                return

    def escolher_item(self, playlist, rotulo):
        """Mostra as músicas da playlist e devolve a escolhida pelo número (#)."""
        self.mostrar_itens(playlist)
        if playlist.quantidade() == 0:
            return None
        print()
        numero = entrada.ler_inteiro(f"{rotulo} (0 para cancelar): ", minimo=0,
                                     maximo=playlist.quantidade())
        if numero == 0:
            tela.discreto("Operação cancelada.")
            return None
        return playlist.get_musicas()[numero - 1]

    def remover_musica(self):
        playlist = self.escolher_playlist()
        if playlist is None:
            return
        musica = self.escolher_item(playlist, "Número (#) da música para remover")
        if musica is None:
            return
        self.app.playlists.remover_musica(playlist.get_id(), musica.get_id())
        tela.sucesso(f'"{musica.get_titulo()}" saiu da playlist "{playlist.get_nome()}".')

    def mover_musica(self):
        playlist = self.escolher_playlist()
        if playlist is None:
            return
        musica = self.escolher_item(playlist, "Número (#) da música que vai mudar de lugar")
        if musica is None:
            return
        nova_posicao = entrada.ler_inteiro(f"Nova posição (1 a {playlist.quantidade()}): ",
                                           minimo=1, maximo=playlist.quantidade())
        self.app.playlists.mover_musica(playlist.get_id(), musica.get_id(), nova_posicao)
        tela.sucesso(f'"{musica.get_titulo()}" agora é a número {nova_posicao}.')
        self.mostrar_itens(self.app.playlists.buscar_por_id(playlist.get_id()))

    def editar(self):
        playlist = self.escolher_playlist("ID da playlist a editar")
        if playlist is None:
            return
        tela.discreto("Enter mantém o valor atual, que aparece entre colchetes.")
        playlist.set_nome(entrada.ler_texto(f"Nome [{playlist.get_nome()}]: ",
                                            padrao=playlist.get_nome()))
        playlist.set_descricao(entrada.ler_opcional_editando("Descrição", playlist.get_descricao()))
        try:
            self.app.playlists.atualizar(playlist)
        except sqlite3.IntegrityError:
            tela.erro(f'Já existe outra playlist chamada "{playlist.get_nome()}".')
            return
        tela.sucesso("Playlist atualizada.")

    def excluir(self):
        playlist = self.escolher_playlist("ID da playlist a excluir")
        if playlist is None:
            return
        if not entrada.confirmar(f'Excluir a playlist "{playlist.get_nome()}"? '
                                 "(as músicas continuam cadastradas)"):
            tela.discreto("Nada foi excluído.")
            return
        self.app.playlists.excluir(playlist.get_id())
        tela.sucesso(f'Playlist "{playlist.get_nome()}" excluída.')

    def tocar(self):
        playlist = self.escolher_playlist("ID da playlist para tocar")
        if playlist is None:
            return
        if playlist.quantidade() == 0:
            tela.aviso("Esta playlist está vazia. Use a opção 4 para adicionar músicas.")
            return
        self.app.tocar_lista(playlist.get_musicas(), f'Playlist "{playlist.get_nome()}"', 0)
