"""Conexão com o banco de dados SQLite do sistema de biblioteca escolar."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "biblioteca.db"


def get_connection():
    """Retorna uma conexão com o banco, habilitando chaves estrangeiras."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Cria as tabelas do banco caso ainda não existam."""
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                ano INTEGER,
                categoria TEXT,
                quantidade INTEGER DEFAULT 1,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                matricula TEXT UNIQUE NOT NULL,
                turma TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS emprestimos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                livro_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                data_emprestimo TEXT DEFAULT CURRENT_TIMESTAMP,
                data_devolucao TEXT,
                status TEXT DEFAULT 'ativo',
                FOREIGN KEY (livro_id) REFERENCES livros (id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            );
            """
        )
        conn.commit()
    finally:
        conn.close()
