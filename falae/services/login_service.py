from datetime import datetime
from typing import Any

from flask import (
    current_app,
    g,
    url_for,
)

from extensions import bcrypt
from falae.repositories.usuario_repository import (
    UsuarioRepository,
)


class LoginService:

    MAXIMO_TENTATIVAS_LOGIN = 3
    TEMPO_BLOQUEIO_MINUTOS = 15

    MENSAGEM_CREDENCIAIS_INVALIDAS = (
        "E-mail ou senha inválidos ou acesso "
        "temporariamente indisponível."
    )

    @staticmethod
    def autenticar(
        email: str | None,
        senha: str | None,
    ) -> dict[str, Any]:
        email_normalizado = (
            email or ""
        ).strip().lower()

        senha_informada = senha or ""

        if (
            not email_normalizado
            or not senha_informada
        ):
            return {
                "sucesso": False,
                "mensagem": (
                    "Informe o e-mail e a senha."
                ),
            }

        repo = UsuarioRepository()

        try:
            usuario = (
                repo.buscar_por_email_login(
                    email_normalizado
                )
            )

            if not usuario:
                current_app.logger.warning(
                    (
                        "AUTENTICACAO_USUARIO_NAO_LOCALIZADO | "
                        "REQUEST=%s | "
                        "IP=%s"
                    ),
                    getattr(
                        g,
                        "request_id",
                        None,
                    ),
                    LoginService._obter_ip_usuario(),
                )

                return {
                    "sucesso": False,
                    "mensagem": (
                        LoginService
                        .MENSAGEM_CREDENCIAIS_INVALIDAS
                    ),
                }

            usuario_id = usuario["id"]

            bloqueado_ate = usuario.get(
                "bloqueado_ate"
            )

            agora = datetime.now()

            if (
                bloqueado_ate
                and bloqueado_ate > agora
            ):
                current_app.logger.warning(
                    (
                        "AUTENTICACAO_USUARIO_BLOQUEADO | "
                        "REQUEST=%s | "
                        "USUARIO=%s | "
                        "IP=%s"
                    ),
                    getattr(
                        g,
                        "request_id",
                        None,
                    ),
                    usuario_id,
                    LoginService._obter_ip_usuario(),
                )

                return {
                    "sucesso": False,
                    "mensagem": (
                        LoginService
                        .MENSAGEM_CREDENCIAIS_INVALIDAS
                    ),
                }

            if (
                bloqueado_ate
                and bloqueado_ate <= agora
            ):
                repo.resetar_tentativas_login(
                    usuario_id
                )

                usuario[
                    "tentativas_login"
                ] = 0

                usuario[
                    "bloqueado_ate"
                ] = None

            senha_hash = usuario.get(
                "senha_hash"
            )

            senha_valida = False

            if senha_hash:
                try:
                    senha_valida = (
                        bcrypt
                        .check_password_hash(
                            senha_hash,
                            senha_informada,
                        )
                    )

                except (ValueError, TypeError):
                    current_app.logger.error(
                        (
                            "AUTENTICACAO_HASH_INVALIDO | "
                            "REQUEST=%s | "
                            "USUARIO=%s"
                        ),
                        getattr(
                            g,
                            "request_id",
                            None,
                        ),
                        usuario_id,
                    )

                    senha_valida = False

            if not senha_valida:
                tentativas = (
                    repo
                    .incrementar_tentativas_login(
                        usuario_id
                    )
                )

                if (
                    tentativas
                    >= LoginService
                    .MAXIMO_TENTATIVAS_LOGIN
                ):
                    repo.bloquear_usuario(
                        usuario_id=usuario_id,
                        minutos=(
                            LoginService
                            .TEMPO_BLOQUEIO_MINUTOS
                        ),
                    )

                    current_app.logger.warning(
                        (
                            "AUTENTICACAO_USUARIO_BLOQUEADO_AGORA | "
                            "REQUEST=%s | "
                            "USUARIO=%s | "
                            "TENTATIVAS=%s | "
                            "IP=%s"
                        ),
                        getattr(
                            g,
                            "request_id",
                            None,
                        ),
                        usuario_id,
                        tentativas,
                        LoginService._obter_ip_usuario(),
                    )

                else:
                    current_app.logger.warning(
                        (
                            "AUTENTICACAO_SENHA_INVALIDA | "
                            "REQUEST=%s | "
                            "USUARIO=%s | "
                            "TENTATIVAS=%s | "
                            "IP=%s"
                        ),
                        getattr(
                            g,
                            "request_id",
                            None,
                        ),
                        usuario_id,
                        tentativas,
                        LoginService._obter_ip_usuario(),
                    )

                return {
                    "sucesso": False,
                    "mensagem": (
                        LoginService
                        .MENSAGEM_CREDENCIAIS_INVALIDAS
                    ),
                }

            repo.registrar_login_sucesso(
                usuario_id=usuario_id,
                ip=LoginService._obter_ip_usuario(),
            )

            current_app.logger.info(
                (
                    "AUTENTICACAO_VALIDADA | "
                    "REQUEST=%s | "
                    "USUARIO=%s | "
                    "PERFIL=%s | "
                    "IP=%s"
                ),
                getattr(
                    g,
                    "request_id",
                    None,
                ),
                usuario_id,
                usuario.get(
                    "perfil"
                ),
                LoginService._obter_ip_usuario(),
            )

            return {
                "sucesso": True,
                "usuario": usuario,
                "destino": (
                    LoginService
                    .redirecionar_pos_login(
                        usuario
                    )
                ),
            }

        finally:
            repo.close()

    @staticmethod
    def _obter_ip_usuario() -> str | None:
        ip = getattr(
            g,
            "ip",
            None,
        )

        if not ip:
            return None

        return str(ip).strip()[:45]

    @staticmethod
    def redirecionar_pos_login(
        usuario: dict[str, Any],
    ) -> str:
        perfil = usuario.get(
            "perfil"
        )

        if perfil == "SUPER_ADMIN":
            return url_for(
                "admin.dashboard"
            )

        if perfil == "ADM_ASSESSORIA":
            return url_for(
                "assessoria.dashboard"
            )

        if perfil in {
            "ADMIN_EMPRESA",
            "GESTOR",
            "AUDITOR",
            "VISUALIZADOR",
        }:
            return url_for(
                "dashboard.centro_controle"
            )

        if perfil == "INVESTIGADOR":
            return url_for(
                "investigador.minha_agenda"
            )

        current_app.logger.error(
            (
                "PERFIL_SEM_DESTINO_POS_LOGIN | "
                "REQUEST=%s | "
                "PERFIL=%s"
            ),
            getattr(
                g,
                "request_id",
                None,
            ),
            perfil,
        )

        return url_for(
            "auth.login"
        )