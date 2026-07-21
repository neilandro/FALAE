from db import get_connection


class DenunciaRepository:

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def listar_denuncias(self, where_sql, params, order_by, per_page, offset):
        params_paginados = params + [per_page, offset]

        self.cursor.execute(f"""
            SELECT
                d.id,
                d.protocolo,
                d.tipo,
                d.categoria,
                d.criticidade,
                d.status,
                d.etapa_atual,
                d.responsavel_id,
                d.criado_em,
                u.nome AS unidade,
                s.nome AS setor,
                usr.nome AS responsavel
            FROM denuncias d
            INNER JOIN unidades u ON d.unidade_id = u.id
            LEFT JOIN setores s ON d.setor_id = s.id
            LEFT JOIN usuarios usr ON usr.id = d.responsavel_id
            WHERE {where_sql}
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
        """, params_paginados)

        return self.cursor.fetchall()

    def contar_denuncias(self, where_sql, params):
        self.cursor.execute(f"""
            SELECT COUNT(*) AS total
            FROM denuncias d
            INNER JOIN unidades u ON d.unidade_id = u.id
            LEFT JOIN setores s ON d.setor_id = s.id
            WHERE {where_sql}
        """, params)

        return self.cursor.fetchone()["total"]

    def buscar_por_id(self, denuncia_id, empresa_id):
        self.cursor.execute("""
            SELECT
                d.id,
                d.protocolo,
                d.tipo,
                d.categoria,
                d.criticidade,
                d.prioridade,
                d.status,
                d.etapa_atual,
                d.responsavel_id,
                d.descricao,
                d.local_ocorrencia,
                d.data_ocorrencia,
                d.observacao_interna,
                d.parecer_triagem,
                d.triagem_concluida_em,
                d.triagem_realizada_por,
                d.criado_em,
                d.data_encerramento,
                u.nome AS unidade,
                s.nome AS setor,
                usr.nome AS responsavel,
                triador.nome AS triador
            FROM denuncias d
            INNER JOIN unidades u ON d.unidade_id = u.id
            LEFT JOIN setores s ON d.setor_id = s.id
            LEFT JOIN usuarios usr ON usr.id = d.responsavel_id
            LEFT JOIN usuarios triador ON triador.id = d.triagem_realizada_por
            WHERE d.id = %s
              AND d.empresa_id = %s
            LIMIT 1
        """, (denuncia_id, empresa_id))

        return self.cursor.fetchone()

    def atualizar_responsavel(self, denuncia_id, empresa_id, responsavel_id):
        self.cursor.execute("""
            UPDATE denuncias
            SET responsavel_id = %s
            WHERE id = %s
              AND empresa_id = %s
        """, (responsavel_id, denuncia_id, empresa_id))

        self.conn.commit()

    def criar_etapa_workflow(
        self,
        denuncia_id,
        empresa_id,
        etapa,
        status_etapa="PENDENTE",
        responsavel_id=None,
        prazo_limite=None,
        iniciado_em=None,
        concluido_em=None,
        observacao=None
    ):
        self.cursor.execute("""
            INSERT INTO denuncia_workflow (
                denuncia_id,
                empresa_id,
                etapa,
                status_etapa,
                responsavel_id,
                prazo_limite,
                iniciado_em,
                concluido_em,
                observacao
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            denuncia_id,
            empresa_id,
            etapa,
            status_etapa,
            responsavel_id,
            prazo_limite,
            iniciado_em,
            concluido_em,
            observacao
        ))

        self.conn.commit()

        return self.cursor.lastrowid

    def listar_workflow(self, denuncia_id, empresa_id):
        self.cursor.execute("""
            SELECT
                w.id,
                w.denuncia_id,
                w.empresa_id,
                w.etapa,
                w.status_etapa,
                w.responsavel_id,
                w.prazo_limite,
                w.iniciado_em,
                w.concluido_em,
                w.observacao,
                w.criado_em,
                usr.nome AS responsavel
            FROM denuncia_workflow w
            LEFT JOIN usuarios usr ON usr.id = w.responsavel_id
            WHERE w.denuncia_id = %s
              AND w.empresa_id = %s
            ORDER BY w.id ASC
        """, (denuncia_id, empresa_id))

        return self.cursor.fetchall()

    def atualizar_etapa_atual(self, denuncia_id, empresa_id, etapa_atual):
        self.cursor.execute("""
            UPDATE denuncias
            SET etapa_atual = %s
            WHERE id = %s
            AND empresa_id = %s
        """, (
            etapa_atual,
            denuncia_id,
            empresa_id
        ))

        self.conn.commit()

        return self.cursor.rowcount > 0

    def concluir_etapa_workflow(self, workflow_id, empresa_id, observacao=None):
        self.cursor.execute("""
            UPDATE denuncia_workflow
            SET status_etapa = 'CONCLUIDA',
                concluido_em = NOW(),
                observacao = COALESCE(%s, observacao)
            WHERE id = %s
              AND empresa_id = %s
        """, (observacao, workflow_id, empresa_id))

        self.conn.commit()

    def concluir_etapa_atual_workflow(
        self,
        denuncia_id,
        empresa_id,
        etapa,
        observacao=None
    ):
        self.cursor.execute("""
            UPDATE denuncia_workflow
            SET status_etapa = 'CONCLUIDA',
                concluido_em = NOW(),
                observacao = COALESCE(%s, observacao)
            WHERE denuncia_id = %s
            AND empresa_id = %s
            AND etapa = %s
            AND status_etapa <> 'CONCLUIDA'
        """, (
            observacao,
            denuncia_id,
            empresa_id,
            etapa
        ))

        self.conn.commit()    

    def iniciar_etapa_workflow(self, workflow_id, empresa_id, responsavel_id=None):
        self.cursor.execute("""
            UPDATE denuncia_workflow
            SET status_etapa = 'EM_ANDAMENTO',
                iniciado_em = COALESCE(iniciado_em, NOW()),
                responsavel_id = COALESCE(%s, responsavel_id)
            WHERE id = %s
              AND empresa_id = %s
        """, (responsavel_id, workflow_id, empresa_id))

        self.conn.commit()

    def avancar_workflow(
        self,
        denuncia_id,
        empresa_id,
        etapa_atual,
        proxima_etapa,
        novo_status,
        usuario_id=None,
        observacao=None
    ):
        try:
            self.cursor.execute("""
                UPDATE denuncia_workflow
                SET status_etapa = 'CONCLUIDA',
                    concluido_em = NOW(),
                    observacao = COALESCE(%s, observacao)
                WHERE denuncia_id = %s
                  AND empresa_id = %s
                  AND etapa = %s
                  AND status_etapa <> 'CONCLUIDA'
            """, (
                observacao,
                denuncia_id,
                empresa_id,
                etapa_atual
            ))

            self.cursor.execute("""
                UPDATE denuncias
                SET etapa_atual = %s,
                    status = %s,
                    data_encerramento = CASE
                        WHEN %s IN ('CONCLUIDA', 'ARQUIVADA') THEN NOW()
                        ELSE data_encerramento
                    END
                WHERE id = %s
                  AND empresa_id = %s
            """, (
                proxima_etapa["etapa"],
                novo_status,
                novo_status,
                denuncia_id,
                empresa_id
            ))

            if self.cursor.rowcount == 0:
                raise ValueError("Denúncia não encontrada para avanço do workflow.")

            self.cursor.execute("""
                INSERT INTO denuncia_workflow (
                    denuncia_id,
                    empresa_id,
                    etapa,
                    status_etapa,
                    responsavel_id,
                    prazo_limite,
                    iniciado_em,
                    concluido_em,
                    observacao
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                denuncia_id,
                empresa_id,
                proxima_etapa["etapa"],
                proxima_etapa["status_etapa"],
                proxima_etapa.get("responsavel_id") or usuario_id,
                proxima_etapa.get("prazo_limite"),
                proxima_etapa.get("iniciado_em"),
                proxima_etapa.get("concluido_em"),
                proxima_etapa.get("observacao")
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except Exception:
            self.conn.rollback()
            raise

    def listar_unidades(self, empresa_id):
        self.cursor.execute("""
            SELECT id, nome
            FROM unidades
            WHERE empresa_id = %s
              AND ativa = 1
            ORDER BY nome
        """, (empresa_id,))

        return self.cursor.fetchall()

    def listar_categorias(self, empresa_id):
        self.cursor.execute("""
            SELECT DISTINCT categoria
            FROM denuncias
            WHERE empresa_id = %s
              AND categoria IS NOT NULL
              AND categoria <> ''
            ORDER BY categoria
        """, (empresa_id,))

        return self.cursor.fetchall()

    def listar_criticidades(self, empresa_id):
        self.cursor.execute("""
            SELECT DISTINCT criticidade
            FROM denuncias
            WHERE empresa_id = %s
              AND criticidade IS NOT NULL
              AND criticidade <> ''
            ORDER BY criticidade
        """, (empresa_id,))

        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()