from flask import (
    Blueprint,
    render_template,
    session,
)

from db import get_connection
from falae.decorators import login_required


main_bp = Blueprint(
    "main",
    __name__,
)


@main_bp.route("/painel")
@login_required
def painel():
    conn = get_connection()
    cursor = conn.cursor(
        dictionary=True
    )

    try:
        if session.get("perfil") == "SUPER_ADMIN":
            cursor.execute(
                """
                SELECT
                    d.id,
                    d.protocolo,
                    d.tipo,
                    d.categoria,
                    d.criticidade,
                    d.descricao,
                    d.status,
                    d.criado_em,
                    e.nome AS empresa,
                    u.nome AS unidade,
                    s.nome AS setor
                FROM denuncias d

                INNER JOIN empresas e
                    ON d.empresa_id = e.id

                INNER JOIN unidades u
                    ON d.unidade_id = u.id

                LEFT JOIN setores s
                    ON d.setor_id = s.id

                ORDER BY d.criado_em DESC
                """
            )

        else:
            cursor.execute(
                """
                SELECT
                    d.id,
                    d.protocolo,
                    d.tipo,
                    d.categoria,
                    d.criticidade,
                    d.descricao,
                    d.status,
                    d.criado_em,
                    e.nome AS empresa,
                    u.nome AS unidade,
                    s.nome AS setor
                FROM denuncias d

                INNER JOIN empresas e
                    ON d.empresa_id = e.id

                INNER JOIN unidades u
                    ON d.unidade_id = u.id

                LEFT JOIN setores s
                    ON d.setor_id = s.id

                WHERE d.empresa_id = %s

                ORDER BY d.criado_em DESC
                """,
                (
                    session["empresa_id"],
                ),
            )

        denuncias = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "public/painel.html",
        denuncias=denuncias,
    )


@main_bp.route("/debug-sessao")
def debug_sessao():
    return {
        "usuario_id": session.get(
            "usuario_id"
        ),
        "empresa_id": session.get(
            "empresa_id"
        ),
        "nome": session.get(
            "nome"
        ),
        "perfil": session.get(
            "perfil"
        ),
    }