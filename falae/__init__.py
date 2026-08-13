from os import getenv

from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from config import Config
from extensions import bcrypt, csrf, mail

from falae.core.exceptions import registrar_exceptions
from falae.core.logger import configurar_logger
from falae.core.request_context import (
    finalizar_request_context,
    iniciar_request_context,
)
from falae.core.security import registrar_security


def registrar_blueprints(app: Flask) -> None:
    from falae.blueprints.admin import admin_bp
    from falae.blueprints.assessoria import assessoria_bp
    from falae.blueprints.auth import auth_bp
    from falae.blueprints.dashboard import dashboard_bp
    from falae.blueprints.denuncia import denuncia_bp
    from falae.blueprints.empresa import empresa_bp
    from falae.blueprints.health import health_bp
    from falae.blueprints.investigador import investigador_bp
    from falae.blueprints.main import main_bp
    from falae.blueprints.personalizacao import personalizacao_bp
    from falae.blueprints.portal import portal_bp
    from falae.blueprints.public import public_bp
    from falae.blueprints.relatorios import relatorios_bp

    blueprints = (
        health_bp,
        main_bp,
        auth_bp,
        admin_bp,
        denuncia_bp,
        dashboard_bp,
        investigador_bp,
        public_bp,
        empresa_bp,
        assessoria_bp,
        personalizacao_bp,
        portal_bp,
        relatorios_bp,
    )

    for blueprint in blueprints:
        app.register_blueprint(
            blueprint
        )


def configurar_sessao(app: Flask) -> None:
    """
    Configura as políticas de segurança da sessão.

    SESSION_COOKIE_SECURE deve permanecer False no
    desenvolvimento local, pois o acesso ocorre por HTTP.

    Em produção com HTTPS, configure:

    SESSION_COOKIE_SECURE=true
    """

    cookie_secure = (
        getenv(
            "SESSION_COOKIE_SECURE",
            "false",
        )
        .strip()
        .lower()
        in {
            "1",
            "true",
            "yes",
            "on",
        }
    )

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=cookie_secure,
    )


def registrar_tratamento_csrf(
    app: Flask,
) -> None:
    """
    Registra uma resposta amigável para requisições
    recusadas pela proteção CSRF.
    """

    @app.errorhandler(CSRFError)
    def tratar_erro_csrf(
        erro: CSRFError,
    ):
        app.logger.warning(
            (
                "CSRF_RECUSADO | "
                "MOTIVO=%s"
            ),
            erro.description,
        )

        return (
            render_template(
                "errors/csrf.html",
            ),
            400,
        )


def create_app() -> Flask:
    Config.validate()

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    app.config.from_object(
        Config
    )

    configurar_sessao(
        app
    )

    configurar_logger(
        app
    )

    registrar_exceptions(
        app
    )

    registrar_tratamento_csrf(
        app
    )

    registrar_security(
        app
    )

    
    #O contexto precisa ser registrado antes do CSRF.
    #Dessa forma, até uma requisição recusada por token
    #inválido terá request_id, IP e demais informações.
    

    app.before_request(
        iniciar_request_context
    )

    app.after_request(
        finalizar_request_context
    )

    bcrypt.init_app(
        app
    )

    csrf.init_app(
        app
    )

    mail.init_app(
        app
    )

    registrar_blueprints(
        app
    )

    from falae.commands.notificacoes import (
        notificacoes_semanais
    )

    app.cli.add_command(
        notificacoes_semanais
    )



    return app