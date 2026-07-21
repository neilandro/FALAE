from io import BytesIO

import qrcode

from flask import (
    Blueprint,
    render_template,
    send_file,
    url_for,
    request
)

from falae.services.empresa_personalizacao_service import (
    EmpresaPersonalizacaoService
)

portal_bp = Blueprint(
    "portal",
    __name__
)

@portal_bp.route("/c/<slug>")
def portal_empresa(slug):

    try:
        empresa = EmpresaPersonalizacaoService.obter_por_slug(slug)

    except ValueError as erro:
        return str(erro), 404

    return render_template(
        "public/portal_empresa.html",
        empresa=empresa
    )

@portal_bp.route("/c/<slug>/qrcode")
def portal_qrcode(slug):

    try:
        EmpresaPersonalizacaoService.obter_por_slug(slug)

    except ValueError as erro:
        return str(erro), 404

    url = request.url_root.rstrip("/") + url_for(
        "portal.portal_empresa",
        slug=slug
    )

    qr = qrcode.make(url)

    imagem = BytesIO()

    qr.save(
        imagem,
        format="PNG"
    )

    imagem.seek(0)

    return send_file(
        imagem,
        mimetype="image/png"
    )


