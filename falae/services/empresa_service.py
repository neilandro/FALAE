import re
import uuid
from typing import Any

from flask import session

from falae.repositories.empresa_repository import (
    EmpresaRepository
)


class EmpresaService:

    @staticmethod
    def _obter_assessoria_id() -> int:
        assessoria_id = session.get(
            "assessoria_id"
        )

        if not assessoria_id:
            raise ValueError(
                "Nenhuma assessoria foi identificada "
                "para o usuário autenticado."
            )

        try:
            return int(
                assessoria_id
            )

        except (
            TypeError,
            ValueError
        ) as exc:
            raise ValueError(
                "A assessoria do usuário é inválida."
            ) from exc

    @staticmethod
    def _normalizar_inteiro(
        valor: Any
    ) -> int:
        if valor in (
            None,
            ""
        ):
            return 0

        try:
            return int(
                valor
            )

        except (
            TypeError,
            ValueError
        ):
            return 0

    @staticmethod
    def listar_empresas_assessoria():
        assessoria_id = (
            EmpresaService
            ._obter_assessoria_id()
        )

        return (
            EmpresaRepository
            .listar_por_assessoria(
                assessoria_id=assessoria_id
            )
        )

    @staticmethod
    def obter_dashboard_assessoria() -> dict:
        """
        Retorna os dados consolidados de todas as empresas
        pertencentes à assessoria autenticada.

        Nenhum dado de empresas pertencentes a outras
        assessorias deve ser retornado.
        """

        assessoria_id = (
            EmpresaService
            ._obter_assessoria_id()
        )

        empresas = (
            EmpresaRepository
            .listar_por_assessoria(
                assessoria_id=assessoria_id
            )
        )

        resumo = (
            EmpresaRepository
            .obter_resumo_dashboard_assessoria(
                assessoria_id=assessoria_id
            )
        )

        investigadores = (
            EmpresaRepository
            .listar_investigadores_assessoria(
                assessoria_id=assessoria_id
            )
        )

        denuncias_recentes = (
            EmpresaRepository
            .listar_denuncias_recentes_assessoria(
                assessoria_id=assessoria_id,
                limite=10
            )
        )

        total_empresas = (
            EmpresaService
            ._normalizar_inteiro(
                resumo.get(
                    "total_empresas"
                )
            )
        )

        total_denuncias = (
            EmpresaService
            ._normalizar_inteiro(
                resumo.get(
                    "total_denuncias"
                )
            )
        )

        total_usuarios = (
            EmpresaService
            ._normalizar_inteiro(
                resumo.get(
                    "total_usuarios"
                )
            )
        )

        total_investigadores = (
            EmpresaService
            ._normalizar_inteiro(
                resumo.get(
                    "total_investigadores"
                )
            )
        )

        denuncias_abertas = (
            EmpresaService
            ._normalizar_inteiro(
                resumo.get(
                    "denuncias_abertas"
                )
            )
        )

        denuncias_criticas = (
            EmpresaService
            ._normalizar_inteiro(
                resumo.get(
                    "denuncias_criticas"
                )
            )
        )

        denuncias_encerradas = (
            EmpresaService
            ._normalizar_inteiro(
                resumo.get(
                    "denuncias_encerradas"
                )
            )
        )

        return {
            "empresas": empresas,
            "investigadores": investigadores,
            "denuncias_recentes": denuncias_recentes,
            "total_empresas": total_empresas,
            "total_denuncias": total_denuncias,
            "total_usuarios": total_usuarios,
            "total_investigadores": (
                total_investigadores
            ),
            "denuncias_abertas": denuncias_abertas,
            "denuncias_criticas": denuncias_criticas,
            "denuncias_encerradas": (
                denuncias_encerradas
            )
        }

    @staticmethod
    def obter_empresa_assessoria(
        empresa_id
    ):
        assessoria_id = (
            EmpresaService
            ._obter_assessoria_id()
        )

        return (
            EmpresaRepository
            .buscar_por_id_assessoria(
                empresa_id=empresa_id,
                assessoria_id=assessoria_id
            )
        )

    @staticmethod
    def obter_empresa_global(
        empresa_id
    ):
        return (
            EmpresaRepository
            .buscar_por_id_global(
                empresa_id=empresa_id
            )
        )

    @staticmethod
    def criar_empresa_assessoria(
        nome,
        cnpj,
        plano
    ):
        assessoria_id = (
            EmpresaService
            ._obter_assessoria_id()
        )

        nome = str(
            nome or ""
        ).strip()

        cnpj = str(
            cnpj or ""
        ).strip()

        plano = str(
            plano or ""
        ).strip()

        if not nome:
            raise ValueError(
                "Informe o nome da empresa."
            )

        if not cnpj:
            raise ValueError(
                "Informe o CNPJ da empresa."
            )

        if not plano:
            raise ValueError(
                "Informe o plano da empresa."
            )

        slug = EmpresaService.gerar_slug(
            nome
        )

        token_publico = uuid.uuid4().hex

        return (
            EmpresaRepository
            .criar_para_assessoria(
                assessoria_id=assessoria_id,
                nome=nome,
                slug=slug,
                cnpj=cnpj,
                plano=plano,
                token_publico=token_publico
            )
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
        assessoria_id = (
            EmpresaService
            ._obter_assessoria_id()
        )

        empresa = (
            EmpresaRepository
            .buscar_por_id_assessoria(
                empresa_id=empresa_id,
                assessoria_id=assessoria_id
            )
        )

        if not empresa:
            raise ValueError(
                "Empresa não encontrada ou acesso "
                "não autorizado."
            )

        nome = str(
            nome or ""
        ).strip()

        cnpj = str(
            cnpj or ""
        ).strip()

        plano = str(
            plano or ""
        ).strip()

        slug = str(
            slug or ""
        ).strip()

        if not nome:
            raise ValueError(
                "Informe o nome da empresa."
            )

        if not cnpj:
            raise ValueError(
                "Informe o CNPJ da empresa."
            )

        if not plano:
            raise ValueError(
                "Informe o plano da empresa."
            )

        if not slug:
            slug = EmpresaService.gerar_slug(
                nome
            )

        if str(ativa) not in (
            "0",
            "1"
        ):
            ativa = 1

        return (
            EmpresaRepository
            .atualizar_por_assessoria(
                empresa_id=empresa_id,
                assessoria_id=assessoria_id,
                nome=nome,
                slug=slug,
                cnpj=cnpj,
                plano=plano,
                ativa=int(
                    ativa
                )
            )
        )

    @staticmethod
    def gerar_slug(
        texto
    ) -> str:
        texto = str(
            texto or ""
        ).lower().strip()

        texto = re.sub(
            r"[^a-z0-9\s-]",
            "",
            texto
        )

        texto = re.sub(
            r"\s+",
            "-",
            texto
        )

        texto = re.sub(
            r"-+",
            "-",
            texto
        )

        return texto.strip(
            "-"
        )