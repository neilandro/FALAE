from flask import Flask

from config import Config
from extensions import bcrypt

from falae.core.logger import configurar_logger
from falae.core.exceptions import registrar_exceptions
from falae.core.request_context import iniciar_request_context, finalizar_request_context


def create_app():
    Config.validate()

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    app.config.from_object(Config)

    bcrypt.init_app(app)

    configurar_logger(app)
    registrar_exceptions(app)

    app.before_request(iniciar_request_context)
    app.after_request(finalizar_request_context)

    from falae.blueprints.auth import auth_bp
    from falae.blueprints.main import main_bp
    from falae.blueprints.admin import admin_bp
    from falae.blueprints.denuncia import denuncia_bp
    from falae.blueprints.dashboard import dashboard_bp
    from falae.blueprints.investigador import investigador_bp
    from falae.blueprints.public import public_bp
    from falae.blueprints.empresa import empresa_bp
    from falae.blueprints.assessoria import assessoria_bp
    from falae.blueprints.personalizacao import (personalizacao_bp)
    from falae.blueprints.portal import portal_bp
    from falae.blueprints.relatorios import relatorios_bp
    

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(denuncia_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(investigador_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(empresa_bp)
    app.register_blueprint(assessoria_bp)
    app.register_blueprint(personalizacao_bp)
    app.register_blueprint(portal_bp)
    app.register_blueprint(relatorios_bp)
    


    return app