from db import get_connection


class UsuarioRepository:

    def __init__(self):
        self.conn = get_connection()

        self.cursor = self.conn.cursor(
            dictionary=True
        )

    def listar_investigadores(
        self,
        empresa_id
    ):
        self.cursor.execute(
            """
            SELECT
                id,
                nome,
                email,
                perfil
            FROM usuarios
            WHERE empresa_id = %s
              AND ativo = 1
              AND perfil IN (
                  'ADMIN_EMPRESA',
                  'GESTOR',
                  'INVESTIGADOR'
              )
            ORDER BY nome
            """,
            (empresa_id,)
        )

        return self.cursor.fetchall()

    def buscar_por_id(
        self,
        usuario_id,
        empresa_id
    ):
        self.cursor.execute(
            """
            SELECT
                id,
                nome,
                email,
                perfil,
                ativo,
                trocar_senha_primeiro_acesso,
                senha_alterada_em
            FROM usuarios
            WHERE id = %s
              AND empresa_id = %s
            LIMIT 1
            """,
            (
                usuario_id,
                empresa_id
            )
        )

        return self.cursor.fetchone()

    def buscar_por_id_global(
        self,
        usuario_id
    ):
        self.cursor.execute(
            """
            SELECT
                id,
                empresa_id,
                assessoria_id,
                nome,
                email,
                perfil,
                ativo,
                trocar_senha_primeiro_acesso,
                senha_alterada_em
            FROM usuarios
            WHERE id = %s
            LIMIT 1
            """,
            (usuario_id,)
        )

        return self.cursor.fetchone()

    def buscar_dados_seguranca(
        self,
        usuario_id
    ):
        self.cursor.execute(
            """
            SELECT
                id,
                senha_hash,
                ativo,
                trocar_senha_primeiro_acesso,
                senha_alterada_em,
                tentativas_login,
                bloqueado_ate,
                ultimo_login,
                ultimo_ip
            FROM usuarios
            WHERE id = %s
            LIMIT 1
            """,
            (usuario_id,)
        )

        return self.cursor.fetchone()

    def atualizar_senha(
        self,
        usuario_id,
        senha_hash
    ):
        """
        Redefine a senha por ação administrativa.

        A nova senha é considerada temporária e o usuário
        será obrigado a substituí-la no próximo acesso.
        """

        try:
            self.cursor.execute(
                """
                UPDATE usuarios
                SET
                    senha_hash = %s,
                    trocar_senha_primeiro_acesso = 1,
                    senha_alterada_em = NOW(),
                    tentativas_login = 0,
                    bloqueado_ate = NULL
                WHERE id = %s
                """,
                (
                    senha_hash,
                    usuario_id
                )
            )

            self.conn.commit()

            return self.cursor.rowcount > 0

        except Exception:
            self.conn.rollback()
            raise

    def atualizar_senha_definitiva(
        self,
        usuario_id,
        senha_hash
    ):
        """
        Registra a nova senha escolhida pelo próprio usuário.

        Após esta operação, a troca obrigatória é encerrada.
        """

        try:
            self.cursor.execute(
                """
                UPDATE usuarios
                SET
                    senha_hash = %s,
                    trocar_senha_primeiro_acesso = 0,
                    senha_alterada_em = NOW(),
                    tentativas_login = 0,
                    bloqueado_ate = NULL
                WHERE id = %s
                  AND ativo = 1
                """,
                (
                    senha_hash,
                    usuario_id
                )
            )

            self.conn.commit()

            return self.cursor.rowcount > 0

        except Exception:
            self.conn.rollback()
            raise

    def incrementar_tentativas_login(
        self,
        usuario_id
    ):
        try:
            self.cursor.execute(
                """
                UPDATE usuarios
                SET
                    tentativas_login = (
                        COALESCE(
                            tentativas_login,
                            0
                        ) + 1
                    )
                WHERE id = %s
                """,
                (usuario_id,)
            )

            self.conn.commit()

            self.cursor.execute(
                """
                SELECT
                    tentativas_login
                FROM usuarios
                WHERE id = %s
                LIMIT 1
                """,
                (usuario_id,)
            )

            resultado = self.cursor.fetchone()

            if not resultado:
                return 0

            return int(
                resultado[
                    "tentativas_login"
                ] or 0
            )

        except Exception:
            self.conn.rollback()
            raise

    def bloquear_usuario(
        self,
        usuario_id,
        minutos=15
    ):
        try:
            self.cursor.execute(
                """
                UPDATE usuarios
                SET
                    bloqueado_ate = DATE_ADD(
                        NOW(),
                        INTERVAL %s MINUTE
                    )
                WHERE id = %s
                """,
                (
                    int(minutos),
                    usuario_id
                )
            )

            self.conn.commit()

            return self.cursor.rowcount > 0

        except Exception:
            self.conn.rollback()
            raise

    def resetar_tentativas_login(
        self,
        usuario_id
    ):
        try:
            self.cursor.execute(
                """
                UPDATE usuarios
                SET
                    tentativas_login = 0,
                    bloqueado_ate = NULL
                WHERE id = %s
                """,
                (usuario_id,)
            )

            self.conn.commit()

            return self.cursor.rowcount > 0

        except Exception:
            self.conn.rollback()
            raise

    def registrar_login_sucesso(
        self,
        usuario_id,
        ip
    ):
        ip_normalizado = (
            str(ip).strip()[:45]
            if ip
            else None
        )

        try:
            self.cursor.execute(
                """
                UPDATE usuarios
                SET
                    tentativas_login = 0,
                    bloqueado_ate = NULL,
                    ultimo_login = NOW(),
                    ultimo_ip = %s
                WHERE id = %s
                """,
                (
                    ip_normalizado,
                    usuario_id
                )
            )

            self.conn.commit()

            return self.cursor.rowcount > 0

        except Exception:
            self.conn.rollback()
            raise

    def listar_empresas(self):
        self.cursor.execute(
            """
            SELECT
                id,
                nome,
                assessoria_id
            FROM empresas
            WHERE ativa = 1
            ORDER BY nome
            """
        )

        return self.cursor.fetchall()

    def listar_assessorias(self):
        self.cursor.execute(
            """
            SELECT
                id,
                nome
            FROM assessorias
            WHERE ativa = 1
            ORDER BY nome
            """
        )

        return self.cursor.fetchall()

    def criar_usuario(
        self,
        dados
    ):
        """
        Todo usuário novo recebe uma senha inicial temporária.

        No primeiro login, será obrigado a cadastrar
        uma senha pessoal e definitiva.
        """

        try:
            self.cursor.execute(
                """
                INSERT INTO usuarios (
                    empresa_id,
                    assessoria_id,
                    nome,
                    email,
                    celular,
                    whatsapp,
                    senha_hash,
                    trocar_senha_primeiro_acesso,
                    senha_alterada_em,
                    perfil,
                    ativo
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    1,
                    NOW(),
                    %s,
                    %s
                )
                """,
                (
                    dados.get(
                        "empresa_id"
                    ),
                    dados.get(
                        "assessoria_id"
                    ),
                    dados.get(
                        "nome"
                    ),
                    dados.get(
                        "email"
                    ),
                    dados.get(
                        "celular"
                    ),
                    dados.get(
                        "whatsapp"
                    ),
                    dados.get(
                        "senha_hash"
                    ),
                    dados.get(
                        "perfil"
                    ),
                    dados.get(
                        "ativo",
                        1
                    )
                )
            )

            self.conn.commit()

            return self.cursor.lastrowid

        except Exception:
            self.conn.rollback()
            raise

    def listar_usuarios_global(self):
        self.cursor.execute(
            """
            SELECT
                u.id,
                u.nome,
                u.email,
                u.celular,
                u.whatsapp,
                u.perfil,
                u.ativo,
                u.trocar_senha_primeiro_acesso,
                u.senha_alterada_em,
                u.criado_em,
                e.nome AS empresa,
                a.nome AS assessoria
            FROM usuarios u
            LEFT JOIN empresas e
                ON e.id = u.empresa_id
            LEFT JOIN assessorias a
                ON a.id = u.assessoria_id
            ORDER BY u.nome
            """
        )

        return self.cursor.fetchall()

    def listar_usuarios_por_assessoria(
        self,
        assessoria_id
    ):
        self.cursor.execute(
            """
            SELECT
                u.id,
                u.nome,
                u.email,
                u.celular,
                u.whatsapp,
                u.perfil,
                u.ativo,
                u.trocar_senha_primeiro_acesso,
                u.senha_alterada_em,
                u.criado_em,
                u.empresa_id,
                u.assessoria_id,

                e.nome AS empresa,

                COALESCE(
                    a_usuario.nome,
                    a_empresa.nome
                ) AS assessoria

            FROM usuarios u

            LEFT JOIN empresas e
                ON e.id = u.empresa_id

            LEFT JOIN assessorias a_usuario
                ON a_usuario.id = u.assessoria_id

            LEFT JOIN assessorias a_empresa
                ON a_empresa.id = e.assessoria_id

            WHERE u.perfil <> 'SUPER_ADMIN'

              AND (
                    (
                        u.perfil = 'ADM_ASSESSORIA'
                        AND u.assessoria_id = %s
                        AND u.empresa_id IS NULL
                    )

                    OR

                    (
                        u.perfil <> 'ADM_ASSESSORIA'
                        AND u.empresa_id IS NOT NULL
                        AND e.assessoria_id = %s
                    )
              )

            ORDER BY
                COALESCE(
                    e.nome,
                    a_usuario.nome
                ),
                u.nome
            """,
            (
                assessoria_id,
                assessoria_id
            )
        )

        return self.cursor.fetchall()
    
    def listar_usuarios_por_empresa(
        self,
        empresa_id
    ):
        self.cursor.execute(
            """
            SELECT
                u.id,
                u.nome,
                u.email,
                u.celular,
                u.whatsapp,
                u.perfil,
                u.ativo,
                u.trocar_senha_primeiro_acesso,
                u.senha_alterada_em,
                u.criado_em,
                e.nome AS empresa,
                a.nome AS assessoria
            FROM usuarios u
            LEFT JOIN empresas e
                ON e.id = u.empresa_id
            LEFT JOIN assessorias a
                ON a.id = u.assessoria_id
            WHERE u.empresa_id = %s
              AND u.perfil NOT IN (
                  'SUPER_ADMIN',
                  'ADM_ASSESSORIA'
              )
            ORDER BY u.nome
            """,
            (empresa_id,)
        )

        return self.cursor.fetchall()

    def obter_usuario(
        self,
        usuario_id
    ):
        self.cursor.execute(
            """
            SELECT
                id,
                nome,
                email,
                celular,
                whatsapp,
                perfil,
                empresa_id,
                assessoria_id,
                ativo,
                trocar_senha_primeiro_acesso,
                senha_alterada_em
            FROM usuarios
            WHERE id = %s
            LIMIT 1
            """,
            (usuario_id,)
        )

        return self.cursor.fetchone()

    def atualizar_usuario(
        self,
        usuario_id,
        dados
    ):
        try:
            self.cursor.execute(
                """
                UPDATE usuarios
                SET
                    nome = %s,
                    email = %s,
                    celular = %s,
                    whatsapp = %s,
                    perfil = %s,
                    empresa_id = %s,
                    assessoria_id = %s,
                    ativo = %s
                WHERE id = %s
                """,
                (
                    dados["nome"],
                    dados["email"],
                    dados["celular"],
                    dados["whatsapp"],
                    dados["perfil"],
                    dados["empresa_id"],
                    dados["assessoria_id"],
                    dados["ativo"],
                    usuario_id
                )
            )

            self.conn.commit()

            return self.cursor.rowcount > 0

        except Exception:
            self.conn.rollback()
            raise

    def close(self):
        self.cursor.close()
        self.conn.close()
