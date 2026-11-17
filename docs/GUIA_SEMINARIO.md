# Guia do seminário (AA04): roteiro de ~10 minutos

Roteiro para apresentar o Toca Aí e explicar o código. Os números de linha (`arquivo:linha`) valem
para a versão deste repositório; se mudar o código, confira de novo.

## Antes de apresentar

- [ ] Rodar `python main.py` uma vez antes (a primeira execução gera o banco e as músicas e demora
      alguns segundos). Para começar limpo, apague a pasta `dados/` e rode de novo.
- [ ] Volume do computador baixo. Se o som atrapalhar, use `python main.py --sem-som`.
- [ ] Editor aberto com: `banco/schema.sql`, `banco/conexao.py`, `modelos/artista.py`,
      `repositorios/base.py`, `audio/saidas.py`, `audio/player.py`, `main.py`.
- [ ] Terminal aberto na pasta do projeto e o README aberto no GitHub.
- [ ] Rodar `python -m unittest` uma vez para mostrar os testes passando (leva uns 30 s).

## Roteiro

| Tempo | O que falar | O que mostrar |
|---|---|---|
| 0:00 a 1:00 | O que é o projeto: um player de músicas no terminal, com banco SQLite3 e Orientação a Objetos. As músicas de exemplo são geradas pelo próprio programa (nada com direitos autorais) | `python main.py` → **1 Player** → **9** → **3** (playlist) → **2** "Seminário de POO". Mostrar **1** pausar, **2** próxima, **5** aleatório, **8** ouvir ao vivo e Ctrl+C para voltar |
| 1:00 a 3:00 | **Banco (Aula 15)**: 6 tabelas, chaves estrangeiras, a tabela N:N `playlist_musica` com a posição, `ON DELETE CASCADE` x exclusão bloqueada. A classe `Banco` faz o `connect`, liga o `PRAGMA foreign_keys`, usa `cursor`, `execute` com `?`, `commit`, `rollback`, `fetchall`, `fetchone` e `close` | `banco/schema.sql`; `banco/conexao.py`. No programa: **4 Artistas** → **5 Excluir** → ID 1 → `s` → mensagem "este artista ainda tem álbuns" (a FK funcionando) |
| 3:00 a 6:00 | **Orientação a Objetos (Aula 14)**: classe, `__init__`, `self`; encapsulamento com `_` e `__` e get/set que valida; `__str__`/`__repr__`; herança com `super().__init__()`; sobrescrita e polimorfismo; associação (instância como atributo) | `modelos/entidade.py`, `modelos/artista.py`, `modelos/musica.py`; `repositorios/base.py` + `repositorios/artista_repositorio.py`; `audio/saidas.py` |
| 6:00 a 7:30 | **Módulos e pacotes (Aula 11)**, **arquivos (Aula 12)** e **exceções (Aula 13)**: cada pasta é um pacote; o programa lê o `schema.sql`, grava relatório `.txt` e `.wav`; nenhuma entrada errada derruba o programa | Árvore de pastas no README; `utils/entrada.py`; `interface/menu_base.py`; `main.py`. No programa: digitar `abc` num menu e numa pergunta de número |
| 7:30 a 9:00 | **Player**: estados (parado, tocando, pausado), relógio com `time.time()`, aleatório com `random.shuffle`, repetir, histórico e ranking com `COUNT` e `GROUP BY` | `audio/player.py`; `repositorios/historico_repositorio.py`. No programa: **7 Histórico e relatórios** → **1** e **5** (exporta `.txt`) |
| 9:00 a 10:00 | **Testes e entrega**: 60 testes com `unittest` e banco temporário, roteiro que passa por todos os menus; repositório público e README | `python -m unittest`; `testes/roteiro_completo.txt`; GitHub |

## Onde está cada conceito

### Banco de dados (Aula 15)

| Conceito | Onde | Como explicar |
|---|---|---|
| Criação das tabelas | `banco/schema.sql:6` em diante | 6 `CREATE TABLE IF NOT EXISTS`; o `IF NOT EXISTS` deixa rodar de novo sem apagar nada |
| Chave estrangeira | `banco/schema.sql:20`, `:32`, `:51`, `:52`, `:61` | `FOREIGN KEY ... REFERENCES`; sem `ON DELETE` o banco bloqueia a exclusão do "pai" |
| N:N com chave composta | `banco/schema.sql:46` a `:53` | `playlist_musica` liga playlist e música; `PRIMARY KEY (playlist_id, musica_id)` impede repetir |
| `CHECK` e `UNIQUE` | `banco/schema.sql:8`, `:28`, `:38` | O próprio banco recusa duração 0 e nome repetido |
| `sqlite3.connect` | `banco/conexao.py:28` | Abre (ou cria) o arquivo `.db` |
| `PRAGMA foreign_keys = ON` | `banco/conexao.py:31` | No SQLite as FKs vêm desligadas; vale por conexão |
| Ler o script `.sql` | `banco/conexao.py:35` a `:37` | `with open(...)` (Aula 12) + `executescript` |
| `cursor`, `execute` com `?`, `commit` | `banco/conexao.py:47` a `:50` | Os valores vão separados do SQL: consulta parametrizada, evita SQL injection |
| `rollback` | `banco/conexao.py:52` e `:68` | Se der erro, desfaz o que não foi confirmado |
| Transação com vários comandos | `banco/conexao.py:56` (`executar_varios`) | Renumerar a playlist: ou grava tudo, ou nada |
| `fetchall` / `fetchone` | `banco/conexao.py:71` e `:77` | Lista de tuplas / uma tupla ou `None` |
| `lastrowid` | `repositorios/base.py:49` | O id gerado pelo `AUTOINCREMENT` volta para o objeto |
| `close` | `banco/conexao.py:83`, chamado no `finally` de `main.py:83` | A conexão fecha sempre, até se der erro |
| `JOIN` | `repositorios/album_repositorio.py:8` a `:12` | O álbum volta do banco já com o artista dentro |
| `LIKE` (busca) | `repositorios/musica_repositorio.py:66` | `%termo%` em título, artista, álbum e gênero |
| `COUNT` + `GROUP BY` (ranking) | `repositorios/historico_repositorio.py:53` | Conta as reproduções por música e ordena |
| `if __name__ == "__main__"` | `main.py:86` | Aula 15, item 1.7: só roda quando o arquivo é executado, não quando é importado |

### Orientação a Objetos (Aula 14)

| Conceito | Onde | Como explicar |
|---|---|---|
| Classe, `__init__`, `self` | `modelos/artista.py:6` a `:15` | `__init__` roda sozinho ao criar o objeto; `self` é o próprio objeto |
| Atributo com valor padrão | `modelos/playlist.py:23` (`self.__musicas = []`); `audio/player.py:35` em diante | Não vem por parâmetro, já nasce com valor (como o `leitura_hodometro = 0`) |
| Fracamente privado (`_`) | `modelos/entidade.py:14` (`self._id`) | Só um aviso: dá para acessar de fora, mas não se deve |
| Fortemente privado (`__`) | `modelos/artista.py:11`; `banco/conexao.py:21` | De fora, `artista.__nome` dá `AttributeError`; só `artista._Artista__nome` (testado em `testes/test_modelos.py`) |
| get/set com validação | `modelos/artista.py:19`; `modelos/musica.py:54` (`set_duracao`) | Igual ao `atualizar_hodometro`: a regra fica num lugar só. Se o valor é inválido, `raise ValueError` |
| `__str__` e `__repr__` | `modelos/artista.py:39`; `modelos/entidade.py:26` | `print(artista)` usa o `__str__` ("DJ Hertz (Argentina)"); o `__repr__` é para o programador (`<Artista id=4>`) |
| Herança + `super().__init__()` (modelos) | `modelos/artista.py:6` e `:10` | `Artista(Entidade)`: o id é tratado uma vez só, na mãe |
| Herança (repositórios) | `repositorios/base.py:9`; `repositorios/artista_repositorio.py:7` e `:11` | O CRUD inteiro está na mãe. É a resposta ao exercício da Aula 15: "refatorar, diminuindo codificação" |
| Sobrescrita / polimorfismo (repositórios) | `repositorios/base.py:35` e `:38`; `repositorios/artista_repositorio.py:19` e `:22`; `repositorios/playlist_repositorio.py:27` | `inserir()` da mãe chama `self.para_tupla()`, e vale a versão da filha. A playlist sobrescreve `para_objeto` para já carregar as músicas |
| Herança (menus) | `interface/menu_base.py:8`; `interface/menu_artistas.py:11` e `:14` | O laço do menu está na mãe (`executar`, linha 39); cada filha só diz as opções |
| Polimorfismo (saídas de áudio) | `audio/saidas.py:28`, `:61`, `:97`, `:128` | O Player chama `saida.tocar()` sem saber se é pygame, winsound ou simulada |
| Associação (instância como atributo) | `modelos/album.py:43`; `modelos/musica.py:46`; `audio/player.py:35` e `:36`; `repositorios/album_repositorio.py:27` | "Tem um" (associação) x "é um" (herança). `musica.get_artista()` atravessa música → álbum → artista |
| Módulos e pacotes (Aula 11) | Pastas com `__init__.py`; imports no topo de cada arquivo | `from modelos.artista import Artista`, nunca `import *` (a aula diz que não é recomendado) |

### Exceções (Aula 13) e arquivos (Aula 12)

| Conceito | Onde | Como explicar |
|---|---|---|
| `try/except ValueError` na leitura | `utils/entrada.py:46` a `:50` | `while True` repete a pergunta; nada de a função chamar ela mesma |
| Rede de segurança dos menus | `interface/menu_base.py:68` a `:77` | Qualquer `ValueError` ou erro de banco vira mensagem, e o menu continua |
| Erro do banco com mensagem amigável | `interface/menu_artistas.py:36` e `:84` | `sqlite3.IntegrityError` = nome repetido ou FK bloqueando |
| Ctrl+C, fim da entrada, `finally` | `main.py:69` a `:83` | `KeyboardInterrupt` e `EOFError` saem com mensagem; o `finally` fecha o banco sempre |
| Ctrl+C só no modo ouvir | `interface/menu_player.py:143` | Ali o Ctrl+C só volta para o menu do player |
| Arquivo texto (`open`, `"w"`, `write`) | `interface/menu_relatorios.py:83` a `:89` | Exporta o relatório `.txt` |
| Arquivo binário `.wav` | `audio/gerador_wav.py:58` a `:89` | `math.sin` calcula a onda, `struct.pack` vira bytes, `wave` grava |

### Player

| Conceito | Onde | Como explicar |
|---|---|---|
| Estados | `audio/player.py:8` a `:11` | parado, tocando, pausado |
| Medir o tempo sem threads | `audio/player.py:50` (`_agora`) e `:99` (`posicao`) | Posição = tempo acumulado + (agora − início). O teste troca o relógio por herança (`testes/test_player.py`) |
| Aleatório | `audio/player.py:151` e `:152` | `random.shuffle` embaralha o resto e mantém a música atual na frente |
| Repetir | `audio/player.py:295` | desligado → fila → faixa |
| Fim da faixa | `audio/player.py:301` (`atualizar`) | A tela chama a cada interação e 4 vezes por segundo no modo ouvir |
| Histórico | `audio/player.py:191` a `:207` | Toda vez que uma faixa começa, grava uma linha no histórico |

## Perguntas prováveis (com respostas curtas)

1. **Quantas tabelas e como se ligam?** Seis. Artista 1:N álbum, álbum 1:N música, música 1:N
   histórico, e playlist N:N música pela tabela `playlist_musica`, que guarda a posição.
2. **O que acontece se eu excluir um artista que tem álbum?** O banco recusa, porque `album.artista_id`
   é chave estrangeira sem cascata. O programa pega o `sqlite3.IntegrityError` e explica.
3. **E se excluir uma playlist?** Os itens dela somem junto (`ON DELETE CASCADE`), mas as músicas
   continuam cadastradas.
4. **Para que serve o `PRAGMA foreign_keys = ON`?** O SQLite vem com as chaves estrangeiras
   desligadas. Sem ele, o banco aceitaria um álbum com um artista que não existe.
5. **Por que `?` no SQL e não f-string?** É consulta parametrizada (Aula 15): o valor vai separado do
   comando, então o que a pessoa digita nunca vira SQL. Evita SQL injection. Tem teste disso.
6. **Mas a classe base monta SQL com f-string.** Só com nomes de tabela e coluna que estão no próprio
   código. Os valores digitados sempre vão pelo `?`.
7. **Para que serve o `commit`? E o `rollback`?** O `commit` grava de vez; sem ele a alteração se perde.
   O `rollback` desfaz o que ainda não foi confirmado, quando dá erro.
8. **`fetchall` x `fetchone`?** Todas as linhas (lista de tuplas) x só a primeira (ou `None`).
9. **O que é o `self`?** A referência ao próprio objeto. O Python passa sozinho na chamada.
10. **Diferença entre `_id` e `__nome`?** Um underscore é só convenção (dá para acessar). Dois mudam o
    nome para `_Artista__nome`, então `artista.__nome` dá `AttributeError`.
11. **Por que get/set e não acessar direto?** Para validar num lugar só. `set_duracao` não deixa
    duração zero ou negativa, como o `atualizar_hodometro` da aula.
12. **`__str__` x `__repr__`?** `__str__` é o texto para o usuário (o `print` usa). `__repr__` é para o
    programador ver qual objeto é, no debug.
13. **Onde tem herança?** Modelos herdam de `Entidade`; repositórios de `RepositorioBase`; menus de
    `MenuBase`; saídas de áudio de `SaidaAudio`. Todas chamam `super().__init__()`.
14. **O que é polimorfismo no seu código?** O mesmo método com comportamento diferente em cada classe:
    o Player chama `saida.tocar()` e cada saída toca do seu jeito; o `inserir()` da classe-mãe chama
    `para_tupla()`, que cada repositório escreve do seu jeito.
15. **Onde tem associação? Qual a diferença para herança?** Associação é "tem um": o álbum tem um
    artista, a música tem um álbum, o player tem uma saída de áudio. Herança é "é um": o artista é uma
    entidade.
16. **Por que criar o `RepositorioBase`?** Para não repetir INSERT, SELECT, UPDATE e DELETE em cada
    tabela. É o exercício da Aula 15 de refatorar o CRUD diminuindo código.
17. **Por que `NotImplementedError` na classe-mãe?** Para avisar que a filha é obrigada a sobrescrever
    aquele método.
18. **Como o programa não quebra com entrada errada?** As leituras repetem a pergunta com `while True`
    e `try/except ValueError`; os menus têm uma rede de segurança; o `main.py` trata Ctrl+C e o fim da
    entrada e fecha o banco no `finally`.
19. **Como sai o som?** Se o `pygame` estiver instalado, por ele; senão, no Windows, pelo `winsound`, que
    já vem com o Python; senão, a reprodução é simulada (o tempo anda, sem som). Nunca dá erro.
20. **Como o player sabe que a música acabou, sem thread?** Ele guarda a hora em que a música começou.
    A cada interação (e 4 vezes por segundo no modo ouvir) compara com a duração e passa para a próxima.
21. **Como funciona o aleatório?** `random.shuffle` embaralha a fila, mantendo a música atual em
    primeiro. Ao desligar, volta para a ordem original.
22. **Como sai o ranking?** `COUNT(*)` do histórico agrupado por música (`GROUP BY`), em ordem
    decrescente, com `LIMIT 10`.
23. **As músicas têm direitos autorais?** Não. São melodias inventadas, geradas pelo programa com
    `math.sin`, `struct.pack` e `wave`.
24. **O arquivo `.db` está no GitHub?** Não, está no `.gitignore`. O `schema.sql` vai no repositório e
    cria o banco na primeira execução.
25. **Como você testou?** 60 testes com `unittest`, cada um com banco temporário, e um roteiro que roda
    o programa de verdade passando por todos os menus com entradas erradas.

## O que vai além da matéria (saiba explicar ou diga que pesquisou)

| Recurso | Onde | Explicação curta |
|---|---|---|
| `raise ValueError(...)` | modelos | "Lança" o erro para quem chamou tratar com `try/except` |
| `raise NotImplementedError` | `repositorios/base.py:35` | Obriga a classe-filha a sobrescrever |
| `raise` sozinho | `banco/conexao.py:53` | Depois do `rollback`, repassa o mesmo erro adiante |
| Lista por compreensão | `repositorios/base.py:70` | `[f"{coluna} = ?" for coluna in self.colunas]` monta a lista num laço curto |
| `LEFT JOIN`, `COALESCE`, `COLLATE NOCASE` | repositórios | Traz quem não tem par (artista sem álbum); troca `NULL` por 0; ordena sem diferenciar maiúscula |
| `struct.pack(f"<{total}h", *amostras)` | `audio/gerador_wav.py:82` | Converte a lista de números em bytes de 16 bits; o `*` espalha a lista como argumentos |
| `os.system("")` e cores ANSI | `utils/tela.py` | Liga as cores no console do Windows |
| `sys.stdout.reconfigure(errors="replace")` | `main.py:90` | Se a saída for para arquivo, caractere estranho vira `?` em vez de erro |
| `subprocess`, `unittest.mock` | `testes/` | Só nos testes: rodar o programa e simular o Ctrl+C |
