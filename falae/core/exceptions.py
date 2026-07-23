from flask import (Flask, current_app, g, render_template, request,)
from werkzeug.exceptions import HTTPException


def _request_id() -> str:
    return getattr(g, "request_id", "sem-request-id")


def _rota_atual() -> str:
    return getattr(
        g,
        "rota",
        request.path if request else "rota-desconhecida",
    )


def registrar_exceptions(app: Flask) -> None:

    @app.errorhandler(403)
    def acesso_negado(erro):
        request_id = _request_id()

        current_app.logger.warning(
            "%s | Acesso negado | rota=%s",
            request_id,
            _rota_atual(),
        )

        return render_template(
            "errors/403.html",
            request_id=request_id,
        ), 403

    @app.errorhandler(404)
    def pagina_nao_encontrada(erro):
        request_id = _request_id()

        current_app.logger.warning(
            "%s | Página não encontrada | rota=%s",
            request_id,
            _rota_atual(),
        )

        return render_template(
            "errors/404.html",
            request_id=request_id,
        ), 404

    @app.errorhandler(405)
    def metodo_nao_permitido(erro):
        request_id = _request_id()

        current_app.logger.warning(
            "%s | Método não permitido | metodo=%s | rota=%s",
            request_id,
            request.method,
            _rota_atual(),
        )

        return render_template(
            "errors/405.html",
            request_id=request_id,
        ), 405

    @app.errorhandler(413)
    def arquivo_muito_grande(erro):
        request_id = _request_id()

        limite_bytes = current_app.config.get(
            "MAX_CONTENT_LENGTH",
            16 * 1024 * 1024,
        )
        limite_mb = limite_bytes / (1024 * 1024)

        current_app.logger.warning(
            "%s | Upload acima do limite | limite_mb=%.2f | rota=%s",
            request_id,
            limite_mb,
            _rota_atual(),
        )

        return render_template(
            "errors/413.html",
            request_id=request_id,
            limite_mb=limite_mb,
        ), 413

    @app.errorhandler(Exception)
    def erro_geral(erro):
        if isinstance(erro, HTTPException):
            return erro

        request_id = _request_id()

        current_app.logger.exception(
            "%s | Erro interno não tratado | metodo=%s | rota=%s",
            request_id,
            request.method,
            _rota_atual(),
        )

        return render_template(
            "errors/500.html",
            request_id=request_id,
        ), 500