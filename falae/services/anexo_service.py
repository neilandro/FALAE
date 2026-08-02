import os
import uuid
import zipfile

from flask import current_app
from werkzeug.utils import secure_filename

from falae.repositories.anexo_repository import (
    AnexoRepository
)


class AnexoService:

    EXTENSOES_PERMITIDAS = {
        "jpg",
        "jpeg",
        "png",
        "pdf",
        "doc",
        "docx"
    }

    MIME_TYPES_PERMITIDOS = {
        "jpg": {
            "image/jpeg"
        },
        "jpeg": {
            "image/jpeg"
        },
        "png": {
            "image/png"
        },
        "pdf": {
            "application/pdf"
        },
        "doc": {
            "application/msword",
            "application/octet-stream"
        },
        "docx": {
            (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            "application/zip",
            "application/octet-stream"
        }
    }

    TAMANHO_MAXIMO = 5 * 1024 * 1024
    MAXIMO_ANEXOS = 3

    @staticmethod
    def _obter_extensao(
        nome_arquivo
    ):
        nome = str(
            nome_arquivo or ""
        ).strip()

        if "." not in nome:
            return ""

        return (
            nome
            .rsplit(".", 1)[1]
            .strip()
            .lower()
        )

    @staticmethod
    def extensao_permitida(
        nome_arquivo
    ):
        extensao = (
            AnexoService._obter_extensao(
                nome_arquivo
            )
        )

        return (
            extensao
            in AnexoService.EXTENSOES_PERMITIDAS
        )

    @staticmethod
    def _obter_tamanho(
        arquivo
    ):
        posicao_original = arquivo.stream.tell()

        arquivo.stream.seek(
            0,
            os.SEEK_END
        )

        tamanho = arquivo.stream.tell()

        arquivo.stream.seek(
            posicao_original
        )

        return tamanho

    @staticmethod
    def _ler_inicio(
        arquivo,
        quantidade=16
    ):
        posicao_original = arquivo.stream.tell()

        arquivo.stream.seek(0)

        conteudo = arquivo.stream.read(
            quantidade
        )

        arquivo.stream.seek(
            posicao_original
        )

        return conteudo

    @staticmethod
    def _arquivo_docx_valido(
        arquivo
    ):
        posicao_original = arquivo.stream.tell()

        try:
            arquivo.stream.seek(0)

            with zipfile.ZipFile(
                arquivo.stream
            ) as documento:
                nomes = set(
                    documento.namelist()
                )

                return (
                    "[Content_Types].xml"
                    in nomes
                    and "word/document.xml"
                    in nomes
                )

        except (
            zipfile.BadZipFile,
            OSError,
            ValueError
        ):
            return False

        finally:
            arquivo.stream.seek(
                posicao_original
            )

    @staticmethod
    def _assinatura_valida(
        arquivo,
        extensao
    ):
        inicio = AnexoService._ler_inicio(
            arquivo,
            quantidade=16
        )

        if extensao in {
            "jpg",
            "jpeg"
        }:
            return inicio.startswith(
                b"\xFF\xD8\xFF"
            )

        if extensao == "png":
            return inicio.startswith(
                b"\x89PNG\r\n\x1a\n"
            )

        if extensao == "pdf":
            return inicio.startswith(
                b"%PDF-"
            )

        if extensao == "doc":
            return inicio.startswith(
                b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"
            )

        if extensao == "docx":
            return (
                AnexoService._arquivo_docx_valido(
                    arquivo
                )
            )

        return False

    @staticmethod
    def _mime_type_valido(
        arquivo,
        extensao
    ):
        mime_type = (
            str(
                arquivo.mimetype or ""
            )
            .strip()
            .lower()
        )

        permitidos = (
            AnexoService
            .MIME_TYPES_PERMITIDOS
            .get(
                extensao,
                set()
            )
        )

        return mime_type in permitidos

    @staticmethod
    def _validar_arquivo(
        arquivo
    ):
        nome_original = str(
            arquivo.filename or ""
        ).strip()

        if not nome_original:
            raise ValueError(
                "Foi enviado um arquivo sem nome."
            )

        nome_seguro = secure_filename(
            nome_original
        )

        if not nome_seguro:
            raise ValueError(
                "O nome do arquivo enviado é inválido."
            )

        extensao = (
            AnexoService._obter_extensao(
                nome_seguro
            )
        )

        if (
            extensao
            not in AnexoService.EXTENSOES_PERMITIDAS
        ):
            raise ValueError(
                f"Arquivo não permitido: {nome_original}"
            )

        tamanho = (
            AnexoService._obter_tamanho(
                arquivo
            )
        )

        if tamanho <= 0:
            raise ValueError(
                f"O arquivo {nome_original} está vazio."
            )

        if (
            tamanho
            > AnexoService.TAMANHO_MAXIMO
        ):
            raise ValueError(
                f"{nome_original} excede "
                "o limite de 5 MB."
            )

        if not AnexoService._mime_type_valido(
            arquivo,
            extensao
        ):
            raise ValueError(
                f"O tipo declarado do arquivo "
                f"{nome_original} não é permitido."
            )

        if not AnexoService._assinatura_valida(
            arquivo,
            extensao
        ):
            raise ValueError(
                f"O conteúdo do arquivo "
                f"{nome_original} não corresponde "
                "ao formato informado."
            )

        arquivo.stream.seek(0)

        return {
            "arquivo": arquivo,
            "nome_original": nome_seguro,
            "extensao": extensao,
            "mime_type": (
                str(
                    arquivo.mimetype
                    or "application/octet-stream"
                )
                .strip()
                .lower()
            ),
            "tamanho": tamanho
        }

    @staticmethod
    def _obter_pasta_destino(
        empresa_id,
        denuncia_id
    ):
        pasta_upload = os.path.abspath(
            current_app.config[
                "UPLOAD_FOLDER"
            ]
        )

        pasta_destino = os.path.abspath(
            os.path.join(
                pasta_upload,
                f"empresa_{int(empresa_id)}",
                f"denuncia_{int(denuncia_id)}"
            )
        )

        try:
            caminho_comum = os.path.commonpath(
                [
                    pasta_upload,
                    pasta_destino
                ]
            )
        except ValueError as erro:
            raise ValueError(
                "O caminho de armazenamento "
                "dos anexos é inválido."
            ) from erro

        if caminho_comum != pasta_upload:
            raise ValueError(
                "O caminho de armazenamento "
                "dos anexos não é permitido."
            )

        os.makedirs(
            pasta_destino,
            exist_ok=True
        )

        return pasta_destino

    @staticmethod
    def _remover_arquivos(
        caminhos
    ):
        for caminho in caminhos:
            try:
                if (
                    caminho
                    and os.path.isfile(caminho)
                ):
                    os.remove(caminho)

            except OSError:
                current_app.logger.exception(
                    (
                        "ANEXO_LIMPEZA_ARQUIVO_FALHOU | "
                        "CAMINHO=%s"
                    ),
                    caminho
                )

    @staticmethod
    def validar_anexos(
        arquivos
    ):
        if not arquivos:
            return []

        arquivos_recebidos = [
            arquivo
            for arquivo in arquivos
            if (
                arquivo
                and arquivo.filename
            )
        ]

        if not arquivos_recebidos:
            return []

        if (
            len(arquivos_recebidos)
            > AnexoService.MAXIMO_ANEXOS
        ):
            raise ValueError(
                "É permitido enviar no máximo "
                "3 anexos."
            )

        arquivos_validados = [
            AnexoService._validar_arquivo(
                arquivo
            )
            for arquivo in arquivos_recebidos
        ]

        for dados_arquivo in arquivos_validados:
            dados_arquivo["arquivo"].stream.seek(0)

        return arquivos_validados

    @staticmethod
    def salvar_anexos(
        arquivos,
        denuncia_id,
        empresa_id,
        arquivos_validados=None
    ):
        if arquivos_validados is None:
            arquivos_validados = (
                AnexoService.validar_anexos(
                    arquivos
                )
            )

        if not arquivos_validados:
            return []

        repository = AnexoRepository()

        anexos_criados = []
        caminhos_criados = []

        try:
            if not repository.denuncia_pertence_empresa(
                denuncia_id=denuncia_id,
                empresa_id=empresa_id
            ):
                raise ValueError(
                    "A denúncia informada não pertence "
                    "à empresa atual."
                )

            total_existente = (
                repository.contar_por_denuncia(
                    denuncia_id=denuncia_id,
                    empresa_id=empresa_id
                )
            )

            if (
                total_existente
                + len(arquivos_validados)
                > AnexoService.MAXIMO_ANEXOS
            ):
                raise ValueError(
                    "Limite máximo de 3 anexos "
                    "por denúncia atingido."
                )

            pasta_destino = (
                AnexoService._obter_pasta_destino(
                    empresa_id=empresa_id,
                    denuncia_id=denuncia_id
                )
            )

            for dados_arquivo in arquivos_validados:
                arquivo = dados_arquivo[
                    "arquivo"
                ]

                extensao = dados_arquivo[
                    "extensao"
                ]

                nome_fisico = (
                    f"{uuid.uuid4().hex}."
                    f"{extensao}"
                )

                caminho = os.path.abspath(
                    os.path.join(
                        pasta_destino,
                        nome_fisico
                    )
                )

                if (
                    os.path.commonpath(
                        [
                            pasta_destino,
                            caminho
                        ]
                    )
                    != pasta_destino
                ):
                    raise ValueError(
                        "O caminho final do anexo "
                        "é inválido."
                    )

                arquivo.stream.seek(0)

                arquivo.save(
                    caminho
                )

                caminhos_criados.append(
                    caminho
                )

                anexo_id = repository.salvar(
                    denuncia_id=denuncia_id,
                    empresa_id=empresa_id,
                    nome_original=(
                        dados_arquivo[
                            "nome_original"
                        ]
                    ),
                    nome_fisico=nome_fisico,
                    caminho=caminho,
                    mime_type=(
                        dados_arquivo[
                            "mime_type"
                        ]
                    ),
                    tamanho=(
                        dados_arquivo[
                            "tamanho"
                        ]
                    )
                )

                anexos_criados.append(
                    anexo_id
                )

            current_app.logger.info(
                (
                    "ANEXOS_SALVOS | "
                    "EMPRESA=%s | "
                    "DENUNCIA=%s | "
                    "TOTAL=%s"
                ),
                empresa_id,
                denuncia_id,
                len(anexos_criados)
            )

            return anexos_criados

        except Exception:
            AnexoService._remover_arquivos(
                caminhos_criados
            )

            if anexos_criados:
                try:
                    repository.excluir_varios(
                        anexo_ids=anexos_criados,
                        empresa_id=empresa_id
                    )

                except Exception:
                    current_app.logger.exception(
                        (
                            "ANEXO_LIMPEZA_BANCO_FALHOU | "
                            "EMPRESA=%s | "
                            "DENUNCIA=%s"
                        ),
                        empresa_id,
                        denuncia_id
                    )

            raise

        finally:
            repository.close()