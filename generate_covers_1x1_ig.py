import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = r"e:\A2\projetos\gerador de voz com texto"
STATIC_DIR = os.path.join(BASE_DIR, "static")
MKT_ROOT = r"E:\A2\Projetos marcketing\clonavoz"

DIR_CAPAS_1X1 = os.path.join(MKT_ROOT, "Capas_de_Alta_Conversao", "Capas_Instagram_1x1")
DIR_IG_1X1 = os.path.join(MKT_ROOT, "Videos_Instagram_1x1")
DIR_IG_ALT = os.path.join(MKT_ROOT, "instagran")

os.makedirs(DIR_CAPAS_1X1, exist_ok=True)
os.makedirs(DIR_IG_1X1, exist_ok=True)
os.makedirs(DIR_IG_ALT, exist_ok=True)

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
    while size > 16:
        f = get_font(size, bold=bold)
        bbox = draw.textbbox((0, 0), text, font=f)
        if (bbox[2] - bbox[0]) <= max_width:
            return f
        size -= 2
    return get_font(16, bold=bold)

def draw_fitted_shadow(draw, pos, text, max_w, start_size, fill, bold=True, anchor="mm"):
    f = get_fitted_font(draw, text, max_w, start_size, bold=bold)
    draw.text((pos[0]+3, pos[1]+4), text, fill=(0, 0, 0, 240), font=f, anchor=anchor)
    draw.text(pos, text, fill=fill, font=f, anchor=anchor)

def draw_auto_badge(draw, width_canvas, text, y_center, start_size, fill_bg, outline_color, text_color, pad_x=40, pad_y=14, border_width=3):
    max_w = width_canvas - 120
    font = get_fitted_font(draw, text, max_w, start_size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    box_w = tw + pad_x * 2
    box_h = th + pad_y * 2
    left = (width_canvas - box_w) // 2
    right = left + box_w
    top = y_center - box_h // 2
    bottom = top + box_h
    radius = box_h // 2
    draw.rounded_rectangle([left, top, right, bottom], radius=radius, fill=fill_bg, outline=outline_color, width=border_width)
    draw.text((width_canvas // 2, y_center), text, fill=text_color, font=font, anchor="mm")

logo_path = os.path.join(STATIC_DIR, "logo_perfil_instagram.png")
if os.path.exists(logo_path):
    logo_base = Image.open(logo_path).convert("RGBA")
else:
    logo_base = Image.new("RGBA", (300, 300), (255, 85, 0, 255))

W, H = 1080, 1080

def make_1x1_bg(glow_color):
    im = Image.new("RGBA", (W, H), (10, 10, 14, 255))
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.ellipse([W//2 - 420, H//2 - 420, W//2 + 420, H//2 + 420], fill=glow_color)
    gl = gl.filter(ImageFilter.GaussianBlur(95))
    return Image.alpha_composite(im, gl)

def save_to_all(img, filename):
    rgb = img.convert("RGB")
    for folder in [DIR_CAPAS_1X1, DIR_IG_1X1, DIR_IG_ALT]:
        path = os.path.join(folder, filename)
        rgb.save(path, quality=95)
    print("Salvo 1:1 ->", filename)

# ==============================================================================
# CAPA 1 (1:1): Comercial - Chega de Pagar em Dólar
# ==============================================================================
def make_cover_1():
    img = make_1x1_bg((255, 60, 20, 55))
    d = ImageDraw.Draw(img)

    draw_auto_badge(d, W, "ALERTA DE ECONOMIA", 95, 28, (40, 15, 15), (255, 60, 60), (255, 100, 100), 40, 12)
    
    draw_fitted_shadow(d, (540, 195), "CHEGA DE PAGAR", 940, 68, (255, 255, 255))
    draw_fitted_shadow(d, (540, 285), "EM DÓLAR!", 940, 88, (255, 220, 0))

    # Central Card with Logo
    d.rounded_rectangle([85, 365, W - 85, 755], radius=30, fill=(18, 18, 24, 240), outline=(255, 85, 0), width=3)
    lr = logo_base.resize((165, 165), Image.Resampling.LANCZOS)
    img.paste(lr, (540 - 82, 390), lr)
    d = ImageDraw.Draw(img)

    draw_fitted_shadow(d, (540, 605), "CLONAVOZ AI", 840, 56, (255, 255, 255))
    draw_fitted_shadow(d, (540, 668), "A Voz Neural 100% Brasileira", 840, 36, (255, 125, 30))
    d.text((540, 718), "Sem Mensalidades no Cartão", fill=(200, 200, 215), font=get_font(28, False), anchor="mm")

    # Bottom PIX CTA
    d.rounded_rectangle([85, 790, W - 85, 935], radius=28, fill=(16, 36, 22, 240), outline=(0, 220, 110), width=3)
    d.text((540, 832), "RECARGA FÁCIL NO PIX", fill=(0, 255, 130), font=get_font(30, True), anchor="mm")
    draw_fitted_shadow(d, (540, 890), "A PARTIR DE R$ 9,90", 840, 48, (255, 255, 255))

    draw_fitted_shadow(d, (540, 995), "LINK NA BIO • @clonavozoficial", 940, 34, (255, 140, 40))
    save_to_all(img, "capa-1-clonavoz-recarga-facil-pix-1x1.png")


# ==============================================================================
# CAPA 2 (1:1): Passo a Passo Canal Dark em 60s
# ==============================================================================
def make_cover_2():
    img = make_1x1_bg((180, 60, 255, 50))
    d = ImageDraw.Draw(img)

    draw_auto_badge(d, W, "TUTORIAL PASSO A PASSO", 90, 28, (30, 15, 45), (180, 80, 255), (210, 150, 255), 40, 12)

    draw_fitted_shadow(d, (540, 185), "COMO CRIAR UM", 940, 58, (255, 255, 255))
    draw_fitted_shadow(d, (540, 265), "CANAL DARK", 940, 82, (255, 95, 20))
    draw_fitted_shadow(d, (540, 345), "EM 60 SEGUNDOS!", 940, 58, (255, 230, 0))

    d.rounded_rectangle([80, 410, W - 80, 810], radius=28, fill=(20, 18, 28, 240), outline=(180, 80, 255), width=3)
    steps = [
        ("1. ROTEIRO:", "Crie no ChatGPT em 10s", (0, 230, 130)),
        ("2. VOZ NEURAL:", "Narre no Clonavoz em 2s", (255, 120, 30)),
        ("3. DOWNLOAD:", "Baixe o MP3 direto", (80, 190, 255)),
        ("4. VÍDEO PRONTO:", "Junte tudo no CapCut", (255, 100, 160))
    ]
    ys = 445
    for ts, ds, cl in steps:
        d.ellipse([125, ys + 8, 145, ys + 28], fill=cl)
        d.text((165, ys + 18), ts, fill=cl, font=get_font(34, True), anchor="lm")
        d.text((460, ys + 18), ds, fill=(215, 215, 225), font=get_font(30, False), anchor="lm")
        ys += 90

    d.rounded_rectangle([95, 845, W - 95, 950], radius=28, fill=(255, 75, 0), outline=(255, 160, 90), width=3)
    draw_fitted_shadow(d, (540, 897), "SEM MICROFONE • SEM APARECER", 820, 38, (255, 255, 255))

    draw_fitted_shadow(d, (540, 1000), "LINK NA BIO • @clonavozoficial", 940, 34, (255, 140, 40))
    save_to_all(img, "capa-2-video-canal-dark-passo-a-passo-1x1.png")


# ==============================================================================
# CAPA 3 (1:1): 3 Ferramentas Secretas de IA
# ==============================================================================
def make_cover_3():
    img = make_1x1_bg((0, 150, 255, 45))
    d = ImageDraw.Draw(img)

    draw_auto_badge(d, W, "PARECEM ILEGAIS DE TÃO BOAS!", 90, 28, (15, 30, 45), (0, 170, 255), (100, 210, 255), 40, 12)

    draw_fitted_shadow(d, (540, 185), "3 FERRAMENTAS", 940, 68, (255, 255, 255))
    draw_fitted_shadow(d, (540, 265), "QUE VOCÊ PRECISA", 940, 58, (255, 105, 20))
    draw_fitted_shadow(d, (540, 345), "CONHECER HOJE!", 940, 66, (0, 255, 140))

    items = [
        ("1. CHATGPT", "Roteiros e Histórias Virais", (0, 230, 130)),
        ("2. CAPCUT", "Edição Automática Grátis", (80, 190, 255)),
        ("3. CLONAVOZ", "Voz Humana Brasileira no PIX", (255, 120, 30))
    ]
    yi = 415
    for tit, dsc, c in items:
        d.rounded_rectangle([85, yi, W - 85, yi + 118], radius=22, fill=(16, 18, 26, 240), outline=c, width=2)
        d.text((130, yi + 38), tit, fill=c, font=get_font(38, True), anchor="lm")
        d.text((130, yi + 84), dsc, fill=(215, 215, 225), font=get_font(28, False), anchor="lm")
        yi += 135

    d.rounded_rectangle([95, 845, W - 95, 950], radius=28, fill=(255, 75, 0), outline=(255, 160, 90), width=3)
    draw_fitted_shadow(d, (540, 897), "TESTE GRÁTIS NO LINK DA BIO!", 820, 38, (255, 255, 255))

    draw_fitted_shadow(d, (540, 1000), "Siga: @clonavozoficial", 940, 34, (255, 140, 40))
    save_to_all(img, "capa-3-ias-secretas-canal-dark-1x1.png")


# ==============================================================================
# CAPA 4 (1:1): Desafio Teste Cego - Humano vs IA
# ==============================================================================
def make_cover_4():
    img = make_1x1_bg((255, 40, 20, 50))
    d = ImageDraw.Draw(img)

    draw_auto_badge(d, W, "DESAFIO DE PERCEPÇÃO SONORA", 90, 28, (40, 15, 15), (255, 60, 60), (255, 100, 100), 40, 12)

    draw_fitted_shadow(d, (540, 185), "LOCUTOR HUMANO", 940, 64, (255, 255, 255))
    draw_fitted_shadow(d, (540, 265), "OU INTELIGÊNCIA", 940, 64, (255, 100, 20))
    draw_fitted_shadow(d, (540, 345), "ARTIFICIAL?", 940, 72, (255, 225, 0))

    # 2 Duel Cards
    d.rounded_rectangle([85, 415, 515, 765], radius=28, fill=(18, 22, 32, 240), outline=(0, 160, 255), width=3)
    d.text((300, 470), "VOZ 1", fill=(80, 190, 255), font=get_font(46, True), anchor="mm")
    d.text((300, 590), "?", fill=(80, 190, 255), font=get_font(96, True), anchor="mm")
    d.text((300, 705), "Humano?", fill=(205, 205, 215), font=get_font(32, True), anchor="mm")

    d.rounded_rectangle([565, 415, 995, 765], radius=28, fill=(32, 20, 16, 240), outline=(255, 120, 20), width=3)
    d.text((780, 470), "VOZ 2", fill=(255, 140, 40), font=get_font(46, True), anchor="mm")
    d.text((780, 590), "?", fill=(255, 140, 40), font=get_font(96, True), anchor="mm")
    d.text((780, 705), "Robô?", fill=(205, 205, 215), font=get_font(32, True), anchor="mm")

    draw_fitted_shadow(d, (540, 815), "99% DAS PESSOAS ERRAM!", 900, 40, (255, 80, 80))

    d.rounded_rectangle([95, 865, W - 95, 960], radius=28, fill=(0, 220, 120), outline=(255, 255, 255), width=3)
    d.text((540, 912), "OUÇA E COMENTE: 1 OU 2?", fill=(10, 30, 15), font=get_font(38, True), anchor="mm")

    draw_fitted_shadow(d, (540, 1005), "LINK NA BIO • @clonavozoficial", 940, 34, (255, 140, 40))
    save_to_all(img, "capa-4-teste-cego-voz-humana-vs-ia-1x1.png")


if __name__ == "__main__":
    make_cover_1()
    make_cover_2()
    make_cover_3()
    make_cover_4()
    print("\n=== TODAS AS 4 CAPAS 1:1 (1080x1080) DO INSTAGRAM GERADAS COM SUCESSO! ===")
