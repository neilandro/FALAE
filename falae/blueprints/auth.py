from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from falae.services.login_service import (
    LoginService
)
from falae.services.usuario_service import (
    UsuarioService
)


auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():
    erro = None

    if request.method == "POST":
        resultado = LoginService.autenticar(
            email=request.form.get(
                "email"
            ),
            senha=request.form.get(
                "senha"
            )
        )

        if not resultado.get(
            "sucesso"
        ):
            erro = resultado.get(
                "mensagem",
                "Não foi possível realizar o login."
            )

            return render_template(
                "public/login.html",
                erro=erro
            )

        usuario = resultado[
            "usuario"
        ]

        session.clear()

        session["usuario_id"] = usuario[
            "id"
        ]

        session["empresa_id"] = usuario.get(
            "empresa_id"
        )

        session["assessoria_id"] = usuario.get(
            "assessoria_id"
        )

        session["assessoria_nome"] = usuario.get(
            "assessoria_nome"
        )

        session["nome"] = usuario[
            "nome"
        ]

        session["perfil"] = usuario[
            "perfil"
        ]

        session[
            "trocar_senha_primeiro_acesso"
        ] = bool(
            usuario.get(
                "trocar_senha_primeiro_acesso"
            )
        )

        session.pop(
            "empresa_ativa",
            None
        )

        session.pop(
            "empresa_ativa_nome",
            None
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
            resultado[
                "destino"
            ]
        )

    return render_template(
        "public/login.html",
        erro=erro
    )


@auth_bp.route(
    "/alterar-senha-obrigatoria",
    methods=["GET", "POST"]
)
def alterar_senha_obrigatoria():
    if not session.get(
        "usuario_id"
    ):
        return redirect(
            url_for(
                "auth.login"
            )
        )

    if not session.get(
        "trocar_senha_primeiro_acesso"
    ):
        return redirect(
            LoginService.redirecionar_pos_login(
                {
                    "perfil": session.get(
                        "perfil"
                    )
                }
            )
        )

    erro = None

    if request.method == "POST":
        resultado = (
            UsuarioService
            .alterar_senha_obrigatoria(
                usuario_id=session.get(
                    "usuario_id"
                ),
                nova_senha=request.form.get(
                    "nova_senha"
                ),
                confirmar_senha=request.form.get(
                    "confirmar_senha"
                )
            )
        )

        if not resultado.get(
            "sucesso"
        ):
            erro = resultado.get(
                "mensagem",
                (
                    "Não foi possível atualizar "
                    "sua senha."
                )
            )

            return render_template(
                "public/alterar_senha_obrigatoria.html",
                erro=erro
            )

        session[
            "trocar_senha_primeiro_acesso"
        ] = False

        destino = (
            LoginService
            .redirecionar_pos_login(
                {
                    "perfil": session.get(
                        "perfil"
                    )
                }
            )
        )

        return redirect(
            destino
        )

    return render_template(
        "public/alterar_senha_obrigatoria.html",
        erro=erro
    )


@auth_bp.route(
    "/logout"
)
def logout():
    session.clear()

    return redirect(
        url_for(
            "auth.login"
        )
    )