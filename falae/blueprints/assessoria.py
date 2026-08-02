from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from falae.decorators import perfil_required
from falae.services.empresa_service import EmpresaService


assessoria_bp = Blueprint(
    "assessoria",
    __name__,
    url_prefix="/assessoria"
)


assessoria_admin_required = perfil_required(
    "ADM_ASSESSORIA"
)


@assessoria_bp.route(
    "/dashboard"
)
@assessoria_admin_required
def dashboard():
    """
    Painel consolidado da assessoria.

    Exibe exclusivamente dados das empresas vinculadas
    à assessoria do usuário autenticado.
    """

    resultado = (
        EmpresaService
        .obter_dashboard_assessoria()
    )

    return render_template(
        "assessoria/dashboard.html",
        empresas=resultado.get(
            "empresas",
            []
        ),
        investigadores=resultado.get(
            "investigadores",
            []
        ),
        denuncias_recentes=resultado.get(
            "denuncias_recentes",
            []
        ),
        total_empresas=resultado.get(
            "total_empresas",
            0
        ),
        total_denuncias=resultado.get(
            "total_denuncias",
            0
        ),
        total_usuarios=resultado.get(
            "total_usuarios",
            0
        ),
        total_investigadores=resultado.get(
            "total_investigadores",
            0
        ),
        denuncias_abertas=resultado.get(
            "denuncias_abertas",
            0
        ),
        denuncias_criticas=resultado.get(
            "denuncias_criticas",
            0
        ),
        denuncias_encerradas=resultado.get(
            "denuncias_encerradas",
            0
        )
    )


@assessoria_bp.route(
    "/empresas"
)
@assessoria_admin_required
def empresas():
    empresas_assessoria = (
        EmpresaService
        .listar_empresas_assessoria()
    )

    return render_template(
        "assessoria/empresas.html",
        empresas=empresas_assessoria
    )


@assessoria_bp.route(
    "/empresas/nova",
    methods=["GET", "POST"]
)
@assessoria_admin_required
def empresa_nova():
    erro = None

    if request.method == "POST":
        try:
            EmpresaService.criar_empresa_assessoria(
                nome=request.form.get(
                    "nome"
                ),
                cnpj=request.form.get(
                    "cnpj"
                ),
                plano=request.form.get(
                    "plano"
                )
            )

            return redirect(
                url_for(
                    "assessoria.empresas"
                )
            )

        except ValueError as exc:
            erro = str(exc)

        except Exception:
            current_app.logger.exception(
                "Erro ao cadastrar empresa pela assessoria."
            )

            erro = (
                "Não foi possível cadastrar a empresa."
            )

    return render_template(
        "assessoria/empresa_nova.html",
        erro=erro
    )


@assessoria_bp.route(
    "/empresas/<int:empresa_id>/editar",
    methods=["GET", "POST"]
)
@assessoria_admin_required
def empresa_editar(
    empresa_id
):
    empresa = (
        EmpresaService
        .obter_empresa_assessoria(
            empresa_id
        )
    )

    if not empresa:
        return (
            "Empresa não encontrada ou acesso "
            "não autorizado."
        ), 404

    erro = None

    if request.method == "POST":
        try:
            EmpresaService.atualizar_empresa_assessoria(
                empresa_id=empresa_id,
                nome=request.form.get(
                    "nome"
                ),
                slug=request.form.get(
                    "slug"
                ),
                cnpj=request.form.get(
                    "cnpj"
                ),
                plano=request.form.get(
                    "plano"
                ),
                ativa=request.form.get(
                    "ativa",
                    1
                )
            )

            return redirect(
                url_for(
                    "assessoria.empresas"
                )
            )

        except ValueError as exc:
            erro = str(exc)

        except Exception:
            current_app.logger.exception(
                "Erro ao atualizar empresa %s pela assessoria.",
                empresa_id
            )

            erro = (
                "Não foi possível atualizar a empresa."
            )

        empresa = (
            EmpresaService
            .obter_empresa_assessoria(
                empresa_id
            )
        )

    return render_template(
        "assessoria/empresa_editar.html",
        empresa=empresa,
        erro=erro
    )


@assessoria_bp.route(
    "/empresas/<int:empresa_id>/entrar"
)
@perfil_required(
    "SUPER_ADMIN",
    "ADM_ASSESSORIA"
)
def entrar_empresa(
    empresa_id
):
    perfil = session.get(
        "perfil"
    )

    if perfil == "SUPER_ADMIN":
        empresa = (
            EmpresaService
            .obter_empresa_global(
                empresa_id
            )
        )

    elif perfil == "ADM_ASSESSORIA":
        empresa = (
            EmpresaService
            .obter_empresa_assessoria(
                empresa_id
            )
        )

    else:
        return (
            "Acesso não autorizado."
        ), 403

    if not empresa:
        return (
            "Empresa não encontrada ou acesso "
            "não autorizado."
        ), 404

    if not empresa.get(
        "ativa"
    ):
        return (
            "Não é possível acessar uma empresa inativa."
        ), 403

    session["empresa_ativa"] = empresa["id"]
    session["empresa_ativa_nome"] = empresa["nome"]

    if empresa.get(
        "slug"
    ):
        session["empresa_ativa_slug"] = empresa["slug"]
    else:
        session.pop(
            "empresa_ativa_slug",
            None
        )

    session.modified = True

    return redirect(
        url_for(
            "dashboard.centro_controle"
        )
    )


@assessoria_bp.route(
    "/sair-empresa"
)
@perfil_required(
    "SUPER_ADMIN",
    "ADM_ASSESSORIA"
)
def sair_empresa():
    session.pop(
        "empresa_ativa",
        None
    )

    session.pop(
        "empresa_ativa_nome",
        None
    )

    session.pop(
        "empresa_ativa_slug",
        None
    )

    session.modified = True

    if session.get(
        "perfil"
    ) == "SUPER_ADMIN":
        return redirect(
            url_for(
                "admin.dashboard"
            )
        )

    return redirect(
        url_for(
            "assessoria.dashboard"
        )
    )