import os

import mysql.connector
from mysql.connector import Error


def _obter_porta() -> int:
    try:
        porta = int(
            os.getenv(
                "DB_PORT",
                "3306",
            )
        )
    except ValueError as exc:
        raise RuntimeError(
            "A variável DB_PORT deve conter um número inteiro."
        ) from exc

    if not 1 <= porta <= 65535:
        raise RuntimeError(
            "A variável DB_PORT deve estar entre 1 e 65535."
        )

    return porta


def _obter_timeout() -> int:
    try:
        timeout = int(
            os.getenv(
                "DB_CONNECTION_TIMEOUT",
                "10",
            )
        )
    except ValueError as exc:
        raise RuntimeError(
            "A variável DB_CONNECTION_TIMEOUT deve "
            "conter um número inteiro."
        ) from exc

    if timeout <= 0:
        raise RuntimeError(
            "A variável DB_CONNECTION_TIMEOUT deve "
            "ser maior que zero."
        )

    return timeout


def get_connection():
    """
    Cria uma conexão MySQL usando variáveis de ambiente.

    A conexão utiliza transações explícitas. Portanto, operações
    de escrita devem executar commit() ou rollback().
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv(
                "DB_HOST",
                "127.0.0.1",
            ),
            port=_obter_porta(),
            user=os.getenv(
                "DB_USER",
                "falae_app",
            ),
            password=os.getenv(
                "DB_PASSWORD",
                "",
            ),
            database=os.getenv(
                "DB_NAME",
                "falae",
            ),
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            use_pure=True,
            autocommit=False,
            connection_timeout=_obter_timeout(),
        )

        if not conn.is_connected():
            conn.close()

            raise RuntimeError(
                "Não foi possível estabelecer conexão "
                "com o banco de dados."
            )

        return conn

    except Error as exc:
        raise RuntimeError(
            "Não foi possível conectar ao banco de dados."
        ) from exc