"""Dados de exemplo para o primeiro uso.

Tudo aqui é FICTÍCIO: artistas, álbuns e melodias foram inventados para o
projeto. As músicas são geradas pelo próprio programa (audio/gerador_wav.py),
então o repositório não tem nenhuma música com direitos autorais.
"""

import os
from datetime import datetime, timedelta

from audio.gerador_wav import duracao_do_wav, gerar_wav
from modelos.album import Album
from modelos.artista import Artista
from modelos.musica import Musica
from modelos.playlist import Playlist
from modelos.reproducao import FORMATO_BANCO, Reproducao
from repositorios.album_repositorio import AlbumRepositorio
from repositorios.artista_repositorio import ArtistaRepositorio
from repositorios.historico_repositorio import HistoricoRepositorio
from repositorios.musica_repositorio import MusicaRepositorio
from repositorios.playlist_repositorio import PlaylistRepositorio

PASTA_DEMO = "musicas_demo"     # fica dentro da pasta de dados (ao lado do .db)

ARTISTAS = [
    ("Os Bits Errantes", "Brasil"),
    ("Lua de Silício", "Portugal"),
    ("Trio Senoidal", "Brasil"),
    ("DJ Hertz", "Argentina"),
    ("Quarteto Fantasma", "Brasil"),      # sem álbum: pode ser excluído na demonstração
]

# (título, ano, gênero, artista)
ALBUNS = [
    ("8 Bits de Saudade", 2024, "Chiptune", "Os Bits Errantes"),
    ("Commit Final", 2026, "Chiptune", "Os Bits Errantes"),
    ("Maré de Silício", 2025, "Synthpop", "Lua de Silício"),
    ("Forró em Dó Maior", 2023, "Forró eletrônico", "Trio Senoidal"),
    ("Frequência Fundamental", 2026, "Eletrônica", "DJ Hertz"),
]

# Cada música é um dicionário (Aula 09). "notas" usa NOTA:TEMPOS; R = pausa.
MUSICAS = [
    {"titulo": "Loop Infinito", "album": "8 Bits de Saudade", "faixa": 1,
     "arquivo": "loop_infinito.wav", "bpm": 150, "forma": "quadrada", "repeticoes": 2,
     "notas": "C5:1 E5:1 G5:1 E5:1 F5:1 A5:1 C6:2 B5:1 G5:1 D5:1 G5:1 C5:4"},
    {"titulo": "Commit às 23:59", "album": "8 Bits de Saudade", "faixa": 2,
     "arquivo": "commit_as_2359.wav", "bpm": 170, "forma": "quadrada", "repeticoes": 2,
     "notas": "A4:0.5 C5:0.5 E5:0.5 A5:0.5 G5:1 E5:1 F5:0.5 E5:0.5 D5:0.5 C5:0.5 "
              "D5:2 E5:0.5 G5:0.5 C6:1 B5:1 A5:3"},
    {"titulo": "Exceção Não Tratada", "album": "Commit Final", "faixa": 1,
     "arquivo": "excecao_nao_tratada.wav", "bpm": 140, "forma": "triangulo", "repeticoes": 2,
     "notas": "E4:1 G4:1 B4:1 E5:1 D5:1 B4:1 G4:1 A4:1 F#4:1 A4:1 C5:1 B4:3"},
    {"titulo": "Self Sem Underscore", "album": "Commit Final", "faixa": 2,
     "arquivo": "self_sem_underscore.wav", "bpm": 132, "forma": "quadrada", "repeticoes": 2,
     "notas": "G4:1 G4:0.5 A4:0.5 B4:1 D5:1 C5:1 A4:1 B4:2 G4:1 E4:1 F#4:1 D4:1 G4:2"},
    {"titulo": "Chave Estrangeira", "album": "Maré de Silício", "faixa": 1,
     "arquivo": "chave_estrangeira.wav", "bpm": 100, "forma": "seno", "repeticoes": 1,
     "notas": "A4:1 C5:1 E5:2 D5:1 C5:1 B4:2 G4:1 B4:1 D5:2 C5:1 B4:1 A4:4"},
    {"titulo": "Fetchall do Amor", "album": "Maré de Silício", "faixa": 2,
     "arquivo": "fetchall_do_amor.wav", "bpm": 96, "forma": "seno", "repeticoes": 1,
     "notas": "F4:1 A4:1 C5:1 F5:1 E5:2 C5:2 D5:1 Bb4:1 G4:1 Bb4:1 A4:4"},
    {"titulo": "Cursor Perdido", "album": "Maré de Silício", "faixa": 3,
     "arquivo": "cursor_perdido.wav", "bpm": 110, "forma": "triangulo", "repeticoes": 1,
     "notas": "D5:1 A4:1 F4:1 A4:1 D5:1 E5:1 F5:2 E5:1 C5:1 A4:1 C5:1 D5:4"},
    {"titulo": "Xote do Ponto e Vírgula", "album": "Forró em Dó Maior", "faixa": 1,
     "arquivo": "xote_do_ponto_e_virgula.wav", "bpm": 150, "forma": "triangulo", "repeticoes": 2,
     "notas": "C5:0.5 C5:0.5 E5:1 G5:0.5 F5:0.5 E5:1 D5:0.5 D5:0.5 F5:1 "
              "A5:0.5 G5:0.5 F5:1 E5:0.5 D5:0.5 C5:2"},
    {"titulo": "Baião do Banco de Dados", "album": "Forró em Dó Maior", "faixa": 2,
     "arquivo": "baiao_do_banco_de_dados.wav", "bpm": 140, "forma": "quadrada", "repeticoes": 2,
     "notas": "G4:0.5 B4:0.5 D5:1 B4:0.5 D5:0.5 G5:1 F5:0.5 E5:0.5 D5:1 C5:0.5 B4:0.5 A4:1 G4:2"},
    {"titulo": "440 Hz", "album": "Frequência Fundamental", "faixa": 1,
     "arquivo": "440_hz.wav", "bpm": 128, "forma": "seno", "repeticoes": 3,
     "notas": "A4:0.5 A4:0.5 A5:0.5 A4:0.5 E5:0.5 A4:0.5 G5:0.5 A4:0.5 "
              "C5:0.5 A4:0.5 D5:0.5 A4:0.5 E5:2"},
    {"titulo": "Bateria de 70 kWh", "album": "Frequência Fundamental", "faixa": 2,
     "arquivo": "bateria_de_70_kwh.wav", "bpm": 124, "forma": "quadrada", "repeticoes": 3,
     "notas": "C4:0.5 C5:0.5 C4:0.5 C5:0.5 Eb4:0.5 Eb5:0.5 F4:0.5 F5:0.5 "
              "G4:0.5 G5:0.5 Bb4:0.5 G5:0.5 C5:2"},
    {"titulo": "Herança Múltipla", "album": "Frequência Fundamental", "faixa": 3,
     "arquivo": "heranca_multipla.wav", "bpm": 118, "forma": "seno", "repeticoes": 1,
     "notas": "E4:1 B4:1 E5:1 G5:1 F#5:1 D5:1 B4:2 C5:1 E5:1 A5:1 G5:1 F#5:4"},
]

# (nome, descrição, títulos das músicas na ordem)
PLAYLISTS = [
    ("Para codar", "Trilha para programar sem bug",
     ["Loop Infinito", "Exceção Não Tratada", "Cursor Perdido", "440 Hz", "Bateria de 70 kWh"]),
    ("Seminário de POO", "Para o dia da apresentação",
     ["Self Sem Underscore", "Herança Múltipla", "Chave Estrangeira", "Fetchall do Amor"]),
    ("Forró do IFSP", "Arrasta-pé no intervalo",
     ["Xote do Ponto e Vírgula", "Baião do Banco de Dados"]),
]

# Histórico inicial (fictício), para o ranking não começar vazio: (título, vezes)
HISTORICO = [
    ("Loop Infinito", 5),
    ("Commit às 23:59", 4),
    ("440 Hz", 3),
    ("Chave Estrangeira", 2),
    ("Xote do Ponto e Vírgula", 1),
]


def garantir_arquivos_demo(pasta_dados, avisar=print):
    """Gera os .wav de demonstração que ainda não existem. Devolve quantos gerou."""
    pasta = os.path.join(pasta_dados, PASTA_DEMO)
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    faltando = []
    for musica in MUSICAS:
        if not os.path.exists(os.path.join(pasta, musica["arquivo"])):
            faltando.append(musica)
    if faltando:
        avisar(f"Gerando {len(faltando)} música(s) de demonstração em {pasta} (só na primeira vez)...")
        for musica in faltando:
            destino = os.path.join(pasta, musica["arquivo"])
            # Grava com outro nome e só renomeia no fim: se o programa for
            # interrompido no meio, não fica um .wav pela metade.
            provisorio = destino + ".parcial"
            gerar_wav(provisorio, musica["notas"], bpm=musica["bpm"],
                      forma=musica["forma"], repeticoes=musica["repeticoes"])
            os.replace(provisorio, destino)
    return len(faltando)


def popular(banco, pasta_dados):
    """Grava os dados de exemplo usando os próprios repositórios (o mesmo CRUD da aplicação)."""
    artistas = ArtistaRepositorio(banco)
    albuns = AlbumRepositorio(banco)
    musicas = MusicaRepositorio(banco)
    playlists = PlaylistRepositorio(banco)
    historico = HistoricoRepositorio(banco)

    artistas_por_nome = {}
    for nome, pais in ARTISTAS:
        artistas_por_nome[nome] = artistas.inserir(Artista(nome, pais))

    albuns_por_titulo = {}
    for titulo, ano, genero, nome_artista in ALBUNS:
        album = Album(titulo, artistas_por_nome[nome_artista], ano, genero)
        albuns_por_titulo[titulo] = albuns.inserir(album)

    musicas_por_titulo = {}
    for dados in MUSICAS:
        caminho_completo = os.path.join(pasta_dados, PASTA_DEMO, dados["arquivo"])
        duracao = duracao_do_wav(caminho_completo)
        # Grava o caminho relativo à pasta de dados (funciona mesmo se a pasta mudar de lugar).
        arquivo = PASTA_DEMO + "/" + dados["arquivo"]
        musica = Musica(dados["titulo"], albuns_por_titulo[dados["album"]], duracao,
                        faixa=dados["faixa"], arquivo=arquivo)
        musicas_por_titulo[dados["titulo"]] = musicas.inserir(musica)

    for nome, descricao, titulos in PLAYLISTS:
        playlist = playlists.inserir(Playlist(nome, descricao))
        for titulo in titulos:
            playlists.adicionar_musica(playlist.get_id(), musicas_por_titulo[titulo].get_id())

    agora = datetime.now()
    horas_atras = 1
    for titulo, vezes in HISTORICO:
        for _ in range(vezes):
            quando = (agora - timedelta(hours=horas_atras)).strftime(FORMATO_BANCO)
            historico.inserir(Reproducao(musicas_por_titulo[titulo], quando))
            horas_atras += 7
