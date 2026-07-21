from db import get_connection


class InvestigadorRepository:

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def minhas_denuncias(self, empresa_id, usuario_id):
        self.cursor.execute("""
            SELECT
                d.id,
                d.protocolo,
                d.tipo,
                d.categoria,
                d.criticidade,
                d.status,
                COALESCE(d.etapa_atual, 'TRIAGEM') AS etapa_atual,
                d.criado_em,
                u.nome AS unidade,
                s.nome AS setor
            FROM denuncias d
            INNER JOIN unidades u ON u.id = d.unidade_id
            LEFT JOIN setores s ON s.id = d.setor_id
            WHERE d.empresa_id = %s
              AND d.responsavel_id = %s
              AND d.status NOT IN ('CONCLUIDA', 'ARQUIVADA')
            ORDER BY
                CASE COALESCE(d.criticidade, '')
                    WHEN 'Alta' THEN 1
                    WHEN 'Média' THEN 2
                    WHEN 'Media' THEN 2
                    WHEN 'Baixa' THEN 3
                    ELSE 4
                END,
                d.criado_em ASC
        """, (empresa_id, usuario_id))

        return self.cursor.fetchall()

    def total_criticas(self, empresa_id, usuario_id):
        self.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM denuncias
            WHERE empresa_id = %s
              AND responsavel_id = %s
              AND criticidade = 'Alta'
              AND status NOT IN ('CONCLUIDA', 'ARQUIVADA')
        """, (empresa_id, usuario_id))

        return self.cursor.fetchone()["total"]

    def total_abertas(self, empresa_id, usuario_id):
        self.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM denuncias
            WHERE empresa_id = %s
              AND responsavel_id = %s
              AND status NOT IN ('CONCLUIDA', 'ARQUIVADA')
        """, (empresa_id, usuario_id))

        return self.cursor.fetchone()["total"]

    def total_vencidas(self, empresa_id, usuario_id):
        self.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM denuncias
            WHERE empresa_id = %s
              AND responsavel_id = %s
              AND status NOT IN ('CONCLUIDA', 'ARQUIVADA')
              AND criado_em <= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """, (empresa_id, usuario_id))

        return self.cursor.fetchone()["total"]

    def total_concluidas_mes(self, empresa_id, usuario_id):
        self.cursor.execute("""
            SELECT COUNT(*) AS total
            FROM denuncias
            WHERE empresa_id = %s
              AND responsavel_id = %s
              AND status = 'CONCLUIDA'
              AND MONTH(criado_em) = MONTH(CURRENT_DATE())
              AND YEAR(criado_em) = YEAR(CURRENT_DATE())
        """, (empresa_id, usuario_id))

        return self.cursor.fetchone()["total"]

    def close(self):
        self.cursor.close()
        self.conn.close()