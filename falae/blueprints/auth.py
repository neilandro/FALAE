from flask import (
    Blueprint,
    current_app,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from falae.services.login_service import (
    LoginService,
)
from falae.services.usuario_service import (
    UsuarioService,
)


auth_bp = Blueprint(
    "auth",
    __name__,
)


def _obter_email_formulario() -> str:
    return (
        request.form.get(
            "email",
            "",
        )
        .strip()
        .lower()
    )


def _registrar_sessao_usuario(
    usuario: dict,
) -> None:
    session.clear()

    session["usuario_id"] = usuario["id"]
    session["empresa_id"] = usuario.get(
        "empresa_id"
    )
    session["assessoria_id"] = usuario.get(
        "assessoria_id"
    )
    session["assessoria_nome"] = usuario.get(
        "assessoria_nome"
    )
    session["nome"] = usuario["nome"]
    session["perfil"] = usuario["perfil"]

    session[
        "trocar_senha_primeiro_acesso"
    ] = bool(
        usuario.get(
            "trocar_senha_primeiro_acesso"
        )
    )

    session.permanent = True


def _obter_destino_pos_login() -> str:
    return (
        LoginService
        .redirecionar_pos_login(
            {
                "perfil": session.get(
                    "perfil"
                )
            }
        )
    )


@auth_bp.route(
    "/login",
    methods=["GET", "POST"],
)
def login():
    if request.method == "GET":
        return render_template(
            "public/login.html",
            erro=None,
        )

    email = _obter_email_formulario()

    resultado = LoginService.autenticar(
        email=email,
        senha=request.form.get(
            "senha",
            "",
        ),
    )

    if not resultado.get(
        "sucesso"
    ):
        current_app.logger.warning(
            (
                "LOGIN_RECUSADO | "
                "REQUEST=%s | "
                "IP=%s"
            ),
            getattr(
                g,
                "request_id",
                None,
            ),
            getattr(
                g,
                "ip",
                None,
            ),
        )

        return render_template(
            "public/login.html",
            erro=resultado.get(
                "mensagem",
                "Não foi possível realizar o login.",
            ),
        )

    usuario = resultado.get(
        "usuario"
    )

    if not usuario:
        current_app.logger.error(
            (
                "LOGIN_RESPOSTA_INVALIDA | "
                "REQUEST=%s"
            ),
            getattr(
                g,
                "request_id",
                None,
            ),
        )

        return render_template(
            "public/login.html",
            erro="Não foi possível realizar o login.",
        )

    _registrar_sessao_usuario(
        usuario
    )

    current_app.logger.info(
        (
            "LOGIN_SUCESSO | "
            "REQUEST=%s | "
            "USUARIO=%s | "
            "PERFIL=%s | "
            "EMPRESA=%s"
        ),
        getattr(
            g,
            "request_id",
            None,
        ),
        session.get(
            "usuario_id"
        ),
        session.get(
            "perfil"
        ),
        session.get(
            "empresa_id"
        ),
    )

    if session.get(
        "trocar_senha_primeiro_acesso"
    ):
        return redirect(
            url_for(
                "auth.alterar_senha_obrigatoria"
            )
        )

    return redirect(
        _obter_destino_pos_login()
    )


@auth_bp.route(
    "/alterar-senha-obrigatoria",
    methods=["GET", "POST"],
)
def alterar_senha_obrigatoria():
    usuario_id = session.get(
        "usuario_id"
    )

    if not usuario_id:
        return redirect(
            url_for(
                "auth.login"
            )
        )

    if not session.get(
        "trocar_senha_primeiro_acesso"
    ):
        return redirect(
            _obter_destino_pos_login()
        )

    if request.method == "GET":
        return render_template(
            "public/alterar_senha_obrigatoria.html",
            erro=None,
        )

    resultado = (
        UsuarioService
        .alterar_senha_obrigatoria(
            usuario_id=usuario_id,
            nova_senha=request.form.get(
                "nova_senha",
                "",
            ),
            confirmar_senha=request.form.get(
                "confirmar_senha",
                "",
            ),
        )
    )

    if not resultado.get(
        "sucesso"
    ):
        current_app.logger.warning(
            (
                "TROCA_SENHA_OBRIGATORIA_FALHOU | "
                "REQUEST=%s | "
                "USUARIO=%s"
            ),
            getattr(
                g,
                "request_id",
                None,
            ),
            usuario_id,
        )

        return render_template(
            "public/alterar_senha_obrigatoria.html",
            erro=resultado.get(
                "mensagem",
                (
                    "Não foi possível atualizar "
                    "sua senha."
                ),
            ),
        )

    session[
        "trocar_senha_primeiro_acesso"
    ] = False

    session.modified = True

    current_app.logger.info(
        (
            "TROCA_SENHA_OBRIGATORIA_CONCLUIDA | "
            "REQUEST=%s | "
            "USUARIO=%s"
        ),
        getattr(
            g,
            "request_id",
            None,
        ),
        usuario_id,
    )

    return redirect(
        _obter_destino_pos_login()
    )


@auth_bp.route(
    "/logout",
    methods=["POST"],
)
def logout():
    usuario_id = session.get(
        "usuario_id"
    )

    session.clear()

    current_app.logger.info(
        (
            "LOGOUT | "
            "REQUEST=%s | "
            "USUARIO=%s"
        ),
        getattr(
            g,
            "request_id",
            None,
        ),
        usuario_id,
    )

    return redirect(
        url_for(
            "auth.login"
        )
    )