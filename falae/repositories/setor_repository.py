from db import get_connection


class SetorRepository:

    def __init__(self):
        self.conn = None
        self.cursor = None

        try:
            self.conn = get_connection()
            self.cursor = self.conn.cursor(dictionary=True)

        except Exception:
            self.close()
            raise

    def listar_por_empresa(self, empresa_id):
        self.cursor.execute(
            """
            SELECT
                s.id,
                s.empresa_id,
                s.unidade_id,
                s.nome,
                s.descricao,
                s.ativo,
                s.criado_em,
                u.nome AS unidade
            FROM setores s
            INNER JOIN unidades u
                ON u.id = s.unidade_id
               AND u.empresa_id = s.empresa_id
            WHERE s.empresa_id = %s
            ORDER BY
                u.nome,
                s.nome
            """,
            (empresa_id,)
        )

        return self.cursor.fetchall()

    def obter_por_id(self, setor_id, empresa_id):
        self.cursor.execute(
            """
            SELECT
                id,
                empresa_id,
                unidade_id,
                nome,
                descricao,
                ativo,
                criado_em
            FROM setores
            WHERE id = %s
              AND empresa_id = %s
            LIMIT 1
            """,
            (
                setor_id,
                empresa_id
            )
        )

        return self.cursor.fetchone()

    def listar_unidades_ativas(self, empresa_id):
        self.cursor.execute(
            """
            SELECT
                id,
                nome
            FROM unidades
            WHERE empresa_id = %s
              AND ativa = 1
            ORDER BY nome
            """,
            (empresa_id,)
        )

        return self.cursor.fetchall()

    def criar(self, empresa_id, dados):
        try:
            self.cursor.execute(
                """
                INSERT INTO setores (
                    empresa_id,
                    unidade_id,
                    nome,
                    descricao,
                    ativo
                )
                VALUES (%s, %s, %s, %s, 1)
                """,
                (
                    empresa_id,
                    dados.get("unidade_id"),
                    dados.get("nome"),
                    dados.get("descricao")
                )
            )

            setor_id = self.cursor.lastrowid
            self.conn.commit()

            return setor_id

        except Exception:
            self.conn.rollback()
            raise

    def atualizar(self, setor_id, empresa_id, dados):
        try:
            self.cursor.execute(
                """
                UPDATE setores
                SET
                    unidade_id = %s,
                    nome = %s,
                    descricao = %s,
                    ativo = %s
                WHERE id = %s
                  AND empresa_id = %s
                """,
                (
                    dados.get("unidade_id"),
                    dados.get("nome"),
                    dados.get("descricao"),
                    dados.get("ativo"),
                    setor_id,
                    empresa_id
                )
            )

            atualizado = self.cursor.rowcount > 0
            self.conn.commit()

            return atualizado

        except Exception:
            self.conn.rollback()
            raise

    def existe_nome(
        self,
        empresa_id,
        unidade_id,
        nome,
        setor_id=None
    ):
        sql = """
            SELECT id
            FROM setores
            WHERE empresa_id = %s
              AND unidade_id = %s
              AND LOWER(TRIM(nome)) = LOWER(TRIM(%s))
        """

        parametros = [
            empresa_id,
            unidade_id,
            nome
        ]

        if setor_id is not None:
            sql += """
                AND id <> %s
            """
            parametros.append(setor_id)

        sql += """
            LIMIT 1
        """

        self.cursor.execute(
            sql,
            tuple(parametros)
        )

        return self.cursor.fetchone()

    def unidade_pertence_empresa(self, unidade_id, empresa_id):
        self.cursor.execute(
            """
            SELECT id
            FROM unidades
            WHERE id = %s
              AND empresa_id = %s
              AND ativa = 1
            LIMIT 1
            """,
            (
                unidade_id,
                empresa_id
            )
        )

        return self.cursor.fetchone()

    def close(self):
        cursor = getattr(self, "cursor", None)
        conn = getattr(self, "conn", None)

        self.cursor = None
        self.conn = None

        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass

        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass