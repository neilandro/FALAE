import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask


def configurar_logger(app: Flask) -> None:
    log_folder = Path(app.config["LOG_FOLDER"])
    log_folder.mkdir(parents=True, exist_ok=True)

    arquivo_log = log_folder / "falae.log"

    formato = (
        "%(asctime)s | %(levelname)s | "
        "pid=%(process)d | thread=%(threadName)s | "
        "%(module)s | %(message)s"
    )

    formatter = logging.Formatter(formato)

    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False

    _adicionar_handler_arquivo(
        app=app,
        arquivo_log=arquivo_log,
        formatter=formatter,
    )

    _adicionar_handler_console(
        app=app,
        formatter=formatter,
    )

    app.logger.info("Logger do FALAE iniciado com sucesso.")


def _adicionar_handler_arquivo(
    app: Flask,
    arquivo_log: Path,
    formatter: logging.Formatter,
) -> None:
    caminho_arquivo = arquivo_log.resolve()

    for handler in app.logger.handlers:
        if not isinstance(handler, RotatingFileHandler):
            continue

        handler_path = Path(handler.baseFilename).resolve()

        if handler_path == caminho_arquivo:
            return

    file_handler = RotatingFileHandler(
        filename=arquivo_log,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    app.logger.addHandler(file_handler)


def _adicionar_handler_console(
    app: Flask,
    formatter: logging.Formatter,
) -> None:
    for handler in app.logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(
            handler,
            logging.FileHandler,
        ):
            return

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    app.logger.addHandler(console_handler)