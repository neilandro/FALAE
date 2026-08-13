from flask import current_app
from flask_mail import Message

from extensions import mail


class EmailService:

    @staticmethod
    def enviar(
        destinatario,
        assunto,
        corpo_html,
        corpo_texto=None
    ):
        if not current_app.config.get("MAIL_ENABLED", False):
            current_app.logger.info(
                (
                    "EMAIL_DESABILITADO | "
                    "destinatario=%s | assunto=%s"
                ),
                destinatario,
                assunto
            )

            return {
                "sucesso": False,
                "enviado": False,
                "motivo": "MAIL_ENABLED=false"
            }

        mensagem = Message(
            subject=assunto,
            recipients=[
                destinatario
            ],
            html=corpo_html,
            body=corpo_texto
        )

        mail.send(
            mensagem
        )

        current_app.logger.info(
            (
                "EMAIL_ENVIADO | "
                "destinatario=%s | assunto=%s"
            ),
            destinatario,
            assunto
        )

        return {
            "sucesso": True,
            "enviado": True
        }