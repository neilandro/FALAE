from db import get_connection


class UsuarioRepository:

    PERFIL_SUPER_ADMIN = "SUPER_ADMIN"
    PERFIL_ADMIN_ASSESSORIA = "ADM_ASSESSORIA"
    PERFIL_ADMIN_EMPRESA = "ADMIN_EMPRESA"

    PERFIS_OPERACIONAIS = (
        "GESTOR",
        "INVESTIGADOR",
        "VISUALIZADOR"
    )

    PERFIS_EMPRESA = (
        "ADMIN_EMPRESA",
        "GESTOR",
        "INVESTIGADOR",
        "VISUALIZADOR"
    )

    PERFIS_ASSESSORIA = (
        "ADM_ASSESSORIA",
        "ADMIN_EMPRESA",
        "GESTOR",
        "INVESTIGADOR",
        "VISUALIZADOR"
    )

    PERFIS_VALIDOS = (
        "SUPER_ADMIN",
        "ADM_ASSESSORIA",
        "ADMIN_EMPRESA",
        "GESTOR",
        "INVESTIGADOR",
        "VISUALIZADOR"
    )

    def __init__(self):
        self.conn = None
        self.cursor = None

        try:
            self.conn = get_connection()
            self.cursor = self.conn.cursor(
                dictionary=True
            )

        except Exception:
            self.close()
            raise

    # =========================================================
    # NORMALIZAÇÃO E VALIDAÇÕES INTERNAS
    # =========================================================

    @staticmethod
    def _normalizar_texto(valor):
        if valor is None:
            return None

        valor_normalizado = str(valor).strip()

        return valor_normalizado or None

    @classmethod
    def _normalizar_email(cls, email):
        email_normalizado = cls._normalizar_texto(
            email
        )

        if email_normalizado is None:
            return None

        return email_normalizado.lower()

    @classmethod
    def _normalizar_perfil(cls, perfil):
        perfil_normalizado = cls._normalizar_texto(
            perfil
        )

        if perfil_normalizado is None:
            return None

        return perfil_normalizado.upper()

    @staticmethod
    def _normalizar_id(valor):
        if valor in (
            None,
            ""
        ):
            return None

        try:
            valor_normalizado = int(valor)

        except (
            TypeError,
            ValueError
        ) as exc:
            raise ValueError(
                "Identificador inválido."
            ) from exc

        if valor_normalizado <= 0:
            raise ValueError(
                "Identificador inválido."
            )

        return valor_normalizado

    @staticmethod
    def _normalizar_ativo(valor):
        if isinstance(
            valor,
            bool
        ):
            return 1 if valor else 0

        if valor in (
            None,
            ""
        ):
            return 1

        try:
            valor_normalizado = int(valor)

        except (
            TypeError,
            ValueError
        ) as exc:
            raise ValueError(
                "Situação do usuário inválida."
            ) from exc

        if valor_normalizado not in (
            0,
            1
        ):
            raise ValueError(
                "Situação do usuário inválida."
            )

        return valor_normalizado

    @staticmethod
    def _normalizar_minutos_bloqueio(
        minutos,
        minimo=1,
        maximo=1440
    ):
        try:
            minutos_normalizados = int(
                minutos
            )

        except (
            TypeError,
            ValueError
        ) as exc:
            raise ValueError(
                "Tempo de bloqueio inválido."
            ) from exc

        return max(
            minimo,
            min(
                minutos_normalizados,
                maximo
            )
        )

    @classmethod
    def _validar_perfil(
        cls,
        perfil,
        perfis_permitidos=None
    ):
        perfil_normalizado = (
            cls._normalizar_perfil(
                perfil
            )
        )

        if (
            perfil_normalizado
            not in cls.PERFIS_VALIDOS
        ):
            raise ValueError(
                "Perfil de usuário inválido."
            )

        if (
            perfis_permitidos is not None
            and perfil_normalizado
            not in perfis_permitidos
        ):
            raise ValueError(
                "Perfil não permitido para esta operação."
            )

        return perfil_normalizado

    @classmethod
    def _preparar_vinculos_perfil(
        cls,
        perfil,
        empresa_id=None,
        assessoria_id=None
    ):
        perfil_normalizado = (
            cls._validar_perfil(
                perfil
            )
        )

        empresa_id_normalizada = (
            cls._normalizar_id(
                empresa_id
            )
        )

        assessoria_id_normalizada = (
            cls._normalizar_id(
                assessoria_id
            )
        )

        if (
            perfil_normalizado
            == cls.PERFIL_SUPER_ADMIN
        ):
            return (
                perfil_normalizado,
                None,
                None
            )

        if (
            perfil_normalizado
            == cls.PERFIL_ADMIN_ASSESSORIA
        ):
            if assessoria_id_normalizada is None:
                raise ValueError(
                    "O administrador da assessoria deve "
                    "estar vinculado a uma assessoria."
                )

            return (
                perfil_normalizado,
                None,
                assessoria_id_normalizada
            )

        if empresa_id_normalizada is None:
            raise ValueError(
                "O usuário deve estar vinculado "
                "a uma empresa."
            )

        return (
            perfil_normalizado,
            empresa_id_normalizada,
            None
        )

    @classmethod
    def _preparar_dados_usuario(
        cls,
        dados
    ):
        if not isinstance(
            dados,
            dict
        ):
            raise ValueError(
                "Dados do usuário inválidos."
            )

        nome = cls._normalizar_texto(
            dados.get("nome")
        )

        email = cls._normalizar_email(
            dados.get("email")
        )

        celular = cls._normalizar_texto(
            dados.get("celular")
        )

        whatsapp = cls._normalizar_texto(
            dados.get("whatsapp")
        )

        senha_hash = dados.get(
            "senha_hash"
        )

        ativo = cls._normalizar_ativo(
            dados.get(
                "ativo",
                1
            )
        )

        if not nome:
            raise ValueError(
                "Informe o nome do usuário."
            )

        if not email:
            raise ValueError(
                "Informe o e-mail do usuário."
            )

        (
            perfil,
            empresa_id,
            assessoria_id
        ) = cls._preparar_vinculos_perfil(
            perfil=dados.get("perfil"),
            empresa_id=dados.get(
                "empresa_id"
            ),
            assessoria_id=dados.get(
                "assessoria_id"
            )
        )

        return {
            "nome": nome,
            "email": email,
            "celular": celular,
            "whatsapp": whatsapp,
            "senha_hash": senha_hash,
            "perfil": perfil,
            "empresa_id": empresa_id,
            "assessoria_id": assessoria_id,
            "ativo": ativo
        }

    # =========================================================
    # CONSULTAS OPERACIONAIS
    # =========================================================

    def listar_investigadores(
        self,
        empresa_id
    ):
        empresa_id = self._normalizar_id(
            empresa_id
        )

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
            (
                empresa_id,
            )
        )

        return self.cursor.fetchall()


    def listar_admins_empresa_para_notificacao(
        self,
        empresa_id
    ):
        empresa_id = self._normalizar_id(
            empresa_id
        )

        self.cursor.execute(
            """
            SELECT
                id,
                nome,
                email
            FROM usuarios
            WHERE empresa_id = %s
            AND ativo = 1
            AND perfil = 'ADMIN_EMPRESA'
            AND email IS NOT NULL
            AND TRIM(email) <> ''
            ORDER BY nome
            """,
            (
                empresa_id,
            )
        )

        return self.cursor.fetchall()




    def buscar_por_id(
        self,
        usuario_id,
        empresa_id
    ):
        usuario_id = self._normalizar_id(
            usuario_id
        )

        empresa_id = self._normalizar_id(
            empresa_id
        )

        self.cursor.execute(
            """
            SELECT
                id,
                empresa_id,
                assessoria_id,
                nome,
                email,
                celular,
                whatsapp,
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
        """
        Consulta global.

        Deve ser utilizada exclusivamente em fluxos
        autorizados para SUPER_ADMIN.
        """

        usuario_id = self._normalizar_id(
            usuario_id
        )

        self.cursor.execute(
            """
            SELECT
                id,
                empresa_id,
                assessoria_id,
                nome,
                email,
                celular,
                whatsapp,
                perfil,
                ativo,
                trocar_senha_primeiro_acesso,
                senha_alterada_em
            FROM usuarios
            WHERE id = %s
            LIMIT 1
            """,
            (
                usuario_id,
            )
        )

        return self.cursor.fetchone()

    def buscar_por_id_super_admin(
        self,
        usuario_id
    ):
        return self.buscar_por_id_global(
            usuario_id
        )

    def buscar_por_id_assessoria(
        self,
        usuario_id,
        assessoria_id
    ):
        usuario_id = self._normalizar_id(
            usuario_id
        )

        assessoria_id = self._normalizar_id(
            assessoria_id
        )

        self.cursor.execute(
            """
            SELECT
                u.id,
                u.empresa_id,
                u.assessoria_id,
                u.nome,
                u.email,
                u.celular,
                u.whatsapp,
                u.perfil,
                u.ativo,
                u.trocar_senha_primeiro_acesso,
                u.senha_alterada_em
            FROM usuarios u
            LEFT JOIN empresas e
                ON e.id = u.empresa_id
            WHERE u.id = %s
              AND u.perfil <> 'SUPER_ADMIN'
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
            LIMIT 1
            """,
            (
                usuario_id,
                assessoria_id,
                assessoria_id
            )
        )

        return self.cursor.fetchone()

    # Mantido para não quebrar chamadas antigas.
    # Trata-se de uma consulta global.
    def obter_usuario(
        self,
        usuario_id
    ):
        return self.buscar_por_id_global(
            usuario_id
        )

    # =========================================================
    # LOGIN E SEGURANÇA
    # =========================================================

    def buscar_por_email_login(
        self,
        email
    ):
        email = self._normalizar_email(
            email
        )

        if not email:
            return None

        self.cursor.execute(
            """
            SELECT
                u.id,
                u.nome,
                u.email,
                u.senha_hash,
                u.perfil,
                u.empresa_id,
                u.assessoria_id,
                u.trocar_senha_primeiro_acesso,
                u.tentativas_login,
                u.bloqueado_ate,
                COALESCE(
                    a_usuario.nome,
                    a_empresa.nome
                ) AS assessoria_nome
            FROM usuarios u
            LEFT JOIN empresas e
                ON e.id = u.empresa_id
            LEFT JOIN assessorias a_usuario
                ON a_usuario.id = u.assessoria_id
            LEFT JOIN assessorias a_empresa
                ON a_empresa.id = e.assessoria_id
            WHERE LOWER(TRIM(u.email)) = %s
              AND u.ativo = 1
              AND (
                    (
                        u.perfil = 'SUPER_ADMIN'
                        AND u.empresa_id IS NULL
                        AND u.assessoria_id IS NULL
                    )
                    OR
                    (
                        u.perfil = 'ADM_ASSESSORIA'
                        AND u.empresa_id IS NULL
                        AND u.assessoria_id IS NOT NULL
                        AND a_usuario.ativa = 1
                    )
                    OR
                    (
                        u.perfil NOT IN (
                            'SUPER_ADMIN',
                            'ADM_ASSESSORIA'
                        )
                        AND u.empresa_id IS NOT NULL
                        AND e.ativa = 1
                        AND (
                            e.assessoria_id IS NULL
                            OR a_empresa.ativa = 1
                        )
                    )
              )
            LIMIT 1
            """,
            (
                email,
            )
        )

        return self.cursor.fetchone()

    def buscar_dados_seguranca(
        self,
        usuario_id
    ):
        usuario_id = self._normalizar_id(
            usuario_id
        )

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
            (
                usuario_id,
            )
        )

        return self.cursor.fetchone()

    def existe_email(
        self,
        email,
        usuario_id=None
    ):
        email = self._normalizar_email(
            email
        )

        if not email:
            return False

        sql = """
            SELECT id
            FROM usuarios
            WHERE LOWER(TRIM(email)) = %s
        """

        parametros = [
            email
        ]

        if usuario_id is not None:
            usuario_id = self._normalizar_id(
                usuario_id
            )

            sql += """
                AND id <> %s
            """

            parametros.append(
                usuario_id
            )

        sql += """
            LIMIT 1
        """

        self.cursor.execute(
            sql,
            tuple(parametros)
        )

        return self.cursor.fetchone() is not None

    def atualizar_senha(
        self,
        usuario_id,
        senha_hash
    ):
        usuario_id = self._normalizar_id(
            usuario_id
        )

        if not senha_hash:
            raise ValueError(
                "Hash da senha não informado."
            )

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

            atualizado = (
                self.cursor.rowcount > 0
            )

            self.conn.commit()

            return atualizado

        except Exception:
            self.conn.rollback()
            raise

    def atualizar_senha_definitiva(
        self,
        usuario_id,
        senha_hash
    ):
        usuario_id = self._normalizar_id(
            usuario_id
        )

        if not senha_hash:
            raise ValueError(
                "Hash da senha não informado."
            )

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

            atualizado = (
                self.cursor.rowcount > 0
            )

            self.conn.commit()

            return atualizado

        except Exception:
            self.conn.rollback()
            raise

    def incrementar_tentativas_login(
        self,
        usuario_id
    ):
        usuario_id = self._normalizar_id(
            usuario_id
        )

        try:
            self.cursor.execute(
                """
                UPDATE usuarios
                SET
                    tentativas_login =
                        COALESCE(
                            tentativas_login,
                            0
                        ) + 1
                WHERE id = %s
                  AND ativo = 1
                """,
                (
                    usuario_id,
                )
            )

            if self.cursor.rowcount == 0:
                self.conn.rollback()
                return 0

            self.cursor.execute(
                """
                SELECT tentativas_login
                FROM usuarios
                WHERE id = %s
                FOR UPDATE
                """,
                (
                    usuario_id,
                )
            )

            resultado = (
                self.cursor.fetchone()
            )

            tentativas = int(
                (
                    resultado or {}
                ).get(
                    "tentativas_login"
                ) or 0
            )

            self.conn.commit()

            return tentativas

        except Exception:
            self.conn.rollback()
            raise

    def bloquear_usuario(
        self,
        usuario_id,
        minutos=15
    ):
        usuario_id = self._normalizar_id(
            usuario_id
        )

        minutos = (
            self._normalizar_minutos_bloqueio(
                minutos
            )
        )

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
                  AND ativo = 1
                """,
                (
                    minutos,
                    usuario_id
                )
            )

            atualizado = (
                self.cursor.rowcount > 0
            )

            self.conn.commit()

            return atualizado

        except Exception:
            self.conn.rollback()
            raise

    def resetar_tentativas_login(
        self,
        usuario_id
    ):
        usuario_id = self._normalizar_id(
            usuario_id
        )

        try:
            self.cursor.execute(
                """
                UPDATE usuarios
                SET
                    tentativas_login = 0,
                    bloqueado_ate = NULL
                WHERE id = %s
                """,
                (
                    usuario_id,
                )
            )

            atualizado = (
                self.cursor.rowcount > 0
            )

            self.conn.commit()

            return atualizado

        except Exception:
            self.conn.rollback()
            raise

    def registrar_login_sucesso(
        self,
        usuario_id,
        ip
    ):
        usuario_id = self._normalizar_id(
            usuario_id
        )

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
                  AND ativo = 1
                """,
                (
                    ip_normalizado,
                    usuario_id
                )
            )

            atualizado = (
                self.cursor.rowcount > 0
            )

            self.conn.commit()

            return atualizado

        except Exception:
            self.conn.rollback()
            raise

    # =========================================================
    # EMPRESAS E ASSESSORIAS
    # =========================================================

    def listar_empresas(self):
        """
        Listagem global.

        Deve ser utilizada exclusivamente por SUPER_ADMIN.
        """

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

    def listar_empresas_por_assessoria(
        self,
        assessoria_id
    ):
        assessoria_id = self._normalizar_id(
            assessoria_id
        )

        self.cursor.execute(
            """
            SELECT
                id,
                nome,
                assessoria_id
            FROM empresas
            WHERE assessoria_id = %s
              AND ativa = 1
            ORDER BY nome
            """,
            (
                assessoria_id,
            )
        )

        return self.cursor.fetchall()

    def buscar_empresa_ativa(
        self,
        empresa_id
    ):
        empresa_id = self._normalizar_id(
            empresa_id
        )

        self.cursor.execute(
            """
            SELECT
                id,
                nome,
                assessoria_id
            FROM empresas
            WHERE id = %s
              AND ativa = 1
            LIMIT 1
            """,
            (
                empresa_id,
            )
        )

        return self.cursor.fetchone()

    def empresa_pertence_assessoria(
        self,
        empresa_id,
        assessoria_id
    ):
        empresa_id = self._normalizar_id(
            empresa_id
        )

        assessoria_id = self._normalizar_id(
            assessoria_id
        )

        self.cursor.execute(
            """
            SELECT id
            FROM empresas
            WHERE id = %s
              AND assessoria_id = %s
              AND ativa = 1
            LIMIT 1
            """,
            (
                empresa_id,
                assessoria_id
            )
        )

        return self.cursor.fetchone() is not None

    def listar_assessorias(self):
        """
        Listagem global.

        Deve ser utilizada exclusivamente por SUPER_ADMIN.
        """

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

    def buscar_assessoria_ativa(
        self,
        assessoria_id
    ):
        assessoria_id = self._normalizar_id(
            assessoria_id
        )

        self.cursor.execute(
            """
            SELECT
                id,
                nome
            FROM assessorias
            WHERE id = %s
              AND ativa = 1
            LIMIT 1
            """,
            (
                assessoria_id,
            )
        )

        return self.cursor.fetchone()

    # =========================================================
    # CRIAÇÃO
    # =========================================================

    def criar_usuario(
        self,
        dados
    ):
        dados_preparados = (
            self._preparar_dados_usuario(
                dados
            )
        )

        if not dados_preparados.get(
            "senha_hash"
        ):
            raise ValueError(
                "Hash da senha não informado."
            )

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
                    dados_preparados[
                        "empresa_id"
                    ],
                    dados_preparados[
                        "assessoria_id"
                    ],
                    dados_preparados[
                        "nome"
                    ],
                    dados_preparados[
                        "email"
                    ],
                    dados_preparados[
                        "celular"
                    ],
                    dados_preparados[
                        "whatsapp"
                    ],
                    dados_preparados[
                        "senha_hash"
                    ],
                    dados_preparados[
                        "perfil"
                    ],
                    dados_preparados[
                        "ativo"
                    ]
                )
            )

            usuario_id = (
                self.cursor.lastrowid
            )

            self.conn.commit()

            return usuario_id

        except Exception:
            self.conn.rollback()
            raise

    # =========================================================
    # LISTAGENS
    # =========================================================

    def listar_usuarios_global(self):
        """
        Listagem global.

        Deve ser utilizada exclusivamente por SUPER_ADMIN.
        """

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
                u.empresa_id,
                u.assessoria_id,
                u.trocar_senha_primeiro_acesso,
                u.senha_alterada_em,
                u.criado_em,
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
            ORDER BY u.nome
            """
        )

        return self.cursor.fetchall()

    def listar_usuarios_por_assessoria(
        self,
        assessoria_id
    ):
        assessoria_id = self._normalizar_id(
            assessoria_id
        )

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
                u.empresa_id,
                u.assessoria_id,
                u.trocar_senha_primeiro_acesso,
                u.senha_alterada_em,
                u.criado_em,
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
        empresa_id = self._normalizar_id(
            empresa_id
        )

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
                u.empresa_id,
                u.assessoria_id,
                u.trocar_senha_primeiro_acesso,
                u.senha_alterada_em,
                u.criado_em,
                e.nome AS empresa,
                a.nome AS assessoria
            FROM usuarios u
            INNER JOIN empresas e
                ON e.id = u.empresa_id
            LEFT JOIN assessorias a
                ON a.id = e.assessoria_id
            WHERE u.empresa_id = %s
              AND u.perfil IN (
                  'GESTOR',
                  'INVESTIGADOR',
                  'VISUALIZADOR'
              )
            ORDER BY u.nome
            """,
            (
                empresa_id,
            )
        )

        return self.cursor.fetchall()

    # =========================================================
    # ATUALIZAÇÕES COM ESCOPO
    # =========================================================

    def atualizar_usuario_global(
        self,
        usuario_id,
        dados
    ):
        """
        Atualização global.

        Deve ser utilizada exclusivamente por SUPER_ADMIN.
        """

        usuario_id = self._normalizar_id(
            usuario_id
        )

        dados_preparados = (
            self._preparar_dados_usuario(
                dados
            )
        )

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
                    dados_preparados[
                        "nome"
                    ],
                    dados_preparados[
                        "email"
                    ],
                    dados_preparados[
                        "celular"
                    ],
                    dados_preparados[
                        "whatsapp"
                    ],
                    dados_preparados[
                        "perfil"
                    ],
                    dados_preparados[
                        "empresa_id"
                    ],
                    dados_preparados[
                        "assessoria_id"
                    ],
                    dados_preparados[
                        "ativo"
                    ],
                    usuario_id
                )
            )

            atualizado = (
                self.cursor.rowcount > 0
            )

            self.conn.commit()

            return atualizado

        except Exception:
            self.conn.rollback()
            raise

    def atualizar_usuario_por_empresa(
        self,
        usuario_id,
        empresa_id,
        dados
    ):
        """
        Atualiza apenas usuários operacionais da empresa.

        O empresa_id e o assessoria_id nunca são recebidos
        dos dados do formulário neste fluxo.
        """

        usuario_id = self._normalizar_id(
            usuario_id
        )

        empresa_id = self._normalizar_id(
            empresa_id
        )

        nome = self._normalizar_texto(
            dados.get("nome")
        )

        email = self._normalizar_email(
            dados.get("email")
        )

        celular = self._normalizar_texto(
            dados.get("celular")
        )

        whatsapp = self._normalizar_texto(
            dados.get("whatsapp")
        )

        ativo = self._normalizar_ativo(
            dados.get(
                "ativo",
                1
            )
        )

        perfil = self._validar_perfil(
            dados.get("perfil"),
            self.PERFIS_OPERACIONAIS
        )

        if not nome:
            raise ValueError(
                "Informe o nome do usuário."
            )

        if not email:
            raise ValueError(
                "Informe o e-mail do usuário."
            )

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
                    ativo = %s
                WHERE id = %s
                  AND empresa_id = %s
                  AND perfil IN (
                      'GESTOR',
                      'INVESTIGADOR',
                      'VISUALIZADOR'
                  )
                """,
                (
                    nome,
                    email,
                    celular,
                    whatsapp,
                    perfil,
                    ativo,
                    usuario_id,
                    empresa_id
                )
            )

            atualizado = (
                self.cursor.rowcount > 0
            )

            self.conn.commit()

            return atualizado

        except Exception:
            self.conn.rollback()
            raise

    def atualizar_usuario_por_assessoria(
        self,
        usuario_id,
        assessoria_id,
        dados
    ):
        """
        Atualiza somente usuários pertencentes à assessoria.

        O vínculo de assessoria é sempre obtido do contexto
        autenticado e nunca é aceito diretamente do formulário.
        """

        usuario_id = self._normalizar_id(
            usuario_id
        )

        assessoria_id = self._normalizar_id(
            assessoria_id
        )

        nome = self._normalizar_texto(
            dados.get("nome")
        )

        email = self._normalizar_email(
            dados.get("email")
        )

        celular = self._normalizar_texto(
            dados.get("celular")
        )

        whatsapp = self._normalizar_texto(
            dados.get("whatsapp")
        )

        ativo = self._normalizar_ativo(
            dados.get(
                "ativo",
                1
            )
        )

        perfil = self._validar_perfil(
            dados.get("perfil"),
            self.PERFIS_ASSESSORIA
        )

        if not nome:
            raise ValueError(
                "Informe o nome do usuário."
            )

        if not email:
            raise ValueError(
                "Informe o e-mail do usuário."
            )

        if (
            perfil
            == self.PERFIL_ADMIN_ASSESSORIA
        ):
            empresa_destino_id = None
            assessoria_destino_id = (
                assessoria_id
            )

        else:
            empresa_destino_id = (
                self._normalizar_id(
                    dados.get("empresa_id")
                )
            )

            assessoria_destino_id = None

        try:
            if empresa_destino_id is not None:
                self.cursor.execute(
                    """
                    SELECT id
                    FROM empresas
                    WHERE id = %s
                      AND assessoria_id = %s
                      AND ativa = 1
                    LIMIT 1
                    FOR UPDATE
                    """,
                    (
                        empresa_destino_id,
                        assessoria_id
                    )
                )

                if not self.cursor.fetchone():
                    self.conn.rollback()

                    raise ValueError(
                        "A empresa informada não pertence "
                        "à assessoria autenticada."
                    )

            self.cursor.execute(
                """
                UPDATE usuarios u
                LEFT JOIN empresas e_atual
                    ON e_atual.id = u.empresa_id
                SET
                    u.nome = %s,
                    u.email = %s,
                    u.celular = %s,
                    u.whatsapp = %s,
                    u.perfil = %s,
                    u.empresa_id = %s,
                    u.assessoria_id = %s,
                    u.ativo = %s
                WHERE u.id = %s
                  AND u.perfil <> 'SUPER_ADMIN'
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
                            AND e_atual.assessoria_id = %s
                        )
                  )
                """,
                (
                    nome,
                    email,
                    celular,
                    whatsapp,
                    perfil,
                    empresa_destino_id,
                    assessoria_destino_id,
                    ativo,
                    usuario_id,
                    assessoria_id,
                    assessoria_id
                )
            )

            atualizado = (
                self.cursor.rowcount > 0
            )

            self.conn.commit()

            return atualizado

        except Exception:
            self.conn.rollback()
            raise

    # Mantido para não quebrar chamadas antigas.
    # Trata-se de uma atualização global.
    def atualizar_usuario(
        self,
        usuario_id,
        dados
    ):
        return self.atualizar_usuario_global(
            usuario_id,
            dados
        )

    # =========================================================
    # ENCERRAMENTO
    # =========================================================

    def close(self):
        cursor = getattr(
            self,
            "cursor",
            None
        )

        conn = getattr(
            self,
            "conn",
            None
        )

        self.cursor = None
        self.conn = None

        if cursor is not None:
            try:
                cursor.close()

            except Exception:
                pass

        if conn is not None:
            try:
                conn.close()

            except Exception:
                pass