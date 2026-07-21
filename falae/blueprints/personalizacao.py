from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    send_file,
    url_for
)

from falae.decorators import perfil_required
from falae.services.empresa_personalizacao_service import (
    EmpresaPersonalizacaoService
)
from falae.services.qrcode_service import QRCodeService


personalizacao_bp = Blueprint(
    "personalizacao",
    __name__
)


personalizacao_required = perfil_required(
    "SUPER_ADMIN",
    "ADM_ASSESSORIA",
    "ADMIN_EMPRESA"
)


@personalizacao_bp.route(
    "/empresa/personalizacao",
    methods=["GET", "POST"]
)
@personalizacao_required
def empresa_personalizacao():
    erro = request.args.get(
        "erro"
    )

    sucesso = None

    if request.args.get(
        "atualizado"
    ) == "1":
        sucesso = (
            "Personalização atualizada com sucesso."
        )

    elif request.args.get(
        "slug_atualizado"
    ) == "1":
        sucesso = (
            "Endereço público atualizado com sucesso."
        )

    elif request.args.get(
        "slug_gerado"
    ) == "1":
        sucesso = (
            "Endereço público gerado com sucesso."
        )

    elif request.args.get(
        "logo_removido"
    ) == "1":
        sucesso = (
            "Logotipo removido com sucesso."
        )

    elif request.args.get(
        "favicon_removido"
    ) == "1":
        sucesso = (
            "Favicon removido com sucesso."
        )

    try:
        personalizacao = (
            EmpresaPersonalizacaoService
            .obter()
        )

    except ValueError as exc:
        return render_template(
            "empresa/personalizacao.html",
            personalizacao=None,
            erro=str(exc),
            sucesso=None
        )

    if request.method == "POST":
        try:
            logo = request.files.get(
                "logo"
            )

            favicon = request.files.get(
                "favicon"
            )

            EmpresaPersonalizacaoService.atualizar(
                nome_canal=request.form.get(
                    "nome_canal"
                ),
                cor_primaria=request.form.get(
                    "cor_primaria"
                ),
                cor_secundaria=request.form.get(
                    "cor_secundaria"
                ),
                mensagem_boas_vindas=request.form.get(
                    "mensagem_boas_vindas"
                ),
                texto_lgpd=request.form.get(
                    "texto_lgpd"
                ),
                termo_uso=request.form.get(
                    "termo_uso"
                ),
                mostrar_logo=request.form.get(
                    "mostrar_logo"
                ),
                mostrar_nome_empresa=request.form.get(
                    "mostrar_nome_empresa"
                ),
                logo=logo,
                favicon=favicon
            )

            return redirect(
                url_for(
                    "personalizacao.empresa_personalizacao",
                    atualizado=1
                )
            )

        except ValueError as exc:
            erro = str(exc)

            try:
                personalizacao = (
                    EmpresaPersonalizacaoService
                    .obter()
                )

            except ValueError:
                personalizacao = None

        except Exception:
            erro = (
                "Não foi possível atualizar a "
                "personalização da empresa."
            )

            try:
                personalizacao = (
                    EmpresaPersonalizacaoService
                    .obter()
                )

            except ValueError:
                personalizacao = None

    return render_template(
        "empresa/personalizacao.html",
        personalizacao=personalizacao,
        erro=erro,
        sucesso=sucesso
    )


@personalizacao_bp.route(
    "/empresa/personalizacao/slug",
    methods=["POST"]
)
@personalizacao_required
def atualizar_slug():
    try:
        EmpresaPersonalizacaoService.atualizar_slug(
            request.form.get(
                "slug"
            )
        )

        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                slug_atualizado=1
            )
        )

    except ValueError as exc:
        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                erro=str(exc)
            )
        )

    except Exception:
        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                erro=(
                    "Não foi possível atualizar "
                    "o endereço público."
                )
            )
        )


@personalizacao_bp.route(
    "/empresa/personalizacao/slug/gerar",
    methods=["POST"]
)
@personalizacao_required
def gerar_slug():
    try:
        (
            EmpresaPersonalizacaoService
            .gerar_slug_automatico()
        )

        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                slug_gerado=1
            )
        )

    except ValueError as exc:
        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                erro=str(exc)
            )
        )

    except Exception:
        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                erro=(
                    "Não foi possível gerar "
                    "o endereço público."
                )
            )
        )


@personalizacao_bp.route(
    "/empresa/personalizacao/qrcode",
    methods=["GET"]
)
@personalizacao_required
def baixar_qrcode():
    try:
        personalizacao = (
            EmpresaPersonalizacaoService
            .obter()
        )

        slug = personalizacao.get(
            "empresa_slug"
        )

        if not slug:
            raise ValueError(
                "Defina o endereço público antes "
                "de gerar o QR Code."
            )

        link_publico = url_for(
            "public.canal_publico",
            slug=slug,
            _external=True
        )

        dados_qrcode = (
            QRCodeService.gerar_dados(
                link=link_publico,
                slug=slug,
                cor_primaria=(
                    personalizacao.get(
                        "cor_primaria"
                    )
                )
            )
        )

        return send_file(
            dados_qrcode["arquivo"],
            mimetype=dados_qrcode[
                "mimetype"
            ],
            as_attachment=True,
            download_name=dados_qrcode[
                "nome_arquivo"
            ],
            max_age=0
        )

    except ValueError as exc:
        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                erro=str(exc)
            )
        )

    except Exception:
        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                erro=(
                    "Não foi possível gerar o QR Code "
                    "do canal público."
                )
            )
        )


@personalizacao_bp.route(
    "/empresa/personalizacao/logo/remover",
    methods=["POST"]
)
@personalizacao_required
def remover_logo():
    try:
        EmpresaPersonalizacaoService.remover_logo()

        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                logo_removido=1
            )
        )

    except ValueError as exc:
        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                erro=str(exc)
            )
        )

    except Exception:
        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                erro=(
                    "Não foi possível remover "
                    "o logotipo."
                )
            )
        )


@personalizacao_bp.route(
    "/empresa/personalizacao/favicon/remover",
    methods=["POST"]
)
@personalizacao_required
def remover_favicon():
    try:
        (
            EmpresaPersonalizacaoService
            .remover_favicon()
        )

        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                favicon_removido=1
            )
        )

    except ValueError as exc:
        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                erro=str(exc)
            )
        )

    except Exception:
        return redirect(
            url_for(
                "personalizacao.empresa_personalizacao",
                erro=(
                    "Não foi possível remover "
                    "o favicon."
                )
            )
        )
