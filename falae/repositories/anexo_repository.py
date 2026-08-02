from db import get_connection


class AnexoRepository:

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(
            dictionary=True
        )

    def denuncia_pertence_empresa(
        self,
        denuncia_id,
        empresa_id
    ):
        self.cursor.execute(
            """
            SELECT id
            FROM denuncias
            WHERE id = %s
              AND empresa_id = %s
            LIMIT 1
            """,
            (
                denuncia_id,
                empresa_id
            )
        )

        return self.cursor.fetchone() is not None

    def salvar(
        self,
        denuncia_id,
        empresa_id,
        nome_original,
        nome_fisico,
        caminho,
        mime_type,
        tamanho
    ):
        try:
            self.cursor.execute(
                """
                INSERT INTO denuncia_anexos (
                    denuncia_id,
                    empresa_id,
                    nome_original,
                    nome_fisico,
                    caminho,
                    mime_type,
                    tamanho
                )
                SELECT
                    d.id,
                    d.empresa_id,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                FROM denuncias d
                WHERE d.id = %s
                  AND d.empresa_id = %s
                """,
                (
                    nome_original,
                    nome_fisico,
                    caminho,
                    mime_type,
                    tamanho,
                    denuncia_id,
                    empresa_id
                )
            )

            if self.cursor.rowcount == 0:
                self.conn.rollback()

                raise ValueError(
                    "A denúncia informada não pertence "
                    "à empresa atual."
                )

            anexo_id = self.cursor.lastrowid

            self.conn.commit()

            return anexo_id

        except Exception:
            self.conn.rollback()
            raise

    def listar_por_denuncia(
        self,
        denuncia_id,
        empresa_id
    ):
        self.cursor.execute(
            """
            SELECT
                id,
                denuncia_id,
                empresa_id,
                nome_original,
                nome_fisico,
                caminho,
                mime_type,
                tamanho,
                criado_em
            FROM denuncia_anexos
            WHERE denuncia_id = %s
              AND empresa_id = %s
            ORDER BY criado_em
            """,
            (
                denuncia_id,
                empresa_id
            )
        )

        return self.cursor.fetchall()

    def contar_por_denuncia(
        self,
        denuncia_id,
        empresa_id
    ):
        self.cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM denuncia_anexos
            WHERE denuncia_id = %s
              AND empresa_id = %s
            """,
            (
                denuncia_id,
                empresa_id
            )
        )

        resultado = self.cursor.fetchone()

        return int(
            resultado.get("total") or 0
        ) if resultado else 0

    def buscar_por_id(
        self,
        anexo_id,
        empresa_id
    ):
        self.cursor.execute(
            """
            SELECT
                id,
                denuncia_id,
                empresa_id,
                nome_original,
                nome_fisico,
                caminho,
                mime_type,
                tamanho,
                criado_em
            FROM denuncia_anexos
            WHERE id = %s
              AND empresa_id = %s
            LIMIT 1
            """,
            (
                anexo_id,
                empresa_id
            )
        )

        return self.cursor.fetchone()

    def excluir(
        self,
        anexo_id,
        empresa_id
    ):
        try:
            self.cursor.execute(
                """
                DELETE FROM denuncia_anexos
                WHERE id = %s
                  AND empresa_id = %s
                """,
                (
                    anexo_id,
                    empresa_id
                )
            )

            excluido = self.cursor.rowcount > 0

            self.conn.commit()

            return excluido

        except Exception:
            self.conn.rollback()
            raise

    def excluir_varios(
        self,
        anexo_ids,
        empresa_id
    ):
        ids_validos = [
            int(anexo_id)
            for anexo_id in anexo_ids
            if anexo_id
        ]

        if not ids_validos:
            return 0

        placeholders = ", ".join(
            ["%s"] * len(ids_validos)
        )

        parametros = [
            *ids_validos,
            empresa_id
        ]

        try:
            self.cursor.execute(
                f"""
                DELETE FROM denuncia_anexos
                WHERE id IN ({placeholders})
                  AND empresa_id = %s
                """,
                tuple(parametros)
            )

            total_excluido = self.cursor.rowcount

            self.conn.commit()

            return total_excluido

        except Exception:
            self.conn.rollback()
            raise

    def close(self):
        cursor = getattr(
            self,
            "cursor",
            None
        )

        conn = getattr(
            self,
            "conn",
            None
        )

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