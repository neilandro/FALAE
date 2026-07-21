import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

from falae.repositories.anexo_repository import AnexoRepository


class AnexoService:

    EXTENSOES_PERMITIDAS = {
        "jpg",
        "jpeg",
        "png",
        "pdf",
        "doc",
        "docx"
    }

    TAMANHO_MAXIMO = 5 * 1024 * 1024
    MAXIMO_ANEXOS = 3

    @staticmethod
    def extensao_permitida(nome_arquivo):
        return (
            "." in nome_arquivo
            and nome_arquivo.rsplit(".", 1)[1].lower()
            in AnexoService.EXTENSOES_PERMITIDAS
        )

    @staticmethod
    def salvar_anexos(arquivos, denuncia_id, empresa_id):
        if not arquivos:
            return

        arquivos_validos = [
            arquivo for arquivo in arquivos
            if arquivo and arquivo.filename
        ]

        if not arquivos_validos:
            return

        if len(arquivos_validos) > AnexoService.MAXIMO_ANEXOS:
            raise Exception("É permitido enviar no máximo 3 anexos.")

        repo = AnexoRepository()

        try:
            total = repo.contar_por_denuncia(denuncia_id)

            if total + len(arquivos_validos) > AnexoService.MAXIMO_ANEXOS:
                raise Exception("Limite máximo de 3 anexos por denúncia atingido.")

            pasta = os.path.abspath(os.path.join(
                current_app.root_path,
                "..",
                "uploads",
                f"empresa_{empresa_id}",
                f"denuncia_{denuncia_id}"
            ))

            os.makedirs(pasta, exist_ok=True)

            for arquivo in arquivos_validos:
                if not AnexoService.extensao_permitida(arquivo.filename):
                    raise Exception(f"Arquivo não permitido: {arquivo.filename}")

                arquivo.seek(0, os.SEEK_END)
                tamanho = arquivo.tell()
                arquivo.seek(0)

                if tamanho > AnexoService.TAMANHO_MAXIMO:
                    raise Exception(f"{arquivo.filename} excede o limite de 5MB.")

                extensao = arquivo.filename.rsplit(".", 1)[1].lower()
                nome_fisico = f"{uuid.uuid4()}.{extensao}"
                caminho = os.path.join(pasta, nome_fisico)

                arquivo.save(caminho)

                repo.salvar(
                    denuncia_id=denuncia_id,
                    empresa_id=empresa_id,
                    nome_original=secure_filename(arquivo.filename),
                    nome_fisico=nome_fisico,
                    caminho=caminho,
                    mime_type=arquivo.mimetype,
                    tamanho=tamanho
                )

        finally:
            repo.close()