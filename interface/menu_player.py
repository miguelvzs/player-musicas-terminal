"""Menu do player: painel com a música atual e os controles."""

import time

from audio.player import PAUSADO, TOCANDO
from interface import listagens
from interface.menu_base import MenuBase
from utils import entrada, tela
from utils.tempo import formatar_tempo

INTERVALO_OUVIR = 0.25      # segundos entre uma atualização da barra e outra


class MenuPlayer(MenuBase):

    def __init__(self, app):
        super().__init__(app, "Player")
        # Os comandos do player são instantâneos: o painel redesenhado já mostra o resultado.
        self.pausar_depois_da_acao = False

    def mostrar_cabecalho(self):
        """Sobrescrita: aqui não precisa da linha "tocando agora", o painel já mostra tudo."""
        tela.limpar_tela()
        tela.titulo(self.titulo)

    def antes_das_opcoes(self):
        self.app.player.atualizar()
        self.mostrar_painel()

    def opcoes(self):
        player = self.app.player
        if player.get_estado() == TOCANDO:
            texto_tocar = "Pausar"
        elif player.get_estado() == PAUSADO:
            texto_tocar = "Continuar"
        else:
            texto_tocar = "Tocar"
        if player.esta_aleatorio():
            texto_aleatorio = "Desligar o modo aleatório"
        else:
            texto_aleatorio = "Ligar o modo aleatório"
        return [
            ("1", texto_tocar, player.tocar_ou_pausar),
            ("2", "Próxima", player.proxima),
            ("3", "Anterior", player.anterior),
            ("4", "Parar", player.parar),
            ("5", texto_aleatorio, player.alternar_aleatorio),
            ("6", "Repetir: desligado > fila > faixa", player.alternar_repetir),
            ("7", "Ver a fila (e pular para uma música)", self.ver_fila),
            ("8", "Ouvir ao vivo (barra animada, Ctrl+C volta)", self.ouvir),
            ("9", "Escolher o que tocar", self.escolher_o_que_tocar),
        ]

    # ----- painel -----

    def mostrar_painel(self):
        player = self.app.player
        musica = player.musica_atual()
        print()
        if musica is None:
            tela.aviso("A fila está vazia. Use a opção 9 para escolher o que tocar.")
        else:
            fila = player.get_fila()
            print(f"  Fila: {player.get_nome_fila()}  (faixa {player.get_indice() + 1} de {len(fila)})")
            print()
            if player.get_estado() == TOCANDO:
                estado = tela.colorir(">> Tocando", tela.VERDE)
            elif player.get_estado() == PAUSADO:
                estado = tela.colorir("|| Pausado", tela.AMARELO)
            else:
                estado = tela.colorir("[] Parado", tela.CINZA)
            print(f"  {estado}:  {tela.colorir(musica.get_titulo(), tela.NEGRITO)}")
            print(f"              {musica.get_artista().get_nome()} - {musica.get_album().get_titulo()}")
            print(f"              {self.linha_de_progresso()}")
            proxima = player.proxima_musica()
            if proxima is None:
                texto_proxima = "(fim da fila)"
            else:
                texto_proxima = f"{proxima.get_titulo()} - {proxima.get_artista().get_nome()}"
            print()
            print(f"  Próxima: {texto_proxima}")

        if player.esta_aleatorio():
            aleatorio = "ligado"
        else:
            aleatorio = "desligado"
        tocando_sem_som = player.get_estado() == TOCANDO and not player.esta_com_som()
        if tocando_sem_som and player.saida.emite_som():
            som = f"{player.saida} - esta faixa está em modo simulado"
        else:
            som = str(player.saida)
        tela.discreto(f"  Aleatório: {aleatorio}  |  Repetir: {player.get_repetir()}  |  Som: {som}")
        aviso = player.pegar_aviso()
        if aviso:
            tela.aviso(aviso)

    def linha_de_progresso(self):
        player = self.app.player
        musica = player.musica_atual()
        posicao = formatar_tempo(player.posicao())
        return f"{tela.barra_progresso(player.progresso())} {posicao} / {musica.duracao_formatada()}"

    # ----- ações -----

    def ver_fila(self):
        player = self.app.player
        fila = player.get_fila()
        tela.subtitulo(f"Fila: {player.get_nome_fila() or 'vazia'}")
        listagens.mostrar_musicas(fila, numerar=True, destacar=player.get_indice() + 1)
        if not fila:
            entrada.pausar()
            return
        numero = entrada.ler_inteiro("\nNúmero (#) para tocar agora, ou Enter para voltar: ",
                                     minimo=1, maximo=len(fila), permitir_vazio=True)
        if numero is not None:
            player.pular_para(numero)

    def ouvir(self):
        """Mostra a barra andando e deixa a fila seguir sozinha, até Ctrl+C."""
        player = self.app.player
        if not player.tem_fila():
            tela.aviso("A fila está vazia. Use a opção 9 para escolher o que tocar.")
            entrada.pausar()
            return
        if player.get_estado() != TOCANDO:
            player.tocar_ou_pausar()
        tela.info("Modo ouvir: a barra anda sozinha e a fila segue. Ctrl+C volta para o menu.\n")
        musica_na_tela = None
        try:
            while player.get_estado() == TOCANDO:
                player.atualizar()
                musica = player.musica_atual()
                if player.get_estado() != TOCANDO or musica is None:
                    break
                if musica is not musica_na_tela:
                    if musica_na_tela is not None:
                        print()
                    print(f"  >> {musica.get_titulo()} - {musica.get_artista().get_nome()}")
                    musica_na_tela = musica
                print(f"\r     {self.linha_de_progresso()}   ", end="", flush=True)
                time.sleep(INTERVALO_OUVIR)
            print()
        except KeyboardInterrupt:
            print()
            tela.info("Voltando ao menu do player (a música continua).")
            time.sleep(1)

    def escolher_o_que_tocar(self):
        tela.subtitulo("O que tocar?")
        print("  1 - Todas as músicas")
        print("  2 - Um álbum")
        print("  3 - Uma playlist")
        print("  4 - Um artista")
        print("  5 - As 10 mais tocadas")
        print("  0 - Cancelar")
        opcao = entrada.ler_inteiro("\nEscolha: ", minimo=0, maximo=5)
        app = self.app
        if opcao == 1:
            app.tocar_lista(app.musicas.listar(), "Todas as músicas", mostrar=False)
        elif opcao == 2:
            print()
            listagens.mostrar_albuns(app.albuns.listar_com_total_de_musicas())
            print()
            album = self.escolher_pelo_id(app.albuns, "ID do álbum")
            if album is not None:
                app.tocar_lista(app.musicas.listar_por_album(album.get_id()),
                                f'Álbum "{album.get_titulo()}"', mostrar=False)
        elif opcao == 3:
            print()
            listagens.mostrar_playlists(app.playlists.listar())
            print()
            playlist = self.escolher_pelo_id(app.playlists, "ID da playlist")
            if playlist is not None:
                app.tocar_lista(playlist.get_musicas(), f'Playlist "{playlist.get_nome()}"',
                                mostrar=False)
        elif opcao == 4:
            print()
            listagens.mostrar_artistas(app.artistas.listar_com_total_de_albuns())
            print()
            artista = self.escolher_pelo_id(app.artistas, "ID do artista")
            if artista is not None:
                app.tocar_lista(app.musicas.listar_por_artista(artista.get_id()),
                                f"Artista {artista.get_nome()}", mostrar=False)
        elif opcao == 5:
            ranking = app.historico.mais_tocadas(10)
            musicas = []
            for musica, vezes in ranking:
                musicas.append(musica)
            app.tocar_lista(musicas, "As 10 mais tocadas", mostrar=False)
