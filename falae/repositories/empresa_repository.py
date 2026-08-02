from db import get_connection


class EmpresaRepository:

    LIMITE_PADRAO = 10
    LIMITE_MAXIMO = 100

    @staticmethod
    def _normalizar_limite(limite):
        try:
            limite = int(limite)
        except (TypeError, ValueError):
            limite = EmpresaRepository.LIMITE_PADRAO

        return max(
            1,
            min(
                limite,
                EmpresaRepository.LIMITE_MAXIMO
            )
        )

    @staticmethod
    def _fechar_recursos(cursor=None, conn=None):
        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()

    @staticmethod
    def listar_por_assessoria(assessoria_id):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

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

                ORDER BY e.nome ASC
                """,
                (assessoria_id,)
            )

            return cursor.fetchall()

        finally:
            EmpresaRepository._fechar_recursos(
                cursor,
                conn
            )

    @staticmethod
    def obter_resumo_dashboard_assessoria(assessoria_id):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

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

            resultado = cursor.fetchone() or {}

            return {
                "total_empresas": int(
                    resultado.get("total_empresas") or 0
                ),
                "total_denuncias": int(
                    resultado.get("total_denuncias") or 0
                ),
                "total_usuarios": int(
                    resultado.get("total_usuarios") or 0
                ),
                "total_investigadores": int(
                    resultado.get("total_investigadores") or 0
                ),
                "denuncias_abertas": int(
                    resultado.get("denuncias_abertas") or 0
                ),
                "denuncias_criticas": int(
                    resultado.get("denuncias_criticas") or 0
                ),
                "denuncias_encerradas": int(
                    resultado.get("denuncias_encerradas") or 0
                )
            }

        finally:
            EmpresaRepository._fechar_recursos(
                cursor,
                conn
            )

    @staticmethod
    def listar_investigadores_assessoria(assessoria_id):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

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
                            WHEN d.status NOT IN (
                                'CONCLUIDA',
                                'ARQUIVADA'
                            )
                            THEN d.id
                            ELSE NULL
                        END
                    ) AS denuncias_em_aberto,

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
                    ) AS denuncias_criticas

                FROM usuarios u

                INNER JOIN empresas e
                    ON e.id = u.empresa_id
                   AND e.assessoria_id = %s

                LEFT JOIN denuncias d
                    ON d.empresa_id = u.empresa_id
                   AND d.responsavel_id = u.id

                WHERE u.ativo = 1
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
                    e.nome ASC,
                    u.nome ASC
                """,
                (assessoria_id,)
            )

            return cursor.fetchall()

        finally:
            EmpresaRepository._fechar_recursos(
                cursor,
                conn
            )

    @staticmethod
    def listar_denuncias_recentes_assessoria(
        assessoria_id,
        limite=10
    ):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            limite = EmpresaRepository._normalizar_limite(
                limite
            )

            cursor.execute(
                """
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
                    COALESCE(
                        d.etapa_atual,
                        'TRIAGEM'
                    ) AS etapa_atual,
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
                   AND e.assessoria_id = %s

                LEFT JOIN unidades u
                    ON u.id = d.unidade_id
                   AND u.empresa_id = d.empresa_id

                LEFT JOIN setores s
                    ON s.id = d.setor_id
                   AND s.empresa_id = d.empresa_id

                LEFT JOIN turnos t
                    ON t.id = d.turno_id
                   AND t.empresa_id = d.empresa_id

                LEFT JOIN usuarios responsavel
                    ON responsavel.id = d.responsavel_id
                   AND responsavel.empresa_id = d.empresa_id

                ORDER BY d.criado_em DESC

                LIMIT %s
                """,
                (
                    assessoria_id,
                    limite
                )
            )

            return cursor.fetchall()

        finally:
            EmpresaRepository._fechar_recursos(
                cursor,
                conn
            )

    @staticmethod
    def buscar_por_id_assessoria(
        empresa_id,
        assessoria_id
    ):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

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
            EmpresaRepository._fechar_recursos(
                cursor,
                conn
            )

    @staticmethod
    def buscar_por_slug(
        slug,
        ignorar_empresa_id=None
    ):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            if ignorar_empresa_id is None:
                cursor.execute(
                    """
                    SELECT
                        id,
                        assessoria_id,
                        nome,
                        slug

                    FROM empresas

                    WHERE slug = %s

                    LIMIT 1
                    """,
                    (slug,)
                )

            else:
                cursor.execute(
                    """
                    SELECT
                        id,
                        assessoria_id,
                        nome,
                        slug

                    FROM empresas

                    WHERE slug = %s
                      AND id <> %s

                    LIMIT 1
                    """,
                    (
                        slug,
                        ignorar_empresa_id
                    )
                )

            return cursor.fetchone()

        finally:
            EmpresaRepository._fechar_recursos(
                cursor,
                conn
            )

    @staticmethod
    def buscar_por_cnpj(
        assessoria_id,
        cnpj,
        ignorar_empresa_id=None
    ):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            if ignorar_empresa_id is None:
                cursor.execute(
                    """
                    SELECT
                        id,
                        assessoria_id,
                        nome,
                        cnpj

                    FROM empresas

                    WHERE assessoria_id = %s
                        AND cnpj = %s

                    LIMIT 1
                    """,
                    (assessoria_id,
                     cnpj)
                )

            else:
                cursor.execute(
                    """
                    SELECT
                        id,
                        assessoria_id,
                        nome,
                        cnpj

                    FROM empresas

                    WHERE assessoria_id = %s
                        AND cnpj = %s
                        AND id <> %s

                    LIMIT 1
                    """,
                    (
                       assessoria_id,
                       cnpj,
                       ignorar_empresa_id
                    )
                )

            return cursor.fetchone()

        finally:
            EmpresaRepository._fechar_recursos(
                cursor,
                conn
            )

    @staticmethod
    def existe_slug(
        slug,
        ignorar_empresa_id=None
    ):
        return EmpresaRepository.buscar_por_slug(
            slug,
            ignorar_empresa_id
        ) is not None

    @staticmethod
    def existe_cnpj(
        assessoria_id,
        cnpj,
        ignorar_empresa_id=None
    ):
        return (
            EmpresaRepository.buscar_por_cnpj(
                assessoria_id,
                cnpj,
                ignorar_empresa_id
            )
            is not None
        )

    @staticmethod
    def criar_para_assessoria(
        assessoria_id,
        nome,
        slug,
        cnpj,
        plano,
        token_publico
    ):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

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
            if conn is not None:
                conn.rollback()

            raise

        finally:
            EmpresaRepository._fechar_recursos(
                cursor,
                conn
            )

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
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

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

            atualizado = cursor.rowcount > 0

            conn.commit()

            return atualizado

        except Exception:
            if conn is not None:
                conn.rollback()

            raise

        finally:
            EmpresaRepository._fechar_recursos(
                cursor,
                conn
            )

    @staticmethod
    def buscar_por_id_super_admin(empresa_id):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

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

                LIMIT 1
                """,
                (empresa_id,)
            )

            return cursor.fetchone()

        finally:
            EmpresaRepository._fechar_recursos(
                cursor,
                conn
            )

    @staticmethod
    def buscar_por_id_global(empresa_id):
        """
        Compatibilidade com chamadas existentes.

        Este método não aplica escopo de assessoria e deve ser chamado
        somente por fluxos previamente protegidos para SUPER_ADMIN.
        """
        return EmpresaRepository.buscar_por_id_super_admin(
            empresa_id
        )


    @staticmethod
    def listar_global():
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    e.id,
                    e.assessoria_id,
                    e.nome,
                    e.slug,
                    e.cnpj,
                    e.logo,
                    e.plano,
                    e.ativa,
                    e.cidade,
                    e.estado,
                    e.criado_em,
                    e.atualizado_em,
                    a.nome AS assessoria,
                    COUNT(DISTINCT CASE WHEN u.ativo = 1 THEN u.id END) AS total_usuarios,
                    COUNT(DISTINCT d.id) AS total_denuncias,
                    COUNT(
                        DISTINCT CASE
                            WHEN d.criticidade = 'Alta'
                             AND d.status NOT IN ('CONCLUIDA', 'ARQUIVADA')
                            THEN d.id
                        END
                    ) AS total_criticas
                FROM empresas e
                LEFT JOIN assessorias a
                    ON a.id = e.assessoria_id
                LEFT JOIN usuarios u
                    ON u.empresa_id = e.id
                LEFT JOIN denuncias d
                    ON d.empresa_id = e.id
                GROUP BY
                    e.id,
                    e.assessoria_id,
                    e.nome,
                    e.slug,
                    e.cnpj,
                    e.logo,
                    e.plano,
                    e.ativa,
                    e.cidade,
                    e.estado,
                    e.criado_em,
                    e.atualizado_em,
                    a.nome
                ORDER BY e.nome ASC
                """
            )

            return cursor.fetchall()

        finally:
            EmpresaRepository._fechar_recursos(cursor, conn)

    @staticmethod
    def listar_assessorias_ativas():
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT id, nome
                FROM assessorias
                WHERE ativa = 1
                ORDER BY nome ASC
                """
            )

            return cursor.fetchall()

        finally:
            EmpresaRepository._fechar_recursos(cursor, conn)

    @staticmethod
    def buscar_dados_completos_global(empresa_id):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    e.*,
                    a.nome AS assessoria
                FROM empresas e
                LEFT JOIN assessorias a
                    ON a.id = e.assessoria_id
                WHERE e.id = %s
                LIMIT 1
                """,
                (empresa_id,)
            )

            return cursor.fetchone()

        finally:
            EmpresaRepository._fechar_recursos(cursor, conn)

    @staticmethod
    def criar_global(dados):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO empresas (
                    assessoria_id,
                    nome,
                    slug,
                    cnpj,
                    endereco,
                    numero,
                    complemento,
                    bairro,
                    cidade,
                    estado,
                    cep,
                    contato_nome,
                    contato_cargo,
                    contato_email,
                    contato_telefone,
                    contato_whatsapp,
                    plano,
                    token_publico,
                    ativa
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    dados.get("assessoria_id"),
                    dados.get("nome"),
                    dados.get("slug"),
                    dados.get("cnpj"),
                    dados.get("endereco"),
                    dados.get("numero"),
                    dados.get("complemento"),
                    dados.get("bairro"),
                    dados.get("cidade"),
                    dados.get("estado"),
                    dados.get("cep"),
                    dados.get("contato_nome"),
                    dados.get("contato_cargo"),
                    dados.get("contato_email"),
                    dados.get("contato_telefone"),
                    dados.get("contato_whatsapp"),
                    dados.get("plano"),
                    dados.get("token_publico"),
                    dados.get("ativa", 1)
                )
            )

            empresa_id = cursor.lastrowid
            conn.commit()
            return empresa_id

        except Exception:
            if conn is not None:
                conn.rollback()
            raise

        finally:
            EmpresaRepository._fechar_recursos(cursor, conn)

    @staticmethod
    def atualizar_global(empresa_id, dados):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE empresas
                SET
                    assessoria_id = %s,
                    nome = %s,
                    slug = %s,
                    cnpj = %s,
                    endereco = %s,
                    numero = %s,
                    complemento = %s,
                    bairro = %s,
                    cidade = %s,
                    estado = %s,
                    cep = %s,
                    contato_nome = %s,
                    contato_cargo = %s,
                    contato_email = %s,
                    contato_telefone = %s,
                    contato_whatsapp = %s,
                    plano = %s,
                    ativa = %s,
                    atualizado_em = NOW()
                WHERE id = %s
                """,
                (
                    dados.get("assessoria_id"),
                    dados.get("nome"),
                    dados.get("slug"),
                    dados.get("cnpj"),
                    dados.get("endereco"),
                    dados.get("numero"),
                    dados.get("complemento"),
                    dados.get("bairro"),
                    dados.get("cidade"),
                    dados.get("estado"),
                    dados.get("cep"),
                    dados.get("contato_nome"),
                    dados.get("contato_cargo"),
                    dados.get("contato_email"),
                    dados.get("contato_telefone"),
                    dados.get("contato_whatsapp"),
                    dados.get("plano"),
                    dados.get("ativa", 1),
                    empresa_id
                )
            )

            atualizado = cursor.rowcount > 0
            conn.commit()
            return atualizado

        except Exception:
            if conn is not None:
                conn.rollback()
            raise

        finally:
            EmpresaRepository._fechar_recursos(cursor, conn)

    @staticmethod
    def obter_totais_global(empresa_id):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    (
                        SELECT COUNT(*)
                        FROM usuarios
                        WHERE empresa_id = %s
                          AND ativo = 1
                          AND perfil <> 'SUPER_ADMIN'
                    ) AS total_usuarios,
                    (
                        SELECT COUNT(*)
                        FROM unidades
                        WHERE empresa_id = %s
                          AND ativa = 1
                    ) AS total_unidades,
                    (
                        SELECT COUNT(*)
                        FROM setores
                        WHERE empresa_id = %s
                          AND ativo = 1
                    ) AS total_setores,
                    (
                        SELECT COUNT(*)
                        FROM denuncias
                        WHERE empresa_id = %s
                    ) AS total_denuncias
                """,
                (empresa_id, empresa_id, empresa_id, empresa_id)
            )

            return cursor.fetchone() or {
                "total_usuarios": 0,
                "total_unidades": 0,
                "total_setores": 0,
                "total_denuncias": 0
            }

        finally:
            EmpresaRepository._fechar_recursos(cursor, conn)
