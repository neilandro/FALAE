from db import get_connection


class PlanoAcaoRepository:

    @staticmethod
    def listar_por_denuncia(empresa_id, denuncia_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, titulo, descricao, responsavel, prazo, status, criado_em, atualizado_em
            FROM planos_acao
            WHERE empresa_id = %s
              AND denuncia_id = %s
            ORDER BY criado_em DESC
        """, (empresa_id, denuncia_id))

        planos = cursor.fetchall()
        cursor.close()
        conn.close()

        return planos


    @staticmethod
    def buscar_duplicado_recente(empresa_id, denuncia_id, titulo, responsavel, prazo, status):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, denuncia_id
            FROM planos_acao
            WHERE empresa_id = %s
              AND denuncia_id = %s
              AND titulo = %s
              AND COALESCE(responsavel, '') = COALESCE(%s, '')
              AND COALESCE(prazo, '1900-01-01') = COALESCE(%s, '1900-01-01')
              AND status = %s
              AND criado_em >= (NOW() - INTERVAL 15 SECOND)
            ORDER BY id DESC
            LIMIT 1
        """, (
            empresa_id, denuncia_id, titulo, responsavel, prazo, status
        ))

        plano = cursor.fetchone()
        cursor.close()
        conn.close()

        return plano

    @staticmethod
    def resumo_por_denuncia(empresa_id, denuncia_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'CONCLUIDA' THEN 1 ELSE 0 END) AS concluidos,
                SUM(CASE WHEN status NOT IN ('CONCLUIDA', 'CANCELADA') THEN 1 ELSE 0 END) AS pendentes
            FROM planos_acao
            WHERE empresa_id = %s
              AND denuncia_id = %s
        """, (empresa_id, denuncia_id))

        resumo = cursor.fetchone() or {}
        cursor.close()
        conn.close()

        return {
            "total": int(resumo.get("total") or 0),
            "concluidos": int(resumo.get("concluidos") or 0),
            "pendentes": int(resumo.get("pendentes") or 0)
        }

    @staticmethod
    def buscar_por_id(empresa_id, plano_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, empresa_id, denuncia_id, titulo, descricao, responsavel, prazo, status
            FROM planos_acao
            WHERE id = %s
              AND empresa_id = %s
            LIMIT 1
        """, (plano_id, empresa_id))

        plano = cursor.fetchone()
        cursor.close()
        conn.close()

        return plano

    @staticmethod
    def criar(empresa_id, denuncia_id, titulo, descricao, responsavel, prazo, status, criado_por):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO planos_acao (
                empresa_id, denuncia_id, titulo, descricao,
                responsavel, prazo, status, criado_por
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            empresa_id, denuncia_id, titulo, descricao,
            responsavel, prazo, status, criado_por
        ))

        plano_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        return plano_id

    @staticmethod
    def atualizar(empresa_id, plano_id, titulo, descricao, responsavel, prazo, status):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE planos_acao
            SET titulo = %s,
                descricao = %s,
                responsavel = %s,
                prazo = %s,
                status = %s,
                atualizado_em = NOW()
            WHERE id = %s
              AND empresa_id = %s
        """, (
            titulo, descricao, responsavel, prazo, status,
            plano_id, empresa_id
        ))

        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def excluir(empresa_id, plano_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM planos_acao
            WHERE id = %s
              AND empresa_id = %s
        """, (plano_id, empresa_id))

        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def concluir(empresa_id, plano_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE planos_acao
            SET status = 'CONCLUIDA',
                concluido_em = NOW(),
                atualizado_em = NOW()
            WHERE id = %s
              AND empresa_id = %s
        """, (plano_id, empresa_id))

        conn.commit()
        cursor.close()
        conn.close()