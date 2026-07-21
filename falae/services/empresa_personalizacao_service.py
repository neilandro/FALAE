import re
import unicodedata
import uuid
from pathlib import Path
from typing import Any

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from falae.repositories.empresa_personalizacao_repository import (
    EmpresaPersonalizacaoRepository
)
from falae.services.context_service import ContextService


class EmpresaPersonalizacaoService:
    """Regras de negócio da personalização visual da empresa."""

    COR_PADRAO_PRIMARIA = "#1F4E78"
    COR_PADRAO_SECUNDARIA = "#163A5C"

    NOME_CANAL_PADRAO = "Canal de Denúncias"

    MENSAGEM_BOAS_VINDAS_PADRAO = (
        "Este é um canal seguro para o registro de denúncias. "
        "As informações serão tratadas com confidencialidade "
        "e responsabilidade."
    )

    TEXTO_LGPD_PADRAO = (
        "Os dados informados serão utilizados exclusivamente "
        "para análise, tratamento e acompanhamento da denúncia, "
        "conforme a legislação aplicável."
    )

    TERMO_USO_PADRAO = (
        "Ao utilizar este canal, o denunciante declara que as "
        "informações fornecidas são verdadeiras e apresentadas "
        "de boa-fé."
    )

    EXTENSOES_LOGO = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }

    EXTENSOES_FAVICON = {
        "png",
        "ico"
    }

    TAMANHO_MAXIMO_LOGO = 3 * 1024 * 1024
    TAMANHO_MAXIMO_FAVICON = 1 * 1024 * 1024

    TAMANHO_MINIMO_SLUG = 3
    TAMANHO_MAXIMO_SLUG = 100

    SLUGS_RESERVADOS = {
        "admin",
        "api",
        "app",
        "assessoria",
        "canal",
        "dashboard",
        "denuncia",
        "denuncias",
        "empresa",
        "empresas",
        "favicon",
        "login",
        "logout",
        "painel",
        "publico",
        "root",
        "static",
        "sistema",
        "super-admin",
        "uploads",
        "usuario",
        "usuarios"
    }

    @staticmethod
    def _obter_empresa_id() -> int:
        empresa_id = ContextService.empresa()

        if not empresa_id:
            raise ValueError(
                "Nenhuma empresa ativa foi identificada."
            )

        return int(empresa_id)

    @staticmethod
    def _normalizar_texto(
        valor: str | None
    ) -> str:
        if valor is None:
            return ""

        return valor.strip()

    @staticmethod
    def _normalizar_nome_canal(
        nome_canal: str | None
    ) -> str:
        nome_normalizado = " ".join(
            (nome_canal or "").strip().split()
        )

        if not nome_normalizado:
            raise ValueError(
                "Informe o nome do canal."
            )

        if len(nome_normalizado) < 3:
            raise ValueError(
                "O nome do canal deve possuir pelo menos 3 caracteres."
            )

        if len(nome_normalizado) > 120:
            raise ValueError(
                "O nome do canal deve possuir no máximo 120 caracteres."
            )

        return nome_normalizado

    @staticmethod
    def _normalizar_cor(
        cor: str | None,
        nome_campo: str
    ) -> str:
        cor_normalizada = (cor or "").strip().upper()

        if not cor_normalizada:
            raise ValueError(
                f"Informe a {nome_campo}."
            )

        if not re.fullmatch(
            r"#[0-9A-F]{6}",
            cor_normalizada
        ):
            raise ValueError(
                f"A {nome_campo} deve estar no formato hexadecimal. "
                "Exemplo: #1F4E78."
            )

        return cor_normalizada

    @staticmethod
    def _validar_tamanho_texto(
        texto: str,
        nome_campo: str,
        limite: int
    ) -> None:
        if len(texto) > limite:
            raise ValueError(
                f"O campo {nome_campo} deve possuir no máximo "
                f"{limite} caracteres."
            )

    @staticmethod
    def _normalizar_booleano(
        valor: Any
    ) -> bool:
        if isinstance(valor, bool):
            return valor

        if isinstance(valor, int):
            return valor == 1

        if isinstance(valor, str):
            return valor.strip().lower() in {
                "1",
                "true",
                "on",
                "sim",
                "yes"
            }

        return False

    @staticmethod
    def _remover_acentos(
        valor: str
    ) -> str:
        texto_normalizado = unicodedata.normalize(
            "NFKD",
            valor
        )

        return "".join(
            caractere
            for caractere in texto_normalizado
            if not unicodedata.combining(caractere)
        )

    @classmethod
    def _normalizar_slug(
        cls,
        slug: str | None
    ) -> str:
        slug_original = (
            slug or ""
        ).strip().lower()

        if not slug_original:
            raise ValueError(
                "Informe o endereço público da empresa."
            )

        slug_sem_acentos = cls._remover_acentos(
            slug_original
        )

        slug_normalizado = re.sub(
            r"[^a-z0-9]+",
            "-",
            slug_sem_acentos
        )

        slug_normalizado = re.sub(
            r"-+",
            "-",
            slug_normalizado
        ).strip("-")

        if not slug_normalizado:
            raise ValueError(
                "O endereço público informado é inválido."
            )

        if len(slug_normalizado) < cls.TAMANHO_MINIMO_SLUG:
            raise ValueError(
                "O endereço público deve possuir pelo menos "
                f"{cls.TAMANHO_MINIMO_SLUG} caracteres."
            )

        if len(slug_normalizado) > cls.TAMANHO_MAXIMO_SLUG:
            raise ValueError(
                "O endereço público deve possuir no máximo "
                f"{cls.TAMANHO_MAXIMO_SLUG} caracteres."
            )

        if slug_normalizado in cls.SLUGS_RESERVADOS:
            raise ValueError(
                "Este endereço público é reservado pelo sistema. "
                "Escolha outro."
            )

        if not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*",
            slug_normalizado
        ):
            raise ValueError(
                "O endereço público deve conter apenas letras, "
                "números e hífens."
            )

        return slug_normalizado

    @classmethod
    def _gerar_slug_disponivel(
        cls,
        nome_empresa: str,
        empresa_id: int
    ) -> str:
        slug_base = cls._normalizar_slug(
            nome_empresa
        )

        if not EmpresaPersonalizacaoRepository.slug_em_uso(
            slug=slug_base,
            ignorar_empresa_id=empresa_id
        ):
            return slug_base

        contador = 2

        while contador <= 9999:
            sufixo = f"-{contador}"

            limite_base = (
                cls.TAMANHO_MAXIMO_SLUG
                - len(sufixo)
            )

            base_reduzida = slug_base[
                :limite_base
            ].rstrip("-")

            slug_candidato = (
                f"{base_reduzida}{sufixo}"
            )

            if not EmpresaPersonalizacaoRepository.slug_em_uso(
                slug=slug_candidato,
                ignorar_empresa_id=empresa_id
            ):
                return slug_candidato

            contador += 1

        raise ValueError(
            "Não foi possível gerar um endereço público disponível."
        )

    @staticmethod
    def _arquivo_enviado(
        arquivo: FileStorage | None
    ) -> bool:
        return bool(
            arquivo
            and arquivo.filename
            and arquivo.filename.strip()
        )

    @staticmethod
    def _obter_extensao(
        arquivo: FileStorage
    ) -> str:
        nome_seguro = secure_filename(
            arquivo.filename or ""
        )

        if "." not in nome_seguro:
            return ""

        return nome_seguro.rsplit(
            ".",
            1
        )[1].lower()

    @staticmethod
    def _obter_tamanho_arquivo(
        arquivo: FileStorage
    ) -> int:
        posicao_atual = arquivo.stream.tell()

        arquivo.stream.seek(
            0,
            2
        )

        tamanho = arquivo.stream.tell()

        arquivo.stream.seek(
            posicao_atual
        )

        return tamanho

    @classmethod
    def _validar_arquivo(
        cls,
        arquivo: FileStorage,
        tipo: str
    ) -> str:
        extensao = cls._obter_extensao(
            arquivo
        )

        if tipo == "logo":
            extensoes_permitidas = cls.EXTENSOES_LOGO
            tamanho_maximo = cls.TAMANHO_MAXIMO_LOGO
            nome_amigavel = "logotipo"

        elif tipo == "favicon":
            extensoes_permitidas = cls.EXTENSOES_FAVICON
            tamanho_maximo = cls.TAMANHO_MAXIMO_FAVICON
            nome_amigavel = "favicon"

        else:
            raise ValueError(
                "Tipo de arquivo inválido."
            )

        if extensao not in extensoes_permitidas:
            extensoes_texto = ", ".join(
                sorted(extensoes_permitidas)
            ).upper()

            raise ValueError(
                f"O {nome_amigavel} deve estar em um dos formatos: "
                f"{extensoes_texto}."
            )

        tamanho = cls._obter_tamanho_arquivo(
            arquivo
        )

        if tamanho <= 0:
            raise ValueError(
                f"O arquivo de {nome_amigavel} está vazio."
            )

        if tamanho > tamanho_maximo:
            limite_mb = round(
                tamanho_maximo / 1024 / 1024
            )

            raise ValueError(
                f"O arquivo de {nome_amigavel} deve possuir no máximo "
                f"{limite_mb} MB."
            )

        return extensao

    @staticmethod
    def _diretorio_upload(
        empresa_id: int,
        tipo: str
    ) -> Path:
        diretorio_static = Path(
            current_app.static_folder
        )

        diretorio = (
            diretorio_static
            / "uploads"
            / "empresas"
            / f"empresa_{empresa_id}"
            / tipo
        )

        diretorio.mkdir(
            parents=True,
            exist_ok=True
        )

        return diretorio

    @staticmethod
    def _caminho_relativo(
        empresa_id: int,
        tipo: str,
        nome_arquivo: str
    ) -> str:
        return (
            f"uploads/empresas/"
            f"empresa_{empresa_id}/"
            f"{tipo}/"
            f"{nome_arquivo}"
        )

    @classmethod
    def _salvar_arquivo(
        cls,
        arquivo: FileStorage,
        empresa_id: int,
        tipo: str
    ) -> str:
        extensao = cls._validar_arquivo(
            arquivo=arquivo,
            tipo=tipo
        )

        prefixo = (
            "logo"
            if tipo == "logo"
            else "favicon"
        )

        nome_arquivo = (
            f"{prefixo}_"
            f"{uuid.uuid4().hex}."
            f"{extensao}"
        )

        diretorio = cls._diretorio_upload(
            empresa_id=empresa_id,
            tipo=tipo
        )

        caminho_completo = (
            diretorio
            / nome_arquivo
        )

        arquivo.stream.seek(0)

        arquivo.save(
            caminho_completo
        )

        return cls._caminho_relativo(
            empresa_id=empresa_id,
            tipo=tipo,
            nome_arquivo=nome_arquivo
        )

    @staticmethod
    def _remover_arquivo_fisico(
        caminho_relativo: str | None
    ) -> None:
        if not caminho_relativo:
            return

        diretorio_static = Path(
            current_app.static_folder
        ).resolve()

        caminho_completo = (
            diretorio_static
            / caminho_relativo
        ).resolve()

        try:
            caminho_completo.relative_to(
                diretorio_static
            )
        except ValueError:
            return

        if (
            caminho_completo.exists()
            and caminho_completo.is_file()
        ):
            caminho_completo.unlink()

    @classmethod
    def _garantir_personalizacao(
        cls,
        empresa_id: int
    ) -> dict[str, Any]:
        personalizacao = (
            EmpresaPersonalizacaoRepository.buscar_por_empresa(
                empresa_id
            )
        )

        if personalizacao:
            return personalizacao

        EmpresaPersonalizacaoRepository.criar_padrao(
            empresa_id
        )

        personalizacao = (
            EmpresaPersonalizacaoRepository.buscar_por_empresa(
                empresa_id
            )
        )

        if not personalizacao:
            raise ValueError(
                "Não foi possível criar a personalização padrão da empresa."
            )

        return personalizacao

    @classmethod
    def obter(cls) -> dict[str, Any]:
        empresa_id = cls._obter_empresa_id()

        personalizacao = cls._garantir_personalizacao(
            empresa_id
        )

        if not personalizacao.get(
            "empresa_slug"
        ):
            slug_gerado = cls._gerar_slug_disponivel(
                nome_empresa=personalizacao["empresa_nome"],
                empresa_id=empresa_id
            )

            EmpresaPersonalizacaoRepository.atualizar_slug_empresa(
                empresa_id=empresa_id,
                slug=slug_gerado
            )

            personalizacao = (
                EmpresaPersonalizacaoRepository.buscar_por_empresa(
                    empresa_id
                )
            )

        if not personalizacao:
            raise ValueError(
                "Não foi possível carregar a personalização da empresa."
            )

        return personalizacao

    @classmethod
    def obter_por_slug(
        cls,
        slug: str | None
    ) -> dict[str, Any]:
        slug_normalizado = cls._normalizar_slug(
            slug
        )

        personalizacao = (
            EmpresaPersonalizacaoRepository.buscar_por_slug(
                slug_normalizado
            )
        )

        if not personalizacao:
            raise ValueError(
                "Canal de denúncias não encontrado."
            )

        if not personalizacao.get(
            "empresa_ativa"
        ):
            raise ValueError(
                "Este canal de denúncias está temporariamente indisponível."
            )

        return personalizacao

    @classmethod
    def atualizar_slug(
        cls,
        slug: str | None
    ) -> dict[str, Any]:
        empresa_id = cls._obter_empresa_id()

        cls._garantir_personalizacao(
            empresa_id
        )

        slug_normalizado = cls._normalizar_slug(
            slug
        )

        if EmpresaPersonalizacaoRepository.slug_em_uso(
            slug=slug_normalizado,
            ignorar_empresa_id=empresa_id
        ):
            raise ValueError(
                "Este endereço público já está sendo utilizado "
                "por outra empresa."
            )

        atualizado = (
            EmpresaPersonalizacaoRepository.atualizar_slug_empresa(
                empresa_id=empresa_id,
                slug=slug_normalizado
            )
        )

        if not atualizado:
            slug_atual = (
                EmpresaPersonalizacaoRepository.buscar_slug_empresa(
                    empresa_id
                )
            )

            if slug_atual != slug_normalizado:
                raise ValueError(
                    "Não foi possível atualizar o endereço público."
                )

        personalizacao = (
            EmpresaPersonalizacaoRepository.buscar_por_empresa(
                empresa_id
            )
        )

        if not personalizacao:
            raise ValueError(
                "Não foi possível carregar a personalização atualizada."
            )

        return personalizacao

    @classmethod
    def gerar_slug_automatico(
        cls
    ) -> dict[str, Any]:
        empresa_id = cls._obter_empresa_id()

        personalizacao = cls._garantir_personalizacao(
            empresa_id
        )

        slug_gerado = cls._gerar_slug_disponivel(
            nome_empresa=personalizacao["empresa_nome"],
            empresa_id=empresa_id
        )

        EmpresaPersonalizacaoRepository.atualizar_slug_empresa(
            empresa_id=empresa_id,
            slug=slug_gerado
        )

        personalizacao_atualizada = (
            EmpresaPersonalizacaoRepository.buscar_por_empresa(
                empresa_id
            )
        )

        if not personalizacao_atualizada:
            raise ValueError(
                "Não foi possível carregar o endereço público gerado."
            )

        return personalizacao_atualizada

    @classmethod
    def atualizar(
        cls,
        nome_canal: str | None,
        cor_primaria: str | None,
        cor_secundaria: str | None,
        mensagem_boas_vindas: str | None,
        texto_lgpd: str | None,
        termo_uso: str | None,
        mostrar_logo: Any,
        mostrar_nome_empresa: Any,
        logo: FileStorage | None = None,
        favicon: FileStorage | None = None
    ) -> dict[str, Any]:
        empresa_id = cls._obter_empresa_id()

        personalizacao_atual = (
            cls._garantir_personalizacao(
                empresa_id
            )
        )

        nome_canal_normalizado = (
            cls._normalizar_nome_canal(
                nome_canal
            )
        )

        cor_primaria_normalizada = (
            cls._normalizar_cor(
                cor_primaria,
                "cor primária"
            )
        )

        cor_secundaria_normalizada = (
            cls._normalizar_cor(
                cor_secundaria,
                "cor secundária"
            )
        )

        mensagem_normalizada = (
            cls._normalizar_texto(
                mensagem_boas_vindas
            )
        )

        texto_lgpd_normalizado = (
            cls._normalizar_texto(
                texto_lgpd
            )
        )

        termo_uso_normalizado = (
            cls._normalizar_texto(
                termo_uso
            )
        )

        cls._validar_tamanho_texto(
            mensagem_normalizada,
            "mensagem de boas-vindas",
            2000
        )

        cls._validar_tamanho_texto(
            texto_lgpd_normalizado,
            "texto LGPD",
            5000
        )

        cls._validar_tamanho_texto(
            termo_uso_normalizado,
            "termo de uso",
            5000
        )

        mostrar_logo_normalizado = (
            cls._normalizar_booleano(
                mostrar_logo
            )
        )

        mostrar_nome_normalizado = (
            cls._normalizar_booleano(
                mostrar_nome_empresa
            )
        )

        novo_logo = None
        novo_favicon = None

        logo_anterior = personalizacao_atual.get(
            "empresa_logo"
        )

        favicon_anterior = personalizacao_atual.get(
            "favicon"
        )

        try:
            if cls._arquivo_enviado(logo):
                novo_logo = cls._salvar_arquivo(
                    arquivo=logo,
                    empresa_id=empresa_id,
                    tipo="logo"
                )

            if cls._arquivo_enviado(favicon):
                novo_favicon = cls._salvar_arquivo(
                    arquivo=favicon,
                    empresa_id=empresa_id,
                    tipo="favicon"
                )

            if novo_logo:
                EmpresaPersonalizacaoRepository.atualizar_logo_empresa(
                    empresa_id=empresa_id,
                    logo=novo_logo
                )

            if novo_favicon:
                atualizado = (
                    EmpresaPersonalizacaoRepository.atualizar(
                        empresa_id=empresa_id,
                        nome_canal=nome_canal_normalizado,
                        favicon=novo_favicon,
                        cor_primaria=cor_primaria_normalizada,
                        cor_secundaria=cor_secundaria_normalizada,
                        mensagem_boas_vindas=mensagem_normalizada,
                        texto_lgpd=texto_lgpd_normalizado,
                        termo_uso=termo_uso_normalizado,
                        mostrar_logo=mostrar_logo_normalizado,
                        mostrar_nome_empresa=mostrar_nome_normalizado
                    )
                )

            else:
                atualizado = (
                    EmpresaPersonalizacaoRepository.atualizar_sem_favicon(
                        empresa_id=empresa_id,
                        nome_canal=nome_canal_normalizado,
                        cor_primaria=cor_primaria_normalizada,
                        cor_secundaria=cor_secundaria_normalizada,
                        mensagem_boas_vindas=mensagem_normalizada,
                        texto_lgpd=texto_lgpd_normalizado,
                        termo_uso=termo_uso_normalizado,
                        mostrar_logo=mostrar_logo_normalizado,
                        mostrar_nome_empresa=mostrar_nome_normalizado
                    )
                )

            if not atualizado:
                personalizacao_existente = (
                    EmpresaPersonalizacaoRepository.buscar_por_empresa(
                        empresa_id
                    )
                )

                if not personalizacao_existente:
                    raise ValueError(
                        "Não foi possível atualizar a personalização."
                    )

        except Exception:
            if novo_logo:
                cls._remover_arquivo_fisico(
                    novo_logo
                )

            if novo_favicon:
                cls._remover_arquivo_fisico(
                    novo_favicon
                )

            raise

        if novo_logo and logo_anterior:
            cls._remover_arquivo_fisico(
                logo_anterior
            )

        if novo_favicon and favicon_anterior:
            cls._remover_arquivo_fisico(
                favicon_anterior
            )

        personalizacao = (
            EmpresaPersonalizacaoRepository.buscar_por_empresa(
                empresa_id
            )
        )

        if not personalizacao:
            raise ValueError(
                "Não foi possível carregar a personalização atualizada."
            )

        return personalizacao

    @classmethod
    def remover_logo(cls) -> dict[str, Any]:
        empresa_id = cls._obter_empresa_id()

        personalizacao = (
            cls._garantir_personalizacao(
                empresa_id
            )
        )

        logo_atual = personalizacao.get(
            "empresa_logo"
        )

        EmpresaPersonalizacaoRepository.remover_logo_empresa(
            empresa_id
        )

        cls._remover_arquivo_fisico(
            logo_atual
        )

        personalizacao_atualizada = (
            EmpresaPersonalizacaoRepository.buscar_por_empresa(
                empresa_id
            )
        )

        if not personalizacao_atualizada:
            raise ValueError(
                "Não foi possível carregar a personalização da empresa."
            )

        return personalizacao_atualizada

    @classmethod
    def remover_favicon(cls) -> dict[str, Any]:
        empresa_id = cls._obter_empresa_id()

        personalizacao = (
            cls._garantir_personalizacao(
                empresa_id
            )
        )

        favicon_atual = personalizacao.get(
            "favicon"
        )

        EmpresaPersonalizacaoRepository.remover_favicon(
            empresa_id
        )

        cls._remover_arquivo_fisico(
            favicon_atual
        )

        personalizacao_atualizada = (
            EmpresaPersonalizacaoRepository.buscar_por_empresa(
                empresa_id
            )
        )

        if not personalizacao_atualizada:
            raise ValueError(
                "Não foi possível carregar a personalização da empresa."
            )

        return personalizacao_atualizada