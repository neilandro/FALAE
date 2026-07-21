from falae.repositories.acompanhamento_repository import AcompanhamentoRepository
from falae.workflow.workflow_engine import WorkflowEngine


class AcompanhamentoService:

    @staticmethod
    def consultar(protocolo):
        protocolo = (protocolo or "").strip().upper()

        if not protocolo:
            return None

        repo = AcompanhamentoRepository()

        try:
            denuncia = repo.buscar_por_protocolo(protocolo)
        finally:
            repo.close()

        if not denuncia:
            return None

        etapa_atual = denuncia.get("etapa_atual") or "TRIAGEM"
        resumo_etapa = WorkflowEngine.resumo_etapa_atual(etapa_atual)
        linha_do_tempo = WorkflowEngine.montar_linha_do_tempo(etapa_atual)

        return {
            "denuncia": denuncia,
            "resumo_etapa": resumo_etapa,
            "linha_do_tempo": linha_do_tempo,
            "mensagem": AcompanhamentoService._mensagem_publica(denuncia)
        }

    @staticmethod
    def _mensagem_publica(denuncia):
        status = denuncia.get("status")

        if status == "NOVA":
            return "Sua denúncia foi recebida e aguarda triagem inicial."

        if status == "EM_ANALISE":
            return "Sua denúncia está em análise pela equipe responsável."

        if status == "CONCLUIDA":
            return "Sua denúncia foi concluída pela equipe responsável."

        if status == "ARQUIVADA":
            return "Sua denúncia foi analisada e arquivada pela equipe responsável."

        return "Sua denúncia está registrada no sistema."