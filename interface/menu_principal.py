"""Menu principal: a porta de entrada e de saída da aplicação."""

from interface.menu_albuns import MenuAlbuns
from interface.menu_artistas import MenuArtistas
from interface.menu_base import MenuBase
from interface.menu_musicas import MenuMusicas
from interface.menu_player import MenuPlayer
from interface.menu_playlists import MenuPlaylists
from interface.menu_relatorios import MenuRelatorios
from utils import entrada, tela


class MenuPrincipal(MenuBase):

    def __init__(self, app):
        super().__init__(app, "Menu principal")
        self.texto_sair = "Sair"
        self.pausar_depois_da_acao = False   # as opções abrem submenus, que já pausam
        # Associação: o menu principal TEM os submenus.
        self.menu_player = MenuPlayer(app)
        self.menu_musicas = MenuMusicas(app)
        self.menu_albuns = MenuAlbuns(app)
        self.menu_artistas = MenuArtistas(app)
        self.menu_playlists = MenuPlaylists(app)
        self.menu_relatorios = MenuRelatorios(app)

    def opcoes(self):
        # Polimorfismo: todos são MenuBase, então todos têm executar().
        return [
            ("1", "Player (tocar, pausar, próxima, aleatório...)", self.menu_player.executar),
            ("2", "Músicas", self.menu_musicas.executar),
            ("3", "Álbuns", self.menu_albuns.executar),
            ("4", "Artistas", self.menu_artistas.executar),
            ("5", "Playlists", self.menu_playlists.executar),
            ("6", "Buscar música", self.buscar),
            ("7", "Histórico e relatórios", self.menu_relatorios.executar),
        ]

    def antes_das_opcoes(self):
        app = self.app
        tela.discreto(
            f"  Biblioteca: {app.musicas.contar()} músicas, {app.albuns.contar()} álbuns, "
            f"{app.artistas.contar()} artistas, {app.playlists.contar()} playlists"
        )
        tela.discreto(f"  Som: {app.player.saida}")

    def buscar(self):
        print()
        self.menu_musicas.buscar()
        entrada.pausar()

    def pode_sair(self):
        return entrada.confirmar("Deseja mesmo sair?")
