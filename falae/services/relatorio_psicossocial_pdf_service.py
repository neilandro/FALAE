import html
from io import BytesIO
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from flask import current_app
from reportlab.lib import colors
from reportlab.lib.enums import (
    TA_CENTER,
    TA_JUSTIFY,
    TA_LEFT
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet
)
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    HRFlowable,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from falae.services.interpretacao_psicossocial_service import (
    InterpretacaoPsicossocialService
)
from falae.services.relatorio_psicossocial_service import (
    RelatorioPsicossocialService
)


class CanvasNumerado(canvas.Canvas):
    """Adiciona rodapé e numeração ao relatório."""

    def __init__(
        self,
        *args,
        empresa_nome: str = "",
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.empresa_nome = empresa_nome
        self._paginas = []

    def showPage(self):
        self._paginas.append(
            dict(self.__dict__)
        )

        self._startPage()

    def save(self):
        total_paginas = len(self._paginas)

        for estado in self._paginas:
            self.__dict__.update(estado)

            self._desenhar_rodape(
                total_paginas
            )

            super().showPage()

        super().save()

    def _desenhar_rodape(
        self,
        total_paginas: int
    ):
        largura, _ = A4

        margem = 1.5 * cm
        y_linha = 1.18 * cm
        y_texto = 0.76 * cm

        self.saveState()

        self.setStrokeColor(
            colors.HexColor("#D7DEE8")
        )

        self.setLineWidth(0.5)

        self.line(
            margem,
            y_linha,
            largura - margem,
            y_linha
        )

        self.setFillColor(
            colors.HexColor("#64748B")
        )

        self.setFont(
            "Helvetica",
            7
        )

        self.drawString(
            margem,
            y_texto,
            self.empresa_nome[:55]
        )

        texto_central = (
            "Confidencial • Gerado pelo FALAE"
        )

        largura_texto = stringWidth(
            texto_central,
            "Helvetica",
            7
        )

        self.drawString(
            (
                largura
                - largura_texto
            )
            / 2,
            y_texto,
            texto_central
        )

        self.drawRightString(
            largura - margem,
            y_texto,
            (
                f"Página {self._pageNumber} "
                f"de {total_paginas}"
            )
        )

        self.restoreState()


class CardIndicador(Flowable):
    """Card compacto para indicadores principais."""

    def __init__(
        self,
        titulo: str,
        valor: str,
        detalhe: str,
        cor: str,
        largura: float = 5.35 * cm,
        altura: float = 2.35 * cm
    ):
        super().__init__()

        self.titulo = titulo
        self.valor = valor
        self.detalhe = detalhe
        self.cor = colors.HexColor(cor)
        self.width = largura
        self.height = altura

    def draw(self):
        pdf = self.canv

        pdf.saveState()

        pdf.setFillColor(colors.white)
        pdf.setStrokeColor(
            colors.HexColor("#DCE3EC")
        )

        pdf.roundRect(
            0,
            0,
            self.width,
            self.height,
            8,
            fill=1,
            stroke=1
        )

        pdf.setFillColor(self.cor)

        pdf.roundRect(
            0,
            0,
            0.16 * cm,
            self.height,
            4,
            fill=1,
            stroke=0
        )

        pdf.setFillColor(
            colors.HexColor("#64748B")
        )

        pdf.setFont(
            "Helvetica-Bold",
            7.5
        )

        pdf.drawString(
            0.4 * cm,
            self.height - 0.55 * cm,
            self.titulo[:36]
        )

        pdf.setFillColor(
            colors.HexColor("#0F172A")
        )

        pdf.setFont(
            "Helvetica-Bold",
            19
        )

        pdf.drawString(
            0.4 * cm,
            self.height - 1.38 * cm,
            self.valor[:18]
        )

        pdf.setFillColor(
            colors.HexColor("#64748B")
        )

        pdf.setFont(
            "Helvetica",
            6.8
        )

        pdf.drawString(
            0.4 * cm,
            0.32 * cm,
            self.detalhe[:48]
        )

        pdf.restoreState()


class RelatorioPsicossocialPDFService:
    """
    Gera uma versão executiva e objetiva do:

    Relatório Técnico de Apoio à Gestão
    de Riscos Psicossociais.
    """

    TITULO = (
        "Relatório Técnico de Apoio à Gestão "
        "de Riscos Psicossociais"
    )

    SUBTITULO = (
        "Indicadores do Canal de Denúncias FALAE"
    )

    COR_PRIMARIA = "#1F4E78"
    COR_SECUNDARIA = "#163A5C"
    COR_TEXTO = "#1E293B"
    COR_TEXTO_SECUNDARIO = "#64748B"
    COR_BORDA = "#DCE3EC"
    COR_FUNDO = "#F8FAFC"

    @classmethod
    def gerar_relatorio(
        cls,
        filtros: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        dados = (
            RelatorioPsicossocialService
            .gerar_dados(
                filtros
            )
        )

        interpretacoes = (
            InterpretacaoPsicossocialService
            .gerar_interpretacoes(
                dados
            )
        )

        arquivo = cls.gerar_pdf(
            dados=dados,
            interpretacoes=interpretacoes
        )

        empresa = dados.get(
            "empresa",
            {}
        )

        return {
            "arquivo": arquivo,
            "nome_arquivo": cls._nome_arquivo(
                empresa.get("nome"),
                dados.get("data_emissao")
            ),
            "mimetype": "application/pdf"
        }

    @classmethod
    def gerar_pdf(
        cls,
        dados: dict[str, Any],
        interpretacoes: dict[str, Any]
    ) -> BytesIO:
        empresa = dados.get(
            "empresa",
            {}
        )

        empresa_nome = str(
            empresa.get("nome")
            or "Empresa não identificada"
        )

        arquivo = BytesIO()

        documento = BaseDocTemplate(
            arquivo,
            pagesize=A4,
            leftMargin=1.55 * cm,
            rightMargin=1.55 * cm,
            topMargin=1.4 * cm,
            bottomMargin=1.65 * cm,
            title=cls.TITULO,
            author="FALAE",
            creator="FALAE"
        )

        largura, altura = A4

        frame = Frame(
            documento.leftMargin,
            documento.bottomMargin,
            largura
            - documento.leftMargin
            - documento.rightMargin,
            altura
            - documento.topMargin
            - documento.bottomMargin,
            id="relatorio"
        )

        documento.addPageTemplates([
            PageTemplate(
                id="relatorio",
                frames=[frame]
            )
        ])

        estilos = cls._estilos(
            dados
        )

        elementos = []

        elementos.extend(
            cls._pagina_capa(
                dados,
                estilos
            )
        )

        elementos.extend(
            cls._pagina_resumo(
                dados,
                interpretacoes,
                estilos
            )
        )

        elementos.extend(
            cls._pagina_indicadores(
                dados,
                estilos
            )
        )

        elementos.extend(
            cls._pagina_recomendacoes(
                interpretacoes,
                estilos
            )
        )

        elementos.extend(
            cls._pagina_conclusao(
                dados,
                interpretacoes,
                estilos
            )
        )

        documento.build(
            elementos,
            canvasmaker=lambda *args, **kwargs: (
                CanvasNumerado(
                    *args,
                    empresa_nome=empresa_nome,
                    **kwargs
                )
            )
        )

        arquivo.seek(0)

        return arquivo

    @classmethod
    def _pagina_capa(
        cls,
        dados,
        estilos
    ):
        empresa = dados.get(
            "empresa",
            {}
        )

        periodo = dados.get(
            "periodo",
            {}
        )

        cor = cls._cor_primaria(
            dados
        )

        logo = cls._logo_empresa(
            empresa
        )

        conteudo = []

        if logo:
            conteudo.append([
                logo
            ])

        conteudo.extend([
            [
                Spacer(
                    1,
                    0.45 * cm
                )
            ],
            [
                Paragraph(
                    cls.TITULO,
                    estilos["capa_titulo"]
                )
            ],
            [
                Paragraph(
                    cls.SUBTITULO,
                    estilos["capa_subtitulo"]
                )
            ],
            [
                Spacer(
                    1,
                    1.1 * cm
                )
            ],
            [
                Paragraph(
                    cls._escapar(
                        empresa.get("nome")
                        or "Empresa não identificada"
                    ),
                    estilos["capa_empresa"]
                )
            ],
            [
                Paragraph(
                    (
                        "<b>Período:</b> "
                        + cls._escapar(
                            periodo.get(
                                "descricao",
                                "Todo o período disponível"
                            )
                        )
                    ),
                    estilos["capa_informacao"]
                )
            ],
            [
                Paragraph(
                    (
                        "<b>Emissão:</b> "
                        + cls._escapar(
                            dados.get(
                                "data_emissao_formatada",
                                ""
                            )
                        )
                    ),
                    estilos["capa_informacao"]
                )
            ],
            [
                Paragraph(
                    (
                        "<b>Metodologia:</b> Versão "
                        + cls._escapar(
                            dados.get(
                                "versao_metodologia",
                                "1.0"
                            )
                        )
                    ),
                    estilos["capa_informacao"]
                )
            ]
        ])

        capa = Table(
            conteudo,
            colWidths=[
                17.7 * cm
            ],
            rowHeights=[
                None
                for _ in conteudo
            ],
            style=TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(cor)
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    1 * cm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    1 * cm
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, 0),
                    1.2 * cm
                ),
                (
                    "BOTTOMPADDING",
                    (0, -1),
                    (-1, -1),
                    1.2 * cm
                )
            ])
        )

        return [
            Spacer(
                1,
                0.8 * cm
            ),
            capa,
            Spacer(
                1,
                0.85 * cm
            ),
            Paragraph(
                "Confidencial • Uso interno",
                estilos["destaque_central"]
            ),
            Spacer(
                1,
                0.25 * cm
            ),
            Paragraph(
                (
                    "Transformando registros em informações "
                    "para apoiar decisões."
                ),
                estilos["texto_central"]
            ),
            Spacer(
                1,
                1.2 * cm
            ),
            cls._caixa_nota(
                (
                    "Documento gerencial elaborado automaticamente "
                    "pelo FALAE. Não substitui avaliações técnicas, "
                    "laudos, diagnósticos ou o processo de "
                    "gerenciamento de riscos ocupacionais."
                ),
                estilos
            ),
            PageBreak()
        ]

    @classmethod
    def _pagina_resumo(
        cls,
        dados,
        interpretacoes,
        estilos
    ):
        indicadores = dados.get(
            "indicadores",
            {}
        )

        indice = dados.get(
            "indice_indicativo",
            {}
        )

        cards = Table(
            [[
                CardIndicador(
                    "Total de denúncias",
                    str(
                        cls._inteiro(
                            dados.get(
                                "total_denuncias"
                            )
                        )
                    ),
                    "Registros analisados",
                    cls.COR_PRIMARIA
                ),
                CardIndicador(
                    "Alta criticidade",
                    str(
                        cls._inteiro(
                            indicadores.get(
                                "criticas"
                            )
                        )
                    ),
                    cls._percentual(
                        indicadores.get(
                            "percentual_criticas"
                        )
                    ),
                    "#B91C1C"
                ),
                CardIndicador(
                    "Em aberto",
                    str(
                        cls._inteiro(
                            indicadores.get(
                                "em_aberto"
                            )
                        )
                    ),
                    cls._percentual(
                        indicadores.get(
                            "percentual_em_aberto"
                        )
                    ),
                    "#D97706"
                )
            ]],
            colWidths=[
                5.75 * cm,
                5.75 * cm,
                5.75 * cm
            ],
            style=TableStyle([
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                )
            ])
        )

        elementos = [
            Paragraph(
                "1. Resumo executivo",
                estilos["titulo"]
            ),
            cards,
            Spacer(
                1,
                0.35 * cm
            ),
            cls._caixa_indice(
                indice,
                estilos
            ),
            Spacer(
                1,
                0.4 * cm
            )
        ]

        resumo = interpretacoes.get(
            "resumo_executivo",
            []
        )

        # Limite intencional para manter o relatório objetivo.
        for texto in resumo[:5]:
            elementos.append(
                Paragraph(
                    cls._escapar(texto),
                    estilos["texto"]
                )
            )

        pontos = interpretacoes.get(
            "pontos_atencao",
            []
        )

        elementos.append(
            Paragraph(
                "Principais pontos de atenção",
                estilos["subtitulo"]
            )
        )

        if pontos:
            for ponto in pontos[:4]:
                elementos.append(
                    cls._item_destaque(
                        titulo=ponto.get(
                            "titulo",
                            ""
                        ),
                        descricao=ponto.get(
                            "descricao",
                            ""
                        ),
                        prioridade=ponto.get(
                            "prioridade",
                            "media"
                        ),
                        estilos=estilos
                    )
                )

        else:
            elementos.append(
                cls._caixa_nota(
                    (
                        "Não foram identificados pontos de atenção "
                        "automáticos para os filtros selecionados."
                    ),
                    estilos,
                    fundo="#ECFDF5",
                    borda="#86EFAC"
                )
            )

        elementos.append(
            PageBreak()
        )

        return elementos

    @classmethod
    def _pagina_indicadores(
        cls,
        dados,
        estilos
    ):
        indicadores = dados.get(
            "indicadores",
            {}
        )

        criticidades = (
            dados.get(
                "criticidades",
                {}
            ).get(
                "distribuicao",
                []
            )
        )

        categorias = dados.get(
            "categorias",
            []
        )

        grafico_criticidade = (
            cls._grafico_barras(
                criticidades,
                "criticidade",
                "total",
                "Distribuição por criticidade",
                limite=5
            )
        )

        grafico_categorias = (
            cls._grafico_barras(
                categorias,
                "categoria",
                "total",
                "Categorias mais frequentes",
                limite=6
            )
        )

        linhas = [
            [
                "Tempo médio de encerramento",
                (
                    f"{cls._numero(
                        indicadores.get(
                            'tempo_medio_encerramento_dias'
                        )
                    ):.1f} dias"
                )
            ],
            [
                "Denúncias abertas há mais de 7 dias",
                (
                    f"{cls._inteiro(
                        indicadores.get(
                            'abertas_mais_7_dias'
                        )
                    )} "
                    f"({cls._percentual(
                        indicadores.get(
                            'percentual_abertas_mais_7_dias'
                        )
                    )})"
                )
            ],
            [
                "Denúncias críticas em aberto",
                (
                    f"{cls._inteiro(
                        indicadores.get(
                            'criticas_em_aberto'
                        )
                    )} "
                    f"({cls._percentual(
                        indicadores.get(
                            'percentual_criticas_em_aberto'
                        )
                    )})"
                )
            ],
            [
                "Denúncias encerradas",
                (
                    f"{cls._inteiro(
                        indicadores.get(
                            'encerradas'
                        )
                    )} "
                    f"({cls._percentual(
                        indicadores.get(
                            'percentual_encerradas'
                        )
                    )})"
                )
            ]
        ]

        return [
            Paragraph(
                "2. Indicadores",
                estilos["titulo"]
            ),
            Table(
                [[
                    grafico_criticidade,
                    grafico_categorias
                ]],
                colWidths=[
                    8.7 * cm,
                    8.7 * cm
                ],
                style=TableStyle([
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        0
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    )
                ])
            ),
            Spacer(
                1,
                0.35 * cm
            ),
            cls._tabela_simples(
                [
                    "Indicador",
                    "Resultado"
                ],
                linhas,
                [
                    11.5 * cm,
                    6 * cm
                ],
                estilos
            ),
            Spacer(
                1,
                0.35 * cm
            ),
            cls._caixa_nota(
                (
                    "Os percentuais representam a participação "
                    "de cada grupo sobre o total de denúncias "
                    "incluídas nos filtros selecionados."
                ),
                estilos
            ),
            PageBreak()
        ]

    @classmethod
    def _pagina_recomendacoes(
        cls,
        interpretacoes,
        estilos
    ):
        recomendacoes = interpretacoes.get(
            "recomendacoes",
            []
        )

        planos = interpretacoes.get(
            "plano_acao_sugerido",
            []
        )

        elementos = [
            Paragraph(
                "3. Recomendações e plano de ação",
                estilos["titulo"]
            )
        ]

        for recomendacao in recomendacoes[:5]:
            elementos.append(
                cls._item_destaque(
                    titulo=recomendacao.get(
                        "titulo",
                        ""
                    ),
                    descricao=recomendacao.get(
                        "descricao",
                        ""
                    ),
                    prioridade=recomendacao.get(
                        "prioridade",
                        "baixa"
                    ),
                    estilos=estilos
                )
            )

        elementos.extend([
            Spacer(
                1,
                0.25 * cm
            ),
            Paragraph(
                "Plano de ação sugerido",
                estilos["subtitulo"]
            )
        ])

        linhas = []

        for plano in planos[:6]:
            linhas.append([
                plano.get(
                    "prioridade",
                    ""
                ),
                plano.get(
                    "acao",
                    ""
                ),
                plano.get(
                    "responsavel_sugerido",
                    ""
                ),
                plano.get(
                    "prazo_sugerido",
                    ""
                )
            ])

        elementos.append(
            cls._tabela_simples(
                [
                    "Prioridade",
                    "Ação sugerida",
                    "Responsável",
                    "Prazo"
                ],
                linhas,
                [
                    2.2 * cm,
                    7 * cm,
                    5.2 * cm,
                    3.1 * cm
                ],
                estilos,
                fonte=6.8
            )
        )

        elementos.extend([
            Spacer(
                1,
                0.35 * cm
            ),
            Paragraph(
                (
                    "As ações apresentadas são sugestões iniciais. "
                    "A organização deve validar responsáveis, prazos, "
                    "recursos e aplicabilidade antes da execução."
                ),
                estilos["nota"]
            ),
            PageBreak()
        ])

        return elementos

    @classmethod
    def _pagina_conclusao(
        cls,
        dados,
        interpretacoes,
        estilos
    ):
        elementos = [
            Paragraph(
                "4. Como interpretar e próximos passos",
                estilos["titulo"]
            ),
            Paragraph(
                "Como os números foram calculados",
                estilos["subtitulo"]
            ),
            cls._tabela_simples(
                [
                    "Indicador",
                    "Cálculo"
                ],
                [
                    [
                        "Percentuais",
                        (
                            "Quantidade do grupo ÷ total "
                            "de denúncias × 100."
                        )
                    ],
                    [
                        "Gravidade",
                        (
                            "Alta = 3 pontos, Média = 2 "
                            "e Baixa = 1."
                        )
                    ],
                    [
                        "Tendência",
                        (
                            "Comparação entre os dois últimos "
                            "meses disponíveis."
                        )
                    ],
                    [
                        "Índice indicativo",
                        (
                            "Combina gravidade, casos críticos "
                            "abertos, tempo e concentração."
                        )
                    ]
                ],
                [
                    5.2 * cm,
                    12.3 * cm
                ],
                estilos
            ),
            Spacer(
                1,
                0.35 * cm
            ),
            Paragraph(
                "Conclusão",
                estilos["subtitulo"]
            )
        ]

        for texto in interpretacoes.get(
            "conclusao",
            []
        )[:4]:
            elementos.append(
                Paragraph(
                    cls._escapar(texto),
                    estilos["texto"]
                )
            )

        elementos.extend([
            Spacer(
                1,
                0.25 * cm
            ),
            cls._caixa_nota(
                (
                    "Poucas denúncias não significam ausência de "
                    "riscos. Um aumento de registros também pode "
                    "indicar maior conhecimento e confiança no canal."
                ),
                estilos,
                fundo="#FFF7ED",
                borda="#FDBA74"
            ),
            Spacer(
                1,
                0.45 * cm
            ),
            Paragraph(
                "Responsabilidade técnica",
                estilos["subtitulo"]
            ),
            Paragraph(
                (
                    "O presente relatório constitui instrumento "
                    "gerencial de apoio. Sua interpretação deve ser "
                    "integrada a outras evidências organizacionais "
                    "e conduzida pelos profissionais responsáveis "
                    "pelo SESMT, RH, Compliance e PGR."
                ),
                estilos["texto"]
            ),
            Spacer(
                1,
                0.9 * cm
            ),
            HRFlowable(
                width=8 * cm,
                thickness=0.7,
                color=colors.HexColor(
                    cls.COR_TEXTO_SECUNDARIO
                ),
                hAlign="LEFT"
            ),
            Paragraph(
                (
                    "Responsável pela análise técnica • "
                    "Nome, cargo e registro profissional"
                ),
                estilos["nota"]
            ),
            Spacer(
                1,
                0.65 * cm
            ),
            Paragraph(
                (
                    "<b>FALAE</b><br/>"
                    "Transformando denúncias em decisões."
                ),
                estilos["destaque_central"]
            )
        ])

        return elementos

    @classmethod
    def _estilos(
        cls,
        dados
    ):
        base = getSampleStyleSheet()

        cor = cls._cor_primaria(
            dados
        )

        return {
            "capa_titulo": ParagraphStyle(
                "CapaTitulo",
                parent=base["Title"],
                fontName="Helvetica-Bold",
                fontSize=23,
                leading=28,
                textColor=colors.white,
                alignment=TA_CENTER,
                spaceAfter=12
            ),
            "capa_subtitulo": ParagraphStyle(
                "CapaSubtitulo",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=11,
                leading=15,
                textColor=colors.HexColor(
                    "#E8EEF5"
                ),
                alignment=TA_CENTER
            ),
            "capa_empresa": ParagraphStyle(
                "CapaEmpresa",
                parent=base["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=17,
                leading=21,
                textColor=colors.white,
                alignment=TA_CENTER,
                spaceAfter=8
            ),
            "capa_informacao": ParagraphStyle(
                "CapaInformacao",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=14,
                textColor=colors.white,
                alignment=TA_CENTER
            ),
            "titulo": ParagraphStyle(
                "Titulo",
                parent=base["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=16,
                leading=20,
                textColor=colors.HexColor(cor),
                spaceAfter=10
            ),
            "subtitulo": ParagraphStyle(
                "Subtitulo",
                parent=base["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=14,
                textColor=colors.HexColor(
                    cls.COR_TEXTO
                ),
                spaceBefore=5,
                spaceAfter=7
            ),
            "texto": ParagraphStyle(
                "Texto",
                parent=base["BodyText"],
                fontName="Helvetica",
                fontSize=8.8,
                leading=13.2,
                textColor=colors.HexColor(
                    cls.COR_TEXTO
                ),
                alignment=TA_JUSTIFY,
                spaceAfter=6
            ),
            "nota": ParagraphStyle(
                "Nota",
                parent=base["BodyText"],
                fontName="Helvetica-Oblique",
                fontSize=7.5,
                leading=10.5,
                textColor=colors.HexColor(
                    cls.COR_TEXTO_SECUNDARIO
                ),
                alignment=TA_JUSTIFY
            ),
            "tabela": ParagraphStyle(
                "Tabela",
                parent=base["BodyText"],
                fontName="Helvetica",
                fontSize=7.2,
                leading=9,
                textColor=colors.HexColor(
                    cls.COR_TEXTO
                )
            ),
            "tabela_header": ParagraphStyle(
                "TabelaHeader",
                parent=base["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=7,
                leading=9,
                textColor=colors.white,
                alignment=TA_CENTER
            ),
            "destaque_central": ParagraphStyle(
                "DestaqueCentral",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=14,
                textColor=colors.HexColor(cor),
                alignment=TA_CENTER
            ),
            "texto_central": ParagraphStyle(
                "TextoCentral",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=13,
                textColor=colors.HexColor(
                    cls.COR_TEXTO
                ),
                alignment=TA_CENTER
            )
        }

    @classmethod
    def _caixa_indice(
        cls,
        indice,
        estilos
    ):
        valor = cls._numero(
            indice.get("valor")
        )

        nivel = cls._escapar(
            indice.get(
                "nivel",
                "Não classificado"
            )
        )

        cor = cls._cor_indice(
            valor
        )

        return Table(
            [[
                Paragraph(
                    (
                        "<b>Índice Indicativo</b><br/>"
                        f"<font size='24'>{valor:.2f}</font>"
                    ),
                    ParagraphStyle(
                        "IndiceValor",
                        parent=estilos["texto"],
                        textColor=colors.white,
                        alignment=TA_CENTER,
                        leading=27
                    )
                ),
                Paragraph(
                    (
                        "<b>Nível de atenção</b><br/>"
                        f"<font size='17'>{nivel}</font>"
                    ),
                    ParagraphStyle(
                        "IndiceNivel",
                        parent=estilos["texto"],
                        textColor=colors.white,
                        alignment=TA_CENTER,
                        leading=21
                    )
                )
            ]],
            colWidths=[
                8.85 * cm,
                8.85 * cm
            ],
            rowHeights=[
                2.6 * cm
            ],
            style=TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(cor)
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.white
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                )
            ])
        )

    @classmethod
    def _item_destaque(
        cls,
        titulo,
        descricao,
        prioridade,
        estilos
    ):
        prioridade = str(
            prioridade or ""
        ).lower()

        if prioridade == "alta":
            fundo = "#FEF2F2"
            borda = "#FCA5A5"

        elif prioridade == "media":
            fundo = "#FFF7ED"
            borda = "#FDBA74"

        else:
            fundo = "#F0FDF4"
            borda = "#86EFAC"

        return Table(
            [[
                Paragraph(
                    (
                        "<b>"
                        + cls._escapar(titulo)
                        + "</b><br/>"
                        + cls._escapar(descricao)
                    ),
                    estilos["texto"]
                )
            ]],
            colWidths=[
                17.7 * cm
            ],
            style=TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(fundo)
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor(borda)
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ]),
            spaceAfter=5
        )

    @classmethod
    def _caixa_nota(
        cls,
        texto,
        estilos,
        fundo="#EFF6FF",
        borda="#93C5FD"
    ):
        return Table(
            [[
                Paragraph(
                    cls._escapar(texto),
                    estilos["nota"]
                )
            ]],
            colWidths=[
                17.7 * cm
            ],
            style=TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(fundo)
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor(borda)
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ])
        )

    @classmethod
    def _tabela_simples(
        cls,
        headers,
        linhas,
        larguras,
        estilos,
        fonte=7.2
    ):
        estilo_celula = ParagraphStyle(
            "Celula",
            parent=estilos["tabela"],
            fontSize=fonte,
            leading=fonte + 2
        )

        dados = [[
            Paragraph(
                cls._escapar(header),
                estilos["tabela_header"]
            )
            for header in headers
        ]]

        if linhas:
            for linha in linhas:
                dados.append([
                    Paragraph(
                        cls._escapar(valor),
                        estilo_celula
                    )
                    for valor in linha
                ])

        else:
            dados.append([
                Paragraph(
                    "Nenhuma informação disponível.",
                    estilo_celula
                )
            ] + [
                Paragraph(
                    "",
                    estilo_celula
                )
                for _ in headers[1:]
            ])

        tabela = Table(
            dados,
            colWidths=larguras,
            repeatRows=1
        )

        estilo = [
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(
                    cls.COR_PRIMARIA
                )
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor(
                    cls.COR_BORDA
                )
            ),
            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.25,
                colors.HexColor(
                    cls.COR_BORDA
                )
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ]

        for indice in range(
            1,
            len(dados)
        ):
            if indice % 2 == 0:
                estilo.append((
                    "BACKGROUND",
                    (0, indice),
                    (-1, indice),
                    colors.HexColor(
                        cls.COR_FUNDO
                    )
                ))

        tabela.setStyle(
            TableStyle(estilo)
        )

        return tabela

    @classmethod
    def _grafico_barras(
        cls,
        itens,
        campo_rotulo,
        campo_valor,
        titulo,
        limite=6
    ):
        if not itens:
            return cls._grafico_sem_dados(
                titulo
            )

        selecionados = sorted(
            itens,
            key=lambda item: cls._numero(
                item.get(campo_valor)
            ),
            reverse=True
        )[:limite]

        selecionados.reverse()

        rotulos = [
            str(
                item.get(campo_rotulo)
                or "Não informado"
            )[:28]
            for item in selecionados
        ]

        valores = [
            cls._numero(
                item.get(campo_valor)
            )
            for item in selecionados
        ]

        figura, eixo = plt.subplots(
            figsize=(4.2, 3.25)
        )

        eixo.barh(
            rotulos,
            valores,
            color=cls.COR_PRIMARIA
        )

        eixo.set_title(
            titulo,
            fontsize=10,
            fontweight="bold",
            pad=8
        )

        eixo.tick_params(
            axis="both",
            labelsize=7
        )

        eixo.grid(
            axis="x",
            linestyle="--",
            alpha=0.22
        )

        eixo.spines["top"].set_visible(False)
        eixo.spines["right"].set_visible(False)

        for indice, valor in enumerate(
            valores
        ):
            eixo.text(
                valor,
                indice,
                f" {int(valor)}",
                va="center",
                fontsize=7
            )

        figura.tight_layout()

        imagem_memoria = BytesIO()

        figura.savefig(
            imagem_memoria,
            format="png",
            dpi=145,
            bbox_inches="tight",
            facecolor="white"
        )

        plt.close(figura)

        imagem_memoria.seek(0)

        imagem = Image(
            imagem_memoria,
            width=8.35 * cm,
            height=6.4 * cm
        )

        imagem._arquivo_memoria = (
            imagem_memoria
        )

        return imagem

    @classmethod
    def _grafico_sem_dados(
        cls,
        titulo
    ):
        return Table(
            [[
                Paragraph(
                    (
                        f"<b>{cls._escapar(titulo)}</b><br/>"
                        "Nenhum dado disponível."
                    ),
                    ParagraphStyle(
                        "SemDados",
                        fontName="Helvetica",
                        fontSize=8,
                        leading=12,
                        alignment=TA_CENTER,
                        textColor=colors.HexColor(
                            cls.COR_TEXTO_SECUNDARIO
                        )
                    )
                )
            ]],
            colWidths=[
                8.35 * cm
            ],
            rowHeights=[
                6.4 * cm
            ],
            style=TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(
                        cls.COR_FUNDO
                    )
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        cls.COR_BORDA
                    )
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                )
            ])
        )

    @classmethod
    def _logo_empresa(
        cls,
        empresa
    ):
        caminho = empresa.get("logo")

        if not caminho:
            return None

        try:
            static = Path(
                current_app.static_folder
            ).resolve()

            arquivo = (
                static
                / str(caminho)
            ).resolve()

            arquivo.relative_to(static)

            if not arquivo.is_file():
                return None

            return Image(
                str(arquivo),
                width=4 * cm,
                height=2.1 * cm,
                kind="proportional"
            )

        except Exception:
            return None

    @classmethod
    def _cor_primaria(
        cls,
        dados
    ):
        personalizacao = dados.get(
            "personalizacao",
            {}
        )

        cor = str(
            personalizacao.get(
                "cor_primaria"
            )
            or cls.COR_PRIMARIA
        ).strip().upper()

        if (
            len(cor) == 7
            and cor.startswith("#")
        ):
            try:
                int(cor[1:], 16)

                return cor

            except ValueError:
                pass

        return cls.COR_PRIMARIA

    @staticmethod
    def _cor_indice(
        valor
    ):
        if valor >= 85:
            return "#991B1B"

        if valor >= 70:
            return "#C2410C"

        if valor >= 50:
            return "#CA8A04"

        if valor >= 25:
            return "#0369A1"

        return "#15803D"

    @staticmethod
    def _numero(
        valor
    ):
        try:
            return float(valor or 0)

        except (
            TypeError,
            ValueError
        ):
            return 0.0

    @classmethod
    def _inteiro(
        cls,
        valor
    ):
        return int(
            cls._numero(valor)
        )

    @classmethod
    def _percentual(
        cls,
        valor
    ):
        return (
            f"{cls._numero(valor):.2f}"
            .replace(".", ",")
            + "%"
        )

    @staticmethod
    def _escapar(
        valor
    ):
        return html.escape(
            str(valor or "")
        ).replace(
            "\n",
            "<br/>"
        )

    @staticmethod
    def _nome_arquivo(
        empresa_nome,
        data_emissao
    ):
        nome = str(
            empresa_nome
            or "empresa"
        ).lower()

        partes = []

        for caractere in nome:
            if caractere.isalnum():
                partes.append(caractere)

            elif caractere in (
                " ",
                "-",
                "_"
            ):
                partes.append("-")

        nome = "".join(partes)

        while "--" in nome:
            nome = nome.replace(
                "--",
                "-"
            )

        nome = nome.strip("-") or "empresa"

        competencia = (
            data_emissao.strftime("%Y%m%d")
            if hasattr(
                data_emissao,
                "strftime"
            )
            else "relatorio"
        )

        return (
            "relatorio-tecnico-riscos-psicossociais-"
            f"{nome}-{competencia}.pdf"
        )