from uuid import uuid4
from werkzeug.exceptions import HTTPException

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)

from db import get_connection
from falae.services.acompanhamento_service import (
    AcompanhamentoService
)
from falae.services.anexo_service import AnexoService
from falae.services.empresa_personalizacao_service import (
    EmpresaPersonalizacaoService
)

from falae.services.notificacao_service import (
    NotificacaoService
)

public_bp = Blueprint(
    "public",
    __name__
)


def _buscar_empresa_por_id(
    empresa_id: int
) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                nome,
                slug,
                logo,
                token_publico,
                ativa
            FROM empresas
            WHERE id = %s
            LIMIT 1
            """,
            (empresa_id,)
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def _montar_empresa(
    personalizacao: dict
) -> dict:
    return {
        "id": personalizacao["empresa_id"],
        "nome": personalizacao["empresa_nome"],
        "slug": personalizacao["empresa_slug"],
        "logo": personalizacao["empresa_logo"],
        "token_publico": personalizacao["token_publico"],
        "ativa": personalizacao["empresa_ativa"]
    }


def _listar_unidades(
    empresa_id: int
) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                nome
            FROM unidades
            WHERE empresa_id = %s
              AND ativa = 1
            ORDER BY nome
            """,
            (empresa_id,)
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def _listar_turnos(
    empresa_id: int
) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                nome
            FROM turnos
            WHERE empresa_id = %s
            ORDER BY nome
            """,
            (empresa_id,)
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def _unidade_pertence_empresa(
    unidade_id: int | str | None,
    empresa_id: int
) -> bool:
    if not unidade_id:
        return False

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id
            FROM unidades
            WHERE id = %s
              AND empresa_id = %s
              AND ativa = 1
            LIMIT 1
            """,
            (
                unidade_id,
                empresa_id
            )
        )

        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conn.close()


def _setor_pertence_empresa(
    setor_id: int | str | None,
    unidade_id: int | str,
    empresa_id: int
) -> bool:
    if not setor_id:
        return True

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                s.id
            FROM setores s

            INNER JOIN unidades u
                ON u.id = s.unidade_id

            WHERE s.id = %s
              AND s.unidade_id = %s
              AND u.empresa_id = %s
            LIMIT 1
            """,
            (
                setor_id,
                unidade_id,
                empresa_id
            )
        )

        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conn.close()


def _turno_pertence_empresa(
    turno_id: int | str | None,
    empresa_id: int
) -> bool:
    if not turno_id:
        return True

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id
            FROM turnos
            WHERE id = %s
              AND empresa_id = %s
            LIMIT 1
            """,
            (
                turno_id,
                empresa_id
            )
        )

        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conn.close()


def _registrar_denuncia(
    empresa_id: int,
    arquivos_validados=None
) -> str:
    protocolo = (
        f"FALAE-{uuid4().hex[:10].upper()}"
    )

    tipo = (
        request.form.get("tipo") or ""
    ).strip()

    categoria = (
        request.form.get("categoria") or ""
    ).strip()

    unidade_id = request.form.get(
        "unidade_id"
    )

    setor_id = (
        request.form.get("setor_id")
        or None
    )

    turno_id = (
        request.form.get("turno_id")
        or None
    )

    descricao = (
        request.form.get("descricao") or ""
    ).strip()

    local_ocorrencia = (
        request.form.get("local_ocorrencia") or ""
    ).strip()

    data_ocorrencia = (
        request.form.get("data_ocorrencia")
        or None
    )

    aceite_lgpd = (
        1
        if request.form.get("aceite_lgpd")
        else 0
    )

    aceite_termo = (
        1
        if request.form.get("aceite_termo")
        else 0
    )

    if not tipo:
        raise ValueError(
            "Informe o tipo da denúncia."
        )

    if not categoria:
        raise ValueError(
            "Informe a categoria da denúncia."
        )

    if not descricao:
        raise ValueError(
            "Descreva a situação que deseja denunciar."
        )

    if not aceite_lgpd:
        raise ValueError(
            "É necessário aceitar o texto de privacidade e LGPD."
        )

    if not aceite_termo:
        raise ValueError(
            "É necessário aceitar o termo de uso."
        )

    if not _unidade_pertence_empresa(
        unidade_id=unidade_id,
        empresa_id=empresa_id
    ):
        raise ValueError(
            "A unidade selecionada é inválida."
        )

    if not _setor_pertence_empresa(
        setor_id=setor_id,
        unidade_id=unidade_id,
        empresa_id=empresa_id
    ):
        raise ValueError(
            "O setor selecionado é inválido."
        )

    if not _turno_pertence_empresa(
        turno_id=turno_id,
        empresa_id=empresa_id
    ):
        raise ValueError(
            "O turno selecionado é inválido."
        )

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO denuncias (
                empresa_id,
                protocolo,
                tipo,
                categoria,
                unidade_id,
                setor_id,
                turno_id,
                descricao,
                local_ocorrencia,
                data_ocorrencia,
                aceite_lgpd,
                aceite_termo,
                status,
                etapa_atual
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'NOVA',
                'TRIAGEM'
            )
            """,
            (
                empresa_id,
                protocolo,
                tipo,
                categoria,
                unidade_id,
                setor_id,
                turno_id,
                descricao,
                local_ocorrencia,
                data_ocorrencia,
                aceite_lgpd,
                aceite_termo
            )
        )

        conn.commit()

        denuncia_id = cursor.lastrowid

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

    AnexoService.salvar_anexos(
        arquivos=None,
        denuncia_id=denuncia_id,
        empresa_id=empresa_id,
        arquivos_validados=arquivos_validados
    )

    return protocolo

@public_bp.route("/")
def home():
    return render_template("layouts/site_base.html")

@public_bp.route("/robots.txt")
def robots_txt():
    return current_app.send_static_file("robots.txt")

@public_bp.route("/sitemap.xml")
def sitemap_xml():
    return current_app.send_static_file("sitemap.xml")

@public_bp.route(
    "/canal/<string:slug>",
    methods=["GET"]
)
def canal_publico(slug):
    try:
        personalizacao = (
            EmpresaPersonalizacaoService.obter_por_slug(
                slug
            )
        )

    except ValueError as exc:
        return render_template(
            "public/canal_indisponivel.html",
            mensagem=str(exc)
        ), 404

    empresa = _montar_empresa(
        personalizacao
    )

    return render_template(
        "public/canal.html",
        empresa=empresa,
        personalizacao=personalizacao
    )


@public_bp.route(
    "/canal/<string:slug>/denunciar",
    methods=["GET", "POST"]
)
def canal_denunciar(slug):
    try:
        personalizacao = (
            EmpresaPersonalizacaoService.obter_por_slug(
                slug
            )
        )

    except ValueError as exc:
        return render_template(
            "public/canal_indisponivel.html",
            mensagem=str(exc)
        ), 404

    empresa = _montar_empresa(
        personalizacao
    )

    empresa_id = empresa["id"]

    unidades = _listar_unidades(
        empresa_id
    )

    turnos = _listar_turnos(
        empresa_id
    )

    erro = None

    if request.method == "POST":
        try:
            arquivos = request.files.getlist(
                "anexos"
            )

            arquivos_validados = (
                AnexoService.validar_anexos(
                    arquivos
                )
            )

            protocolo = _registrar_denuncia(
                empresa_id=empresa_id,
                arquivos_validados=arquivos_validados
            )

            try:
                NotificacaoService.notificar_nova_denuncia(
                    empresa_id=empresa_id,
                    protocolo=protocolo
                )

            except Exception:
                current_app.logger.exception(
                    (
                        "Falha ao processar notificação "
                        "de nova denúncia | "
                        "empresa_id=%s | protocolo=%s"
                    ),
                    empresa_id,
                    protocolo
                )

            return render_template(
                "public/denuncia_sucesso.html",
                protocolo=protocolo,
                aviso_anexo=None,
                empresa=empresa,
                personalizacao=personalizacao
            )

        except ValueError as exc:
            erro = str(exc)

        except HTTPException:
            raise

        except Exception:
            current_app.logger.exception(
                "Erro inesperado ao registrar denúncia | "
                "empresa_id=%s",
                empresa_id
            )

            erro = (
                "Não foi possível registrar a denúncia. "
                "Revise os dados e tente novamente."
            )

    return render_template(
        "public/denunciar.html",
        empresa_id=empresa_id,
        empresa=empresa,
        personalizacao=personalizacao,
        unidades=unidades,
        turnos=turnos,
        erro=erro
    )


@public_bp.route(
    "/denunciar/<int:empresa_id>",
    methods=["GET"]
)
def denunciar(empresa_id):
    empresa = _buscar_empresa_por_id(
        empresa_id
    )

    if not empresa:
        return "Empresa não encontrada.", 404

    if not empresa.get("ativa"):
        return (
            "Este canal de denúncias está "
            "temporariamente indisponível."
        ), 404

    if not empresa.get("slug"):
        return (
            "O endereço público desta empresa "
            "ainda não foi configurado."
        ), 404

    return redirect(
        url_for(
            "public.canal_denunciar",
            slug=empresa["slug"]
        )
    )


@public_bp.route(
    "/acompanhar",
    methods=["GET", "POST"]
)
def acompanhar():
    resultado = None
    erro = None

    if request.method == "POST":
        protocolo = (
            request.form.get("protocolo") or ""
        ).strip()

        if not protocolo:
            erro = "Informe o número do protocolo."

        else:
            resultado = (
                AcompanhamentoService.consultar(
                    protocolo
                )
            )

            if not resultado:
                erro = (
                    "Protocolo não encontrado. "
                    "Verifique o número informado."
                )

    return render_template(
        "public/acompanhar.html",
        resultado=resultado,
        erro=erro
    )