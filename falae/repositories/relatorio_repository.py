from datetime import date, datetime
from typing import Any

from db import get_connection


class RelatorioRepository:
    """
    Consultas consolidadas para relatórios gerenciais e psicossociais.

    Este Repository é responsável exclusivamente pelo acesso aos dados.
    Cálculos, percentuais, índices e interpretações devem permanecer
    nos Services.
    """

    STATUS_ENCERRADOS = (
        "CONCLUIDA",
        "ARQUIVADA"
    )

    def __init__(self):
        self.conn = get_connection()

        self.cursor = self.conn.cursor(
            dictionary=True
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

        return valor_normalizado

    @classmethod
    def _montar_filtros(
        cls,
        empresa_id: int,
        data_inicio: str | date | datetime | None = None,
        data_fim: str | date | datetime | None = None,
        unidade_id: int | str | None = None,
        setor_id: int | str | None = None,
        turno_id: int | str | None = None,
        alias: str = "d"
    ) -> tuple[str, list[Any]]:
        """
        Monta filtros parametrizados para as consultas de denúncias.

        O alias é controlado internamente e nunca deve receber valores
        vindos diretamente do usuário.
        """

        filtros = [
            f"{alias}.empresa_id = %s"
        ]

        parametros: list[Any] = [
            int(empresa_id)
        ]

        data_inicio_normalizada = (
            cls._normalizar_data(
                data_inicio
            )
        )

        data_fim_normalizada = (
            cls._normalizar_data(
                data_fim
            )
        )

        if data_inicio_normalizada:
            filtros.append(
                f"DATE({alias}.criado_em) >= %s"
            )

            parametros.append(
                data_inicio_normalizada
            )

        if data_fim_normalizada:
            filtros.append(
                f"DATE({alias}.criado_em) <= %s"
            )

            parametros.append(
                data_fim_normalizada
            )

        if unidade_id:
            filtros.append(
                f"{alias}.unidade_id = %s"
            )

            parametros.append(
                int(unidade_id)
            )

        if setor_id:
            filtros.append(
                f"{alias}.setor_id = %s"
            )

            parametros.append(
                int(setor_id)
            )

        if turno_id:
            filtros.append(
                f"{alias}.turno_id = %s"
            )

            parametros.append(
                int(turno_id)
            )

        return (
            " AND ".join(
                filtros
            ),
            parametros
        )

    def obter_empresa(
        self,
        empresa_id: int
    ) -> dict[str, Any] | None:
        self.cursor.execute(
            """
            SELECT
                e.id,
                e.nome,
                e.cnpj,
                e.logo,
                e.slug,
                e.endereco,
                e.numero,
                e.complemento,
                e.bairro,
                e.cidade,
                e.estado,
                e.cep,
                e.contato_nome,
                e.contato_cargo,
                e.contato_email,
                e.contato_telefone,
                e.plano,
                e.ativa,

                a.nome AS assessoria_nome

            FROM empresas e

            LEFT JOIN assessorias a
                ON a.id = e.assessoria_id

            WHERE e.id = %s

            LIMIT 1
            """,
            (empresa_id,)
        )

        return self.cursor.fetchone()

    def total_denuncias(
        self,
        empresa_id: int,
        data_inicio=None,
        data_fim=None,
        unidade_id=None,
        setor_id=None,
        turno_id=None
    ) -> int:
        where_sql, parametros = (
            self._montar_filtros(
                empresa_id=empresa_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                unidade_id=unidade_id,
                setor_id=setor_id,
                turno_id=turno_id
            )
        )

        self.cursor.execute(
            f"""
            SELECT
                COUNT(*) AS total

            FROM denuncias d

            WHERE {where_sql}
            """,
            parametros
        )

        resultado = self.cursor.fetchone()

        return int(
            resultado["total"] or 0
        )

    def resumo_status(
        self,
        empresa_id: int,
        data_inicio=None,
        data_fim=None,
        unidade_id=None,
        setor_id=None,
        turno_id=None
    ) -> list[dict[str, Any]]:
        where_sql, parametros = (
            self._montar_filtros(
                empresa_id=empresa_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                unidade_id=unidade_id,
                setor_id=setor_id,
                turno_id=turno_id
            )
        )

        self.cursor.execute(
            f"""
            SELECT
                COALESCE(
                    NULLIF(TRIM(d.status), ''),
                    'NAO_INFORMADO'
                ) AS status,

                COUNT(*) AS total

            FROM denuncias d

            WHERE {where_sql}

            GROUP BY
                COALESCE(
                    NULLIF(TRIM(d.status), ''),
                    'NAO_INFORMADO'
                )

            ORDER BY total DESC
            """,
            parametros
        )

        return self.cursor.fetchall()

    def distribuicao_criticidade(
        self,
        empresa_id: int,
        data_inicio=None,
        data_fim=None,
        unidade_id=None,
        setor_id=None,
        turno_id=None
    ) -> list[dict[str, Any]]:
        where_sql, parametros = (
            self._montar_filtros(
                empresa_id=empresa_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                unidade_id=unidade_id,
                setor_id=setor_id,
                turno_id=turno_id
            )
        )

        self.cursor.execute(
            f"""
            SELECT
                resultado.criticidade,
                resultado.total

            FROM (
                SELECT
                    COALESCE(
                        NULLIF(
                            TRIM(d.criticidade),
                            ''
                        ),
                        'Não informada'
                    ) AS criticidade,

                    COUNT(*) AS total

                FROM denuncias d

                WHERE {where_sql}

                GROUP BY
                    COALESCE(
                        NULLIF(
                            TRIM(d.criticidade),
                            ''
                        ),
                        'Não informada'
                    )
            ) AS resultado

            ORDER BY
                CASE
                    WHEN LOWER(
                        TRIM(resultado.criticidade)
                    ) = 'alta'
                        THEN 1

                    WHEN LOWER(
                        TRIM(resultado.criticidade)
                    ) IN (
                        'média',
                        'media'
                    )
                        THEN 2

                    WHEN LOWER(
                        TRIM(resultado.criticidade)
                    ) = 'baixa'
                        THEN 3

                    ELSE 4
                END,
                resultado.total DESC
            """,
            parametros
        )

        return self.cursor.fetchall()

    def distribuicao_categorias(
        self,
        empresa_id: int,
        data_inicio=None,
        data_fim=None,
        unidade_id=None,
        setor_id=None,
        turno_id=None
    ) -> list[dict[str, Any]]:
        where_sql, parametros = (
            self._montar_filtros(
                empresa_id=empresa_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                unidade_id=unidade_id,
                setor_id=setor_id,
                turno_id=turno_id
            )
        )

        self.cursor.execute(
            f"""
            SELECT
                COALESCE(
                    NULLIF(TRIM(d.categoria), ''),
                    NULLIF(TRIM(d.tipo), ''),
                    'Não informada'
                ) AS categoria,

                COUNT(*) AS total,

                SUM(
                    CASE
                        WHEN d.criticidade = 'Alta'
                        THEN 1
                        ELSE 0
                    END
                ) AS criticas,

                SUM(
                    CASE
                        WHEN d.status NOT IN (
                            'CONCLUIDA',
                            'ARQUIVADA'
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS em_aberto

            FROM denuncias d

            WHERE {where_sql}

            GROUP BY
                COALESCE(
                    NULLIF(TRIM(d.categoria), ''),
                    NULLIF(TRIM(d.tipo), ''),
                    'Não informada'
                )

            ORDER BY total DESC
            """,
            parametros
        )

        return self.cursor.fetchall()

    def distribuicao_unidades(
        self,
        empresa_id: int,
        data_inicio=None,
        data_fim=None,
        unidade_id=None,
        setor_id=None,
        turno_id=None
    ) -> list[dict[str, Any]]:
        where_sql, parametros = (
            self._montar_filtros(
                empresa_id=empresa_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                unidade_id=unidade_id,
                setor_id=setor_id,
                turno_id=turno_id
            )
        )

        self.cursor.execute(
            f"""
            SELECT
                d.unidade_id,

                COALESCE(
                    u.nome,
                    'Não informada'
                ) AS unidade,

                u.cidade,
                u.estado,

                COUNT(d.id) AS total,

                SUM(
                    CASE
                        WHEN d.criticidade = 'Alta'
                        THEN 1
                        ELSE 0
                    END
                ) AS criticas,

                SUM(
                    CASE
                        WHEN d.status NOT IN (
                            'CONCLUIDA',
                            'ARQUIVADA'
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS em_aberto

            FROM denuncias d

            LEFT JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id

            WHERE {where_sql}

            GROUP BY
                d.unidade_id,
                u.nome,
                u.cidade,
                u.estado

            ORDER BY total DESC
            """,
            parametros
        )

        return self.cursor.fetchall()

    def distribuicao_setores(
        self,
        empresa_id: int,
        data_inicio=None,
        data_fim=None,
        unidade_id=None,
        setor_id=None,
        turno_id=None
    ) -> list[dict[str, Any]]:
        where_sql, parametros = (
            self._montar_filtros(
                empresa_id=empresa_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                unidade_id=unidade_id,
                setor_id=setor_id,
                turno_id=turno_id
            )
        )

        self.cursor.execute(
            f"""
            SELECT
                d.setor_id,

                COALESCE(
                    s.nome,
                    'Não informado'
                ) AS setor,

                COALESCE(
                    u.nome,
                    'Não informada'
                ) AS unidade,

                COUNT(d.id) AS total,

                SUM(
                    CASE
                        WHEN d.criticidade = 'Alta'
                        THEN 1
                        ELSE 0
                    END
                ) AS criticas,

                SUM(
                    CASE
                        WHEN d.status NOT IN (
                            'CONCLUIDA',
                            'ARQUIVADA'
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS em_aberto

            FROM denuncias d

            LEFT JOIN setores s
                ON s.id = d.setor_id

            LEFT JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id

            WHERE {where_sql}

            GROUP BY
                d.setor_id,
                s.nome,
                u.nome

            ORDER BY total DESC
            """,
            parametros
        )

        return self.cursor.fetchall()

    def distribuicao_turnos(
        self,
        empresa_id: int,
        data_inicio=None,
        data_fim=None,
        unidade_id=None,
        setor_id=None,
        turno_id=None
    ) -> list[dict[str, Any]]:
        where_sql, parametros = (
            self._montar_filtros(
                empresa_id=empresa_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                unidade_id=unidade_id,
                setor_id=setor_id,
                turno_id=turno_id
            )
        )

        self.cursor.execute(
            f"""
            SELECT
                d.turno_id,

                COALESCE(
                    t.nome,
                    'Não informado'
                ) AS turno,

                COUNT(d.id) AS total,

                SUM(
                    CASE
                        WHEN d.criticidade = 'Alta'
                        THEN 1
                        ELSE 0
                    END
                ) AS criticas,

                SUM(
                    CASE
                        WHEN d.status NOT IN (
                            'CONCLUIDA',
                            'ARQUIVADA'
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS em_aberto

            FROM denuncias d

            LEFT JOIN turnos t
                ON t.id = d.turno_id
               AND t.empresa_id = d.empresa_id

            WHERE {where_sql}

            GROUP BY
                d.turno_id,
                t.nome

            ORDER BY total DESC
            """,
            parametros
        )

        return self.cursor.fetchall()

    def evolucao_mensal(
        self,
        empresa_id: int,
        data_inicio=None,
        data_fim=None,
        unidade_id=None,
        setor_id=None,
        turno_id=None
    ) -> list[dict[str, Any]]:
        where_sql, parametros = (
            self._montar_filtros(
                empresa_id=empresa_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                unidade_id=unidade_id,
                setor_id=setor_id,
                turno_id=turno_id
            )
        )

        self.cursor.execute(
            f"""
            SELECT
                DATE_FORMAT(
                    d.criado_em,
                    '%Y-%m'
                ) AS competencia,

                YEAR(
                    d.criado_em
                ) AS ano,

                MONTH(
                    d.criado_em
                ) AS mes,

                COUNT(*) AS total,

                SUM(
                    CASE
                        WHEN d.criticidade = 'Alta'
                        THEN 1
                        ELSE 0
                    END
                ) AS criticas,

                SUM(
                    CASE
                        WHEN d.status IN (
                            'CONCLUIDA',
                            'ARQUIVADA'
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS encerradas

            FROM denuncias d

            WHERE {where_sql}

            GROUP BY
                DATE_FORMAT(
                    d.criado_em,
                    '%Y-%m'
                ),
                YEAR(
                    d.criado_em
                ),
                MONTH(
                    d.criado_em
                )

            ORDER BY
                ano ASC,
                mes ASC
            """,
            parametros
        )

        return self.cursor.fetchall()

    def indicadores_operacionais(
        self,
        empresa_id: int,
        data_inicio=None,
        data_fim=None,
        unidade_id=None,
        setor_id=None,
        turno_id=None
    ) -> dict[str, Any]:
        where_sql, parametros = (
            self._montar_filtros(
                empresa_id=empresa_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                unidade_id=unidade_id,
                setor_id=setor_id,
                turno_id=turno_id
            )
        )

        self.cursor.execute(
            f"""
            SELECT
                COUNT(*) AS total,

                SUM(
                    CASE
                        WHEN d.status NOT IN (
                            'CONCLUIDA',
                            'ARQUIVADA'
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS em_aberto,

                SUM(
                    CASE
                        WHEN d.status IN (
                            'CONCLUIDA',
                            'ARQUIVADA'
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS encerradas,

                SUM(
                    CASE
                        WHEN d.criticidade = 'Alta'
                        THEN 1
                        ELSE 0
                    END
                ) AS criticas,

                SUM(
                    CASE
                        WHEN d.criticidade = 'Alta'
                         AND d.status NOT IN (
                            'CONCLUIDA',
                            'ARQUIVADA'
                         )
                        THEN 1
                        ELSE 0
                    END
                ) AS criticas_em_aberto,

                SUM(
                    CASE
                        WHEN d.status NOT IN (
                            'CONCLUIDA',
                            'ARQUIVADA'
                        )
                         AND d.criado_em <= DATE_SUB(
                            NOW(),
                            INTERVAL 7 DAY
                         )
                        THEN 1
                        ELSE 0
                    END
                ) AS abertas_mais_7_dias,

                COALESCE(
                    ROUND(
                        AVG(
                            CASE
                                WHEN d.status IN (
                                    'CONCLUIDA',
                                    'ARQUIVADA'
                                )
                                THEN TIMESTAMPDIFF(
                                    DAY,
                                    d.criado_em,
                                    COALESCE(
                                        d.data_encerramento,
                                        d.criado_em
                                    )
                                )
                                ELSE NULL
                            END
                        ),
                        1
                    ),
                    0
                ) AS tempo_medio_encerramento_dias,

                COALESCE(
                    ROUND(
                        AVG(
                            CASE
                                WHEN d.status NOT IN (
                                    'CONCLUIDA',
                                    'ARQUIVADA'
                                )
                                THEN TIMESTAMPDIFF(
                                    DAY,
                                    d.criado_em,
                                    NOW()
                                )
                                ELSE NULL
                            END
                        ),
                        1
                    ),
                    0
                ) AS idade_media_abertas_dias

            FROM denuncias d

            WHERE {where_sql}
            """,
            parametros
        )

        resultado = self.cursor.fetchone()

        return resultado or {}

    def concentracao_categoria_unidade(
        self,
        empresa_id: int,
        data_inicio=None,
        data_fim=None,
        unidade_id=None,
        setor_id=None,
        turno_id=None
    ) -> list[dict[str, Any]]:
        """
        Retorna combinações de categoria e unidade.

        Esta consulta permitirá ao Service identificar concentrações,
        por exemplo: assédio moral concentrado em determinada unidade.
        """

        where_sql, parametros = (
            self._montar_filtros(
                empresa_id=empresa_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                unidade_id=unidade_id,
                setor_id=setor_id,
                turno_id=turno_id
            )
        )

        self.cursor.execute(
            f"""
            SELECT
                COALESCE(
                    NULLIF(TRIM(d.categoria), ''),
                    NULLIF(TRIM(d.tipo), ''),
                    'Não informada'
                ) AS categoria,

                COALESCE(
                    u.nome,
                    'Não informada'
                ) AS unidade,

                COUNT(d.id) AS total,

                SUM(
                    CASE
                        WHEN d.criticidade = 'Alta'
                        THEN 1
                        ELSE 0
                    END
                ) AS criticas

            FROM denuncias d

            LEFT JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id

            WHERE {where_sql}

            GROUP BY
                COALESCE(
                    NULLIF(TRIM(d.categoria), ''),
                    NULLIF(TRIM(d.tipo), ''),
                    'Não informada'
                ),
                u.nome

            ORDER BY total DESC
            """,
            parametros
        )

        return self.cursor.fetchall()

    def resumo_planos_acao(
        self,
        empresa_id: int,
        data_inicio=None,
        data_fim=None,
        unidade_id=None,
        setor_id=None,
        turno_id=None
    ) -> dict[str, Any]:
        where_sql, parametros = (
            self._montar_filtros(
                empresa_id=empresa_id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                unidade_id=unidade_id,
                setor_id=setor_id,
                turno_id=turno_id
            )
        )

        self.cursor.execute(
            f"""
            SELECT
                COUNT(p.id) AS total_planos,

                SUM(
                    CASE
                        WHEN p.status = 'CONCLUIDA'
                        THEN 1
                        ELSE 0
                    END
                ) AS concluidos,

                SUM(
                    CASE
                        WHEN p.status NOT IN (
                            'CONCLUIDA',
                            'CANCELADA'
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS pendentes,

                SUM(
                    CASE
                        WHEN p.prazo < CURRENT_DATE()
                         AND p.status NOT IN (
                            'CONCLUIDA',
                            'CANCELADA'
                         )
                        THEN 1
                        ELSE 0
                    END
                ) AS vencidos

            FROM planos_acao p

            INNER JOIN denuncias d
                ON d.id = p.denuncia_id

            WHERE {where_sql}
            """,
            parametros
        )

        resultado = self.cursor.fetchone()

        return resultado or {}

    def listar_unidades_filtro(
        self,
        empresa_id: int
    ) -> list[dict[str, Any]]:
        self.cursor.execute(
            """
            SELECT
                id,
                nome
            FROM unidades
            WHERE empresa_id = %s
              AND ativa = 1
            ORDER BY nome
            """,
            (empresa_id,)
        )

        return self.cursor.fetchall()

    def listar_setores_filtro(
        self,
        empresa_id: int
    ) -> list[dict[str, Any]]:
        self.cursor.execute(
            """
            SELECT
                s.id,
                s.nome,
                s.unidade_id,
                u.nome AS unidade

            FROM setores s

            INNER JOIN unidades u
                ON u.id = s.unidade_id

            WHERE u.empresa_id = %s
              AND s.ativo = 1

            ORDER BY
                u.nome,
                s.nome
            """,
            (empresa_id,)
        )

        return self.cursor.fetchall()

    def listar_turnos_filtro(
        self,
        empresa_id: int
    ) -> list[dict[str, Any]]:
        self.cursor.execute(
            """
            SELECT
                id,
                nome
            FROM turnos
            WHERE empresa_id = %s
            ORDER BY nome
            """,
            (empresa_id,)
        )

        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()
