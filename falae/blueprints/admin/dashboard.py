from flask import render_template

from . import admin_bp

from falae.decorators import super_admin_required
from falae.services.admin_dashboard_service import AdminDashboardService


@admin_bp.route("/dashboard")
@super_admin_required
def dashboard():
    dados = AdminDashboardService.obter_dashboard()

    return render_template(
        "admin/dashboard.html",
        **dados
    )