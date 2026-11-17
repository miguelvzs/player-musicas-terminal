"""Tabelas prontas para mostrar artistas, álbuns, músicas e playlists.

Ficam num módulo separado porque vários menus mostram as mesmas listas.
"""

from utils import tela


def mostrar_artistas(artistas_com_total):
    """Recebe tuplas (Artista, total de álbuns)."""
    if not artistas_com_total:
        tela.aviso("Nenhum artista cadastrado.")
        return
    linhas = []
    for artista, total in artistas_com_total:
        linhas.append([artista.get_id(), artista.get_nome(), artista.get_pais() or "-", total])
    tela.imprimir_tabela(["ID", "Nome", "País", "Álbuns"], linhas, a_direita=(0, 3))


def mostrar_albuns(albuns_com_total):
    """Recebe tuplas (Album, total de músicas)."""
    if not albuns_com_total:
        tela.aviso("Nenhum álbum cadastrado.")
        return
    linhas = []
    for album, total in albuns_com_total:
        linhas.append([
            album.get_id(),
            album.get_titulo(),
            album.get_artista().get_nome(),
            album.get_ano() or "-",
            album.get_genero() or "-",
            total,
        ])
    tela.imprimir_tabela(["ID", "Título", "Artista", "Ano", "Gênero", "Faixas"], linhas,
                         a_direita=(0, 3, 5))


def mostrar_musicas(musicas, numerar=False, destacar=None):
    """Mostra músicas. numerar=True usa 1, 2, 3... no lugar do ID (para filas).
    destacar: posição (começando em 1) que recebe a marca ">>"."""
    if not musicas:
        tela.aviso("Nenhuma música encontrada.")
        return
    linhas = []
    numero = 1
    for musica in musicas:
        if numerar:
            marca = ">>" if numero == destacar else ""
            primeira = f"{marca} {numero}".strip()
        else:
            primeira = musica.get_id()
        linhas.append([
            primeira,
            musica.get_titulo(),
            musica.get_artista().get_nome(),
            musica.get_album().get_titulo(),
            musica.duracao_formatada(),
        ])
        numero += 1
    if numerar:
        cabecalho = "#"
    else:
        cabecalho = "ID"
    tela.imprimir_tabela([cabecalho, "Título", "Artista", "Álbum", "Duração"], linhas,
                         a_direita=(0, 4))


def mostrar_playlists(playlists):
    if not playlists:
        tela.aviso("Nenhuma playlist cadastrada.")
        return
    linhas = []
    for playlist in playlists:
        linhas.append([
            playlist.get_id(),
            playlist.get_nome(),
            playlist.quantidade(),
            playlist.duracao_total_formatada(),
            playlist.get_descricao() or "-",
        ])
    tela.imprimir_tabela(["ID", "Nome", "Músicas", "Duração", "Descrição"], linhas,
                         a_direita=(0, 2, 3))
