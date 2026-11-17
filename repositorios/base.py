"""Classe-mãe dos repositórios: o CRUD que é igual para todas as tabelas.

É a resposta ao exercício da Aula 15 ("refatorar o código diminuindo
codificação"): em vez de repetir INSERT/UPDATE/DELETE/SELECT em cada classe,
o CRUD é escrito UMA vez aqui e as classes-filhas só dizem o que muda.
"""


class RepositorioBase:
    """CRUD genérico. Cada filha informa, no super().__init__():

    - tabela:   nome da tabela no banco;
    - colunas:  colunas que o programa preenche (sem o id, que é automático);
    - consulta: o SELECT que monta a linha completa (com JOIN, se precisar);
    - ordem:    como ordenar a listagem.

    E sobrescreve dois métodos (polimorfismo):
    - para_tupla(objeto): objeto -> tupla de valores, na ordem de colunas;
    - para_objeto(linha): linha do banco -> objeto.

    Segurança: nomes de tabela e coluna vêm do próprio código, nunca do
    usuário. Os VALORES sempre vão separados, pelo marcador ? (consulta
    parametrizada, Aula 15), o que impede SQL injection.
    """

    def __init__(self, banco, tabela, colunas, consulta, ordem):
        self.banco = banco            # associação: o repositório TEM um Banco
        self.tabela = tabela
        self.colunas = colunas
        self.consulta = consulta
        self.ordem = ordem

    # ----- métodos que as classes-filhas são obrigadas a sobrescrever -----

    def para_tupla(self, objeto):
        raise NotImplementedError("A classe-filha precisa implementar para_tupla().")

    def para_objeto(self, linha):
        raise NotImplementedError("A classe-filha precisa implementar para_objeto().")

    # ----- CRUD comum -----

    def inserir(self, objeto):
        """CREATE: grava o objeto e coloca nele o id gerado pelo banco."""
        nomes = ", ".join(self.colunas)
        marcadores = ", ".join(["?"] * len(self.colunas))     # "?, ?, ?"
        sql = f"INSERT INTO {self.tabela} ({nomes}) VALUES ({marcadores})"
        cursor = self.banco.executar(sql, self.para_tupla(objeto))
        objeto.set_id(cursor.lastrowid)
        return objeto

    def listar(self):
        """READ: devolve todos os registros como objetos."""
        linhas = self.banco.consultar(f"{self.consulta} ORDER BY {self.ordem}")
        objetos = []
        for linha in linhas:
            objetos.append(self.para_objeto(linha))
        return objetos

    def buscar_por_id(self, id):
        """READ: devolve um objeto, ou None se o id não existir."""
        sql = f"{self.consulta} WHERE {self.tabela}.id = ?"
        linha = self.banco.consultar_um(sql, (id,))
        if linha is None:
            return None
        return self.para_objeto(linha)

    def atualizar(self, objeto):
        """UPDATE: grava as alterações de um objeto que já tem id."""
        atribuicoes = ", ".join([f"{coluna} = ?" for coluna in self.colunas])
        sql = f"UPDATE {self.tabela} SET {atribuicoes} WHERE id = ?"
        parametros = self.para_tupla(objeto) + (objeto.get_id(),)
        cursor = self.banco.executar(sql, parametros)
        return cursor.rowcount > 0

    def excluir(self, id):
        """DELETE: apaga pelo id. Devolve True se apagou alguma linha.

        Se uma chave estrangeira impedir (ex.: artista que ainda tem álbum),
        o sqlite3 lança IntegrityError e quem chamou mostra a mensagem.
        """
        cursor = self.banco.executar(f"DELETE FROM {self.tabela} WHERE id = ?", (id,))
        return cursor.rowcount > 0

    def contar(self):
        linha = self.banco.consultar_um(f"SELECT COUNT(*) FROM {self.tabela}")
        return linha[0]
