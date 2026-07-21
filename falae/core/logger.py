import logging
import os
from logging.handlers import RotatingFileHandler


def configurar_logger(app):
    if not os.path.exists("logs"):
        os.makedirs("logs")

    arquivo_log = "logs/falae.log"

    handler = RotatingFileHandler(
        arquivo_log,
        maxBytes=1024 * 1024 * 5,
        backupCount=5,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(module)s | %(message)s"
    )

    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    app.logger.info("Logger do FALAE iniciado com sucesso.")