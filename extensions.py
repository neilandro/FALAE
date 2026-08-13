from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect


bcrypt = Bcrypt()
csrf = CSRFProtect()
mail = Mail()