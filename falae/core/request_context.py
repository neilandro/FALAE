import time
import uuid

from flask import (
    current_app,
    g,
    redirect,
    request,
    session,
    url_for,
)


ENDPOINTS_LIBERADOS_TROCA_SENHA = {
    "auth.alterar_senha_obrigatoria",
    "auth.logout",
    "static",
}


def _obter_ip_cliente() -> str | None:
    confiar_proxy = current_app.config.get(
        "TRUST_PROXY_HEADERS",
        False,
    )

    if confiar_proxy:
        ip_encaminhado = request.headers.get(
            "X-Forwarded-For",
            "",
        )

        if ip_encaminhado:
            return (
                ip_encaminhado
                .split(",", maxsplit=1)[0]
                .strip()[:45]
                or None
            )

    if not request.remote_addr:
        return None

    return request.remote_addr[:45]


def _deve_redirecionar_troca_senha() -> bool:
    usuario_logado = bool(
        session.get("usuario_id")
    )

    troca_obrigatoria = bool(
        session.get(
            "trocar_senha_primeiro_acesso",
            False,
        )
    )

    endpoint_atual = request.endpoint

    if not usuario_logado:
        return False

    if not troca_obrigatoria:
        return False

    if endpoint_atual is None:
        return False

    return (
        endpoint_atual
        not in ENDPOINTS_LIBERADOS_TROCA_SENHA
    )


def iniciar_request_context():
    g.request_id = str(
        uuid.uuid4()
    )

    g.inicio = time.perf_counter()

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

    g.ip = _obter_ip_cliente()

    g.user_agent = (
        request.headers.get(
            "User-Agent",
            "",
        )[:500]
        or None
    )

    g.metodo = request.method
    g.rota = request.path

    if _deve_redirecionar_troca_senha():
        return redirect(
            url_for(
                "auth.alterar_senha_obrigatoria"
            )
        )

    return None


def finalizar_request_context(response):
    inicio = getattr(
        g,
        "inicio",
        None,
    )

    if inicio is None:
        tempo_ms = 0.0
    else:
        tempo_ms = round(
            (
                time.perf_counter()
                - inicio
            )
            * 1000,
            2,
        )

    request_id = getattr(
        g,
        "request_id",
        str(uuid.uuid4()),
    )

    mensagem = (
        "REQUEST=%s | "
        "EMPRESA=%s | "
        "USUARIO=%s | "
        "PERFIL=%s | "
        "IP=%s | "
        "%s %s | "
        "STATUS=%s | "
        "%.2f ms"
    )

    argumentos = (
        request_id,
        getattr(g, "empresa_id", None),
        getattr(g, "usuario_id", None),
        getattr(g, "perfil", None),
        getattr(g, "ip", None),
        getattr(g, "metodo", request.method),
        getattr(g, "rota", request.path),
        response.status_code,
        tempo_ms,
    )

    if response.status_code >= 500:
        current_app.logger.error(
            mensagem,
            *argumentos,
        )

    elif response.status_code >= 400:
        current_app.logger.warning(
            mensagem,
            *argumentos,
        )

    else:
        current_app.logger.info(
            mensagem,
            *argumentos,
        )

    response.headers[
        "X-Request-ID"
    ] = request_id

    return response