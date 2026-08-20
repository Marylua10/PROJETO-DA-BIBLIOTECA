"""Modelos de dados do sistema de biblioteca escolar."""
from database import get_connection


class Livro:
    """Representa um livro do acervo."""

    @staticmethod
    def listar(termo=None):
        """Lista livros com informação de disponibilidade."""
        conn = get_connection()
        try:
            base = """
                SELECT l.*,
                       l.quantidade - COUNT(e.id) AS disponiveis
                FROM livros l
                LEFT JOIN emprestimos e
                    ON e.livro_id = l.id AND e.status = 'ativo'
            """
            if termo:
                like = f"%{termo}%"
                query = base + " WHERE l.titulo LIKE ? OR l.autor LIKE ? GROUP BY l.id ORDER BY l.titulo"
                rows = conn.execute(query, (like, like)).fetchall()
            else:
                query = base + " GROUP BY l.id ORDER BY l.titulo"
                rows = conn.execute(query).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def buscar(livro_id):
        """Busca um livro pelo id."""
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM livros WHERE id = ?", (livro_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def criar(dados):
        """Cadastra um novo livro."""
        conn = get_connection()
        try:
            cur = conn.execute(
                """
                INSERT INTO livros (titulo, autor, ano, categoria, quantidade, capa)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    dados["titulo"],
                    dados["autor"],
                    dados.get("ano"),
                    dados.get("categoria"),
                    dados.get("quantidade", 1),
                    dados.get("capa"),
                ),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    @staticmethod
    def atualizar(livro_id, dados):
        """Atualiza os dados de um livro."""
        conn = get_connection()
        try:
            # Se capa foi atualizada, inclui no UPDATE
            if "capa" in dados:
                cur = conn.execute(
                    """
                    UPDATE livros
                    SET titulo = ?, autor = ?, ano = ?, categoria = ?, quantidade = ?, capa = ?
                    WHERE id = ?
                    """,
                    (
                        dados["titulo"],
                        dados["autor"],
                        dados.get("ano"),
                        dados.get("categoria"),
                        dados.get("quantidade", 1),
                        dados["capa"],
                        livro_id,
                    ),
                )
            else:
                cur = conn.execute(
                    """
                    UPDATE livros
                    SET titulo = ?, autor = ?, ano = ?, categoria = ?, quantidade = ?
                    WHERE id = ?
                    """,
                    (
                        dados["titulo"],
                        dados["autor"],
                        dados.get("ano"),
                        dados.get("categoria"),
                        dados.get("quantidade", 1),
                        livro_id,
                    ),
                )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def excluir(livro_id):
        """Remove um livro do acervo."""
        conn = get_connection()
        try:
            cur = conn.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def disponiveis(livro_id):
        """Retorna quantos exemplares de um livro estão disponíveis para empréstimo."""
        conn = get_connection()
        try:
            row = conn.execute(
                """
                SELECT l.quantidade - COUNT(e.id) AS disponiveis
                FROM livros l
                LEFT JOIN emprestimos e
                    ON e.livro_id = l.id AND e.status = 'ativo'
                WHERE l.id = ?
                GROUP BY l.id
                """,
                (livro_id,),
            ).fetchone()
            return (row["disponiveis"] if row else 0) or 0
        finally:
            conn.close()


class Usuario:
    """Representa um usuário (aluno) da biblioteca."""

    @staticmethod
    def listar(termo=None):
        """Lista usuários, opcionalmente filtrando por nome ou matrícula."""
        conn = get_connection()
        try:
            if termo:
                like = f"%{termo}%"
                rows = conn.execute(
                    "SELECT * FROM usuarios WHERE nome LIKE ? OR matricula LIKE ? ORDER BY nome",
                    (like, like),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM usuarios ORDER BY nome").fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def buscar(usuario_id):
        """Busca um usuário pelo id."""
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def criar(dados):
        """Cadastra um novo usuário."""
        conn = get_connection()
        try:
            cur = conn.execute(
                """
                INSERT INTO usuarios (nome, email, matricula, turma)
                VALUES (?, ?, ?, ?)
                """,
                (
                    dados["nome"],
                    dados["email"],
                    dados["matricula"],
                    dados.get("turma"),
                ),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    @staticmethod
    def atualizar(usuario_id, dados):
        """Atualiza os dados de um usuário."""
        conn = get_connection()
        try:
            cur = conn.execute(
                """
                UPDATE usuarios
                SET nome = ?, email = ?, matricula = ?, turma = ?
                WHERE id = ?
                """,
                (
                    dados["nome"],
                    dados["email"],
                    dados["matricula"],
                    dados.get("turma"),
                    usuario_id,
                ),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def excluir(usuario_id):
        """Remove um usuário."""
        conn = get_connection()
        try:
            cur = conn.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()


class Emprestimo:
    """Representa um empréstimo de livro."""

    @staticmethod
    def criar(livro_id, usuario_id):
        """Registra um empréstimo, desde que haja exemplar disponível."""
        conn = get_connection()
        try:
            row = conn.execute(
                """
                SELECT l.quantidade - COUNT(e.id) AS disponiveis
                FROM livros l
                LEFT JOIN emprestimos e
                    ON e.livro_id = l.id AND e.status = 'ativo'
                WHERE l.id = ?
                GROUP BY l.id
                """,
                (livro_id,),
            ).fetchone()
            disponiveis = (row["disponiveis"] if row else 0) or 0
            if disponiveis <= 0:
                return None
            cur = conn.execute(
                """
                INSERT INTO emprestimos (livro_id, usuario_id)
                VALUES (?, ?)
                """,
                (livro_id, usuario_id),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    @staticmethod
    def devolver(emprestimo_id):
        """Marca um empréstimo como devolvido."""
        conn = get_connection()
        try:
            cur = conn.execute(
                """
                UPDATE emprestimos
                SET status = 'devolvido', data_devolucao = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'ativo'
                """,
                (emprestimo_id,),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def listar_ativos():
        """Lista empréstimos ativos com dados do livro e do usuário."""
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT e.id, e.data_emprestimo, e.data_devolucao, e.status,
                       l.id AS livro_id, l.titulo, l.autor,
                       u.id AS usuario_id, u.nome AS usuario_nome, u.matricula, u.turma
                FROM emprestimos e
                JOIN livros l ON l.id = e.livro_id
                JOIN usuarios u ON u.id = e.usuario_id
                WHERE e.status = 'ativo'
                ORDER BY e.data_emprestimo DESC
                """
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
