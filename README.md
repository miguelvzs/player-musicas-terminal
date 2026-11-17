# Toca Aí: player e gerenciador de músicas no terminal

Programa em **Python**, feito com **Orientação a Objetos** e banco **SQLite3**. Ele guarda uma
biblioteca de músicas (artistas, álbuns, músicas e playlists) e **toca as músicas** no terminal.

Atividade Avaliativa 04 de Programação Orientada a Objetos (ADS, 2º semestre, IFSP Bragança Paulista).
Autor: Miguel (https://github.com/miguelvzs).

## 1. Como rodar

Precisa do **Python 3.10 ou mais novo**. Não precisa instalar nenhuma biblioteca.

```bash
git clone https://github.com/miguelvzs/player-musicas-terminal.git
cd player-musicas-terminal
python main.py
```

- `python main.py --sem-som` roda sem som: o tempo e a barra de progresso andam, mas não sai áudio.
- Na primeira vez, o programa cria a pasta `dados/` com o banco `player.db`, as tabelas, os dados de
  exemplo e as músicas. Isso leva cerca de meio minuto.
- Para sair, use a opção `0` do menu. O Ctrl+C também sai sem quebrar.
- Para começar do zero, apague a pasta `dados/`.

## 2. O que o programa faz

| Menu principal | O que tem dentro |
|---|---|
| 1 Player | Tocar, pausar, próxima, anterior, parar, modo aleatório, repetir, ver a fila, ouvir com a barra andando |
| 2 Músicas | Listar, cadastrar, editar, excluir, buscar, tocar uma música, adicionar a uma playlist |
| 3 Álbuns | Listar, cadastrar, ver as faixas, editar, excluir |
| 4 Artistas | Listar, cadastrar, ver os álbuns, editar, excluir |
| 5 Playlists | Criar, ver, adicionar e remover músicas, mudar a posição, editar, excluir, tocar |
| 6 Buscar música | Procura pelo título, artista, álbum ou gênero |
| 7 Histórico e relatórios | 10 mais tocadas, artistas mais ouvidos, histórico, resumo, exportar `.txt`, limpar |
| 0 Sair | Pede confirmação antes de fechar |

## 3. Como o código está organizado (Aula 11: módulos e pacotes)

Cada pasta é um **pacote** (tem `__init__.py`) e cada arquivo é um **módulo** que o `main.py` importa.

```text
main.py          começa o programa: abre o banco, cria as tabelas e chama o menu
banco/           a conexão com o SQLite3 e o script das tabelas (schema.sql)
modelos/         as classes dos dados: Artista, Album, Musica, Playlist, Reproducao
repositorios/    o CRUD de cada tabela (INSERT, SELECT, UPDATE, DELETE)
interface/       os menus e as telas do terminal
audio/           o player, as saídas de som e as músicas geradas pelo programa
utils/           leitura do teclado, desenho da tela e conversão de tempo
testes/          testes automáticos
```

Caminho de uma ação: **menu → repositório → `Banco` → SQLite**. O menu nunca escreve SQL. Quem
escreve SQL é o repositório, e só a classe `Banco` fala com o SQLite.

## 4. Banco de dados (Aula 15: SQLite3)

São **6 tabelas** ligadas por chaves estrangeiras. O script está em `banco/schema.sql`.

```text
artista 1 ──< N album 1 ──< N musica 1 ──< N historico_reproducao
                                 │
                       playlist_musica (N:N, guarda a posição)
                                 │
                              playlist
```

| Tabela | Guarda | Regra importante |
|---|---|---|
| `artista` | quem canta ou toca | nome obrigatório e único |
| `album` | os álbuns de cada artista (1:N) | não deixa excluir um artista que ainda tem álbum |
| `musica` | as faixas de cada álbum (1:N) | duração maior que zero; não deixa excluir um álbum que ainda tem música |
| `playlist` | as listas do usuário | nome obrigatório e único |
| `playlist_musica` | a ligação N:N entre playlist e música | a mesma música não entra duas vezes na mesma playlist |
| `historico_reproducao` | cada vez que uma música tocou | é a base do ranking de mais tocadas |

A classe **`Banco`** (`banco/conexao.py`) usa os comandos da Aula 15:

- `sqlite3.connect()` abre a conexão e `cursor()` cria o cursor;
- `execute(sql, parametros)` executa o SQL, sempre com `?` no lugar dos valores, o que impede SQL injection;
- `commit()` grava e `rollback()` desfaz se der erro;
- `fetchall()` e `fetchone()` leem o resultado;
- `lastrowid` dá o id gerado no INSERT e `close()` fecha a conexão.

O **CRUD** foi escrito uma vez só, na classe `RepositorioBase` (`repositorios/base.py`). É o exercício
da Aula 15, "refatorar o CRUD diminuindo codificação". Cada repositório filho só informa a tabela e as
colunas.

## 5. Orientação a Objetos (Aula 14)

| Conceito da aula | Onde está no código |
|---|---|
| Classe, objeto, `__init__` e `self` | todas as classes, por exemplo `Artista("Os Bits Errantes", "Brasil")` |
| Atributo com valor padrão | `Artista(nome, pais="")`, `Album(..., ano=None, genero="")` |
| Método que valida | `set_nome()`, `set_ano()` e `set_duracao()` não aceitam valor errado e avisam com `ValueError` |
| Encapsulamento `_` e `__` com get/set | `self._id` em `Entidade`; `self.__nome` em `Artista`; `self.__conexao` em `Banco`; acesso por `get_nome()` / `set_nome()` |
| `__str__` e `__repr__` | `__str__` em cada modelo (o que o `print` mostra); `__repr__` em `Entidade` |
| Herança com `super().__init__()` | `Entidade` é mãe dos 5 modelos; `RepositorioBase` é mãe dos 5 repositórios; `MenuBase` é mãe dos 7 menus; `SaidaAudio` é mãe das saídas de som |
| Sobrescrita (polimorfismo) | cada repositório sobrescreve `para_tupla()` e `para_objeto()`; cada menu sobrescreve `opcoes()`; cada saída de som sobrescreve `tocar()`, `pausar()` e `parar()` |
| Instância como atributo (associação) | um `Album` tem um `Artista`; uma `Musica` tem um `Album`; o `Player` tem uma saída de som |

## 6. Tratamento de erros (Aula 13: try/except)

O programa **não quebra** com entrada errada:

- `utils/entrada.py` repete a pergunta até a resposta ser válida (`while True` + `try/except ValueError`).
  Por exemplo, digitar `abc` onde se pede um número.
- `MenuBase.executar_acao()` trata `ValueError` (dado inválido) e `sqlite3.Error` (problema no banco)
  e mostra uma mensagem em vez de parar.
- O `main.py` trata o Ctrl+C e, no `finally`, **sempre** fecha o banco.

## 7. Arquivos (Aula 12)

- O `Banco` lê o `banco/schema.sql` com `with open(..., "r")` para criar as tabelas.
- O menu de relatórios grava um relatório em `.txt` com `with open(..., "w")` e `write()`.
- As datas do histórico usam o módulo `datetime` (Aula 11).

## 8. O enunciado e onde cada item foi atendido

| O enunciado pede | Onde está |
|---|---|
| Python com Orientação a Objetos e terminal integrado ao SQLite3 | seções 4 e 5 |
| Menu com entrada e saída, sem erros ou interrupções abruptas | seções 2 e 6 |
| No mínimo 4 tabelas relacionais | 6 tabelas, seção 4 |
| CRUD | artistas, álbuns, músicas e playlists: criar, listar, editar e excluir |
| Responsabilidades separadas em arquivos e módulos | seção 3 |
| Criatividade | o som e as músicas geradas pelo programa (seção 9) |
| README com instruções e bibliotecas | seções 1 e 10 |

## 9. Parte criativa: o som

Esta parte vai além das aulas. Usei módulos da biblioteca padrão que pesquisei para gravar e tocar som.

- **Tocar:**
  - No Windows, o som sai pelo módulo `winsound`, sem instalar nada.
  - Com o `pygame` instalado (`pip install pygame`), ele é usado no lugar.
  - Sem nenhum dos dois, a reprodução é simulada.
- **Músicas geradas pelo programa:** não há gravação nenhuma. O programa calcula as ondas e grava os
  arquivos `.wav`:
  - 12 melodias curtas, calculadas com `math`;
  - 11 músicas em estilo de videogame de 16 bits (classes `Canal` e `Trilha`). Uma `Trilha` tem
    vários `Canal`, que é o mesmo conceito de instância como atributo da Aula 14.
- **Direitos autorais:** as músicas em 16 bits são clássicos em domínio público (Beethoven, Grieg,
  Mozart, Offenbach, Richard Strauss e a canção russa Korobeiniki) e temas de jogo compostos para o
  projeto.
- **Limitação:** sem threads, o player só passa para a próxima música quando você mexe no menu ou
  usa a opção "Ouvir", que deixa a fila seguir sozinha.

## 10. Bibliotecas

Todas são da biblioteca padrão do Python, menos o `pygame`, que é opcional.

| Biblioteca | Para quê | Aula |
|---|---|---|
| `sqlite3` | banco de dados | 15 |
| `datetime` | data e hora do histórico e das playlists | 11 |
| `math` | cálculo das ondas das músicas | 11 |
| `random` | modo aleatório do player | laboratórios |
| `os`, `sys` | caminhos de arquivos e opções da linha de comando | — |
| `time` | relógio do player | — |
| `struct`, `wave`, `array`, `tempfile`, `winsound` | gravar e tocar `.wav` (parte criativa) | — |
| `unittest` | testes automáticos | — |
| `pygame` | som opcional (`pip install pygame`) | — |

## 11. Testes

```bash
python -m unittest
```

São 72 testes automáticos. Um deles roda o programa inteiro digitando as respostas do arquivo
`testes/roteiro_completo.txt`, que passa por todos os menus com entradas erradas no meio, e confere que
nada quebra.
