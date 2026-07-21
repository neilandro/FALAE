from flask import session

from falae.repositories.investigador_repository import InvestigadorRepository
from falae.services.sla_service import SlaService


class InvestigadorService:

    @staticmethod
    def obter_agenda():
        usuario_id = session["usuario_id"]
        empresa_id = session["empresa_id"]

        repo = InvestigadorRepository()

        try:
            minhas_denuncias = repo.minhas_denuncias(
                empresa_id,
                usuario_id
            )

            for denuncia in minhas_denuncias:
                denuncia["sla"] = SlaService.calcular(denuncia)

            criticas = repo.total_criticas(
                empresa_id,
                usuario_id
            )

            abertas = repo.total_abertas(
                empresa_id,
                usuario_id
            )

            vencidas = repo.total_vencidas(
                empresa_id,
                usuario_id
            )

            concluidas = repo.total_concluidas_mes(
                empresa_id,
                usuario_id
            )

        finally:
            repo.close()

        return {
            "minhas_denuncias": minhas_denuncias,
            "indicadores": {
                "criticas": criticas,
                "abertas": abertas,
                "vencidas": vencidas,
                "concluidas": concluidas
            }
        }