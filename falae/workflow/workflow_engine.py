from datetime import datetime, timedelta


class WorkflowEngine:

    ETAPAS = [
        {"ordem": 1, "codigo": "TRIAGEM", "nome": "Triagem", "sla_dias": 1},
        {"ordem": 2, "codigo": "INVESTIGACAO", "nome": "Investigação", "sla_dias": 5},
        {"ordem": 3, "codigo": "EVIDENCIAS", "nome": "Coleta de Evidências", "sla_dias": 3},
        {"ordem": 4, "codigo": "PARECER", "nome": "Parecer", "sla_dias": 2},
        {"ordem": 5, "codigo": "PLANO_ACAO", "nome": "Plano de Ação", "sla_dias": 7},
        {"ordem": 6, "codigo": "VALIDACAO", "nome": "Validação", "sla_dias": 2},
        {"ordem": 7, "codigo": "ENCERRAMENTO", "nome": "Encerramento", "sla_dias": 1}
    ]

    @classmethod
    def listar_etapas(cls):
        return cls.ETAPAS

    @classmethod
    def obter_etapa(cls, codigo):
        for etapa in cls.ETAPAS:
            if etapa["codigo"] == codigo:
                return etapa
        return None

    @classmethod
    def primeira_etapa(cls):
        return cls.ETAPAS[0]

    @classmethod
    def ultima_etapa(cls):
        return cls.ETAPAS[-1]

    @classmethod
    def proxima_etapa(cls, codigo_atual):
        etapa_atual = cls.obter_etapa(codigo_atual)

        if not etapa_atual:
            return cls.primeira_etapa()

        proxima_ordem = etapa_atual["ordem"] + 1

        for etapa in cls.ETAPAS:
            if etapa["ordem"] == proxima_ordem:
                return etapa

        return None

    @classmethod
    def etapa_anterior(cls, codigo_atual):
        etapa_atual = cls.obter_etapa(codigo_atual)

        if not etapa_atual:
            return None

        ordem_anterior = etapa_atual["ordem"] - 1

        for etapa in cls.ETAPAS:
            if etapa["ordem"] == ordem_anterior:
                return etapa

        return None

    @classmethod
    def calcular_prazo_limite(cls, codigo_etapa, data_base=None):
        etapa = cls.obter_etapa(codigo_etapa)

        if not etapa:
            return None

        if data_base is None:
            data_base = datetime.now()

        return data_base + timedelta(days=etapa["sla_dias"])

    @classmethod
    def esta_atrasada(cls, prazo_limite):
        if not prazo_limite:
            return False

        return datetime.now() > prazo_limite

    @classmethod
    def calcular_percentual_conclusao(cls, codigo_etapa_atual):
        etapa = cls.obter_etapa(codigo_etapa_atual)

        if not etapa:
            return 0

        total_etapas = len(cls.ETAPAS)

        return round((etapa["ordem"] / total_etapas) * 100)

    @classmethod
    def preparar_inicio_etapa(cls, codigo_etapa, responsavel_id=None, observacao=None):
        etapa = cls.obter_etapa(codigo_etapa)

        if not etapa:
            return None

        return {
            "etapa": etapa["codigo"],
            "status_etapa": "EM_ANDAMENTO",
            "responsavel_id": responsavel_id,
            "prazo_limite": cls.calcular_prazo_limite(etapa["codigo"]),
            "iniciado_em": datetime.now(),
            "concluido_em": None,
            "observacao": observacao
        }

    @classmethod
    def preparar_investigacao_pos_triagem(cls, responsavel_id=None, observacao=None):
        return cls.preparar_inicio_etapa(
            codigo_etapa="INVESTIGACAO",
            responsavel_id=responsavel_id,
            observacao=observacao
        )

    @classmethod
    def definir_status_por_etapa(cls, codigo_etapa):
        if codigo_etapa == "TRIAGEM":
            return "NOVA"

        if codigo_etapa in [
            "INVESTIGACAO",
            "EVIDENCIAS",
            "PARECER",
            "PLANO_ACAO",
            "VALIDACAO"
        ]:
            return "EM_ANALISE"

        if codigo_etapa == "ENCERRAMENTO":
            return "CONCLUIDA"

        if codigo_etapa == "ARQUIVADA":
            return "ARQUIVADA"

        return "EM_ANALISE"

    @classmethod
    def montar_linha_do_tempo(cls, etapa_atual):
        linha_do_tempo = []

        etapa_atual_obj = cls.obter_etapa(etapa_atual)

        if not etapa_atual_obj:
            etapa_atual_obj = cls.primeira_etapa()

        ordem_atual = etapa_atual_obj["ordem"]

        for etapa in cls.ETAPAS:
            if etapa["ordem"] < ordem_atual:
                status_visual = "concluida"
            elif etapa["ordem"] == ordem_atual:
                status_visual = "atual"
            else:
                status_visual = "pendente"

            linha_do_tempo.append({
                "ordem": etapa["ordem"],
                "codigo": etapa["codigo"],
                "nome": etapa["nome"],
                "sla_dias": etapa["sla_dias"],
                "status_visual": status_visual
            })

        return linha_do_tempo

    @classmethod
    def resumo_etapa_atual(cls, codigo_etapa_atual):
        etapa = cls.obter_etapa(codigo_etapa_atual)

        if not etapa:
            etapa = cls.primeira_etapa()

        proxima = cls.proxima_etapa(etapa["codigo"])

        return {
            "codigo": etapa["codigo"],
            "nome": etapa["nome"],
            "sla_dias": etapa["sla_dias"],
            "percentual_conclusao": cls.calcular_percentual_conclusao(etapa["codigo"]),
            "proxima_etapa": proxima["nome"] if proxima else None
        }