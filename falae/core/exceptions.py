from flask import render_template, current_app, g
import traceback


def registrar_exceptions(app):

    @app.errorhandler(404)
    def pagina_nao_encontrada(e):

        current_app.logger.warning(
            f"{g.request_id} | Página não encontrada | {g.rota}"
        )

        return render_template(
            "errors/404.html"
        ), 404


    @app.errorhandler(403)
    def acesso_negado(e):

        current_app.logger.warning(
            f"{g.request_id} | Acesso negado"
        )

        return render_template(
            "errors/403.html"
        ), 403


    @app.errorhandler(Exception)
    def erro_geral(e):

        current_app.logger.error(
            f"""
REQUEST........: {g.request_id}

ERRO...........: {str(e)}

TRACEBACK

{traceback.format_exc()}
"""
        )

        return render_template(
            "errors/500.html",
            request_id=g.request_id
        ), 500