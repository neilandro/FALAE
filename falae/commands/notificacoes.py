import click

from falae.repositories.usuario_repository import (
    UsuarioRepository
)
from falae.repositories.denuncia_repository import (
    DenunciaRepository
)
from falae.services.notificacao_service import (
    NotificacaoService
)


@click.command("notificacoes-semanais")
def notificacoes_semanais():
    usuario_repo = UsuarioRepository()

    empresas_processadas = 0
    empresas_com_pendencias = 0
    emails_enviados = 0
    erros = 0

    try:
        empresas = usuario_repo.listar_empresas()

        for empresa in empresas:
            empresas_processadas += 1

            empresa_id = empresa["id"]

            denuncia_repo = DenunciaRepository()

            try:
                denuncias = (
                    denuncia_repo
                    .listar_paradas_para_notificacao(
                        empresa_id=empresa_id,
                        dias=7,
                        limite=100
                    )
                )

            finally:
                denuncia_repo.close()

            if not denuncias:
                continue

            empresas_com_pendencias += 1

            try:
                resultado = (
                    NotificacaoService
                    .notificar_resumo_semanal(
                        empresa_id=empresa_id,
                        denuncias=denuncias,
                        dias=7
                    )
                )

                emails_enviados += int(
                    resultado.get(
                        "enviados",
                        0
                    )
                )

            except Exception as exc:
                erros += 1

                click.echo(
                    (
                        f"ERRO | "
                        f"empresa_id={empresa_id} | "
                        f"{exc}"
                    )
                )

        click.echo("")
        click.echo("Resumo da execução")
        click.echo("------------------")
        click.echo(
            f"Empresas processadas: {empresas_processadas}"
        )
        click.echo(
            (
                "Empresas com pendências: "
                f"{empresas_com_pendencias}"
            )
        )
        click.echo(
            f"E-mails enviados: {emails_enviados}"
        )
        click.echo(
            f"Erros: {erros}"
        )

    finally:
        usuario_repo.close()