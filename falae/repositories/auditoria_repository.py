from db import get_connection


class AuditoriaRepository:

    @staticmethod
    def registrar(
        empresa_id,
        usuario_id,
        modulo,
        acao,
        registro_id=None,
        valor_antigo=None,
        valor_novo=None,
        ip=None,
        user_agent=None,
        request_id=None
    ):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO auditoria
            (
                empresa_id,
                usuario_id,
                modulo,
                acao,
                registro_id,
                valor_antigo,
                valor_novo,
                ip,
                user_agent,
                request_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            empresa_id,
            usuario_id,
            modulo,
            acao,
            registro_id,
            valor_antigo,
            valor_novo,
            ip,
            user_agent,
            request_id
        ))

        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def listar_por_registro(modulo, registro_id, empresa_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                a.id,
                a.modulo,
                a.acao,
                a.registro_id,
                a.valor_antigo,
                a.valor_novo,
                a.ip,
                a.user_agent,
                a.request_id,
                a.criado_em,
                u.nome AS usuario
            FROM auditoria a
            LEFT JOIN usuarios u ON a.usuario_id = u.id
            WHERE a.modulo = %s
              AND a.registro_id = %s
              AND a.empresa_id = %s
            ORDER BY a.criado_em DESC
        """, (
            modulo,
            registro_id,
            empresa_id
        ))

        historico = cursor.fetchall()

        cursor.close()
        conn.close()

        return historico

    @staticmethod
    def listar_ultimos_eventos(empresa_id, limite=5):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                a.id,
                a.modulo,
                a.acao,
                a.registro_id,
                a.criado_em,
                u.nome AS usuario
            FROM auditoria a
            LEFT JOIN usuarios u ON a.usuario_id = u.id
            WHERE a.empresa_id = %s
            ORDER BY a.criado_em DESC
            LIMIT %s
        """, (
            empresa_id,
            limite
        ))

        eventos = cursor.fetchall()

        cursor.close()
        conn.close()

        return eventos