from db import get_connection


class AnexoRepository:

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def salvar(
        self,
        denuncia_id,
        empresa_id,
        nome_original,
        nome_fisico,
        caminho,
        mime_type,
        tamanho
    ):
        self.cursor.execute("""
            INSERT INTO denuncia_anexos (
                denuncia_id,
                empresa_id,
                nome_original,
                nome_fisico,
                caminho,
                mime_type,
                tamanho
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            denuncia_id,
            empresa_id,
            nome_original,
            nome_fisico,
            caminho,
            mime_type,
            tamanho
        ))

        self.conn.commit()

        return self.cursor.lastrowid

    def listar_por_denuncia(self, denuncia_id, empresa_id):
        self.cursor.execute("""
            SELECT
                id,
                nome_original,
                nome_fisico,
                caminho,
                mime_type,
                tamanho,
                criado_em
            FROM denuncia_anexos
            WHERE denuncia_id=%s
              AND empresa_id=%s
            ORDER BY criado_em
        """, (
            denuncia_id,
            empresa_id
        ))

        return self.cursor.fetchall()

    def contar_por_denuncia(self, denuncia_id):
        self.cursor.execute("""
            SELECT COUNT(*) total
            FROM denuncia_anexos
            WHERE denuncia_id=%s
        """, (denuncia_id,))

        return self.cursor.fetchone()["total"]

    def buscar_por_id(self, anexo_id, empresa_id):
        self.cursor.execute("""
            SELECT *
            FROM denuncia_anexos
            WHERE id=%s
              AND empresa_id=%s
            LIMIT 1
        """, (
            anexo_id,
            empresa_id
        ))

        return self.cursor.fetchone()

    def excluir(self, anexo_id, empresa_id):
        self.cursor.execute("""
            DELETE
            FROM denuncia_anexos
            WHERE id=%s
              AND empresa_id=%s
        """, (
            anexo_id,
            empresa_id
        ))

        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()