import time
import uuid

from flask import (
    current_app,
    g,
    redirect,
    request,
    session,
    url_for
)


ENDPOINTS_LIBERADOS_TROCA_SENHA = {
    "auth.alterar_senha_obrigatoria",
    "auth.logout",
    "static"
}


def iniciar_request_context():
    g.request_id = str(
        uuid.uuid4()
    )

    g.inicio = time.time()

    g.usuario_id = session.get(
        "usuario_id"
    )

    g.empresa_id = (
        session.get("empresa_ativa")
        or session.get("empresa_id")
    )

    g.nome = session.get(
        "nome"
    )

    g.perfil = session.get(
        "perfil"
    )

    ip_encaminhado = request.headers.get(
        "X-Forwarded-For"
    )

    if ip_encaminhado:
        g.ip = (
            ip_encaminhado
            .split(",")[0]
            .strip()[:45]
        )

    else:
        g.ip = (
            request.remote_addr[:45]
            if request.remote_addr
            else None
        )

    g.user_agent = request.headers.get(
        "User-Agent"
    )

    g.metodo = request.method
    g.rota = request.path

    usuario_logado = session.get(
        "usuario_id"
    )

    troca_obrigatoria = session.get(
        "trocar_senha_primeiro_acesso",
        False
    )

    endpoint_atual = request.endpoint

    if (
        usuario_logado
        and troca_obrigatoria
        and endpoint_atual
        not in ENDPOINTS_LIBERADOS_TROCA_SENHA
    ):
        return redirect(
            url_for(
                "auth.alterar_senha_obrigatoria"
            )
        )

    return None


def finalizar_request_context(
    response
):
    inicio = getattr(
        g,
        "inicio",
        time.time()
    )

    tempo_ms = round(
        (
            time.time()
            - inicio
        )
        * 1000,
        2
    )

    request_id = getattr(
        g,
        "request_id",
        str(uuid.uuid4())
    )

    current_app.logger.info(
        (
            f"REQUEST={request_id} | "
            f"EMPRESA={getattr(g, 'empresa_id', None)} | "
            f"USUARIO={getattr(g, 'usuario_id', None)} | "
            f"PERFIL={getattr(g, 'perfil', None)} | "
            f"IP={getattr(g, 'ip', None)} | "
            f"{getattr(g, 'metodo', request.method)} "
            f"{getattr(g, 'rota', request.path)} | "
            f"STATUS={response.status_code} | "
            f"{tempo_ms} ms"
        )
    )

    response.headers[
        "X-Request-ID"
    ] = request_id

    return response