from flask import (
    redirect,
    render_template,
    request,
    url_for,
    current_app,
    session,
)

from . import admin_bp

from falae.decorators import perfil_required
from falae.services.usuario_service import UsuarioService


@admin_bp.route("/usuarios")
@perfil_required(
    "SUPER_ADMIN",
    "ADM_ASSESSORIA",
    "ADMIN_EMPRESA"
)
def usuarios():
    lista_usuarios = UsuarioService.listar_usuarios()

    return render_template(
        "admin/usuarios.html",
        usuarios=lista_usuarios
    )

@admin_bp.route(
    "/usuarios/novo",
    methods=["GET", "POST"]
)
@perfil_required(
    "SUPER_ADMIN",
    "ADM_ASSESSORIA",
    "ADMIN_EMPRESA"
)
def usuario_novo():
    dados_formulario = (
        UsuarioService.preparar_formulario_usuario()
    )

    empresa_id_preselecionada = (
        request.args.get("empresa_id")
    )

    erro = None

    if request.method == "POST":
        resultado = UsuarioService.criar_usuario(
            request.form
        )

        if resultado.get("sucesso"):
            return redirect(
                url_for(
                    "admin.usuarios"
                )
            )

        erro = resultado.get(
            "mensagem",
            "Não foi possível criar o usuário."
        )

    return render_template(
        "admin/forms/usuario_form.html",
        modo="novo",
        usuario=None,
        erro=erro,
        empresa_id_preselecionada=(
            empresa_id_preselecionada
        ),
        **dados_formulario
    )


@admin_bp.route(
    "/usuarios/<int:usuario_id>/editar",
    methods=["GET", "POST"]
)
@perfil_required(
    "SUPER_ADMIN",
    "ADM_ASSESSORIA",
    "ADMIN_EMPRESA"
)
def usuario_editar(usuario_id):
    dados_formulario = (
        UsuarioService.preparar_formulario_usuario()
    )

    usuario = UsuarioService.obter_usuario(
        usuario_id
    )

    if not usuario:
        return (
            "Usuário não encontrado.",
            404
        )

    if not UsuarioService.pode_acessar_usuario(
        usuario
    ):
        return (
            "Acesso não autorizado.",
            403
        )

    erro = None

    if request.method == "POST":
        resultado = UsuarioService.editar_usuario(
            usuario_id=usuario_id,
            dados_form=request.form
        )

        if resultado.get("sucesso"):
            return redirect(
                url_for(
                    "admin.usuarios"
                )
            )

        erro = resultado.get(
            "mensagem",
            "Não foi possível atualizar o usuário."
        )

        usuario = {
            **usuario,
            "nome": request.form.get("nome"),
            "email": request.form.get("email"),
            "celular": request.form.get("celular"),
            "whatsapp": request.form.get("whatsapp"),
            "perfil": request.form.get("perfil"),
            "empresa_id": (
                request.form.get("empresa_id")
                or None
            ),
            "assessoria_id": (
                request.form.get("assessoria_id")
                or None
            ),
            "ativo": request.form.get(
                "ativo",
                1
            )
        }

    return render_template(
        "admin/forms/usuario_form.html",
        modo="editar",
        usuario=usuario,
        erro=erro,
        empresa_id_preselecionada=None,
        **dados_formulario
    )


@admin_bp.route(
    "/usuarios/<int:usuario_id>/resetar-senha",
    methods=["POST"]
)
@perfil_required(
    "SUPER_ADMIN",
    "ADM_ASSESSORIA",
    "ADMIN_EMPRESA"
)
def resetar_senha_usuario(usuario_id):
    resultado = UsuarioService.resetar_senha(
        usuario_id
    )

    if not resultado.get("sucesso"):
        mensagem = resultado.get(
            "mensagem",
            "Não foi possível redefinir a senha."
        )

        if mensagem == "Usuário não encontrado.":
            return mensagem, 404

        return mensagem, 403

    return render_template(
        "admin/senha_resetada.html",
        usuario=resultado["usuario"],
        senha_temporaria=resultado[
            "senha_temporaria"
        ]
    )
