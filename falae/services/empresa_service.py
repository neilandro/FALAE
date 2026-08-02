import re
import uuid
from typing import Any, Mapping

from flask import session

from falae.repositories.empresa_repository import EmpresaRepository
from falae.utils.cnpj import normalizar_cnpj, validar_cnpj


class EmpresaService:

    PLANOS_VALIDOS = {
        "BASICO",
        "PROFISSIONAL",
        "ENTERPRISE"
    }

    @staticmethod
    def _obter_assessoria_id() -> int:
        assessoria_id = session.get("assessoria_id")

        if not assessoria_id:
            raise ValueError(
                "Nenhuma assessoria foi identificada "
                "para o usuário autenticado."
            )

        try:
            return int(assessoria_id)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "A assessoria do usuário é inválida."
            ) from exc

    @staticmethod
    def _normalizar_inteiro(valor: Any) -> int:
        if valor in (None, ""):
            return 0

        try:
            return int(valor)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _texto(valor: Any, limite: int | None = None) -> str:
        texto = str(valor or "").strip()
        return texto[:limite] if limite else texto

    @staticmethod
    def _inteiro_opcional(valor: Any) -> int | None:
        if valor in (None, ""):
            return None

        try:
            numero = int(valor)
        except (TypeError, ValueError) as exc:
            raise ValueError("A assessoria informada é inválida.") from exc

        return numero if numero > 0 else None

    @staticmethod
    def _normalizar_ativa(valor: Any, padrao: int = 1) -> int:
        if str(valor) in ("0", "1"):
            return int(valor)
        return padrao

    @staticmethod
    def _normalizar_dados_formulario(dados: Mapping[str, Any]) -> dict:
        return {
            "assessoria_id": EmpresaService._inteiro_opcional(
                dados.get("assessoria_id")
            ),
            "nome": EmpresaService._texto(dados.get("nome"), 150),
            "cnpj": normalizar_cnpj(dados.get("cnpj")),
            "endereco": EmpresaService._texto(dados.get("endereco"), 255),
            "numero": EmpresaService._texto(dados.get("numero"), 30),
            "complemento": EmpresaService._texto(
                dados.get("complemento"),
                120
            ),
            "bairro": EmpresaService._texto(dados.get("bairro"), 120),
            "cidade": EmpresaService._texto(dados.get("cidade"), 120),
            "estado": EmpresaService._texto(
                dados.get("estado"),
                2
            ).upper(),
            "cep": re.sub(r"\D", "", str(dados.get("cep") or ""))[:8],
            "contato_nome": EmpresaService._texto(
                dados.get("contato_nome"),
                150
            ),
            "contato_cargo": EmpresaService._texto(
                dados.get("contato_cargo"),
                120
            ),
            "contato_email": EmpresaService._texto(
                dados.get("contato_email"),
                150
            ).lower(),
            "contato_telefone": EmpresaService._texto(
                dados.get("contato_telefone"),
                30
            ),
            "contato_whatsapp": EmpresaService._texto(
                dados.get("contato_whatsapp"),
                30
            ),
            "plano": EmpresaService._texto(
                dados.get("plano"),
                30
            ).upper(),
            "ativa": EmpresaService._normalizar_ativa(
                dados.get("ativa"),
                1
            )
        }

    @staticmethod
    def _validar_dados_empresa(dados: dict) -> None:
        if not dados["nome"]:
            raise ValueError("Informe o nome da empresa.")

        if len(dados["nome"]) < 2:
            raise ValueError("O nome da empresa deve possuir ao menos 2 caracteres.")

        if not dados["cnpj"]:
            raise ValueError("Informe o CNPJ da empresa.")

        if not validar_cnpj(dados["cnpj"]):
            raise ValueError(
                "Informe um CNPJ válido. O sistema aceita os formatos "
                "numérico e alfanumérico."
            )

        if dados["plano"] not in EmpresaService.PLANOS_VALIDOS:
            raise ValueError("Selecione um plano válido para a empresa.")

        if dados["estado"] and not re.fullmatch(r"[A-Z]{2}", dados["estado"]):
            raise ValueError("Informe o estado utilizando uma UF válida com 2 letras.")

        if dados["cep"] and len(dados["cep"]) != 8:
            raise ValueError("Informe um CEP válido com 8 números.")

        email = dados["contato_email"]
        if email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValueError("Informe um e-mail de contato válido.")

    @staticmethod
    def _validar_duplicidade(dados: dict, ignorar_empresa_id=None) -> None:
        if EmpresaRepository.existe_cnpj(
            dados["assessoria_id"],
            dados["cnpj"],
            ignorar_empresa_id=ignorar_empresa_id
        ):
            raise ValueError(
                "Já existe uma empresa cadastrada com este CNPJ nesta assessoria."
            )

        if EmpresaRepository.existe_slug(
            dados["slug"],
            ignorar_empresa_id=ignorar_empresa_id
        ):
            raise ValueError(
                "Já existe uma empresa com a mesma chave de acesso. "
                "Altere o nome da empresa."
            )

    @staticmethod
    def listar_empresas_global():
        return EmpresaRepository.listar_global()

    @staticmethod
    def listar_assessorias_ativas():
        return EmpresaRepository.listar_assessorias_ativas()

    @staticmethod
    def obter_empresa_global_completa(empresa_id):
        return EmpresaRepository.buscar_dados_completos_global(empresa_id)

    @staticmethod
    def obter_detalhe_empresa_global(empresa_id) -> dict | None:
        empresa = EmpresaRepository.buscar_dados_completos_global(empresa_id)

        if not empresa:
            return None

        totais = EmpresaRepository.obter_totais_global(empresa_id)

        return {
            "empresa": empresa,
            "total_usuarios": int(totais.get("total_usuarios") or 0),
            "total_unidades": int(totais.get("total_unidades") or 0),
            "total_setores": int(totais.get("total_setores") or 0),
            "total_denuncias": int(totais.get("total_denuncias") or 0)
        }

    @staticmethod
    def criar_empresa_global(dados_formulario: Mapping[str, Any]) -> dict:
        try:
            dados = EmpresaService._normalizar_dados_formulario(
                dados_formulario
            )
            dados["slug"] = EmpresaService.gerar_slug(dados["nome"])
            dados["token_publico"] = uuid.uuid4().hex
            dados["ativa"] = 1

            EmpresaService._validar_dados_empresa(dados)
            EmpresaService._validar_duplicidade(dados)

            empresa_id = EmpresaRepository.criar_global(dados)

            return {
                "sucesso": True,
                "mensagem": "Empresa cadastrada com sucesso.",
                "empresa_id": empresa_id,
                "dados": dados
            }

        except ValueError as exc:
            return {
                "sucesso": False,
                "mensagem": str(exc),
                "dados": dict(dados_formulario)
            }

    @staticmethod
    def atualizar_empresa_global(
        empresa_id,
        dados_formulario: Mapping[str, Any]
    ) -> dict:
        empresa = EmpresaRepository.buscar_dados_completos_global(empresa_id)

        if not empresa:
            return {
                "sucesso": False,
                "mensagem": "Empresa não encontrada.",
                "dados": dict(dados_formulario)
            }

        try:
            dados = EmpresaService._normalizar_dados_formulario(
                dados_formulario
            )
            dados["slug"] = EmpresaService.gerar_slug(dados["nome"])

            EmpresaService._validar_dados_empresa(dados)
            EmpresaService._validar_duplicidade(
                dados,
                ignorar_empresa_id=empresa_id
            )

            EmpresaRepository.atualizar_global(empresa_id, dados)

            return {
                "sucesso": True,
                "mensagem": "Empresa atualizada com sucesso.",
                "empresa_id": empresa_id,
                "dados": dados
            }

        except ValueError as exc:
            return {
                "sucesso": False,
                "mensagem": str(exc),
                "empresa_id": empresa_id,
                "dados": dict(dados_formulario)
            }

    @staticmethod
    def listar_empresas_assessoria():
        assessoria_id = EmpresaService._obter_assessoria_id()
        return EmpresaRepository.listar_por_assessoria(
            assessoria_id=assessoria_id
        )

    @staticmethod
    def obter_dashboard_assessoria() -> dict:
        assessoria_id = EmpresaService._obter_assessoria_id()

        empresas = EmpresaRepository.listar_por_assessoria(
            assessoria_id=assessoria_id
        )
        resumo = EmpresaRepository.obter_resumo_dashboard_assessoria(
            assessoria_id=assessoria_id
        )
        investigadores = EmpresaRepository.listar_investigadores_assessoria(
            assessoria_id=assessoria_id
        )
        denuncias_recentes = (
            EmpresaRepository.listar_denuncias_recentes_assessoria(
                assessoria_id=assessoria_id,
                limite=10
            )
        )

        return {
            "empresas": empresas,
            "investigadores": investigadores,
            "denuncias_recentes": denuncias_recentes,
            "total_empresas": EmpresaService._normalizar_inteiro(
                resumo.get("total_empresas")
            ),
            "total_denuncias": EmpresaService._normalizar_inteiro(
                resumo.get("total_denuncias")
            ),
            "total_usuarios": EmpresaService._normalizar_inteiro(
                resumo.get("total_usuarios")
            ),
            "total_investigadores": EmpresaService._normalizar_inteiro(
                resumo.get("total_investigadores")
            ),
            "denuncias_abertas": EmpresaService._normalizar_inteiro(
                resumo.get("denuncias_abertas")
            ),
            "denuncias_criticas": EmpresaService._normalizar_inteiro(
                resumo.get("denuncias_criticas")
            ),
            "denuncias_encerradas": EmpresaService._normalizar_inteiro(
                resumo.get("denuncias_encerradas")
            )
        }

    @staticmethod
    def obter_empresa_assessoria(empresa_id):
        assessoria_id = EmpresaService._obter_assessoria_id()
        return EmpresaRepository.buscar_por_id_assessoria(
            empresa_id=empresa_id,
            assessoria_id=assessoria_id
        )

    @staticmethod
    def obter_empresa_global(empresa_id):
        return EmpresaRepository.buscar_por_id_global(
            empresa_id=empresa_id
        )

    @staticmethod
    def criar_empresa_assessoria(nome, cnpj, plano):
        assessoria_id = EmpresaService._obter_assessoria_id()

        dados = {
            "assessoria_id": assessoria_id,
            "nome": EmpresaService._texto(nome, 150),
            "cnpj": normalizar_cnpj(cnpj),
            "plano": EmpresaService._texto(plano, 30).upper()
        }
        dados["slug"] = EmpresaService.gerar_slug(dados["nome"])

        if not dados["nome"]:
            raise ValueError("Informe o nome da empresa.")

        if not validar_cnpj(dados["cnpj"]):
            raise ValueError("Informe um CNPJ válido.")

        if dados["plano"] not in EmpresaService.PLANOS_VALIDOS:
            raise ValueError("Informe um plano válido.")

        EmpresaService._validar_duplicidade(dados)

        return EmpresaRepository.criar_para_assessoria(
            assessoria_id=assessoria_id,
            nome=dados["nome"],
            slug=dados["slug"],
            cnpj=dados["cnpj"],
            plano=dados["plano"],
            token_publico=uuid.uuid4().hex
        )

    @staticmethod
    def atualizar_empresa_assessoria(
        empresa_id,
        nome,
        slug,
        cnpj,
        plano,
        ativa
    ):
        assessoria_id = EmpresaService._obter_assessoria_id()

        empresa = EmpresaRepository.buscar_por_id_assessoria(
            empresa_id=empresa_id,
            assessoria_id=assessoria_id
        )

        if not empresa:
            raise ValueError(
                "Empresa não encontrada ou acesso não autorizado."
            )

        nome = EmpresaService._texto(nome, 150)
        cnpj = normalizar_cnpj(cnpj)
        plano = EmpresaService._texto(plano, 30).upper()
        slug = EmpresaService._texto(slug) or EmpresaService.gerar_slug(nome)

        if not nome:
            raise ValueError("Informe o nome da empresa.")

        if not validar_cnpj(cnpj):
            raise ValueError("Informe um CNPJ válido.")

        if plano not in EmpresaService.PLANOS_VALIDOS:
            raise ValueError("Informe um plano válido.")

        dados_duplicidade = {
            "assessoria_id": assessoria_id,
            "cnpj": cnpj,
            "slug": slug
        }
        EmpresaService._validar_duplicidade(
            dados_duplicidade,
            ignorar_empresa_id=empresa_id
        )

        return EmpresaRepository.atualizar_por_assessoria(
            empresa_id=empresa_id,
            assessoria_id=assessoria_id,
            nome=nome,
            slug=slug,
            cnpj=cnpj,
            plano=plano,
            ativa=EmpresaService._normalizar_ativa(ativa, 1)
        )

    @staticmethod
    def gerar_slug(texto) -> str:
        texto = str(texto or "").lower().strip()
        texto = re.sub(r"[^a-z0-9\s-]", "", texto)
        texto = re.sub(r"\s+", "-", texto)
        texto = re.sub(r"-+", "-", texto)
        return texto.strip("-")