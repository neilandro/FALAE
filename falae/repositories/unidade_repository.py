from db import get_connection


class UnidadeRepository:

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def listar_por_empresa(self, empresa_id):
        self.cursor.execute("""
            SELECT
                id,
                empresa_id,
                nome,
                cnpj,
                cep,
                endereco,
                numero,
                complemento,
                bairro,
                cidade,
                estado,
                ativa,
                criado_em
            FROM unidades
            WHERE empresa_id = %s
            ORDER BY nome
        """, (empresa_id,))

        return self.cursor.fetchall()

    def obter_por_id(self, unidade_id, empresa_id):
        self.cursor.execute("""
            SELECT
                id,
                empresa_id,
                nome,
                cnpj,
                cep,
                endereco,
                numero,
                complemento,
                bairro,
                cidade,
                estado,
                ativa,
                criado_em
            FROM unidades
            WHERE id = %s
              AND empresa_id = %s
            LIMIT 1
        """, (
            unidade_id,
            empresa_id
        ))

        return self.cursor.fetchone()

    def criar(self, empresa_id, dados):
        self.cursor.execute("""
            INSERT INTO unidades (
                empresa_id,
                nome,
                cnpj,
                cep,
                endereco,
                numero,
                complemento,
                bairro,
                cidade,
                estado,
                ativa
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, 1
            )
        """, (
            empresa_id,
            dados.get("nome"),
            dados.get("cnpj"),
            dados.get("cep"),
            dados.get("endereco"),
            dados.get("numero"),
            dados.get("complemento"),
            dados.get("bairro"),
            dados.get("cidade"),
            dados.get("estado")
        ))

        self.conn.commit()

        return self.cursor.lastrowid

    def atualizar(self, unidade_id, empresa_id, dados):
        self.cursor.execute("""
            UPDATE unidades
            SET
                nome = %s,
                cnpj = %s,
                cep = %s,
                endereco = %s,
                numero = %s,
                complemento = %s,
                bairro = %s,
                cidade = %s,
                estado = %s,
                ativa = %s
            WHERE id = %s
              AND empresa_id = %s
        """, (
            dados.get("nome"),
            dados.get("cnpj"),
            dados.get("cep"),
            dados.get("endereco"),
            dados.get("numero"),
            dados.get("complemento"),
            dados.get("bairro"),
            dados.get("cidade"),
            dados.get("estado"),
            dados.get("ativa"),
            unidade_id,
            empresa_id
        ))

        self.conn.commit()

        return self.cursor.rowcount

    def existe_nome(self, empresa_id, nome, unidade_id=None):
        sql = """
            SELECT id
            FROM unidades
            WHERE empresa_id = %s
              AND LOWER(TRIM(nome)) = LOWER(TRIM(%s))
        """

        parametros = [empresa_id, nome]

        if unidade_id is not None:
            sql += """
                AND id <> %s
            """
            parametros.append(unidade_id)

        sql += """
            LIMIT 1
        """

        self.cursor.execute(sql, tuple(parametros))

        return self.cursor.fetchone()

    

    def alterar_status(self, unidade_id, empresa_id, ativa):
        self.cursor.execute("""
            UPDATE unidades
            SET ativa = %s
            WHERE id = %s
              AND empresa_id = %s
        """, (
            ativa,
            unidade_id,
            empresa_id
        ))

        self.conn.commit()

        return self.cursor.rowcount

    def close(self):
        self.cursor.close()
        self.conn.close()