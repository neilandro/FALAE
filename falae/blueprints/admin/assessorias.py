from flask import render_template, request, redirect, url_for
from db import get_connection

from . import admin_bp
from falae.decorators import super_admin_required

@admin_bp.route("/assessorias")
@super_admin_required

def assessorias():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.id,
            a.nome,
            a.cnpj,
            a.responsavel,
            a.email,
            a.telefone,
            a.ativa,
            a.criado_em,
            COUNT(e.id) AS total_empresas
        FROM assessorias a
        LEFT JOIN empresas e ON e.assessoria_id = a.id
        GROUP BY
            a.id,
            a.nome,
            a.cnpj,
            a.responsavel,
            a.email,
            a.telefone,
            a.ativa,
            a.criado_em
        ORDER BY a.nome
    """)

    assessorias = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/assessorias.html", assessorias=assessorias)

@admin_bp.route("/assessorias/nova", methods=["GET", "POST"])
@super_admin_required
def assessoria_nova():
    if request.method == "POST":
        nome = request.form.get("nome")
        cnpj = request.form.get("cnpj")
        responsavel = request.form.get("responsavel")
        email = request.form.get("email")
        telefone = request.form.get("telefone")
        ativa = request.form.get("ativa", 1)

        endereco = request.form.get("endereco")
        numero = request.form.get("numero")
        complemento = request.form.get("complemento")
        bairro = request.form.get("bairro")
        cidade = request.form.get("cidade")
        estado = request.form.get("estado")
        cep = request.form.get("cep")

        contato_nome = request.form.get("contato_nome")
        contato_cargo = request.form.get("contato_cargo")
        contato_email = request.form.get("contato_email")
        contato_telefone = request.form.get("contato_telefone")
        contato_whatsapp = request.form.get("contato_whatsapp")

        site = request.form.get("site")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO assessorias (
                nome,
                cnpj,
                responsavel,
                email,
                telefone,
                ativa,
                endereco,
                numero,
                complemento,
                bairro,
                cidade,
                estado,
                cep,
                contato_nome,
                contato_cargo,
                contato_email,
                contato_telefone,
                contato_whatsapp,
                site
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            nome,
            cnpj,
            responsavel,
            email,
            telefone,
            ativa,
            endereco,
            numero,
            complemento,
            bairro,
            cidade,
            estado,
            cep,
            contato_nome,
            contato_cargo,
            contato_email,
            contato_telefone,
            contato_whatsapp,
            site
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("admin.assessorias"))

    return render_template(
        "admin/forms/assessoria_form.html",
        modo="novo",
        assessoria=None
    )

@admin_bp.route("/assessorias/<int:assessoria_id>/editar", methods=["GET", "POST"])
@super_admin_required
def assessoria_editar(assessoria_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM assessorias
        WHERE id = %s
        LIMIT 1
    """, (assessoria_id,))

    assessoria = cursor.fetchone()

    if not assessoria:
        cursor.close()
        conn.close()
        return "Assessoria não encontrada.", 404

    if request.method == "POST":

        cursor.execute("""
            UPDATE assessorias
            SET
                nome=%s,
                cnpj=%s,
                responsavel=%s,
                email=%s,
                telefone=%s,
                ativa=%s,
                endereco=%s,
                numero=%s,
                complemento=%s,
                bairro=%s,
                cidade=%s,
                estado=%s,
                cep=%s,
                contato_nome=%s,
                contato_cargo=%s,
                contato_email=%s,
                contato_telefone=%s,
                contato_whatsapp=%s,
                site=%s
            WHERE id=%s
        """, (

            request.form.get("nome"),
            request.form.get("cnpj"),
            request.form.get("responsavel"),
            request.form.get("email"),
            request.form.get("telefone"),
            request.form.get("ativa"),

            request.form.get("endereco"),
            request.form.get("numero"),
            request.form.get("complemento"),
            request.form.get("bairro"),
            request.form.get("cidade"),
            (request.form.get("estado") or "")[:2].upper(),
            request.form.get("cep"),

            request.form.get("contato_nome"),
            request.form.get("contato_cargo"),
            request.form.get("contato_email"),
            request.form.get("contato_telefone"),
            request.form.get("contato_whatsapp"),

            request.form.get("site"),

            assessoria_id

        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("admin.assessorias"))

    cursor.close()
    conn.close()

    return render_template(
        "admin/forms/assessoria_form.html",
        modo="editar",
        assessoria=assessoria
    )


@admin_bp.route("/assessorias/<int:assessoria_id>")
@super_admin_required
def assessoria_detalhe(assessoria_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            nome,
            cnpj,
            responsavel,
            email,
            telefone,
            ativa,
            criado_em
        FROM assessorias
        WHERE id = %s
        LIMIT 1
    """, (assessoria_id,))

    assessoria = cursor.fetchone()

    if not assessoria:
        cursor.close()
        conn.close()
        return "Assessoria não encontrada.", 404

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM empresas
        WHERE assessoria_id = %s
          AND ativa = 1
    """, (assessoria_id,))
    total_empresas = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM usuarios u
        INNER JOIN empresas e ON e.id = u.empresa_id
        WHERE e.assessoria_id = %s
          AND u.ativo = 1
    """, (assessoria_id,))
    total_usuarios = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM denuncias d
        INNER JOIN empresas e ON e.id = d.empresa_id
        WHERE e.assessoria_id = %s
    """, (assessoria_id,))
    total_denuncias = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM denuncias d
        INNER JOIN empresas e ON e.id = d.empresa_id
        WHERE e.assessoria_id = %s
          AND d.criticidade = 'Alta'
          AND d.status NOT IN ('CONCLUIDA', 'ARQUIVADA')
    """, (assessoria_id,))
    total_criticas = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT
            e.id,
            e.nome,
            e.cnpj,
            e.slug,
            e.plano,
            e.ativa,
            e.criado_em,
            COUNT(DISTINCT u.id) AS total_usuarios,
            COUNT(DISTINCT d.id) AS total_denuncias
        FROM empresas e
        LEFT JOIN usuarios u ON u.empresa_id = e.id
        LEFT JOIN denuncias d ON d.empresa_id = e.id
        WHERE e.assessoria_id = %s
        GROUP BY
            e.id,
            e.nome,
            e.cnpj,
            e.slug,
            e.plano,
            e.ativa,
            e.criado_em
        ORDER BY e.nome
    """, (assessoria_id,))

    empresas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin/assessoria_detalhe.html",
        assessoria=assessoria,
        empresas=empresas,
        total_empresas=total_empresas,
        total_usuarios=total_usuarios,
        total_denuncias=total_denuncias,
        total_criticas=total_criticas
    )