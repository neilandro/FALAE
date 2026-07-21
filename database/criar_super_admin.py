from extensions import bcrypt
from db import get_connection

assessoria_id = 1  # ajuste para o ID da assessoria criada
nome = "Administrador Solução Med"
email = "admin@solucaomed.com.br"
senha = "Admin@123"
perfil = "ADM_ASSESSORIA"

senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO usuarios (
        empresa_id,
        nome,
        email,
        senha_hash,
        perfil,
        ativo
    )
    VALUES (%s, %s, %s, %s, %s, %s)
""", (
    None,
    nome,
    email,
    senha_hash,
    perfil,
    1
))

conn.commit()
cursor.close()
conn.close()

print("ADM_ASSESSORIA criado com sucesso!")