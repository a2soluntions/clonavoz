import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_FILENAME = "Relatorio_Viabilidade_VoxStudio_SaaS.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(2 * cm, 28.5 * cm, "VoxStudio AI • Relatório Executivo de Viabilidade & Negócios")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(2 * cm, 28.3 * cm, 19 * cm, 28.3 * cm)

        # Footer
        footer_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(19 * cm, 1.2 * cm, footer_text)
        self.drawString(2 * cm, 1.2 * cm, "Auditoria Financeira & Plano de Negócios • Confidencial")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(2 * cm, 1.5 * cm, 19 * cm, 1.5 * cm)
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_FILENAME,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    primary_color = colors.HexColor("#0F172A")
    brand_blue = colors.HexColor("#2563EB")
    text_dark = colors.HexColor("#1E293B")
    accent_emerald = colors.HexColor("#059669")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=6,
    )
    
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=14,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=brand_blue,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=text_dark,
        spaceAfter=5,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=12,
        bulletIndent=4,
        spaceAfter=3,
    )

    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E3A8A"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=text_dark,
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell_style,
        fontName="Helvetica-Bold",
    )

    table_cell_green = ParagraphStyle(
        "TableCellGreen",
        parent=table_cell_style,
        fontName="Helvetica-Bold",
        textColor=accent_emerald,
    )

    story = []

    # -------------------------------------------------------------
    # CABEÇALHO DO RELATÓRIO
    # -------------------------------------------------------------
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("AUDITORIA FINANCEIRA & ESTUDO DE VIABILIDADE", ParagraphStyle("Tag", fontName="Helvetica-Bold", fontSize=9, textColor=brand_blue, spaceAfter=4)))
    story.append(Paragraph("Plataforma de Síntese & Clonagem de Voz com IA", title_style))
    story.append(Paragraph("Demonstrativo Preciso de Custos de API, Precificação de Pacotes, Margens Reais e Lucratividade", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=brand_blue, spaceBefore=0, spaceAfter=12))

    # Meta Info Card
    meta_data = [
        [
            Paragraph("<b>Projeto:</b> VoxStudio SaaS (Conversor de Voz Comercial)", table_cell_style),
            Paragraph("<b>Cotação Base de Câmbio:</b> US$ 1,00 = R$ 5,60", table_cell_style)
        ],
        [
            Paragraph("<b>Modelo de Cobrança:</b> Venda de Créditos por Áudio (PIX)", table_cell_style),
            Paragraph("<b>Auditoria de Dados:</b> Outubro de 2026", table_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[8.5 * cm, 8.5 * cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 1. A MATEMÁTICA REAL E AUDITADA POR CARACTERE E POR ÁUDIO
    # -------------------------------------------------------------
    story.append(Paragraph("1. A Matemática Real da ElevenLabs: Quanto Custa 1 Caractere e 1 Áudio?", h1_style))
    story.append(Paragraph(
        "Para responder com rigor se os cálculos estão corretos: a ElevenLabs não cobra por 'áudio', mas sim por <b>caracteres de texto</b> "
        "(incluindo espaços e pontuações). Portanto, o custo exato de cada áudio depende do tamanho do texto que o usuário digita.",
        body_style
    ))

    calc_data = [
        [
            Paragraph("<b>Plano ElevenLabs</b>", table_header_style),
            Paragraph("<b>Preço Mensal</b>", table_header_style),
            Paragraph("<b>Créditos / Chars</b>", table_header_style),
            Paragraph("<b>Custo por Caractere</b>", table_header_style),
            Paragraph("<b>Custo Áudio 30s<br/>(~450 caracteres)</b>", table_header_style),
            Paragraph("<b>Custo Áudio 1 min<br/>(~900 caracteres)</b>", table_header_style)
        ],
        [
            Paragraph("<b>Starter</b>", table_cell_bold),
            Paragraph("US$ 5,00 (~R$ 28,00)", table_cell_style),
            Paragraph("30.000", table_cell_style),
            Paragraph("R$ 0,00093", table_cell_style),
            Paragraph("<b>R$ 0,42</b>", table_cell_bold),
            Paragraph("<b>R$ 0,84</b>", table_cell_bold)
        ],
        [
            Paragraph("<b>Creator</b>", table_cell_bold),
            Paragraph("US$ 22,00 (~R$ 123,20)", table_cell_style),
            Paragraph("121.000", table_cell_style),
            Paragraph("R$ 0,00101", table_cell_style),
            Paragraph("<b>R$ 0,45</b>", table_cell_bold),
            Paragraph("<b>R$ 0,91</b>", table_cell_bold)
        ],
        [
            Paragraph("<b>Pro</b>", table_cell_bold),
            Paragraph("US$ 99,00 (~R$ 554,40)", table_cell_style),
            Paragraph("600.000", table_cell_style),
            Paragraph("R$ 0,00092", table_cell_style),
            Paragraph("<b>R$ 0,41</b>", table_cell_bold),
            Paragraph("<b>R$ 0,83</b>", table_cell_bold)
        ]
    ]
    calc_table = Table(calc_data, colWidths=[2.6 * cm, 3.2 * cm, 2.5 * cm, 2.8 * cm, 2.9 * cm, 3.0 * cm])
    calc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
    ]))
    story.append(calc_table)
    story.append(Spacer(1, 8))

    callout_data = [[
        Paragraph(
            "<b>Ponto Crítico de Auditoria:</b> O custo real de um áudio completo de 1 minuto (~900 caracteres / 150 palavras) "
            "fica entre <b>R$ 0,83 e R$ 0,85</b>. Já para vídeos curtos de 30 segundos (TikTok / Reels / Shorts / anúncios), "
            "o custo é de <b>R$ 0,42</b>. Portanto, os cálculos de pacotes devem ser estruturados levando em conta essa média real.",
            callout_style
        )
    ]]
    callout_table = Table(callout_data, colWidths=[17 * cm])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 2. TABELA CORRIGIDA E REALISTA DE PACOTES DE CRÉDITOS
    # -------------------------------------------------------------
    story.append(Paragraph("2. Tabela Corrigida: Pacotes de Venda, Custos e Lucro Real", h1_style))
    story.append(Paragraph(
        "Abaixo está a demonstração financeira real, já descontando a <b>Taxa do PIX (Mercado Pago / Asaas ~0,99%)</b> "
        "e o custo real da API considerando áudios de até 1.000 caracteres (~1 min):",
        body_style
    ))

    packages_data = [
        [
            Paragraph("<b>Pacote</b>", table_header_style),
            Paragraph("<b>Preço de Venda</b>", table_header_style),
            Paragraph("<b>Qtd. Áudios (1 min)</b>", table_header_style),
            Paragraph("<b>Preço / Áudio</b>", table_header_style),
            Paragraph("<b>Taxa PIX (1%)</b>", table_header_style),
            Paragraph("<b>Custo API Real</b>", table_header_style),
            Paragraph("<b>Lucro Líquido</b>", table_header_style),
            Paragraph("<b>Margem %</b>", table_header_style)
        ],
        [
            Paragraph("<b>Básico / Teste</b>", table_cell_bold),
            Paragraph("R$ 9,90", table_cell_style),
            Paragraph("3 áudios", table_cell_style),
            Paragraph("R$ 3,30", table_cell_style),
            Paragraph("R$ 0,10", table_cell_style),
            Paragraph("R$ 2,52", table_cell_style),
            Paragraph("<b>R$ 7,28</b>", table_cell_green),
            Paragraph("<b>73,5%</b>", table_cell_green)
        ],
        [
            Paragraph("<b>Criador Dark</b>", table_cell_bold),
            Paragraph("R$ 27,90", table_cell_style),
            Paragraph("12 áudios", table_cell_style),
            Paragraph("R$ 2,32", table_cell_style),
            Paragraph("R$ 0,28", table_cell_style),
            Paragraph("R$ 10,08", table_cell_style),
            Paragraph("<b>R$ 17,54</b>", table_cell_green),
            Paragraph("<b>62,8%</b>", table_cell_green)
        ],
        [
            Paragraph("<b>Profissional</b>", table_cell_bold),
            Paragraph("R$ 57,90", table_cell_style),
            Paragraph("30 áudios", table_cell_style),
            Paragraph("R$ 1,93", table_cell_style),
            Paragraph("R$ 0,58", table_cell_style),
            Paragraph("R$ 25,20", table_cell_style),
            Paragraph("<b>R$ 32,12</b>", table_cell_green),
            Paragraph("<b>55,5%</b>", table_cell_green)
        ],
        [
            Paragraph("<b>Agência / Master</b>", table_cell_bold),
            Paragraph("R$ 119,90", table_cell_style),
            Paragraph("70 áudios", table_cell_style),
            Paragraph("R$ 1,71", table_cell_style),
            Paragraph("R$ 1,20", table_cell_style),
            Paragraph("R$ 58,80", table_cell_style),
            Paragraph("<b>R$ 59,90</b>", table_cell_green),
            Paragraph("<b>50,0%</b>", table_cell_green)
        ]
    ]

    packages_table = Table(packages_data, colWidths=[2.5 * cm, 2.2 * cm, 2.3 * cm, 2.1 * cm, 2.0 * cm, 2.2 * cm, 2.0 * cm, 1.7 * cm])
    packages_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
    ]))
    story.append(packages_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>Conclusão da Análise de Lucro:</b> Mesmo ajustando os custos com máximo rigor (áudios completos de 1 minuto e descontando taxas de pagamento), "
        "o lucro líquido permanece entre <b>50% e 73,5%</b>. No mercado de produtos digitais e serviços, uma margem líquida superior a 50% é considerada "
        "<b>excepcionalmente saudável</b>.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Page Break for Break-even and Market viability
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 3. PONTO DE EQUILÍBRIO (BREAK-EVEN): QUANTAS VENDAS PRECISO?
    # -------------------------------------------------------------
    story.append(Paragraph("3. Ponto de Equilíbrio (Break-Even): Quantas Vendas para Lucrar?", h1_style))
    story.append(Paragraph(
        "Considerando todos os custos fixos mensais para manter a plataforma no ar:",
        body_style
    ))
    story.append(Paragraph("• <b>Plano Starter ElevenLabs:</b> R$ 28,00 / mês", bullet_style))
    story.append(Paragraph("• <b>Hospedagem VPS Nuvem:</b> R$ 30,00 / mês", bullet_style))
    story.append(Paragraph("• <b>Domínio Registro.br:</b> R$ 3,33 / mês (R$ 40/ano)", bullet_style))
    story.append(Paragraph("• <b>CUSTO FIXO TOTAL:</b> <b>R$ 61,33 / mês</b>", bullet_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>Para empatar todos os seus custos (R$ 61,33) no mês, você só precisa de:</b><br/>"
        "• <b>9 vendas</b> do pacote Básico de R$ 9,90;<br/>"
        "• OU <b>4 vendas</b> do pacote Criador de R$ 27,90;<br/>"
        "• OU <b>2 vendas</b> do pacote Profissional de R$ 57,90;<br/>"
        "• OU <b>1 única venda</b> do pacote Agência de R$ 119,90!",
        body_style
    ))
    story.append(Paragraph(
        "<b>Tudo o que for vendido a partir disso é LUCRO LÍQUIDO no seu bolso.</b>",
        ParagraphStyle("BoldCallout", fontName="Helvetica-Bold", fontSize=10, textColor=accent_emerald)
    ))
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------
    # 4. VALIDAÇÃO DE MERCADO: AS PESSOAS REALMENTE PAGAM?
    # -------------------------------------------------------------
    story.append(Paragraph("4. As Pessoas Realmente Pagam? Comparativo com a Concorrência", h1_style))
    story.append(Paragraph(
        "Sim, e o motivo é uma simples comparação de custo que o cliente faz na cabeça dele:",
        body_style
    ))

    comp_data = [
        [
            Paragraph("<b>Opção do Cliente</b>", table_header_style),
            Paragraph("<b>Custo para o Cliente</b>", table_header_style),
            Paragraph("<b>Prazo de Entrega</b>", table_header_style),
            Paragraph("<b>Inconveniência / Atrito</b>", table_header_style)
        ],
        [
            Paragraph("<b>Locutor Humano Profissional</b><br/>(VinteConto, Workana)", table_cell_bold),
            Paragraph("R$ 50,00 a R$ 200,00 por áudio", table_cell_style),
            Paragraph("24 a 48 horas", table_cell_style),
            Paragraph("Precisa negociar, mandar script, esperar regravar erros.", table_cell_style)
        ],
        [
            Paragraph("<b>Assinar ElevenLabs Direto</b>", table_cell_bold),
            Paragraph("US$ 5 a US$ 22 / mês em Dólar", table_cell_style),
            Paragraph("Instantâneo", table_cell_style),
            Paragraph("Exige cartão internacional, cobra IOF, site 100% em inglês, cobrança recorrente automática.", table_cell_style)
        ],
        [
            Paragraph("<b>SEU SISTEMA (VoxStudio)</b>", table_cell_bold),
            Paragraph("<b>R$ 1,71 a R$ 3,30 por áudio (PIX)</b>", table_cell_green),
            Paragraph("<b>3 segundos</b>", table_cell_green),
            Paragraph("<b>Paga no PIX sem cartão, interface 100% em português, gera e baixa na hora!</b>", table_cell_green)
        ]
    ]

    comp_table = Table(comp_data, colWidths=[4.2 * cm, 4.4 * cm, 3.2 * cm, 5.2 * cm])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#ECFDF5")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # 5. RECOMENDAÇÃO FINAL
    # -------------------------------------------------------------
    story.append(Paragraph("5. Recomendação Estratégica", h1_style))
    story.append(Paragraph(
        "A viabilidade é comprovada pelos números. O risco financeiro para começar é praticamente nulo (R$ 61,00/mês). "
        "A recomendação técnica e comercial é <b>avançar na estruturação do sistema</b> com integração do Starter e do PIX, "
        "validando as primeiras vendas com criadores de conteúdo do YouTube e TikTok.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF atualizado com sucesso!")

if __name__ == "__main__":
    build_pdf()
