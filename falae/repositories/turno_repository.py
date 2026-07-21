from typing import Any

from db import get_connection


class TurnoRepository:
    """Responsável exclusivamente pelo acesso aos dados de turnos."""

    @staticmethod
    def listar_por_empresa(empresa_id: int) -> list[dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    empresa_id,
                    nome
                FROM turnos
                WHERE empresa_id = %s
                ORDER BY nome
                """,
                (empresa_id,),
            )

            return cursor.fetchall()

        finally:
            cursor.close()

    @staticmethod
    def buscar_por_id(
        turno_id: int,
        empresa_id: int,
    ) -> dict[str, Any] | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    empresa_id,
                    nome
                FROM turnos
                WHERE id = %s
                  AND empresa_id = %s
                LIMIT 1
                """,
                (
                    turno_id,
                    empresa_id,
                ),
            )

            return cursor.fetchone()

        finally:
            cursor.close()

    @staticmethod
    def buscar_por_nome(
        nome: str,
        empresa_id: int,
        ignorar_turno_id: int | None = None,
    ) -> dict[str, Any] | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            sql = """
                SELECT
                    id,
                    empresa_id,
                    nome
                FROM turnos
                WHERE empresa_id = %s
                  AND LOWER(TRIM(nome)) = LOWER(TRIM(%s))
            """

            parametros: list[Any] = [
                empresa_id,
                nome,
            ]

            if ignorar_turno_id is not None:
                sql += " AND id <> %s"
                parametros.append(ignorar_turno_id)

            sql += " LIMIT 1"

            cursor.execute(
                sql,
                tuple(parametros),
            )

            return cursor.fetchone()

        finally:
            cursor.close()

    @staticmethod
    def criar(
        empresa_id: int,
        nome: str,
    ) -> int:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)   

        try:
            cursor.execute(
                """
                INSERT INTO turnos (
                    empresa_id,
                    nome
                )
                VALUES (%s, %s)
                """,
                (
                    empresa_id,
                    nome,
                ),
            )

            conn.commit()

            return cursor.lastrowid

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()

    @staticmethod
    def atualizar(
        turno_id: int,
        empresa_id: int,
        nome: str,
    ) -> bool:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                UPDATE turnos
                SET nome = %s
                WHERE id = %s
                  AND empresa_id = %s
                """,
                (
                    nome,
                    turno_id,
                    empresa_id,
                ),
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()

    @staticmethod
    def excluir(
        turno_id: int,
        empresa_id: int,
    ) -> bool:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                DELETE FROM turnos
                WHERE id = %s
                  AND empresa_id = %s
                """,
                (
                    turno_id,
                    empresa_id,
                ),
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()