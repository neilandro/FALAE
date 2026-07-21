from flask import render_template, request, redirect, url_for
from db import get_connection
import uuid

from . import admin_bp
from falae.decorators import super_admin_required


@admin_bp.route("/empresas")
@super_admin_required
def empresas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            e.id,
            e.nome,
            e.cnpj,
            e.plano,
            e.ativa,
            e.cidade,
            e.estado,

            a.nome AS assessoria,

            COUNT(DISTINCT u.id) AS total_usuarios,

            COUNT(DISTINCT d.id) AS total_denuncias,

            SUM(
                CASE
                    WHEN d.criticidade = 'Alta'
                    AND d.status NOT IN ('CONCLUIDA','ARQUIVADA')
                    THEN 1
                    ELSE 0
                END
            ) AS total_criticas

        FROM empresas e

        LEFT JOIN assessorias a
            ON a.id = e.assessoria_id

        LEFT JOIN usuarios u
            ON u.empresa_id = e.id
            AND u.ativo = 1

        LEFT JOIN denuncias d
            ON d.empresa_id = e.id

        GROUP BY

            e.id,
            e.nome,
            e.cnpj,
            e.plano,
            e.ativa,
            e.cidade,
            e.estado,
            a.nome

        ORDER BY e.nome;
    """)

    empresas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin/empresas.html", empresas=empresas)
    #return "<h1 style='background:white;color:black;padding:30px'>ADMIN EMPRESAS OK</h1>"

@admin_bp.route("/empresas/nova", methods=["GET", "POST"])
@super_admin_required
def empresa_nova():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nome
        FROM assessorias
        WHERE ativa = 1
        ORDER BY nome
    """)
    assessorias = cursor.fetchall()

    if request.method == "POST":
        nome = request.form.get("nome")
        cnpj = request.form.get("cnpj")
        plano = request.form.get("plano")
        assessoria_id = request.form.get("assessoria_id") or None

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

        slug = nome.lower().strip().replace(" ", "-")
        token_publico = uuid.uuid4().hex

        cursor.execute("""
            INSERT INTO empresas (
                assessoria_id,
                nome,
                slug,
                cnpj,
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
                plano,
                token_publico,
                ativa
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        """, (
            assessoria_id,
            nome,
            slug,
            cnpj,
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
            plano,
            token_publico
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("admin.empresas"))

    cursor.close()
    conn.close()

    return render_template(
        "admin/forms/empresa_form.html",
        modo="novo",
        empresa=None,
        assessorias=assessorias
)

@admin_bp.route("/empresas/<int:empresa_id>/editar", methods=["GET", "POST"])
@super_admin_required
def empresa_editar(empresa_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nome
        FROM assessorias
        WHERE ativa = 1
        ORDER BY nome
    """)
    assessorias = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM empresas
        WHERE id = %s
        LIMIT 1
    """, (empresa_id,))

    empresa = cursor.fetchone()

    if not empresa:
        cursor.close()
        conn.close()
        return "Empresa não encontrada.", 404

    if request.method == "POST":
        nome = request.form.get("nome")
        cnpj = request.form.get("cnpj")
        plano = request.form.get("plano")
        assessoria_id = request.form.get("assessoria_id") or None
        ativa = request.form.get("ativa", 1)

        slug = nome.lower().strip().replace(" ", "-")

        cursor.execute("""
            UPDATE empresas
            SET
                assessoria_id=%s,
                nome=%s,
                slug=%s,
                cnpj=%s,
                plano=%s,
                ativa=%s
            WHERE id=%s
        """, (
            assessoria_id,
            nome,
            slug,
            cnpj,
            plano,
            ativa,
            empresa_id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("admin.empresas"))

    cursor.close()
    conn.close()

    return render_template(
        "admin/forms/empresa_form.html",
        modo="editar",
        empresa=empresa,
        assessorias=assessorias
)

@admin_bp.route("/empresas/<int:empresa_id>")
@super_admin_required
def empresa_detalhe(empresa_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            e.*,
            a.nome AS assessoria
        FROM empresas e
        LEFT JOIN assessorias a ON a.id = e.assessoria_id
        WHERE e.id = %s
        LIMIT 1
    """, (empresa_id,))

    empresa = cursor.fetchone()

    if not empresa:
        cursor.close()
        conn.close()
        return "Empresa não encontrada.", 404

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM usuarios
        WHERE empresa_id = %s
          AND ativo = 1
          AND perfil <> 'SUPER_ADMIN'
    """, (empresa_id,))
    total_usuarios = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM unidades
        WHERE empresa_id = %s
          AND ativa = 1
    """, (empresa_id,))
    total_unidades = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM setores
        WHERE empresa_id = %s
          AND ativo = 1
    """, (empresa_id,))
    total_setores = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM denuncias
        WHERE empresa_id = %s
    """, (empresa_id,))
    total_denuncias = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return render_template(
        "admin/empresa_detalhe.html",
        empresa=empresa,
        total_usuarios=total_usuarios,
        total_unidades=total_unidades,
        total_setores=total_setores,
        total_denuncias=total_denuncias
    )

