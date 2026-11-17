"""Módulo de conexão com o banco SQLite3 (Aula 15)."""

import os
import sqlite3
from sqlite3 import Error

# Caminho do script de criação das tabelas, na mesma pasta deste arquivo.
CAMINHO_SCHEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


class Banco:
    """Cuida da conexão com o banco: abrir, criar as tabelas, executar SQL e fechar.

    Os repositórios (pasta repositorios/) recebem um objeto Banco e só falam
    com o banco por meio dele.
    """

    def __init__(self, caminho):
        """Guarda o caminho do arquivo .db. A conexão só abre em conectar()."""
        self.caminho = caminho
        self.__conexao = None  # fortemente privado: ninguém de fora mexe na conexão

    def conectar(self):
        """Abre a conexão e liga a checagem de chaves estrangeiras."""
        pasta = os.path.dirname(self.caminho)
        if pasta and not os.path.exists(pasta):
            os.makedirs(pasta)
        self.__conexao = sqlite3.connect(self.caminho)
        # No SQLite as chaves estrangeiras vêm DESLIGADAS. Sem esta linha,
        # o banco aceitaria um álbum com artista_id que não existe.
        self.__conexao.execute("PRAGMA foreign_keys = ON")

    def criar_tabelas(self):
        """Lê o arquivo schema.sql (Aula 12) e executa todos os CREATE TABLE."""
        with open(CAMINHO_SCHEMA, "r", encoding="utf-8") as arquivo:
            script = arquivo.read()
        self.__conexao.executescript(script)
        self.__conexao.commit()

    def executar(self, sql, parametros=()):
        """Executa INSERT, UPDATE ou DELETE e confirma com commit().

        Devolve o cursor, para quem chamou ler cursor.lastrowid (id gerado)
        ou cursor.rowcount (quantas linhas foram afetadas).
        Se der erro, desfaz com rollback() e repassa o erro para quem chamou.
        """
        cursor = self.__conexao.cursor()
        try:
            cursor.execute(sql, parametros)
            self.__conexao.commit()
        except Error:
            self.__conexao.rollback()
            raise
        return cursor

    def executar_varios(self, comandos):
        """Executa vários comandos como uma coisa só (transação).

        comandos é uma lista de tuplas (sql, parametros). Ou todos dão certo
        e o commit() grava tudo, ou um falha e o rollback() desfaz todos.
        """
        cursor = self.__conexao.cursor()
        try:
            for sql, parametros in comandos:
                cursor.execute(sql, parametros)
            self.__conexao.commit()
        except Error:
            self.__conexao.rollback()
            raise

    def consultar(self, sql, parametros=()):
        """Executa um SELECT e devolve todas as linhas (lista de tuplas)."""
        cursor = self.__conexao.cursor()
        cursor.execute(sql, parametros)
        return cursor.fetchall()

    def consultar_um(self, sql, parametros=()):
        """Executa um SELECT e devolve só a primeira linha (ou None)."""
        cursor = self.__conexao.cursor()
        cursor.execute(sql, parametros)
        return cursor.fetchone()

    def fechar(self):
        """Fecha a conexão. Tudo já foi gravado, pois cada comando faz commit()."""
        if self.__conexao is not None:
            self.__conexao.close()
            self.__conexao = None

    def __str__(self):
        return f"Banco SQLite em {self.caminho}"
