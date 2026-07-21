from falae.services.context_service import ContextService

from falae.repositories.dashboard_repository import DashboardRepository
from falae.services.audit_service import AuditService
from falae.workflow.workflow_engine import WorkflowEngine


class DashboardService:

    @staticmethod
    def obter_centro_controle():
        empresa_id = ContextService.empresa()

        repo = DashboardRepository()

        try:
            total_denuncias = repo.total_denuncias(empresa_id)
            denuncias_novas = repo.denuncias_novas(empresa_id)
            denuncias_criticas = repo.denuncias_criticas(empresa_id)
            denuncias_em_analise_mais_7_dias = repo.denuncias_em_analise_mais_7_dias(empresa_id)
            denuncias_concluidas_mes = repo.denuncias_concluidas_mes(empresa_id)
            denuncias_em_aberto = repo.denuncias_em_aberto(empresa_id)
            denuncias_criticas_em_aberto = repo.denuncias_criticas_em_aberto(empresa_id)
            tempo_medio_atendimento_dias = repo.tempo_medio_atendimento_dias(empresa_id)
            percentual_concluidas_mes = repo.percentual_concluidas_mes(empresa_id)
            ranking_unidades = repo.ranking_unidades(empresa_id)
            ranking_categorias = repo.ranking_categorias(empresa_id)
            
            ranking_turnos = repo.ranking_turnos(empresa_id)
            dados_turnos = repo.denuncias_por_turno_e_status(empresa_id)

            radar_dados = repo.radar_riscos(empresa_id)
        finally:
            repo.close()

        ultimos_eventos = AuditService.listar_ultimos_eventos(
            empresa_id=empresa_id,
            limite=5
        )

        health_score = DashboardService._calcular_health_score(
            denuncias_em_aberto=denuncias_em_aberto,
            denuncias_criticas_em_aberto=denuncias_criticas_em_aberto,
            denuncias_em_analise_mais_7_dias=denuncias_em_analise_mais_7_dias,
            tempo_medio_atendimento_dias=tempo_medio_atendimento_dias,
            percentual_concluidas_mes=percentual_concluidas_mes
        )

        insights = DashboardService._gerar_insights(
            total_denuncias=total_denuncias,
            denuncias_novas=denuncias_novas,
            denuncias_criticas=denuncias_criticas
        )

        pendencias = DashboardService._gerar_pendencias(
            denuncias_criticas=denuncias_criticas,
            denuncias_em_analise_mais_7_dias=denuncias_em_analise_mais_7_dias,
            denuncias_concluidas_mes=denuncias_concluidas_mes
        )

        acoes_recomendadas = DashboardService._gerar_acoes_recomendadas(
            denuncias_novas=denuncias_novas,
            denuncias_criticas=denuncias_criticas,
            denuncias_em_analise_mais_7_dias=denuncias_em_analise_mais_7_dias,
            denuncias_concluidas_mes=denuncias_concluidas_mes
        )

        alertas_inteligentes = DashboardService.obter_alertas_inteligentes()
        radar_riscos = DashboardService._montar_radar_riscos(radar_dados)
        indicadores_turnos = DashboardService._montar_indicadores_turnos(dados_turnos)

        return {
            "total_denuncias": total_denuncias,
            "denuncias_novas": denuncias_novas,
            "denuncias_criticas": denuncias_criticas,
            "ranking_unidades": ranking_unidades,
            "ranking_categorias": ranking_categorias,
            "ranking_turnos": ranking_turnos,
            "indicadores_turnos": indicadores_turnos,
            "ultimos_eventos": ultimos_eventos,
            "insights": insights,
            "pendencias": pendencias,
            "acoes_recomendadas": acoes_recomendadas,
            "health_score": health_score,
            "alertas_inteligentes": alertas_inteligentes,
            "radar_riscos": radar_riscos
            
        }

    @staticmethod
    def obter_painel_operacional():
        empresa_id = ContextService.empresa()

        repo = DashboardRepository()

        try:
            denuncias = repo.denuncias_kanban(empresa_id)
            resumo_etapas = repo.resumo_kanban_por_etapa(empresa_id)
            denuncias_em_aberto = repo.denuncias_em_aberto(empresa_id)
            denuncias_criticas_em_aberto = repo.denuncias_criticas_em_aberto(empresa_id)
            denuncias_em_analise_mais_7_dias = repo.denuncias_em_analise_mais_7_dias(empresa_id)
            tempo_medio_atendimento_dias = repo.tempo_medio_atendimento_dias(empresa_id)
            percentual_concluidas_mes = repo.percentual_concluidas_mes(empresa_id)
            radar_dados = repo.radar_riscos(empresa_id)
        finally:
            repo.close()

        health_score = DashboardService._calcular_health_score(
            denuncias_em_aberto=denuncias_em_aberto,
            denuncias_criticas_em_aberto=denuncias_criticas_em_aberto,
            denuncias_em_analise_mais_7_dias=denuncias_em_analise_mais_7_dias,
            tempo_medio_atendimento_dias=tempo_medio_atendimento_dias,
            percentual_concluidas_mes=percentual_concluidas_mes
        )

        kanban = DashboardService._montar_kanban(
            denuncias=denuncias,
            resumo_etapas=resumo_etapas
        )

        alertas_inteligentes = DashboardService.obter_alertas_inteligentes()
        radar_riscos = DashboardService._montar_radar_riscos(radar_dados)

        return {
            "health_score": health_score,
            "kanban": kanban,
            "total_abertas": denuncias_em_aberto,
            "total_criticas": denuncias_criticas_em_aberto,
            "total_atrasadas": denuncias_em_analise_mais_7_dias,
            "alertas_inteligentes": alertas_inteligentes,
            "radar_riscos": radar_riscos
        }

    @staticmethod
    def obter_alertas_inteligentes(limite_total=10):
        empresa_id = ContextService.empresa()

        repo = DashboardRepository()

        try:
            criticas_sem_responsavel = repo.alertas_denuncias_criticas_sem_responsavel(empresa_id)
            sem_responsavel = repo.alertas_denuncias_sem_responsavel(empresa_id)
            paradas_mais_7_dias = repo.alertas_denuncias_paradas_mais_7_dias(empresa_id)
            criticas_antigas = repo.alertas_denuncias_criticas_antigas(empresa_id)
            planos_vencidos = repo.alertas_planos_acao_vencidos(empresa_id)
            planos_vencem_amanha = repo.alertas_planos_acao_vencem_amanha(empresa_id)
            em_encerramento = repo.alertas_denuncias_em_encerramento(empresa_id)
        finally:
            repo.close()

        alertas = []

        for denuncia in criticas_sem_responsavel:
            alertas.append({
                "prioridade": "alta",
                "peso": 1,
                "icone": "🔴",
                "titulo": "Denúncia crítica sem responsável",
                "descricao": f"{denuncia['protocolo']} • {denuncia['unidade']}",
                "acao": "Atribuir responsável",
                "url": f"/empresa/denuncia/{denuncia['id']}"
            })

        for denuncia in criticas_antigas:
            alertas.append({
                "prioridade": "alta",
                "peso": 2,
                "icone": "🔴",
                "titulo": "Denúncia crítica parada",
                "descricao": f"{denuncia['protocolo']} • Aberta há {denuncia['dias_aberta']} dia(s)",
                "acao": "Abrir investigação",
                "url": f"/empresa/denuncia/{denuncia['id']}"
            })

        for plano in planos_vencidos:
            alertas.append({
                "prioridade": "alta",
                "peso": 3,
                "icone": "🔴",
                "titulo": "Plano de ação vencido",
                "descricao": f"{plano['protocolo']} • Prazo: {plano['prazo']}",
                "acao": "Ver plano",
                "url": f"/empresa/denuncia/{plano['denuncia_id']}"
            })

        for denuncia in paradas_mais_7_dias:
            alertas.append({
                "prioridade": "media",
                "peso": 4,
                "icone": "🟠",
                "titulo": "Investigação sem movimentação recente",
                "descricao": f"{denuncia['protocolo']} • Aberta há {denuncia['dias_aberta']} dia(s)",
                "acao": "Revisar investigação",
                "url": f"/empresa/denuncia/{denuncia['id']}"
            })

        for denuncia in sem_responsavel:
            alertas.append({
                "prioridade": "media",
                "peso": 5,
                "icone": "🟡",
                "titulo": "Denúncia sem responsável",
                "descricao": f"{denuncia['protocolo']} • {denuncia['unidade']}",
                "acao": "Atribuir responsável",
                "url": f"/empresa/denuncia/{denuncia['id']}"
            })

        for plano in planos_vencem_amanha:
            alertas.append({
                "prioridade": "media",
                "peso": 6,
                "icone": "🟡",
                "titulo": "Plano de ação vence amanhã",
                "descricao": f"{plano['protocolo']} • {plano['titulo']}",
                "acao": "Ver plano",
                "url": f"/empresa/denuncia/{plano['denuncia_id']}"
            })

        for denuncia in em_encerramento:
            alertas.append({
                "prioridade": "baixa",
                "peso": 7,
                "icone": "🟢",
                "titulo": "Investigação pronta para encerramento",
                "descricao": f"{denuncia['protocolo']} • Etapa de encerramento",
                "acao": "Finalizar caso",
                "url": f"/empresa/denuncia/{denuncia['id']}"
            })

        alertas_unicos = DashboardService._remover_alertas_duplicados(alertas)
        alertas_ordenados = sorted(alertas_unicos, key=lambda item: item["peso"])

        return alertas_ordenados[:limite_total]

    @staticmethod
    def _montar_indicadores_turnos(dados_turnos):
        indicadores = []

        for item in dados_turnos:
            total = item["total"] or 0
            em_aberto = item["em_aberto"] or 0
            concluidas = item["concluidas"] or 0
            criticas_abertas = item["criticas_abertas"] or 0
            mais_7_dias = item["mais_7_dias"] or 0

            percentual_concluidas = 0

            if total > 0:
                percentual_concluidas = round(
                    (concluidas / total) * 100,
                    1
                )

            nivel_atencao = DashboardService._classificar_turno(
                criticas_abertas=criticas_abertas,
                mais_7_dias=mais_7_dias,
                em_aberto=em_aberto
            )

            indicadores.append({
                "id": item["id"],
                "nome": item["nome"],
                "total": total,
                "em_aberto": em_aberto,
                "concluidas": concluidas,
                "criticas_abertas": criticas_abertas,
                "mais_7_dias": mais_7_dias,
                "percentual_concluidas": percentual_concluidas,
                "nivel": nivel_atencao["nivel"],
                "classe": nivel_atencao["classe"],
                "icone": nivel_atencao["icone"]
            })

        return indicadores

    @staticmethod
    def _classificar_turno(
        criticas_abertas,
        mais_7_dias,
        em_aberto
    ):
        if criticas_abertas > 0:
            return {
                "nivel": "Crítico",
                "classe": "alto",
                "icone": "🔴"
            }

        if mais_7_dias > 0:
            return {
                "nivel": "Atenção",
                "classe": "elevado",
                "icone": "🟠"
            }

        if em_aberto > 0:
            return {
                "nivel": "Acompanhamento",
                "classe": "moderado",
                "icone": "🟡"
            }

        return {
            "nivel": "Regular",
            "classe": "baixo",
            "icone": "🟢"
        }

    @staticmethod
    def _montar_radar_riscos(radar_dados):
        radar = []

        for item in radar_dados:
            total = item["total"] or 0
            criticas = item["criticas"] or 0
            em_aberto = item["em_aberto"] or 0
            mais_7_dias = item["mais_7_dias"] or 0
            media_dias_aberta = float(item["media_dias_aberta"] or 0)

            indice = 0

            indice += min(total * 5, 25)
            indice += min(criticas * 15, 35)
            indice += min(em_aberto * 6, 25)
            indice += min(mais_7_dias * 8, 25)

            if media_dias_aberta >= 15:
                indice += 15
            elif media_dias_aberta >= 7:
                indice += 8
            elif media_dias_aberta >= 3:
                indice += 4

            indice = max(0, min(100, int(indice)))
            classificacao = DashboardService._classificar_risco(indice)

            radar.append({
                "categoria": item["categoria"],
                "total": total,
                "criticas": criticas,
                "em_aberto": em_aberto,
                "mais_7_dias": mais_7_dias,
                "media_dias_aberta": media_dias_aberta,
                "indice": indice,
                "classe": classificacao["classe"],
                "icone": classificacao["icone"],
                "nivel": classificacao["nivel"]
            })

        return sorted(radar, key=lambda item: item["indice"], reverse=True)

    @staticmethod
    def _classificar_risco(indice):
        if indice >= 80:
            return {
                "classe": "alto",
                "icone": "🔴",
                "nivel": "Alto"
            }

        if indice >= 60:
            return {
                "classe": "elevado",
                "icone": "🟠",
                "nivel": "Elevado"
            }

        if indice >= 35:
            return {
                "classe": "moderado",
                "icone": "🟡",
                "nivel": "Moderado"
            }

        return {
            "classe": "baixo",
            "icone": "🟢",
            "nivel": "Baixo"
        }

    @staticmethod
    def _remover_alertas_duplicados(alertas):
        vistos = set()
        alertas_unicos = []

        for alerta in alertas:
            chave = (
                alerta["titulo"],
                alerta["url"]
            )

            if chave in vistos:
                continue

            vistos.add(chave)
            alertas_unicos.append(alerta)

        return alertas_unicos

    @staticmethod
    def _montar_kanban(denuncias, resumo_etapas):
        resumo_por_etapa = {
            item["etapa"]: item
            for item in resumo_etapas
        }

        colunas = []

        for etapa in WorkflowEngine.listar_etapas():
            codigo = etapa["codigo"]

            denuncias_da_etapa = [
                denuncia
                for denuncia in denuncias
                if denuncia["etapa_atual"] == codigo
            ]

            resumo = resumo_por_etapa.get(codigo, {})

            colunas.append({
                "codigo": codigo,
                "nome": etapa["nome"],
                "sla_dias": etapa["sla_dias"],
                "total": resumo.get("total", 0),
                "criticas": resumo.get("criticas", 0) or 0,
                "mais_7_dias": resumo.get("mais_7_dias", 0) or 0,
                "denuncias": denuncias_da_etapa
            })

        return colunas

    @staticmethod
    def _calcular_health_score(
        denuncias_em_aberto,
        denuncias_criticas_em_aberto,
        denuncias_em_analise_mais_7_dias,
        tempo_medio_atendimento_dias,
        percentual_concluidas_mes
    ):
        score = 100

        score -= denuncias_criticas_em_aberto * 12
        score -= denuncias_em_analise_mais_7_dias * 8
        score -= denuncias_em_aberto * 2

        if tempo_medio_atendimento_dias > 15:
            score -= 15
        elif tempo_medio_atendimento_dias > 7:
            score -= 8
        elif tempo_medio_atendimento_dias > 3:
            score -= 3

        if percentual_concluidas_mes < 30:
            score -= 12
        elif percentual_concluidas_mes < 60:
            score -= 7
        elif percentual_concluidas_mes < 80:
            score -= 3

        score = max(0, min(100, int(score)))

        status = DashboardService._classificar_health_score(score)

        return {
            "score": score,
            "status": status["status"],
            "icone": status["icone"],
            "classe": status["classe"],
            "descricao": status["descricao"],
            "indicadores": {
                "denuncias_em_aberto": denuncias_em_aberto,
                "denuncias_criticas_em_aberto": denuncias_criticas_em_aberto,
                "denuncias_em_analise_mais_7_dias": denuncias_em_analise_mais_7_dias,
                "tempo_medio_atendimento_dias": tempo_medio_atendimento_dias,
                "percentual_concluidas_mes": percentual_concluidas_mes
            }
        }

    @staticmethod
    def _classificar_health_score(score):
        if score >= 85:
            return {
                "status": "Excelente",
                "icone": "🟢",
                "classe": "excelente",
                "descricao": "A gestão está saudável, com baixo nível de pendências relevantes."
            }

        if score >= 70:
            return {
                "status": "Boa",
                "icone": "🟡",
                "classe": "boa",
                "descricao": "A gestão está controlada, mas existem pontos que merecem acompanhamento."
            }

        if score >= 50:
            return {
                "status": "Atenção",
                "icone": "🟠",
                "classe": "atencao",
                "descricao": "Existem pendências importantes que podem comprometer a resposta da empresa."
            }

        return {
            "status": "Crítica",
            "icone": "🔴",
            "classe": "critica",
            "descricao": "A gestão exige ação imediata para reduzir riscos e atrasos."
        }

    @staticmethod
    def _gerar_insights(total_denuncias, denuncias_novas, denuncias_criticas):
        insights = [
            f"📊 Total de denúncias registradas: {total_denuncias}."
        ]

        if denuncias_criticas > 0:
            insights.append(
                f"🔴 Existem {denuncias_criticas} denúncias críticas que merecem prioridade de análise."
            )
        else:
            insights.append(
                "🟢 Não existem denúncias críticas pendentes no momento."
            )

        if denuncias_novas > 0:
            insights.append(
                f"🟦 Existem {denuncias_novas} novas denúncias aguardando triagem inicial."
            )
        else:
            insights.append(
                "🟢 Não há novas denúncias aguardando triagem."
            )

        return insights

    @staticmethod
    def _gerar_pendencias(
        denuncias_criticas,
        denuncias_em_analise_mais_7_dias,
        denuncias_concluidas_mes
    ):
        return [
            {
                "tipo": "critica",
                "icone": "🔴",
                "titulo": "Denúncias críticas",
                "descricao": f"{denuncias_criticas} denúncia(s) crítica(s) merecem prioridade de análise.",
                "total": denuncias_criticas
            },
            {
                "tipo": "analise",
                "icone": "🟡",
                "titulo": "Em análise há mais de 7 dias",
                "descricao": f"{denuncias_em_analise_mais_7_dias} denúncia(s) estão há mais de 7 dias em análise.",
                "total": denuncias_em_analise_mais_7_dias
            },
            {
                "tipo": "concluidas",
                "icone": "🟢",
                "titulo": "Concluídas neste mês",
                "descricao": f"{denuncias_concluidas_mes} denúncia(s) foram concluídas neste mês.",
                "total": denuncias_concluidas_mes
            }
        ]

    @staticmethod
    def _gerar_acoes_recomendadas(
        denuncias_novas,
        denuncias_criticas,
        denuncias_em_analise_mais_7_dias,
        denuncias_concluidas_mes
    ):
        acoes = []

        if denuncias_criticas > 0:
            acoes.append({
                "prioridade": "alta",
                "icone": "🔴",
                "titulo": "Priorizar denúncias críticas",
                "descricao": f"Analise primeiro as {denuncias_criticas} denúncia(s) crítica(s) pendente(s)."
            })

        if denuncias_em_analise_mais_7_dias > 0:
            acoes.append({
                "prioridade": "media",
                "icone": "🟡",
                "titulo": "Revisar denúncias paradas",
                "descricao": f"Existem {denuncias_em_analise_mais_7_dias} denúncia(s) em análise há mais de 7 dias."
            })

        if denuncias_novas > 0:
            acoes.append({
                "prioridade": "media",
                "icone": "🟦",
                "titulo": "Realizar triagem inicial",
                "descricao": f"Faça a triagem de {denuncias_novas} nova(s) denúncia(s) aguardando tratamento."
            })

        if denuncias_concluidas_mes == 0:
            acoes.append({
                "prioridade": "baixa",
                "icone": "⚪",
                "titulo": "Acompanhar encerramentos",
                "descricao": "Nenhuma denúncia foi concluída neste mês. Verifique possíveis gargalos no fluxo."
            })

        if not acoes:
            acoes.append({
                "prioridade": "normal",
                "icone": "🟢",
                "titulo": "Nenhuma ação crítica para hoje",
                "descricao": "O cenário atual não apresenta pendências relevantes no momento."
            })

        return acoes