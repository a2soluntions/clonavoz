import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = r"e:\A2\projetos\gerador de voz com texto"
STATIC_DIR = os.path.join(BASE_DIR, "static")
DESKTOP_DIR = r"C:\Users\User\Desktop"
CAPAS_ROOT = os.path.join(DESKTOP_DIR, "Capas_de_Alta_Conversao")
DIR_VERTICAL = os.path.join(CAPAS_ROOT, "Capas_Reels_TikTok_Shorts_9x16")
DIR_HORIZONTAL = os.path.join(CAPAS_ROOT, "Thumbnails_YouTube_16x9")

os.makedirs(DIR_VERTICAL, exist_ok=True)
os.makedirs(DIR_HORIZONTAL, exist_ok=True)

# Font loader
_font_cache = {}
def get_font(size, bold=True):
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    win_fonts = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"] if bold else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
    for f in win_fonts:
        if os.path.exists(f):
            try:
                font = ImageFont.truetype(f, size)
                _font_cache[key] = font
                return font
            except Exception:
                pass
    return ImageFont.load_default()

def get_fitted_font(draw, text, max_width, start_size, bold=True):
    size = start_size
    while size > 18:
        f = get_font(size, bold=bold)
        bbox = draw.textbbox((0, 0), text, font=f)
        if (bbox[2] - bbox[0]) <= max_width:
            return f
        size -= 2
    return get_font(18, bold=bold)

def draw_text_with_shadow(draw, pos, text, font, fill, shadow_fill=(0, 0, 0, 240), offset=(4, 5), anchor="mm"):
    x, y = pos
    draw.text((x + offset[0], y + offset[1]), text, fill=shadow_fill, font=font, anchor=anchor)
    draw.text((x, y), text, fill=fill, font=font, anchor=anchor)

def draw_badge(draw, text, center_x, center_y, font, bg_fill, border_color, text_color, pad_x=40, pad_y=16):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    w = tw + pad_x * 2
    h = th + pad_y * 2
    left = center_x - w // 2
    top = center_y - h // 2
    draw.rounded_rectangle([left, top, left + w, top + h], radius=h//2, fill=bg_fill, outline=border_color, width=3)
    draw.text((center_x, center_y), text, fill=text_color, font=font, anchor="mm")

# Load logo
logo_path = os.path.join(STATIC_DIR, "logo_perfil_instagram.png")
if os.path.exists(logo_path):
    logo_base = Image.open(logo_path).convert("RGBA")
else:
    logo_base = Image.new("RGBA", (300, 300), (255, 85, 0, 255))

# ==============================================================================
# 1. GERAR CAPAS VERTICAIS (1080 x 1920) - REELS / TIKTOK / SHORTS
# ==============================================================================
def create_vertical_bg(glow_color=(255, 75, 0, 50)):
    w, h = 1080, 1920
    img = Image.new("RGBA", (w, h), (10, 10, 14, 255))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.ellipse([w//2 - 500, 750 - 500, w//2 + 500, 750 + 500], fill=glow_color)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.alpha_composite(img, glow)
    return img

def render_vertical_cover_1():
    # Comercial: Chega de pagar em dólar
    img = create_vertical_bg((255, 60, 20, 55))
    draw = ImageDraw.Draw(img)

    draw_badge(draw, "ALERTA DE ECONOMIA", 540, 220, get_font(34, True), (40, 15, 15), (255, 60, 60), (255, 100, 100), 50, 18)
    
    draw_text_with_shadow(draw, (540, 380), "CHEGA DE", get_font(80, True), (255, 255, 255))
    draw_text_with_shadow(draw, (540, 480), "PAGAR EM", get_font(96, True), (255, 70, 70))
    draw_text_with_shadow(draw, (540, 590), "DÓLAR!", get_font(110, True), (255, 220, 0))

    # Center Visual Box
    draw.rounded_rectangle([90, 720, 990, 1260], radius=36, fill=(18, 18, 24, 240), outline=(255, 85, 0, 180), width=3)
    
    lw = 240
    lr = logo_base.resize((lw, lw), Image.Resampling.LANCZOS)
    img.paste(lr, (540 - lw//2, 760), lr)
    draw = ImageDraw.Draw(img)

    draw_text_with_shadow(draw, (540, 1060), "CLONAVOZ AI", get_font(68, True), (255, 255, 255))
    draw.text((540, 1140), "A Voz Neural 100% Brasileira", fill=(255, 125, 30), font=get_font(42, True), anchor="mm")
    draw.text((540, 1205), "Sem Mensalidades no Cartão", fill=(200, 200, 215), font=get_font(34, False), anchor="mm")

    # Big CTA Offer
    draw.rounded_rectangle([90, 1340, 990, 1580], radius=34, fill=(16, 36, 22, 240), outline=(0, 220, 110, 200), width=3)
    draw.text((540, 1400), "RECARREGUE NO PIX", fill=(0, 255, 130), font=get_font(38, True), anchor="mm")
    draw_text_with_shadow(draw, (540, 1485), "A PARTIR DE R$ 9,90", get_font(58, True), (255, 255, 255))

    draw_text_with_shadow(draw, (540, 1680), "www.clonavoz.com.br", get_font(52, True), (255, 140, 40))
    draw.text((540, 1760), "Toque para Assistir!", fill=(220, 220, 230), font=get_font(34, True), anchor="mm")

    dest = os.path.join(DIR_VERTICAL, "capa_1_comercial_chega_de_pagar_em_dolar.png")
    img.convert("RGB").save(dest, quality=95)
    print("Salvo:", dest)

def render_vertical_cover_2():
    # Tutorial Canal Dark em 60s
    img = create_vertical_bg((180, 60, 255, 50))
    draw = ImageDraw.Draw(img)

    draw_badge(draw, "TUTORIAL SECRETO", 540, 220, get_font(34, True), (30, 15, 45), (180, 80, 255), (210, 150, 255), 50, 18)

    draw_text_with_shadow(draw, (540, 360), "COMO CRIAR UM", get_font(72, True), (255, 255, 255))
    draw_text_with_shadow(draw, (540, 460), "CANAL DARK", get_font(104, True), (255, 95, 20))
    draw_text_with_shadow(draw, (540, 565), "EM 60 SEGUNDOS!", get_font(84, True), (255, 255, 0))

    # Visual checklist
    draw.rounded_rectangle([90, 680, 990, 1280], radius=36, fill=(20, 18, 28, 240), outline=(180, 80, 255, 180), width=3)
    
    steps = [
        ("1. ROTEIRO:", "Crie no ChatGPT em 10s", (0, 230, 130)),
        ("2. VOZ NEURAL:", "Narre no Clonavoz em 2s", (255, 120, 30)),
        ("3. DOWNLOAD:", "Baixe o MP3 direto", (80, 190, 255)),
        ("4. VÍDEO PRONTO:", "Junte tudo no CapCut", (255, 100, 160))
    ]
    y_step = 760
    for title_s, desc_s, col in steps:
        draw.ellipse([140, y_step + 10, 164, y_step + 34], fill=col)
        draw.text((190, y_step + 22), title_s, fill=col, font=get_font(42, True), anchor="lm")
        draw.text((190, y_step + 68), desc_s, fill=(210, 210, 220), font=get_font(34, False), anchor="lm")
        y_step += 125

    draw_badge(draw, "SEM MICROFONE • SEM APARECER", 540, 1380, get_font(38, True), (35, 20, 15), (255, 100, 20), (255, 160, 60), 55, 20)

    draw.rounded_rectangle([100, 1490, 980, 1640], radius=34, fill=(255, 75, 0), outline=(255, 160, 90), width=3)
    draw_text_with_shadow(draw, (540, 1565), "ASSISTA O PASSO A PASSO", get_font(46, True), (255, 255, 255))

    draw_text_with_shadow(draw, (540, 1740), "www.clonavoz.com.br", get_font(50, True), (255, 140, 40))

    dest = os.path.join(DIR_VERTICAL, "capa_2_canal_dark_passo_a_passo_60s.png")
    img.convert("RGB").save(dest, quality=95)
    print("Salvo:", dest)

def render_vertical_cover_3():
    # 3 IAs Secretas
    img = create_vertical_bg((0, 150, 255, 45))
    draw = ImageDraw.Draw(img)

    draw_badge(draw, "PARECEM ILEGAIS DE TÃO BOAS!", 540, 220, get_font(34, True), (15, 30, 45), (0, 170, 255), (100, 210, 255), 50, 18)

    draw_text_with_shadow(draw, (540, 360), "3 SITES DE IA", get_font(92, True), (255, 255, 255))
    draw_text_with_shadow(draw, (540, 470), "QUE VOCÊ PRECISA", get_font(76, True), (255, 105, 20))
    draw_text_with_shadow(draw, (540, 580), "CONHECER HOJE!", get_font(86, True), (0, 255, 140))

    draw.rounded_rectangle([90, 690, 990, 1310], radius=36, fill=(18, 20, 28, 240), outline=(0, 170, 255, 160), width=3)

    items = [
        ("1. CHATGPT", "Roteiros e Histórias Virais", (0, 230, 130)),
        ("2. CAPCUT", "Edição Automática Grátis", (80, 190, 255)),
        ("3. CLONAVOZ", "Voz Humana Brasileira no PIX", (255, 120, 30))
    ]
    y_it = 770
    for tit, dsc, c in items:
        draw.rounded_rectangle([130, y_it, 950, y_it + 140], radius=24, fill=(12, 14, 20), outline=c, width=2)
        draw.text((170, y_it + 45), tit, fill=c, font=get_font(46, True), anchor="lm")
        draw.text((170, y_it + 98), dsc, fill=(210, 210, 225), font=get_font(34, False), anchor="lm")
        y_it += 180

    draw.rounded_rectangle([100, 1420, 980, 1570], radius=34, fill=(255, 75, 0), outline=(255, 160, 90), width=3)
    draw_text_with_shadow(draw, (540, 1495), "VEJA COMO USAR AGORA", get_font(46, True), (255, 255, 255))

    draw_text_with_shadow(draw, (540, 1680), "www.clonavoz.com.br", get_font(52, True), (255, 140, 40))
    draw.text((540, 1750), "@clonavozoficial", fill=(180, 180, 190), font=get_font(36, False), anchor="mm")

    dest = os.path.join(DIR_VERTICAL, "capa_3_tres_ias_secretas_para_videos.png")
    img.convert("RGB").save(dest, quality=95)
    print("Salvo:", dest)

def render_vertical_cover_4():
    # Teste Cego: Humano vs IA
    img = create_vertical_bg((255, 40, 20, 50))
    draw = ImageDraw.Draw(img)

    draw_badge(draw, "DESAFIO DE PERCEPÇÃO", 540, 220, get_font(34, True), (40, 15, 15), (255, 60, 60), (255, 100, 100), 50, 18)

    draw_text_with_shadow(draw, (540, 370), "HUMANO OU", get_font(92, True), (255, 255, 255))
    draw_text_with_shadow(draw, (540, 480), "INTELIGÊNCIA", get_font(92, True), (255, 100, 20))
    draw_text_with_shadow(draw, (540, 590), "ARTIFICIAL?", get_font(96, True), (255, 225, 0))

    # Big 2-Card Duel Box
    draw.rounded_rectangle([90, 710, 520, 1180], radius=32, fill=(18, 22, 32, 240), outline=(0, 160, 255), width=3)
    draw.text((305, 780), "VOZ 1", fill=(80, 190, 255), font=get_font(56, True), anchor="mm")
    draw.text((305, 930), "?", fill=(80, 190, 255), font=get_font(120, True), anchor="mm")
    draw.text((305, 1090), "Humano?", fill=(200, 200, 215), font=get_font(36, True), anchor="mm")

    draw.rounded_rectangle([560, 710, 990, 1180], radius=32, fill=(32, 20, 16, 240), outline=(255, 120, 20), width=3)
    draw.text((775, 780), "VOZ 2", fill=(255, 140, 40), font=get_font(56, True), anchor="mm")
    draw.text((775, 930), "?", fill=(255, 140, 40), font=get_font(120, True), anchor="mm")
    draw.text((775, 1090), "Robô?", fill=(200, 200, 215), font=get_font(36, True), anchor="mm")

    draw_text_with_shadow(draw, (540, 1280), "99% DAS PESSOAS ERRAM!", get_font(48, True), (255, 70, 70))
    
    draw.rounded_rectangle([100, 1370, 980, 1520], radius=34, fill=(0, 220, 120), outline=(255, 255, 255), width=3)
    draw_text_with_shadow(draw, (540, 1445), "OUÇA E COMENTE SEU PALPITE!", get_font(42, True), (10, 30, 15))

    draw_text_with_shadow(draw, (540, 1650), "www.clonavoz.com.br", get_font(52, True), (255, 140, 40))

    dest = os.path.join(DIR_VERTICAL, "capa_4_desafio_humano_ou_ia_teste_cego.png")
    img.convert("RGB").save(dest, quality=95)
    print("Salvo:", dest)


# ==============================================================================
# 2. GERAR THUMBNAILS HORIZONTAIS (1280 x 720) - YOUTUBE OFICIAL (16:9)
# ==============================================================================
def create_horizontal_bg(glow_color=(255, 75, 0, 55)):
    w, h = 1280, 720
    img = Image.new("RGBA", (w, h), (10, 10, 14, 255))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.ellipse([850 - 350, 360 - 350, 850 + 350, 360 + 350], fill=glow_color)
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.alpha_composite(img, glow)
    return img

def render_horizontal_thumb_1():
    # Thumb YouTube 1: Chega de Pagar em Dólar
    img = create_horizontal_bg((255, 60, 20, 60))
    draw = ImageDraw.Draw(img)

    draw_badge(draw, "100% BRASILEIRO • NO PIX", 260, 80, get_font(24, True), (35, 18, 18), (255, 60, 60), (255, 100, 100), 35, 12)

    draw_text_with_shadow(draw, (50, 180), "CHEGA DE", get_font(64, True), (255, 255, 255), anchor="lm")
    draw_text_with_shadow(draw, (50, 260), "PAGAR EM", get_font(78, True), (255, 75, 75), anchor="lm")
    draw_text_with_shadow(draw, (50, 350), "DÓLAR!", get_font(90, True), (255, 220, 0), anchor="lm")

    draw.rounded_rectangle([50, 440, 620, 620], radius=24, fill=(18, 18, 24), outline=(255, 85, 0), width=2)
    draw.text((80, 485), "• Sem Cartão Internacional", fill=(225, 225, 225), font=get_font(28, True), anchor="lm")
    draw.text((80, 535), "• Sem Mensalidades Abusivas", fill=(225, 225, 225), font=get_font(28, True), anchor="lm")
    draw.text((80, 580), "• Recarga a Partir de R$ 9,90", fill=(0, 240, 130), font=get_font(30, True), anchor="lm")

    # Right side 3D Squircle Logo Card
    draw.rounded_rectangle([720, 90, 1220, 630], radius=36, fill=(16, 16, 22), outline=(255, 85, 0), width=3)
    lw = 240
    lr = logo_base.resize((lw, lw), Image.Resampling.LANCZOS)
    img.paste(lr, (970 - lw//2, 140), lr)
    draw = ImageDraw.Draw(img)

    draw_text_with_shadow(draw, (970, 430), "CLONAVOZ AI", get_font(48, True), (255, 255, 255))
    draw.text((970, 495), "Vozes Neurais Realistas", fill=(255, 125, 30), font=get_font(30, True), anchor="mm")
    draw.text((970, 560), "www.clonavoz.com.br", fill=(200, 200, 215), font=get_font(28, True), anchor="mm")

    dest = os.path.join(DIR_HORIZONTAL, "thumb_1_comercial_chega_de_pagar_em_dolar.png")
    img.convert("RGB").save(dest, quality=95)
    print("Salvo:", dest)

def render_horizontal_thumb_2():
    # Thumb YouTube 2: Canal Dark em 60s
    img = create_horizontal_bg((180, 60, 255, 55))
    draw = ImageDraw.Draw(img)

    draw_badge(draw, "PASSO A PASSO COMPLETO", 280, 80, get_font(24, True), (30, 15, 45), (180, 80, 255), (210, 150, 255), 35, 12)

    draw_text_with_shadow(draw, (50, 180), "COMO CRIAR UM", get_font(58, True), (255, 255, 255), anchor="lm")
    draw_text_with_shadow(draw, (50, 265), "CANAL DARK", get_font(84, True), (255, 95, 20), anchor="lm")
    draw_text_with_shadow(draw, (50, 355), "EM 60 SEGUNDOS!", get_font(68, True), (255, 225, 0), anchor="lm")

    draw.rounded_rectangle([50, 440, 640, 620], radius=24, fill=(20, 18, 28), outline=(180, 80, 255), width=2)
    draw.text((80, 490), "• Sem Usar Microfone", fill=(225, 225, 225), font=get_font(28, True), anchor="lm")
    draw.text((80, 540), "• Sem Mostrar o Rosto", fill=(255, 140, 40), font=get_font(30, True), anchor="lm")
    draw.text((80, 585), "• 100% no Piloto Automático", fill=(0, 230, 130), font=get_font(28, True), anchor="lm")

    # Right side Visual Showcase
    draw.rounded_rectangle([720, 90, 1220, 630], radius=36, fill=(18, 18, 26), outline=(0, 200, 130), width=3)
    draw_text_with_shadow(draw, (970, 170), "4 PASSOS SIMPLES", get_font(38, True), (0, 230, 130))

    items = ["1. ChatGPT (Roteiro)", "2. Clonavoz (Voz IA)", "3. Download MP3", "4. CapCut (Vídeo)"]
    y_it = 250
    for it in items:
        draw.rounded_rectangle([760, y_it, 1180, y_it + 65], radius=16, fill=(26, 26, 36), outline=(255, 255, 255, 60), width=1)
        draw.text((790, y_it + 32), it, fill=(255, 255, 255), font=get_font(26, True), anchor="lm")
        y_it += 85

    dest = os.path.join(DIR_HORIZONTAL, "thumb_2_canal_dark_passo_a_passo_60s.png")
    img.convert("RGB").save(dest, quality=95)
    print("Salvo:", dest)

def render_horizontal_thumb_3():
    # Thumb YouTube 3: 3 IAs Secretas
    img = create_horizontal_bg((0, 160, 255, 55))
    draw = ImageDraw.Draw(img)

    draw_badge(draw, "SEGREDO DOS CRIADORES", 260, 80, get_font(24, True), (15, 30, 45), (0, 170, 255), (100, 210, 255), 35, 12)

    draw_text_with_shadow(draw, (50, 180), "3 SITES DE IA", get_font(72, True), (255, 255, 255), anchor="lm")
    draw_text_with_shadow(draw, (50, 270), "QUE PARECEM", get_font(68, True), (255, 105, 20), anchor="lm")
    draw_text_with_shadow(draw, (50, 360), "ILEGAIS!", get_font(84, True), (0, 255, 140), anchor="lm")

    draw.rounded_rectangle([50, 450, 620, 620], radius=24, fill=(18, 20, 28), outline=(0, 170, 255), width=2)
    draw.text((80, 500), "Crie vídeos virais em segundos", fill=(225, 225, 225), font=get_font(28, True), anchor="lm")
    draw.text((80, 560), "Mesmo começando do absoluto zero!", fill=(255, 125, 30), font=get_font(26, True), anchor="lm")

    # Right side 3 Badges
    draw.rounded_rectangle([720, 90, 1220, 630], radius=36, fill=(16, 18, 26), outline=(0, 170, 255), width=3)
    
    ias = [
        ("1. CHATGPT", "Roteiros Automáticos", (0, 230, 130)),
        ("2. CAPCUT", "Edição Grátis", (80, 190, 255)),
        ("3. CLONAVOZ", "Voz Humana no PIX", (255, 120, 30))
    ]
    y_ia = 160
    for tit, sub, c in ias:
        draw.rounded_rectangle([760, y_ia, 1180, y_ia + 120], radius=20, fill=(22, 24, 34), outline=c, width=2)
        draw.text((790, y_ia + 42), tit, fill=c, font=get_font(34, True), anchor="lm")
        draw.text((790, y_ia + 85), sub, fill=(200, 200, 215), font=get_font(24, False), anchor="lm")
        y_ia += 145

    dest = os.path.join(DIR_HORIZONTAL, "thumb_3_tres_ias_secretas_para_videos.png")
    img.convert("RGB").save(dest, quality=95)
    print("Salvo:", dest)

def render_horizontal_thumb_4():
    # Thumb YouTube 4: Teste Cego Humano vs IA
    img = create_horizontal_bg((255, 40, 20, 55))
    draw = ImageDraw.Draw(img)

    draw_badge(draw, "DESAFIO DE ÁUDIO", 220, 80, get_font(24, True), (40, 15, 15), (255, 60, 60), (255, 100, 100), 35, 12)

    draw_text_with_shadow(draw, (50, 180), "HUMANO OU", get_font(72, True), (255, 255, 255), anchor="lm")
    draw_text_with_shadow(draw, (50, 265), "INTELIGÊNCIA", get_font(72, True), (255, 100, 20), anchor="lm")
    draw_text_with_shadow(draw, (50, 355), "ARTIFICIAL?", get_font(78, True), (255, 225, 0), anchor="lm")

    draw.rounded_rectangle([50, 450, 620, 620], radius=24, fill=(24, 18, 22), outline=(255, 70, 70), width=2)
    draw.text((80, 500), "99% das Pessoas Erram!", fill=(255, 90, 90), font=get_font(32, True), anchor="lm")
    draw.text((80, 560), "Você consegue adivinhar a voz real?", fill=(225, 225, 225), font=get_font(24, True), anchor="lm")

    # Right side Versus Duel Boxes
    draw.rounded_rectangle([720, 130, 930, 590], radius=28, fill=(18, 22, 32), outline=(0, 160, 255), width=3)
    draw.text((825, 200), "VOZ 1", fill=(80, 190, 255), font=get_font(38, True), anchor="mm")
    draw.text((825, 360), "?", fill=(80, 190, 255), font=get_font(84, True), anchor="mm")
    draw.text((825, 510), "Humano?", fill=(200, 200, 215), font=get_font(26, True), anchor="mm")

    draw.rounded_rectangle([970, 130, 1180, 590], radius=28, fill=(32, 20, 16), outline=(255, 120, 20), width=3)
    draw.text((1075, 200), "VOZ 2", fill=(255, 140, 40), font=get_font(38, True), anchor="mm")
    draw.text((1075, 360), "?", fill=(255, 140, 40), font=get_font(84, True), anchor="mm")
    draw.text((1075, 510), "Robô?", fill=(200, 200, 215), font=get_font(26, True), anchor="mm")

    dest = os.path.join(DIR_HORIZONTAL, "thumb_4_desafio_humano_ou_ia_teste_cego.png")
    img.convert("RGB").save(dest, quality=95)
    print("Salvo:", dest)


if __name__ == "__main__":
    print("--- [1/2] Gerando Capas Verticais (9:16) para Reels, TikTok e Shorts... ---")
    render_vertical_cover_1()
    render_vertical_cover_2()
    render_vertical_cover_3()
    render_vertical_cover_4()

    print("\n--- [2/2] Gerando Thumbnails Horizontais (16:9) para o YouTube... ---")
    render_horizontal_thumb_1()
    render_horizontal_thumb_2()
    render_horizontal_thumb_3()
    render_horizontal_thumb_4()

    print("\n*******************************************************************")
    print("TODAS AS 8 CAPAS FORAM GERADAS COM SUCESSO EM: " + CAPAS_ROOT)
    print("*******************************************************************")
