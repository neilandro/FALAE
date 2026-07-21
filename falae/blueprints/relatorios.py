from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    send_file,
    url_for
)

from falae.decorators import perfil_required
from falae.services.interpretacao_psicossocial_service import (
    InterpretacaoPsicossocialService
)
from falae.services.relatorio_psicossocial_pdf_service import (
    RelatorioPsicossocialPDFService
)
from falae.services.relatorio_psicossocial_service import (
    RelatorioPsicossocialService
)


relatorios_bp = Blueprint(
    "relatorios",
    __name__
)


relatorios_empresa_required = perfil_required(
    "SUPER_ADMIN",
    "ADM_ASSESSORIA",
    "ADMIN_EMPRESA",
    "GESTOR",
    "AUDITOR",
    "VISUALIZADOR"
)


def _obter_filtros_request() -> dict:
    return {
        "data_inicio": (
            request.args.get("data_inicio")
            or request.form.get("data_inicio")
            or None
        ),
        "data_fim": (
            request.args.get("data_fim")
            or request.form.get("data_fim")
            or None
        ),
        "unidade_id": (
            request.args.get("unidade_id")
            or request.form.get("unidade_id")
            or None
        ),
        "setor_id": (
            request.args.get("setor_id")
            or request.form.get("setor_id")
            or None
        ),
        "turno_id": (
            request.args.get("turno_id")
            or request.form.get("turno_id")
            or None
        )
    }


@relatorios_bp.route(
    "/empresa/relatorios/psicossocial",
    methods=["GET", "POST"]
)
@relatorios_empresa_required
def relatorio_psicossocial():
    erro = None
    dados = None
    interpretacoes = None

    try:
        opcoes_filtro = (
            RelatorioPsicossocialService
            .preparar_filtros()
        )

    except ValueError as exc:
        return render_template(
            "empresa/relatorio_psicossocial.html",
            erro=str(exc),
            dados=None,
            interpretacoes=None,
            filtros={},
            unidades=[],
            setores=[],
            turnos=[]
        )

    filtros = _obter_filtros_request()

    gerar_visualizacao = (
        request.method == "POST"
        or request.args.get("visualizar") == "1"
    )

    if gerar_visualizacao:
        try:
            dados = (
                RelatorioPsicossocialService
                .gerar_dados(
                    filtros=filtros
                )
            )

            interpretacoes = (
                InterpretacaoPsicossocialService
                .gerar_interpretacoes(
                    dados
                )
            )

        except ValueError as exc:
            erro = str(exc)

        except Exception as exc:
            current_app.logger.exception(
                "Erro ao gerar a pré-visualização "
                "do relatório psicossocial."
            )

            erro = (
                "Não foi possível gerar a pré-visualização "
                f"do relatório: {str(exc)}"
            )

    return render_template(
        "empresa/relatorio_psicossocial.html",
        erro=erro,
        dados=dados,
        interpretacoes=interpretacoes,
        filtros=filtros,
        unidades=opcoes_filtro.get(
            "unidades",
            []
        ),
        setores=opcoes_filtro.get(
            "setores",
            []
        ),
        turnos=opcoes_filtro.get(
            "turnos",
            []
        )
    )


@relatorios_bp.route(
    "/empresa/relatorios/psicossocial/pdf",
    methods=["GET"]
)
@relatorios_empresa_required
def baixar_relatorio_psicossocial():
    filtros = _obter_filtros_request()

    try:
        resultado = (
            RelatorioPsicossocialPDFService
            .gerar_relatorio(
                filtros=filtros
            )
        )

        return send_file(
            resultado["arquivo"],
            mimetype=resultado["mimetype"],
            as_attachment=True,
            download_name=resultado[
                "nome_arquivo"
            ],
            max_age=0
        )

    except ValueError as exc:
        return redirect(
            url_for(
                "relatorios.relatorio_psicossocial",
                erro=str(exc),
                **{
                    chave: valor
                    for chave, valor in filtros.items()
                    if valor
                }
            )
        )

    except Exception as exc:
        current_app.logger.exception(
            "Erro ao gerar o PDF do relatório psicossocial."
        )

        return redirect(
            url_for(
                "relatorios.relatorio_psicossocial",
                erro=(
                    "Não foi possível gerar o PDF do relatório: "
                    f"{str(exc)}"
                ),
                **{
                    chave: valor
                    for chave, valor in filtros.items()
                    if valor
                }
            )
        )