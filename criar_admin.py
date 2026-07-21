from db import get_connection
from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
bcrypt = Bcrypt(app)

nome = "Administrador"
email = "admin@empresa.com"
senha = "123456"
empresa_id = 1

senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO usuarios
    (empresa_id, nome, email, senha_hash, perfil)
    VALUES (%s, %s, %s, %s, %s)
""", (
    empresa_id,
    nome,
    email,
    senha_hash,
    "ADMIN"
))

conn.commit()

cursor.close()
conn.close()

print("Usuário administrador criado com sucesso.")