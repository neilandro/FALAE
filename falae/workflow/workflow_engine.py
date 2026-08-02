from datetime import datetime, timedelta


class WorkflowEngine:

    ETAPAS = [
        {
            "ordem": 1,
            "codigo": "TRIAGEM",
            "nome": "Triagem",
            "sla_dias": 1
        },
        {
            "ordem": 2,
            "codigo": "INVESTIGACAO",
            "nome": "Investigação",
            "sla_dias": 5
        },
        {
            "ordem": 3,
            "codigo": "EVIDENCIAS",
            "nome": "Coleta de Evidências",
            "sla_dias": 3
        },
        {
            "ordem": 4,
            "codigo": "PARECER",
            "nome": "Parecer",
            "sla_dias": 2
        },
        {
            "ordem": 5,
            "codigo": "PLANO_ACAO",
            "nome": "Plano de Ação",
            "sla_dias": 7
        },
        {
            "ordem": 6,
            "codigo": "VALIDACAO",
            "nome": "Validação",
            "sla_dias": 2
        },
        {
            "ordem": 7,
            "codigo": "ENCERRAMENTO",
            "nome": "Encerramento",
            "sla_dias": 1
        }
    ]

    ETAPAS_POR_CODIGO = {
        etapa["codigo"]: etapa
        for etapa in ETAPAS
    }

    @classmethod
    def listar_etapas(cls):
        return [
            etapa.copy()
            for etapa in cls.ETAPAS
        ]

    @classmethod
    def obter_etapa(cls, codigo):
        if not isinstance(codigo, str):
            return None

        codigo_normalizado = codigo.strip().upper()

        etapa = cls.ETAPAS_POR_CODIGO.get(codigo_normalizado)

        return etapa.copy() if etapa else None

    @classmethod
    def primeira_etapa(cls):
        return cls.ETAPAS[0].copy()

    @classmethod
    def ultima_etapa(cls):
        return cls.ETAPAS[-1].copy()

    @classmethod
    def proxima_etapa(cls, codigo_atual):
        etapa_atual = cls.obter_etapa(codigo_atual)

        if not etapa_atual:
            return None

        proxima_ordem = etapa_atual["ordem"] + 1

        for etapa in cls.ETAPAS:
            if etapa["ordem"] == proxima_ordem:
                return etapa.copy()

        return None

    @classmethod
    def etapa_anterior(cls, codigo_atual):
        etapa_atual = cls.obter_etapa(codigo_atual)

        if not etapa_atual:
            return None

        ordem_anterior = etapa_atual["ordem"] - 1

        for etapa in cls.ETAPAS:
            if etapa["ordem"] == ordem_anterior:
                return etapa.copy()

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
        if prazo_limite is None:
            return False

        if not isinstance(prazo_limite, datetime):
            raise ValueError(
                "O prazo limite deve ser uma data e hora válida."
            )

        return datetime.now() > prazo_limite

    @classmethod
    def calcular_percentual_conclusao(cls, codigo_etapa_atual):
        etapa = cls.obter_etapa(codigo_etapa_atual)

        if not etapa:
            return 0

        total_etapas = len(cls.ETAPAS)

        return round(
            (etapa["ordem"] / total_etapas) * 100
        )

    @classmethod
    def preparar_inicio_etapa(
        cls,
        codigo_etapa,
        responsavel_id=None,
        observacao=None
    ):
        etapa = cls.obter_etapa(codigo_etapa)

        if not etapa:
            return None

        iniciado_em = datetime.now()

        return {
            "etapa": etapa["codigo"],
            "status_etapa": "EM_ANDAMENTO",
            "responsavel_id": responsavel_id,
            "prazo_limite": cls.calcular_prazo_limite(
                etapa["codigo"],
                data_base=iniciado_em
            ),
            "iniciado_em": iniciado_em,
            "concluido_em": None,
            "observacao": observacao
        }

    @classmethod
    def preparar_investigacao_pos_triagem(
        cls,
        responsavel_id=None,
        observacao=None
    ):
        return cls.preparar_inicio_etapa(
            codigo_etapa="INVESTIGACAO",
            responsavel_id=responsavel_id,
            observacao=observacao
        )

    @classmethod
    def definir_status_por_etapa(cls, codigo_etapa):
        if not isinstance(codigo_etapa, str):
            return None

        codigo_normalizado = codigo_etapa.strip().upper()

        if codigo_normalizado == "TRIAGEM":
            return "NOVA"

        if codigo_normalizado in {
            "INVESTIGACAO",
            "EVIDENCIAS",
            "PARECER",
            "PLANO_ACAO",
            "VALIDACAO"
        }:
            return "EM_ANALISE"

        if codigo_normalizado == "ENCERRAMENTO":
            return "CONCLUIDA"

        if codigo_normalizado == "ARQUIVADA":
            return "ARQUIVADA"

        return None

    @classmethod
    def montar_linha_do_tempo(cls, etapa_atual):
        linha_do_tempo = []

        codigo_atual = (
            etapa_atual.strip().upper()
            if isinstance(etapa_atual, str)
            else ""
        )

        arquivada = codigo_atual == "ARQUIVADA"

        etapa_atual_obj = cls.obter_etapa(codigo_atual)

        if arquivada:
            ordem_atual = None
        elif etapa_atual_obj:
            ordem_atual = etapa_atual_obj["ordem"]
        else:
            ordem_atual = cls.primeira_etapa()["ordem"]

        for etapa in cls.ETAPAS:
            if arquivada:
                status_visual = "arquivada"
            elif etapa["ordem"] < ordem_atual:
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
        codigo_atual = (
            codigo_etapa_atual.strip().upper()
            if isinstance(codigo_etapa_atual, str)
            else ""
        )

        if codigo_atual == "ARQUIVADA":
            return {
                "codigo": "ARQUIVADA",
                "nome": "Arquivada",
                "sla_dias": None,
                "percentual_conclusao": 100,
                "proxima_etapa": None
            }

        etapa = cls.obter_etapa(codigo_atual)

        if not etapa:
            etapa = cls.primeira_etapa()

        proxima = cls.proxima_etapa(etapa["codigo"])

        return {
            "codigo": etapa["codigo"],
            "nome": etapa["nome"],
            "sla_dias": etapa["sla_dias"],
            "percentual_conclusao": (
                cls.calcular_percentual_conclusao(
                    etapa["codigo"]
                )
            ),
            "proxima_etapa": (
                proxima["nome"]
                if proxima
                else None
            )
        }