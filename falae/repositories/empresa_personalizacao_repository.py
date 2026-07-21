from typing import Any

from db import get_connection


class EmpresaPersonalizacaoRepository:
    """Acesso aos dados de personalização visual das empresas."""

    @staticmethod
    def buscar_por_empresa(
        empresa_id: int
    ) -> dict[str, Any] | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    ep.id,
                    ep.empresa_id,
                    ep.nome_canal,
                    ep.favicon,
                    ep.cor_primaria,
                    ep.cor_secundaria,
                    ep.mensagem_boas_vindas,
                    ep.texto_lgpd,
                    ep.termo_uso,
                    ep.mostrar_logo,
                    ep.mostrar_nome_empresa,
                    ep.criado_em,
                    ep.atualizado_em,

                    e.nome AS empresa_nome,
                    e.slug AS empresa_slug,
                    e.logo AS empresa_logo,
                    e.token_publico,
                    e.ativa AS empresa_ativa

                FROM empresa_personalizacao ep

                INNER JOIN empresas e
                    ON e.id = ep.empresa_id

                WHERE ep.empresa_id = %s

                LIMIT 1
                """,
                (empresa_id,)
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_slug(
        slug: str
    ) -> dict[str, Any] | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    ep.id,
                    ep.empresa_id,
                    ep.nome_canal,
                    ep.favicon,
                    ep.cor_primaria,
                    ep.cor_secundaria,
                    ep.mensagem_boas_vindas,
                    ep.texto_lgpd,
                    ep.termo_uso,
                    ep.mostrar_logo,
                    ep.mostrar_nome_empresa,
                    ep.criado_em,
                    ep.atualizado_em,

                    e.nome AS empresa_nome,
                    e.slug AS empresa_slug,
                    e.logo AS empresa_logo,
                    e.token_publico,
                    e.ativa AS empresa_ativa

                FROM empresas e

                LEFT JOIN empresa_personalizacao ep
                    ON ep.empresa_id = e.id

                WHERE LOWER(TRIM(e.slug)) = LOWER(TRIM(%s))

                LIMIT 1
                """,
                (slug,)
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_slug_empresa(
        empresa_id: int
    ) -> str | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    slug
                FROM empresas
                WHERE id = %s
                LIMIT 1
                """,
                (empresa_id,)
            )

            empresa = cursor.fetchone()

            if not empresa:
                return None

            return empresa["slug"]

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def slug_em_uso(
        slug: str,
        ignorar_empresa_id: int | None = None
    ) -> bool:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            sql = """
                SELECT
                    id
                FROM empresas
                WHERE LOWER(TRIM(slug)) = LOWER(TRIM(%s))
            """

            parametros: list[Any] = [
                slug
            ]

            if ignorar_empresa_id is not None:
                sql += """
                    AND id <> %s
                """

                parametros.append(
                    ignorar_empresa_id
                )

            sql += """
                LIMIT 1
            """

            cursor.execute(
                sql,
                tuple(parametros)
            )

            return cursor.fetchone() is not None

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar_slug_empresa(
        empresa_id: int,
        slug: str
    ) -> bool:
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE empresas
                SET slug = %s
                WHERE id = %s
                """,
                (
                    slug,
                    empresa_id
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
    def existe_para_empresa(
        empresa_id: int
    ) -> bool:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    id
                FROM empresa_personalizacao
                WHERE empresa_id = %s
                LIMIT 1
                """,
                (empresa_id,)
            )

            return cursor.fetchone() is not None

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def criar_padrao(
        empresa_id: int
    ) -> int:
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO empresa_personalizacao (
                    empresa_id,
                    nome_canal,
                    cor_primaria,
                    cor_secundaria,
                    mensagem_boas_vindas,
                    texto_lgpd,
                    termo_uso,
                    mostrar_logo,
                    mostrar_nome_empresa
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    empresa_id,
                    "Canal de Denúncias",
                    "#1F4E78",
                    "#163A5C",
                    (
                        "Este é um canal seguro para o registro de denúncias. "
                        "As informações serão tratadas com confidencialidade "
                        "e responsabilidade."
                    ),
                    (
                        "Os dados informados serão utilizados exclusivamente "
                        "para análise, tratamento e acompanhamento da denúncia, "
                        "conforme a legislação aplicável."
                    ),
                    (
                        "Ao utilizar este canal, o denunciante declara que as "
                        "informações fornecidas são verdadeiras e apresentadas "
                        "de boa-fé."
                    ),
                    1,
                    1
                )
            )

            conn.commit()

            return cursor.lastrowid

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar(
        empresa_id: int,
        nome_canal: str,
        favicon: str | None,
        cor_primaria: str,
        cor_secundaria: str,
        mensagem_boas_vindas: str | None,
        texto_lgpd: str | None,
        termo_uso: str | None,
        mostrar_logo: bool,
        mostrar_nome_empresa: bool
    ) -> bool:
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE empresa_personalizacao
                SET
                    nome_canal = %s,
                    favicon = %s,
                    cor_primaria = %s,
                    cor_secundaria = %s,
                    mensagem_boas_vindas = %s,
                    texto_lgpd = %s,
                    termo_uso = %s,
                    mostrar_logo = %s,
                    mostrar_nome_empresa = %s
                WHERE empresa_id = %s
                """,
                (
                    nome_canal,
                    favicon,
                    cor_primaria,
                    cor_secundaria,
                    mensagem_boas_vindas,
                    texto_lgpd,
                    termo_uso,
                    int(mostrar_logo),
                    int(mostrar_nome_empresa),
                    empresa_id
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
    def atualizar_sem_favicon(
        empresa_id: int,
        nome_canal: str,
        cor_primaria: str,
        cor_secundaria: str,
        mensagem_boas_vindas: str | None,
        texto_lgpd: str | None,
        termo_uso: str | None,
        mostrar_logo: bool,
        mostrar_nome_empresa: bool
    ) -> bool:
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE empresa_personalizacao
                SET
                    nome_canal = %s,
                    cor_primaria = %s,
                    cor_secundaria = %s,
                    mensagem_boas_vindas = %s,
                    texto_lgpd = %s,
                    termo_uso = %s,
                    mostrar_logo = %s,
                    mostrar_nome_empresa = %s
                WHERE empresa_id = %s
                """,
                (
                    nome_canal,
                    cor_primaria,
                    cor_secundaria,
                    mensagem_boas_vindas,
                    texto_lgpd,
                    termo_uso,
                    int(mostrar_logo),
                    int(mostrar_nome_empresa),
                    empresa_id
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
    def atualizar_logo_empresa(
        empresa_id: int,
        logo: str
    ) -> bool:
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE empresas
                SET logo = %s
                WHERE id = %s
                """,
                (
                    logo,
                    empresa_id
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
    def remover_logo_empresa(
        empresa_id: int
    ) -> bool:
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE empresas
                SET logo = NULL
                WHERE id = %s
                """,
                (empresa_id,)
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
    def remover_favicon(
        empresa_id: int
    ) -> bool:
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE empresa_personalizacao
                SET favicon = NULL
                WHERE empresa_id = %s
                """,
                (empresa_id,)
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()