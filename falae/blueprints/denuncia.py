from io import BytesIO

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for
)
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from falae.decorators import empresa_admin_required, perfil_required
from falae.repositories.anexo_repository import AnexoRepository
from falae.services.audit_service import AuditService
from falae.services.denuncia_service import DenunciaService
from falae.services.plano_acao_service import PlanoAcaoService
from falae.services.triagem_service import TriagemService


denuncia_bp = Blueprint("denuncia", __name__)


@denuncia_bp.route("/empresa/denuncias")
@perfil_required(
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "GESTOR",
    "AUDITOR",
    "VISUALIZADOR"
)
def empresa_denuncias():
    filtros = {
        "protocolo": request.args.get("protocolo"),
        "status": request.args.get("status"),
        "categoria": request.args.get("categoria"),
        "criticidade": request.args.get("criticidade"),
        "unidade_id": request.args.get("unidade_id"),
        "data_inicio": request.args.get("data_inicio"),
        "data_fim": request.args.get("data_fim"),
        "ordenacao": request.args.get(
            "ordenacao",
            "mais_recentes"
        )
    }

    resultado = DenunciaService.listar_paginado(
        **filtros,
        page=request.args.get("page", 1, type=int),
        per_page=20
    )

    return render_template(
        "empresa/denuncias.html",
        denuncias=resultado["denuncias"],
        categorias=DenunciaService.listar_categorias(),
        criticidades=DenunciaService.listar_criticidades(),
        unidades=DenunciaService.listar_unidades(),
        filtros=filtros,
        paginacao=resultado["paginacao"]
    )


@denuncia_bp.route("/empresa/denuncia/<int:denuncia_id>")
@perfil_required(
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "GESTOR",
    "INVESTIGADOR",
    "AUDITOR",
    "VISUALIZADOR"
)
def empresa_denuncia_detalhe(denuncia_id):
    dados = DenunciaService.obter_denuncia_com_workflow(denuncia_id)

    if not dados:
        return (
            "Denúncia não encontrada ou acesso não autorizado.",
            404
        )

    perfil = session.get("perfil")
    usuario_id = session.get("usuario_id")

    if (
        perfil == "INVESTIGADOR"
        and dados["denuncia"].get("responsavel_id") != usuario_id
    ):
        return "Acesso não autorizado para esta denúncia.", 403

    timeline = AuditService.listar_timeline(
        modulo="denuncias",
        registro_id=denuncia_id,
        empresa_id=session["empresa_id"]
    )

    anexo_repo = AnexoRepository()

    try:
        anexos = anexo_repo.listar_por_denuncia(
            denuncia_id=denuncia_id,
            empresa_id=session["empresa_id"]
        )
    finally:
        anexo_repo.close()

    return render_template(
        "empresa/denuncia_detalhe.html",
        denuncia=dados["denuncia"],
        workflow=dados["workflow"],
        linha_do_tempo=dados["linha_do_tempo"],
        resumo_etapa=dados["resumo_etapa"],
        timeline=timeline,
        planos_acao=PlanoAcaoService.listar_por_denuncia(denuncia_id),
        resumo_planos=PlanoAcaoService.resumo_por_denuncia(denuncia_id),
        investigadores=DenunciaService.listar_investigadores(),
        anexos=anexos,
        modo_edicao_triagem=(
            request.args.get("editar_triagem") == "1"
        )
    )


@denuncia_bp.route("/empresa/anexo/<int:anexo_id>")
@perfil_required(
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "GESTOR",
    "INVESTIGADOR",
    "AUDITOR",
    "VISUALIZADOR"
)
def empresa_visualizar_anexo(anexo_id):
    repo = AnexoRepository()

    try:
        anexo = repo.buscar_por_id(
            anexo_id=anexo_id,
            empresa_id=session["empresa_id"]
        )
    finally:
        repo.close()

    if not anexo:
        return (
            "Anexo não encontrado ou acesso não autorizado.",
            404
        )

    return send_file(
        anexo["caminho"],
        mimetype=anexo["mime_type"],
        as_attachment=False,
        download_name=anexo["nome_original"]
    )


@denuncia_bp.route("/empresa/anexo/<int:anexo_id>/download")
@perfil_required(
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "GESTOR",
    "INVESTIGADOR",
    "AUDITOR",
    "VISUALIZADOR"
)
def empresa_download_anexo(anexo_id):
    repo = AnexoRepository()

    try:
        anexo = repo.buscar_por_id(
            anexo_id=anexo_id,
            empresa_id=session["empresa_id"]
        )
    finally:
        repo.close()

    if not anexo:
        return (
            "Anexo não encontrado ou acesso não autorizado.",
            404
        )

    return send_file(
        anexo["caminho"],
        mimetype=anexo["mime_type"],
        as_attachment=True,
        download_name=anexo["nome_original"]
    )


@denuncia_bp.route(
    "/empresa/denuncia/<int:denuncia_id>/atribuir-responsavel",
    methods=["POST"]
)
@perfil_required("SUPER_ADMIN", "ADMIN_EMPRESA", "GESTOR")
def empresa_atribuir_responsavel(denuncia_id):
    resultado = DenunciaService.atribuir_responsavel(
        denuncia_id=denuncia_id,
        responsavel_id=request.form.get("responsavel_id") or None
    )

    if resultado.get("sucesso"):
        AuditService.registrar(
            modulo="denuncias",
            acao="atribuir_responsavel",
            registro_id=denuncia_id,
            valor_antigo=resultado.get("valor_antigo"),
            valor_novo=resultado.get("valor_novo")
        )

    flash(
        resultado.get("mensagem", "Não foi possível atribuir responsável."),
        "success" if resultado.get("sucesso") else "warning"
    )

    return redirect(
        url_for(
            "denuncia.empresa_denuncia_detalhe",
            denuncia_id=denuncia_id
        )
    )


@denuncia_bp.route(
    "/empresa/denuncia/<int:denuncia_id>/concluir-triagem",
    methods=["POST"]
)
@empresa_admin_required
def empresa_concluir_triagem(denuncia_id):
    resultado = TriagemService.concluir_triagem(
        denuncia_id=denuncia_id,
        criticidade=request.form.get("criticidade"),
        categoria=request.form.get("categoria"),
        responsavel_id=request.form.get("responsavel_id"),
        parecer_triagem=request.form.get("parecer_triagem"),
        necessita_investigacao=request.form.get(
            "necessita_investigacao"
        ),
        prioridade=request.form.get("prioridade")
    )

    if resultado.get("sucesso"):
        AuditService.registrar(
            modulo="triagem",
            acao="concluir_triagem",
            registro_id=denuncia_id,
            valor_antigo=resultado.get("denuncia"),
            valor_novo=resultado.get("resultado")
        )

    flash(
        resultado.get("mensagem", "Não foi possível concluir a triagem."),
        "success" if resultado.get("sucesso") else "warning"
    )

    return redirect(
        url_for(
            "denuncia.empresa_denuncia_detalhe",
            denuncia_id=denuncia_id
        )
    )


@denuncia_bp.route(
    "/empresa/denuncia/<int:denuncia_id>/avancar-etapa",
    methods=["POST"]
)
@perfil_required(
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "GESTOR",
    "INVESTIGADOR"
)
def empresa_avancar_etapa_denuncia(denuncia_id):
    observacao = request.form.get("observacao_workflow")

    resultado = DenunciaService.avancar_etapa(
        denuncia_id=denuncia_id,
        observacao=observacao
    )

    if resultado.get("sucesso"):
        AuditService.registrar(
            modulo="denuncias",
            acao="avancar_etapa_denuncia",
            registro_id=denuncia_id,
            valor_antigo={
                "etapa_atual": resultado.get("etapa_anterior")
            },
            valor_novo={
                "etapa_atual": resultado.get("etapa_atual"),
                "etapa_nome": resultado.get("etapa_nome"),
                "observacao": observacao
            }
        )

    flash(
        resultado.get("mensagem", "Não foi possível avançar a etapa."),
        "success" if resultado.get("sucesso") else "warning"
    )

    return redirect(
        url_for(
            "denuncia.empresa_denuncia_detalhe",
            denuncia_id=denuncia_id
        )
    )


@denuncia_bp.route(
    "/empresa/denuncia/<int:denuncia_id>/atualizar",
    methods=["POST"]
)
@perfil_required(
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "GESTOR",
    "INVESTIGADOR"
)
def empresa_atualizar_denuncia(denuncia_id):
    resultado = DenunciaService.atualizar_denuncia(
        denuncia_id=denuncia_id,
        status=request.form.get("status"),
        criticidade=request.form.get("criticidade") or None,
        observacao_interna=request.form.get("observacao_interna")
    )

    if resultado.get("sucesso"):
        AuditService.registrar(
            modulo="denuncias",
            acao="atualizar_denuncia",
            registro_id=denuncia_id,
            valor_antigo=resultado.get("valor_antigo"),
            valor_novo=resultado.get("valor_novo")
        )

    flash(
        resultado.get("mensagem", "Não foi possível atualizar a denúncia."),
        "success" if resultado.get("sucesso") else "warning"
    )

    return redirect(
        url_for(
            "denuncia.empresa_denuncia_detalhe",
            denuncia_id=denuncia_id
        )
    )


@denuncia_bp.route(
    "/empresa/denuncia/<int:denuncia_id>/plano",
    methods=["POST"]
)
@perfil_required(
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "GESTOR",
    "INVESTIGADOR"
)
def empresa_criar_plano(denuncia_id):
    resultado = PlanoAcaoService.criar(
        denuncia_id=denuncia_id,
        titulo=request.form.get("titulo"),
        descricao=request.form.get("descricao"),
        responsavel=request.form.get("responsavel"),
        prazo=request.form.get("prazo") or None,
        status=request.form.get("status")
    )

    flash(
        resultado.get(
            "mensagem",
            "Não foi possível cadastrar o plano de ação."
        ),
        "success" if resultado.get("sucesso") else "warning"
    )

    return redirect(
        url_for(
            "denuncia.empresa_denuncia_detalhe",
            denuncia_id=denuncia_id
        ) + "#planos"
    )


@denuncia_bp.route(
    "/empresa/plano/<int:plano_id>/editar",
    methods=["GET", "POST"]
)
@perfil_required(
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "GESTOR",
    "INVESTIGADOR"
)
def empresa_editar_plano(plano_id):
    plano = PlanoAcaoService.obter(plano_id)

    if not plano:
        return "Plano de ação não encontrado.", 404

    if request.method == "POST":
        denuncia_id = PlanoAcaoService.atualizar(
            plano_id=plano_id,
            titulo=request.form.get("titulo"),
            descricao=request.form.get("descricao"),
            responsavel=request.form.get("responsavel"),
            prazo=request.form.get("prazo") or None,
            status=request.form.get("status")
        )

        return redirect(
            url_for(
                "denuncia.empresa_denuncia_detalhe",
                denuncia_id=denuncia_id
            )
        )

    return render_template(
        "empresa/plano_editar.html",
        plano=plano
    )


@denuncia_bp.route(
    "/empresa/plano/<int:plano_id>/excluir",
    methods=["POST"]
)
@perfil_required(
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "GESTOR",
    "INVESTIGADOR"
)
def empresa_excluir_plano(plano_id):
    denuncia_id = PlanoAcaoService.excluir(plano_id)

    if not denuncia_id:
        return "Plano de ação não encontrado.", 404

    return redirect(
        url_for(
            "denuncia.empresa_denuncia_detalhe",
            denuncia_id=denuncia_id
        )
    )


@denuncia_bp.route("/empresa/denuncias/exportar")
@empresa_admin_required
def exportar_denuncias_excel():
    denuncias = DenunciaService.obter_dados_exportacao()

    wb = Workbook()
    ws = wb.active
    ws.title = "Denúncias"

    ws.append([
        "Protocolo",
        "Unidade",
        "Setor",
        "Categoria",
        "Criticidade",
        "Status",
        "Etapa Atual",
        "Data"
    ])

    for denuncia in denuncias:
        ws.append([
            denuncia["protocolo"],
            denuncia["unidade"],
            denuncia["setor"],
            denuncia["categoria"],
            denuncia["criticidade"],
            denuncia["status"],
            denuncia["etapa_atual"],
            str(denuncia["criado_em"])
        ])

    arquivo = BytesIO()
    wb.save(arquivo)
    arquivo.seek(0)

    return send_file(
        arquivo,
        as_attachment=True,
        download_name="denuncias.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )


@denuncia_bp.route("/empresa/denuncias/exportar-pdf")
@empresa_admin_required
def exportar_denuncias_pdf():
    denuncias = DenunciaService.obter_dados_exportacao(limite=100)

    arquivo = BytesIO()
    pdf = canvas.Canvas(arquivo, pagesize=A4)

    _, altura = A4
    y = altura - 50

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Relatório de Denúncias")
    y -= 30
    pdf.setFont("Helvetica", 9)

    for denuncia in denuncias:
        linha = (
            f"{denuncia['protocolo']} | "
            f"{denuncia['unidade']} | "
            f"{denuncia['categoria']} | "
            f"{denuncia['status']} | "
            f"{denuncia['etapa_atual']} | "
            f"{denuncia['criado_em']}"
        )

        pdf.drawString(50, y, linha[:110])
        y -= 18

        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = altura - 50

    pdf.save()
    arquivo.seek(0)

    return send_file(
        arquivo,
        as_attachment=True,
        download_name="denuncias.pdf",
        mimetype="application/pdf"
    )


@denuncia_bp.route(
    "/empresa/plano/<int:plano_id>/concluir",
    methods=["POST"]
)
@perfil_required(
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "GESTOR",
    "INVESTIGADOR"
)
def empresa_concluir_plano(plano_id):
    denuncia_id = PlanoAcaoService.concluir(plano_id)

    if not denuncia_id:
        return "Plano de ação não encontrado.", 404

    return redirect(
        url_for(
            "denuncia.empresa_denuncia_detalhe",
            denuncia_id=denuncia_id
        )
    )
