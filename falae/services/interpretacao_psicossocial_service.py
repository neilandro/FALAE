from typing import Any


class InterpretacaoPsicossocialService:
    """
    Gera interpretações automáticas com base em regras transparentes.

    Este Service não realiza diagnóstico clínico, psicológico,
    ocupacional ou organizacional.

    Os textos produzidos possuem finalidade gerencial e servem
    como apoio à análise dos profissionais responsáveis.
    """

    LIMITE_CONCENTRACAO_MODERADA = 30
    LIMITE_CONCENTRACAO_RELEVANTE = 40
    LIMITE_CONCENTRACAO_ELEVADA = 60

    LIMITE_CRITICAS_ATENCAO = 20
    LIMITE_CRITICAS_PRIORITARIO = 30

    LIMITE_ABERTAS_ATENCAO = 40
    LIMITE_ABERTAS_ELEVADO = 60

    LIMITE_ATRASADAS_ATENCAO = 20
    LIMITE_ATRASADAS_ELEVADO = 40

    LIMITE_PLANOS_VENCIDOS_ATENCAO = 15
    LIMITE_PLANOS_VENCIDOS_ELEVADO = 30

    LIMITE_TEMPO_MEDIO_ATENCAO = 7
    LIMITE_TEMPO_MEDIO_ELEVADO = 15

    PALAVRAS_CHAVE_PSICOSSOCIAIS = {
        "assedio": {
            "termos": [
                "assédio",
                "assedio",
                "assédio moral",
                "assedio moral",
                "assédio sexual",
                "assedio sexual"
            ],
            "fator": "Práticas de liderança e relações interpessoais",
            "recomendacoes": [
                (
                    "Avaliar práticas de liderança, comunicação "
                    "e relacionamento interpessoal nas áreas "
                    "com maior concentração de registros."
                ),
                (
                    "Reforçar orientações sobre prevenção e combate "
                    "ao assédio, incluindo canais de acolhimento "
                    "e procedimentos de apuração."
                ),
                (
                    "Capacitar lideranças para gestão de conflitos, "
                    "comunicação respeitosa e prevenção de condutas "
                    "inadequadas."
                )
            ]
        },
        "discriminacao": {
            "termos": [
                "discriminação",
                "discriminacao",
                "preconceito"
            ],
            "fator": "Respeito, diversidade e inclusão",
            "recomendacoes": [
                (
                    "Revisar práticas, políticas e treinamentos "
                    "relacionados à diversidade, respeito e inclusão."
                ),
                (
                    "Avaliar a necessidade de ações educativas "
                    "sobre comportamentos discriminatórios e "
                    "condutas esperadas."
                )
            ]
        },
        "violencia": {
            "termos": [
                "violência",
                "violencia",
                "ameaça",
                "ameaca",
                "agressão",
                "agressao"
            ],
            "fator": "Violência, ameaça e segurança psicológica",
            "recomendacoes": [
                (
                    "Priorizar a apuração dos registros relacionados "
                    "a violência, ameaças ou agressões."
                ),
                (
                    "Revisar medidas de prevenção, acolhimento "
                    "e resposta a situações de violência no trabalho."
                )
            ]
        },
        "sobrecarga": {
            "termos": [
                "sobrecarga",
                "pressão",
                "pressao",
                "excesso de trabalho",
                "meta",
                "metas",
                "jornada"
            ],
            "fator": "Demandas, ritmo e organização do trabalho",
            "recomendacoes": [
                (
                    "Avaliar distribuição de atividades, metas, "
                    "ritmo de trabalho e adequação das jornadas."
                ),
                (
                    "Verificar a existência de sobrecarga recorrente "
                    "em setores, unidades ou turnos específicos."
                )
            ]
        },
        "conflitos": {
            "termos": [
                "conflito",
                "relacionamento",
                "comunicação",
                "comunicacao",
                "clima"
            ],
            "fator": "Comunicação e relacionamento no trabalho",
            "recomendacoes": [
                (
                    "Fortalecer mecanismos de comunicação interna "
                    "e mediação de conflitos."
                ),
                (
                    "Avaliar o clima organizacional nas áreas com "
                    "maior recorrência de registros."
                )
            ]
        },
        "inseguranca": {
            "termos": [
                "conduta insegura",
                "segurança",
                "seguranca",
                "risco",
                "acidente"
            ],
            "fator": "Condições de trabalho e segurança operacional",
            "recomendacoes": [
                (
                    "Revisar procedimentos operacionais, treinamentos "
                    "e controles relacionados à segurança do trabalho."
                ),
                (
                    "Avaliar se os registros indicam falhas recorrentes "
                    "em processos, orientação ou supervisão."
                )
            ]
        }
    }

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
            InterpretacaoPsicossocialService._numero(
                valor
            )
        )

    @staticmethod
    def _texto_normalizado(
        valor: Any
    ) -> str:
        return str(
            valor or ""
        ).strip().lower()

    @staticmethod
    def _plural(
        quantidade: int,
        singular: str,
        plural: str
    ) -> str:
        return (
            singular
            if quantidade == 1
            else plural
        )

    @staticmethod
    def _formatar_percentual(
        valor: Any
    ) -> str:
        numero = (
            InterpretacaoPsicossocialService._numero(
                valor
            )
        )

        return (
            f"{numero:.2f}"
            .replace(
                ".",
                ","
            )
            + "%"
        )

    @classmethod
    def _categoria_corresponde(
        cls,
        categoria: str,
        termos: list[str]
    ) -> bool:
        categoria_normalizada = (
            cls._texto_normalizado(
                categoria
            )
        )

        return any(
            termo in categoria_normalizada
            for termo in termos
        )

    @classmethod
    def gerar_interpretacoes(
        cls,
        dados_relatorio: dict[str, Any]
    ) -> dict[str, Any]:
        if not dados_relatorio:
            raise ValueError(
                "Os dados do relatório não foram informados."
            )

        total_denuncias = cls._inteiro(
            dados_relatorio.get(
                "total_denuncias"
            )
        )

        resumo_executivo = cls._gerar_resumo_executivo(
            dados_relatorio
        )

        pontos_atencao = cls._gerar_pontos_atencao(
            dados_relatorio
        )

        aspectos_positivos = cls._gerar_aspectos_positivos(
            dados_relatorio
        )

        fatores_associados = cls._identificar_fatores_associados(
            dados_relatorio
        )

        recomendacoes = cls._gerar_recomendacoes(
            dados_relatorio,
            fatores_associados
        )

        plano_acao = cls._gerar_plano_acao_sugerido(
            dados_relatorio,
            fatores_associados
        )

        conclusao = cls._gerar_conclusao(
            dados_relatorio,
            pontos_atencao
        )

        return {
            "total_denuncias": total_denuncias,
            "resumo_executivo": resumo_executivo,
            "pontos_atencao": pontos_atencao,
            "aspectos_positivos": aspectos_positivos,
            "fatores_associados": fatores_associados,
            "recomendacoes": recomendacoes,
            "plano_acao_sugerido": plano_acao,
            "conclusao": conclusao,
            "como_interpretar": cls._gerar_orientacoes_interpretacao(),
            "limitacoes": cls._gerar_limitacoes(),
            "criterios_aplicados": cls._gerar_criterios_aplicados()
        }

    @classmethod
    def _gerar_resumo_executivo(
        cls,
        dados: dict[str, Any]
    ) -> list[str]:
        total = cls._inteiro(
            dados.get(
                "total_denuncias"
            )
        )

        indicadores = dados.get(
            "indicadores",
            {}
        )

        concentracoes = dados.get(
            "concentracoes",
            {}
        )

        evolucao = dados.get(
            "evolucao",
            {}
        )

        indice = dados.get(
            "indice_indicativo",
            {}
        )

        resumo = []

        if total == 0:
            resumo.append(
                "Não foram identificadas denúncias para o período "
                "e os filtros selecionados."
            )

            resumo.append(
                "A ausência de registros não permite concluir pela "
                "ausência de fatores de risco psicossociais, pois pode "
                "estar relacionada ao nível de divulgação, acesso ou "
                "confiança no canal."
            )

            return resumo

        palavra_denuncia = cls._plural(
            total,
            "denúncia",
            "denúncias"
        )

        resumo.append(
            f"No período analisado foram registradas "
            f"{total} {palavra_denuncia}."
        )

        maior_categoria = concentracoes.get(
            "maior_categoria"
        )

        if maior_categoria:
            resumo.append(
                "A categoria com maior participação foi "
                f"“{maior_categoria['nome']}”, com "
                f"{maior_categoria['total']} registro(s), "
                "representando "
                f"{cls._formatar_percentual(
                    maior_categoria['percentual']
                )} do total."
            )

        maior_unidade = concentracoes.get(
            "maior_unidade"
        )

        if maior_unidade:
            resumo.append(
                "A unidade com maior concentração de registros foi "
                f"“{maior_unidade['nome']}”, responsável por "
                f"{cls._formatar_percentual(
                    maior_unidade['percentual']
                )} das denúncias analisadas."
            )

        maior_setor = concentracoes.get(
            "maior_setor"
        )

        if maior_setor:
            resumo.append(
                "O setor com maior número de ocorrências foi "
                f"“{maior_setor['nome']}”, com "
                f"{maior_setor['total']} registro(s)."
            )

        maior_turno = concentracoes.get(
            "maior_turno"
        )

        if maior_turno:
            resumo.append(
                "O turno com maior quantidade de registros foi "
                f"“{maior_turno['nome']}”, representando "
                f"{cls._formatar_percentual(
                    maior_turno['percentual']
                )} do total."
            )

        percentual_criticas = cls._numero(
            indicadores.get(
                "percentual_criticas"
            )
        )

        if percentual_criticas > 0:
            resumo.append(
                "As denúncias classificadas com alta criticidade "
                "corresponderam a "
                f"{cls._formatar_percentual(
                    percentual_criticas
                )} dos registros."
            )

        classificacao_tendencia = evolucao.get(
            "classificacao"
        )

        if (
            classificacao_tendencia
            and classificacao_tendencia
            != "Sem base comparativa"
        ):
            variacao = cls._numero(
                evolucao.get(
                    "variacao_percentual"
                )
            )

            resumo.append(
                "A comparação entre os dois últimos meses "
                f"disponíveis indicou tendência "
                f"{classificacao_tendencia.lower()}, "
                f"com variação de "
                f"{cls._formatar_percentual(
                    variacao
                )}."
            )

        nivel_indice = indice.get(
            "nivel"
        )

        valor_indice = cls._numero(
            indice.get(
                "valor"
            )
        )

        if nivel_indice:
            resumo.append(
                "O Índice Indicativo de Atenção Psicossocial "
                f"foi calculado em {valor_indice:.2f} pontos, "
                f"com classificação “{nivel_indice}”."
            )

        return resumo

    @classmethod
    def _gerar_pontos_atencao(
        cls,
        dados: dict[str, Any]
    ) -> list[dict[str, Any]]:
        indicadores = dados.get(
            "indicadores",
            {}
        )

        concentracoes = dados.get(
            "concentracoes",
            {}
        )

        planos = dados.get(
            "planos_acao",
            {}
        )

        criticidades = dados.get(
            "criticidades",
            {}
        )

        evolucao = dados.get(
            "evolucao",
            {}
        )

        pontos = []

        percentual_criticas = cls._numero(
            indicadores.get(
                "percentual_criticas"
            )
        )

        percentual_criticas_abertas = cls._numero(
            indicadores.get(
                "percentual_criticas_em_aberto"
            )
        )

        if (
            percentual_criticas
            >= cls.LIMITE_CRITICAS_PRIORITARIO
        ):
            pontos.append({
                "prioridade": "alta",
                "titulo": (
                    "Participação elevada de denúncias críticas"
                ),
                "descricao": (
                    "As denúncias de alta criticidade representam "
                    f"{cls._formatar_percentual(
                        percentual_criticas
                    )} do total analisado."
                ),
                "criterio": (
                    "Percentual de denúncias críticas igual "
                    f"ou superior a "
                    f"{cls.LIMITE_CRITICAS_PRIORITARIO}%."
                )
            })

        elif (
            percentual_criticas
            >= cls.LIMITE_CRITICAS_ATENCAO
        ):
            pontos.append({
                "prioridade": "media",
                "titulo": (
                    "Participação relevante de denúncias críticas"
                ),
                "descricao": (
                    "As denúncias de alta criticidade representam "
                    f"{cls._formatar_percentual(
                        percentual_criticas
                    )} do total analisado."
                ),
                "criterio": (
                    "Percentual de denúncias críticas igual "
                    f"ou superior a "
                    f"{cls.LIMITE_CRITICAS_ATENCAO}%."
                )
            })

        if (
            percentual_criticas_abertas
            >= cls.LIMITE_CRITICAS_ATENCAO
        ):
            pontos.append({
                "prioridade": "alta",
                "titulo": (
                    "Denúncias críticas ainda em aberto"
                ),
                "descricao": (
                    "Os registros críticos ainda não encerrados "
                    "representam "
                    f"{cls._formatar_percentual(
                        percentual_criticas_abertas
                    )} do total."
                ),
                "criterio": (
                    "Percentual de denúncias críticas em aberto "
                    f"igual ou superior a "
                    f"{cls.LIMITE_CRITICAS_ATENCAO}%."
                )
            })

        percentual_em_aberto = cls._numero(
            indicadores.get(
                "percentual_em_aberto"
            )
        )

        if (
            percentual_em_aberto
            >= cls.LIMITE_ABERTAS_ELEVADO
        ):
            pontos.append({
                "prioridade": "alta",
                "titulo": (
                    "Elevado volume de denúncias em aberto"
                ),
                "descricao": (
                    f"{cls._formatar_percentual(
                        percentual_em_aberto
                    )} das denúncias permanecem em tratamento."
                ),
                "criterio": (
                    "Percentual em aberto igual ou superior "
                    f"a {cls.LIMITE_ABERTAS_ELEVADO}%."
                )
            })

        elif (
            percentual_em_aberto
            >= cls.LIMITE_ABERTAS_ATENCAO
        ):
            pontos.append({
                "prioridade": "media",
                "titulo": (
                    "Volume relevante de denúncias em aberto"
                ),
                "descricao": (
                    f"{cls._formatar_percentual(
                        percentual_em_aberto
                    )} das denúncias permanecem em tratamento."
                ),
                "criterio": (
                    "Percentual em aberto igual ou superior "
                    f"a {cls.LIMITE_ABERTAS_ATENCAO}%."
                )
            })

        percentual_atrasadas = cls._numero(
            indicadores.get(
                "percentual_abertas_mais_7_dias"
            )
        )

        if (
            percentual_atrasadas
            >= cls.LIMITE_ATRASADAS_ELEVADO
        ):
            pontos.append({
                "prioridade": "alta",
                "titulo": (
                    "Concentração elevada de denúncias abertas "
                    "há mais de sete dias"
                ),
                "descricao": (
                    f"{cls._formatar_percentual(
                        percentual_atrasadas
                    )} dos registros permanecem abertos "
                    "há mais de sete dias."
                ),
                "criterio": (
                    "Percentual de denúncias abertas há mais "
                    f"de sete dias igual ou superior a "
                    f"{cls.LIMITE_ATRASADAS_ELEVADO}%."
                )
            })

        elif (
            percentual_atrasadas
            >= cls.LIMITE_ATRASADAS_ATENCAO
        ):
            pontos.append({
                "prioridade": "media",
                "titulo": (
                    "Denúncias abertas há mais de sete dias"
                ),
                "descricao": (
                    f"{cls._formatar_percentual(
                        percentual_atrasadas
                    )} dos registros permanecem abertos "
                    "há mais de sete dias."
                ),
                "criterio": (
                    "Percentual de denúncias abertas há mais "
                    f"de sete dias igual ou superior a "
                    f"{cls.LIMITE_ATRASADAS_ATENCAO}%."
                )
            })

        tempo_medio = cls._numero(
            indicadores.get(
                "tempo_medio_encerramento_dias"
            )
        )

        if tempo_medio >= cls.LIMITE_TEMPO_MEDIO_ELEVADO:
            pontos.append({
                "prioridade": "alta",
                "titulo": (
                    "Tempo médio elevado para encerramento"
                ),
                "descricao": (
                    "O tempo médio de encerramento foi de "
                    f"{tempo_medio:.1f} dias."
                ),
                "criterio": (
                    "Tempo médio igual ou superior a "
                    f"{cls.LIMITE_TEMPO_MEDIO_ELEVADO} dias."
                )
            })

        elif tempo_medio >= cls.LIMITE_TEMPO_MEDIO_ATENCAO:
            pontos.append({
                "prioridade": "media",
                "titulo": (
                    "Tempo médio de encerramento requer acompanhamento"
                ),
                "descricao": (
                    "O tempo médio de encerramento foi de "
                    f"{tempo_medio:.1f} dias."
                ),
                "criterio": (
                    "Tempo médio igual ou superior a "
                    f"{cls.LIMITE_TEMPO_MEDIO_ATENCAO} dias."
                )
            })

        maior_categoria = concentracoes.get(
            "maior_categoria"
        )

        if maior_categoria:
            percentual = cls._numero(
                maior_categoria.get(
                    "percentual"
                )
            )

            if percentual >= cls.LIMITE_CONCENTRACAO_ELEVADA:
                prioridade = "alta"

            elif percentual >= cls.LIMITE_CONCENTRACAO_RELEVANTE:
                prioridade = "media"

            else:
                prioridade = None

            if prioridade:
                pontos.append({
                    "prioridade": prioridade,
                    "titulo": (
                        "Concentração de denúncias em uma categoria"
                    ),
                    "descricao": (
                        f"A categoria “{maior_categoria['nome']}” "
                        f"representa "
                        f"{cls._formatar_percentual(
                            percentual
                        )} dos registros."
                    ),
                    "criterio": (
                        "Maior categoria com participação igual "
                        f"ou superior a "
                        f"{cls.LIMITE_CONCENTRACAO_RELEVANTE}%."
                    )
                })

        maior_unidade = concentracoes.get(
            "maior_unidade"
        )

        if maior_unidade:
            percentual = cls._numero(
                maior_unidade.get(
                    "percentual"
                )
            )

            if percentual >= cls.LIMITE_CONCENTRACAO_ELEVADA:
                prioridade = "alta"

            elif percentual >= cls.LIMITE_CONCENTRACAO_RELEVANTE:
                prioridade = "media"

            else:
                prioridade = None

            if prioridade:
                pontos.append({
                    "prioridade": prioridade,
                    "titulo": (
                        "Concentração de denúncias em uma unidade"
                    ),
                    "descricao": (
                        f"A unidade “{maior_unidade['nome']}” "
                        f"concentra "
                        f"{cls._formatar_percentual(
                            percentual
                        )} dos registros."
                    ),
                    "criterio": (
                        "Maior unidade com participação igual "
                        f"ou superior a "
                        f"{cls.LIMITE_CONCENTRACAO_RELEVANTE}%."
                    )
                })

        percentual_vencidos = cls._numero(
            planos.get(
                "percentual_vencidos"
            )
        )

        if (
            percentual_vencidos
            >= cls.LIMITE_PLANOS_VENCIDOS_ELEVADO
        ):
            pontos.append({
                "prioridade": "alta",
                "titulo": (
                    "Percentual elevado de planos de ação vencidos"
                ),
                "descricao": (
                    f"{cls._formatar_percentual(
                        percentual_vencidos
                    )} dos planos de ação estão vencidos."
                ),
                "criterio": (
                    "Percentual de planos vencidos igual "
                    f"ou superior a "
                    f"{cls.LIMITE_PLANOS_VENCIDOS_ELEVADO}%."
                )
            })

        elif (
            percentual_vencidos
            >= cls.LIMITE_PLANOS_VENCIDOS_ATENCAO
        ):
            pontos.append({
                "prioridade": "media",
                "titulo": (
                    "Planos de ação vencidos"
                ),
                "descricao": (
                    f"{cls._formatar_percentual(
                        percentual_vencidos
                    )} dos planos de ação estão vencidos."
                ),
                "criterio": (
                    "Percentual de planos vencidos igual "
                    f"ou superior a "
                    f"{cls.LIMITE_PLANOS_VENCIDOS_ATENCAO}%."
                )
            })

        if evolucao.get("classificacao") == "Crescente":
            pontos.append({
                "prioridade": "media",
                "titulo": (
                    "Tendência crescente no volume mensal"
                ),
                "descricao": (
                    "Os dois últimos meses disponíveis apresentaram "
                    "crescimento de "
                    f"{cls._formatar_percentual(
                        evolucao.get(
                            'variacao_percentual'
                        )
                    )}."
                ),
                "criterio": (
                    "Variação mensal superior a 10%."
                )
            })

        indice_gravidade = cls._numero(
            criticidades.get(
                "indice_gravidade"
            )
        )

        if indice_gravidade >= 70:
            pontos.append({
                "prioridade": "alta",
                "titulo": (
                    "Índice de gravidade elevado"
                ),
                "descricao": (
                    "O índice normalizado de gravidade foi "
                    f"calculado em {indice_gravidade:.2f} pontos."
                ),
                "criterio": (
                    "Índice normalizado de gravidade igual "
                    "ou superior a 70 pontos."
                )
            })

        ordem = {
            "alta": 1,
            "media": 2,
            "baixa": 3
        }

        return sorted(
            pontos,
            key=lambda item: ordem.get(
                item["prioridade"],
                4
            )
        )

    @classmethod
    def _gerar_aspectos_positivos(
        cls,
        dados: dict[str, Any]
    ) -> list[dict[str, Any]]:
        indicadores = dados.get(
            "indicadores",
            {}
        )

        planos = dados.get(
            "planos_acao",
            {}
        )

        evolucao = dados.get(
            "evolucao",
            {}
        )

        aspectos = []

        percentual_encerradas = cls._numero(
            indicadores.get(
                "percentual_encerradas"
            )
        )

        if percentual_encerradas >= 80:
            aspectos.append({
                "titulo": (
                    "Elevado percentual de denúncias encerradas"
                ),
                "descricao": (
                    f"{cls._formatar_percentual(
                        percentual_encerradas
                    )} dos registros foram encerrados."
                )
            })

        percentual_planos_concluidos = cls._numero(
            planos.get(
                "percentual_concluidos"
            )
        )

        if percentual_planos_concluidos >= 80:
            aspectos.append({
                "titulo": (
                    "Boa execução dos planos de ação"
                ),
                "descricao": (
                    f"{cls._formatar_percentual(
                        percentual_planos_concluidos
                    )} dos planos de ação foram concluídos."
                )
            })

        if evolucao.get("classificacao") == "Decrescente":
            aspectos.append({
                "titulo": (
                    "Redução no volume mensal de denúncias"
                ),
                "descricao": (
                    "Os dois últimos meses disponíveis apresentaram "
                    "redução de "
                    f"{cls._formatar_percentual(
                        abs(
                            cls._numero(
                                evolucao.get(
                                    'variacao_percentual'
                                )
                            )
                        )
                    )}."
                )
            })

        percentual_criticas_abertas = cls._numero(
            indicadores.get(
                "percentual_criticas_em_aberto"
            )
        )

        if percentual_criticas_abertas == 0:
            aspectos.append({
                "titulo": (
                    "Ausência de denúncias críticas em aberto"
                ),
                "descricao": (
                    "Não foram identificadas denúncias de alta "
                    "criticidade ainda abertas no período analisado."
                )
            })

        return aspectos

    @classmethod
    def _identificar_fatores_associados(
        cls,
        dados: dict[str, Any]
    ) -> list[dict[str, Any]]:
        categorias = dados.get(
            "categorias",
            []
        )

        fatores = []

        for chave, configuracao in (
            cls.PALAVRAS_CHAVE_PSICOSSOCIAIS.items()
        ):
            categorias_encontradas = []
            total_encontrado = 0

            for item in categorias:
                categoria = item.get(
                    "categoria"
                )

                if cls._categoria_corresponde(
                    categoria,
                    configuracao["termos"]
                ):
                    categorias_encontradas.append(
                        categoria
                    )

                    total_encontrado += cls._inteiro(
                        item.get(
                            "total"
                        )
                    )

            if categorias_encontradas:
                fatores.append({
                    "codigo": chave,
                    "fator": configuracao["fator"],
                    "categorias_relacionadas": (
                        categorias_encontradas
                    ),
                    "total_registros": total_encontrado,
                    "observacao": (
                        "Associação indicativa baseada no nome "
                        "das categorias registradas. Deve ser "
                        "validada por análise técnica."
                    )
                })

        return fatores

    @classmethod
    def _gerar_recomendacoes(
        cls,
        dados: dict[str, Any],
        fatores: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        indicadores = dados.get(
            "indicadores",
            {}
        )

        planos = dados.get(
            "planos_acao",
            {}
        )

        concentracoes = dados.get(
            "concentracoes",
            {}
        )

        recomendacoes = []
        textos_adicionados = set()

        def adicionar(
            prioridade: str,
            titulo: str,
            descricao: str,
            fundamento: str
        ) -> None:
            chave = (
                titulo.strip().lower(),
                descricao.strip().lower()
            )

            if chave in textos_adicionados:
                return

            textos_adicionados.add(
                chave
            )

            recomendacoes.append({
                "prioridade": prioridade,
                "titulo": titulo,
                "descricao": descricao,
                "fundamento": fundamento
            })

        percentual_criticas_abertas = cls._numero(
            indicadores.get(
                "percentual_criticas_em_aberto"
            )
        )

        if percentual_criticas_abertas > 0:
            adicionar(
                prioridade="alta",
                titulo=(
                    "Priorizar denúncias críticas em aberto"
                ),
                descricao=(
                    "Revisar imediatamente os registros de alta "
                    "criticidade ainda não encerrados, definindo "
                    "responsáveis, prazos e medidas de contenção."
                ),
                fundamento=(
                    "Existência de denúncias críticas em aberto."
                )
            )

        percentual_atrasadas = cls._numero(
            indicadores.get(
                "percentual_abertas_mais_7_dias"
            )
        )

        if percentual_atrasadas >= cls.LIMITE_ATRASADAS_ATENCAO:
            adicionar(
                prioridade="alta",
                titulo=(
                    "Revisar casos sem conclusão em prazo adequado"
                ),
                descricao=(
                    "Avaliar os motivos de permanência dos registros "
                    "em aberto por mais de sete dias e estabelecer "
                    "prazos internos de acompanhamento."
                ),
                fundamento=(
                    "Percentual relevante de denúncias abertas "
                    "há mais de sete dias."
                )
            )

        percentual_planos_vencidos = cls._numero(
            planos.get(
                "percentual_vencidos"
            )
        )

        if percentual_planos_vencidos > 0:
            adicionar(
                prioridade="alta",
                titulo=(
                    "Regularizar planos de ação vencidos"
                ),
                descricao=(
                    "Revisar responsáveis e prazos dos planos "
                    "vencidos, registrando justificativas e novas "
                    "datas quando tecnicamente aplicável."
                ),
                fundamento=(
                    "Existência de planos de ação vencidos."
                )
            )

        maior_unidade = concentracoes.get(
            "maior_unidade"
        )

        if (
            maior_unidade
            and cls._numero(
                maior_unidade.get(
                    "percentual"
                )
            )
            >= cls.LIMITE_CONCENTRACAO_RELEVANTE
        ):
            adicionar(
                prioridade="media",
                titulo=(
                    "Realizar análise direcionada na unidade "
                    "com maior concentração"
                ),
                descricao=(
                    f"Aprofundar a análise na unidade "
                    f"“{maior_unidade['nome']}”, considerando "
                    "entrevistas, observações, indicadores de RH "
                    "e condições de organização do trabalho."
                ),
                fundamento=(
                    "Concentração de denúncias igual ou superior "
                    f"a {cls.LIMITE_CONCENTRACAO_RELEVANTE}% "
                    "em uma única unidade."
                )
            )

        maior_setor = concentracoes.get(
            "maior_setor"
        )

        if (
            maior_setor
            and cls._numero(
                maior_setor.get(
                    "percentual"
                )
            )
            >= cls.LIMITE_CONCENTRACAO_RELEVANTE
        ):
            adicionar(
                prioridade="media",
                titulo=(
                    "Avaliar o setor com maior incidência"
                ),
                descricao=(
                    f"Analisar o setor “{maior_setor['nome']}” "
                    "quanto às práticas de liderança, comunicação, "
                    "distribuição de atividades, conflitos e "
                    "condições de trabalho."
                ),
                fundamento=(
                    "Concentração relevante de denúncias "
                    "em um único setor."
                )
            )

        for fator in fatores:
            configuracao = (
                cls.PALAVRAS_CHAVE_PSICOSSOCIAIS.get(
                    fator["codigo"],
                    {}
                )
            )

            for texto in configuracao.get(
                "recomendacoes",
                []
            ):
                adicionar(
                    prioridade="media",
                    titulo=fator["fator"],
                    descricao=texto,
                    fundamento=(
                        "Categorias relacionadas identificadas: "
                        + ", ".join(
                            fator[
                                "categorias_relacionadas"
                            ]
                        )
                        + "."
                    )
                )

        adicionar(
            prioridade="baixa",
            titulo=(
                "Monitorar os indicadores periodicamente"
            ),
            descricao=(
                "Recomenda-se repetir a análise em periodicidade "
                "definida pela organização, comparando os resultados "
                "com períodos anteriores."
            ),
            fundamento=(
                "Prática de monitoramento contínuo da gestão."
            )
        )

        adicionar(
            prioridade="baixa",
            titulo=(
                "Cruzar os resultados com outras fontes"
            ),
            descricao=(
                "Analisar os registros em conjunto com absenteísmo, "
                "turnover, afastamentos, entrevistas, pesquisas de "
                "clima, dados de saúde ocupacional e informações "
                "do PGR."
            ),
            fundamento=(
                "O Canal de Denúncias constitui apenas uma das "
                "fontes possíveis de evidências organizacionais."
            )
        )

        ordem = {
            "alta": 1,
            "media": 2,
            "baixa": 3
        }

        return sorted(
            recomendacoes,
            key=lambda item: ordem.get(
                item["prioridade"],
                4
            )
        )

    @classmethod
    def _gerar_plano_acao_sugerido(
        cls,
        dados: dict[str, Any],
        fatores: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        indicadores = dados.get(
            "indicadores",
            {}
        )

        planos = []

        def adicionar(
            prioridade: str,
            acao: str,
            objetivo: str,
            responsavel_sugerido: str,
            prazo_sugerido: str,
            indicador_acompanhamento: str
        ) -> None:
            if any(
                item["acao"] == acao
                for item in planos
            ):
                return

            planos.append({
                "prioridade": prioridade,
                "acao": acao,
                "objetivo": objetivo,
                "responsavel_sugerido": (
                    responsavel_sugerido
                ),
                "prazo_sugerido": prazo_sugerido,
                "indicador_acompanhamento": (
                    indicador_acompanhamento
                )
            })

        if cls._inteiro(
            indicadores.get(
                "criticas_em_aberto"
            )
        ) > 0:
            adicionar(
                prioridade="Alta",
                acao=(
                    "Revisar todas as denúncias críticas em aberto"
                ),
                objetivo=(
                    "Garantir priorização, definição de responsável "
                    "e adoção de medidas imediatas quando necessárias."
                ),
                responsavel_sugerido=(
                    "Compliance, RH, SESMT e gestão responsável"
                ),
                prazo_sugerido="Imediato",
                indicador_acompanhamento=(
                    "Quantidade de denúncias críticas em aberto"
                )
            )

        if cls._inteiro(
            indicadores.get(
                "abertas_mais_7_dias"
            )
        ) > 0:
            adicionar(
                prioridade="Alta",
                acao=(
                    "Revisar denúncias abertas há mais de sete dias"
                ),
                objetivo=(
                    "Identificar gargalos no tratamento e reduzir "
                    "o tempo de resposta."
                ),
                responsavel_sugerido=(
                    "Gestor do canal e responsáveis pelas investigações"
                ),
                prazo_sugerido="Até 15 dias",
                indicador_acompanhamento=(
                    "Percentual de denúncias abertas há mais de sete dias"
                )
            )

        for fator in fatores:
            codigo = fator["codigo"]

            if codigo == "assedio":
                adicionar(
                    prioridade="Alta",
                    acao=(
                        "Executar ação preventiva sobre assédio "
                        "e condutas respeitosas"
                    ),
                    objetivo=(
                        "Reforçar comportamentos esperados e reduzir "
                        "a ocorrência de condutas inadequadas."
                    ),
                    responsavel_sugerido=(
                        "RH, Compliance, Jurídico e lideranças"
                    ),
                    prazo_sugerido="Até 60 dias",
                    indicador_acompanhamento=(
                        "Quantidade de registros relacionados a assédio"
                    )
                )

            elif codigo == "sobrecarga":
                adicionar(
                    prioridade="Média",
                    acao=(
                        "Avaliar distribuição de demandas, metas "
                        "e jornadas"
                    ),
                    objetivo=(
                        "Identificar possíveis situações de sobrecarga "
                        "ou pressão organizacional excessiva."
                    ),
                    responsavel_sugerido=(
                        "RH, SESMT e gestores das áreas"
                    ),
                    prazo_sugerido="Até 60 dias",
                    indicador_acompanhamento=(
                        "Registros relacionados a sobrecarga, "
                        "pressão ou jornadas"
                    )
                )

            elif codigo == "conflitos":
                adicionar(
                    prioridade="Média",
                    acao=(
                        "Fortalecer comunicação e mediação de conflitos"
                    ),
                    objetivo=(
                        "Reduzir falhas de comunicação e apoiar "
                        "a resolução estruturada de conflitos."
                    ),
                    responsavel_sugerido=(
                        "RH e lideranças"
                    ),
                    prazo_sugerido="Até 90 dias",
                    indicador_acompanhamento=(
                        "Registros relacionados a conflitos "
                        "e comunicação"
                    )
                )

            elif codigo == "discriminacao":
                adicionar(
                    prioridade="Alta",
                    acao=(
                        "Reforçar programa de diversidade, respeito "
                        "e prevenção à discriminação"
                    ),
                    objetivo=(
                        "Prevenir comportamentos discriminatórios "
                        "e fortalecer ambiente respeitoso."
                    ),
                    responsavel_sugerido=(
                        "RH, Compliance e lideranças"
                    ),
                    prazo_sugerido="Até 60 dias",
                    indicador_acompanhamento=(
                        "Registros relacionados a discriminação"
                    )
                )

            elif codigo == "violencia":
                adicionar(
                    prioridade="Alta",
                    acao=(
                        "Revisar medidas de prevenção e resposta "
                        "a situações de violência"
                    ),
                    objetivo=(
                        "Garantir resposta rápida, acolhimento "
                        "e prevenção de recorrências."
                    ),
                    responsavel_sugerido=(
                        "SESMT, RH, Segurança Patrimonial "
                        "e Compliance"
                    ),
                    prazo_sugerido="Imediato",
                    indicador_acompanhamento=(
                        "Registros relacionados a violência "
                        "ou ameaças"
                    )
                )

            elif codigo == "inseguranca":
                adicionar(
                    prioridade="Alta",
                    acao=(
                        "Revisar procedimentos e treinamentos "
                        "de segurança"
                    ),
                    objetivo=(
                        "Reduzir falhas operacionais e comportamentos "
                        "inseguros identificados nos registros."
                    ),
                    responsavel_sugerido=(
                        "SESMT, operação e lideranças"
                    ),
                    prazo_sugerido="Até 30 dias",
                    indicador_acompanhamento=(
                        "Registros relacionados a condutas inseguras"
                    )
                )

        adicionar(
            prioridade="Média",
            acao=(
                "Realizar análise complementar dos fatores psicossociais"
            ),
            objetivo=(
                "Complementar os dados do canal com entrevistas, "
                "observações, avaliações organizacionais e demais "
                "evidências aplicáveis."
            ),
            responsavel_sugerido=(
                "SESMT, RH e profissionais tecnicamente responsáveis"
            ),
            prazo_sugerido="Conforme planejamento do PGR",
            indicador_acompanhamento=(
                "Conclusão da análise complementar"
            )
        )

        adicionar(
            prioridade="Baixa",
            acao=(
                "Reavaliar os indicadores em ciclo periódico"
            ),
            objetivo=(
                "Monitorar tendências, reincidências e efetividade "
                "das ações adotadas."
            ),
            responsavel_sugerido=(
                "Gestor do canal, RH e SESMT"
            ),
            prazo_sugerido="Trimestral",
            indicador_acompanhamento=(
                "Comparativo entre períodos"
            )
        )

        ordem = {
            "Alta": 1,
            "Média": 2,
            "Baixa": 3
        }

        return sorted(
            planos,
            key=lambda item: ordem.get(
                item["prioridade"],
                4
            )
        )

    @classmethod
    def _gerar_conclusao(
        cls,
        dados: dict[str, Any],
        pontos_atencao: list[dict[str, Any]]
    ) -> list[str]:
        total = cls._inteiro(
            dados.get(
                "total_denuncias"
            )
        )

        indice = dados.get(
            "indice_indicativo",
            {}
        )

        conclusao = []

        if total == 0:
            conclusao.append(
                "Os filtros selecionados não apresentaram registros "
                "suficientes para análise estatística por meio do "
                "Canal de Denúncias."
            )

            conclusao.append(
                "Recomenda-se avaliar o nível de divulgação, acesso "
                "e confiança dos trabalhadores no canal, além de "
                "utilizar outras fontes de evidência."
            )

        else:
            nivel = indice.get(
                "nivel",
                "Não classificado"
            )

            valor = cls._numero(
                indice.get(
                    "valor"
                )
            )

            conclusao.append(
                "Os dados analisados permitiram identificar padrões "
                "de distribuição, criticidade, concentração e andamento "
                "dos registros realizados no Canal de Denúncias."
            )

            conclusao.append(
                "O Índice Indicativo de Atenção Psicossocial foi "
                f"calculado em {valor:.2f} pontos, com classificação "
                f"“{nivel}”, conforme a metodologia descrita "
                "neste relatório."
            )

            pontos_altos = [
                item
                for item in pontos_atencao
                if item.get(
                    "prioridade"
                ) == "alta"
            ]

            if pontos_altos:
                conclusao.append(
                    "Foram identificados pontos de atenção classificados "
                    "como prioritários, recomendando-se análise detalhada "
                    "e definição de ações com responsáveis e prazos."
                )

            else:
                conclusao.append(
                    "Não foram identificados, pelas regras utilizadas, "
                    "pontos de atenção classificados como prioridade alta. "
                    "Ainda assim, recomenda-se manter o monitoramento "
                    "periódico e a análise integrada com outras fontes."
                )

        conclusao.append(
            "Este relatório não substitui o processo de identificação "
            "de perigos, avaliação de riscos, elaboração do inventário "
            "ou definição de medidas de prevenção conduzidos pelos "
            "profissionais responsáveis."
        )

        conclusao.append(
            "As informações podem ser utilizadas como evidência "
            "complementar e subsídio para a gestão, o planejamento "
            "de ações preventivas e a revisão do PGR."
        )

        return conclusao

    @staticmethod
    def _gerar_orientacoes_interpretacao() -> list[str]:
        return [
            (
                "Poucas denúncias não significam necessariamente "
                "ausência de problemas ou fatores de risco."
            ),
            (
                "Um aumento no volume de registros pode representar "
                "maior confiança, conhecimento ou acesso ao canal."
            ),
            (
                "A concentração em determinada unidade, setor, turno "
                "ou categoria deve orientar investigação complementar, "
                "não uma conclusão automática."
            ),
            (
                "Denúncias são relatos que precisam ser analisados, "
                "apurados e contextualizados antes da tomada de decisão."
            ),
            (
                "Os indicadores devem ser cruzados com outras fontes, "
                "como absenteísmo, afastamentos, turnover, pesquisas "
                "de clima, entrevistas e observações."
            ),
            (
                "A comparação entre períodos deve considerar mudanças "
                "na divulgação do canal, no quadro de trabalhadores "
                "e na estrutura organizacional."
            )
        ]

    @staticmethod
    def _gerar_limitacoes() -> list[str]:
        return [
            (
                "O relatório utiliza somente os dados registrados "
                "no Canal de Denúncias FALAE."
            ),
            (
                "Os registros podem conter percepções individuais "
                "e dependem da qualidade das informações relatadas."
            ),
            (
                "O sistema não confirma automaticamente a procedência "
                "ou veracidade de uma denúncia."
            ),
            (
                "As associações com fatores psicossociais são "
                "indicativas e baseadas nas categorias cadastradas."
            ),
            (
                "O índice apresentado não constitui escala clínica, "
                "instrumento psicológico, avaliação ergonômica, "
                "laudo técnico ou medição de exposição ocupacional."
            ),
            (
                "A interpretação final deve ser realizada por "
                "profissionais responsáveis, considerando o contexto "
                "da organização."
            )
        ]

    @classmethod
    def _gerar_criterios_aplicados(
        cls
    ) -> list[dict[str, Any]]:
        return [
            {
                "indicador": (
                    "Concentração relevante"
                ),
                "criterio": (
                    f"Participação igual ou superior a "
                    f"{cls.LIMITE_CONCENTRACAO_RELEVANTE}%."
                )
            },
            {
                "indicador": (
                    "Concentração elevada"
                ),
                "criterio": (
                    f"Participação igual ou superior a "
                    f"{cls.LIMITE_CONCENTRACAO_ELEVADA}%."
                )
            },
            {
                "indicador": (
                    "Denúncias críticas — atenção"
                ),
                "criterio": (
                    f"Participação igual ou superior a "
                    f"{cls.LIMITE_CRITICAS_ATENCAO}%."
                )
            },
            {
                "indicador": (
                    "Denúncias críticas — prioridade"
                ),
                "criterio": (
                    f"Participação igual ou superior a "
                    f"{cls.LIMITE_CRITICAS_PRIORITARIO}%."
                )
            },
            {
                "indicador": (
                    "Denúncias em aberto — atenção"
                ),
                "criterio": (
                    f"Participação igual ou superior a "
                    f"{cls.LIMITE_ABERTAS_ATENCAO}%."
                )
            },
            {
                "indicador": (
                    "Denúncias em aberto — elevado"
                ),
                "criterio": (
                    f"Participação igual ou superior a "
                    f"{cls.LIMITE_ABERTAS_ELEVADO}%."
                )
            },
            {
                "indicador": (
                    "Abertas há mais de sete dias — atenção"
                ),
                "criterio": (
                    f"Participação igual ou superior a "
                    f"{cls.LIMITE_ATRASADAS_ATENCAO}%."
                )
            },
            {
                "indicador": (
                    "Abertas há mais de sete dias — elevado"
                ),
                "criterio": (
                    f"Participação igual ou superior a "
                    f"{cls.LIMITE_ATRASADAS_ELEVADO}%."
                )
            },
            {
                "indicador": (
                    "Tendência crescente"
                ),
                "criterio": (
                    "Crescimento superior a 10% entre "
                    "os dois últimos meses disponíveis."
                )
            },
            {
                "indicador": (
                    "Tendência decrescente"
                ),
                "criterio": (
                    "Redução superior a 10% entre "
                    "os dois últimos meses disponíveis."
                )
            }
        ]
