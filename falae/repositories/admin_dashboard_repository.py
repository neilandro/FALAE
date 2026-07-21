from db import get_connection


class AdminDashboardRepository:

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def total_assessorias(self):
        self.cursor.execute("""
            SELECT COUNT(*) total
            FROM assessorias
            WHERE ativa = 1
        """)
        return self.cursor.fetchone()["total"]

    def total_empresas(self):
        self.cursor.execute("""
            SELECT COUNT(*) total
            FROM empresas
            WHERE ativa = 1
        """)
        return self.cursor.fetchone()["total"]

    def total_usuarios(self):
        self.cursor.execute("""
            SELECT COUNT(*) total
            FROM usuarios
            WHERE ativo = 1
        """)
        return self.cursor.fetchone()["total"]

    def total_denuncias(self):
        self.cursor.execute("""
            SELECT COUNT(*) total
            FROM denuncias
        """)
        return self.cursor.fetchone()["total"]

    def total_denuncias_criticas(self):
        self.cursor.execute("""
            SELECT COUNT(*) total
            FROM denuncias
            WHERE criticidade='ALTA'
              AND status<>'CONCLUIDA'
        """)
        return self.cursor.fetchone()["total"]

    def total_empresas_inativas(self):
        self.cursor.execute("""
            SELECT COUNT(*) total
            FROM empresas
            WHERE ativa = 0
        """)
        return self.cursor.fetchone()["total"]

    def total_assessorias_inativas(self):
        self.cursor.execute("""
            SELECT COUNT(*) total
            FROM assessorias
            WHERE ativa = 0
        """)
        return self.cursor.fetchone()["total"]

    def close(self):
        self.cursor.close()
        self.conn.close()

    def ultimas_assessorias(self, limite=5):
        self.cursor.execute("""
            SELECT
                id,
                nome,
                criado_em
            FROM assessorias
            ORDER BY criado_em DESC
            LIMIT %s
        """, (limite,))

        return self.cursor.fetchall()    
    
    def ultimas_empresas(self, limite=5):
        self.cursor.execute("""
            SELECT
                id,
                nome,
                criado_em
            FROM empresas
            ORDER BY criado_em DESC
            LIMIT %s
        """, (limite,))

        return self.cursor.fetchall()
    
    def ultimos_usuarios(self, limite=5):
        self.cursor.execute("""
            SELECT
                id,
                nome,
                perfil,
                criado_em
            FROM usuarios
            ORDER BY criado_em DESC
            LIMIT %s
        """, (limite,))

        return self.cursor.fetchall()
    
    def empresas_sem_admin(self):
        self.cursor.execute("""
            SELECT
                e.id,
                e.nome
            FROM empresas e
            LEFT JOIN usuarios u
                ON u.empresa_id = e.id
            AND u.perfil = 'ADMIN_EMPRESA'
            AND u.ativo = 1
            WHERE e.ativa = 1
            GROUP BY e.id, e.nome
            HAVING COUNT(u.id) = 0
            ORDER BY e.nome
        """)

        return self.cursor.fetchall()


    def assessorias_sem_empresas(self):
        self.cursor.execute("""
            SELECT
                a.id,
                a.nome
            FROM assessorias a
            LEFT JOIN empresas e
                ON e.assessoria_id = a.id
            AND e.ativa = 1
            WHERE a.ativa = 1
            GROUP BY a.id, a.nome
            HAVING COUNT(e.id) = 0
            ORDER BY a.nome
        """)

        return self.cursor.fetchall()