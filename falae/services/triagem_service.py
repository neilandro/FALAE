from flask import current_app, session

from falae.repositories.triagem_repository import TriagemRepository
from falae.repositories.usuario_repository import UsuarioRepository
from falae.services.notificacao_service import NotificacaoService
from falae.workflow.workflow_engine import WorkflowEngine

class TriagemService:

        @staticmethod
        def concluir_triagem(
            denuncia_id,
            criticidade,
            categoria,
            responsavel_id,
            parecer_triagem,
            necessita_investigacao,
            prioridade
        ):
            empresa_id = session["empresa_id"]
            usuario_id = session["usuario_id"]

            if responsavel_id:
                responsavel_id = int(responsavel_id)
            else:
                responsavel_id = None

            necessita_investigacao = (
                True
                if necessita_investigacao == "SIM"
                else False
            )

            repo = TriagemRepository()
            usuario_repo = UsuarioRepository()

            try:
                denuncia = repo.buscar_denuncia(
                    denuncia_id,
                    empresa_id
                )

                if not denuncia:
                    return {
                        "sucesso": False,
                        "mensagem": "Denúncia não encontrada."
                    }

                responsavel_anterior_id = (
                    denuncia.get("responsavel_id")
                )

                responsavel = None

                if responsavel_id:
                    responsavel = usuario_repo.buscar_por_id(
                        responsavel_id,
                        empresa_id
                    )

                    if not responsavel:
                        return {
                            "sucesso": False,
                            "mensagem": "Responsável inválido."
                        }

                workflow_inicial = None

                if necessita_investigacao:
                    workflow_inicial = (
                        WorkflowEngine
                        .preparar_investigacao_pos_triagem(
                            responsavel_id=responsavel_id,
                            observacao=parecer_triagem
                        )
                    )

                resultado = repo.concluir_triagem(
                    denuncia_id=denuncia_id,
                    empresa_id=empresa_id,
                    criticidade=criticidade,
                    categoria=categoria,
                    responsavel_id=responsavel_id,
                    parecer_triagem=parecer_triagem,
                    necessita_investigacao=necessita_investigacao,
                    prioridade=prioridade,
                    triagem_realizada_por=usuario_id,
                    workflow_inicial=workflow_inicial
                )

                houve_nova_atribuicao = (
                    necessita_investigacao
                    and responsavel_id is not None
                    and responsavel_id != responsavel_anterior_id
                )

                if houve_nova_atribuicao:
                    try:
                        NotificacaoService.notificar_responsavel_atribuido(
                            responsavel=responsavel,
                            protocolo=denuncia["protocolo"]
                        )

                    except Exception:
                        current_app.logger.exception(
                            (
                                "Falha ao enviar notificação "
                                "de responsável após triagem | "
                                "empresa_id=%s | "
                                "denuncia_id=%s | "
                                "responsavel_id=%s"
                            ),
                            empresa_id,
                            denuncia_id,
                            responsavel_id
                        )

                return {
                    "sucesso": True,
                    "denuncia": denuncia,
                    "resultado": resultado
                }

            finally:
                repo.close()
                usuario_repo.close()