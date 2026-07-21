from datetime import date, datetime
from typing import Any

from falae.repositories.relatorio_repository import (
    RelatorioRepository
)
from falae.services.context_service import ContextService


class RelatorioPsicossocialService:
    """
    Processamento dos indicadores utilizados no:

    Relatório Técnico de Apoio à Gestão de Riscos Psicossociais.

    Este Service não realiza diagnóstico clínico, psicológico,
    ocupacional ou organizacional.

    Os resultados possuem caráter estatístico, gerencial e indicativo,
    devendo ser analisados por profissionais responsáveis pelo SESMT,
    RH, PGR e demais áreas competentes.
    """

    VERSAO_METODOLOGIA = "1.0"

    PESOS_CRITICIDADE = {
        "alta": 3,
        "média": 2,
        "media": 2,
        "baixa": 1
    }

    FAIXAS_INDICE = [
        {
            "minimo": 0,
            "maximo": 24.99,
            "nivel": "Muito baixo",
            "classe": "muito-baixo"
        },
        {
            "minimo": 25,
            "maximo": 49.99,
            "nivel": "Baixo",
            "classe": "baixo"
        },
        {
            "minimo": 50,
            "maximo": 69.99,
            "nivel": "Moderado",
            "classe": "moderado"
        },
        {
            "minimo": 70,
            "maximo": 84.99,
            "nivel": "Elevado",
            "classe": "elevado"
        },
        {
            "minimo": 85,
            "maximo": 100,
            "nivel": "Crítico",
            "classe": "critico"
        }
    ]

    @staticmethod
    def _obter_empresa_id() -> int:
        empresa_id = ContextService.empresa()

        if not empresa_id:
            raise ValueError(
                "Nenhuma empresa ativa foi identificada."
            )

        return int(
            empresa_id
        )

    @staticmethod
    def _normalizar_data(
        valor: str | date | datetime | None
    ) -> str | None:
        if valor is None:
            return None

        if isinstance(valor, datetime):
            return valor.strftime(
                "%Y-%m-%d"
            )

        if isinstance(valor, date):
            return valor.strftime(
                "%Y-%m-%d"
            )

        valor_normalizado = str(
            valor
        ).strip()

        if not valor_normalizado:
            return None

        try:
            data_convertida = datetime.strptime(
                valor_normalizado,
                "%Y-%m-%d"
            )

        except ValueError as exc:
            raise ValueError(
                "A data informada é inválida. "
                "Utilize o formato AAAA-MM-DD."
            ) from exc

        return data_convertida.strftime(
            "%Y-%m-%d"
        )

    @classmethod
    def _normalizar_filtros(
        cls,
        filtros: dict[str, Any] | None
    ) -> dict[str, Any]:
        filtros_recebidos = filtros or {}

        data_inicio = cls._normalizar_data(
            filtros_recebidos.get(
                "data_inicio"
            )
        )

        data_fim = cls._normalizar_data(
            filtros_recebidos.get(
                "data_fim"
            )
        )

        if (
            data_inicio
            and data_fim
            and data_inicio > data_fim
        ):
            raise ValueError(
                "A data inicial não pode ser maior "
                "que a data final."
            )

        return {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "unidade_id": cls._normalizar_id(
                filtros_recebidos.get(
                    "unidade_id"
                )
            ),
            "setor_id": cls._normalizar_id(
                filtros_recebidos.get(
                    "setor_id"
                )
            ),
            "turno_id": cls._normalizar_id(
                filtros_recebidos.get(
                    "turno_id"
                )
            )
        }

    @staticmethod
    def _normalizar_id(
        valor: Any
    ) -> int | None:
        if valor in (
            None,
            ""
        ):
            return None

        try:
            valor_convertido = int(
                valor
            )

        except (
            TypeError,
            ValueError
        ) as exc:
            raise ValueError(
                "Um dos filtros selecionados é inválido."
            ) from exc

        if valor_convertido <= 0:
            raise ValueError(
                "Um dos filtros selecionados é inválido."
            )

        return valor_convertido

    @staticmethod
    def _numero(
        valor: Any
    ) -> float:
        if valor in (
            None,
            ""
        ):
            return 0.0

        try:
            return float(
                valor
            )

        except (
            TypeError,
            ValueError
        ):
            return 0.0

    @staticmethod
    def _inteiro(
        valor: Any
    ) -> int:
        return int(
            RelatorioPsicossocialService._numero(
                valor
            )
        )

    @staticmethod
    def _percentual(
        quantidade: Any,
        total: Any,
        casas: int = 2
    ) -> float:
        quantidade_numero = (
            RelatorioPsicossocialService._numero(
                quantidade
            )
        )

        total_numero = (
            RelatorioPsicossocialService._numero(
                total
            )
        )

        if total_numero <= 0:
            return 0.0

        return round(
            (
                quantidade_numero
                / total_numero
            )
            * 100,
            casas
        )

    @classmethod
    def _adicionar_percentuais(
        cls,
        itens: list[dict[str, Any]],
        total_geral: int
    ) -> list[dict[str, Any]]:
        resultado = []

        for item in itens:
            item_processado = dict(
                item
            )

            item_processado["total"] = (
                cls._inteiro(
                    item_processado.get(
                        "total"
                    )
                )
            )

            item_processado["percentual"] = (
                cls._percentual(
                    item_processado["total"],
                    total_geral
                )
            )

            if "criticas" in item_processado:
                item_processado["criticas"] = (
                    cls._inteiro(
                        item_processado.get(
                            "criticas"
                        )
                    )
                )

                item_processado[
                    "percentual_criticas"
                ] = cls._percentual(
                    item_processado["criticas"],
                    item_processado["total"]
                )

            if "em_aberto" in item_processado:
                item_processado["em_aberto"] = (
                    cls._inteiro(
                        item_processado.get(
                            "em_aberto"
                        )
                    )
                )

                item_processado[
                    "percentual_em_aberto"
                ] = cls._percentual(
                    item_processado["em_aberto"],
                    item_processado["total"]
                )

            resultado.append(
                item_processado
            )

        return resultado

    @classmethod
    def _processar_criticidades(
        cls,
        itens: list[dict[str, Any]],
        total_geral: int
    ) -> dict[str, Any]:
        distribuicao = []
        soma_pontos = 0
        total_classificado = 0

        for item in itens:
            criticidade = str(
                item.get(
                    "criticidade"
                )
                or "Não informada"
            ).strip()

            total = cls._inteiro(
                item.get(
                    "total"
                )
            )

            chave = criticidade.lower()

            peso = cls.PESOS_CRITICIDADE.get(
                chave,
                0
            )

            pontos = (
                total
                * peso
            )

            if peso > 0:
                total_classificado += total
                soma_pontos += pontos

            distribuicao.append({
                "criticidade": criticidade,
                "total": total,
                "percentual": cls._percentual(
                    total,
                    total_geral
                ),
                "peso": peso,
                "pontos": pontos
            })

        media_ponderada = 0.0

        if total_classificado > 0:
            media_ponderada = round(
                soma_pontos
                / total_classificado,
                2
            )

        indice_gravidade = 0.0

        if media_ponderada > 0:
            indice_gravidade = round(
                (
                    (
                        media_ponderada
                        - 1
                    )
                    / 2
                )
                * 100,
                2
            )

            indice_gravidade = max(
                0.0,
                min(
                    100.0,
                    indice_gravidade
                )
            )

        return {
            "distribuicao": distribuicao,
            "total_classificado": total_classificado,
            "total_nao_classificado": max(
                total_geral
                - total_classificado,
                0
            ),
            "soma_pontos": soma_pontos,
            "media_ponderada": media_ponderada,
            "indice_gravidade": indice_gravidade,
            "formula_media": (
                "Σ (quantidade por criticidade × peso) "
                "÷ total de denúncias classificadas"
            ),
            "formula_indice": (
                "((média ponderada − 1) ÷ 2) × 100"
            )
        }

    @classmethod
    def _processar_evolucao(
        cls,
        itens: list[dict[str, Any]]
    ) -> dict[str, Any]:
        evolucao = []

        for item in itens:
            evolucao.append({
                "competencia": item.get(
                    "competencia"
                ),
                "ano": cls._inteiro(
                    item.get(
                        "ano"
                    )
                ),
                "mes": cls._inteiro(
                    item.get(
                        "mes"
                    )
                ),
                "total": cls._inteiro(
                    item.get(
                        "total"
                    )
                ),
                "criticas": cls._inteiro(
                    item.get(
                        "criticas"
                    )
                ),
                "encerradas": cls._inteiro(
                    item.get(
                        "encerradas"
                    )
                )
            })

        if len(
            evolucao
        ) < 2:
            return {
                "itens": evolucao,
                "variacao_percentual": 0.0,
                "classificacao": "Sem base comparativa",
                "periodo_anterior": None,
                "periodo_atual": (
                    evolucao[-1]
                    if evolucao
                    else None
                ),
                "formula": (
                    "((valor atual − valor anterior) "
                    "÷ valor anterior) × 100"
                )
            }

        periodo_anterior = evolucao[-2]
        periodo_atual = evolucao[-1]

        valor_anterior = periodo_anterior[
            "total"
        ]

        valor_atual = periodo_atual[
            "total"
        ]

        if valor_anterior <= 0:
            if valor_atual > 0:
                variacao = 100.0
                classificacao = (
                    "Aumento sem base anterior"
                )

            else:
                variacao = 0.0
                classificacao = "Estável"

        else:
            variacao = round(
                (
                    (
                        valor_atual
                        - valor_anterior
                    )
                    / valor_anterior
                )
                * 100,
                2
            )

            if variacao > 10:
                classificacao = "Crescente"

            elif variacao < -10:
                classificacao = "Decrescente"

            else:
                classificacao = "Estável"

        return {
            "itens": evolucao,
            "variacao_percentual": variacao,
            "classificacao": classificacao,
            "periodo_anterior": periodo_anterior,
            "periodo_atual": periodo_atual,
            "formula": (
                "((valor atual − valor anterior) "
                "÷ valor anterior) × 100"
            )
        }

    @classmethod
    def _obter_maior_concentracao(
        cls,
        itens: list[dict[str, Any]],
        campo_nome: str,
        total_geral: int
    ) -> dict[str, Any] | None:
        if not itens or total_geral <= 0:
            return None

        item_maior = max(
            itens,
            key=lambda item: cls._inteiro(
                item.get(
                    "total"
                )
            )
        )

        total_item = cls._inteiro(
            item_maior.get(
                "total"
            )
        )

        return {
            "nome": item_maior.get(
                campo_nome
            )
            or "Não informado",
            "total": total_item,
            "percentual": cls._percentual(
                total_item,
                total_geral
            )
        }

    @classmethod
    def _processar_concentracoes_cruzadas(
        cls,
        itens: list[dict[str, Any]],
        total_geral: int
    ) -> list[dict[str, Any]]:
        resultado = []

        for item in itens:
            total = cls._inteiro(
                item.get(
                    "total"
                )
            )

            percentual = cls._percentual(
                total,
                total_geral
            )

            resultado.append({
                "categoria": item.get(
                    "categoria"
                )
                or "Não informada",
                "unidade": item.get(
                    "unidade"
                )
                or "Não informada",
                "total": total,
                "criticas": cls._inteiro(
                    item.get(
                        "criticas"
                    )
                ),
                "percentual_total": percentual,
                "concentracao_relevante": (
                    percentual >= 20
                )
            })

        return resultado

    @classmethod
    def _processar_indicadores_operacionais(
        cls,
        dados: dict[str, Any]
    ) -> dict[str, Any]:
        total = cls._inteiro(
            dados.get(
                "total"
            )
        )

        em_aberto = cls._inteiro(
            dados.get(
                "em_aberto"
            )
        )

        encerradas = cls._inteiro(
            dados.get(
                "encerradas"
            )
        )

        criticas = cls._inteiro(
            dados.get(
                "criticas"
            )
        )

        criticas_em_aberto = cls._inteiro(
            dados.get(
                "criticas_em_aberto"
            )
        )

        abertas_mais_7_dias = cls._inteiro(
            dados.get(
                "abertas_mais_7_dias"
            )
        )

        return {
            "total": total,
            "em_aberto": em_aberto,
            "encerradas": encerradas,
            "criticas": criticas,
            "criticas_em_aberto": criticas_em_aberto,
            "abertas_mais_7_dias": abertas_mais_7_dias,
            "percentual_em_aberto": cls._percentual(
                em_aberto,
                total
            ),
            "percentual_encerradas": cls._percentual(
                encerradas,
                total
            ),
            "percentual_criticas": cls._percentual(
                criticas,
                total
            ),
            "percentual_criticas_em_aberto": (
                cls._percentual(
                    criticas_em_aberto,
                    total
                )
            ),
            "percentual_abertas_mais_7_dias": (
                cls._percentual(
                    abertas_mais_7_dias,
                    total
                )
            ),
            "tempo_medio_encerramento_dias": round(
                cls._numero(
                    dados.get(
                        "tempo_medio_encerramento_dias"
                    )
                ),
                1
            ),
            "idade_media_abertas_dias": round(
                cls._numero(
                    dados.get(
                        "idade_media_abertas_dias"
                    )
                ),
                1
            )
        }

    @classmethod
    def _processar_planos_acao(
        cls,
        dados: dict[str, Any]
    ) -> dict[str, Any]:
        total = cls._inteiro(
            dados.get(
                "total_planos"
            )
        )

        concluidos = cls._inteiro(
            dados.get(
                "concluidos"
            )
        )

        pendentes = cls._inteiro(
            dados.get(
                "pendentes"
            )
        )

        vencidos = cls._inteiro(
            dados.get(
                "vencidos"
            )
        )

        return {
            "total": total,
            "concluidos": concluidos,
            "pendentes": pendentes,
            "vencidos": vencidos,
            "percentual_concluidos": cls._percentual(
                concluidos,
                total
            ),
            "percentual_pendentes": cls._percentual(
                pendentes,
                total
            ),
            "percentual_vencidos": cls._percentual(
                vencidos,
                total
            )
        }

    @classmethod
    def _calcular_indice_indicativo(
        cls,
        indicadores: dict[str, Any],
        criticidades: dict[str, Any],
        maior_categoria: dict[str, Any] | None,
        maior_unidade: dict[str, Any] | None
    ) -> dict[str, Any]:
        """
        Índice indicativo de atenção psicossocial.

        O índice não mede saúde mental, exposição ocupacional real,
        probabilidade de adoecimento ou conformidade legal.

        Ele resume padrões encontrados nos registros do canal.
        """

        componente_gravidade = round(
            criticidades.get(
                "indice_gravidade",
                0
            )
            * 0.35,
            2
        )

        componente_criticas_abertas = round(
            min(
                indicadores.get(
                    "percentual_criticas_em_aberto",
                    0
                ),
                100
            )
            * 0.25,
            2
        )

        componente_atraso = round(
            min(
                indicadores.get(
                    "percentual_abertas_mais_7_dias",
                    0
                ),
                100
            )
            * 0.20,
            2
        )

        concentracao_categoria = (
            maior_categoria.get(
                "percentual",
                0
            )
            if maior_categoria
            else 0
        )

        concentracao_unidade = (
            maior_unidade.get(
                "percentual",
                0
            )
            if maior_unidade
            else 0
        )

        media_concentracao = (
            (
                concentracao_categoria
                + concentracao_unidade
            )
            / 2
        )

        componente_concentracao = round(
            min(
                media_concentracao,
                100
            )
            * 0.20,
            2
        )

        indice = round(
            componente_gravidade
            + componente_criticas_abertas
            + componente_atraso
            + componente_concentracao,
            2
        )

        indice = max(
            0.0,
            min(
                100.0,
                indice
            )
        )

        classificacao = cls._classificar_indice(
            indice
        )

        return {
            "valor": indice,
            "nivel": classificacao["nivel"],
            "classe": classificacao["classe"],
            "componentes": {
                "gravidade": {
                    "valor_base": criticidades.get(
                        "indice_gravidade",
                        0
                    ),
                    "peso_percentual": 35,
                    "contribuicao": componente_gravidade
                },
                "criticas_em_aberto": {
                    "valor_base": indicadores.get(
                        "percentual_criticas_em_aberto",
                        0
                    ),
                    "peso_percentual": 25,
                    "contribuicao": (
                        componente_criticas_abertas
                    )
                },
                "abertas_mais_7_dias": {
                    "valor_base": indicadores.get(
                        "percentual_abertas_mais_7_dias",
                        0
                    ),
                    "peso_percentual": 20,
                    "contribuicao": componente_atraso
                },
                "concentracao": {
                    "valor_base": round(
                        media_concentracao,
                        2
                    ),
                    "peso_percentual": 20,
                    "contribuicao": (
                        componente_concentracao
                    )
                }
            },
            "formula": (
                "(índice de gravidade × 35%) + "
                "(percentual de denúncias críticas abertas × 25%) + "
                "(percentual de denúncias abertas há mais de 7 dias × 20%) + "
                "(média da concentração por categoria e unidade × 20%)"
            ),
            "observacao": (
                "Indicador gerencial e estatístico baseado "
                "exclusivamente nos registros do canal. "
                "Não representa diagnóstico, laudo ocupacional "
                "ou avaliação clínica."
            )
        }

    @classmethod
    def _classificar_indice(
        cls,
        indice: float
    ) -> dict[str, str]:
        for faixa in cls.FAIXAS_INDICE:
            if (
                faixa["minimo"]
                <= indice
                <= faixa["maximo"]
            ):
                return {
                    "nivel": faixa["nivel"],
                    "classe": faixa["classe"]
                }

        return {
            "nivel": "Não classificado",
            "classe": "nao-classificado"
        }

    @staticmethod
    def _montar_metodologia() -> dict[str, Any]:
        return {
            "versao": (
                RelatorioPsicossocialService
                .VERSAO_METODOLOGIA
            ),
            "titulo": (
                "Metodologia de cálculo dos indicadores"
            ),
            "premissas": [
                (
                    "Foram considerados exclusivamente os "
                    "registros armazenados no Canal de Denúncias "
                    "FALAE dentro do período e dos filtros "
                    "selecionados."
                ),
                (
                    "Os resultados refletem registros realizados "
                    "no canal e não representam, isoladamente, "
                    "a prevalência real de riscos psicossociais "
                    "na organização."
                ),
                (
                    "A ausência ou o baixo número de denúncias "
                    "não comprova ausência de riscos."
                ),
                (
                    "O aumento de registros pode decorrer tanto "
                    "de mudanças no ambiente organizacional quanto "
                    "do aumento da confiança e divulgação do canal."
                ),
                (
                    "Os indicadores devem ser analisados em conjunto "
                    "com outras fontes, como avaliações organizacionais, "
                    "entrevistas, observações, dados de absenteísmo, "
                    "turnover e informações do PGR."
                )
            ],
            "calculos": [
                {
                    "nome": "Percentual de participação",
                    "formula": (
                        "(quantidade do grupo ÷ total de denúncias) × 100"
                    ),
                    "exemplo": (
                        "Se 10 de 40 denúncias pertencem a uma categoria: "
                        "(10 ÷ 40) × 100 = 25%."
                    )
                },
                {
                    "nome": "Média ponderada de criticidade",
                    "formula": (
                        "Σ (quantidade × peso) ÷ total classificado"
                    ),
                    "criterios": [
                        "Alta = 3 pontos",
                        "Média = 2 pontos",
                        "Baixa = 1 ponto"
                    ]
                },
                {
                    "nome": "Índice normalizado de gravidade",
                    "formula": (
                        "((média ponderada − 1) ÷ 2) × 100"
                    ),
                    "explicacao": (
                        "Converte a média de criticidade, originalmente "
                        "com valores entre 1 e 3, para uma escala "
                        "entre 0 e 100."
                    )
                },
                {
                    "nome": "Variação mensal",
                    "formula": (
                        "((valor atual − valor anterior) "
                        "÷ valor anterior) × 100"
                    ),
                    "explicacao": (
                        "Compara o total do último mês disponível "
                        "com o mês imediatamente anterior."
                    )
                },
                {
                    "nome": (
                        "Índice indicativo de atenção psicossocial"
                    ),
                    "formula": (
                        "(gravidade × 35%) + "
                        "(críticas abertas × 25%) + "
                        "(abertas há mais de 7 dias × 20%) + "
                        "(concentração × 20%)"
                    ),
                    "explicacao": (
                        "Índice gerencial próprio do FALAE para "
                        "resumir padrões existentes nos registros. "
                        "Não constitui diagnóstico ou avaliação "
                        "técnica substitutiva."
                    )
                }
            ],
            "faixas_indice": (
                RelatorioPsicossocialService
                .FAIXAS_INDICE
            )
        }

    @classmethod
    def preparar_filtros(cls) -> dict[str, Any]:
        empresa_id = cls._obter_empresa_id()

        repo = RelatorioRepository()

        try:
            return {
                "unidades": repo.listar_unidades_filtro(
                    empresa_id
                ),
                "setores": repo.listar_setores_filtro(
                    empresa_id
                ),
                "turnos": repo.listar_turnos_filtro(
                    empresa_id
                )
            }

        finally:
            repo.close()

    @classmethod
    def gerar_dados(
        cls,
        filtros: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        empresa_id = cls._obter_empresa_id()

        filtros_normalizados = (
            cls._normalizar_filtros(
                filtros
            )
        )

        parametros = {
            "empresa_id": empresa_id,
            **filtros_normalizados
        }

        repo = RelatorioRepository()

        try:
            empresa = repo.obter_empresa(
                empresa_id
            )

            if not empresa:
                raise ValueError(
                    "A empresa ativa não foi encontrada."
                )

            total_denuncias = (
                repo.total_denuncias(
                    **parametros
                )
            )

            status_dados = repo.resumo_status(
                **parametros
            )

            criticidade_dados = (
                repo.distribuicao_criticidade(
                    **parametros
                )
            )

            categoria_dados = (
                repo.distribuicao_categorias(
                    **parametros
                )
            )

            unidade_dados = (
                repo.distribuicao_unidades(
                    **parametros
                )
            )

            setor_dados = (
                repo.distribuicao_setores(
                    **parametros
                )
            )

            turno_dados = (
                repo.distribuicao_turnos(
                    **parametros
                )
            )

            evolucao_dados = (
                repo.evolucao_mensal(
                    **parametros
                )
            )

            indicadores_dados = (
                repo.indicadores_operacionais(
                    **parametros
                )
            )

            concentracoes_dados = (
                repo.concentracao_categoria_unidade(
                    **parametros
                )
            )

            planos_dados = (
                repo.resumo_planos_acao(
                    **parametros
                )
            )

        finally:
            repo.close()

        status = cls._adicionar_percentuais(
            status_dados,
            total_denuncias
        )

        criticidades = cls._processar_criticidades(
            criticidade_dados,
            total_denuncias
        )

        categorias = cls._adicionar_percentuais(
            categoria_dados,
            total_denuncias
        )

        unidades = cls._adicionar_percentuais(
            unidade_dados,
            total_denuncias
        )

        setores = cls._adicionar_percentuais(
            setor_dados,
            total_denuncias
        )

        turnos = cls._adicionar_percentuais(
            turno_dados,
            total_denuncias
        )

        evolucao = cls._processar_evolucao(
            evolucao_dados
        )

        indicadores = (
            cls._processar_indicadores_operacionais(
                indicadores_dados
            )
        )

        planos_acao = cls._processar_planos_acao(
            planos_dados
        )

        maior_categoria = (
            cls._obter_maior_concentracao(
                categorias,
                "categoria",
                total_denuncias
            )
        )

        maior_unidade = (
            cls._obter_maior_concentracao(
                unidades,
                "unidade",
                total_denuncias
            )
        )

        maior_setor = (
            cls._obter_maior_concentracao(
                setores,
                "setor",
                total_denuncias
            )
        )

        maior_turno = (
            cls._obter_maior_concentracao(
                turnos,
                "turno",
                total_denuncias
            )
        )

        concentracoes_cruzadas = (
            cls._processar_concentracoes_cruzadas(
                concentracoes_dados,
                total_denuncias
            )
        )

        indice_indicativo = (
            cls._calcular_indice_indicativo(
                indicadores=indicadores,
                criticidades=criticidades,
                maior_categoria=maior_categoria,
                maior_unidade=maior_unidade
            )
        )

        data_emissao = datetime.now()

        return {
            "titulo": (
                "Relatório Técnico de Apoio à Gestão "
                "de Riscos Psicossociais"
            ),
            "subtitulo": (
                "Indicadores gerenciais obtidos a partir "
                "do Canal de Denúncias FALAE"
            ),
            "versao_metodologia": (
                cls.VERSAO_METODOLOGIA
            ),
            "data_emissao": data_emissao,
            "data_emissao_formatada": (
                data_emissao.strftime(
                    "%d/%m/%Y às %H:%M"
                )
            ),
            "empresa": empresa,
            "filtros": filtros_normalizados,
            "periodo": cls._montar_periodo(
                filtros_normalizados
            ),
            "total_denuncias": total_denuncias,
            "indicadores": indicadores,
            "status": status,
            "criticidades": criticidades,
            "categorias": categorias,
            "unidades": unidades,
            "setores": setores,
            "turnos": turnos,
            "evolucao": evolucao,
            "planos_acao": planos_acao,
            "concentracoes": {
                "maior_categoria": maior_categoria,
                "maior_unidade": maior_unidade,
                "maior_setor": maior_setor,
                "maior_turno": maior_turno,
                "categoria_unidade": (
                    concentracoes_cruzadas
                )
            },
            "indice_indicativo": indice_indicativo,
            "metodologia": cls._montar_metodologia(),
            "avisos": cls._montar_avisos(
                total_denuncias
            )
        }

    @staticmethod
    def _montar_periodo(
        filtros: dict[str, Any]
    ) -> dict[str, str | None]:
        data_inicio = filtros.get(
            "data_inicio"
        )

        data_fim = filtros.get(
            "data_fim"
        )

        return {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "data_inicio_formatada": (
                datetime.strptime(
                    data_inicio,
                    "%Y-%m-%d"
                ).strftime(
                    "%d/%m/%Y"
                )
                if data_inicio
                else None
            ),
            "data_fim_formatada": (
                datetime.strptime(
                    data_fim,
                    "%Y-%m-%d"
                ).strftime(
                    "%d/%m/%Y"
                )
                if data_fim
                else None
            ),
            "descricao": (
                RelatorioPsicossocialService
                ._descricao_periodo(
                    data_inicio,
                    data_fim
                )
            )
        }

    @staticmethod
    def _descricao_periodo(
        data_inicio: str | None,
        data_fim: str | None
    ) -> str:
        if data_inicio and data_fim:
            inicio = datetime.strptime(
                data_inicio,
                "%Y-%m-%d"
            ).strftime(
                "%d/%m/%Y"
            )

            fim = datetime.strptime(
                data_fim,
                "%Y-%m-%d"
            ).strftime(
                "%d/%m/%Y"
            )

            return (
                f"De {inicio} até {fim}"
            )

        if data_inicio:
            inicio = datetime.strptime(
                data_inicio,
                "%Y-%m-%d"
            ).strftime(
                "%d/%m/%Y"
            )

            return (
                f"A partir de {inicio}"
            )

        if data_fim:
            fim = datetime.strptime(
                data_fim,
                "%Y-%m-%d"
            ).strftime(
                "%d/%m/%Y"
            )

            return (
                f"Até {fim}"
            )

        return (
            "Todo o período disponível"
        )

    @staticmethod
    def _montar_avisos(
        total_denuncias: int
    ) -> list[str]:
        avisos = [
            (
                "Este relatório possui finalidade gerencial "
                "e de apoio à tomada de decisão."
            ),
            (
                "Os resultados não substituem avaliações técnicas, "
                "laudos, perícias, diagnósticos ou pareceres emitidos "
                "por profissionais legalmente habilitados."
            ),
            (
                "Os indicadores devem ser interpretados juntamente "
                "com outras evidências organizacionais e ocupacionais."
            )
        ]

        if total_denuncias == 0:
            avisos.append(
                "Não foram encontradas denúncias para os filtros "
                "selecionados. A ausência de registros não comprova "
                "ausência de fatores de risco psicossociais."
            )

        elif total_denuncias < 5:
            avisos.append(
                "A quantidade reduzida de registros limita a "
                "representatividade estatística dos indicadores."
            )

        return avisos

