from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from . import admin_bp
from falae.decorators import super_admin_required
from falae.services.empresa_service import EmpresaService


@admin_bp.route("/empresas")
@super_admin_required
def empresas():
    empresas_cadastradas = EmpresaService.listar_empresas_global()

    return render_template(
        "admin/empresas.html",
        empresas=empresas_cadastradas,
    )


@admin_bp.route(
    "/empresas/nova",
    methods=["GET", "POST"],
)
@super_admin_required
def empresa_nova():
    assessorias = EmpresaService.listar_assessorias_ativas()
    empresa = {}

    if request.method == "POST":
        dados_formulario = request.form.to_dict()

        try:
            resultado = EmpresaService.criar_empresa_global(
                dados_formulario
            )

            if resultado.get("sucesso"):
                empresa_id = resultado.get("empresa_id")

                flash(
                    resultado.get(
                        "mensagem",
                        "Empresa cadastrada com sucesso.",
                    ),
                    "success",
                )

                current_app.logger.info(
                    "Empresa cadastrada com sucesso. empresa_id=%s",
                    empresa_id,
                )

                return redirect(
                    url_for("admin.empresas")
                )

            empresa = resultado.get(
                "dados",
                dados_formulario,
            )

            flash(
                resultado.get(
                    "mensagem",
                    "Não foi possível cadastrar a empresa.",
                ),
                "danger",
            )

        except Exception:
            current_app.logger.exception(
                "Erro inesperado ao cadastrar empresa"
            )

            empresa = dados_formulario

            flash(
                "Ocorreu um erro inesperado ao cadastrar a empresa. "
                "Verifique os dados e tente novamente.",
                "danger",
            )

    return render_template(
        "admin/forms/empresa_form.html",
        modo="novo",
        empresa=empresa,
        assessorias=assessorias,
    )


@admin_bp.route(
    "/empresas/<int:empresa_id>/editar",
    methods=["GET", "POST"],
)
@super_admin_required
def empresa_editar(empresa_id):
    assessorias = EmpresaService.listar_assessorias_ativas()

    empresa = EmpresaService.obter_empresa_global_completa(
        empresa_id
    )

    if not empresa:
        flash(
            "Empresa não encontrada.",
            "danger",
        )

        return redirect(
            url_for("admin.empresas")
        )

    if request.method == "POST":
        dados_formulario = request.form.to_dict()

        try:
            resultado = EmpresaService.atualizar_empresa_global(
                empresa_id,
                dados_formulario,
            )

            if resultado.get("sucesso"):
                flash(
                    resultado.get(
                        "mensagem",
                        "Empresa atualizada com sucesso.",
                    ),
                    "success",
                )

                current_app.logger.info(
                    "Empresa atualizada com sucesso. empresa_id=%s",
                    empresa_id,
                )

                return redirect(
                    url_for("admin.empresas")
                )

            empresa = {
                **empresa,
                **resultado.get(
                    "dados",
                    dados_formulario,
                ),
            }

            flash(
                resultado.get(
                    "mensagem",
                    "Não foi possível atualizar a empresa.",
                ),
                "danger",
            )

        except Exception:
            current_app.logger.exception(
                "Erro inesperado ao atualizar empresa. empresa_id=%s",
                empresa_id,
            )

            empresa = {
                **empresa,
                **dados_formulario,
            }

            flash(
                "Ocorreu um erro inesperado ao atualizar a empresa. "
                "Verifique os dados e tente novamente.",
                "danger",
            )

    return render_template(
        "admin/forms/empresa_form.html",
        modo="editar",
        empresa=empresa,
        assessorias=assessorias,
    )


@admin_bp.route(
    "/empresas/<int:empresa_id>"
)
@super_admin_required
def empresa_detalhe(empresa_id):
    detalhe = EmpresaService.obter_detalhe_empresa_global(
        empresa_id
    )

    if not detalhe:
        flash(
            "Empresa não encontrada.",
            "danger",
        )

        return redirect(
            url_for("admin.empresas")
        )

    return render_template(
        "admin/empresa_detalhe.html",
        **detalhe,
    )