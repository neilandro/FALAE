from flask import Flask

from config import Config
from extensions import bcrypt

from falae.core.exceptions import registrar_exceptions
from falae.core.logger import configurar_logger
from falae.core.request_context import (
    finalizar_request_context,
    iniciar_request_context,
)


def registrar_blueprints(app: Flask) -> None:
    from falae.blueprints.admin import admin_bp
    from falae.blueprints.assessoria import assessoria_bp
    from falae.blueprints.auth import auth_bp
    from falae.blueprints.dashboard import dashboard_bp
    from falae.blueprints.denuncia import denuncia_bp
    from falae.blueprints.empresa import empresa_bp
    from falae.blueprints.investigador import investigador_bp
    from falae.blueprints.main import main_bp
    from falae.blueprints.personalizacao import personalizacao_bp
    from falae.blueprints.portal import portal_bp
    from falae.blueprints.public import public_bp
    from falae.blueprints.relatorios import relatorios_bp

    blueprints = (
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
        app.register_blueprint(blueprint)


def create_app() -> Flask:
    Config.validate()

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    app.config.from_object(Config)

    bcrypt.init_app(app)

    configurar_logger(app)
    registrar_exceptions(app)

    app.before_request(iniciar_request_context)
    app.after_request(finalizar_request_context)

    registrar_blueprints(app)

    return app