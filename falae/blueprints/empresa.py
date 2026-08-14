from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    flash
)


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
            flash(
                resultado["mensagem"],
                "success"
            )

            return redirect(
                url_for("empresa.unidades")
            )

        flash(
            resultado.get(
                "mensagem",
                "Não foi possível cadastrar a unidade."
            ),
            "danger"
        )

        return render_template(
            "empresa/unidade_form.html",
            modo="novo",
            unidade=request.form.to_dict()
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
        flash(
            "Unidade não encontrada ou acesso não autorizado.",
            "danger"
        )

        return redirect(
            url_for("empresa.unidades")
        )

    if request.method == "POST":
        resultado = UnidadeService.editar(
            unidade_id,
            request.form
        )

        if resultado["sucesso"]:
            flash(
                resultado["mensagem"],
                "success"
            )

            return redirect(
                url_for("empresa.unidades")
            )

        flash(
            resultado.get(
                "mensagem",
                "Não foi possível atualizar a unidade."
            ),
            "danger"
        )

        unidade_form = {
            **unidade,
            **request.form.to_dict()
        }

        return render_template(
            "empresa/unidade_form.html",
            modo="editar",
            unidade=unidade_form
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

    if resultado["sucesso"]:
        flash(
            resultado.get(
                "mensagem",
                "Status da unidade atualizado com sucesso."
            ),
            "success"
        )
    else:
        flash(
            resultado.get(
                "mensagem",
                "Não foi possível atualizar o status da unidade."
            ),
            "danger"
        )

    return redirect(
        url_for("empresa.unidades")
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
            flash(
                resultado.get(
                    "mensagem",
                    "Setor cadastrado com sucesso."
                ),
                "success"
            )

            return redirect(
                url_for("empresa.setores")
            )

        flash(
            resultado.get(
                "mensagem",
                "Não foi possível cadastrar o setor."
            ),
            "danger"
        )

        return render_template(
            "empresa/setor_form.html",
            modo="novo",
            setor=None,
            **dados_formulario
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
        flash(
            "Setor não encontrado ou acesso não autorizado.",
            "danger"
        )

        return redirect(
            url_for("empresa.setores")
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
            flash(
                resultado.get(
                    "mensagem",
                    "Setor atualizado com sucesso."
                ),
                "success"
            )

            return redirect(
                url_for("empresa.setores")
            )

        flash(
            resultado.get(
                "mensagem",
                "Não foi possível atualizar o setor."
            ),
            "danger"
        )

        return render_template(
            "empresa/setor_form.html",
            modo="editar",
            setor=setor,
            **dados_formulario
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
    lista_usuarios = UsuarioService.listar_usuarios()

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
@perfil_required(
    "SUPER_ADMIN",
    "ADM_ASSESSORIA",
    "ADMIN_EMPRESA"
)
def editar_usuario(usuario_id):
    usuario = UsuarioService.obter_usuario(
        usuario_id
    )

    if not usuario:
        flash(
            "Usuário não encontrado ou acesso não autorizado.",
            "danger"
        )

        return redirect(
            url_for("admin.usuarios")
        )

    dados_formulario = (
        UsuarioService.preparar_formulario_usuario()
    )

    if request.method == "POST":
        resultado = UsuarioService.editar_usuario(
            usuario_id=usuario_id,
            dados_form=request.form
        )

        if resultado["sucesso"]:
            flash(
                resultado["mensagem"],
                "success"
            )

            return redirect(
                url_for("admin.usuarios")
            )

        flash(
            resultado.get(
                "mensagem",
                "Não foi possível atualizar o usuário."
            ),
            "danger"
        )

        usuario_form = {
            **usuario,
            "nome": request.form.get(
                "nome",
                usuario.get("nome")
            ),
            "email": request.form.get(
                "email",
                usuario.get("email")
            ),
            "celular": request.form.get(
                "celular",
                usuario.get("celular")
            ),
            "whatsapp": request.form.get(
                "whatsapp",
                usuario.get("whatsapp")
            ),
            "perfil": request.form.get(
                "perfil",
                usuario.get("perfil")
            ),
            "empresa_id": request.form.get(
                "empresa_id"
            ) or None,
            "assessoria_id": request.form.get(
                "assessoria_id"
            ) or None,
            "ativo": request.form.get(
                "ativo",
                usuario.get("ativo", 1)
            )
        }

        return render_template(
            "empresa/usuario_editar.html",
            usuario=usuario_form,
            empresas=dados_formulario["empresas"],
            assessorias=dados_formulario["assessorias"],
            perfis=dados_formulario["perfis"]
        )

    return render_template(
        "empresa/usuario_editar.html",
        usuario=usuario,
        empresas=dados_formulario["empresas"],
        assessorias=dados_formulario["assessorias"],
        perfis=dados_formulario["perfis"]
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
                request.form.get("nome")
            )

            flash(
                "Turno cadastrado com sucesso.",
                "success"
            )

            return redirect(
                url_for("empresa.turnos")
            )

        except ValueError as erro:
            flash(
                str(erro),
                "danger"
            )

            return render_template(
                "empresa/turno_form.html",
                turno=None
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

    except ValueError as erro:
        flash(
            str(erro),
            "danger"
        )

        return redirect(
            url_for("empresa.turnos")
        )

    if request.method == "POST":
        try:
            TurnoService.atualizar(
                turno_id=turno_id,
                nome=request.form.get("nome")
            )

            flash(
                "Turno atualizado com sucesso.",
                "success"
            )

            return redirect(
                url_for("empresa.turnos")
            )

        except ValueError as erro:
            flash(
                str(erro),
                "danger"
            )

            turno_form = {
                **turno,
                "nome": request.form.get(
                    "nome",
                    turno.get("nome")
                )
            }

            return render_template(
                "empresa/turno_form.html",
                turno=turno_form
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

        flash(
            "Turno excluído com sucesso.",
            "success"
        )

    except ValueError as erro:
        flash(
            str(erro),
            "danger"
        )

    return redirect(
        url_for("empresa.turnos")
    )