from db import get_connection


class PlanoAcaoRepository:

    # =========================================================
    # LISTAGEM
    # =========================================================

    @staticmethod
    def listar_por_denuncia(empresa_id, denuncia_id):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    p.id,
                    p.titulo,
                    p.descricao,
                    p.responsavel,
                    p.prazo,
                    p.status,
                    p.criado_em,
                    p.atualizado_em
                FROM planos_acao p
                INNER JOIN denuncias d
                    ON d.id = p.denuncia_id
                   AND d.empresa_id = p.empresa_id
                WHERE p.empresa_id = %s
                  AND p.denuncia_id = %s
                ORDER BY p.criado_em DESC
            """, (
                empresa_id,
                denuncia_id
            ))

            return cursor.fetchall()

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # =========================================================
    # DUPLICIDADE
    # =========================================================

    @staticmethod
    def buscar_duplicado_recente(
        empresa_id,
        denuncia_id,
        titulo,
        responsavel,
        prazo,
        status
    ):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    p.id,
                    p.denuncia_id
                FROM planos_acao p
                INNER JOIN denuncias d
                    ON d.id = p.denuncia_id
                   AND d.empresa_id = p.empresa_id
                WHERE p.empresa_id = %s
                  AND p.denuncia_id = %s
                  AND p.titulo = %s
                  AND COALESCE(
                        p.responsavel,
                        ''
                  ) = COALESCE(%s, '')
                  AND COALESCE(
                        p.prazo,
                        '1900-01-01'
                  ) = COALESCE(%s, '1900-01-01')
                  AND p.status = %s
                  AND p.criado_em >= (
                        NOW() - INTERVAL 15 SECOND
                  )
                ORDER BY p.id DESC
                LIMIT 1
            """, (
                empresa_id,
                denuncia_id,
                titulo,
                responsavel,
                prazo,
                status
            ))

            return cursor.fetchone()

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # =========================================================
    # RESUMO
    # =========================================================

    @staticmethod
    def resumo_por_denuncia(empresa_id, denuncia_id):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    COUNT(*) AS total,

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
                    ) AS pendentes

                FROM planos_acao p
                INNER JOIN denuncias d
                    ON d.id = p.denuncia_id
                   AND d.empresa_id = p.empresa_id
                WHERE p.empresa_id = %s
                  AND p.denuncia_id = %s
            """, (
                empresa_id,
                denuncia_id
            ))

            resumo = cursor.fetchone() or {}

            return {
                "total": int(
                    resumo.get("total") or 0
                ),
                "concluidos": int(
                    resumo.get("concluidos") or 0
                ),
                "pendentes": int(
                    resumo.get("pendentes") or 0
                )
            }

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # =========================================================
    # BUSCA POR ID
    # =========================================================

    @staticmethod
    def buscar_por_id(empresa_id, plano_id):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    p.id,
                    p.empresa_id,
                    p.denuncia_id,
                    p.titulo,
                    p.descricao,
                    p.responsavel,
                    p.prazo,
                    p.status
                FROM planos_acao p
                INNER JOIN denuncias d
                    ON d.id = p.denuncia_id
                   AND d.empresa_id = p.empresa_id
                WHERE p.id = %s
                  AND p.empresa_id = %s
                LIMIT 1
            """, (
                plano_id,
                empresa_id
            ))

            return cursor.fetchone()

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    
    #CRIAÇÃO
    

    @staticmethod
    def criar(
        empresa_id,
        denuncia_id,
        titulo,
        descricao,
        responsavel,
        prazo,
        status,
        criado_por
    ):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            
            #A inserção só acontece quando a denúncia existe
            #e pertence à mesma empresa.

            #Isso impede a criação de um plano vinculado a uma
            #denúncia de outro tenant.
            
            cursor.execute("""
                INSERT INTO planos_acao (
                    empresa_id,
                    denuncia_id,
                    titulo,
                    descricao,
                    responsavel,
                    prazo,
                    status,
                    criado_por
                )
                SELECT
                    d.empresa_id,
                    d.id,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                FROM denuncias d
                WHERE d.id = %s
                  AND d.empresa_id = %s
            """, (
                titulo,
                descricao,
                responsavel,
                prazo,
                status,
                criado_por,
                denuncia_id,
                empresa_id
            ))

            if cursor.rowcount == 0:
                conn.rollback()

                raise ValueError(
                    "Denúncia não encontrada no escopo "
                    "da empresa."
                )

            plano_id = cursor.lastrowid

            conn.commit()

            return plano_id

        except Exception:
            if conn:
                conn.rollback()

            raise

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # =========================================================
    # ATUALIZAÇÃO
    # =========================================================

    @staticmethod
    def atualizar(
        empresa_id,
        plano_id,
        titulo,
        descricao,
        responsavel,
        prazo,
        status
    ):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            
            #O JOIN confirma que o plano está associado a uma
            #denúncia pertencente à mesma empresa.
            
            cursor.execute("""
                UPDATE planos_acao p
                INNER JOIN denuncias d
                    ON d.id = p.denuncia_id
                   AND d.empresa_id = p.empresa_id

                SET
                    p.titulo = %s,
                    p.descricao = %s,
                    p.responsavel = %s,
                    p.prazo = %s,
                    p.status = %s,
                    p.atualizado_em = NOW()

                WHERE p.id = %s
                  AND p.empresa_id = %s
            """, (
                titulo,
                descricao,
                responsavel,
                prazo,
                status,
                plano_id,
                empresa_id
            ))

            atualizado = cursor.rowcount > 0

            conn.commit()

            return atualizado

        except Exception:
            if conn:
                conn.rollback()

            raise

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # =========================================================
    # EXCLUSÃO
    # =========================================================

    @staticmethod
    def excluir(empresa_id, plano_id):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            
            #O plano somente é excluído quando existe uma
            #denúncia correspondente no mesmo tenant.
            
            cursor.execute("""
                DELETE p
                FROM planos_acao p
                INNER JOIN denuncias d
                    ON d.id = p.denuncia_id
                   AND d.empresa_id = p.empresa_id
                WHERE p.id = %s
                  AND p.empresa_id = %s
            """, (
                plano_id,
                empresa_id
            ))

            excluido = cursor.rowcount > 0

            conn.commit()

            return excluido

        except Exception:
            if conn:
                conn.rollback()

            raise

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # =========================================================
    # CONCLUSÃO
    # =========================================================

    @staticmethod
    def concluir(empresa_id, plano_id):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE planos_acao p
                INNER JOIN denuncias d
                    ON d.id = p.denuncia_id
                   AND d.empresa_id = p.empresa_id

                SET
                    p.status = 'CONCLUIDA',
                    p.concluido_em = COALESCE(
                        p.concluido_em,
                        NOW()
                    ),
                    p.atualizado_em = NOW()

                WHERE p.id = %s
                  AND p.empresa_id = %s
                  AND p.status <> 'CONCLUIDA'
            """, (
                plano_id,
                empresa_id
            ))

            concluido = cursor.rowcount > 0

            conn.commit()

            return concluido

        except Exception:
            if conn:
                conn.rollback()

            raise

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()