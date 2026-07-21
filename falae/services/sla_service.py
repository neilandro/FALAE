from datetime import datetime

from falae.workflow.workflow_engine import WorkflowEngine


class SlaService:

    @staticmethod
    def calcular(denuncia):
        etapa_atual = denuncia.get("etapa_atual") or "TRIAGEM"
        criado_em = denuncia.get("criado_em")

        etapa = WorkflowEngine.obter_etapa(etapa_atual)

        if not etapa or not criado_em:
            return SlaService._sem_sla()

        if isinstance(criado_em, str):
            criado_em = SlaService._parse_datetime(criado_em)

        if not criado_em:
            return SlaService._sem_sla()

        prazo_limite = WorkflowEngine.calcular_prazo_limite(
            etapa_atual,
            criado_em
        )

        agora = datetime.now()

        dias_restantes = (prazo_limite.date() - agora.date()).days

        if dias_restantes < 0:
            dias_atraso = abs(dias_restantes)

            return {
                "status": "ATRASADO",
                "classe": "danger",
                "icone": "🔴",
                "dias": dias_atraso,
                "texto": f"{dias_atraso} dia(s) de atraso"
            }

        if dias_restantes == 0:
            return {
                "status": "VENCE_HOJE",
                "classe": "warning",
                "icone": "🟡",
                "dias": 0,
                "texto": "Vence hoje"
            }

        return {
            "status": "NO_PRAZO",
            "classe": "success",
            "icone": "🟢",
            "dias": dias_restantes,
            "texto": f"{dias_restantes} dia(s) restantes"
        }

    @staticmethod
    def _sem_sla():
        return {
            "status": "SEM_SLA",
            "classe": "neutral",
            "icone": "⚪",
            "dias": None,
            "texto": "SLA não definido"
        }

    @staticmethod
    def _parse_datetime(valor):
        formatos = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y"
        ]

        for formato in formatos:
            try:
                return datetime.strptime(valor, formato)
            except ValueError:
                continue

        return None