from flask import Blueprint, render_template

from falae.decorators import perfil_required
from falae.services.investigador_service import InvestigadorService


investigador_bp = Blueprint(
    "investigador",
    __name__
)


@investigador_bp.route("/empresa/minha-agenda")
@perfil_required("SUPER_ADMIN", "ADMIN_EMPRESA", "GESTOR", "INVESTIGADOR")
def minha_agenda():

    dados = InvestigadorService.obter_agenda()

    return render_template(
        "empresa/agenda_investigador.html",
        **dados
    )