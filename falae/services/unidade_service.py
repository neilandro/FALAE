import re

from falae.repositories.unidade_repository import UnidadeRepository
from falae.services.context_service import ContextService


class UnidadeService:

    @staticmethod
    def listar():
        empresa_id = ContextService.empresa()
        repo = UnidadeRepository()

        try:
            return repo.listar_por_empresa(empresa_id)
        finally:
            repo.close()

    @staticmethod
    def obter(unidade_id):
        empresa_id = ContextService.empresa()
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
        empresa_id = ContextService.empresa()
        dados = UnidadeService._montar_dados_formulario(form)

        validacao = UnidadeService._validar_dados(dados)

        if not validacao["sucesso"]:
            return validacao

        repo = UnidadeRepository()

        try:
            if repo.existe_nome(
                empresa_id=empresa_id,
                nome=dados["nome"]
            ):
                return {
                    "sucesso": False,
                    "mensagem": "Já existe uma unidade com esse nome."
                }

           
            unidade_id = repo.criar(
                empresa_id=empresa_id,
                dados=dados
            )

            return {
                "sucesso": True,
                "mensagem": "Unidade cadastrada com sucesso.",
                "unidade_id": unidade_id
            }
        finally:
            repo.close()

    @staticmethod
    def editar(unidade_id, form):
        empresa_id = ContextService.empresa()
        dados = UnidadeService._montar_dados_formulario(form)

        validacao = UnidadeService._validar_dados(dados)

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
                    "mensagem": "Unidade não encontrada."
                }
        


            repo.atualizar(
                unidade_id=unidade_id,
                empresa_id=empresa_id,
                dados=dados
            )

            return {
                "sucesso": True,
                "mensagem": "Unidade atualizada com sucesso."
            }
        finally:
            repo.close()

    @staticmethod
    def alterar_status(unidade_id, ativa):
        empresa_id = ContextService.empresa()

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
                    "mensagem": "Unidade não encontrada."
                }

            repo.alterar_status(
                unidade_id=unidade_id,
                empresa_id=empresa_id,
                ativa=ativa
            )

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
        cnpj = UnidadeService._somente_numeros(
            form.get("cnpj", "")
        )

        cep = UnidadeService._somente_numeros(
            form.get("cep", "")
        )

        estado = (form.get("estado") or "").strip().upper()[:2]

        try:
            ativa = int(form.get("ativa", 1))
        except (TypeError, ValueError):
            ativa = 1

        if ativa not in (0, 1):
            ativa = 1

        return {
            "nome": (form.get("nome") or "").strip(),
            "cnpj": cnpj or None,
            "cep": cep or None,
            "endereco": (form.get("endereco") or "").strip() or None,
            "numero": (form.get("numero") or "").strip() or None,
            "complemento": (form.get("complemento") or "").strip() or None,
            "bairro": (form.get("bairro") or "").strip() or None,
            "cidade": (form.get("cidade") or "").strip() or None,
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

        if dados["cnpj"] and not UnidadeService._cnpj_valido(
            dados["cnpj"]
        ):
            return {
                "sucesso": False,
                "mensagem": "Informe um CNPJ válido."
            }

        if dados["cep"] and len(dados["cep"]) != 8:
            return {
                "sucesso": False,
                "mensagem": "Informe um CEP válido com 8 números."
            }

        if dados["estado"] and len(dados["estado"]) != 2:
            return {
                "sucesso": False,
                "mensagem": "Informe a sigla do estado com 2 letras."
            }

        return {
            "sucesso": True
        }

    @staticmethod
    def _somente_numeros(valor):
        return re.sub(r"\D", "", valor or "")

    @staticmethod
    def _cnpj_valido(cnpj):
        cnpj = UnidadeService._somente_numeros(cnpj)

        if len(cnpj) != 14:
            return False

        if cnpj == cnpj[0] * 14:
            return False

        def calcular_digito(base, pesos):
            soma = sum(
                int(numero) * peso
                for numero, peso in zip(base, pesos)
            )

            resto = soma % 11

            return "0" if resto < 2 else str(11 - resto)

        primeiro_digito = calcular_digito(
            cnpj[:12],
            [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        )

        segundo_digito = calcular_digito(
            cnpj[:12] + primeiro_digito,
            [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        )

        return cnpj[-2:] == primeiro_digito + segundo_digito