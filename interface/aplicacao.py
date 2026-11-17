"""A classe Aplicacao junta as peças: banco, repositórios, player e menus."""

from audio.player import PARADO, TOCANDO, Player
from interface.menu_principal import MenuPrincipal
from repositorios.album_repositorio import AlbumRepositorio
from repositorios.artista_repositorio import ArtistaRepositorio
from repositorios.historico_repositorio import HistoricoRepositorio
from repositorios.musica_repositorio import MusicaRepositorio
from repositorios.playlist_repositorio import PlaylistRepositorio
from utils import entrada, tela
from utils.tempo import formatar_tempo


class Aplicacao:
    """Objeto central que os menus recebem (self.app) para chegar em tudo."""

    def __init__(self, banco, saida, pasta_dados):
        self.banco = banco
        self.pasta_dados = pasta_dados
        # Um repositório para cada tabela
        self.artistas = ArtistaRepositorio(banco)
        self.albuns = AlbumRepositorio(banco)
        self.musicas = MusicaRepositorio(banco)
        self.playlists = PlaylistRepositorio(banco)
        self.historico = HistoricoRepositorio(banco)
        # O player recebe a saída de áudio e o histórico (associação)
        self.player = Player(saida, self.historico, pasta_dados)
        self.menu_principal = MenuPrincipal(self)

    def executar(self):
        self.menu_principal.executar()

    def encerrar(self):
        """Para o som antes de fechar o programa."""
        self.player.parar()

    def mostrar_tocando_agora(self):
        """Linha de status que aparece no topo dos menus quando há música."""
        self.player.atualizar()
        musica = self.player.musica_atual()
        if musica is None or self.player.get_estado() == PARADO:
            return
        if self.player.get_estado() == TOCANDO:
            marca = tela.colorir(">> Tocando", tela.VERDE)
        else:
            marca = tela.colorir("|| Pausado", tela.AMARELO)
        posicao = formatar_tempo(self.player.posicao())
        print(f"  {marca}: {musica.get_titulo()} - {musica.get_artista().get_nome()}"
              f"  [{posicao} / {musica.duracao_formatada()}]")

    def tocar_lista(self, musicas, nome, posicao=0, mostrar=True):
        """Põe a lista na fila do player e começa a tocar.

        mostrar=False é usado dentro do menu do player, que redesenha o painel.
        """
        if not musicas:
            tela.aviso("Não há músicas para tocar aí.")
            entrada.pausar()
            return False
        self.player.carregar_fila(musicas, nome, posicao)
        self.player.tocar()
        if mostrar:
            tela.sucesso(f"Tocando agora: {self.player.musica_atual()}")
            aviso = self.player.pegar_aviso()
            if aviso:
                tela.aviso(aviso)
            tela.discreto("Os controles (pausar, próxima, aleatório...) ficam no menu Player.")
        return True
