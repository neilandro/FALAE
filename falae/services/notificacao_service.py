from flask import current_app, render_template

from falae.repositories.usuario_repository import (
    UsuarioRepository
)

from falae.services.email_service import (
    EmailService
)


class NotificacaoService:

    @staticmethod
    def notificar_nova_denuncia(
        empresa_id,
        protocolo
    ):
        repository = UsuarioRepository()

        try:
            administradores = (
                repository
                .listar_admins_empresa_para_notificacao(
                    empresa_id
                )
            )

            if not administradores:
                current_app.logger.warning(
                    (
                        "NOTIFICACAO_NOVA_DENUNCIA | "
                        "Nenhum ADMIN_EMPRESA encontrado | "
                        "empresa_id=%s | protocolo=%s"
                    ),
                    empresa_id,
                    protocolo
                )

                return

            for administrador in administradores:
                corpo_html = render_template(
                    "emails/nova_denuncia.html",
                    nome=administrador["nome"],
                    protocolo=protocolo
                )

                corpo_texto = (
                    f"Olá, {administrador['nome']}.\n\n"
                    "Uma nova denúncia foi registrada no FALAE "
                    "e está aguardando análise.\n\n"
                    f"Protocolo: {protocolo}\n\n"
                    "Acesse o FALAE para consultar as informações."
                )

                EmailService.enviar(
                    destinatario=administrador["email"],
                    assunto="Nova denúncia registrada no FALAE",
                    corpo_html=corpo_html,
                    corpo_texto=corpo_texto
                )

        finally:
            repository.close()

    @staticmethod
    def notificar_responsavel_atribuido(
        responsavel,
        protocolo
    ):
        if not responsavel:
            return

        email = (
            responsavel.get("email") or ""
        ).strip()

        if not email:
            current_app.logger.warning(
                (
                    "NOTIFICACAO_RESPONSAVEL | "
                    "Responsável sem e-mail | "
                    "responsavel_id=%s | protocolo=%s"
                ),
                responsavel.get("id"),
                protocolo
            )

            return

        corpo_html = render_template(
            "emails/denuncia_atribuida.html",
            nome=responsavel["nome"],
            protocolo=protocolo
        )

        corpo_texto = (
            f"Olá, {responsavel['nome']}.\n\n"
            "Uma denúncia foi atribuída à sua "
            "responsabilidade no FALAE.\n\n"
            f"Protocolo: {protocolo}\n\n"
            "Acesse o FALAE para consultar as informações "
            "e dar continuidade ao tratamento."
        )

        EmailService.enviar(
            destinatario=email,
            assunto="Uma denúncia foi atribuída a você no FALAE",
            corpo_html=corpo_html,
            corpo_texto=corpo_texto

        )

    @staticmethod
    def notificar_resumo_semanal(
        empresa_id,
        denuncias,
        dias=7
    ):
        if not denuncias:
            current_app.logger.info(
                (
                    "RESUMO_SEMANAL | "
                    "Nenhuma denúncia parada | "
                    "empresa_id=%s"
                ),
                empresa_id
            )

            return {
                "sucesso": True,
                "enviados": 0
            }

        repository = UsuarioRepository()

        try:
            administradores = (
                repository
                .listar_admins_empresa_para_notificacao(
                    empresa_id
                )
            )

            if not administradores:
                current_app.logger.warning(
                    (
                        "RESUMO_SEMANAL | "
                        "Nenhum ADMIN_EMPRESA encontrado | "
                        "empresa_id=%s"
                    ),
                    empresa_id
                )

                return {
                    "sucesso": False,
                    "enviados": 0
                }

            enviados = 0

            for administrador in administradores:
                corpo_html = render_template(
                    "emails/resumo_semanal.html",
                    nome=administrador["nome"],
                    denuncias=denuncias,
                    dias=dias
                )

                linhas = [
                    f"Olá, {administrador['nome']}.",
                    "",
                    (
                        f"Existem {len(denuncias)} denúncia(s) "
                        f"sem movimentação há pelo menos {dias} dias."
                    ),
                    ""
                ]

                for denuncia in denuncias:
                    linha = (
                        f"{denuncia['protocolo']} - "
                        f"{denuncia['dias_sem_movimentacao']} "
                        "dia(s) sem movimentação"
                    )

                    if denuncia.get("responsavel"):
                        linha += (
                            f" - Responsável: "
                            f"{denuncia['responsavel']}"
                        )

                    linhas.append(linha)

                linhas.extend(
                    [
                        "",
                        (
                            "Acesse o FALAE para revisar as pendências "
                            "e dar continuidade ao tratamento."
                        )
                    ]
                )

                corpo_texto = "\n".join(linhas)

                EmailService.enviar(
                    destinatario=administrador["email"],
                    assunto="FALAE — Resumo semanal de pendências",
                    corpo_html=corpo_html,
                    corpo_texto=corpo_texto
                )

                enviados += 1

            current_app.logger.info(
                (
                    "RESUMO_SEMANAL | "
                    "empresa_id=%s | "
                    "denuncias=%s | "
                    "emails_enviados=%s"
                ),
                empresa_id,
                len(denuncias),
                enviados
            )

            return {
                "sucesso": True,
                "enviados": enviados
            }

        finally:
            repository.close()