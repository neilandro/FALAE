from db import get_connection


class AcompanhamentoRepository:

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def buscar_por_protocolo(self, protocolo):
        self.cursor.execute("""
            SELECT
                d.id,
                d.protocolo,
                d.status,
                d.etapa_atual,
                d.criado_em,
                d.triagem_concluida_em,
                d.data_encerramento,
                e.nome AS empresa
            FROM denuncias d
            INNER JOIN empresas e ON e.id = d.empresa_id
            WHERE d.protocolo = %s
            LIMIT 1
        """, (protocolo,))

        return self.cursor.fetchone()

    def close(self):
        self.cursor.close()
        self.conn.close()