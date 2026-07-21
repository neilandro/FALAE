from db import get_connection
from flask import Flask
from flask_bcrypt import Bcrypt

print("Iniciando criação do Super Admin...")

app = Flask(__name__)
bcrypt = Bcrypt(app)

try:
    conn = get_connection()
    print("Conectou no banco.")

    cursor = conn.cursor(dictionary=True)

    senha_hash = bcrypt.generate_password_hash("123456").decode("utf-8")

    cursor.execute("""
        SELECT id FROM empresas 
        WHERE token_publico = %s
    """, ("falae-admin",))

    empresa = cursor.fetchone()

    if empresa:
        empresa_id = empresa["id"]
        print("Empresa Falae SaaS já existe.")
    else:
        cursor.execute("""
            INSERT INTO empresas 
            (nome, cnpj, token_publico, ativa, plano)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            "Falae SaaS",
            "00.000.000/0001-00",
            "falae-admin",
            1,
            "ENTERPRISE"
        ))

        conn.commit()
        empresa_id = cursor.lastrowid
        print("Empresa Falae SaaS criada.")

    cursor.execute("""
        SELECT id FROM usuarios
        WHERE email = %s
    """, ("admin@falae.com.br",))

    usuario = cursor.fetchone()

    if usuario:
        cursor.execute("""
            UPDATE usuarios
            SET nome = %s,
                senha_hash = %s,
                perfil = %s,
                empresa_id = %s,
                ativo = %s
            WHERE email = %s
        """, (
            "Super Administrador",
            senha_hash,
            "SUPER_ADMIN",
            empresa_id,
            1,
            "admin@falae.com.br"
        ))

        print("Usuário Super Admin atualizado.")
    else:
        cursor.execute("""
            INSERT INTO usuarios
            (empresa_id, nome, email, senha_hash, perfil, ativo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            empresa_id,
            "Super Administrador",
            "admin@falae.com.br",
            senha_hash,
            "SUPER_ADMIN",
            1
        ))

        print("Usuário Super Admin criado.")

    conn.commit()

    cursor.close()
    conn.close()

    print("Processo finalizado com sucesso.")
    print("Login: admin@falae.com.br")
    print("Senha: 123456")

except Exception as e:
    print("Erro ao criar Super Admin:")
    print(type(e))
    print(e)