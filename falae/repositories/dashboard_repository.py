from db import get_connection


class DashboardRepository:

    LIMITE_ALERTAS_PADRAO = 5
    LIMITE_ALERTAS_MAXIMO = 100

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    @classmethod
    def _limite_seguro(cls, limite):
        try:
            limite = int(limite)
        except (TypeError, ValueError):
            return cls.LIMITE_ALERTAS_PADRAO

        if limite < 1:
            return cls.LIMITE_ALERTAS_PADRAO

        return min(
            limite,
            cls.LIMITE_ALERTAS_MAXIMO
        )

    def total_denuncias(self, empresa_id):
        self.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM denuncias
            WHERE empresa_id = %s
        """, (empresa_id,))

        resultado = self.cursor.fetchone() or {}

        return int(resultado.get("total") or 0)

    def denuncias_novas(self, empresa_id):
        self.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM denuncias
            WHERE empresa_id = %s
              AND status = 'NOVA'
        """, (empresa_id,))

        resultado = self.cursor.fetchone() or {}

        return int(resultado.get("total") or 0)

    def denuncias_criticas(self, empresa_id):
        self.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM denuncias
            WHERE empresa_id = %s
              AND criticidade = 'Alta'
        """, (empresa_id,))

        resultado = self.cursor.fetchone() or {}

        return int(resultado.get("total") or 0)

    def denuncias_em_analise_mais_7_dias(self, empresa_id):
        self.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM denuncias
            WHERE empresa_id = %s
              AND status = 'EM_ANALISE'
              AND criado_em <= DATE_SUB(
                    NOW(),
                    INTERVAL 7 DAY
              )
        """, (empresa_id,))

        resultado = self.cursor.fetchone() or {}

        return int(resultado.get("total") or 0)

    def denuncias_concluidas_mes(self, empresa_id):
        self.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM denuncias
            WHERE empresa_id = %s
              AND status = 'CONCLUIDA'
              AND criado_em >= DATE_FORMAT(
                    CURRENT_DATE(),
                    '%%Y-%%m-01'
              )
              AND criado_em < DATE_ADD(
                    DATE_FORMAT(
                        CURRENT_DATE(),
                        '%%Y-%%m-01'
                    ),
                    INTERVAL 1 MONTH
              )
        """, (empresa_id,))

        resultado = self.cursor.fetchone() or {}

        return int(resultado.get("total") or 0)

    def denuncias_em_aberto(self, empresa_id):
        self.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM denuncias
            WHERE empresa_id = %s
              AND status IN (
                    'NOVA',
                    'EM_ANALISE'
              )
        """, (empresa_id,))

        resultado = self.cursor.fetchone() or {}

        return int(resultado.get("total") or 0)

    def denuncias_criticas_em_aberto(self, empresa_id):
        self.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM denuncias
            WHERE empresa_id = %s
              AND criticidade = 'Alta'
              AND status IN (
                    'NOVA',
                    'EM_ANALISE'
              )
        """, (empresa_id,))

        resultado = self.cursor.fetchone() or {}

        return int(resultado.get("total") or 0)

    def tempo_medio_atendimento_dias(self, empresa_id):
        self.cursor.execute("""
            SELECT
                COALESCE(
                    ROUND(
                        AVG(
                            TIMESTAMPDIFF(
                                DAY,
                                criado_em,
                                data_encerramento
                            )
                        ),
                        1
                    ),
                    0
                ) AS media_dias
            FROM denuncias
            WHERE empresa_id = %s
              AND status = 'CONCLUIDA'
              AND data_encerramento IS NOT NULL
              AND data_encerramento >= criado_em
        """, (empresa_id,))

        resultado = self.cursor.fetchone() or {}

        return float(
            resultado.get("media_dias") or 0
        )

    def percentual_concluidas_mes(self, empresa_id):
        self.cursor.execute("""
            SELECT
                COUNT(*) AS total_mes,

                SUM(
                    CASE
                        WHEN status = 'CONCLUIDA'
                        THEN 1
                        ELSE 0
                    END
                ) AS concluidas_mes

            FROM denuncias
            WHERE empresa_id = %s
              AND criado_em >= DATE_FORMAT(
                    CURRENT_DATE(),
                    '%%Y-%%m-01'
              )
              AND criado_em < DATE_ADD(
                    DATE_FORMAT(
                        CURRENT_DATE(),
                        '%%Y-%%m-01'
                    ),
                    INTERVAL 1 MONTH
              )
        """, (empresa_id,))

        resultado = self.cursor.fetchone() or {}

        total_mes = int(
            resultado.get("total_mes") or 0
        )

        concluidas_mes = int(
            resultado.get("concluidas_mes") or 0
        )

        if total_mes == 0:
            return 100

        return round(
            (concluidas_mes / total_mes) * 100,
            1
        )

    def ranking_unidades(self, empresa_id):
        self.cursor.execute("""
            SELECT
                u.nome,
                COUNT(d.id) AS total

            FROM denuncias d

            INNER JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id

            WHERE d.empresa_id = %s

            GROUP BY
                u.id,
                u.nome

            ORDER BY
                total DESC,
                u.nome ASC

            LIMIT 5
        """, (empresa_id,))

        return self.cursor.fetchall()

    def ranking_categorias(self, empresa_id):
        self.cursor.execute("""
            SELECT
                COALESCE(
                    NULLIF(TRIM(categoria), ''),
                    'Não informada'
                ) AS categoria,

                COUNT(id) AS total

            FROM denuncias

            WHERE empresa_id = %s

            GROUP BY
                COALESCE(
                    NULLIF(TRIM(categoria), ''),
                    'Não informada'
                )

            ORDER BY
                total DESC,
                categoria ASC

            LIMIT 5
        """, (empresa_id,))

        return self.cursor.fetchall()

    def denuncias_kanban(self, empresa_id):
        self.cursor.execute("""
            SELECT
                d.id,
                d.protocolo,
                d.tipo,
                d.categoria,
                d.criticidade,
                d.status,
                COALESCE(
                    d.etapa_atual,
                    'TRIAGEM'
                ) AS etapa_atual,
                d.criado_em,
                d.responsavel_id,
                u.nome AS unidade,
                s.nome AS setor,
                usr.nome AS responsavel

            FROM denuncias d

            INNER JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id

            LEFT JOIN setores s
                ON s.id = d.setor_id
               AND s.empresa_id = d.empresa_id

            LEFT JOIN usuarios usr
                ON usr.id = d.responsavel_id
               AND (
                    usr.empresa_id = d.empresa_id
                    OR usr.empresa_id IS NULL
               )

            WHERE d.empresa_id = %s
              AND d.status NOT IN (
                    'CONCLUIDA',
                    'ARQUIVADA'
              )

            ORDER BY
                CASE COALESCE(
                    d.criticidade,
                    ''
                )
                    WHEN 'Alta' THEN 1
                    WHEN 'Média' THEN 2
                    WHEN 'Media' THEN 2
                    WHEN 'Baixa' THEN 3
                    ELSE 4
                END,
                d.criado_em ASC
        """, (empresa_id,))

        return self.cursor.fetchall()

    def resumo_kanban_por_etapa(self, empresa_id):
        self.cursor.execute("""
            SELECT
                COALESCE(
                    etapa_atual,
                    'TRIAGEM'
                ) AS etapa,

                COUNT(*) AS total,

                SUM(
                    CASE
                        WHEN criticidade = 'Alta'
                        THEN 1
                        ELSE 0
                    END
                ) AS criticas,

                SUM(
                    CASE
                        WHEN criado_em <= DATE_SUB(
                            NOW(),
                            INTERVAL 7 DAY
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS mais_7_dias

            FROM denuncias

            WHERE empresa_id = %s
              AND status NOT IN (
                    'CONCLUIDA',
                    'ARQUIVADA'
              )

            GROUP BY
                COALESCE(
                    etapa_atual,
                    'TRIAGEM'
                )
        """, (empresa_id,))

        return self.cursor.fetchall()

    def alertas_denuncias_criticas_sem_responsavel(
        self,
        empresa_id,
        limite=5
    ):
        limite = self._limite_seguro(limite)

        self.cursor.execute("""
            SELECT
                d.id,
                d.protocolo,
                d.tipo,
                d.categoria,
                d.criticidade,
                d.status,
                COALESCE(
                    d.etapa_atual,
                    'TRIAGEM'
                ) AS etapa_atual,
                d.criado_em,
                u.nome AS unidade,
                s.nome AS setor

            FROM denuncias d

            INNER JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id

            LEFT JOIN setores s
                ON s.id = d.setor_id
               AND s.empresa_id = d.empresa_id

            WHERE d.empresa_id = %s
              AND d.status NOT IN (
                    'CONCLUIDA',
                    'ARQUIVADA'
              )
              AND d.criticidade = 'Alta'
              AND d.responsavel_id IS NULL

            ORDER BY d.criado_em ASC

            LIMIT %s
        """, (
            empresa_id,
            limite
        ))

        return self.cursor.fetchall()

    def alertas_denuncias_sem_responsavel(
        self,
        empresa_id,
        limite=5
    ):
        limite = self._limite_seguro(limite)

        self.cursor.execute("""
            SELECT
                d.id,
                d.protocolo,
                d.tipo,
                d.categoria,
                d.criticidade,
                d.status,
                COALESCE(
                    d.etapa_atual,
                    'TRIAGEM'
                ) AS etapa_atual,
                d.criado_em,
                u.nome AS unidade,
                s.nome AS setor

            FROM denuncias d

            INNER JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id

            LEFT JOIN setores s
                ON s.id = d.setor_id
               AND s.empresa_id = d.empresa_id

            WHERE d.empresa_id = %s
              AND d.status NOT IN (
                    'CONCLUIDA',
                    'ARQUIVADA'
              )
              AND d.responsavel_id IS NULL

            ORDER BY
                CASE COALESCE(
                    d.criticidade,
                    ''
                )
                    WHEN 'Alta' THEN 1
                    WHEN 'Média' THEN 2
                    WHEN 'Media' THEN 2
                    WHEN 'Baixa' THEN 3
                    ELSE 4
                END,
                d.criado_em ASC

            LIMIT %s
        """, (
            empresa_id,
            limite
        ))

        return self.cursor.fetchall()

    def alertas_denuncias_paradas_mais_7_dias(
        self,
        empresa_id,
        limite=5
    ):
        limite = self._limite_seguro(limite)

        self.cursor.execute("""
            SELECT
                d.id,
                d.protocolo,
                d.tipo,
                d.categoria,
                d.criticidade,
                d.status,
                COALESCE(
                    d.etapa_atual,
                    'TRIAGEM'
                ) AS etapa_atual,
                d.criado_em,

                TIMESTAMPDIFF(
                    DAY,
                    d.criado_em,
                    NOW()
                ) AS dias_aberta,

                u.nome AS unidade,
                s.nome AS setor,
                usr.nome AS responsavel

            FROM denuncias d

            INNER JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id

            LEFT JOIN setores s
                ON s.id = d.setor_id
               AND s.empresa_id = d.empresa_id

            LEFT JOIN usuarios usr
                ON usr.id = d.responsavel_id
               AND (
                    usr.empresa_id = d.empresa_id
                    OR usr.empresa_id IS NULL
               )

            WHERE d.empresa_id = %s
              AND d.status NOT IN (
                    'CONCLUIDA',
                    'ARQUIVADA'
              )
              AND d.criado_em <= DATE_SUB(
                    NOW(),
                    INTERVAL 7 DAY
              )

            ORDER BY d.criado_em ASC

            LIMIT %s
        """, (
            empresa_id,
            limite
        ))

        return self.cursor.fetchall()

    def alertas_denuncias_criticas_antigas(
        self,
        empresa_id,
        limite=5
    ):
        limite = self._limite_seguro(limite)

        self.cursor.execute("""
            SELECT
                d.id,
                d.protocolo,
                d.tipo,
                d.categoria,
                d.criticidade,
                d.status,
                COALESCE(
                    d.etapa_atual,
                    'TRIAGEM'
                ) AS etapa_atual,
                d.criado_em,

                TIMESTAMPDIFF(
                    DAY,
                    d.criado_em,
                    NOW()
                ) AS dias_aberta,

                u.nome AS unidade,
                s.nome AS setor,
                usr.nome AS responsavel

            FROM denuncias d

            INNER JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id

            LEFT JOIN setores s
                ON s.id = d.setor_id
               AND s.empresa_id = d.empresa_id

            LEFT JOIN usuarios usr
                ON usr.id = d.responsavel_id
               AND (
                    usr.empresa_id = d.empresa_id
                    OR usr.empresa_id IS NULL
               )

            WHERE d.empresa_id = %s
              AND d.status NOT IN (
                    'CONCLUIDA',
                    'ARQUIVADA'
              )
              AND d.criticidade = 'Alta'
              AND d.criado_em <= DATE_SUB(
                    NOW(),
                    INTERVAL 3 DAY
              )

            ORDER BY d.criado_em ASC

            LIMIT %s
        """, (
            empresa_id,
            limite
        ))

        return self.cursor.fetchall()

    def alertas_planos_acao_vencidos(
        self,
        empresa_id,
        limite=5
    ):
        limite = self._limite_seguro(limite)

        self.cursor.execute("""
            SELECT
                p.id,
                p.denuncia_id,
                p.titulo,
                p.responsavel,
                p.prazo,
                p.status,
                d.protocolo,
                d.criticidade,
                COALESCE(
                    d.etapa_atual,
                    'TRIAGEM'
                ) AS etapa_atual,
                u.nome AS unidade

            FROM planos_acao p

            INNER JOIN denuncias d
                ON d.id = p.denuncia_id
               AND d.empresa_id = p.empresa_id

            INNER JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id

            WHERE p.empresa_id = %s
              AND p.prazo < CURRENT_DATE()
              AND p.status NOT IN (
                    'CONCLUIDA',
                    'CANCELADA'
              )

            ORDER BY p.prazo ASC

            LIMIT %s
        """, (
            empresa_id,
            limite
        ))

        return self.cursor.fetchall()

    def alertas_planos_acao_vencem_amanha(
        self,
        empresa_id,
        limite=5
    ):
        limite = self._limite_seguro(limite)

        self.cursor.execute("""
            SELECT
                p.id,
                p.denuncia_id,
                p.titulo,
                p.responsavel,
                p.prazo,
                p.status,
                d.protocolo,
                d.criticidade,
                COALESCE(
                    d.etapa_atual,
                    'TRIAGEM'
                ) AS etapa_atual,
                u.nome AS unidade

            FROM planos_acao p

            INNER JOIN denuncias d
                ON d.id = p.denuncia_id
               AND d.empresa_id = p.empresa_id

            INNER JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id

            WHERE p.empresa_id = %s
              AND p.prazo = DATE_ADD(
                    CURRENT_DATE(),
                    INTERVAL 1 DAY
              )
              AND p.status NOT IN (
                    'CONCLUIDA',
                    'CANCELADA'
              )

            ORDER BY p.prazo ASC

            LIMIT %s
        """, (
            empresa_id,
            limite
        ))

        return self.cursor.fetchall()

    def alertas_denuncias_em_encerramento(
        self,
        empresa_id,
        limite=5
    ):
        limite = self._limite_seguro(limite)

        self.cursor.execute("""
            SELECT
                d.id,
                d.protocolo,
                d.tipo,
                d.categoria,
                d.criticidade,
                d.status,
                COALESCE(
                    d.etapa_atual,
                    'TRIAGEM'
                ) AS etapa_atual,
                d.criado_em,
                u.nome AS unidade,
                s.nome AS setor,
                usr.nome AS responsavel

            FROM denuncias d

            INNER JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id

            LEFT JOIN setores s
                ON s.id = d.setor_id
               AND s.empresa_id = d.empresa_id

            LEFT JOIN usuarios usr
                ON usr.id = d.responsavel_id
               AND (
                    usr.empresa_id = d.empresa_id
                    OR usr.empresa_id IS NULL
               )

            WHERE d.empresa_id = %s
              AND d.status NOT IN (
                    'CONCLUIDA',
                    'ARQUIVADA'
              )
              AND COALESCE(
                    d.etapa_atual,
                    'TRIAGEM'
              ) = 'ENCERRAMENTO'

            ORDER BY d.criado_em ASC

            LIMIT %s
        """, (
            empresa_id,
            limite
        ))

        return self.cursor.fetchall()

    def radar_riscos(self, empresa_id):
        self.cursor.execute("""
            SELECT
                COALESCE(
                    NULLIF(TRIM(categoria), ''),
                    NULLIF(TRIM(tipo), ''),
                    'Não informada'
                ) AS categoria,

                COUNT(*) AS total,

                SUM(
                    CASE
                        WHEN criticidade = 'Alta'
                        THEN 1
                        ELSE 0
                    END
                ) AS criticas,

                SUM(
                    CASE
                        WHEN status NOT IN (
                            'CONCLUIDA',
                            'ARQUIVADA'
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS em_aberto,

                SUM(
                    CASE
                        WHEN status NOT IN (
                            'CONCLUIDA',
                            'ARQUIVADA'
                        )
                         AND criado_em <= DATE_SUB(
                            NOW(),
                            INTERVAL 7 DAY
                         )
                        THEN 1
                        ELSE 0
                    END
                ) AS mais_7_dias,

                COALESCE(
                    ROUND(
                        AVG(
                            CASE
                                WHEN status NOT IN (
                                    'CONCLUIDA',
                                    'ARQUIVADA'
                                )
                                THEN TIMESTAMPDIFF(
                                    DAY,
                                    criado_em,
                                    NOW()
                                )
                                ELSE NULL
                            END
                        ),
                        1
                    ),
                    0
                ) AS media_dias_aberta

            FROM denuncias

            WHERE empresa_id = %s

            GROUP BY
                COALESCE(
                    NULLIF(TRIM(categoria), ''),
                    NULLIF(TRIM(tipo), ''),
                    'Não informada'
                )

            ORDER BY
                total DESC,
                categoria ASC
        """, (empresa_id,))

        return self.cursor.fetchall()

    def ranking_turnos(self, empresa_id):
        self.cursor.execute("""
            SELECT
                t.id,
                t.nome,
                COUNT(d.id) AS total

            FROM denuncias d

            INNER JOIN turnos t
                ON t.id = d.turno_id
               AND t.empresa_id = d.empresa_id

            WHERE d.empresa_id = %s
              AND d.turno_id IS NOT NULL

            GROUP BY
                t.id,
                t.nome

            ORDER BY
                total DESC,
                t.nome ASC
        """, (empresa_id,))

        return self.cursor.fetchall()

    def denuncias_por_turno_e_status(self, empresa_id):
        self.cursor.execute("""
            SELECT
                t.id,
                t.nome,
                COUNT(d.id) AS total,

                SUM(
                    CASE
                        WHEN d.status IN (
                            'NOVA',
                            'EM_ANALISE'
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS em_aberto,

                SUM(
                    CASE
                        WHEN d.status = 'CONCLUIDA'
                        THEN 1
                        ELSE 0
                    END
                ) AS concluidas,

                SUM(
                    CASE
                        WHEN d.criticidade = 'Alta'
                         AND d.status IN (
                            'NOVA',
                            'EM_ANALISE'
                         )
                        THEN 1
                        ELSE 0
                    END
                ) AS criticas_abertas,

                SUM(
                    CASE
                        WHEN d.status IN (
                            'NOVA',
                            'EM_ANALISE'
                        )
                         AND d.criado_em <= DATE_SUB(
                            NOW(),
                            INTERVAL 7 DAY
                         )
                        THEN 1
                        ELSE 0
                    END
                ) AS mais_7_dias

            FROM denuncias d

            INNER JOIN turnos t
                ON t.id = d.turno_id
               AND t.empresa_id = d.empresa_id

            WHERE d.empresa_id = %s
              AND d.turno_id IS NOT NULL

            GROUP BY
                t.id,
                t.nome

            ORDER BY
                total DESC,
                t.nome ASC
        """, (empresa_id,))

        return self.cursor.fetchall()

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None

        if self.conn:
            self.conn.close()
            self.conn = None