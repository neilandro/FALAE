from db import get_connection


class TriagemRepository:

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def buscar_denuncia(self, denuncia_id, empresa_id):
        self.cursor.execute("""
            SELECT
                id,
                empresa_id,
                protocolo,
                tipo,
                categoria,
                criticidade,
                prioridade,
                status,
                etapa_atual,
                responsavel_id,
                observacao_interna,
                parecer_triagem,
                triagem_concluida_em,
                triagem_realizada_por
            FROM denuncias
            WHERE id = %s
              AND empresa_id = %s
            LIMIT 1
        """, (denuncia_id, empresa_id))

        return self.cursor.fetchone()

    def concluir_triagem(
        self,
        denuncia_id,
        empresa_id,
        criticidade,
        categoria,
        responsavel_id,
        parecer_triagem,
        necessita_investigacao,
        prioridade,
        triagem_realizada_por,
        workflow_inicial=None
    ):

        self.cursor.execute("""
            UPDATE denuncias
            SET criticidade = %s,
                categoria = %s,
                responsavel_id = %s,
                parecer_triagem = %s,
                prioridade = %s,
                triagem_realizada_por = %s,
                triagem_concluida_em = NOW()
            WHERE id = %s
            AND empresa_id = %s
        """, (
            criticidade,
            categoria,
            responsavel_id,
            parecer_triagem,
            prioridade,
            triagem_realizada_por,
            denuncia_id,
            empresa_id
        ))

        self.conn.commit()

        return {
            "criticidade": criticidade,
            "categoria": categoria,
            "prioridade": prioridade,
            "responsavel_id": responsavel_id,
            "necessita_investigacao": necessita_investigacao,
            "triagem_concluida": True
        }
    
    def close(self):
        self.cursor.close()
        self.conn.close()