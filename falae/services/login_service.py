from datetime import datetime

from flask import request, url_for

from db import get_connection
from extensions import bcrypt
from falae.repositories.usuario_repository import (
    UsuarioRepository
)


class LoginService:

    MAXIMO_TENTATIVAS_LOGIN = 3
    TEMPO_BLOQUEIO_MINUTOS = 15

    @staticmethod
    def autenticar(
        email: str | None,
        senha: str | None
    ) -> dict:
        email_normalizado = (
            email or ""
        ).strip().lower()

        senha_informada = (
            senha or ""
        )

        if not email_normalizado or not senha_informada:
            return {
                "sucesso": False,
                "mensagem": "Informe o e-mail e a senha."
            }

        usuario = LoginService._buscar_usuario_por_email(
            email_normalizado
        )

        if not usuario:
            return {
                "sucesso": False,
                "mensagem": "E-mail ou senha inválidos."
            }

        usuario_id = usuario["id"]
        bloqueado_ate = usuario.get(
            "bloqueado_ate"
        )

        agora = datetime.now()

        repo = UsuarioRepository()

        try:
            if (
                bloqueado_ate
                and bloqueado_ate > agora
            ):
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Acesso temporariamente bloqueado "
                        "por segurança. "
                        "Tente novamente após "
                        f"{LoginService._formatar_horario(
                            bloqueado_ate
                        )}."
                    )
                }

            if (
                bloqueado_ate
                and bloqueado_ate <= agora
            ):
                repo.resetar_tentativas_login(
                    usuario_id
                )

                usuario["tentativas_login"] = 0
                usuario["bloqueado_ate"] = None

            senha_valida = bcrypt.check_password_hash(
                usuario["senha_hash"],
                senha_informada
            )

            if not senha_valida:
                tentativas = (
                    repo.incrementar_tentativas_login(
                        usuario_id
                    )
                )

                if (
                    tentativas
                    >= LoginService.MAXIMO_TENTATIVAS_LOGIN
                ):
                    repo.bloquear_usuario(
                        usuario_id=usuario_id,
                        minutos=(
                            LoginService
                            .TEMPO_BLOQUEIO_MINUTOS
                        )
                    )

                    return {
                        "sucesso": False,
                        "mensagem": (
                            "Acesso temporariamente bloqueado "
                            "por segurança após "
                            f"{LoginService.MAXIMO_TENTATIVAS_LOGIN} "
                            "tentativas inválidas. "
                            "Tente novamente em "
                            f"{LoginService.TEMPO_BLOQUEIO_MINUTOS} "
                            "minutos."
                        )
                    }

                tentativas_restantes = (
                    LoginService.MAXIMO_TENTATIVAS_LOGIN
                    - tentativas
                )

                if tentativas_restantes == 1:
                    mensagem = (
                        "E-mail ou senha inválidos. "
                        "Você possui mais 1 tentativa antes "
                        "do bloqueio temporário."
                    )

                else:
                    mensagem = (
                        "E-mail ou senha inválidos. "
                        f"Você possui mais {tentativas_restantes} "
                        "tentativas antes do bloqueio temporário."
                    )

                return {
                    "sucesso": False,
                    "mensagem": mensagem
                }

            repo.registrar_login_sucesso(
                usuario_id=usuario_id,
                ip=LoginService._obter_ip_usuario()
            )

        finally:
            repo.close()

        return {
            "sucesso": True,
            "usuario": usuario,
            "destino": (
                LoginService.redirecionar_pos_login(
                    usuario
                )
            )
        }

    @staticmethod
    def _buscar_usuario_por_email(
        email: str
    ) -> dict | None:
        conn = get_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        try:
            cursor.execute(
                """
                SELECT
                    u.*,
                    a.nome AS assessoria_nome
                FROM usuarios u

                LEFT JOIN assessorias a
                    ON a.id = u.assessoria_id

                WHERE LOWER(TRIM(u.email))
                    = LOWER(TRIM(%s))
                  AND u.ativo = 1

                LIMIT 1
                """,
                (email,)
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def _obter_ip_usuario() -> str | None:
        ip_encaminhado = request.headers.get(
            "X-Forwarded-For"
        )

        if ip_encaminhado:
            return (
                ip_encaminhado
                .split(",")[0]
                .strip()[:45]
            )

        if request.remote_addr:
            return request.remote_addr[:45]

        return None

    @staticmethod
    def _formatar_horario(
        data_hora
    ) -> str:
        if not data_hora:
            return ""

        if isinstance(
            data_hora,
            datetime
        ):
            return data_hora.strftime(
                "%H:%M"
            )

        return str(
            data_hora
        )

    @staticmethod
    def redirecionar_pos_login(
        usuario
    ):
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

        if perfil in [
            "ADMIN_EMPRESA",
            "GESTOR",
            "AUDITOR",
            "VISUALIZADOR"
        ]:
            return url_for(
                "dashboard.centro_controle"
            )

        if perfil == "INVESTIGADOR":
            return url_for(
                "investigador.minha_agenda"
            )

        return url_for(
            "auth.login"
        )
