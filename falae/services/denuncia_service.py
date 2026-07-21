from flask import session

from falae.repositories.denuncia_repository import DenunciaRepository
from falae.repositories.usuario_repository import UsuarioRepository
from falae.workflow.workflow_engine import WorkflowEngine
from falae.services.context_service import ContextService


class DenunciaService:

    @staticmethod
    def _empresa_id():
        return ContextService.empresa()

    # =====================================================
    # COMBOS / FILTROS
    # =====================================================

    @staticmethod
    def listar_unidades():
        repo = DenunciaRepository()

        try:
            return repo.listar_unidades(DenunciaService._empresa_id())
        finally:
            repo.close()

    @staticmethod
    def listar_categorias():
        repo = DenunciaRepository()

        try:
            return repo.listar_categorias(DenunciaService._empresa_id())
        finally:
            repo.close()

    @staticmethod
    def listar_criticidades():
        repo = DenunciaRepository()

        try:
            return repo.listar_criticidades(DenunciaService._empresa_id())
        finally:
            repo.close()

    @staticmethod
    def listar_investigadores():
        repo = UsuarioRepository()

        try:
            return repo.listar_investigadores(DenunciaService._empresa_id())
        finally:
            repo.close()

    # =====================================================
    # DENÚNCIAS
    # =====================================================

    @staticmethod
    def obter_denuncia(denuncia_id):
        repo = DenunciaRepository()

        try:
            return repo.buscar_por_id(
                denuncia_id,
                DenunciaService._empresa_id()
            )
        finally:
            repo.close()

    @staticmethod
    def obter_denuncia_com_workflow(denuncia_id):
        repo = DenunciaRepository()

        try:
            empresa_id = DenunciaService._empresa_id()

            denuncia = repo.buscar_por_id(
                denuncia_id,
                empresa_id
            )

            if not denuncia:
                return None

            etapa_atual = denuncia.get("etapa_atual") or "TRIAGEM"

            workflow = repo.listar_workflow(
                denuncia_id,
                empresa_id
            )

            return {
                "denuncia": denuncia,
                "workflow": workflow,
                "linha_do_tempo": WorkflowEngine.montar_linha_do_tempo(etapa_atual),
                "resumo_etapa": WorkflowEngine.resumo_etapa_atual(etapa_atual)
            }
        finally:
            repo.close()

    @staticmethod
    def atribuir_responsavel(denuncia_id, responsavel_id):
        empresa_id = DenunciaService._empresa_id()

        if not responsavel_id:
            responsavel_id = None

        repo = DenunciaRepository()
        usuario_repo = UsuarioRepository()

        try:
            denuncia = repo.buscar_por_id(denuncia_id, empresa_id)

            if not denuncia:
                return {
                    "sucesso": False,
                    "mensagem": "Denúncia não encontrada."
                }

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

            repo.atualizar_responsavel(
                denuncia_id=denuncia_id,
                empresa_id=empresa_id,
                responsavel_id=responsavel_id
            )

            return {
                "sucesso": True,
                "mensagem": "Responsável atribuído com sucesso.",
                "responsavel": responsavel,
                "valor_antigo": {
                    "responsavel_id": denuncia.get("responsavel_id"),
                    "responsavel": denuncia.get("responsavel")
                },
                "valor_novo": {
                    "responsavel_id": responsavel_id,
                    "responsavel": responsavel["nome"] if responsavel else None
                }
            }
        finally:
            repo.close()
            usuario_repo.close()

    # =====================================================
    # WORKFLOW
    # =====================================================

    @staticmethod
    def listar_workflow(denuncia_id):
        repo = DenunciaRepository()

        try:
            return repo.listar_workflow(
                denuncia_id,
                DenunciaService._empresa_id()
            )
        finally:
            repo.close()

    @staticmethod
    def iniciar_etapa(workflow_id, responsavel_id=None):
        repo = DenunciaRepository()

        try:
            repo.iniciar_etapa_workflow(
                workflow_id,
                DenunciaService._empresa_id(),
                responsavel_id
            )
        finally:
            repo.close()

    @staticmethod
    def concluir_etapa(workflow_id, observacao=None):
        repo = DenunciaRepository()

        try:
            repo.concluir_etapa_workflow(
                workflow_id,
                DenunciaService._empresa_id(),
                observacao
            )
        finally:
            repo.close()

    @staticmethod
    def alterar_etapa_denuncia(denuncia_id, etapa):
        repo = DenunciaRepository()

        try:
            repo.atualizar_etapa_atual(
                denuncia_id,
                DenunciaService._empresa_id(),
                etapa
            )
        finally:
            repo.close()

    @staticmethod
    def avancar_etapa(denuncia_id, observacao=None):
        repo = DenunciaRepository()

        try:
            empresa_id = DenunciaService._empresa_id()
            usuario_id = session.get("usuario_id")

            denuncia = repo.buscar_por_id(
                denuncia_id=denuncia_id,
                empresa_id=empresa_id
            )

            if not denuncia:
                return {
                    "sucesso": False,
                    "mensagem": "Denúncia não encontrada."
                }

            etapa_atual = denuncia.get("etapa_atual") or "TRIAGEM"

            if etapa_atual == "PLANO_ACAO":
                from falae.repositories.plano_acao_repository import PlanoAcaoRepository

                resumo_planos = PlanoAcaoRepository.resumo_por_denuncia(
                    empresa_id=empresa_id,
                    denuncia_id=denuncia_id
                )

                if resumo_planos["total"] == 0:
                    return {
                        "sucesso": False,
                        "mensagem": "Cadastre ao menos um plano de ação antes de avançar para Validação."
                    }

                if resumo_planos["pendentes"] > 0:
                    return {
                        "sucesso": False,
                        "mensagem": "Conclua todos os planos de ação antes de avançar para Validação."
                    }

            proxima_etapa = WorkflowEngine.proxima_etapa(etapa_atual)

            if not proxima_etapa:
                return {
                    "sucesso": False,
                    "mensagem": "Não existe uma próxima etapa."
                }

            proxima_etapa_codigo = proxima_etapa["codigo"]
            proxima_etapa_nome = proxima_etapa["nome"]

            dados_nova_etapa = WorkflowEngine.preparar_inicio_etapa(
                codigo_etapa=proxima_etapa_codigo,
                responsavel_id=denuncia.get("responsavel_id"),
                observacao=observacao
            )

            novo_status = WorkflowEngine.definir_status_por_etapa(
                proxima_etapa_codigo
            )

            repo.avancar_workflow(
                denuncia_id=denuncia_id,
                empresa_id=empresa_id,
                etapa_atual=etapa_atual,
                proxima_etapa=dados_nova_etapa,
                novo_status=novo_status,
                usuario_id=usuario_id,
                observacao=observacao
            )

            return {
                "sucesso": True,
                "mensagem": f"Denúncia avançada para {proxima_etapa_nome}.",
                "etapa_anterior": etapa_atual,
                "etapa_atual": proxima_etapa_codigo,
                "etapa_nome": proxima_etapa_nome
            }

        finally:
            repo.close()

    # =====================================================
    # FLUXO PADRÃO
    # =====================================================

    @staticmethod
    def etapas_padrao():
        return WorkflowEngine.listar_etapas()