import os

import mysql.connector
from mysql.connector import Error


def get_connection():
    """Cria uma conexão MySQL usando somente variáveis de ambiente."""
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "falae_app"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "falae"),
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            use_pure=True,
            connection_timeout=int(os.getenv("DB_CONNECTION_TIMEOUT", "10")),
        )
    except Error as exc:
        raise RuntimeError(f"Não foi possível conectar ao banco de dados: {exc}") from exc
