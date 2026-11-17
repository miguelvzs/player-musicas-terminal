"""Menu de histórico e relatórios (ranking, resumo e exportação para .txt)."""

import os
from datetime import datetime

from interface.menu_base import MenuBase
from utils import entrada, tela
from utils.tempo import formatar_tempo


class MenuRelatorios(MenuBase):

    def __init__(self, app):
        super().__init__(app, "Histórico e relatórios")

    def opcoes(self):
        return [
            ("1", "As 10 mais tocadas", self.mais_tocadas),
            ("2", "Artistas mais ouvidos", self.artistas_mais_ouvidos),
            ("3", "Histórico recente", self.historico_recente),
            ("4", "Resumo da biblioteca", self.resumo),
            ("5", "Exportar relatório para arquivo .txt", self.exportar),
            ("6", "Limpar o histórico", self.limpar_historico),
        ]

    def mais_tocadas(self):
        tela.subtitulo("As 10 mais tocadas")
        ranking = self.app.historico.mais_tocadas(10)
        if not ranking:
            tela.aviso("O histórico está vazio. Toque alguma música primeiro.")
            return
        linhas = []
        posicao = 1
        for musica, vezes in ranking:
            linhas.append([f"{posicao}º", musica.get_titulo(), musica.get_artista().get_nome(), vezes])
            posicao += 1
        tela.imprimir_tabela(["#", "Título", "Artista", "Vezes"], linhas, a_direita=(0, 3))

    def artistas_mais_ouvidos(self):
        tela.subtitulo("Artistas mais ouvidos")
        ranking = self.app.historico.artistas_mais_ouvidos(5)
        if not ranking:
            tela.aviso("O histórico está vazio.")
            return
        linhas = []
        posicao = 1
        for nome, vezes in ranking:
            linhas.append([f"{posicao}º", nome, vezes])
            posicao += 1
        tela.imprimir_tabela(["#", "Artista", "Reproduções"], linhas, a_direita=(0, 2))

    def historico_recente(self):
        tela.subtitulo("Últimas 20 reproduções")
        reproducoes = self.app.historico.ultimas(20)
        if not reproducoes:
            tela.aviso("O histórico está vazio.")
            return
        linhas = []
        for reproducao in reproducoes:
            musica = reproducao.musica
            linhas.append([reproducao.data_formatada(), musica.get_titulo(),
                           musica.get_artista().get_nome()])
        tela.imprimir_tabela(["Quando", "Título", "Artista"], linhas)

    def numeros_da_biblioteca(self):
        """Dicionário com os totais (usado na tela e no arquivo)."""
        app = self.app
        return {
            "Artistas": app.artistas.contar(),
            "Álbuns": app.albuns.contar(),
            "Músicas": app.musicas.contar(),
            "Playlists": app.playlists.contar(),
            "Reproduções no histórico": app.historico.contar(),
            "Duração da biblioteca": formatar_tempo(app.musicas.duracao_total()),
            "Tempo tocado (soma das faixas)": formatar_tempo(app.historico.tempo_total_ouvido()),
        }

    def resumo(self):
        tela.subtitulo("Resumo da biblioteca")
        for nome, valor in self.numeros_da_biblioteca().items():
            print(f"  {nome:.<30} {valor}")

    def exportar(self):
        """Grava um relatório em .txt (Aula 12: open, modo "w", write)."""
        agora = datetime.now()
        nome_arquivo = f"relatorio_{agora.strftime('%Y-%m-%d_%H%M%S')}.txt"
        caminho = os.path.join(self.app.pasta_dados, nome_arquivo)
        try:
            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write("TOCA AÍ - Relatório do player\n")
                arquivo.write(f"Gerado em {agora.strftime('%d/%m/%Y %H:%M')}\n\n")

                arquivo.write("RESUMO\n")
                for nome, valor in self.numeros_da_biblioteca().items():
                    arquivo.write(f"  {nome}: {valor}\n")

                arquivo.write("\nAS 10 MAIS TOCADAS\n")
                posicao = 1
                for musica, vezes in self.app.historico.mais_tocadas(10):
                    arquivo.write(f"  {posicao}. {musica} - {vezes} vez(es)\n")
                    posicao += 1

                arquivo.write("\nPLAYLISTS\n")
                for playlist in self.app.playlists.listar():
                    arquivo.write(f"  {playlist}\n")
                    numero = 1
                    for musica in playlist.get_musicas():
                        arquivo.write(f"     {numero}. {musica}\n")
                        numero += 1
        except OSError as problema:
            tela.erro(f"Não foi possível gravar o arquivo: {problema}")
            return
        tela.sucesso(f"Relatório salvo em: {caminho}")

    def limpar_historico(self):
        total = self.app.historico.contar()
        if total == 0:
            tela.aviso("O histórico já está vazio.")
            return
        if not entrada.confirmar(f"Apagar as {total} reproduções do histórico?"):
            tela.discreto("Nada foi apagado.")
            return
        apagadas = self.app.historico.limpar()
        tela.sucesso(f"{apagadas} reproduções apagadas. O ranking começa do zero.")
