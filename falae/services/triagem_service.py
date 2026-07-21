from flask import session

from falae.repositories.triagem_repository import TriagemRepository
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

        necessita_investigacao = True if necessita_investigacao == "SIM" else False

        repo = TriagemRepository()

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

            workflow_inicial = None

            if necessita_investigacao:
                workflow_inicial = WorkflowEngine.preparar_investigacao_pos_triagem(
                    responsavel_id=responsavel_id,
                    observacao=parecer_triagem
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

            return {
                "sucesso": True,
                "denuncia": denuncia,
                "resultado": resultado
            }

        finally:
            repo.close()