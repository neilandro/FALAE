from flask import Blueprint, render_template, session, request, send_file, redirect, url_for, flash
from io import BytesIO
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from db import get_connection
from falae.decorators import empresa_admin_required, perfil_required
from falae.repositories.denuncia_repository import DenunciaRepository
from falae.repositories.anexo_repository import AnexoRepository
from falae.services.denuncia_service import DenunciaService


denuncia_bp = Blueprint("denuncia", __name__)


@denuncia_bp.route("/empresa/denuncias")
@perfil_required("SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "GESTOR",
    "AUDITOR",
    "VISUALIZADOR"
)
def empresa_denuncias():
    protocolo = request.args.get("protocolo")
    status = request.args.get("status")
    categoria = request.args.get("categoria")
    criticidade = request.args.get("criticidade")
    unidade_id = request.args.get("unidade_id")
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")
    ordenacao = request.args.get("ordenacao", "recentes")

    page = request.args.get("page", 1, type=int)
    per_page = 20

    if page < 1:
        page = 1

    offset = (page - 1) * per_page

    filtros = ["d.empresa_id = %s"]
    params = [session["empresa_id"]]

    if protocolo:
        filtros.append("d.protocolo LIKE %s")
        params.append(f"%{protocolo}%")

    if status:
        filtros.append("d.status = %s")
        params.append(status)

    if categoria:
        filtros.append("d.categoria = %s")
        params.append(categoria)

    if criticidade:
        filtros.append("d.criticidade = %s")
        params.append(criticidade)

    if unidade_id:
        filtros.append("d.unidade_id = %s")
        params.append(unidade_id)

    if data_inicio:
        filtros.append("DATE(d.criado_em) >= %s")
        params.append(data_inicio)

    if data_fim:
        filtros.append("DATE(d.criado_em) <= %s")
        params.append(data_fim)

    if ordenacao == "antigas":
        order_by = "d.criado_em ASC"
    elif ordenacao == "protocolo_asc":
        order_by = "d.protocolo ASC"
    elif ordenacao == "protocolo_desc":
        order_by = "d.protocolo DESC"
    else:
        order_by = "d.criado_em DESC"

    where_sql = " AND ".join(filtros)

    repo = DenunciaRepository()

    try:
        total_registros = repo.contar_denuncias(where_sql, params)
        total_paginas = (total_registros + per_page - 1) // per_page

        denuncias = repo.listar_denuncias(
            where_sql=where_sql,
            params=params,
            order_by=order_by,
            per_page=per_page,
            offset=offset
        )
    finally:
        repo.close()

    unidades = DenunciaService.listar_unidades()
    categorias = DenunciaService.listar_categorias()
    criticidades = DenunciaService.listar_criticidades()

    return render_template(
        "empresa/denuncias.html",
        denuncias=denuncias,
        categorias=categorias,
        criticidades=criticidades,
        unidades=unidades,
        filtros={
            "protocolo": protocolo,
            "status": status,
            "categoria": categoria,
            "criticidade": criticidade,
            "unidade_id": unidade_id,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "ordenacao": ordenacao
        },
        paginacao={
            "page": page,
            "per_page": per_page,
            "total_registros": total_registros,
            "total_paginas": total_paginas
        }
    )


@denuncia_bp.route("/empresa/denuncia/<int:denuncia_id>")
@perfil_required("ADMIN_EMPRESA", "GESTOR", "INVESTIGADOR", "AUDITOR", "VISUALIZADOR")
def empresa_denuncia_detalhe(denuncia_id):
    from falae.services.audit_service import AuditService
    from falae.services.plano_acao_service import PlanoAcaoService

    dados = DenunciaService.obter_denuncia_com_workflow(denuncia_id)
    modo_edicao_triagem = request.args.get("editar_triagem") == "1"

    if not dados:
        return "Denúncia não encontrada ou acesso não autorizado.", 404
    
    perfil = session.get("perfil")
    usuario_id = session.get("usuario_id")

    if perfil == "INVESTIGADOR":
        if dados["denuncia"].get("responsavel_id") != usuario_id:
            return "Acesso não autorizado para esta denúncia.", 403

    timeline = AuditService.listar_timeline(
        modulo="denuncias",
        registro_id=denuncia_id,
        empresa_id=session["empresa_id"]
    )

    planos_acao = PlanoAcaoService.listar_por_denuncia(denuncia_id)
    resumo_planos = PlanoAcaoService.resumo_por_denuncia(denuncia_id)
    investigadores = DenunciaService.listar_investigadores()

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
        planos_acao=planos_acao,
        resumo_planos=resumo_planos,
        investigadores=investigadores,
        anexos=anexos,
        modo_edicao_triagem=modo_edicao_triagem
    )


@denuncia_bp.route("/empresa/anexo/<int:anexo_id>")
@perfil_required("SUPER_ADMIN", "ADMIN_EMPRESA", "GESTOR", "INVESTIGADOR", "AUDITOR", "VISUALIZADOR")
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
        return "Anexo não encontrado ou acesso não autorizado.", 404

    return send_file(
        anexo["caminho"],
        mimetype=anexo["mime_type"],
        as_attachment=False,
        download_name=anexo["nome_original"]
    )


@denuncia_bp.route("/empresa/anexo/<int:anexo_id>/download")
@perfil_required("SUPER_ADMIN", "ADMIN_EMPRESA", "GESTOR", "INVESTIGADOR", "AUDITOR", "VISUALIZADOR")
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
        return "Anexo não encontrado ou acesso não autorizado.", 404

    return send_file(
        anexo["caminho"],
        mimetype=anexo["mime_type"],
        as_attachment=True,
        download_name=anexo["nome_original"]
    )


@denuncia_bp.route("/empresa/denuncia/<int:denuncia_id>/atribuir-responsavel", methods=["POST"])
@perfil_required("SUPER_ADMIN", "ADMIN_EMPRESA", "GESTOR")
def empresa_atribuir_responsavel(denuncia_id):
    from falae.services.audit_service import AuditService

    responsavel_id = request.form.get("responsavel_id") or None

    resultado = DenunciaService.atribuir_responsavel(
        denuncia_id=denuncia_id,
        responsavel_id=responsavel_id
    )

    if resultado.get("sucesso"):
        AuditService.registrar(
            modulo="denuncias",
            acao="atribuir_responsavel",
            registro_id=denuncia_id,
            valor_antigo=resultado.get("valor_antigo"),
            valor_novo=resultado.get("valor_novo")
        )

    return redirect(url_for("denuncia.empresa_denuncia_detalhe", denuncia_id=denuncia_id))

@denuncia_bp.route("/empresa/denuncia/<int:denuncia_id>/concluir-triagem", methods=["POST"])
@empresa_admin_required
def empresa_concluir_triagem(denuncia_id):
    from falae.services.triagem_service import TriagemService
    from falae.services.audit_service import AuditService

    resultado = TriagemService.concluir_triagem(
        denuncia_id=denuncia_id,
        criticidade=request.form.get("criticidade"),
        categoria=request.form.get("categoria"),
        responsavel_id=request.form.get("responsavel_id"),
        parecer_triagem=request.form.get("parecer_triagem"),
        necessita_investigacao=request.form.get("necessita_investigacao"),
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

    return redirect(url_for("denuncia.empresa_denuncia_detalhe", denuncia_id=denuncia_id))


@denuncia_bp.route("/empresa/denuncia/<int:denuncia_id>/avancar-etapa", methods=["POST"])
@perfil_required("SUPER_ADMIN", "ADMIN_EMPRESA", "GESTOR", "INVESTIGADOR")
def empresa_avancar_etapa_denuncia(denuncia_id):
    from falae.services.audit_service import AuditService

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
            valor_antigo=None,
            valor_novo={
                "etapa_atual": resultado.get("etapa_atual"),
                "etapa_nome": resultado.get("etapa_nome"),
                "observacao": observacao
            }
        )

    return redirect(url_for("denuncia.empresa_denuncia_detalhe", denuncia_id=denuncia_id))


@denuncia_bp.route("/empresa/denuncia/<int:denuncia_id>/atualizar", methods=["POST"])
@perfil_required("SUPER_ADMIN", "ADMIN_EMPRESA", "GESTOR", "INVESTIGADOR")
def empresa_atualizar_denuncia(denuncia_id):
    from falae.services.audit_service import AuditService

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT status, observacao_interna, criticidade
        FROM denuncias
        WHERE id = %s AND empresa_id = %s
    """, (denuncia_id, session["empresa_id"]))

    denuncia = cursor.fetchone()

    if not denuncia:
        cursor.close()
        conn.close()
        return "Denúncia não encontrada ou acesso não autorizado.", 404

    status = request.form.get("status")
    criticidade = request.form.get("criticidade") or None
    observacao_interna = request.form.get("observacao_interna")

    etapa_atual = None

    if status == "NOVA":
        etapa_atual = "TRIAGEM"
    elif status == "EM_ANALISE":
        etapa_atual = "INVESTIGACAO"
    elif status == "CONCLUIDA":
        etapa_atual = "ENCERRAMENTO"
    elif status == "ARQUIVADA":
        etapa_atual = "ARQUIVADA"

    cursor.execute("""
        UPDATE denuncias
        SET status = %s,
            criticidade = %s,
            etapa_atual = %s,
            observacao_interna = %s,
            data_encerramento = CASE
                WHEN %s IN ('CONCLUIDA', 'ARQUIVADA') THEN NOW()
                ELSE data_encerramento
            END
        WHERE id = %s AND empresa_id = %s
    """, (
        status,
        criticidade,
        etapa_atual,
        observacao_interna,
        status,
        denuncia_id,
        session["empresa_id"]
    ))

    conn.commit()
    cursor.close()
    conn.close()

    AuditService.registrar(
        modulo="denuncias",
        acao="atualizar_denuncia",
        registro_id=denuncia_id,
        valor_antigo={
            "status": denuncia["status"],
            "criticidade": denuncia["criticidade"],
            "observacao_interna": denuncia["observacao_interna"]
        },
        valor_novo={
            "status": status,
            "criticidade": criticidade,
            "etapa_atual": etapa_atual,
            "observacao_interna": observacao_interna
        }
    )

    return redirect(url_for("denuncia.empresa_denuncia_detalhe", denuncia_id=denuncia_id))


@denuncia_bp.route("/empresa/denuncia/<int:denuncia_id>/plano", methods=["POST"])
@perfil_required("SUPER_ADMIN", "ADMIN_EMPRESA", "GESTOR", "INVESTIGADOR")
def empresa_criar_plano(denuncia_id):
    from falae.services.plano_acao_service import PlanoAcaoService

    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")
    responsavel = request.form.get("responsavel")
    prazo = request.form.get("prazo") or None
    status = request.form.get("status")

    resultado = PlanoAcaoService.criar(
        denuncia_id=denuncia_id,
        titulo=titulo,
        descricao=descricao,
        responsavel=responsavel,
        prazo=prazo,
        status=status
    )

    flash(
        resultado.get("mensagem", "Não foi possível cadastrar o plano de ação."),
        "success" if resultado.get("sucesso") else "warning"
    )

    return redirect(
        url_for("denuncia.empresa_denuncia_detalhe", denuncia_id=denuncia_id) + "#planos"
    )

@denuncia_bp.route("/empresa/plano/<int:plano_id>/editar", methods=["GET", "POST"])
@perfil_required("SUPER_ADMIN", "ADMIN_EMPRESA", "GESTOR", "INVESTIGADOR")
def empresa_editar_plano(plano_id):
    from falae.services.plano_acao_service import PlanoAcaoService

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

        return redirect(url_for("denuncia.empresa_denuncia_detalhe", denuncia_id=denuncia_id))

    return render_template("empresa/plano_editar.html", plano=plano)


@denuncia_bp.route("/empresa/plano/<int:plano_id>/excluir", methods=["POST"])
@perfil_required("SUPER_ADMIN", "ADMIN_EMPRESA", "GESTOR", "INVESTIGADOR")
def empresa_excluir_plano(plano_id):
    from falae.services.plano_acao_service import PlanoAcaoService

    denuncia_id = PlanoAcaoService.excluir(plano_id)

    if not denuncia_id:
        return "Plano de ação não encontrado.", 404

    return redirect(url_for("denuncia.empresa_denuncia_detalhe", denuncia_id=denuncia_id))

@denuncia_bp.route("/empresa/denuncias/exportar")
@empresa_admin_required
def exportar_denuncias_excel():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.protocolo,
            u.nome AS unidade,
            COALESCE(s.nome, 'Não informado') AS setor,
            COALESCE(d.categoria, d.tipo) AS categoria,
            COALESCE(d.criticidade, 'Não informada') AS criticidade,
            d.status,
            d.etapa_atual,
            d.criado_em
        FROM denuncias d
        INNER JOIN unidades u ON d.unidade_id = u.id
        LEFT JOIN setores s ON d.setor_id = s.id
        WHERE d.empresa_id = %s
        ORDER BY d.criado_em DESC
    """, (session["empresa_id"],))

    denuncias = cursor.fetchall()

    cursor.close()
    conn.close()

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

    for d in denuncias:
        ws.append([
            d["protocolo"],
            d["unidade"],
            d["setor"],
            d["categoria"],
            d["criticidade"],
            d["status"],
            d["etapa_atual"],
            str(d["criado_em"])
        ])

    arquivo = BytesIO()
    wb.save(arquivo)
    arquivo.seek(0)

    return send_file(
        arquivo,
        as_attachment=True,
        download_name="denuncias.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@denuncia_bp.route("/empresa/denuncias/exportar-pdf")
@empresa_admin_required
def exportar_denuncias_pdf():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.protocolo,
            u.nome AS unidade,
            COALESCE(d.categoria, d.tipo) AS categoria,
            d.status,
            d.etapa_atual,
            d.criado_em
        FROM denuncias d
        INNER JOIN unidades u ON d.unidade_id = u.id
        WHERE d.empresa_id = %s
        ORDER BY d.criado_em DESC
        LIMIT 100
    """, (session["empresa_id"],))

    denuncias = cursor.fetchall()

    cursor.close()
    conn.close()

    arquivo = BytesIO()
    pdf = canvas.Canvas(arquivo, pagesize=A4)

    largura, altura = A4
    y = altura - 50

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Relatório de Denúncias")
    y -= 30

    pdf.setFont("Helvetica", 9)

    for d in denuncias:
        linha = (
            f"{d['protocolo']} | {d['unidade']} | {d['categoria']} | "
            f"{d['status']} | {d['etapa_atual']} | {d['criado_em']}"
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

@denuncia_bp.route("/empresa/plano/<int:plano_id>/concluir", methods=["POST"])
@perfil_required("SUPER_ADMIN", "ADMIN_EMPRESA", "GESTOR", "INVESTIGADOR")
def empresa_concluir_plano(plano_id):
    from falae.services.plano_acao_service import PlanoAcaoService

    denuncia_id = PlanoAcaoService.concluir(plano_id)

    if not denuncia_id:
        return "Plano de ação não encontrado.", 404

    return redirect(url_for("denuncia.empresa_denuncia_detalhe", denuncia_id=denuncia_id))