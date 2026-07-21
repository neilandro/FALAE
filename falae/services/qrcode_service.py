import re
from io import BytesIO
from typing import Any

import qrcode
from PIL import Image
from qrcode.constants import ERROR_CORRECT_H


class QRCodeService:
    """Geração de QR Codes do portal público do FALAE."""

    COR_PADRAO = "#1F4E78"
    COR_FUNDO = "#FFFFFF"

    TAMANHO_CAIXA = 12
    TAMANHO_BORDA = 4

    @staticmethod
    def _normalizar_texto(
        valor: str | None
    ) -> str:
        return (
            valor or ""
        ).strip()

    @classmethod
    def _validar_link(
        cls,
        link: str | None
    ) -> str:
        link_normalizado = cls._normalizar_texto(
            link
        )

        if not link_normalizado:
            raise ValueError(
                "O link público do canal não foi informado."
            )

        if not link_normalizado.startswith(
            ("http://", "https://")
        ):
            raise ValueError(
                "O link público do canal é inválido."
            )

        if len(link_normalizado) > 2000:
            raise ValueError(
                "O link público do canal ultrapassa "
                "o tamanho permitido."
            )

        return link_normalizado

    @classmethod
    def _normalizar_cor(
        cls,
        cor: str | None
    ) -> str:
        cor_normalizada = (
            cor or cls.COR_PADRAO
        ).strip().upper()

        if not re.fullmatch(
            r"#[0-9A-F]{6}",
            cor_normalizada
        ):
            return cls.COR_PADRAO

        return cor_normalizada

    @classmethod
    def gerar_imagem(
        cls,
        link: str,
        cor_primaria: str | None = None
    ) -> Image.Image:
        link_validado = cls._validar_link(
            link
        )

        cor_validada = cls._normalizar_cor(
            cor_primaria
        )

        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_H,
            box_size=cls.TAMANHO_CAIXA,
            border=cls.TAMANHO_BORDA
        )

        qr.add_data(
            link_validado
        )

        qr.make(
            fit=True
        )

        imagem = qr.make_image(
            fill_color=cor_validada,
            back_color=cls.COR_FUNDO
        )

        return imagem.convert(
            "RGB"
        )

    @classmethod
    def gerar_png(
        cls,
        link: str,
        cor_primaria: str | None = None
    ) -> BytesIO:
        imagem = cls.gerar_imagem(
            link=link,
            cor_primaria=cor_primaria
        )

        arquivo = BytesIO()

        imagem.save(
            arquivo,
            format="PNG",
            optimize=True
        )

        arquivo.seek(0)

        return arquivo

    @classmethod
    def gerar_nome_arquivo(
        cls,
        slug: str | None
    ) -> str:
        slug_normalizado = (
            slug or "canal"
        ).strip().lower()

        slug_normalizado = re.sub(
            r"[^a-z0-9-]+",
            "-",
            slug_normalizado
        )

        slug_normalizado = re.sub(
            r"-+",
            "-",
            slug_normalizado
        ).strip("-")

        if not slug_normalizado:
            slug_normalizado = "canal"

        return (
            f"qrcode-canal-{slug_normalizado}.png"
        )

    @classmethod
    def gerar_dados(
        cls,
        link: str,
        slug: str | None,
        cor_primaria: str | None = None
    ) -> dict[str, Any]:
        return {
            "arquivo": cls.gerar_png(
                link=link,
                cor_primaria=cor_primaria
            ),
            "nome_arquivo": cls.gerar_nome_arquivo(
                slug
            ),
            "mimetype": "image/png"
        }