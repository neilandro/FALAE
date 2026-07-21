from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for
)

from db import get_connection
from falae.decorators import perfil_required
from falae.services.context_service import ContextService
from falae.services.setor_service import SetorService
from falae.services.turno_service import TurnoService
from falae.services.unidade_service import UnidadeService
from falae.services.usuario_service import UsuarioService


empresa_bp = Blueprint(
    "empresa",
    __name__
)


empresa_cadastros_required = perfil_required(
    "SUPER_ADMIN",
    "ADM_ASSESSORIA",
    "ADMIN_EMPRESA"
)


PERFIS_USUARIO_EMPRESA = [
    "GESTOR",
    "INVESTIGADOR",
    "VISUALIZADOR"
]


@empresa_bp.route(
    "/empresa/unidades"
)
@empresa_cadastros_required
def unidades():
    lista_unidades = UnidadeService.listar()

    return render_template(
        "empresa/unidades.html",
        unidades=lista_unidades
    )


@empresa_bp.route(
    "/empresa/unidades/nova",
    methods=["GET", "POST"]
)
@empresa_cadastros_required
def unidade_nova():
    if request.method == "POST":
        resultado = UnidadeService.criar(
            request.form
        )

        if resultado["sucesso"]:
            return redirect(
                url_for(
                    "empresa.unidades"
                )
            )

        return (
            resultado["mensagem"],
            400
        )

    return render_template(
        "empresa/unidade_form.html",
        modo="novo",
        unidade=None
    )


@empresa_bp.route(
    "/empresa/unidades/<int:unidade_id>/editar",
    methods=["GET", "POST"]
)
@empresa_cadastros_required
def unidade_editar(unidade_id):
    unidade = UnidadeService.obter(
        unidade_id
    )

    if not unidade:
        return (
            "Unidade não encontrada.",
            404
        )

    if request.method == "POST":
        resultado = UnidadeService.editar(
            unidade_id,
            request.form
        )

        if resultado["sucesso"]:
            return redirect(
                url_for(
                    "empresa.unidades"
                )
            )

        return (
            resultado["mensagem"],
            400
        )

    return render_template(
        "empresa/unidade_form.html",
        modo="editar",
        unidade=unidade
    )


@empresa_bp.route(
    "/empresa/unidades/<int:unidade_id>/status",
    methods=["POST"]
)
@empresa_cadastros_required
def unidade_alterar_status(unidade_id):
    ativa = request.form.get(
        "ativa"
    )

    resultado = UnidadeService.alterar_status(
        unidade_id=unidade_id,
        ativa=ativa
    )

    if not resultado["sucesso"]:
        return (
            resultado["mensagem"],
            400
        )

    return redirect(
        url_for(
            "empresa.unidades"
        )
    )


@empresa_bp.route(
    "/empresa/setores"
)
@empresa_cadastros_required
def setores():
    lista_setores = SetorService.listar()

    return render_template(
        "empresa/setores.html",
        setores=lista_setores
    )


@empresa_bp.route(
    "/empresa/setores/novo",
    methods=["GET", "POST"]
)
@empresa_cadastros_required
def setor_novo():
    dados_formulario = (
        SetorService.preparar_formulario()
    )

    if request.method == "POST":
        resultado = SetorService.criar(
            request.form
        )

        if resultado["sucesso"]:
            return redirect(
                url_for(
                    "empresa.setores"
                )
            )

        return (
            resultado["mensagem"],
            400
        )

    return render_template(
        "empresa/setor_form.html",
        modo="novo",
        setor=None,
        **dados_formulario
    )


@empresa_bp.route(
    "/empresa/setores/<int:setor_id>/editar",
    methods=["GET", "POST"]
)
@empresa_cadastros_required
def setor_editar(setor_id):
    setor = SetorService.obter(
        setor_id
    )

    if not setor:
        return (
            "Setor não encontrado.",
            404
        )

    dados_formulario = (
        SetorService.preparar_formulario()
    )

    if request.method == "POST":
        resultado = SetorService.editar(
            setor_id=setor_id,
            form=request.form
        )

        if resultado["sucesso"]:
            return redirect(
                url_for(
                    "empresa.setores"
                )
            )

        return (
            resultado["mensagem"],
            400
        )

    return render_template(
        "empresa/setor_form.html",
        modo="editar",
        setor=setor,
        **dados_formulario
    )


@empresa_bp.route(
    "/empresa/usuarios"
)
@empresa_cadastros_required
def usuarios():
    empresa_id = ContextService.empresa()

    conn = get_connection()
    cursor = conn.cursor(
        dictionary=True
    )

    try:
        cursor.execute(
            """
            SELECT
                id,
                nome,
                email,
                perfil,
                ativo,
                criado_em,
                tentativas_login,
                bloqueado_ate,
                ultimo_login
            FROM usuarios
            WHERE empresa_id = %s
              AND perfil <> 'SUPER_ADMIN'
            ORDER BY nome
            """,
            (empresa_id,)
        )

        lista_usuarios = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "empresa/usuarios.html",
        usuarios=lista_usuarios
    )


@empresa_bp.route(
    "/empresa/usuarios/novo",
    methods=["GET", "POST"]
)
@empresa_cadastros_required
def usuario_novo():
    empresa_id = ContextService.empresa()
    erro = None

    if request.method == "POST":
        dados_form = request.form.to_dict()

        dados_form["empresa_id"] = str(
            empresa_id
        )

        perfil = dados_form.get(
            "perfil"
        )

        if perfil not in PERFIS_USUARIO_EMPRESA:
            erro = (
                "O perfil selecionado não é permitido "
                "neste cadastro."
            )

        else:
            resultado = UsuarioService.criar_usuario(
                dados_form
            )

            if resultado.get("sucesso"):
                return redirect(
                    url_for(
                        "empresa.usuarios"
                    )
                )

            erro = resultado.get(
                "mensagem",
                "Não foi possível criar o usuário."
            )

    return render_template(
        "empresa/usuario_novo.html",
        erro=erro,
        perfis=PERFIS_USUARIO_EMPRESA
    )


@empresa_bp.route(
    "/empresa/usuarios/<int:usuario_id>/editar",
    methods=["GET", "POST"]
)
@empresa_cadastros_required
def usuario_editar(usuario_id):
    empresa_id = ContextService.empresa()

    usuario = UsuarioService.obter_usuario(
        usuario_id
    )

    if (
        not usuario
        or usuario.get("empresa_id") != empresa_id
    ):
        return (
            "Usuário não encontrado ou acesso não autorizado.",
            404
        )

    if usuario.get("perfil") in [
        "SUPER_ADMIN",
        "ADM_ASSESSORIA",
        "ADMIN_EMPRESA"
    ]:
        return (
            "Este usuário não pode ser alterado por esta tela.",
            403
        )

    erro = None

    if request.method == "POST":
        dados_form = request.form.to_dict()

        dados_form["empresa_id"] = str(
            empresa_id
        )

        perfil = dados_form.get(
            "perfil"
        )

        if perfil not in PERFIS_USUARIO_EMPRESA:
            erro = (
                "O perfil selecionado não é permitido "
                "nesta edição."
            )

        else:
            resultado = UsuarioService.editar_usuario(
                usuario_id=usuario_id,
                dados_form=dados_form
            )

            if resultado.get("sucesso"):
                return redirect(
                    url_for(
                        "empresa.usuarios"
                    )
                )

            erro = resultado.get(
                "mensagem",
                "Não foi possível atualizar o usuário."
            )

            usuario = {
                **usuario,
                "nome": request.form.get(
                    "nome"
                ),
                "email": request.form.get(
                    "email"
                ),
                "celular": request.form.get(
                    "celular"
                ),
                "whatsapp": request.form.get(
                    "whatsapp"
                ),
                "perfil": request.form.get(
                    "perfil"
                ),
                "ativo": request.form.get(
                    "ativo",
                    1
                )
            }

    return render_template(
        "empresa/usuario_editar.html",
        usuario=usuario,
        erro=erro,
        perfis=PERFIS_USUARIO_EMPRESA
    )


@empresa_bp.route(
    "/empresa/turnos"
)
@empresa_cadastros_required
def turnos():
    lista_turnos = TurnoService.listar()

    return render_template(
        "empresa/turnos.html",
        turnos=lista_turnos
    )


@empresa_bp.route(
    "/empresa/turnos/novo",
    methods=["GET", "POST"]
)
@empresa_cadastros_required
def turno_novo():
    if request.method == "POST":
        try:
            TurnoService.criar(
                request.form.get(
                    "nome"
                )
            )

            return redirect(
                url_for(
                    "empresa.turnos"
                )
            )

        except ValueError as erro:
            return render_template(
                "empresa/turno_form.html",
                turno=None,
                erro=str(erro)
            )

    return render_template(
        "empresa/turno_form.html",
        turno=None
    )


@empresa_bp.route(
    "/empresa/turnos/<int:turno_id>/editar",
    methods=["GET", "POST"]
)
@empresa_cadastros_required
def turno_editar(turno_id):
    try:
        turno = TurnoService.buscar_por_id(
            turno_id
        )

    except ValueError:
        return redirect(
            url_for(
                "empresa.turnos"
            )
        )

    if request.method == "POST":
        try:
            TurnoService.atualizar(
                turno_id=turno_id,
                nome=request.form.get(
                    "nome"
                )
            )

            return redirect(
                url_for(
                    "empresa.turnos"
                )
            )

        except ValueError as erro:
            return render_template(
                "empresa/turno_form.html",
                turno=turno,
                erro=str(erro)
            )

    return render_template(
        "empresa/turno_form.html",
        turno=turno
    )


@empresa_bp.route(
    "/empresa/turnos/<int:turno_id>/excluir",
    methods=["POST"]
)
@empresa_cadastros_required
def turno_excluir(turno_id):
    try:
        TurnoService.excluir(
            turno_id
        )

    except ValueError:
        pass

    return redirect(
        url_for(
            "empresa.turnos"
        )
    )

