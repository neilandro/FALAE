from db import get_connection


class EmpresaRepository:

    @staticmethod
    def listar_por_assessoria(
        assessoria_id
    ):
        conn = get_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        try:
            cursor.execute(
                """
                SELECT
                    e.id,
                    e.nome,
                    e.slug,
                    e.cnpj,
                    e.logo,
                    e.plano,
                    e.ativa,
                    e.criado_em,

                    COUNT(
                        DISTINCT CASE
                            WHEN u.ativo = 1
                            THEN u.id
                            ELSE NULL
                        END
                    ) AS total_usuarios,

                    COUNT(
                        DISTINCT d.id
                    ) AS total_denuncias,

                    COUNT(
                        DISTINCT CASE
                            WHEN d.status NOT IN (
                                'CONCLUIDA',
                                'ARQUIVADA'
                            )
                            THEN d.id
                            ELSE NULL
                        END
                    ) AS denuncias_abertas,

                    COUNT(
                        DISTINCT CASE
                            WHEN d.criticidade = 'Alta'
                             AND d.status NOT IN (
                                'CONCLUIDA',
                                'ARQUIVADA'
                             )
                            THEN d.id
                            ELSE NULL
                        END
                    ) AS denuncias_criticas,

                    COUNT(
                        DISTINCT CASE
                            WHEN u.ativo = 1
                             AND u.perfil = 'INVESTIGADOR'
                            THEN u.id
                            ELSE NULL
                        END
                    ) AS total_investigadores

                FROM empresas e

                LEFT JOIN usuarios u
                    ON u.empresa_id = e.id

                LEFT JOIN denuncias d
                    ON d.empresa_id = e.id

                WHERE e.assessoria_id = %s

                GROUP BY
                    e.id,
                    e.nome,
                    e.slug,
                    e.cnpj,
                    e.logo,
                    e.plano,
                    e.ativa,
                    e.criado_em

                ORDER BY e.nome
                """,
                (assessoria_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obter_resumo_dashboard_assessoria(
        assessoria_id
    ):
        conn = get_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        try:
            cursor.execute(
                """
                SELECT
                    COUNT(
                        DISTINCT e.id
                    ) AS total_empresas,

                    COUNT(
                        DISTINCT d.id
                    ) AS total_denuncias,

                    COUNT(
                        DISTINCT CASE
                            WHEN u.ativo = 1
                            THEN u.id
                            ELSE NULL
                        END
                    ) AS total_usuarios,

                    COUNT(
                        DISTINCT CASE
                            WHEN u.ativo = 1
                             AND u.perfil = 'INVESTIGADOR'
                            THEN u.id
                            ELSE NULL
                        END
                    ) AS total_investigadores,

                    COUNT(
                        DISTINCT CASE
                            WHEN d.status NOT IN (
                                'CONCLUIDA',
                                'ARQUIVADA'
                            )
                            THEN d.id
                            ELSE NULL
                        END
                    ) AS denuncias_abertas,

                    COUNT(
                        DISTINCT CASE
                            WHEN d.criticidade = 'Alta'
                             AND d.status NOT IN (
                                'CONCLUIDA',
                                'ARQUIVADA'
                             )
                            THEN d.id
                            ELSE NULL
                        END
                    ) AS denuncias_criticas,

                    COUNT(
                        DISTINCT CASE
                            WHEN d.status IN (
                                'CONCLUIDA',
                                'ARQUIVADA'
                            )
                            THEN d.id
                            ELSE NULL
                        END
                    ) AS denuncias_encerradas

                FROM empresas e

                LEFT JOIN usuarios u
                    ON u.empresa_id = e.id

                LEFT JOIN denuncias d
                    ON d.empresa_id = e.id

                WHERE e.assessoria_id = %s
                """,
                (assessoria_id,)
            )

            resultado = cursor.fetchone()

            return resultado or {
                "total_empresas": 0,
                "total_denuncias": 0,
                "total_usuarios": 0,
                "total_investigadores": 0,
                "denuncias_abertas": 0,
                "denuncias_criticas": 0,
                "denuncias_encerradas": 0
            }

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_investigadores_assessoria(
        assessoria_id
    ):
        conn = get_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        try:
            cursor.execute(
                """
                SELECT
                    u.id,
                    u.nome,
                    u.email,
                    u.celular,
                    u.whatsapp,
                    u.perfil,
                    u.ativo,
                    u.empresa_id,
                    e.nome AS empresa_nome,

                    COUNT(
                        DISTINCT CASE
                            WHEN d.responsavel_id = u.id
                             AND d.status NOT IN (
                                'CONCLUIDA',
                                'ARQUIVADA'
                             )
                            THEN d.id
                            ELSE NULL
                        END
                    ) AS denuncias_em_aberto,

                    COUNT(
                        DISTINCT CASE
                            WHEN d.responsavel_id = u.id
                             AND d.criticidade = 'Alta'
                             AND d.status NOT IN (
                                'CONCLUIDA',
                                'ARQUIVADA'
                             )
                            THEN d.id
                            ELSE NULL
                        END
                    ) AS denuncias_criticas

                FROM usuarios u

                INNER JOIN empresas e
                    ON e.id = u.empresa_id

                LEFT JOIN denuncias d
                    ON d.empresa_id = e.id
                   AND d.responsavel_id = u.id

                WHERE e.assessoria_id = %s
                  AND u.ativo = 1
                  AND u.perfil IN (
                      'ADMIN_EMPRESA',
                      'GESTOR',
                      'INVESTIGADOR'
                  )

                GROUP BY
                    u.id,
                    u.nome,
                    u.email,
                    u.celular,
                    u.whatsapp,
                    u.perfil,
                    u.ativo,
                    u.empresa_id,
                    e.nome

                ORDER BY
                    e.nome,
                    u.nome
                """,
                (assessoria_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_denuncias_recentes_assessoria(
        assessoria_id,
        limite=10
    ):
        conn = get_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        try:
            try:
                limite = int(
                    limite
                )

            except (
                TypeError,
                ValueError
            ):
                limite = 10

            limite = max(
                1,
                min(
                    limite,
                    100
                )
            )

            cursor.execute(
                f"""
                SELECT
                    d.id,
                    d.protocolo,
                    d.tipo,
                    COALESCE(
                        NULLIF(
                            TRIM(d.categoria),
                            ''
                        ),
                        NULLIF(
                            TRIM(d.tipo),
                            ''
                        ),
                        'Não informada'
                    ) AS categoria,
                    COALESCE(
                        NULLIF(
                            TRIM(d.criticidade),
                            ''
                        ),
                        'Não informada'
                    ) AS criticidade,
                    d.status,
                    d.etapa_atual,
                    d.criado_em,
                    d.empresa_id,

                    e.nome AS empresa_nome,

                    u.nome AS unidade_nome,

                    COALESCE(
                        s.nome,
                        'Não informado'
                    ) AS setor_nome,

                    COALESCE(
                        t.nome,
                        'Não informado'
                    ) AS turno_nome,

                    responsavel.nome AS responsavel_nome

                FROM denuncias d

                INNER JOIN empresas e
                    ON e.id = d.empresa_id

                LEFT JOIN unidades u
                    ON u.id = d.unidade_id
                   AND u.empresa_id = d.empresa_id

                LEFT JOIN setores s
                    ON s.id = d.setor_id

                LEFT JOIN turnos t
                    ON t.id = d.turno_id
                   AND t.empresa_id = d.empresa_id

                LEFT JOIN usuarios responsavel
                    ON responsavel.id = d.responsavel_id
                   AND responsavel.empresa_id = d.empresa_id

                WHERE e.assessoria_id = %s

                ORDER BY d.criado_em DESC

                LIMIT {limite}
                """,
                (assessoria_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_id_assessoria(
        empresa_id,
        assessoria_id
    ):
        conn = get_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    assessoria_id,
                    nome,
                    slug,
                    cnpj,
                    logo,
                    plano,
                    ativa,
                    token_publico,
                    criado_em,
                    atualizado_em

                FROM empresas

                WHERE id = %s
                  AND assessoria_id = %s

                LIMIT 1
                """,
                (
                    empresa_id,
                    assessoria_id
                )
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def criar_para_assessoria(
        assessoria_id,
        nome,
        slug,
        cnpj,
        plano,
        token_publico
    ):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO empresas (
                    assessoria_id,
                    nome,
                    slug,
                    cnpj,
                    plano,
                    token_publico,
                    ativa
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    1
                )
                """,
                (
                    assessoria_id,
                    nome,
                    slug,
                    cnpj,
                    plano,
                    token_publico
                )
            )

            empresa_id = cursor.lastrowid

            conn.commit()

            return empresa_id

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar_por_assessoria(
        empresa_id,
        assessoria_id,
        nome,
        slug,
        cnpj,
        plano,
        ativa
    ):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE empresas

                SET
                    nome = %s,
                    slug = %s,
                    cnpj = %s,
                    plano = %s,
                    ativa = %s,
                    atualizado_em = NOW()

                WHERE id = %s
                  AND assessoria_id = %s
                """,
                (
                    nome,
                    slug,
                    cnpj,
                    plano,
                    ativa,
                    empresa_id,
                    assessoria_id
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_id_global(
        empresa_id
    ):
        conn = get_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    assessoria_id,
                    nome,
                    slug,
                    cnpj,
                    logo,
                    plano,
                    ativa,
                    token_publico

                FROM empresas

                WHERE id = %s

                LIMIT 1
                """,
                (empresa_id,)
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()