from flask import Blueprint, jsonify

from db import get_connection


health_bp = Blueprint(
    "health",
    __name__,
)


@health_bp.route(
    "/health",
    methods=["GET"],
)
def health():
    """
    Verifica se a aplicação e o banco de dados
    estão disponíveis.

    Retorna:
        200: aplicação pronta para receber tráfego.
        503: aplicação ativa, mas sem acesso ao banco.
    """

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1"
        )

        resultado = cursor.fetchone()

        if not resultado:
            raise RuntimeError(
                "O banco não respondeu ao teste de saúde."
            )

        return (
            jsonify(
                {
                    "status": "ok",
                    "aplicacao": "falae",
                    "banco": "disponivel",
                }
            ),
            200,
        )

    except Exception:
        return (
            jsonify(
                {
                    "status": "indisponivel",
                    "aplicacao": "falae",
                    "banco": "indisponivel",
                }
            ),
            503,
        )

    finally:
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