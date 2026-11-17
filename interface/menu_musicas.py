"""Menu de músicas: CRUD da tabela musica, busca e atalhos para tocar."""

import os
import wave

from audio.gerador_wav import duracao_do_wav
from interface import listagens
from interface.menu_base import MenuBase
from modelos.musica import Musica
from utils import entrada, tela
from utils.tempo import formatar_tempo


class MenuMusicas(MenuBase):

    def __init__(self, app):
        super().__init__(app, "Músicas")

    def opcoes(self):
        return [
            ("1", "Listar músicas", self.listar),
            ("2", "Cadastrar música", self.cadastrar),
            ("3", "Editar música", self.editar),
            ("4", "Excluir música", self.excluir),
            ("5", "Buscar música", self.buscar),
            ("6", "Tocar uma música", self.tocar_uma),
            ("7", "Adicionar música a uma playlist", self.adicionar_a_playlist),
        ]

    def listar(self):
        tela.subtitulo("Músicas cadastradas")
        listagens.mostrar_musicas(self.app.musicas.listar())

    # ----- cadastro e edição -----

    def ler_arquivo_audio(self, mensagem):
        """Pede o caminho de um arquivo de áudio. Enter = sem arquivo (devolve "")."""
        while True:
            texto = entrada.ler_texto(mensagem, obrigatorio=False)
            texto = texto.strip('"').strip("'")      # o Windows copia caminhos com aspas
            if texto == "":
                return ""
            caminho = os.path.abspath(texto)
            if os.path.isfile(caminho):
                return caminho
            tela.erro(f"Arquivo não encontrado: {caminho}")

    def ler_duracao_do_arquivo(self, caminho):
        """Se o arquivo for .wav, descobre a duração sozinho. Senão devolve None."""
        if not caminho.lower().endswith(".wav"):
            return None
        try:
            duracao = duracao_do_wav(caminho)
        except (wave.Error, EOFError, OSError):
            tela.aviso("Não consegui ler a duração deste .wav; informe manualmente.")
            return None
        tela.info(f"Duração lida do arquivo: {formatar_tempo(duracao)}")
        return duracao

    def cadastrar(self):
        if self.app.albuns.contar() == 0:
            tela.aviso("Cadastre um álbum primeiro (menu Álbuns).")
            return
        tela.subtitulo("Álbuns")
        listagens.mostrar_albuns(self.app.albuns.listar_com_total_de_musicas())
        print()
        album = self.escolher_pelo_id(self.app.albuns, "Em qual álbum? ID")
        if album is None:
            return
        tela.subtitulo(f"Nova música em {album}")
        titulo = entrada.ler_texto("Título da música: ")
        arquivo = self.ler_arquivo_audio(
            "Arquivo de áudio .wav (Enter = sem arquivo, reprodução simulada): ")
        duracao = None
        if arquivo:
            duracao = self.ler_duracao_do_arquivo(arquivo)
        if duracao is None:
            duracao = entrada.ler_duracao("Duração (ex.: 3:25): ")
        sugestao = self.app.musicas.proximo_numero_faixa(album.get_id())
        faixa = entrada.ler_inteiro(f"Número da faixa [{sugestao}]: ", minimo=1, padrao=sugestao)

        musica = Musica(titulo, album, duracao, faixa=faixa, arquivo=arquivo)
        self.app.musicas.inserir(musica)
        tela.sucesso(f'Música "{musica.get_titulo()}" cadastrada com ID {musica.get_id()}.')

    def editar(self):
        self.listar()
        print()
        musica = self.escolher_pelo_id(self.app.musicas, "ID da música a editar")
        if musica is None:
            return
        tela.discreto("Enter mantém o valor atual, que aparece entre colchetes.")
        musica.set_titulo(entrada.ler_texto(f"Título [{musica.get_titulo()}]: ",
                                            padrao=musica.get_titulo()))
        musica.set_duracao(entrada.ler_duracao(f"Duração [{musica.duracao_formatada()}]: ",
                                               padrao=musica.get_duracao()))
        faixa_atual = musica.get_faixa()
        if faixa_atual is None:
            faixa_atual = 1
        musica.set_faixa(entrada.ler_inteiro(f"Número da faixa [{faixa_atual}]: ",
                                             minimo=1, padrao=faixa_atual))

        arquivo_atual = musica.get_arquivo() or ""
        tela.discreto(f"Arquivo atual: {arquivo_atual or '(nenhum)'}")
        if entrada.confirmar("Trocar o arquivo de áudio?"):
            musica.set_arquivo(self.ler_arquivo_audio("Novo arquivo (Enter = nenhum): "))

        self.app.musicas.atualizar(musica)
        self.app.player.substituir_na_fila(musica)
        tela.sucesso("Música atualizada.")

    def excluir(self):
        self.listar()
        print()
        musica = self.escolher_pelo_id(self.app.musicas, "ID da música a excluir")
        if musica is None:
            return
        tela.aviso("Ela também sai das playlists e do histórico (ON DELETE CASCADE).")
        if not entrada.confirmar(f'Excluir "{musica.get_titulo()}"?'):
            tela.discreto("Nada foi excluído.")
            return
        self.app.musicas.excluir(musica.get_id())
        self.app.player.remover_da_fila(musica.get_id())
        tela.sucesso(f'Música "{musica.get_titulo()}" excluída.')

    # ----- busca e atalhos -----

    def buscar(self):
        termo = entrada.ler_texto("Buscar por título, artista, álbum ou gênero: ")
        resultados = self.app.musicas.buscar(termo)
        tela.subtitulo(f'Resultados para "{termo}"')
        listagens.mostrar_musicas(resultados, numerar=True)
        if not resultados:
            return
        numero = entrada.ler_inteiro("\nNúmero (#) para tocar, ou Enter para voltar: ",
                                     minimo=1, maximo=len(resultados), permitir_vazio=True)
        if numero is not None:
            self.app.tocar_lista(resultados, f'Busca "{termo}"', numero - 1)

    def tocar_uma(self):
        musicas = self.app.musicas.listar()
        tela.subtitulo("Músicas")
        listagens.mostrar_musicas(musicas)
        if not musicas:
            return
        print()
        escolhida = self.escolher_pelo_id(self.app.musicas, "ID da música para tocar")
        if escolhida is None:
            return
        posicao = 0
        for i in range(len(musicas)):
            if musicas[i].get_id() == escolhida.get_id():
                posicao = i
        # A fila fica com todas as músicas, começando pela escolhida.
        self.app.tocar_lista(musicas, "Todas as músicas", posicao)

    def adicionar_a_playlist(self):
        if self.app.playlists.contar() == 0:
            tela.aviso("Crie uma playlist primeiro (menu Playlists).")
            return
        self.listar()
        print()
        musica = self.escolher_pelo_id(self.app.musicas, "ID da música")
        if musica is None:
            return
        tela.subtitulo("Playlists")
        listagens.mostrar_playlists(self.app.playlists.listar())
        print()
        playlist = self.escolher_pelo_id(self.app.playlists, "ID da playlist")
        if playlist is None:
            return
        if self.app.playlists.adicionar_musica(playlist.get_id(), musica.get_id()):
            tela.sucesso(f'"{musica.get_titulo()}" entrou na playlist "{playlist.get_nome()}".')
        else:
            tela.aviso(f'"{musica.get_titulo()}" já está na playlist "{playlist.get_nome()}".')
