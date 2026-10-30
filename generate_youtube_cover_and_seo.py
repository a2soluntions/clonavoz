import os
import math
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = r"e:\A2\projetos\gerador de voz com texto"
STATIC_DIR = os.path.join(BASE_DIR, "static")
MKT_BASE = r"E:\A2\Projetos marcketing\clonavoz"
YOUTUBE_DIR = os.path.join(MKT_BASE, "3_YOUTUBE")
THUMBS_DIR = os.path.join(YOUTUBE_DIR, "Thumbnails_16x9")
DESKTOP_DIR = r"C:\Users\User\Desktop"

os.makedirs(THUMBS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

WIDTH = 1280
HEIGHT = 720

def get_font(size, bold=False):
    win_fonts = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"] if bold else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
    for f in win_fonts:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_badge = get_font(24, bold=True)
font_huge = get_font(76, bold=True)
font_title = get_font(52, bold=True)
font_subtitle = get_font(34, bold=True)
font_body = get_font(24, bold=False)
font_price = get_font(54, bold=True)
font_card_head = get_font(26, bold=True)

# Cria canvas base em 1280x720
img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 9, 14, 255))

# 1. Background com atmosfera neon (Laranja fogo no topo esquerdo + Verde esmeralda no canto direito)
glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
g_draw = ImageDraw.Draw(glow_layer)

# Glow Laranja (Esquerda)
g_draw.ellipse([-100, -100, 650, 650], fill=(255, 75, 0, 80))
# Glow Verde Esmeralda (Direita)
g_draw.ellipse([700, 200, 1450, 950], fill=(0, 225, 120, 65))
# Glow Roxo/Azul central profundo
g_draw.ellipse([450, 150, 950, 650], fill=(80, 40, 200, 45))

glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(120))
img = Image.alpha_composite(img, glow_layer)
draw = ImageDraw.Draw(img)

# Grade técnica sutil no fundo
for x in range(0, WIDTH, 80):
    draw.line([(x, 0), (x, HEIGHT)], fill=(255, 255, 255, 8), width=1)
for y in range(0, HEIGHT, 80):
    draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 8), width=1)

# Helper para badges arredondados
def draw_badge(x, y, text, font, bg_fill, border_color, text_color, pad_x=22, pad_y=8):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    box_w = tw + pad_x * 2
    box_h = th + pad_y * 2
    draw.rounded_rectangle([x, y, x + box_w, y + box_h], radius=box_h//2, fill=bg_fill, outline=border_color, width=2)
    draw.text((x + box_w//2, y + box_h//2), text, fill=text_color, font=font, anchor="mm")
    return box_w

# --- LADO ESQUERDO: TEXTO DE IMPACTO E GANCHO VIRAL ---

# Badge 1: Topo Alerta
draw_badge(60, 48, "NOVA IA BRASILEIRA", font_badge, (45, 18, 12, 240), (255, 85, 0, 230), (255, 140, 60))
draw_badge(345, 48, "100% SOTAQUE NATURAL", font_badge, (16, 32, 24, 240), (0, 225, 120, 220), (0, 255, 140))

# Título 1: ADEUS DÓLAR!
# Sombra projetada para máxima legibilidade
draw.text((64, 122), "ADEUS ELEVENLABS!", fill=(0, 0, 0, 220), font=font_huge, anchor="lt")
draw.text((60, 118), "ADEUS ELEVENLABS!", fill=(255, 75, 40), font=font_huge, anchor="lt")

# Título 2: VOZ DE IA REALISTA
draw.text((64, 212), "VOZ DE IA REALISTA", fill=(0, 0, 0, 220), font=font_huge, anchor="lt")
draw.text((60, 208), "VOZ DE IA REALISTA", fill=(255, 255, 255), font=font_huge, anchor="lt")

# Linha 3: Subtítulo de Conversão
draw.text((60, 310), "Locuções perfeitas sem pagar mensalidade!", fill=(200, 205, 220), font=font_subtitle, anchor="lt")

# Card Grande de Destaque: Pague no PIX
card_pix_x = 60
card_pix_y = 375
card_pix_w = 640
card_pix_h = 240

# Sombra do Card
draw.rounded_rectangle([card_pix_x + 4, card_pix_y + 4, card_pix_x + card_pix_w + 4, card_pix_y + card_pix_h + 4], radius=24, fill=(0, 0, 0, 180))
# Corpo do Card
draw.rounded_rectangle([card_pix_x, card_pix_y, card_pix_x + card_pix_w, card_pix_y + card_pix_h], radius=24, fill=(14, 24, 18, 245), outline=(0, 225, 120, 180), width=3)

# Conteúdo interno do Card PIX
draw_badge(card_pix_x + 30, card_pix_y + 24, "DIRETO NO PIX", font_badge, (0, 225, 120, 40), (0, 225, 120, 200), (0, 255, 140))
draw_badge(card_pix_x + 220, card_pix_y + 24, "SEM CADASTRO", font_badge, (255, 85, 0, 35), (255, 85, 0, 180), (255, 140, 60))
draw_badge(card_pix_x + 415, card_pix_y + 24, "BAIXE NA HORA", font_badge, (20, 30, 45, 240), (0, 160, 255, 180), (100, 200, 255))

draw.text((card_pix_x + 30, card_pix_y + 92), "A partir de apenas:", fill=(180, 215, 190), font=font_body, anchor="lt")
draw.text((card_pix_x + 30, card_pix_y + 124), "R$ 2,49", fill=(0, 255, 140), font=font_price, anchor="lt")
draw.text((card_pix_x + 245, card_pix_y + 148), "por áudio completo!", fill=(225, 245, 230), font=font_subtitle, anchor="lt")

draw.text((card_pix_x + 30, card_pix_y + 195), "Perfeito para: Canais Dark • Reels • TikTok • VSLs & Anúncios", fill=(170, 195, 180), font=font_body, anchor="lt")

# Footer Marca
draw.text((60, 660), "CLONAVOZ.COM.BR  •  INTELIGÊNCIA ARTIFICIAL DE VOZ", fill=(130, 135, 150), font=font_badge, anchor="lt")


# --- LADO DIREITO: CARD DE COMPARATIVO & LOGOTIPO EM ALTO RELEVO ---

right_card_x = 745
right_card_y = 55
right_card_w = 475
right_card_h = 560

# Sombra
draw.rounded_rectangle([right_card_x + 6, right_card_y + 6, right_card_x + right_card_w + 6, right_card_y + right_card_h + 6], radius=28, fill=(0, 0, 0, 200))
# Card Comparativo Glass
draw.rounded_rectangle([right_card_x, right_card_y, right_card_x + right_card_w, right_card_y + right_card_h], radius=28, fill=(18, 18, 26, 245), outline=(255, 110, 30, 140), width=3)

# Logo Clonavoz no topo do card
logo_path = os.path.join(STATIC_DIR, "logo_perfil_instagram.png")
if os.path.exists(logo_path):
    logo_raw = Image.open(logo_path).convert("RGBA").resize((130, 130), Image.Resampling.LANCZOS)
    img.paste(logo_raw, (right_card_x + right_card_w//2 - 65, right_card_y + 25), logo_raw)
    draw = ImageDraw.Draw(img)

draw.text((right_card_x + right_card_w//2, right_card_y + 175), "CLONAVOZ AI", fill=(255, 255, 255), font=font_title, anchor="mm")
draw.text((right_card_x + right_card_w//2, right_card_y + 215), "Comparativo Real de Mercado", fill=(255, 140, 50), font=font_card_head, anchor="mm")

draw.line([(right_card_x + 40, right_card_y + 240), (right_card_x + right_card_w - 40, right_card_y + 240)], fill=(255, 255, 255, 30), width=1)

# Item Comparativo 1: Gringas
box1_y = right_card_y + 260
draw.rounded_rectangle([right_card_x + 30, box1_y, right_card_x + right_card_w - 30, box1_y + 90], radius=16, fill=(28, 18, 20, 230), outline=(255, 60, 60, 120), width=2)
draw.text((right_card_x + 50, box1_y + 22), "Plataformas Gringas:", fill=(200, 180, 185), font=font_body, anchor="lt")
draw.text((right_card_x + 50, box1_y + 48), "R$ 180 a R$ 450 / mês  [X]", fill=(255, 90, 90), font=font_card_head, anchor="lt")

# Item Comparativo 2: Clonavoz
box2_y = right_card_y + 365
draw.rounded_rectangle([right_card_x + 30, box2_y, right_card_x + right_card_w - 30, box2_y + 95], radius=16, fill=(16, 32, 22, 240), outline=(0, 225, 120, 180), width=2)
draw.text((right_card_x + 50, box2_y + 22), "Clonavoz (Zero Assinatura):", fill=(180, 220, 195), font=font_body, anchor="lt")
draw.text((right_card_x + 50, box2_y + 50), "Apenas R$ 2,49 no PIX  [V]", fill=(0, 255, 140), font=font_title, anchor="lt")

# Oferta de Boas-Vindas Banner Destaque
banner_y = right_card_y + 480
draw.rounded_rectangle([right_card_x + 30, banner_y, right_card_x + right_card_w - 30, banner_y + 55], radius=14, fill=(255, 85, 0), outline=(255, 160, 80), width=2)
draw.text((right_card_x + right_card_w//2, banner_y + 27), "OFERTA: 30 ÁUDIOS POR R$ 19,90", fill=(255, 255, 255), font=font_card_head, anchor="mm")

# Waveform decorativa animada no canto
for b in range(16):
    bh = int(14 + 32 * abs(math.sin(b * 0.7)))
    bx = right_card_x + 75 + b * 20
    by = 665 - bh // 2
    draw.rounded_rectangle([bx, by, bx + 10, by + bh], radius=4, fill=(0, 255, 140, 220))

draw.text((right_card_x + 420, 665), "ÁUDIO HD", fill=(0, 255, 140), font=font_badge, anchor="rm")

# Salva arquivo da Capa 16:9
output_thumb = os.path.join(THUMBS_DIR, "Capa_YouTube_Voz_IA_Clonavoz.png")
img.save(output_thumb, "PNG")
print(f"Capa YouTube salva com sucesso em: {output_thumb}")

# Copia para Desktop, Pasta Principal de Marketing e Static
dest_paths = [
    os.path.join(MKT_BASE, "Capa_YouTube_Voz_IA_Clonavoz.png"),
    os.path.join(DESKTOP_DIR, "Capa_YouTube_Voz_IA_Clonavoz.png"),
    os.path.join(STATIC_DIR, "Capa_YouTube_Voz_IA_Clonavoz.png")
]
for d in dest_paths:
    try:
        shutil.copyfile(output_thumb, d)
        print(f"Copia criada em: {d}")
    except Exception as e:
        print(f"Aviso ao copiar: {e}")

# --- GERAÇÃO DA DESCRIÇÃO COMPLETA E TAGS PARA O YOUTUBE ---
seo_text = """================================================================================
TÍTULOS SUGERIDOS PARA O YOUTUBE (TESTE A/B DE ALTO CTR):
================================================================================
Opção 1 (Mais Recomendada - Dor do Dólar + Solução):
ADEUS ELEVENLABS! Como Gerar Voz de IA Ultra-Realista no PIX (Sem Assinatura e Sem Cadastro)

Opção 2 (Foco em Canais Dark e Ganhar Dinheiro):
A Melhor IA de Voz para Canais Dark, Reels e TikTok no Brasil (Pague no PIX por Áudio)

Opção 3 (Foco em Preço e Praticidade Imediata):
Voz Neural Humana por R$ 2,49 no PIX: Chega de Pagar em Dólar no Cartão!

================================================================================
DESCRIÇÃO PRONTA PARA COPIAR E COLAR NO YOUTUBE:
================================================================================
🚨 Cansado de pagar assinaturas abusivas em dólar no cartão internacional só para ter vozes de inteligência artificial nos seus vídeos?

Conheça o CLONAVOZ AI (https://clonavoz.com.br) — a ferramenta de locução neural feita para o Brasil, com sotaque 100% natural, sem tom robótico e sem cobranças em dólar!

🔥 A MAIOR NOVIDADE: AGORA VOCÊ PODE GERAR DIRETO NO PIX, SEM CADASTRO!
✅ Digite seu texto no estúdio
✅ Ouça a demonstração gratuita para aprovar a voz
✅ Pague apenas a partir de R$ 2,49 no PIX e baixe seu arquivo .MP3 imediatamente!
Zero burocracia, sem formulários, sem cartão e sem mensalidade obrigatória.

🎁 QUER ECONOMIZAR AINDA MAIS?
Aproveite o Pacote de Boas-Vindas exclusivo:
Garanta 30 ÁUDIOS COMPLETOS por apenas R$ 19,90 no PIX (apenas R$ 0,66 por locução completa)!

👉 Experimente agora mesmo: https://clonavoz.com.br
(Disponível para celular, tablet e computador)

--------------------------------------------------------------------------------
📌 IDEAL PARA QUEM CRIA:
• Canais Dark no YouTube (histórias, curiosidades, mistérios, resumos)
• Vídeos para Reels, TikTok e YouTube Shorts com alta retenção
• VSLs (Vídeos de Vendas) e criativos de anúncios de alta conversão
• Podcasts, audiolivros, infoprodutos e vídeos institucionais

--------------------------------------------------------------------------------
⏱️ CAPÍTULOS / TIMESTAMPS:
00:00 - Chega de pagar em dólar por voz de IA
00:08 - O problema das plataformas gringas (IOF e mensalidades caras)
00:15 - Conheça o Clonavoz AI: Voz 100% brasileira
00:23 - Como gerar no PIX a partir de R$ 2,49 (Sem Cadastro)
00:30 - Oferta Especial de Boas-Vindas: 30 áudios por R$ 19,90
00:35 - Como testar grátis no link

--------------------------------------------------------------------------------
🏷️ TAGS / PALAVRAS-CHAVE RECOMENDADAS PARA O YOUTUBE:
clonavoz, voz de ia, inteligencia artificial, voz neural, elevenlabs alternativa, alternativa elevenlabs brasil, voz sintetica, tts brasil, como criar canais dark, canal dark youtube, voz para canal dark, narrador de ia, gerador de voz com texto, converter texto em voz, voz humanizada ia, voz realista inteligencia artificial, vozes neurais portugues, clonagem de voz ia, narracao para reels, narracao para tiktok, voz para vsl, criar audio no pix, voz ia sem cartao de credito

--------------------------------------------------------------------------------
HASHTAGS:
#clonavoz #vozdeia #inteligenciaartificial #canaisdark #marketingdigital #elevenlabs #reelsbrasil #tiktokbrasil #vsl #ia
================================================================================
"""

seo_file_path = os.path.join(YOUTUBE_DIR, "Descricao_e_Tags_YouTube_Viral.txt")
desktop_seo_path = os.path.join(DESKTOP_DIR, "Descricao_e_Tags_YouTube_Viral.txt")

with open(seo_file_path, "w", encoding="utf-8") as f:
    f.write(seo_text)

with open(desktop_seo_path, "w", encoding="utf-8") as f:
    f.write(seo_text)

print(f"Descricao e Tags salvas com sucesso em: {seo_file_path} e no Desktop!")
