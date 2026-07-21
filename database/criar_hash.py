from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

print(
    bcrypt.generate_password_hash("Admin@123").decode("utf-8")
)