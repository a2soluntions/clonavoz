import os
import math
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = r"e:\A2\projetos\gerador de voz com texto"
STATIC_DIR = os.path.join(BASE_DIR, "static")
MKT_BASE = r"E:\A2\Projetos marcketing\clonavoz"
IG_DIR = os.path.join(MKT_BASE, "1_INSTAGRAM")
STORIES_DIR = os.path.join(IG_DIR, "Capas_Stories_9x16")
DESKTOP_DIR = r"C:\Users\User\Desktop"

os.makedirs(STORIES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920

def get_font(size, bold=False):
    win_fonts = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"] if bold else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
    for f in win_fonts:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_badge = get_font(28, bold=True)
font_huge = get_font(72, bold=True)
font_title = get_font(52, bold=True)
font_subtitle = get_font(38, bold=True)
font_body = get_font(30, bold=False)
font_price = get_font(84, bold=True)
font_cta_btn = get_font(42, bold=True)
font_footer = get_font(24, bold=False)

# Cria canvas base 1080x1920
img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 9, 14, 255))

# 1. Background com atmosfera neon profissional
glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
g_draw = ImageDraw.Draw(glow_layer)

# Glow Laranja (Topo)
g_draw.ellipse([WIDTH//2 - 450, 80, WIDTH//2 + 450, 980], fill=(255, 75, 0, 65))
# Glow Verde Esmeralda (Centro-Baixo)
g_draw.ellipse([WIDTH//2 - 480, 800, WIDTH//2 + 480, 1600], fill=(0, 225, 120, 50))
# Glow Azul profundo
g_draw.ellipse([WIDTH//2 - 350, 500, WIDTH//2 + 350, 1200], fill=(60, 40, 180, 35))

glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(140))
img = Image.alpha_composite(img, glow_layer)
draw = ImageDraw.Draw(img)

# Grade técnica sutil
for x in range(0, WIDTH, 90):
    draw.line([(x, 0), (x, HEIGHT)], fill=(255, 255, 255, 6), width=1)
for y in range(0, HEIGHT, 90):
    draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 6), width=1)

# Helper para badges centralizados auto-dimensionados
def draw_auto_badge(draw, text, y_center, font, fill_bg, outline_color, text_color, pad_x=36, pad_y=14, border_width=2):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    box_w = tw + pad_x * 2
    box_h = th + pad_y * 2
    left = (WIDTH - box_w) // 2
    right = left + box_w
    top = y_center - box_h // 2
    bottom = top + box_h
    radius = box_h // 2
    draw.rounded_rectangle([left, top, right, bottom], radius=radius, fill=fill_bg, outline=outline_color, width=border_width)
    draw.text((WIDTH // 2, y_center), text, fill=text_color, font=font, anchor="mm")
    return (left, top, right, bottom)

# --- ZONA SEGURA SUPERIOR DO INSTAGRAM STORIES (220px+) ---

# Header Marca
draw.text((WIDTH//2, 230), "CLONAVOZ AI", fill=(255, 130, 45, 240), font=font_subtitle, anchor="mm")
draw.line([(WIDTH//2 - 100, 255), (WIDTH//2 + 100, 255)], fill=(255, 85, 0, 180), width=2)

# Badge de Novidade
draw_auto_badge(draw, "NOVA IA DE VOZ NO BRASIL", 310, font_badge,
                fill_bg=(40, 16, 12, 235), outline_color=(255, 85, 0, 220), text_color=(255, 140, 60))

# Título de Alto Impacto
draw.text((WIDTH//2, 400), "ADEUS ELEVENLABS!", fill=(255, 75, 40), font=font_huge, anchor="mm")
draw.text((WIDTH//2, 485), "VOZ DE IA REALISTA", fill=(255, 255, 255), font=font_huge, anchor="mm")
draw.text((WIDTH//2, 560), "SEM PAGAR EM DÓLAR", fill=(255, 205, 60), font=font_title, anchor="mm")

# --- CARD 1: COMPARATIVO DE CUSTO ---
card_comp_w = WIDTH - 140
card_comp_x = 70
card_comp_y = 630
card_comp_h = 240

# Sombra
draw.rounded_rectangle([card_comp_x + 4, card_comp_y + 4, card_comp_x + card_comp_w + 4, card_comp_y + card_comp_h + 4], radius=26, fill=(0, 0, 0, 180))
# Corpo Glass
draw.rounded_rectangle([card_comp_x, card_comp_y, card_comp_x + card_comp_w, card_comp_y + card_comp_h], radius=26, fill=(18, 18, 26, 240), outline=(255, 100, 20, 120), width=2)

# Linha 1: Gringas
draw.rounded_rectangle([card_comp_x + 25, card_comp_y + 25, card_comp_x + card_comp_w - 25, card_comp_y + 115], radius=16, fill=(28, 18, 20, 230), outline=(255, 60, 60, 120), width=2)
draw.text((card_comp_x + 50, card_comp_y + 50), "Plataformas Gringas (Cartão Internacional):", fill=(200, 180, 185), font=font_body, anchor="lt")
draw.text((card_comp_x + 50, card_comp_y + 80), "R$ 180 a R$ 450 / mês  [Cobrança em Dólar + IOF]", fill=(255, 90, 90), font=font_badge, anchor="lt")

# Linha 2: Clonavoz
draw.rounded_rectangle([card_comp_x + 25, card_comp_y + 130, card_comp_x + card_comp_w - 25, card_comp_y + 215], radius=16, fill=(16, 32, 22, 240), outline=(0, 225, 120, 180), width=2)
draw.text((card_comp_x + 50, card_comp_y + 148), "Clonavoz AI (100% Brasileiro):", fill=(180, 220, 195), font=font_body, anchor="lt")
draw.text((card_comp_x + 50, card_comp_y + 180), "A partir de R$ 2,49 no PIX  [Zero Assinatura]", fill=(0, 255, 140), font=font_subtitle, anchor="lt")

# --- CARD 2: DESTAQUE PIX & VALORES ---
card_pix_w = WIDTH - 140
card_pix_x = 70
card_pix_y = 905
card_pix_h = 440

# Sombra
draw.rounded_rectangle([card_pix_x + 4, card_pix_y + 4, card_pix_x + card_pix_w + 4, card_pix_y + card_pix_h + 4], radius=32, fill=(0, 0, 0, 180))
# Corpo Glass Esmeralda
draw.rounded_rectangle([card_pix_x, card_pix_y, card_pix_x + card_pix_w, card_pix_y + card_pix_h], radius=32, fill=(14, 25, 18, 245), outline=(0, 225, 120, 180), width=3)

# Badges internos
draw_auto_badge(draw, "ZERO CADASTRO • DIRETO NO PIX", card_pix_y + 50, font_badge,
                fill_bg=(0, 225, 120, 35), outline_color=(0, 225, 120, 200), text_color=(0, 255, 140))

draw.text((WIDTH//2, card_pix_y + 115), "Áudios completos a partir de:", fill=(185, 220, 200), font=font_subtitle, anchor="mm")
draw.text((WIDTH//2, card_pix_y + 195), "R$ 2,49", fill=(0, 255, 140), font=font_price, anchor="mm")
draw.text((WIDTH//2, card_pix_y + 265), "por áudio completo proporcional ao texto", fill=(160, 200, 180), font=font_body, anchor="mm")

draw.line([(card_pix_x + 60, card_pix_y + 300), (card_pix_x + card_pix_w - 60, card_pix_y + 300)], fill=(0, 225, 120, 80), width=2)

# Bullets
bullets = [
    "Sem formulários, sem cartão e sem burocracia",
    "Ouça a prévia grátis para aprovar a voz",
    "Download imediato do arquivo .MP3 na hora"
]
b_y = card_pix_y + 335
for b in bullets:
    draw.ellipse([card_pix_x + 50, b_y - 6, card_pix_x + 64, b_y + 8], fill=(0, 255, 140))
    draw.text((card_pix_x + 85, b_y), b, fill=(235, 250, 240), font=font_body, anchor="lm")
    b_y += 35

# --- CARD 3: OFERTA DE BOAS-VINDAS ---
draw_auto_badge(draw, "OFERTA: 30 ÁUDIOS POR R$ 19,90 (R$ 0,66/ÁUDIO)", 1390, font_subtitle,
                fill_bg=(24, 20, 14, 235), outline_color=(255, 180, 0, 220), text_color=(255, 210, 60), pad_x=50, pad_y=16)

# --- BOTÃO CTA DE AÇÃO PARA STORIES (Espaço ideal para a figurinha de link) ---
btn_w = WIDTH - 140
btn_x = 70
btn_y = 1470
btn_h = 130

# Botão Pulsante Laranja
draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=38, fill=(255, 75, 0), outline=(255, 160, 80), width=3)
draw.text((WIDTH//2, btn_y + 45), "EXPERIMENTAR GRÁTIS", fill=(255, 255, 255), font=font_cta_btn, anchor="mm")
draw.text((WIDTH//2, btn_y + 92), "Toque na figurinha de link ou link na bio", fill=(255, 225, 200), font=font_body, anchor="mm")

# Seta indicativa para figurinha
draw.text((WIDTH//2, 1640), "Cole a figurinha de link do Instagram aqui 👆", fill=(0, 255, 140), font=font_subtitle, anchor="mm")
draw.text((WIDTH//2, 1690), "Gere sua primeira locução em menos de 10 segundos!", fill=(180, 185, 200), font=font_body, anchor="mm")

# Footer legal
draw.text((WIDTH//2, 1840), "Clonavoz AI • Inteligência Artificial de Voz no Brasil", fill=(110, 115, 130), font=font_footer, anchor="mm")

# Salva arquivo da Capa Stories 9:16
output_stories = os.path.join(STORIES_DIR, "Capa_Stories_Clonavoz_9x16.png")
img.save(output_stories, "PNG")
print(f"Capa Stories salva com sucesso em: {output_stories}")

# Copia para Desktop, Pasta Principal de Marketing e Static
dest_paths = [
    os.path.join(MKT_BASE, "Capa_Stories_Clonavoz_9x16.png"),
    os.path.join(DESKTOP_DIR, "Capa_Stories_Clonavoz_9x16.png"),
    os.path.join(STATIC_DIR, "Capa_Stories_Clonavoz_9x16.png")
]
for d in dest_paths:
    try:
        shutil.copyfile(output_stories, d)
        print(f"Copia criada em: {d}")
    except Exception as e:
        print(f"Aviso ao copiar: {e}")

print("[OK] CAPA STORIES 9:16 GERADA COM SUCESSO!")
