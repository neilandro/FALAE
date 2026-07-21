from functools import wraps
from flask import session, redirect, url_for, render_template


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "usuario_id" not in session:
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function


def perfil_required(*perfis):

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            if "usuario_id" not in session:
                return redirect(url_for("auth.login"))

            perfil_usuario = session.get("perfil")

            if perfil_usuario not in perfis:
                return render_template("errors/403.html"), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Compatibilidade com o código atual
super_admin_required = perfil_required("SUPER_ADMIN")

empresa_admin_required = perfil_required(
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "GESTOR"
)