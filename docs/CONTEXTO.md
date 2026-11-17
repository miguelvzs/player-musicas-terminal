# Contexto do projeto

Documento escrito antes do código. Diz o que o projeto é, o que entra, o que fica de fora e quais
decisões já foram tomadas. Se o código e este arquivo divergirem, um dos dois está errado.

## 1. Objetivo

Atividade Avaliativa 04 de Programação Orientada a Objetos (ADS, 2º semestre, IFSP Bragança Paulista).
Entrega: 17/11/2026, 23:59. Vale 5,0 pontos, com seminário individual.

Tema: **Toca Aí**, um player e gerenciador de músicas que roda no terminal, feito em Python com
Orientação a Objetos e banco SQLite3.

## 2. O que o enunciado pede (Moodle)

| # | Requisito |
|---|---|
| R1 | Aplicação em Python, paradigma de Orientação a Objetos, interface ou terminal integrada com SQLite3 |
| R2 | Menu de opções com entrada e saída da aplicação, sem erros ou interrupções abruptas |
| R3 | Banco SQLite3 com no mínimo 4 tabelas relacionais |
| R4 | Manutenção das tabelas por CRUD (create, read, update, delete) conforme a necessidade |
| R5 | Responsabilidades separadas em arquivos/módulos |
| R6 | Ser criativo, original |
| R7 | Repositório no GitHub (abre sem login) com README: instruções de uso e bibliotecas instaladas |
| R8 | Entregar o link do repositório e um .zip com todos os arquivos |

## 3. Base de conteúdo (não extrapolar)

Só o que foi dado no semestre, nas aulas da professora (repositório `IFSP_BRA_LP2I2`):

- Aula 11: módulos, `import`, pacotes com `__init__.py`, módulo `datetime`, `math`.
- Aula 12: arquivos (`open`, modos `r`/`w`/`a`, `write`, `read`, caminhos).
- Aula 13: exceções (`try`/`except`/`else`/`finally`).
- Aula 14: classes, `__init__`, `self`, atributos com valor padrão, métodos que validam, herança com
  `super().__init__()`, sobrescrita, instância como atributo (associação), módulos, encapsulamento
  com `_` e `__` e métodos get/set, `__str__` e `__repr__`.
- Aula 15: `sqlite3` (`connect`, `cursor`, `execute` com `?`, `commit`, `rollback`, `fetchall`,
  `fetchone`, `lastrowid`, `close`) e o exercício "refatorar o CRUD diminuindo codificação".

Fica de fora: ORM, dataclasses, `@property`, classes abstratas (`abc`), threads, async, type hints,
frameworks de interface de terminal.

## 4. Entra

- 6 tabelas com chaves estrangeiras de verdade (`PRAGMA foreign_keys = ON`): `artista`, `album`,
  `musica`, `playlist`, `playlist_musica` (N:N com posição) e `historico_reproducao`.
- CRUD de artistas, álbuns, músicas e playlists; adicionar, remover e reordenar músicas na playlist;
  busca; histórico e ranking de mais tocadas; exportar relatório para `.txt`.
- Player: tocar, pausar/continuar, parar, próxima, anterior, aleatório, repetir (fila ou faixa),
  fila a partir de todas as músicas, de um álbum, de uma playlist ou das mais tocadas, e um modo
  "ouvir ao vivo" com barra de progresso.
- Áudio real quando possível, sem instalar nada no Windows; reprodução simulada (só o tempo) quando
  não houver como tocar.
- Músicas de demonstração geradas pelo próprio programa (`wave`, `math`, `struct`), com dados
  fictícios. Nenhuma música com direitos autorais.
- Testes com `unittest` e banco temporário; roteiro de execução pelo `stdin`.

## 5. Não entra

- Interface gráfica, web ou API.
- Tocar MP3 sem biblioteca extra (o `winsound` só toca `.wav`; com `pygame` instalado, toca também
  `.mp3` e `.ogg`).
- Avanço automático de faixa enquanto o programa espera uma digitação no menu (precisaria de
  threads, que não foram vistas). O player confere o tempo a cada interação e no modo "ouvir".
- Login, usuários, nuvem.

## 6. Decisões

### Tomadas

| # | Decisão | Motivo |
|---|---|---|
| D1 | Nome do app: **Toca Aí**. Repositório: `player-musicas-terminal` | Curto e descritivo; pode ser trocado sem impacto no código |
| D2 | Uma conexão aberta durante toda a execução, fechada no `finally` do `main.py` | O `PRAGMA foreign_keys` vale por conexão; abrir e fechar a cada método (como no exemplo MySQL da Aula 15) obrigaria a repetir o PRAGMA |
| D3 | Excluir artista com álbum ou álbum com música é **bloqueado** pelo banco (FK sem cascata); a tela explica o motivo | Mostra a integridade referencial funcionando |
| D4 | Excluir playlist apaga seus itens; excluir música tira a música das playlists e do histórico (`ON DELETE CASCADE`) | Itens e histórico não existem sem a música/playlist |
| D5 | A mesma música não entra duas vezes na mesma playlist (chave primária `playlist_id, musica_id`) | Simplifica a reordenação |
| D6 | Saída de áudio por polimorfismo: `pygame` se instalado; senão `winsound` (Windows, biblioteca padrão); senão simulada | Funciona sem instalar nada e nunca quebra |
| D7 | Validação nos modelos com `raise ValueError`, tratada nas telas com `try/except` | A regra fica num lugar só (encapsulamento, Aula 14) |
| D8 | Banco em `dados/player.db`, criado na primeira execução pelo `banco/schema.sql`; `dados/` fica fora do Git | O enunciado pede o script de criação, não o arquivo do banco |
| D9 | Uma reprodução entra no histórico quando a faixa começa a tocar | Regra simples de explicar para o ranking |

### Abertas

| # | Decisão | Recomendação | Quem decide |
|---|---|---|---|
| A1 | Tema confirmado com a professora ("antes de iniciar, conversar com a professora sobre o tema") | Mostrar este documento e o README para ela antes da entrega | Miguel, com a professora |
