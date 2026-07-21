# from falae.services.usuario_service import UsuarioService
# from falae.services.admin_dashboard_service import AdminDashboardService
# from flask import Blueprint, render_template, request, redirect, url_for
# from db import get_connection
# from extensions import bcrypt
# from falae.decorators import super_admin_required, perfil_required
# import uuid

# admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# @admin_bp.route("/dashboard")
# @super_admin_required
# def dashboard():
#     dados = AdminDashboardService.obter_dashboard()

#     return render_template(
#         "admin/dashboard.html",
#         **dados
#     )

# @admin_bp.route("/empresas")
# @super_admin_required
# def empresas():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("""
#         SELECT
#             e.id,
#             e.nome,
#             e.cnpj,
#             e.plano,
#             e.ativa,
#             e.cidade,
#             e.estado,

#             a.nome AS assessoria,

#             COUNT(DISTINCT u.id) AS total_usuarios,

#             COUNT(DISTINCT d.id) AS total_denuncias,

#             SUM(
#                 CASE
#                     WHEN d.criticidade = 'Alta'
#                     AND d.status NOT IN ('CONCLUIDA','ARQUIVADA')
#                     THEN 1
#                     ELSE 0
#                 END
#             ) AS total_criticas

#         FROM empresas e

#         LEFT JOIN assessorias a
#             ON a.id = e.assessoria_id

#         LEFT JOIN usuarios u
#             ON u.empresa_id = e.id
#             AND u.ativo = 1

#         LEFT JOIN denuncias d
#             ON d.empresa_id = e.id

#         GROUP BY

#             e.id,
#             e.nome,
#             e.cnpj,
#             e.plano,
#             e.ativa,
#             e.cidade,
#             e.estado,
#             a.nome

#         ORDER BY e.nome;
#     """)

#     empresas = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     return render_template("admin/empresas.html", empresas=empresas)
    #return "<h1 style='background:white;color:black;padding:30px'>ADMIN EMPRESAS OK</h1>"


# @admin_bp.route("/empresas/nova", methods=["GET", "POST"])
# @super_admin_required
# def empresa_nova():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("""
#         SELECT id, nome
#         FROM assessorias
#         WHERE ativa = 1
#         ORDER BY nome
#     """)
#     assessorias = cursor.fetchall()

#     if request.method == "POST":
#         nome = request.form.get("nome")
#         cnpj = request.form.get("cnpj")
#         plano = request.form.get("plano")
#         assessoria_id = request.form.get("assessoria_id") or None

#         endereco = request.form.get("endereco")
#         numero = request.form.get("numero")
#         complemento = request.form.get("complemento")
#         bairro = request.form.get("bairro")
#         cidade = request.form.get("cidade")
#         estado = request.form.get("estado")
#         cep = request.form.get("cep")

#         contato_nome = request.form.get("contato_nome")
#         contato_cargo = request.form.get("contato_cargo")
#         contato_email = request.form.get("contato_email")
#         contato_telefone = request.form.get("contato_telefone")
#         contato_whatsapp = request.form.get("contato_whatsapp")

#         slug = nome.lower().strip().replace(" ", "-")
#         token_publico = uuid.uuid4().hex

#         cursor.execute("""
#             INSERT INTO empresas (
#                 assessoria_id,
#                 nome,
#                 slug,
#                 cnpj,
#                 endereco,
#                 numero,
#                 complemento,
#                 bairro,
#                 cidade,
#                 estado,
#                 cep,
#                 contato_nome,
#                 contato_cargo,
#                 contato_email,
#                 contato_telefone,
#                 contato_whatsapp,
#                 plano,
#                 token_publico,
#                 ativa
#             )
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
#         """, (
#             assessoria_id,
#             nome,
#             slug,
#             cnpj,
#             endereco,
#             numero,
#             complemento,
#             bairro,
#             cidade,
#             estado,
#             cep,
#             contato_nome,
#             contato_cargo,
#             contato_email,
#             contato_telefone,
#             contato_whatsapp,
#             plano,
#             token_publico
#         ))

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return redirect(url_for("admin.empresas"))

#     cursor.close()
#     conn.close()

#     return render_template(
#         "admin/forms/empresa_form.html",
#         modo="novo",
#         empresa=None,
#         assessorias=assessorias
# )
    

# @admin_bp.route("/assessorias")
# @super_admin_required
# def assessorias():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("""
#         SELECT
#             a.id,
#             a.nome,
#             a.cnpj,
#             a.responsavel,
#             a.email,
#             a.telefone,
#             a.ativa,
#             a.criado_em,
#             COUNT(e.id) AS total_empresas
#         FROM assessorias a
#         LEFT JOIN empresas e ON e.assessoria_id = a.id
#         GROUP BY
#             a.id,
#             a.nome,
#             a.cnpj,
#             a.responsavel,
#             a.email,
#             a.telefone,
#             a.ativa,
#             a.criado_em
#         ORDER BY a.nome
#     """)

#     assessorias = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     return render_template("admin/assessorias.html", assessorias=assessorias)

# @admin_bp.route("/assessorias/nova", methods=["GET", "POST"])
# @super_admin_required
# def assessoria_nova():
#     if request.method == "POST":
#         nome = request.form.get("nome")
#         cnpj = request.form.get("cnpj")
#         responsavel = request.form.get("responsavel")
#         email = request.form.get("email")
#         telefone = request.form.get("telefone")
#         ativa = request.form.get("ativa", 1)

#         endereco = request.form.get("endereco")
#         numero = request.form.get("numero")
#         complemento = request.form.get("complemento")
#         bairro = request.form.get("bairro")
#         cidade = request.form.get("cidade")
#         estado = request.form.get("estado")
#         cep = request.form.get("cep")

#         contato_nome = request.form.get("contato_nome")
#         contato_cargo = request.form.get("contato_cargo")
#         contato_email = request.form.get("contato_email")
#         contato_telefone = request.form.get("contato_telefone")
#         contato_whatsapp = request.form.get("contato_whatsapp")

#         site = request.form.get("site")

#         conn = get_connection()
#         cursor = conn.cursor()

#         cursor.execute("""
#             INSERT INTO assessorias (
#                 nome,
#                 cnpj,
#                 responsavel,
#                 email,
#                 telefone,
#                 ativa,
#                 endereco,
#                 numero,
#                 complemento,
#                 bairro,
#                 cidade,
#                 estado,
#                 cep,
#                 contato_nome,
#                 contato_cargo,
#                 contato_email,
#                 contato_telefone,
#                 contato_whatsapp,
#                 site
#             )
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """, (
#             nome,
#             cnpj,
#             responsavel,
#             email,
#             telefone,
#             ativa,
#             endereco,
#             numero,
#             complemento,
#             bairro,
#             cidade,
#             estado,
#             cep,
#             contato_nome,
#             contato_cargo,
#             contato_email,
#             contato_telefone,
#             contato_whatsapp,
#             site
#         ))

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return redirect(url_for("admin.assessorias"))

#     return render_template(
#         "admin/forms/assessoria_form.html",
#         modo="novo",
#         assessoria=None
#     )

# @admin_bp.route("/assessorias/<int:assessoria_id>/editar", methods=["GET", "POST"])
# @super_admin_required
# def assessoria_editar(assessoria_id):

#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("""
#         SELECT *
#         FROM assessorias
#         WHERE id = %s
#         LIMIT 1
#     """, (assessoria_id,))

#     assessoria = cursor.fetchone()

#     if not assessoria:
#         cursor.close()
#         conn.close()
#         return "Assessoria não encontrada.", 404

#     if request.method == "POST":

#         cursor.execute("""
#             UPDATE assessorias
#             SET
#                 nome=%s,
#                 cnpj=%s,
#                 responsavel=%s,
#                 email=%s,
#                 telefone=%s,
#                 ativa=%s,
#                 endereco=%s,
#                 numero=%s,
#                 complemento=%s,
#                 bairro=%s,
#                 cidade=%s,
#                 estado=%s,
#                 cep=%s,
#                 contato_nome=%s,
#                 contato_cargo=%s,
#                 contato_email=%s,
#                 contato_telefone=%s,
#                 contato_whatsapp=%s,
#                 site=%s
#             WHERE id=%s
#         """, (

#             request.form.get("nome"),
#             request.form.get("cnpj"),
#             request.form.get("responsavel"),
#             request.form.get("email"),
#             request.form.get("telefone"),
#             request.form.get("ativa"),

#             request.form.get("endereco"),
#             request.form.get("numero"),
#             request.form.get("complemento"),
#             request.form.get("bairro"),
#             request.form.get("cidade"),
#             (request.form.get("estado") or "")[:2].upper(),
#             request.form.get("cep"),

#             request.form.get("contato_nome"),
#             request.form.get("contato_cargo"),
#             request.form.get("contato_email"),
#             request.form.get("contato_telefone"),
#             request.form.get("contato_whatsapp"),

#             request.form.get("site"),

#             assessoria_id

#         ))

#         conn.commit()

#         cursor.close()
#         conn.close()

#         return redirect(url_for("admin.assessorias"))

#     cursor.close()
#     conn.close()

#     return render_template(
#         "admin/forms/assessoria_form.html",
#         modo="editar",
#         assessoria=assessoria
#     )

# @admin_bp.route("/usuarios")
# @perfil_required("SUPER_ADMIN", "ADM_ASSESSORIA", "ADMIN_EMPRESA")
# def usuarios():
#     usuarios = UsuarioService.listar_usuarios()

#     return render_template(
#         "admin/usuarios.html",
#         usuarios=usuarios
#     )

# @admin_bp.route("/usuarios/novo", methods=["GET", "POST"])
# @super_admin_required
# def usuario_novo():
#     dados_formulario = UsuarioService.preparar_formulario_usuario()
#     empresa_id_preselecionada = request.args.get("empresa_id")

#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("""
#         SELECT id, nome
#         FROM empresas
#         WHERE ativa = 1
#         ORDER BY nome
#     """)
#     empresas = cursor.fetchall()

#     if request.method == "POST":
#         nome = request.form.get("nome")
#         email = request.form.get("email")
#         senha = request.form.get("senha")
#         perfil = request.form.get("perfil")
#         empresa_id = request.form.get("empresa_id") or None
#         assessoria_id = request.form.get("assessoria_id") or None
#         ativo = request.form.get("ativo", 1)

#         senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")

#         cursor.execute("""
#             INSERT INTO usuarios (
#                 empresa_id,
#                 assessoria_id,
#                 nome,
#                 email,
#                 senha_hash,
#                 perfil,
#                 ativo
#             )
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#         """, (
#             empresa_id,
#             assessoria_id,
#             nome,
#             email,
#             senha_hash,
#             perfil,
#             ativo
#         ))

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return redirect(url_for("admin.usuarios"))

#     cursor.close()
#     conn.close()

#     return render_template(
#         "admin/forms/usuario_form.html",
#         modo="novo",
#         usuario=None,
#         empresa_id_preselecionada=empresa_id_preselecionada,
#         **dados_formulario
#     )

# @admin_bp.route("/usuarios/<int:usuario_id>/editar", methods=["GET", "POST"])
# @perfil_required("SUPER_ADMIN", "ADM_ASSESSORIA", "ADMIN_EMPRESA")
# def usuario_editar(usuario_id):

#     dados_formulario = UsuarioService.preparar_formulario_usuario()

#     usuario = UsuarioService.obter_usuario(usuario_id)

#     if not usuario:
#         return "Usuário não encontrado.", 404
    
#     if not UsuarioService.pode_acessar_usuario(usuario):
#         return "Acesso não autorizado.", 403

#     if request.method == "POST":

#         resultado = UsuarioService.editar_usuario(
#             usuario_id,
#             request.form
#         )

#         if not resultado["sucesso"]:
#             return resultado["mensagem"], 403

#         return redirect(url_for("admin.usuarios"))

#     return render_template(
#         "admin/forms/usuario_form.html",
#         modo="editar",
#         usuario=usuario,
#         empresa_id_preselecionada=None,
#         **dados_formulario
#     )

# @admin_bp.route("/usuarios/<int:usuario_id>/resetar-senha", methods=["POST"])
# @super_admin_required
# def resetar_senha_usuario(usuario_id):
#     resultado = UsuarioService.resetar_senha(usuario_id)

#     if not resultado.get("sucesso"):
#         return resultado.get("mensagem"), 404

#     return render_template(
#         "admin/senha_resetada.html",
#         usuario=resultado["usuario"],
#         senha_temporaria=resultado["senha_temporaria"]
#     )

# @admin_bp.route("/assessorias/<int:assessoria_id>")
# @super_admin_required
# def assessoria_detalhe(assessoria_id):
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("""
#         SELECT
#             id,
#             nome,
#             cnpj,
#             responsavel,
#             email,
#             telefone,
#             ativa,
#             criado_em
#         FROM assessorias
#         WHERE id = %s
#         LIMIT 1
#     """, (assessoria_id,))

#     assessoria = cursor.fetchone()

#     if not assessoria:
#         cursor.close()
#         conn.close()
#         return "Assessoria não encontrada.", 404

#     cursor.execute("""
#         SELECT COUNT(*) AS total
#         FROM empresas
#         WHERE assessoria_id = %s
#           AND ativa = 1
#     """, (assessoria_id,))
#     total_empresas = cursor.fetchone()["total"]

#     cursor.execute("""
#         SELECT COUNT(*) AS total
#         FROM usuarios u
#         INNER JOIN empresas e ON e.id = u.empresa_id
#         WHERE e.assessoria_id = %s
#           AND u.ativo = 1
#     """, (assessoria_id,))
#     total_usuarios = cursor.fetchone()["total"]

#     cursor.execute("""
#         SELECT COUNT(*) AS total
#         FROM denuncias d
#         INNER JOIN empresas e ON e.id = d.empresa_id
#         WHERE e.assessoria_id = %s
#     """, (assessoria_id,))
#     total_denuncias = cursor.fetchone()["total"]

#     cursor.execute("""
#         SELECT COUNT(*) AS total
#         FROM denuncias d
#         INNER JOIN empresas e ON e.id = d.empresa_id
#         WHERE e.assessoria_id = %s
#           AND d.criticidade = 'Alta'
#           AND d.status NOT IN ('CONCLUIDA', 'ARQUIVADA')
#     """, (assessoria_id,))
#     total_criticas = cursor.fetchone()["total"]

#     cursor.execute("""
#         SELECT
#             e.id,
#             e.nome,
#             e.cnpj,
#             e.slug,
#             e.plano,
#             e.ativa,
#             e.criado_em,
#             COUNT(DISTINCT u.id) AS total_usuarios,
#             COUNT(DISTINCT d.id) AS total_denuncias
#         FROM empresas e
#         LEFT JOIN usuarios u ON u.empresa_id = e.id
#         LEFT JOIN denuncias d ON d.empresa_id = e.id
#         WHERE e.assessoria_id = %s
#         GROUP BY
#             e.id,
#             e.nome,
#             e.cnpj,
#             e.slug,
#             e.plano,
#             e.ativa,
#             e.criado_em
#         ORDER BY e.nome
#     """, (assessoria_id,))

#     empresas = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     return render_template(
#         "admin/assessoria_detalhe.html",
#         assessoria=assessoria,
#         empresas=empresas,
#         total_empresas=total_empresas,
#         total_usuarios=total_usuarios,
#         total_denuncias=total_denuncias,
#         total_criticas=total_criticas
#     )

# @admin_bp.route("/empresas/<int:empresa_id>")
# @super_admin_required
# def empresa_detalhe(empresa_id):
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("""
#         SELECT
#             e.*,
#             a.nome AS assessoria
#         FROM empresas e
#         LEFT JOIN assessorias a ON a.id = e.assessoria_id
#         WHERE e.id = %s
#         LIMIT 1
#     """, (empresa_id,))

#     empresa = cursor.fetchone()

#     if not empresa:
#         cursor.close()
#         conn.close()
#         return "Empresa não encontrada.", 404

#     cursor.execute("""
#         SELECT COUNT(*) AS total
#         FROM usuarios
#         WHERE empresa_id = %s
#           AND ativo = 1
#           AND perfil <> 'SUPER_ADMIN'
#     """, (empresa_id,))
#     total_usuarios = cursor.fetchone()["total"]

#     cursor.execute("""
#         SELECT COUNT(*) AS total
#         FROM unidades
#         WHERE empresa_id = %s
#           AND ativa = 1
#     """, (empresa_id,))
#     total_unidades = cursor.fetchone()["total"]

#     cursor.execute("""
#         SELECT COUNT(*) AS total
#         FROM setores
#         WHERE empresa_id = %s
#           AND ativo = 1
#     """, (empresa_id,))
#     total_setores = cursor.fetchone()["total"]

#     cursor.execute("""
#         SELECT COUNT(*) AS total
#         FROM denuncias
#         WHERE empresa_id = %s
#     """, (empresa_id,))
#     total_denuncias = cursor.fetchone()["total"]

#     cursor.close()
#     conn.close()

#     return render_template(
#         "admin/empresa_detalhe.html",
#         empresa=empresa,
#         total_usuarios=total_usuarios,
#         total_unidades=total_unidades,
#         total_setores=total_setores,
#         total_denuncias=total_denuncias
#     )


# @admin_bp.route("/empresas/<int:empresa_id>/editar", methods=["GET", "POST"])
# @super_admin_required
# def empresa_editar(empresa_id):
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("""
#         SELECT id, nome
#         FROM assessorias
#         WHERE ativa = 1
#         ORDER BY nome
#     """)
#     assessorias = cursor.fetchall()

#     cursor.execute("""
#         SELECT *
#         FROM empresas
#         WHERE id = %s
#         LIMIT 1
#     """, (empresa_id,))

#     empresa = cursor.fetchone()

#     if not empresa:
#         cursor.close()
#         conn.close()
#         return "Empresa não encontrada.", 404

#     if request.method == "POST":
#         nome = request.form.get("nome")
#         cnpj = request.form.get("cnpj")
#         plano = request.form.get("plano")
#         assessoria_id = request.form.get("assessoria_id") or None
#         ativa = request.form.get("ativa", 1)

#         slug = nome.lower().strip().replace(" ", "-")

#         cursor.execute("""
#             UPDATE empresas
#             SET
#                 assessoria_id=%s,
#                 nome=%s,
#                 slug=%s,
#                 cnpj=%s,
#                 plano=%s,
#                 ativa=%s
#             WHERE id=%s
#         """, (
#             assessoria_id,
#             nome,
#             slug,
#             cnpj,
#             plano,
#             ativa,
#             empresa_id
#         ))

#         conn.commit()

#         cursor.close()
#         conn.close()

#         return redirect(url_for("admin.empresas"))

#     cursor.close()
#     conn.close()

#     return render_template(
#         "admin/forms/empresa_form.html",
#         modo="editar",
#         empresa=empresa,
#         assessorias=assessorias
# )