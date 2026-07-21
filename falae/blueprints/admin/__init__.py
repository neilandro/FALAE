from flask import Blueprint

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

from . import dashboard
from . import empresas
from . import assessorias
from . import usuarios