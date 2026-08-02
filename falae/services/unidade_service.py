import re

from falae.repositories.unidade_repository import UnidadeRepository
from falae.services.context_service import ContextService


class UnidadeService:
    """Regras de negócio relacionadas ao cadastro de unidades."""

    @staticmethod
    def _obter_empresa_id() -> int:
        empresa_id = ContextService.empresa()

        if not empresa_id:
            raise ValueError(
                "Nenhuma empresa ativa foi identificada."
            )

        return int(empresa_id)

    @staticmethod
    def listar():
        empresa_id = UnidadeService._obter_empresa_id()
        repo = UnidadeRepository()

        try:
            return repo.listar_por_empresa(empresa_id)
        finally:
            repo.close()

    @staticmethod
    def obter(unidade_id):
        empresa_id = UnidadeService._obter_empresa_id()
        repo = UnidadeRepository()

        try:
            return repo.obter_por_id(
                unidade_id=unidade_id,
                empresa_id=empresa_id
            )
        finally:
            repo.close()

    @staticmethod
    def criar(form):
        empresa_id = UnidadeService._obter_empresa_id()

        dados = UnidadeService._montar_dados_formulario(
            form
        )

        validacao = UnidadeService._validar_dados(
            dados
        )

        if not validacao["sucesso"]:
            return validacao

        repo = UnidadeRepository()

        try:
            unidade_existente = repo.existe_nome(
                empresa_id=empresa_id,
                nome=dados["nome"]
            )

            if unidade_existente:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Já existe uma unidade com esse nome."
                    )
                }

            unidade_id = repo.criar(
                empresa_id=empresa_id,
                dados=dados
            )

            return {
                "sucesso": True,
                "mensagem": (
                    "Unidade cadastrada com sucesso."
                ),
                "unidade_id": unidade_id
            }

        finally:
            repo.close()

    @staticmethod
    def editar(unidade_id, form):
        empresa_id = UnidadeService._obter_empresa_id()

        dados = UnidadeService._montar_dados_formulario(
            form
        )

        validacao = UnidadeService._validar_dados(
            dados
        )

        if not validacao["sucesso"]:
            return validacao

        repo = UnidadeRepository()

        try:
            unidade = repo.obter_por_id(
                unidade_id=unidade_id,
                empresa_id=empresa_id
            )

            if not unidade:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Unidade não encontrada ou sem "
                        "permissão para edição."
                    )
                }

            unidade_duplicada = repo.existe_nome(
                empresa_id=empresa_id,
                nome=dados["nome"],
                unidade_id=unidade_id
            )

            if unidade_duplicada:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Já existe outra unidade com esse nome."
                    )
                }

            atualizado = repo.atualizar(
                unidade_id=unidade_id,
                empresa_id=empresa_id,
                dados=dados
            )

            if not atualizado:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Não foi possível atualizar a unidade."
                    )
                }

            return {
                "sucesso": True,
                "mensagem": (
                    "Unidade atualizada com sucesso."
                )
            }

        finally:
            repo.close()

    @staticmethod
    def alterar_status(unidade_id, ativa):
        empresa_id = UnidadeService._obter_empresa_id()

        try:
            ativa = int(ativa)
        except (TypeError, ValueError):
            return {
                "sucesso": False,
                "mensagem": "Status inválido."
            }

        if ativa not in (0, 1):
            return {
                "sucesso": False,
                "mensagem": "Status inválido."
            }

        repo = UnidadeRepository()

        try:
            unidade = repo.obter_por_id(
                unidade_id=unidade_id,
                empresa_id=empresa_id
            )

            if not unidade:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Unidade não encontrada ou sem "
                        "permissão para alteração."
                    )
                }

            atualizado = repo.alterar_status(
                unidade_id=unidade_id,
                empresa_id=empresa_id,
                ativa=ativa
            )

            if not atualizado:
                return {
                    "sucesso": False,
                    "mensagem": (
                        "Não foi possível alterar o status "
                        "da unidade."
                    )
                }

            return {
                "sucesso": True,
                "mensagem": (
                    "Unidade ativada com sucesso."
                    if ativa == 1
                    else "Unidade inativada com sucesso."
                )
            }

        finally:
            repo.close()

    @staticmethod
    def _montar_dados_formulario(form):
        nome = UnidadeService._normalizar_texto(
            form.get("nome")
        )

        cnpj = UnidadeService._somente_numeros(
            form.get("cnpj", "")
        )

        cep = UnidadeService._somente_numeros(
            form.get("cep", "")
        )

        estado = (
            form.get("estado") or ""
        ).strip().upper()[:2]

        try:
            ativa = int(
                form.get("ativa", 1)
            )
        except (TypeError, ValueError):
            ativa = 1

        if ativa not in (0, 1):
            ativa = 1

        return {
            "nome": nome,
            "cnpj": cnpj or None,
            "cep": cep or None,
            "endereco": (
                UnidadeService._normalizar_texto(
                    form.get("endereco")
                ) or None
            ),
            "numero": (
                UnidadeService._normalizar_texto(
                    form.get("numero")
                ) or None
            ),
            "complemento": (
                UnidadeService._normalizar_texto(
                    form.get("complemento")
                ) or None
            ),
            "bairro": (
                UnidadeService._normalizar_texto(
                    form.get("bairro")
                ) or None
            ),
            "cidade": (
                UnidadeService._normalizar_texto(
                    form.get("cidade")
                ) or None
            ),
            "estado": estado or None,
            "ativa": ativa
        }

    @staticmethod
    def _validar_dados(dados):
        if not dados["nome"]:
            return {
                "sucesso": False,
                "mensagem": "Informe o nome da unidade."
            }

        if len(dados["nome"]) < 2:
            return {
                "sucesso": False,
                "mensagem": (
                    "O nome da unidade deve possuir "
                    "pelo menos 2 caracteres."
                )
            }

        if len(dados["nome"]) > 150:
            return {
                "sucesso": False,
                "mensagem": (
                    "O nome da unidade deve possuir "
                    "no máximo 150 caracteres."
                )
            }

        if (
            dados["cnpj"]
            and not UnidadeService._cnpj_valido(
                dados["cnpj"]
            )
        ):
            return {
                "sucesso": False,
                "mensagem": "Informe um CNPJ válido."
            }

        if (
            dados["cep"]
            and len(dados["cep"]) != 8
        ):
            return {
                "sucesso": False,
                "mensagem": (
                    "Informe um CEP válido com 8 números."
                )
            }

        if (
            dados["estado"]
            and len(dados["estado"]) != 2
        ):
            return {
                "sucesso": False,
                "mensagem": (
                    "Informe a sigla do estado com 2 letras."
                )
            }

        return {
            "sucesso": True
        }

    @staticmethod
    def _normalizar_texto(valor):
        return " ".join(
            (valor or "").strip().split()
        )

    @staticmethod
    def _somente_numeros(valor):
        return re.sub(
            r"\D",
            "",
            valor or ""
        )

    @staticmethod
    def _cnpj_valido(cnpj):
        cnpj = UnidadeService._somente_numeros(
            cnpj
        )

        if len(cnpj) != 14:
            return False

        if cnpj == cnpj[0] * 14:
            return False

        def calcular_digito(base, pesos):
            soma = sum(
                int(numero) * peso
                for numero, peso in zip(
                    base,
                    pesos
                )
            )

            resto = soma % 11

            return (
                "0"
                if resto < 2
                else str(11 - resto)
            )

        primeiro_digito = calcular_digito(
            cnpj[:12],
            [
                5, 4, 3, 2,
                9, 8, 7, 6,
                5, 4, 3, 2
            ]
        )

        segundo_digito = calcular_digito(
            cnpj[:12] + primeiro_digito,
            [
                6, 5, 4, 3, 2,
                9, 8, 7, 6,
                5, 4, 3, 2
            ]
        )

        return (
            cnpj[-2:]
            == primeiro_digito + segundo_digito
        )