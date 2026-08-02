import re

from db import get_connection


class DenunciaRepository:

    ORDENACOES_PERMITIDAS = {
        "mais_recentes": "d.criado_em DESC",
        "mais_antigas": "d.criado_em ASC",
        "recentes": "d.criado_em DESC",
        "antigas": "d.criado_em ASC",
        "protocolo_asc": "d.protocolo ASC",
        "protocolo_desc": "d.protocolo DESC",
        "status_asc": "d.status ASC",
        "status_desc": "d.status DESC",
        "criticidade_asc": "d.criticidade ASC",
        "criticidade_desc": "d.criticidade DESC",
        "etapa_asc": "d.etapa_atual ASC",
        "etapa_desc": "d.etapa_atual DESC",
        "unidade_asc": "u.nome ASC",
        "unidade_desc": "u.nome DESC",
        "d.criado_em DESC": "d.criado_em DESC",
        "d.criado_em ASC": "d.criado_em ASC",
        "d.protocolo ASC": "d.protocolo ASC",
        "d.protocolo DESC": "d.protocolo DESC",
        "d.status ASC": "d.status ASC",
        "d.status DESC": "d.status DESC",
        "d.criticidade ASC": "d.criticidade ASC",
        "d.criticidade DESC": "d.criticidade DESC",
        "d.etapa_atual ASC": "d.etapa_atual ASC",
        "d.etapa_atual DESC": "d.etapa_atual DESC",
        "u.nome ASC": "u.nome ASC",
        "u.nome DESC": "u.nome DESC",
    }

    COLUNAS_FILTRO_PERMITIDAS = {
        "d.empresa_id",
        "d.unidade_id",
        "d.setor_id",
        "d.responsavel_id",
        "d.tipo",
        "d.categoria",
        "d.criticidade",
        "d.status",
        "d.etapa_atual",
        "d.protocolo",
        "d.criado_em",
        "d.data_ocorrencia",
        "u.nome",
        "s.nome",
    }

    OPERADORES_FILTRO_PERMITIDOS = {
        "=",
        "<>",
        "!=",
        ">",
        ">=",
        "<",
        "<=",
        "LIKE",
        "IS NULL",
        "IS NOT NULL",
    }

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    @classmethod
    def _obter_order_by_seguro(cls, order_by):
        if not isinstance(order_by, str):
            return cls.ORDENACOES_PERMITIDAS["mais_recentes"]

        return cls.ORDENACOES_PERMITIDAS.get(
            order_by.strip(),
            cls.ORDENACOES_PERMITIDAS["mais_recentes"]
        )

    @classmethod
    def _validar_where_sql(cls, where_sql):
        if not isinstance(where_sql, str):
            raise ValueError("Filtro SQL inválido.")

        where_sql = where_sql.strip()

        if not where_sql:
            raise ValueError("O filtro SQL não pode estar vazio.")

        conteudo_bloqueado = re.compile(
            r"""
            (;)
            |(--\s*)
            |(/\*)
            |(\*/)
            |(\bUNION\b)
            |(\bOR\b)
            |(\bDROP\b)
            |(\bALTER\b)
            |(\bTRUNCATE\b)
            |(\bINSERT\b)
            |(\bUPDATE\b)
            |(\bDELETE\b)
            |(\bEXEC\b)
            |(\bSLEEP\b)
            |(\bBENCHMARK\b)
            |(\bINFORMATION_SCHEMA\b)
            """,
            re.IGNORECASE | re.VERBOSE
        )

        if conteudo_bloqueado.search(where_sql):
            raise ValueError(
                "O filtro informado contém uma expressão não permitida."
            )

        condicoes = re.split(
            r"\s+AND\s+",
            where_sql,
            flags=re.IGNORECASE
        )

        padrao_condicao = re.compile(
            r"""
            ^\s*
            (?P<coluna>[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)
            \s*
            (?P<operador>
                IS\s+NOT\s+NULL
                |IS\s+NULL
                |LIKE
                |>=
                |<=
                |<>
                |!=
                |=
                |>
                |<
            )
            \s*
            (?P<valor>%s)?
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE
        )

        colunas_permitidas = {
            item.lower()
            for item in cls.COLUNAS_FILTRO_PERMITIDAS
        }

        for condicao in condicoes:
            condicao = condicao.strip()

            while condicao.startswith("(") and condicao.endswith(")"):
                condicao = condicao[1:-1].strip()

            correspondencia = padrao_condicao.fullmatch(condicao)

            if not correspondencia:
                raise ValueError(
                    f"Condição de filtro não permitida: {condicao}"
                )

            coluna = correspondencia.group("coluna").lower()
            operador = re.sub(
                r"\s+",
                " ",
                correspondencia.group("operador").upper()
            )
            valor = correspondencia.group("valor")

            if coluna not in colunas_permitidas:
                raise ValueError(
                    f"Coluna não permitida no filtro: {coluna}"
                )

            if operador not in cls.OPERADORES_FILTRO_PERMITIDOS:
                raise ValueError(
                    f"Operador não permitido no filtro: {operador}"
                )

            operador_sem_valor = operador in {
                "IS NULL",
                "IS NOT NULL",
            }

            if operador_sem_valor and valor is not None:
                raise ValueError(
                    f"O operador {operador} não aceita valor."
                )

            if not operador_sem_valor and valor != "%s":
                raise ValueError(
                    "Todos os valores dos filtros devem utilizar "
                    "placeholders parametrizados."
                )

        return where_sql

    def listar_denuncias(
        self,
        where_sql,
        params,
        order_by,
        per_page,
        offset
    ):
        where_sql_seguro = self._validar_where_sql(where_sql)
        order_by_seguro = self._obter_order_by_seguro(order_by)

        try:
            per_page = int(per_page)
            offset = int(offset)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Os dados de paginação são inválidos."
            ) from exc

        per_page = max(1, min(per_page, 100))
        offset = max(0, offset)

        params_paginados = list(params) + [per_page, offset]

        self.cursor.execute(
            f"""
            SELECT
                d.id,
                d.protocolo,
                d.tipo,
                d.categoria,
                d.criticidade,
                d.status,
                d.etapa_atual,
                d.responsavel_id,
                d.criado_em,
                u.nome AS unidade,
                s.nome AS setor,
                usr.nome AS responsavel
            FROM denuncias d
            INNER JOIN unidades u
                ON d.unidade_id = u.id
               AND u.empresa_id = d.empresa_id
            LEFT JOIN setores s
                ON d.setor_id = s.id
               AND s.empresa_id = d.empresa_id
            LEFT JOIN usuarios usr
                ON usr.id = d.responsavel_id
               AND (
                    usr.empresa_id = d.empresa_id
                    OR usr.empresa_id IS NULL
               )
            WHERE {where_sql_seguro}
            ORDER BY {order_by_seguro}
            LIMIT %s OFFSET %s
            """,
            params_paginados
        )

        return self.cursor.fetchall()

    def contar_denuncias(self, where_sql, params):
        where_sql_seguro = self._validar_where_sql(where_sql)

        self.cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM denuncias d
            INNER JOIN unidades u
                ON d.unidade_id = u.id
               AND u.empresa_id = d.empresa_id
            LEFT JOIN setores s
                ON d.setor_id = s.id
               AND s.empresa_id = d.empresa_id
            WHERE {where_sql_seguro}
            """,
            params
        )

        resultado = self.cursor.fetchone()
        return resultado["total"] if resultado else 0

    def buscar_por_id(self, denuncia_id, empresa_id):
        self.cursor.execute("""
            SELECT
                d.id,
                d.protocolo,
                d.tipo,
                d.categoria,
                d.criticidade,
                d.prioridade,
                d.status,
                d.etapa_atual,
                d.responsavel_id,
                d.descricao,
                d.local_ocorrencia,
                d.data_ocorrencia,
                d.observacao_interna,
                d.parecer_triagem,
                d.triagem_concluida_em,
                d.triagem_realizada_por,
                d.criado_em,
                d.data_encerramento,
                u.nome AS unidade,
                s.nome AS setor,
                usr.nome AS responsavel,
                triador.nome AS triador
            FROM denuncias d
            INNER JOIN unidades u
                ON d.unidade_id = u.id
               AND u.empresa_id = d.empresa_id
            LEFT JOIN setores s
                ON d.setor_id = s.id
               AND s.empresa_id = d.empresa_id
            LEFT JOIN usuarios usr
                ON usr.id = d.responsavel_id
               AND (
                    usr.empresa_id = d.empresa_id
                    OR usr.empresa_id IS NULL
               )
            LEFT JOIN usuarios triador
                ON triador.id = d.triagem_realizada_por
               AND (
                    triador.empresa_id = d.empresa_id
                    OR triador.empresa_id IS NULL
               )
            WHERE d.id = %s
              AND d.empresa_id = %s
            LIMIT 1
        """, (denuncia_id, empresa_id))

        return self.cursor.fetchone()

    def atualizar_denuncia(
        self,
        denuncia_id,
        empresa_id,
        status,
        criticidade,
        etapa_atual,
        observacao_interna
    ):
        try:
            self.cursor.execute("""
                SELECT
                    status,
                    criticidade,
                    etapa_atual,
                    observacao_interna
                FROM denuncias
                WHERE id = %s
                  AND empresa_id = %s
                LIMIT 1
            """, (denuncia_id, empresa_id))

            valor_antigo = self.cursor.fetchone()

            if not valor_antigo:
                return None

            self.cursor.execute("""
                UPDATE denuncias
                SET status = %s,
                    criticidade = %s,
                    etapa_atual = %s,
                    observacao_interna = %s,
                    data_encerramento = CASE
                        WHEN %s IN ('CONCLUIDA', 'ARQUIVADA')
                            THEN NOW()
                        WHEN %s NOT IN ('CONCLUIDA', 'ARQUIVADA')
                            THEN NULL
                        ELSE data_encerramento
                    END
                WHERE id = %s
                  AND empresa_id = %s
            """, (
                status,
                criticidade,
                etapa_atual,
                observacao_interna,
                status,
                status,
                denuncia_id,
                empresa_id
            ))

            self.conn.commit()

            return {
                "valor_antigo": valor_antigo,
                "valor_novo": {
                    "status": status,
                    "criticidade": criticidade,
                    "etapa_atual": etapa_atual,
                    "observacao_interna": observacao_interna
                }
            }

        except Exception:
            self.conn.rollback()
            raise

    def listar_dados_exportacao(self, empresa_id, limite=None):
        sql_limite = ""
        params = [empresa_id]

        if limite is not None:
            try:
                limite = int(limite)
            except (TypeError, ValueError) as exc:
                raise ValueError("Limite de exportação inválido.") from exc

            limite = max(1, min(limite, 10000))
            sql_limite = "LIMIT %s"
            params.append(limite)

        self.cursor.execute(
            f"""
            SELECT
                d.protocolo,
                u.nome AS unidade,
                COALESCE(s.nome, 'Não informado') AS setor,
                COALESCE(d.categoria, d.tipo) AS categoria,
                COALESCE(d.criticidade, 'Não informada') AS criticidade,
                d.status,
                d.etapa_atual,
                d.criado_em
            FROM denuncias d
            INNER JOIN unidades u
                ON u.id = d.unidade_id
               AND u.empresa_id = d.empresa_id
            LEFT JOIN setores s
                ON s.id = d.setor_id
               AND s.empresa_id = d.empresa_id
            WHERE d.empresa_id = %s
            ORDER BY d.criado_em DESC
            {sql_limite}
            """,
            params
        )

        return self.cursor.fetchall()

    def atualizar_responsavel(
        self,
        denuncia_id,
        empresa_id,
        responsavel_id
    ):
        self.cursor.execute("""
            UPDATE denuncias d
            SET d.responsavel_id = %s
            WHERE d.id = %s
              AND d.empresa_id = %s
              AND (
                    %s IS NULL
                    OR EXISTS (
                        SELECT 1
                        FROM usuarios usr
                        WHERE usr.id = %s
                          AND usr.ativo = 1
                          AND (
                                usr.empresa_id = d.empresa_id
                                OR usr.empresa_id IS NULL
                          )
                    )
              )
        """, (
            responsavel_id,
            denuncia_id,
            empresa_id,
            responsavel_id,
            responsavel_id
        ))

        self.conn.commit()
        return self.cursor.rowcount > 0

    def criar_etapa_workflow(
        self,
        denuncia_id,
        empresa_id,
        etapa,
        status_etapa="PENDENTE",
        responsavel_id=None,
        prazo_limite=None,
        iniciado_em=None,
        concluido_em=None,
        observacao=None
    ):
        self.cursor.execute("""
            INSERT INTO denuncia_workflow (
                denuncia_id,
                empresa_id,
                etapa,
                status_etapa,
                responsavel_id,
                prazo_limite,
                iniciado_em,
                concluido_em,
                observacao
            )
            SELECT
                d.id,
                d.empresa_id,
                %s,
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
            etapa,
            status_etapa,
            responsavel_id,
            prazo_limite,
            iniciado_em,
            concluido_em,
            observacao,
            denuncia_id,
            empresa_id
        ))

        if self.cursor.rowcount == 0:
            self.conn.rollback()
            raise ValueError(
                "Denúncia não encontrada no escopo da empresa."
            )

        self.conn.commit()
        return self.cursor.lastrowid

    def listar_workflow(self, denuncia_id, empresa_id):
        self.cursor.execute("""
            SELECT
                w.id,
                w.denuncia_id,
                w.empresa_id,
                w.etapa,
                w.status_etapa,
                w.responsavel_id,
                w.prazo_limite,
                w.iniciado_em,
                w.concluido_em,
                w.observacao,
                w.criado_em,
                usr.nome AS responsavel
            FROM denuncia_workflow w
            INNER JOIN denuncias d
                ON d.id = w.denuncia_id
               AND d.empresa_id = w.empresa_id
            LEFT JOIN usuarios usr
                ON usr.id = w.responsavel_id
               AND (
                    usr.empresa_id = w.empresa_id
                    OR usr.empresa_id IS NULL
               )
            WHERE w.denuncia_id = %s
              AND w.empresa_id = %s
            ORDER BY w.id ASC
        """, (denuncia_id, empresa_id))

        return self.cursor.fetchall()

    def atualizar_etapa_atual(self, denuncia_id, empresa_id, etapa_atual):
        self.cursor.execute("""
            UPDATE denuncias
            SET etapa_atual = %s
            WHERE id = %s
              AND empresa_id = %s
        """, (etapa_atual, denuncia_id, empresa_id))

        self.conn.commit()
        return self.cursor.rowcount > 0

    def concluir_etapa_workflow(
        self,
        workflow_id,
        empresa_id,
        observacao=None
    ):
        self.cursor.execute("""
            UPDATE denuncia_workflow w
            INNER JOIN denuncias d
                ON d.id = w.denuncia_id
               AND d.empresa_id = w.empresa_id
            SET w.status_etapa = 'CONCLUIDA',
                w.concluido_em = NOW(),
                w.observacao = COALESCE(%s, w.observacao)
            WHERE w.id = %s
              AND w.empresa_id = %s
        """, (observacao, workflow_id, empresa_id))

        self.conn.commit()
        return self.cursor.rowcount > 0

    def concluir_etapa_atual_workflow(
        self,
        denuncia_id,
        empresa_id,
        etapa,
        observacao=None
    ):
        self.cursor.execute("""
            UPDATE denuncia_workflow
            SET status_etapa = 'CONCLUIDA',
                concluido_em = NOW(),
                observacao = COALESCE(%s, observacao)
            WHERE denuncia_id = %s
              AND empresa_id = %s
              AND etapa = %s
              AND status_etapa <> 'CONCLUIDA'
        """, (
            observacao,
            denuncia_id,
            empresa_id,
            etapa
        ))

        self.conn.commit()
        return self.cursor.rowcount > 0

    def iniciar_etapa_workflow(
        self,
        workflow_id,
        empresa_id,
        responsavel_id=None
    ):
        self.cursor.execute("""
            UPDATE denuncia_workflow w
            INNER JOIN denuncias d
                ON d.id = w.denuncia_id
               AND d.empresa_id = w.empresa_id
            SET w.status_etapa = 'EM_ANDAMENTO',
                w.iniciado_em = COALESCE(w.iniciado_em, NOW()),
                w.responsavel_id = COALESCE(%s, w.responsavel_id)
            WHERE w.id = %s
              AND w.empresa_id = %s
        """, (responsavel_id, workflow_id, empresa_id))

        self.conn.commit()
        return self.cursor.rowcount > 0

    def avancar_workflow(
        self,
        denuncia_id,
        empresa_id,
        etapa_atual,
        proxima_etapa,
        novo_status,
        usuario_id=None,
        observacao=None
    ):
        try:
            self.cursor.execute("""
                UPDATE denuncia_workflow
                SET status_etapa = 'CONCLUIDA',
                    concluido_em = NOW(),
                    observacao = COALESCE(%s, observacao)
                WHERE denuncia_id = %s
                  AND empresa_id = %s
                  AND etapa = %s
                  AND status_etapa <> 'CONCLUIDA'
            """, (
                observacao,
                denuncia_id,
                empresa_id,
                etapa_atual
            ))

            self.cursor.execute("""
                UPDATE denuncias
                SET etapa_atual = %s,
                    status = %s,
                    data_encerramento = CASE
                        WHEN %s IN ('CONCLUIDA', 'ARQUIVADA')
                            THEN NOW()
                        ELSE data_encerramento
                    END
                WHERE id = %s
                  AND empresa_id = %s
            """, (
                proxima_etapa["etapa"],
                novo_status,
                novo_status,
                denuncia_id,
                empresa_id
            ))

            if self.cursor.rowcount == 0:
                raise ValueError(
                    "Denúncia não encontrada para avanço do workflow."
                )

            self.cursor.execute("""
                INSERT INTO denuncia_workflow (
                    denuncia_id,
                    empresa_id,
                    etapa,
                    status_etapa,
                    responsavel_id,
                    prazo_limite,
                    iniciado_em,
                    concluido_em,
                    observacao
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                denuncia_id,
                empresa_id,
                proxima_etapa["etapa"],
                proxima_etapa["status_etapa"],
                proxima_etapa.get("responsavel_id") or usuario_id,
                proxima_etapa.get("prazo_limite"),
                proxima_etapa.get("iniciado_em"),
                proxima_etapa.get("concluido_em"),
                proxima_etapa.get("observacao")
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except Exception:
            self.conn.rollback()
            raise

    def listar_unidades(self, empresa_id):
        self.cursor.execute("""
            SELECT id, nome
            FROM unidades
            WHERE empresa_id = %s
              AND ativa = 1
            ORDER BY nome
        """, (empresa_id,))

        return self.cursor.fetchall()

    def listar_categorias(self, empresa_id):
        self.cursor.execute("""
            SELECT DISTINCT categoria
            FROM denuncias
            WHERE empresa_id = %s
              AND categoria IS NOT NULL
              AND categoria <> ''
            ORDER BY categoria
        """, (empresa_id,))

        return self.cursor.fetchall()

    def listar_criticidades(self, empresa_id):
        self.cursor.execute("""
            SELECT DISTINCT criticidade
            FROM denuncias
            WHERE empresa_id = %s
              AND criticidade IS NOT NULL
              AND criticidade <> ''
            ORDER BY criticidade
        """, (empresa_id,))

        return self.cursor.fetchall()

    def close(self):
        if self.cursor:
            self.cursor.close()

        if self.conn:
            self.conn.close()
