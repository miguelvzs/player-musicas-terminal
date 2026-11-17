-- Script de criação do banco do Toca Aí (SQLite3).
-- É lido pela classe Banco (banco/conexao.py) toda vez que o programa abre.
-- "IF NOT EXISTS" faz o script poder rodar de novo sem apagar nada.

-- 1. Artista: quem canta/toca.
CREATE TABLE IF NOT EXISTS artista (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome  TEXT NOT NULL UNIQUE,
    pais  TEXT
);

-- 2. Álbum: pertence a UM artista (relação 1:N artista -> album).
--    Sem ON DELETE: o banco NÃO deixa excluir um artista que ainda tem álbuns.
CREATE TABLE IF NOT EXISTS album (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo      TEXT NOT NULL,
    ano         INTEGER,
    genero      TEXT,
    artista_id  INTEGER NOT NULL,
    FOREIGN KEY (artista_id) REFERENCES artista (id)
);

-- 3. Música: pertence a UM álbum (relação 1:N album -> musica).
--    "arquivo" é opcional: sem arquivo, a reprodução é simulada.
CREATE TABLE IF NOT EXISTS musica (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo            TEXT NOT NULL,
    duracao_segundos  INTEGER NOT NULL CHECK (duracao_segundos > 0),
    numero_faixa      INTEGER,
    arquivo           TEXT,
    album_id          INTEGER NOT NULL,
    FOREIGN KEY (album_id) REFERENCES album (id)
);

-- 4. Playlist: lista de músicas montada pelo usuário.
CREATE TABLE IF NOT EXISTS playlist (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT NOT NULL UNIQUE,
    descricao  TEXT,
    criada_em  TEXT NOT NULL
);

-- 5. Itens da playlist: tabela associativa da relação N:N playlist <-> musica.
--    A chave primária composta impede a mesma música duas vezes na mesma playlist.
--    ON DELETE CASCADE: apagar a playlist (ou a música) apaga os itens junto.
CREATE TABLE IF NOT EXISTS playlist_musica (
    playlist_id  INTEGER NOT NULL,
    musica_id    INTEGER NOT NULL,
    posicao      INTEGER NOT NULL,
    PRIMARY KEY (playlist_id, musica_id),
    FOREIGN KEY (playlist_id) REFERENCES playlist (id) ON DELETE CASCADE,
    FOREIGN KEY (musica_id) REFERENCES musica (id) ON DELETE CASCADE
);

-- 6. Histórico: cada vez que uma música começa a tocar vira uma linha aqui.
--    É a base do ranking de "mais tocadas" (COUNT + GROUP BY).
CREATE TABLE IF NOT EXISTS historico_reproducao (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    musica_id  INTEGER NOT NULL,
    tocada_em  TEXT NOT NULL,
    FOREIGN KEY (musica_id) REFERENCES musica (id) ON DELETE CASCADE
);
