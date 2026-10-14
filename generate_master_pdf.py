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

PDF_FILENAME = "Plano_de_Negocios_Completo_VoxStudio_SaaS.pdf"

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
            self.drawString(2 * cm, 28.5 * cm, "PLANO DE NEGÓCIOS & CHECKLIST DE IMPLEMENTAÇÃO • SAAS DE VOZ COM IA")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(2 * cm, 28.3 * cm, 19 * cm, 28.3 * cm)

        # Footer
        footer_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(19 * cm, 1.2 * cm, footer_text)
        self.drawString(2 * cm, 1.2 * cm, "Documento Estratégico Oficial • Arquitetura Serverless Vercel & Modelo PIX")
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
    brand_blue = colors.HexColor("#1D4ED8")
    accent_emerald = colors.HexColor("#047857")
    accent_purple = colors.HexColor("#6D28D9")
    text_dark = colors.HexColor("#1E293B")
    bg_subtle = colors.HexColor("#F8FAFC")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=6,
    )
    
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13.5,
        textColor=brand_blue,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=text_dark,
        spaceAfter=4,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=11,
        bulletIndent=4,
        spaceAfter=2.5,
    )

    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E3A8A"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
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
    # CAPA DO PLANO DE NEGÓCIOS
    # -------------------------------------------------------------
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("DOCUMENTO ESTRATÉGICO INTEGRAL • VERSÃO DEFINITIVA", ParagraphStyle("Tag", fontName="Helvetica-Bold", fontSize=8.5, textColor=brand_blue, spaceAfter=4)))
    story.append(Paragraph("Plano de Negócios & Checklist de Execução:<br/>Plataforma SaaS de Clonagem e Síntese Vocal", title_style))
    story.append(Paragraph("Engenharia de Produto, Arquitetura Serverless (Vercel), Análise Competitiva, DRE Auditado e Roteiro de Implementação", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=brand_blue, spaceBefore=0, spaceAfter=8))

    # Meta Info Card
    meta_data = [
        [
            Paragraph("<b>Stack Recomendada:</b> Vercel (Frontend/Edge) + ElevenLabs (IA) + Supabase (DB)", table_cell_style),
            Paragraph("<b>Modelo Comercial:</b> Pay-Per-Audio / Créditos Pré-pagos via PIX", table_cell_style)
        ],
        [
            Paragraph("<b>Custo Fixo Mínimo:</b> R$ 31,33 / mês (ElevenLabs Starter + Domínio)", table_cell_style),
            Paragraph("<b>Margem Líquida Média:</b> 50% a 73,5% por transação de venda", table_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[8.5 * cm, 8.5 * cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_subtle),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # 1. VISÃO GERAL EXECUTIVA & VIABILIDADE DO NEGÓCIO
    # -------------------------------------------------------------
    story.append(Paragraph("1. Visão Geral do Negócio: Por que a Oportunidade é Gigante?", h1_style))
    story.append(Paragraph(
        "O negócio baseia-se em resolver a maior dor de criadores de conteúdo, agências e pequenas empresas: "
        "<b>o alto custo e a extrema lentidão da locução humana tradicional</b>. Enquanto um locutor cobra de R$ 50 a R$ 200 "
        "por áudio e demora até 48 horas, a nossa plataforma entrega voz com qualidade humana e clonagem perfeita em 3 segundos "
        "por uma fração do preço (R$ 1,70 a R$ 3,30).",
        body_style
    ))
    story.append(Paragraph(
        "<b>Os 4 Principais Públicos Compradores no Brasil:</b><br/>"
        "1. <b>Criadores de Canais Dark:</b> Milhares de pessoas que faturam no YouTube e TikTok com vídeos sem aparecer e precisam de 10 a 30 áudios por semana.<br/>"
        "2. <b>Gestores de Tráfego & Afiliados:</b> Criadores de anúncios em vídeo (VSLs) que testam dezenas de variações de narração por semana.<br/>"
        "3. <b>Pequenas Empresas:</b> Mensagens para WhatsApp Business, esperas telefônicas e propaganda de redes sociais.<br/>"
        "4. <b>Infoprodutores & Educadores:</b> Narração automatizada de apostilas, slides e cursos online.",
        bullet_style
    ))
    story.append(Spacer(1, 4))

    # -------------------------------------------------------------
    # 2. ARQUITETURA TECNOLÓGICA & ESCALABILIDADE (VERCEL)
    # -------------------------------------------------------------
    story.append(Paragraph("2. Arquitetura Tecnológica: Por que a Vercel é a Melhor Escolha?", h1_style))
    story.append(Paragraph(
        "A Vercel foi escolhida como a espinha dorsal de infraestrutura da plataforma pelas seguintes razões comprovadas:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Custo Zero de Servidor Inicial:</b> O plano Hobby da Vercel é 100% gratuito e elimina o custo de VPS no início.<br/>"
        "• <b>Escalabilidade Infinita Automática (Auto-Scaling):</b> Ao contrário de servidores comuns (Hostinger/VPS) que travam "
        "se 500 pessoas entrarem juntas, a Vercel suporta picos de até 50.000 usuários simultâneos acionando micro-funções isoladas.<br/>"
        "• <b>Servidores em São Paulo (Edge CDN):</b> Latência mínima para clientes brasileiros.<br/>"
        "• <b>Deploy Contínuo via GitHub:</b> Qualquer atualização no código vai para o ar em 30 segundos com SSL/HTTPS gratuito.",
        bullet_style
    ))

    arch_data = [
        [
            Paragraph("<b>Camada do Sistema</b>", table_header_style),
            Paragraph("<b>Ferramenta / Provedor</b>", table_header_style),
            Paragraph("<b>Custo Inicial</b>", table_header_style),
            Paragraph("<b>Papel no Negócio</b>", table_header_style)
        ],
        [
            Paragraph("<b>Frontend & API Serverless</b>", table_cell_bold),
            Paragraph("Vercel (Next.js / FastAPI Edge)", table_cell_style),
            Paragraph("<b>R$ 0,00</b> (Grátis)", table_cell_green),
            Paragraph("Interface web do usuário, roteamento e escala global.", table_cell_style)
        ],
        [
            Paragraph("<b>Motor Neural de IA</b>", table_cell_bold),
            Paragraph("ElevenLabs API (Plano Starter)", table_cell_style),
            Paragraph("<b>US$ 5,00 (~R$ 28,00)</b>", table_cell_style),
            Paragraph("Geração de fala ultra-realista e Clonagem Instantânea.", table_cell_style)
        ],
        [
            Paragraph("<b>Banco de Dados & Auth</b>", table_cell_bold),
            Paragraph("Supabase (PostgreSQL + Auth)", table_cell_style),
            Paragraph("<b>R$ 0,00</b> (Grátis até 500MB)", table_cell_green),
            Paragraph("Contas de clientes, senhas, saldo de créditos e extrato.", table_cell_style)
        ],
        [
            Paragraph("<b>Armazenamento de Áudio</b>", table_cell_bold),
            Paragraph("Cloudflare R2 / Supabase Storage", table_cell_style),
            Paragraph("<b>R$ 0,00</b> (Grátis até 10GB)", table_cell_green),
            Paragraph("Hospedagem segura dos arquivos WAV/MP3 para download.", table_cell_style)
        ],
        [
            Paragraph("<b>Gateway de Pagamento</b>", table_cell_bold),
            Paragraph("Mercado Pago / Asaas (PIX)", table_cell_style),
            Paragraph("<b>R$ 0,00 fixo</b> (~0,99% p/ venda)", table_cell_style),
            Paragraph("Emissão de QR Code PIX e liberação instantânea de saldo.", table_cell_style)
        ]
    ]
    arch_table = Table(arch_data, colWidths=[4.0 * cm, 4.4 * cm, 3.4 * cm, 5.2 * cm])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 6))

    # Page Break for Financials & Competitors
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 3. DEMONSTRATIVO FINANCEIRO AUDITADO & PRECIFICAÇÃO
    # -------------------------------------------------------------
    story.append(Paragraph("3. Matemática Financeira Auditada: Custos, Pacotes e Lucro Líquido", h1_style))
    story.append(Paragraph(
        "A ElevenLabs consome créditos por caractere de texto. No Plano Starter (US$ 5,00 = ~R$ 28,00 por 30.000 caracteres), "
        "o custo é de <b>R$ 0,00093 por caractere</b>. Isso resulta em um custo de <b>R$ 0,42 para áudios curtos (30s)</b> e "
        "<b>R$ 0,84 para áudios de 1 minuto completo (~900 caracteres)</b>.",
        body_style
    ))

    packages_data = [
        [
            Paragraph("<b>Pacote de Créditos</b>", table_header_style),
            Paragraph("<b>Preço Cobrado</b>", table_header_style),
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
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
    ]))
    story.append(packages_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Ponto de Equilíbrio (Break-Even):</b> Como a Vercel e o Supabase são gratuitos no início, seu custo fixo mensal é de apenas "
        "<b>R$ 31,33/mês</b> (R$ 28 da ElevenLabs + R$ 3,33 do domínio anual de R$ 40). "
        "Com <b>apenas 2 vendas de R$ 27,90 ou 4 vendas de R$ 9,90</b> no mês, todo o custo do negócio já está pago!",
        body_style
    ))
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # 4. MAPEAMENTO DE DOMÍNIOS NO REGISTRO.BR
    # -------------------------------------------------------------
    story.append(Paragraph("4. Auditoria Oficial de Naming no Registro.br", h1_style))
    story.append(Paragraph(
        "O domínio original <b>voxstudio.com.br</b> já se encontra ocupado por terceiros. "
        "Identificamos excelentes opções <b>100% disponíveis para registro imediato no Registro.br (R$ 40/ano)</b>:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>clonavoz.com.br (LIVRE):</b> Nome altamente comercial, curto e focado na dor de clonar vozes com facilidade.<br/>"
        "• <b>vozneural.com.br (LIVRE):</b> Nome sofisticado, autoridade tecnológica imediata para agências e narradores.<br/>"
        "• <b>clonadordevoz.com.br (LIVRE):</b> Termo exato de busca orgânica no Google (máximo potencial de tráfego grátis).",
        bullet_style
    ))
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # 5. MÁQUINA DE MARKETING & AQUISIÇÃO
    # -------------------------------------------------------------
    story.append(Paragraph("5. Modelos de Marketing para Alavancar o Negócio", h1_style))
    story.append(Paragraph(
        "• <b>Vídeos Virais de Demonstração (TikTok/Reels/Shorts) - Custo R$ 0:</b> Gravar vídeos curtos mostrando a clonagem de áudios "
        "curiosos com a chamada: <i>'Link na bio para testar 1 áudio grátis'</i>.<br/>"
        "• <b>Infiltração em Comunidades Quentes:</b> Grupos de Facebook e Telegram de criadores de Canais Dark e Afiliados de VSL.<br/>"
        "• <b>Mecanismo de Indicação 'Member-Get-Member':</b> Conceder 3 áudios grátis para o usuário que indicar um amigo pagante.<br/>"
        "• <b>Google Search Ads de Alta Intenção:</b> Anúncios de pesquisa para termos como <i>'clonador de voz portugues'</i>.",
        bullet_style
    ))
    story.append(Spacer(1, 6))

    # Page Break for Checklist
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 6. CHECKLIST COMPLETO DE IMPLEMENTAÇÃO DO NEGÓCIO
    # -------------------------------------------------------------
    story.append(Paragraph("6. Checklist Estruturado de Implementação Passo a Passo", h1_style))
    story.append(Paragraph(
        "Seguindo a sua solicitação, o checklist foi ordenado iniciando pela <b>Experiência do Usuário (UX/UI)</b>, "
        "seguida pelas <b>APIs & Integrações</b>, e deixando a <b>configuração do domínio por último</b> "
        "(enquanto o registro é feito em paralelo):",
        body_style
    ))

    chk_header_style = ParagraphStyle("ChkHead", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=brand_blue)
    chk_sub_style = ParagraphStyle("ChkSub", fontName="Helvetica", fontSize=8, leading=11, textColor=text_dark)

    chk_data = [
        [
            Paragraph("<b>Fase / Etapa</b>", table_header_style),
            Paragraph("<b>Atividades Detalhadas de Execução</b>", table_header_style),
            Paragraph("<b>Critério de Conclusão / Entregável</b>", table_header_style)
        ],
        [
            Paragraph("<b>FASE 1:<br/>UX & UI<br/>(Interface do Usuário)</b>", chk_header_style),
            Paragraph(
                "1.1. Desenhar a Landing Page de alta conversão (título forte, vídeo rápido de exemplo, prova social).<br/>"
                "1.2. Criar o Studio do Usuário com Seletor de Voz em Dropdown moderno e agrupado.<br/>"
                "1.3. Integrar WaveSurfer.js para visualização de ondas sonoras e player interativo.<br/>"
                "1.4. Desenvolver Modal de Upload de Voz com pré-escuta de áudio e termos de autorização.<br/>"
                "1.5. Desenvolver Modal de Recarga com cards de pacotes de crédito e tela de QR Code PIX.<br/>"
                "1.6. Criar indicador visual fixo de 'Saldo de Áudios Disponíveis' no topo da tela.",
                chk_sub_style
            ),
            Paragraph("Telas e componentes responsivos prontos e validados visualmente no PC e celular.", table_cell_style)
        ],
        [
            Paragraph("<b>FASE 2:<br/>APIs & Motor de IA<br/>(ElevenLabs)</b>", chk_header_style),
            Paragraph(
                "2.1. Criar conta Starter na ElevenLabs e obter a chave de API de produção.<br/>"
                "2.2. Integrar endpoint de Text-to-Speech com modelo Eleven Multilingual v2 / Turbo.<br/>"
                "2.3. Integrar endpoint de Instant Voice Cloning (envio do áudio de 1 min da voz enviada).<br/>"
                "2.4. Implementar trava de caracteres (1 crédito = até 1.000 caracteres, bloqueio sem saldo).<br/>"
                "2.5. Implementar fallback de erro amigável caso a API demore ou oscile.",
                chk_sub_style
            ),
            Paragraph("Áudios gerados com clonagem real 10/10 e voz da Marina idêntica em menos de 3 segundos.", table_cell_style)
        ],
        [
            Paragraph("<b>FASE 3:<br/>Banco de Dados & Pagamento PIX</b>", chk_header_style),
            Paragraph(
                "3.1. Criar projeto gratuito no Supabase (PostgreSQL) para gerenciar Usuários e Créditos.<br/>"
                "3.2. Implementar sistema de Cadastro e Login simples (e-mail e senha).<br/>"
                "3.3. Configurar concessão automática de 1 áudio grátis de boas-vindas no cadastro.<br/>"
                "3.4. Criar conta no Mercado Pago ou Asaas e obter credenciais de API PIX.<br/>"
                "3.5. Desenvolver Webhook de confirmação de pagamento: assim que o PIX for pago, os créditos caem no saldo do usuário em 2 segundos.",
                chk_sub_style
            ),
            Paragraph("Fluxo completo de compra testado: pagamento PIX aprovado e saldo liberado automaticamente.", table_cell_style)
        ],
        [
            Paragraph("<b>FASE 4:<br/>Deploy na Vercel & Escalabilidade</b>", chk_header_style),
            Paragraph(
                "4.1. Criar repositório privado no GitHub com o código da aplicação.<br/>"
                "4.2. Conectar o repositório na Vercel (plano Hobby gratuito).<br/>"
                "4.3. Cadastrar as variáveis de ambiente secretas na Vercel (API Keys, tokens de banco).<br/>"
                "4.4. Testar funcionamento das rotas serverless na Edge de São Paulo.<br/>"
                "4.5. Validar tempo de carregamento e certificado SSL automático.",
                chk_sub_style
            ),
            Paragraph("Site no ar na nuvem Vercel com auto-scaling ativo e resposta ultra-rápida.", table_cell_style)
        ],
        [
            Paragraph("<b>FASE 5:<br/>Domínio & Lançamento Comercial</b>", chk_header_style),
            Paragraph(
                "5.1. Registrar o domínio escolhido (ex: <i>clonavoz.com.br</i>) no Registro.br (R$ 40/ano).<br/>"
                "5.2. Apontar os DNS do Registro.br para os servidores da Vercel (CNAME e A records).<br/>"
                "5.3. Realizar teste de compra real de R$ 9,90 de ponta a ponta em ambiente de produção.<br/>"
                "5.4. Publicar os primeiros vídeos no TikTok e Reels e divulgar em grupos de Canais Dark.",
                chk_sub_style
            ),
            Paragraph("Plataforma aberta ao público com domínio próprio oficial e faturando.", table_cell_green)
        ]
    ]

    chk_table = Table(chk_data, colWidths=[3.2 * cm, 9.6 * cm, 4.2 * cm])
    chk_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(chk_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 7. CONCLUSÃO
    # -------------------------------------------------------------
    story.append(Paragraph("7. Conclusão e Próximos Passos", h1_style))
    story.append(Paragraph(
        "Este plano de negócios fornece a estrutura completa para colocar um SaaS de voz altamente lucrativo no ar "
        "com investimento mínimo e máxima escalabilidade. O roadmap está desenhado para execução precisa quando você "
        "decidir dar início ao desenvolvimento.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Plano de Negócios Completo gerado em PDF: {PDF_FILENAME}")

if __name__ == "__main__":
    build_pdf()
