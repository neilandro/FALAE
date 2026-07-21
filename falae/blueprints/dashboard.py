from flask import Blueprint, render_template, request, session

from db import get_connection
from falae.decorators import empresa_admin_required
from falae.services.dashboard_service import DashboardService
from falae.decorators import perfil_required
from falae.services.context_service import ContextService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/empresa/dashboard")
@perfil_required(
    "SUPER_ADMIN",
    "ADM_ASSESSORIA",
    "ADMIN_EMPRESA"
)
def empresa_dashboard():
    empresa_id = ContextService.empresa()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")
    unidade_id = request.args.get("unidade_id")
    turno_id = request.args.get("turno_id")
    status = request.args.get("status")

    filtros = ["d.empresa_id = %s"]
    params = [empresa_id]

    if data_inicio:
        filtros.append("DATE(d.criado_em) >= %s")
        params.append(data_inicio)

    if data_fim:
        filtros.append("DATE(d.criado_em) <= %s")
        params.append(data_fim)

    if unidade_id:
        filtros.append("d.unidade_id = %s")
        params.append(unidade_id)

    if turno_id:
        filtros.append("d.turno_id = %s")
        params.append(turno_id)


    if status:
        filtros.append("d.status = %s")
        params.append(status)

    where_sql = " AND ".join(filtros)

    cursor.execute(f"SELECT COUNT(*) AS total FROM denuncias d WHERE {where_sql}", params)
    total = cursor.fetchone()["total"]

    cursor.execute(f"SELECT COUNT(*) AS total FROM denuncias d WHERE {where_sql} AND d.status = 'NOVA'", params)
    novas = cursor.fetchone()["total"]

    cursor.execute(f"SELECT COUNT(*) AS total FROM denuncias d WHERE {where_sql} AND d.status = 'EM_ANALISE'", params)
    em_analise = cursor.fetchone()["total"]

    cursor.execute(f"""
        SELECT COUNT(*) AS total
        FROM denuncias d
        WHERE {where_sql} AND d.status IN ('CONCLUIDA', 'ARQUIVADA')
    """, params)
    encerradas = cursor.fetchone()["total"]

    cursor.execute(f"""
        SELECT d.categoria, COUNT(*) AS total
        FROM denuncias d
        WHERE {where_sql}
        GROUP BY d.categoria
        ORDER BY total DESC
    """, params)
    por_categoria = cursor.fetchall()

    cursor.execute(f"""
        SELECT d.criticidade, COUNT(*) AS total
        FROM denuncias d
        WHERE {where_sql}
        GROUP BY d.criticidade
        ORDER BY total DESC
    """, params)
    por_criticidade = cursor.fetchall()

    cursor.execute(f"""
        SELECT u.nome AS unidade, COUNT(d.id) AS total
        FROM denuncias d
        INNER JOIN unidades u ON d.unidade_id = u.id
        WHERE {where_sql}
        GROUP BY u.nome
        ORDER BY total DESC
    """, params)
    por_unidade = cursor.fetchall()

    cursor.execute(f"""
        SELECT COALESCE(s.nome, 'Não informado') AS setor, COUNT(d.id) AS total
        FROM denuncias d
        LEFT JOIN setores s ON d.setor_id = s.id
        WHERE {where_sql}
        GROUP BY setor
        ORDER BY total DESC
    """, params)
    por_setor = cursor.fetchall()

    cursor.execute(f"""
        SELECT
            COALESCE(t.nome, 'Não informado') AS turno,
            COUNT(d.id) AS total
        FROM denuncias d
        LEFT JOIN turnos t
            ON t.id = d.turno_id
        AND t.empresa_id = d.empresa_id
        WHERE {where_sql}
        GROUP BY t.id, t.nome
        ORDER BY total DESC
    """, params)
    por_turno = cursor.fetchall()

    cursor.execute("""
        SELECT id, nome
        FROM unidades
        WHERE empresa_id = %s AND ativa = 1
        ORDER BY nome
    """, (session["empresa_id"],))
    unidades = cursor.fetchall()


    cursor.execute("""
        SELECT id, nome
        FROM turnos
        WHERE empresa_id = %s
        ORDER BY nome
    """, (session["empresa_id"],))
    turnos = cursor.fetchall()


    cursor.close()
    conn.close()

    return render_template(
        "empresa/dashboard.html",
        total=total,
        novas=novas,
        em_analise=em_analise,
        encerradas=encerradas,
        por_categoria=por_categoria,
        por_criticidade=por_criticidade,
        por_unidade=por_unidade,
        por_setor=por_setor,
        por_turno=por_turno,
        unidades=unidades,
        turnos=turnos,
        filtros={
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "unidade_id": unidade_id,
            "turno_id": turno_id,
            "status": status
        }
    )

@dashboard_bp.route("/empresa/centro-controle")
@perfil_required("SUPER_ADMIN", "ADM_ASSESSORIA", "ADMIN_EMPRESA", "GESTOR")
def centro_controle():
    dados = DashboardService.obter_centro_controle()

    return render_template(
        "empresa/centro_controle.html",
        **dados
    )


@dashboard_bp.route("/empresa/painel-operacional")
@empresa_admin_required
def painel_operacional():
    dados = DashboardService.obter_painel_operacional()

    return render_template(
        "empresa/painel_operacional.html",
        **dados
    )