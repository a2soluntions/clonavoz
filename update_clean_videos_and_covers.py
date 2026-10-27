import os
import sys
import math
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf
import tts_engine

BASE_DIR = r"e:\A2\projetos\gerador de voz com texto"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
STATIC_DIR = os.path.join(BASE_DIR, "static")
SCRATCH_ROOT = os.path.join(BASE_DIR, "scratch_clean_all")

MKT_ROOT = r"E:\A2\Projetos marcketing\clonavoz"
DIR_INSTAGRAM = os.path.join(MKT_ROOT, "1_INSTAGRAM")
DIR_TIKTOK = os.path.join(MKT_ROOT, "2_TIKTOK")
DIR_YOUTUBE = os.path.join(MKT_ROOT, "3_YOUTUBE")

os.makedirs(SCRATCH_ROOT, exist_ok=True)
os.makedirs(os.path.join(DIR_INSTAGRAM, "Videos_1x1"), exist_ok=True)
os.makedirs(os.path.join(DIR_INSTAGRAM, "Capas_1x1"), exist_ok=True)
os.makedirs(os.path.join(DIR_TIKTOK, "Videos_9x16"), exist_ok=True)
os.makedirs(os.path.join(DIR_TIKTOK, "Capas_9x16"), exist_ok=True)
os.makedirs(os.path.join(DIR_YOUTUBE, "Videos_Shorts_9x16"), exist_ok=True)
os.makedirs(os.path.join(DIR_YOUTUBE, "Thumbnails_16x9"), exist_ok=True)

FPS = 30

_font_cache = {}
def get_font(size, bold=False):
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

def draw_fitted_text(draw, pos, text, max_width, start_size, fill, bold=True, anchor="mm"):
    font = get_fitted_font(draw, text, max_width, start_size, bold=bold)
    draw.text(pos, text, fill=fill, font=font, anchor=anchor)

def draw_fitted_shadow(draw, pos, text, max_w, start_size, fill, bold=True, anchor="mm"):
    f = get_fitted_font(draw, text, max_w, start_size, bold=bold)
    draw.text((pos[0]+3, pos[1]+4), text, fill=(0, 0, 0, 240), font=f, anchor=anchor)
    draw.text(pos, text, fill=fill, font=f, anchor=anchor)

def draw_auto_badge(draw, width_canvas, text, y_center, start_size, fill_bg, outline_color, text_color, pad_x=42, pad_y=15, border_width=2):
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

def make_base_bg(w, h, glow_color=(255, 75, 0, 42)):
    img = Image.new("RGBA", (w, h), (10, 10, 14, 255))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    r = int(min(w, h) * 0.44)
    cx, cy = w // 2, int(h * 0.46)
    g_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=glow_color)
    glow = glow.filter(ImageFilter.GaussianBlur(95))
    img = Image.alpha_composite(img, glow)
    return img.convert("RGB")

def encode_video(w, h, draw_fn, wav_path, bgm_path, output_paths):
    info = sf.info(wav_path)
    dur = info.duration
    total_sec = math.ceil(dur + 1.2)
    total_frames = int(total_sec * FPS)

    frames_dir = os.path.join(SCRATCH_ROOT, "frames")
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir, exist_ok=True)

    first_out = output_paths[0]
    print(f"Renderizando {os.path.basename(first_out)} ({w}x{h}, {total_frames} frames)...")
    for i in range(total_frames):
        t = i / FPS
        im = draw_fn(t, i)
        im.save(os.path.join(frames_dir, f"f_{i:05d}.jpg"), quality=92)

    temp_vid = os.path.join(SCRATCH_ROOT, "temp_v.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "f_%05d.jpg"),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        temp_vid
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    temp_aud = os.path.join(SCRATCH_ROOT, "temp_a.m4a")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", wav_path, "-i", bgm_path,
        "-filter_complex",
        "[0:a]volume=1.35[v];[1:a]volume=0.15,aloop=loop=-1:size=2e+09[bgm];[v][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "[aout]", "-c:a", "aac", "-b:a", "192k",
        temp_aud
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", temp_vid, "-i", temp_aud,
        "-c:v", "copy", "-c:a", "aac", "-shortest",
        first_out
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    for extra in output_paths[1:]:
        shutil.copyfile(first_out, extra)
    print(f"OK -> Salvo em: {output_paths}")


# ==============================================================================
# 1. GERAR LOCUÇÕES LIMPAS (ZERO LINKS, ZERO @ENDEREÇOS, APENAS DESCRIÇÃO)
# ==============================================================================
print("--- [1/4] Sintetizando Locuções Limpas (Sem Links e Sem Endereços)... ---")

script_comercial = (
    "Cansado de pagar assinaturas em dólar no cartão internacional para ter voz de inteligência artificial? "
    "Conheça o Clonavoz! A inteligência artificial de voz feita para o Brasil, com sotaque cem por cento natural. "
    "Perfeito para seus canais Dark, vídeos curtos, e anúncios de alta conversão. "
    "Crie áudios profissionais em segundos. "
    "Sem assinaturas fixas. Recarregue no Pícs a partir de apenas nove reais e noventa. "
    "Confira todas as informações na descrição e faça seu teste grátis hoje mesmo!"
)
wav_comercial = tts_engine.synthesize_text(script_comercial, voice_key="faber", speed=0.98)["file_path"]

script_passo = (
    "Como criar um canal Dark lucrativo em menos de um minuto. "
    "Primeiro passo: peça um roteiro de curiosidades para o ChatGPT. "
    "Segundo passo: cole o texto no Clonavoz e escolha a voz neural brasileira. "
    "Terceiro passo: baixe o áudio em alta definição no seu computador ou celular. "
    "Quarto passo: junte com vídeos de fundo no CapCut e pronto! "
    "Sem microfone e sem mostrar o rosto. Confira a descrição e faça seu teste grátis agora mesmo!"
)
wav_passo = tts_engine.synthesize_text(script_passo, voice_key="dii", speed=1.0)["file_path"]

script_3ias = (
    "Três ferramentas de inteligência artificial que você precisa conhecer hoje. "
    "Número um: ChatGPT, para criar roteiros e histórias em segundos. "
    "Número dois: CapCut, para editar seus vídeos de graça no celular. "
    "E número três: Clonavoz! A inteligência artificial brasileira que narra seus vídeos com voz humana sem pagar em dólar. "
    "Recarregue no Pícs por apenas nove reais e noventa. "
    "Confira os detalhes na descrição e faça seu teste grátis!"
)
wav_3ias = tts_engine.synthesize_text(script_3ias, voice_key="faber", speed=0.98)["file_path"]

script_teste = (
    "Teste de percepção sonora: você consegue descobrir qual dessas vozes é um locutor humano e qual é uma inteligência artificial? "
    "Ouça a voz número um... "
    "No meio da escuridão, apenas os mais corajosos encontram a verdade. "
    "Agora, ouça a voz número dois... "
    "O universo guarda mistérios que a mente humana ainda não consegue explicar. "
    "E aí, qual é a inteligência artificial? A número um ou a número dois? "
    "Deixe seu palpite nos comentários! "
    "O segredo? As duas foram geradas no Clonavoz! "
    "Confira a descrição e faça seu teste grátis agora mesmo!"
)
wav_teste = tts_engine.synthesize_text(script_teste, voice_key="faber", speed=0.96)["file_path"]


# ==============================================================================
# 2. GERAR TODAS AS 12 CAPAS SEM NENHUM ENDEREÇO (@) E SEM NENHUM LINK (WWW)
# ==============================================================================
def generate_all_clean_covers():
    print("\n--- [2/4] Gerando Capas 1:1, 9:16 e 16:9 (ZERO Endereços e ZERO Links)... ---")

    # --- A) CAPAS 1:1 (1080x1080) PARA 1_INSTAGRAM\Capas_1x1 ---
    W, H = 1080, 1080
    def make_1x1_bg(gcol):
        im = Image.new("RGBA", (W, H), (10, 10, 14, 255))
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gl)
        gd.ellipse([W//2 - 420, H//2 - 420, W//2 + 420, H//2 + 420], fill=gcol)
        gl = gl.filter(ImageFilter.GaussianBlur(95))
        return Image.alpha_composite(im, gl)

    # 1:1 Cover 1
    img = make_1x1_bg((255, 60, 20, 55))
    d = ImageDraw.Draw(img)
    draw_auto_badge(d, W, "ALERTA DE ECONOMIA", 95, 28, (40, 15, 15), (255, 60, 60), (255, 100, 100), 40, 12)
    draw_fitted_shadow(d, (540, 195), "CHEGA DE PAGAR", 940, 68, (255, 255, 255))
    draw_fitted_shadow(d, (540, 285), "EM DÓLAR!", 940, 88, (255, 220, 0))
    d.rounded_rectangle([85, 365, W - 85, 755], radius=30, fill=(18, 18, 24, 240), outline=(255, 85, 0), width=3)
    lr = logo_base.resize((165, 165), Image.Resampling.LANCZOS)
    img.paste(lr, (540 - 82, 390), lr)
    d = ImageDraw.Draw(img)
    draw_fitted_shadow(d, (540, 605), "CLONAVOZ AI", 840, 56, (255, 255, 255))
    draw_fitted_shadow(d, (540, 668), "A Voz Neural 100% Brasileira", 840, 36, (255, 125, 30))
    d.text((540, 718), "Sem Mensalidades no Cartão", fill=(200, 200, 215), font=get_font(28, False), anchor="mm")
    d.rounded_rectangle([85, 790, W - 85, 935], radius=28, fill=(16, 36, 22, 240), outline=(0, 220, 110), width=3)
    d.text((540, 832), "RECARGA FÁCIL NO PIX", fill=(0, 255, 130), font=get_font(30, True), anchor="mm")
    draw_fitted_shadow(d, (540, 890), "A PARTIR DE R$ 9,90", 840, 48, (255, 255, 255))
    draw_fitted_shadow(d, (540, 995), "LOCUÇÃO PROFISSIONAL EM SEGUNDOS", 940, 32, (255, 140, 40))
    img.convert("RGB").save(os.path.join(DIR_INSTAGRAM, "Capas_1x1", "capa-1-clonavoz-recarga-facil-pix-1x1.png"), quality=95)

    # 1:1 Cover 2
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
    draw_fitted_shadow(d, (540, 1000), "100% NO PILOTO AUTOMÁTICO", 940, 32, (255, 140, 40))
    img.convert("RGB").save(os.path.join(DIR_INSTAGRAM, "Capas_1x1", "capa-2-video-canal-dark-passo-a-passo-1x1.png"), quality=95)

    # 1:1 Cover 3
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
    draw_fitted_shadow(d, (540, 897), "CRIE VÍDEOS EM SEGUNDOS!", 820, 38, (255, 255, 255))
    draw_fitted_shadow(d, (540, 1000), "CLONAVOZ AI • VOZ NEURAL", 940, 32, (255, 140, 40))
    img.convert("RGB").save(os.path.join(DIR_INSTAGRAM, "Capas_1x1", "capa-3-ias-secretas-canal-dark-1x1.png"), quality=95)

    # 1:1 Cover 4
    img = make_1x1_bg((255, 40, 20, 50))
    d = ImageDraw.Draw(img)
    draw_auto_badge(d, W, "DESAFIO DE PERCEPÇÃO SONORA", 90, 28, (40, 15, 15), (255, 60, 60), (255, 100, 100), 40, 12)
    draw_fitted_shadow(d, (540, 185), "LOCUTOR HUMANO", 940, 64, (255, 255, 255))
    draw_fitted_shadow(d, (540, 265), "OU INTELIGÊNCIA", 940, 64, (255, 100, 20))
    draw_fitted_shadow(d, (540, 345), "ARTIFICIAL?", 940, 72, (255, 225, 0))
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
    draw_fitted_shadow(d, (540, 1005), "CLONAVOZ AI • VOZ NEURAL", 940, 32, (255, 140, 40))
    img.convert("RGB").save(os.path.join(DIR_INSTAGRAM, "Capas_1x1", "capa-4-teste-cego-voz-humana-vs-ia-1x1.png"), quality=95)

    # --- B) CAPAS 9:16 (1080x1920) PARA 2_TIKTOK\Capas_9x16 ---
    w9, h9 = 1080, 1920
    def make_vbg(gcol):
        im = Image.new("RGBA", (w9, h9), (10, 10, 14, 255))
        gl = Image.new("RGBA", (w9, h9), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gl)
        gd.ellipse([w9//2 - 500, 750 - 500, w9//2 + 500, 750 + 500], fill=gcol)
        gl = gl.filter(ImageFilter.GaussianBlur(120))
        return Image.alpha_composite(im, gl)

    def shadow_txt(dr, pos, txt, fnt, fl, anchor="mm"):
        dr.text((pos[0]+4, pos[1]+5), txt, fill=(0,0,0,240), font=fnt, anchor=anchor)
        dr.text(pos, txt, fill=fl, font=fnt, anchor=anchor)

    # 9:16 Cover 1
    im1 = make_vbg((255, 60, 20, 55))
    d1 = ImageDraw.Draw(im1)
    draw_auto_badge(d1, w9, "ALERTA DE ECONOMIA", 220, 34, (40, 15, 15), (255, 60, 60), (255, 100, 100), 50, 18)
    shadow_txt(d1, (540, 380), "CHEGA DE", get_font(80, True), (255, 255, 255))
    shadow_txt(d1, (540, 480), "PAGAR EM", get_font(96, True), (255, 70, 70))
    shadow_txt(d1, (540, 590), "DÓLAR!", get_font(110, True), (255, 220, 0))
    d1.rounded_rectangle([90, 720, 990, 1260], radius=36, fill=(18, 18, 24, 240), outline=(255, 85, 0), width=3)
    lr = logo_base.resize((240, 240), Image.Resampling.LANCZOS)
    im1.paste(lr, (540 - 120, 760), lr)
    d1 = ImageDraw.Draw(im1)
    shadow_txt(d1, (540, 1060), "CLONAVOZ AI", get_font(68, True), (255, 255, 255))
    d1.text((540, 1140), "A Voz Neural 100% Brasileira", fill=(255, 125, 30), font=get_font(42, True), anchor="mm")
    d1.text((540, 1205), "Sem Mensalidades no Cartão", fill=(200, 200, 215), font=get_font(34, False), anchor="mm")
    d1.rounded_rectangle([90, 1340, 990, 1580], radius=34, fill=(16, 36, 22, 240), outline=(0, 220, 110), width=3)
    d1.text((540, 1400), "RECARREGUE NO PIX", fill=(0, 255, 130), font=get_font(38, True), anchor="mm")
    shadow_txt(d1, (540, 1485), "A PARTIR DE R$ 9,90", get_font(58, True), (255, 255, 255))
    shadow_txt(d1, (540, 1690), "LOCUÇÃO NEURAL EM SEGUNDOS", get_font(42, True), (255, 140, 40))
    d1.text((540, 1765), "Assista Agora!", fill=(220, 220, 230), font=get_font(36, True), anchor="mm")
    im1.convert("RGB").save(os.path.join(DIR_TIKTOK, "Capas_9x16", "capa_1_comercial_chega_de_pagar_em_dolar.png"), quality=95)

    # 9:16 Cover 2
    im2 = make_vbg((180, 60, 255, 50))
    d2 = ImageDraw.Draw(im2)
    draw_auto_badge(d2, w9, "TUTORIAL SECRETO", 220, 34, (30, 15, 45), (180, 80, 255), (210, 150, 255), 50, 18)
    shadow_txt(d2, (540, 360), "COMO CRIAR UM", get_font(72, True), (255, 255, 255))
    shadow_txt(d2, (540, 460), "CANAL DARK", get_font(104, True), (255, 95, 20))
    shadow_txt(d2, (540, 565), "EM 60 SEGUNDOS!", get_font(84, True), (255, 255, 0))
    d2.rounded_rectangle([90, 680, 990, 1280], radius=36, fill=(20, 18, 28, 240), outline=(180, 80, 255), width=3)
    ys = 760
    for ts, ds, cl in steps:
        d2.ellipse([140, ys + 10, 164, ys + 34], fill=cl)
        d2.text((190, ys + 22), ts, fill=cl, font=get_font(42, True), anchor="lm")
        d2.text((190, ys + 68), ds, fill=(210, 210, 220), font=get_font(34, False), anchor="lm")
        ys += 125
    draw_auto_badge(d2, w9, "SEM MICROFONE • SEM APARECER", 1380, 36, (35, 20, 15), (255, 100, 20), (255, 160, 60), 50, 18)
    d2.rounded_rectangle([100, 1490, 980, 1630], radius=34, fill=(255, 75, 0), outline=(255, 160, 90), width=3)
    shadow_txt(d2, (540, 1560), "ASSISTA O PASSO A PASSO", get_font(44, True), (255, 255, 255))
    d2.text((540, 1730), "CLONAVOZ AI • VOZ NEURAL", fill=(255, 140, 40), font=get_font(38, True), anchor="mm")
    im2.convert("RGB").save(os.path.join(DIR_TIKTOK, "Capas_9x16", "capa_2_canal_dark_passo_a_passo_60s.png"), quality=95)

    # 9:16 Cover 3
    im3 = make_vbg((0, 150, 255, 45))
    d3 = ImageDraw.Draw(im3)
    draw_auto_badge(d3, w9, "PARECEM ILEGAIS DE TÃO BOAS!", 220, 34, (15, 30, 45), (0, 170, 255), (100, 210, 255), 50, 18)
    shadow_txt(d3, (540, 360), "3 FERRAMENTAS", get_font(88, True), (255, 255, 255))
    shadow_txt(d3, (540, 470), "QUE VOCÊ PRECISA", get_font(76, True), (255, 105, 20))
    shadow_txt(d3, (540, 580), "CONHECER HOJE!", get_font(86, True), (0, 255, 140))
    d3.rounded_rectangle([90, 690, 990, 1310], radius=36, fill=(18, 20, 28, 240), outline=(0, 170, 255), width=3)
    yi = 770
    for tit, dsc, c in items:
        d3.rounded_rectangle([130, yi, 950, yi + 140], radius=24, fill=(12, 14, 20), outline=c, width=2)
        d3.text((170, yi + 45), tit, fill=c, font=get_font(46, True), anchor="lm")
        d3.text((170, yi + 98), dsc, fill=(210, 210, 225), font=get_font(34, False), anchor="lm")
        yi += 180
    d3.rounded_rectangle([100, 1420, 980, 1570], radius=34, fill=(255, 75, 0), outline=(255, 160, 90), width=3)
    shadow_txt(d3, (540, 1495), "VEJA COMO USAR AGORA!", get_font(46, True), (255, 255, 255))
    d3.text((540, 1690), "CLONAVOZ AI • VOZ NEURAL", fill=(255, 140, 40), font=get_font(38, True), anchor="mm")
    im3.convert("RGB").save(os.path.join(DIR_TIKTOK, "Capas_9x16", "capa_3_tres_ias_secretas_para_videos.png"), quality=95)

    # 9:16 Cover 4
    im4 = make_vbg((255, 40, 20, 50))
    d4 = ImageDraw.Draw(im4)
    draw_auto_badge(d4, w9, "DESAFIO DE PERCEPÇÃO", 220, 34, (40, 15, 15), (255, 60, 60), (255, 100, 100), 50, 18)
    shadow_txt(d4, (540, 370), "HUMANO OU", get_font(92, True), (255, 255, 255))
    shadow_txt(d4, (540, 480), "INTELIGÊNCIA", get_font(92, True), (255, 100, 20))
    shadow_txt(d4, (540, 590), "ARTIFICIAL?", get_font(96, True), (255, 225, 0))
    d4.rounded_rectangle([90, 710, 520, 1180], radius=32, fill=(18, 22, 32, 240), outline=(0, 160, 255), width=3)
    d4.text((305, 780), "VOZ 1", fill=(80, 190, 255), font=get_font(56, True), anchor="mm")
    d4.text((305, 930), "?", fill=(80, 190, 255), font=get_font(120, True), anchor="mm")
    d4.text((305, 1090), "Humano?", fill=(200, 200, 215), font=get_font(36, True), anchor="mm")
    d4.rounded_rectangle([560, 710, 990, 1180], radius=32, fill=(32, 20, 16, 240), outline=(255, 120, 20), width=3)
    d4.text((775, 780), "VOZ 2", fill=(255, 140, 40), font=get_font(56, True), anchor="mm")
    d4.text((775, 930), "?", fill=(255, 140, 40), font=get_font(120, True), anchor="mm")
    d4.text((775, 1090), "Robô?", fill=(200, 200, 215), font=get_font(36, True), anchor="mm")
    shadow_txt(d4, (540, 1280), "99% DAS PESSOAS ERRAM!", get_font(48, True), (255, 70, 70))
    d4.rounded_rectangle([100, 1370, 980, 1520], radius=34, fill=(0, 220, 120), outline=(255, 255, 255), width=3)
    shadow_txt(d4, (540, 1445), "OUÇA E COMENTE SEU PALPITE!", get_font(42, True), (10, 30, 15))
    d4.text((540, 1660), "CLONAVOZ AI • VOZ NEURAL", fill=(255, 140, 40), font=get_font(38, True), anchor="mm")
    im4.convert("RGB").save(os.path.join(DIR_TIKTOK, "Capas_9x16", "capa_4_desafio_humano_ou_ia_teste_cego.png"), quality=95)

    # --- C) THUMBNAILS 16:9 (1280x720) PARA 3_YOUTUBE\Thumbnails_16x9 ---
    def make_hbg(gcol):
        im = Image.new("RGBA", (1280, 720), (10, 10, 14, 255))
        gl = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gl)
        gd.ellipse([850 - 350, 360 - 350, 850 + 350, 360 + 350], fill=gcol)
        gl = gl.filter(ImageFilter.GaussianBlur(90))
        return Image.alpha_composite(im, gl)

    # Thumb 1 (Removed www.clonavoz.com.br!)
    th1 = make_hbg((255, 60, 20, 60))
    dt1 = ImageDraw.Draw(th1)
    dt1.rounded_rectangle([55, 55, 465, 105], radius=25, fill=(35, 18, 18), outline=(255, 60, 60), width=3)
    dt1.text((260, 80), "100% BRASILEIRO • NO PIX", fill=(255, 100, 100), font=get_font(24, True), anchor="mm")
    shadow_txt(dt1, (50, 180), "CHEGA DE", get_font(64, True), (255, 255, 255), anchor="lm")
    shadow_txt(dt1, (50, 260), "PAGAR EM", get_font(78, True), (255, 75, 75), anchor="lm")
    shadow_txt(dt1, (50, 350), "DÓLAR!", get_font(90, True), (255, 220, 0), anchor="lm")
    dt1.rounded_rectangle([50, 440, 620, 620], radius=24, fill=(18, 18, 24), outline=(255, 85, 0), width=2)
    dt1.text((80, 485), "• Sem Cartão Internacional", fill=(225, 225, 225), font=get_font(28, True), anchor="lm")
    dt1.text((80, 535), "• Sem Mensalidades Abusivas", fill=(225, 225, 225), font=get_font(28, True), anchor="lm")
    dt1.text((80, 580), "• Recarga a Partir de R$ 9,90", fill=(0, 240, 130), font=get_font(30, True), anchor="lm")
    dt1.rounded_rectangle([720, 90, 1220, 630], radius=36, fill=(16, 16, 22), outline=(255, 85, 0), width=3)
    lr = logo_base.resize((240, 240), Image.Resampling.LANCZOS)
    th1.paste(lr, (970 - 120, 140), lr)
    dt1 = ImageDraw.Draw(th1)
    shadow_txt(dt1, (970, 430), "CLONAVOZ AI", get_font(48, True), (255, 255, 255))
    dt1.text((970, 495), "Vozes Neurais Realistas", fill=(255, 125, 30), font=get_font(30, True), anchor="mm")
    dt1.text((970, 560), "Locução Pronta em 2 Segundos", fill=(200, 200, 215), font=get_font(26, True), anchor="mm")
    th1.convert("RGB").save(os.path.join(DIR_YOUTUBE, "Thumbnails_16x9", "thumb_1_comercial_chega_de_pagar_em_dolar.png"), quality=95)
    print("Todas as capas 1:1, 9:16 e 16:9 geradas sem links e sem @!")


# ==============================================================================
# 3. LAYOUTS DE VÍDEO 1:1 (INSTAGRAM) E 9:16 (TIKTOK / YOUTUBE) SEM ENDEREÇOS
# ==============================================================================
W1, H1 = 1080, 1080
bg_1x1_orange = make_base_bg(W1, H1, (255, 75, 0, 42))
bg_1x1_purple = make_base_bg(W1, H1, (200, 60, 255, 38))
bg_1x1_red = make_base_bg(W1, H1, (255, 50, 20, 38))

def draw_header_footer_1x1(draw):
    draw.text((W1//2, 52), "CLONAVOZ AI • VOZ NEURAL", fill=(255, 120, 40), font=get_font(26, True), anchor="mm")
    draw.line([(W1//2 - 140, 72), (W1//2 + 140, 72)], fill=(255, 85, 0), width=2)
    draw.text((W1//2, 1042), "Desenvolvido por nx49 System Development", fill=(105, 105, 120), font=get_font(22, False), anchor="mm")

def draw_cta_1x1(draw, t):
    draw_auto_badge(draw, W1, "SEM ASSINATURAS • RECARGA FÁCIL PIX", 140, 28, (16, 36, 22), (0, 220, 110), (0, 255, 130))
    draw_fitted_text(draw, (W1//2, 240), "Comece Agora Por Apenas", 900, 36, (200, 200, 210), True)
    draw_fitted_text(draw, (W1//2, 330), "R$ 9,90", 900, 82, (0, 255, 135), True)
    draw_fitted_text(draw, (W1//2, 405), "No PIX com Liberação Imediata", 900, 30, (175, 175, 185), False)

    pulse = int(math.sin(t * 6) * 4)
    btop = 475 + pulse
    bbot = btop + 110
    draw.rounded_rectangle([100, btop, W1 - 100, bbot], radius=34, fill=(255, 75, 0), outline=(255, 160, 90), width=3)
    draw_fitted_text(draw, (W1//2, (btop + bbot)//2), "TESTE GRÁTIS HOJE MESMO!", 820, 44, (255, 255, 255), True)

    draw_fitted_text(draw, (W1//2, 675), "CLONAVOZ AI", 900, 52, (255, 125, 30), True)
    draw_fitted_text(draw, (W1//2, 745), "Vozes Neurais 100% Brasileiras", 920, 36, (210, 210, 220), True)
    draw_auto_badge(draw, W1, "Mais Informações na Descrição", 885, 32, (22, 22, 28), (180, 180, 195), (255, 255, 255), pad_x=50, pad_y=16)

def frame_comercial_1x1(t, idx):
    img = bg_1x1_orange.copy()
    draw = ImageDraw.Draw(img)
    draw_header_footer_1x1(draw)
    if t < 5.2:
        draw_auto_badge(draw, W1, "CHEGA DE PAGAR EM DÓLAR", 145, 28, (35, 18, 18), (255, 60, 60), (255, 110, 110))
        draw_fitted_text(draw, (W1//2, 245), "Cansado de", 900, 38, (210, 210, 220), True)
        draw_fitted_text(draw, (W1//2, 325), "ASSINATURAS ABUSIVAS?", 940, 68, (255, 75, 75), True)
        draw.rounded_rectangle([80, 420, W1 - 80, 770], radius=28, fill=(20, 16, 20), outline=(255, 60, 60), width=2)
        draw_fitted_text(draw, (W1//2, 485), "Plataformas Estrangeiras:", 840, 36, (165, 165, 180), True)
        draw_fitted_text(draw, (W1//2, 560), "R$ 150 a R$ 550 / mês", 840, 56, (255, 95, 95), True)
        draw_fitted_text(draw, (W1//2, 645), "• Exigem Cartão Internacional", 840, 32, (225, 225, 225), False)
        draw_fitted_text(draw, (W1//2, 705), "• Cobram IOF e Taxas em Dólar", 840, 32, (225, 225, 225), False)
        draw_fitted_text(draw, (W1//2, 895), "Existe uma solução 100% brasileira...", 920, 38, (255, 135, 45), True)
    elif t < 11.8:
        draw_auto_badge(draw, W1, "100% FEITO NO BRASIL", 140, 28, (28, 20, 12), (255, 110, 0), (255, 155, 55))
        lw = int(190 + math.sin(t * 4) * 8)
        lr = logo_base.resize((lw, lw), Image.Resampling.LANCZOS)
        img.paste(lr, (W1//2 - lw//2, 205), lr)
        draw = ImageDraw.Draw(img)
        draw_fitted_text(draw, (W1//2, 455), "CLONAVOZ AI", 920, 72, (255, 255, 255), True)
        draw_fitted_text(draw, (W1//2, 535), "Voz Neural Hiper-Realista", 920, 50, (255, 115, 25), True)
        draw_fitted_text(draw, (W1//2, 600), "Sem sotaque robótico ou estrangeiro", 920, 34, (195, 195, 205), True)
        bar_count = 22
        bar_w, spacing = 14, 16
        sx = W1//2 - (bar_count * (bar_w + spacing)) // 2
        for b in range(bar_count):
            bh = int(24 + 95 * abs(math.sin(t * 8 + b * 0.4)))
            bx = sx + b * (bar_w + spacing)
            by = 740 - bh // 2
            draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=6, fill=(255, int(80 + 120 * (b/bar_count)), 0))
        draw_fitted_text(draw, (W1//2, 895), "Narração gerada em 2 segundos!", 920, 38, (255, 255, 255), True)
    elif t < 18.2:
        draw_auto_badge(draw, W1, "ONDE VOCÊ PODE USAR?", 140, 28, (16, 25, 38), (0, 165, 255), (110, 205, 255))
        draw_fitted_text(draw, (W1//2, 230), "Turbine sua Produção:", 920, 58, (255, 255, 255), True)
        cards = [
            ("CANAIS DARK & VÍDEOS", "Histórias, mistérios e curiosidades sem microfone"),
            ("VÍDEOS CURTOS VIRAIS", "Áudios persuasivos com retenção máxima"),
            ("VSLs & ANÚNCIOS DE VENDA", "Locução de cinema para alta conversão"),
        ]
        cy = 310
        for tc, dc in cards:
            draw.rounded_rectangle([75, cy, W1 - 75, cy + 150], radius=22, fill=(18, 18, 24), outline=(255, 85, 0), width=2)
            draw_fitted_text(draw, (W1//2, cy + 50), tc, W1 - 200, 38, (255, 145, 45), True)
            draw_fitted_text(draw, (W1//2, cy + 108), dc, W1 - 200, 30, (200, 200, 210), False)
            cy += 175
        draw_fitted_text(draw, (W1//2, 895), "Download Direto em WAV e MP3", 920, 36, (255, 255, 255), True)
    else:
        draw_cta_1x1(draw, t)
    return img

def frame_passo_1x1(t, idx):
    img = bg_1x1_purple.copy()
    draw = ImageDraw.Draw(img)
    draw_header_footer_1x1(draw)
    if t < 4.0:
        draw_auto_badge(draw, W1, "TUTORIAL CANAL DARK", 145, 28, (30, 18, 40), (180, 80, 255), (210, 150, 255))
        draw_fitted_text(draw, (W1//2, 255), "COMO CRIAR UM", 920, 64, (255, 255, 255), True)
        draw_fitted_text(draw, (W1//2, 340), "CANAL DARK", 920, 74, (255, 95, 20), True)
        draw_fitted_text(draw, (W1//2, 420), "EM 60 SEGUNDOS!", 920, 52, (255, 255, 255), True)
        draw.rounded_rectangle([85, 510, W1 - 85, 840], radius=28, fill=(22, 18, 26), outline=(180, 80, 255), width=2)
        draw_fitted_text(draw, (W1//2, 585), "• Sem Usar Microfone", 820, 38, (220, 220, 230), True)
        draw_fitted_text(draw, (W1//2, 670), "• Sem Mostrar o Rosto", 820, 44, (255, 140, 40), True)
        draw_fitted_text(draw, (W1//2, 755), "• 100% no Piloto Automático", 820, 38, (0, 230, 130), True)
    elif t < 10.2:
        draw_auto_badge(draw, W1, "PASSO 1 & PASSO 2", 145, 28, (25, 20, 30), (255, 120, 40), (255, 160, 70))
        draw.rounded_rectangle([75, 230, W1 - 75, 510], radius=26, fill=(18, 18, 24), outline=(0, 200, 130), width=2)
        draw_fitted_text(draw, (W1//2, 295), "PASSO 1: ROTEIRO", W1 - 210, 48, (0, 230, 130), True)
        draw_fitted_text(draw, (W1//2, 375), "Peça a história ao ChatGPT", W1 - 210, 36, (215, 215, 225), True)
        draw_fitted_text(draw, (W1//2, 440), "Pronto em menos de 10 segundos", W1 - 210, 30, (165, 165, 175), False)
        draw.rounded_rectangle([75, 555, W1 - 75, 865], radius=26, fill=(26, 18, 22), outline=(255, 90, 20), width=2)
        draw_fitted_text(draw, (W1//2, 620), "PASSO 2: CLONAVOZ", W1 - 210, 48, (255, 105, 25), True)
        draw_fitted_text(draw, (W1//2, 700), "Cole o texto e escolha a voz", W1 - 210, 36, (220, 220, 230), True)
        draw_fitted_text(draw, (W1//2, 765), "Vozes neurais brasileiras ultra-realistas", W1 - 210, 30, (175, 175, 185), False)
        draw_fitted_text(draw, (W1//2, 820), "Gera a narração em 2 segundos!", W1 - 210, 30, (255, 155, 55), True)
    elif t < 16.2:
        draw_auto_badge(draw, W1, "PASSO 3 & PASSO 4", 145, 28, (20, 25, 35), (0, 160, 255), (100, 200, 255))
        draw.rounded_rectangle([75, 235, W1 - 75, 525], radius=26, fill=(18, 18, 24), outline=(0, 160, 255), width=2)
        draw_fitted_text(draw, (W1//2, 305), "PASSO 3: DOWNLOAD DIRETO", W1 - 210, 46, (80, 190, 255), True)
        draw_fitted_text(draw, (W1//2, 385), "Baixe o áudio em WAV ou MP3", W1 - 210, 36, (215, 215, 225), True)
        draw_fitted_text(draw, (W1//2, 455), "Arquivo pronto direto no seu dispositivo", W1 - 210, 30, (165, 165, 175), False)
        draw.rounded_rectangle([75, 565, W1 - 75, 855], radius=26, fill=(18, 18, 24), outline=(255, 80, 120), width=2)
        draw_fitted_text(draw, (W1//2, 635), "PASSO 4: JUNTE NO CAPCUT", W1 - 210, 46, (255, 100, 140), True)
        draw_fitted_text(draw, (W1//2, 715), "Adicione vídeos de fundo gratuitos", W1 - 210, 36, (215, 215, 225), True)
        draw_fitted_text(draw, (W1//2, 785), "Seu vídeo está pronto para viralizar!", W1 - 210, 30, (165, 165, 175), False)
    else:
        draw_cta_1x1(draw, t)
    return img

def frame_3ias_1x1(t, idx):
    img = bg_1x1_orange.copy()
    draw = ImageDraw.Draw(img)
    draw_header_footer_1x1(draw)
    if t < 4.0:
        draw_auto_badge(draw, W1, "FERRAMENTAS SECRETAS DE IA", 145, 28, (20, 25, 40), (0, 160, 255), (100, 200, 255))
        draw_fitted_text(draw, (W1//2, 260), "3 FERRAMENTAS", 920, 68, (255, 255, 255), True)
        draw_fitted_text(draw, (W1//2, 340), "QUE VOCÊ PRECISA", 920, 52, (255, 105, 20), True)
        draw_fitted_text(draw, (W1//2, 420), "CONHECER HOJE!", 920, 64, (255, 255, 255), True)
        draw.rounded_rectangle([85, 510, W1 - 85, 840], radius=28, fill=(18, 18, 24), outline=(255, 85, 0), width=2)
        draw_fitted_text(draw, (W1//2, 585), "1. Roteiros em Segundos", 820, 38, (205, 205, 215), True)
        draw_fitted_text(draw, (W1//2, 670), "2. Edição Automática", 820, 38, (205, 205, 215), True)
        draw_fitted_text(draw, (W1//2, 755), "3. Voz Neural no PIX", 820, 48, (255, 125, 30), True)
    elif t < 8.5:
        draw_auto_badge(draw, W1, "FERRAMENTAS 1 & 2", 145, 28, (25, 25, 30), (200, 200, 210), (225, 225, 235))
        draw.rounded_rectangle([75, 235, W1 - 75, 515], radius=26, fill=(20, 20, 26), outline=(0, 200, 120), width=2)
        draw_fitted_text(draw, (W1//2, 305), "1. CHATGPT", W1 - 210, 52, (0, 230, 130), True)
        draw_fitted_text(draw, (W1//2, 385), "Criação de histórias e roteiros", W1 - 210, 36, (210, 210, 220), True)
        draw_fitted_text(draw, (W1//2, 450), "Pronto em menos de 10 segundos", W1 - 210, 30, (160, 160, 170), False)
        draw.rounded_rectangle([75, 560, W1 - 75, 840], radius=26, fill=(20, 20, 26), outline=(0, 160, 255), width=2)
        draw_fitted_text(draw, (W1//2, 630), "2. CAPCUT", W1 - 210, 52, (80, 190, 255), True)
        draw_fitted_text(draw, (W1//2, 710), "Edição de vídeo profissional", W1 - 210, 36, (210, 210, 220), True)
        draw_fitted_text(draw, (W1//2, 775), "Grátis no celular e computador", W1 - 210, 30, (160, 160, 170), False)
        draw_fitted_text(draw, (W1//2, 920), "E agora, a mais importante...", 900, 36, (255, 125, 30), True)
    elif t < 16.2:
        draw_auto_badge(draw, W1, "A FERRAMENTA SECRETA", 140, 28, (35, 18, 12), (255, 100, 0), (255, 140, 40))
        lw = int(185 + math.sin(t * 4) * 8)
        lr = logo_base.resize((lw, lw), Image.Resampling.LANCZOS)
        img.paste(lr, (W1//2 - lw//2, 205), lr)
        draw = ImageDraw.Draw(img)
        draw_fitted_text(draw, (W1//2, 450), "3. CLONAVOZ AI", 920, 68, (255, 255, 255), True)
        draw_fitted_text(draw, (W1//2, 530), "A Voz Neural 100% Brasileira", 920, 48, (255, 110, 20), True)
        draw_fitted_text(draw, (W1//2, 595), "Sem assinaturas abusivas em dólar", 920, 34, (200, 200, 210), True)
        bar_count = 22
        bar_w, spacing = 14, 16
        sx = W1//2 - (bar_count * (bar_w + spacing)) // 2
        for b in range(bar_count):
            bh = int(24 + 90 * abs(math.sin(t * 8 + b * 0.45)))
            bx = sx + b * (bar_w + spacing)
            by = 735 - bh // 2
            draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=6, fill=(255, int(80 + 120 * (b/bar_count)), 0))
        draw_fitted_text(draw, (W1//2, 895), "Narre seus vídeos em segundos!", 920, 38, (255, 255, 255), True)
    else:
        draw_cta_1x1(draw, t)
    return img

def frame_teste_1x1(t, idx):
    img = bg_1x1_red.copy()
    draw = ImageDraw.Draw(img)
    draw_header_footer_1x1(draw)
    if t < 6.5:
        draw_auto_badge(draw, W1, "TESTE DE PERCEPÇÃO SONORA", 145, 28, (35, 15, 15), (255, 50, 50), (255, 100, 100))
        draw_fitted_text(draw, (W1//2, 265), "LOCUTOR HUMANO", 920, 64, (255, 255, 255), True)
        draw_fitted_text(draw, (W1//2, 345), "OU INTELIGÊNCIA", 920, 64, (255, 100, 20), True)
        draw_fitted_text(draw, (W1//2, 425), "ARTIFICIAL?", 920, 68, (255, 255, 255), True)
        draw.rounded_rectangle([90, 530, W1 - 90, 820], radius=28, fill=(18, 18, 24), outline=(255, 80, 20), width=2)
        draw_fitted_text(draw, (W1//2, 625), "Preste muita atenção no som...", 820, 38, (205, 205, 215), True)
        draw_fitted_text(draw, (W1//2, 720), "Você consegue acertar?", 820, 50, (255, 140, 40), True)
    elif t < 12.0:
        draw_auto_badge(draw, W1, "OUÇA COM ATENÇÃO", 140, 28, (20, 30, 45), (0, 160, 255), (100, 200, 255))
        draw_fitted_text(draw, (W1//2, 240), "VOZ NÚMERO 1", 920, 68, (80, 190, 255), True)
        draw_fitted_text(draw, (W1//2, 320), '"No meio da escuridão, apenas os', 920, 36, (220, 220, 230), True)
        draw_fitted_text(draw, (W1//2, 370), 'mais corajosos encontram a verdade."', 920, 36, (220, 220, 230), True)
        draw.rounded_rectangle([W1//2 - 105, 435, W1//2 + 105, 645], radius=28, fill=(20, 24, 34), outline=(0, 160, 255), width=3)
        draw_fitted_text(draw, (W1//2, 540), "?", 200, 96, (80, 190, 255), True)
        bar_count = 20
        bar_w, spacing = 14, 16
        sx = W1//2 - (bar_count * (bar_w + spacing)) // 2
        for b in range(bar_count):
            bh = int(20 + 85 * abs(math.sin(t * 7 + b * 0.5)))
            bx = sx + b * (bar_w + spacing)
            by = 795 - bh // 2
            draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=6, fill=(0, int(150 + 80 * (b/bar_count)), 255))
    elif t < 18.5:
        draw_auto_badge(draw, W1, "AGORA A SEGUNDA VOZ", 140, 28, (40, 25, 15), (255, 140, 0), (255, 170, 60))
        draw_fitted_text(draw, (W1//2, 240), "VOZ NÚMERO 2", 920, 68, (255, 150, 40), True)
        draw_fitted_text(draw, (W1//2, 320), '"O universo guarda mistérios que', 920, 36, (220, 220, 230), True)
        draw_fitted_text(draw, (W1//2, 370), 'a mente humana não consegue explicar."', 920, 36, (220, 220, 230), True)
        draw.rounded_rectangle([W1//2 - 105, 435, W1//2 + 105, 645], radius=28, fill=(34, 22, 16), outline=(255, 140, 0), width=3)
        draw_fitted_text(draw, (W1//2, 540), "?", 200, 96, (255, 150, 40), True)
        bar_count = 20
        bar_w, spacing = 14, 16
        sx = W1//2 - (bar_count * (bar_w + spacing)) // 2
        for b in range(bar_count):
            bh = int(20 + 85 * abs(math.sin(t * 7 + b * 0.5)))
            bx = sx + b * (bar_w + spacing)
            by = 795 - bh // 2
            draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=6, fill=(255, int(80 + 120 * (b/bar_count)), 0))
    elif t < 24.8:
        draw_auto_badge(draw, W1, "QUAL É A INTELIGÊNCIA ARTIFICIAL?", 145, 28, (35, 18, 15), (255, 60, 20), (255, 110, 40))
        draw_fitted_text(draw, (W1//2, 265), "QUAL DELAS É A IA?", 920, 68, (255, 255, 255), True)
        draw_fitted_text(draw, (W1//2, 355), "Voz 1 ou Voz 2?", 920, 62, (255, 110, 20), True)
        draw.rounded_rectangle([90, 455, W1 - 90, 760], radius=30, fill=(22, 18, 24), outline=(0, 230, 130), width=3)
        draw_fitted_text(draw, (W1//2, 535), "DEIXE SEU PALPITE", 820, 52, (0, 240, 140), True)
        draw_fitted_text(draw, (W1//2, 615), "NOS COMENTÁRIOS!", 820, 52, (255, 255, 255), True)
        draw_fitted_text(draw, (W1//2, 695), "Comente 1 ou 2 abaixo", 820, 36, (200, 200, 210), True)
        draw_fitted_text(draw, (W1//2, 880), "Revelação nos próximos segundos...", 900, 34, (180, 180, 190), True)
    else:
        draw_auto_badge(draw, W1, "O SEGREDO REVELADO!", 140, 28, (16, 36, 22), (0, 220, 110), (0, 255, 130))
        draw_fitted_text(draw, (W1//2, 235), "AS DUAS VOZES FORAM", 920, 48, (255, 255, 255), True)
        draw_fitted_text(draw, (W1//2, 310), "GERADAS POR IA!", 920, 68, (255, 110, 20), True)
        draw_fitted_text(draw, (W1//2, 380), "Feitas no Clonavoz em Segundos", 920, 34, (200, 200, 210), True)
        pulse = int(math.sin(t * 6) * 4)
        btop = 455 + pulse
        bbot = btop + 110
        draw.rounded_rectangle([100, btop, W1 - 100, bbot], radius=34, fill=(255, 75, 0), outline=(255, 160, 90), width=3)
        draw_fitted_text(draw, (W1//2, (btop + bbot)//2), "TESTE GRÁTIS HOJE MESMO!", 820, 44, (255, 255, 255), True)
        draw_fitted_text(draw, (W1//2, 650), "CLONAVOZ AI", 920, 54, (255, 125, 30), True)
        draw_auto_badge(draw, W1, "Recarga Fácil no PIX por R$ 9,90", 770, 32, (22, 35, 26), (0, 220, 120), (0, 240, 140), pad_x=45, pad_y=14)
        draw_auto_badge(draw, W1, "Mais Informações na Descrição", 895, 32, (22, 22, 28), (180, 180, 195), (255, 255, 255), pad_x=45, pad_y=14)
    return img


# --- 9:16 (1080x1920) PARA TIKTOK E YOUTUBE SHORTS (ZERO ENDEREÇOS E ZERO LINKS) ---
W9, H9 = 1080, 1920
bg_9_orange = make_base_bg(W9, H9, (255, 75, 0, 42))
bg_9_purple = make_base_bg(W9, H9, (200, 60, 255, 38))
bg_9_red = make_base_bg(W9, H9, (255, 50, 20, 38))

def draw_header_footer_9x16(draw):
    draw.text((W9//2, 130), "CLONAVOZ AI • VOZ NEURAL", fill=(255, 120, 40), font=get_font(32, True), anchor="mm")
    draw.line([(W9//2 - 160, 160), (W9//2 + 160, 160)], fill=(255, 85, 0), width=2)
    draw.text((W9//2, 1830), "Desenvolvido por nx49 System Development", fill=(100, 100, 115), font=get_font(26, False), anchor="mm")

def draw_cta_9x16(draw, t):
    draw_auto_badge(draw, W9, "SEM ASSINATURAS • RECARGA NO PIX", 270, 32, (16, 36, 22), (0, 220, 110), (0, 255, 130), pad_x=55, pad_y=18)
    draw_fitted_text(draw, (W9//2, 420), "Comece Agora Por Apenas", 900, 42, (195, 195, 205), True)
    draw_fitted_text(draw, (W9//2, 535), "R$ 9,90", 900, 88, (0, 255, 135), True)
    draw_fitted_text(draw, (W9//2, 625), "No PIX com Liberação Imediata", 900, 34, (175, 175, 185), False)

    pulse = int(math.sin(t * 6) * 4)
    btop = 750 + pulse
    bbot = btop + 130
    draw.rounded_rectangle([90, btop, W9 - 90, bbot], radius=38, fill=(255, 75, 0), outline=(255, 155, 80), width=3)
    draw_fitted_text(draw, (W9//2, (btop + bbot) // 2), "TESTE GRÁTIS HOJE MESMO!", 820, 46, (255, 255, 255), True)

    draw_fitted_text(draw, (W9//2, 1030), "CLONAVOZ AI", 900, 64, (255, 125, 30), True)
    draw_fitted_text(draw, (W9//2, 1115), "Vozes Neurais 100% Brasileiras", 900, 40, (210, 210, 220), True)
    draw_auto_badge(draw, W9, "Mais Informações na Descrição", 1320, 38, (22, 22, 28), (180, 180, 195), (255, 255, 255), pad_x=55, pad_y=22)

def frame_comercial_9x16(t, idx):
    img = bg_9_orange.copy()
    draw = ImageDraw.Draw(img)
    draw_header_footer_9x16(draw)
    if t < 5.2:
        draw_auto_badge(draw, W9, "CHEGA DE PAGAR EM DÓLAR", 280, 32, (35, 18, 18), (255, 60, 60), (255, 110, 110))
        draw_fitted_text(draw, (W9//2, 460), "Cansado de", 900, 42, (210, 210, 220), True)
        draw_fitted_text(draw, (W9//2, 560), "ASSINATURAS", 920, 84, (255, 70, 70), True)
        draw_fitted_text(draw, (W9//2, 660), "ABUSIVAS?", 920, 84, (255, 255, 255), True)
        draw.rounded_rectangle([90, 810, W9 - 90, 1200], radius=32, fill=(20, 16, 20), outline=(255, 60, 60), width=2)
        draw_fitted_text(draw, (W9//2, 885), "Plataformas Estrangeiras:", 840, 42, (160, 160, 175), True)
        draw_fitted_text(draw, (W9//2, 970), "R$ 150 a R$ 550 / mês", 840, 62, (255, 90, 90), True)
        draw_fitted_text(draw, (W9//2, 1062), "• Exigem Cartão Internacional", 840, 36, (225, 225, 225), False)
        draw_fitted_text(draw, (W9//2, 1132), "• Cobram IOF e Taxas em Dólar", 840, 36, (225, 225, 225), False)
        draw_fitted_text(draw, (W9//2, 1480), "Existe uma solução brasileira...", 900, 42, (255, 130, 45), True)
    elif t < 11.8:
        draw_auto_badge(draw, W9, "100% FEITO NO BRASIL", 280, 32, (28, 20, 12), (255, 110, 0), (255, 155, 55))
        lw = int(260 + math.sin(t * 4) * 12)
        lr = logo_base.resize((lw, lw), Image.Resampling.LANCZOS)
        img.paste(lr, (W9//2 - lw//2, 400), lr)
        draw = ImageDraw.Draw(img)
        draw_fitted_text(draw, (W9//2, 760), "CLONAVOZ AI", 920, 84, (255, 255, 255), True)
        draw_fitted_text(draw, (W9//2, 850), "Voz Neural Hiper-Realista", 920, 60, (255, 115, 25), True)
        draw_fitted_text(draw, (W9//2, 930), "Sem sotaque robótico ou estrangeiro", 920, 40, (195, 195, 205), True)
        bar_count = 24
        bar_w, spacing = 14, 18
        sx = W9//2 - (bar_count * (bar_w + spacing)) // 2
        for b in range(bar_count):
            bh = int(30 + 130 * abs(math.sin(t * 8 + b * 0.4)))
            bx = sx + b * (bar_w + spacing)
            by = 1150 - bh // 2
            draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=7, fill=(255, int(80 + 120 * (b/bar_count)), 0))
        draw_fitted_text(draw, (W9//2, 1360), "Narração gerada em 2 segundos!", 900, 42, (255, 255, 255), True)
    elif t < 18.2:
        draw_auto_badge(draw, W9, "ONDE VOCÊ PODE USAR?", 280, 32, (16, 25, 38), (0, 165, 255), (110, 205, 255))
        draw_fitted_text(draw, (W9//2, 400), "Turbine sua Produção:", 920, 74, (255, 255, 255), True)
        cards = [
            ("CANAIS DARK & HISTÓRIAS", "Mistérios e curiosidades sem usar microfone"),
            ("VÍDEOS CURTOS VIRAIS", "Áudios persuasivos com retenção máxima"),
            ("VSLs & ANÚNCIOS DE VENDA", "Locução de cinema para alta conversão"),
        ]
        cy = 520
        for tc, dc in cards:
            draw.rounded_rectangle([80, cy, W9 - 80, cy + 190], radius=26, fill=(18, 18, 24), outline=(255, 85, 0), width=2)
            draw_fitted_text(draw, (W9//2, cy + 64), tc, W9 - 220, 42, (255, 145, 45), True)
            draw_fitted_text(draw, (W9//2, cy + 130), dc, W9 - 220, 34, (195, 195, 205), False)
            cy += 240
        draw_fitted_text(draw, (W9//2, 1420), "Download Direto em WAV e MP3", 900, 42, (255, 255, 255), True)
    else:
        draw_cta_9x16(draw, t)
    return img

def frame_passo_9x16(t, idx):
    img = bg_9_purple.copy()
    draw = ImageDraw.Draw(img)
    draw_header_footer_9x16(draw)
    if t < 4.0:
        draw_auto_badge(draw, W9, "TUTORIAL CANAL DARK", 280, 32, (30, 18, 40), (180, 80, 255), (210, 150, 255))
        draw_fitted_text(draw, (W9//2, 470), "COMO CRIAR UM", 920, 80, (255, 255, 255), True)
        draw_fitted_text(draw, (W9//2, 570), "CANAL DARK", 920, 84, (255, 90, 20), True)
        draw_fitted_text(draw, (W9//2, 670), "EM 60 SEGUNDOS!", 920, 60, (255, 255, 255), True)
        draw.rounded_rectangle([90, 840, W9-90, 1200], radius=32, fill=(22, 18, 26), outline=(180, 80, 255), width=2)
        draw_fitted_text(draw, (W9//2, 930), "Sem Microfone", 820, 42, (220, 220, 230), True)
        draw_fitted_text(draw, (W9//2, 1010), "Sem Mostrar o Rosto", 820, 56, (255, 140, 40), True)
        draw_fitted_text(draw, (W9//2, 1090), "100% no Piloto Automático", 820, 42, (0, 230, 130), True)
    elif t < 10.2:
        draw_auto_badge(draw, W9, "PASSO 1 & PASSO 2", 280, 32, (25, 20, 30), (255, 120, 40), (255, 160, 70))
        draw.rounded_rectangle([80, 420, W9-80, 720], radius=28, fill=(18, 18, 24), outline=(0, 200, 130), width=2)
        draw_fitted_text(draw, (W9//2, 495), "PASSO 1: ROTEIRO", W9 - 220, 54, (0, 230, 130), True)
        draw_fitted_text(draw, (W9//2, 575), "Peça a história ao ChatGPT", W9 - 220, 40, (210, 210, 220), True)
        draw_fitted_text(draw, (W9//2, 645), "Pronto em menos de 10 segundos", W9 - 220, 34, (160, 160, 170), False)
        draw.rounded_rectangle([80, 800, W9-80, 1150], radius=28, fill=(26, 18, 22), outline=(255, 90, 20), width=2)
        draw_fitted_text(draw, (W9//2, 875), "PASSO 2: CLONAVOZ", W9 - 220, 54, (255, 100, 20), True)
        draw_fitted_text(draw, (W9//2, 955), "Cole o texto e escolha a voz", W9 - 220, 40, (220, 220, 230), True)
        draw_fitted_text(draw, (W9//2, 1025), "Vozes neurais brasileiras ultra-realistas", W9 - 220, 34, (160, 160, 170), False)
        draw_fitted_text(draw, (W9//2, 1090), "Gera a narração em 2 segundos!", W9 - 220, 34, (255, 150, 50), True)
    elif t < 16.2:
        draw_auto_badge(draw, W9, "PASSO 3 & PASSO 4", 280, 32, (20, 25, 35), (0, 160, 255), (100, 200, 255))
        draw.rounded_rectangle([80, 420, W9-80, 720], radius=28, fill=(18, 18, 24), outline=(0, 160, 255), width=2)
        draw_fitted_text(draw, (W9//2, 495), "PASSO 3: DOWNLOAD DIRETO", W9 - 220, 50, (80, 190, 255), True)
        draw_fitted_text(draw, (W9//2, 575), "Baixe o áudio em WAV ou MP3", W9 - 220, 40, (210, 210, 220), True)
        draw_fitted_text(draw, (W9//2, 645), "Arquivo pronto direto no seu dispositivo", W9 - 220, 34, (160, 160, 170), False)
        draw.rounded_rectangle([80, 800, W9-80, 1100], radius=28, fill=(18, 18, 24), outline=(255, 80, 120), width=2)
        draw_fitted_text(draw, (W9//2, 875), "PASSO 4: JUNTE NO CAPCUT", W9 - 220, 50, (255, 100, 140), True)
        draw_fitted_text(draw, (W9//2, 955), "Adicione vídeos de fundo gratuitos", W9 - 220, 40, (210, 210, 220), True)
        draw_fitted_text(draw, (W9//2, 1025), "Seu vídeo está pronto para viralizar!", W9 - 220, 34, (160, 160, 170), False)
    else:
        draw_cta_9x16(draw, t)
    return img

def frame_3ias_9x16(t, idx):
    img = bg_9_orange.copy()
    draw = ImageDraw.Draw(img)
    draw_header_footer_9x16(draw)
    if t < 4.0:
        draw_auto_badge(draw, W9, "FERRAMENTAS SECRETAS DE IA", 280, 32, (20, 25, 40), (0, 160, 255), (100, 200, 255))
        draw_fitted_text(draw, (W9//2, 480), "3 FERRAMENTAS", 920, 82, (255, 255, 255), True)
        draw_fitted_text(draw, (W9//2, 580), "QUE VOCÊ PRECISA", 920, 62, (255, 100, 20), True)
        draw_fitted_text(draw, (W9//2, 660), "CONHECER HOJE!", 920, 80, (255, 255, 255), True)
        draw.rounded_rectangle([100, 850, W9-100, 1250], radius=32, fill=(18, 18, 24), outline=(255, 85, 0), width=2)
        draw_fitted_text(draw, (W9//2, 950), "1. Roteiros em Segundos", 820, 42, (200, 200, 210), True)
        draw_fitted_text(draw, (W9//2, 1050), "2. Edição Automática", 820, 42, (200, 200, 210), True)
        draw_fitted_text(draw, (W9//2, 1150), "3. Voz Neural no PIX", 820, 58, (255, 120, 30), True)
    elif t < 8.5:
        draw_auto_badge(draw, W9, "FERRAMENTA 1 & 2", 280, 32, (25, 25, 30), (200, 200, 210), (220, 220, 230))
        draw.rounded_rectangle([90, 420, W9-90, 720], radius=30, fill=(20, 20, 26), outline=(0, 200, 120), width=2)
        draw_fitted_text(draw, (W9//2, 490), "1. CHATGPT", W9 - 220, 58, (0, 230, 130), True)
        draw_fitted_text(draw, (W9//2, 570), "Criação de histórias e roteiros", W9 - 220, 40, (200, 200, 210), True)
        draw_fitted_text(draw, (W9//2, 640), "Pronto em menos de 10 segundos", W9 - 220, 34, (160, 160, 170), False)
        draw.rounded_rectangle([90, 800, W9-90, 1100], radius=30, fill=(20, 20, 26), outline=(0, 160, 255), width=2)
        draw_fitted_text(draw, (W9//2, 870), "2. CAPCUT", W9 - 220, 58, (80, 190, 255), True)
        draw_fitted_text(draw, (W9//2, 950), "Edição de vídeo profissional", W9 - 220, 40, (200, 200, 210), True)
        draw_fitted_text(draw, (W9//2, 1020), "Grátis no celular e computador", W9 - 220, 34, (160, 160, 170), False)
        draw_fitted_text(draw, (W9//2, 1320), "E agora, a mais importante...", 900, 42, (255, 120, 30), True)
    elif t < 16.2:
        draw_auto_badge(draw, W9, "A FERRAMENTA SECRETA", 270, 32, (35, 18, 12), (255, 100, 0), (255, 140, 40))
        lw = int(220 + math.sin(t * 4) * 10)
        lr = logo_base.resize((lw, lw), Image.Resampling.LANCZOS)
        img.paste(lr, (W9//2 - lw//2, 380), lr)
        draw = ImageDraw.Draw(img)
        draw_fitted_text(draw, (W9//2, 690), "3. CLONAVOZ AI", 920, 80, (255, 255, 255), True)
        draw_fitted_text(draw, (W9//2, 780), "A Voz Neural 100% Brasileira", 920, 56, (255, 110, 20), True)
        draw_fitted_text(draw, (W9//2, 850), "Sem assinaturas abusivas em dólar", 920, 40, (200, 200, 210), True)
        bar_count = 22
        bar_w, spacing = 16, 18
        sx = W9//2 - (bar_count * (bar_w + spacing)) // 2
        for b in range(bar_count):
            bh = int(30 + 120 * abs(math.sin(t * 8 + b * 0.45)))
            bx = sx + b * (bar_w + spacing)
            by = 1060 - bh // 2
            draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=7, fill=(255, int(80 + 120 * (b/bar_count)), 0))
        draw_fitted_text(draw, (W9//2, 1260), "Narre seus vídeos em segundos!", 900, 42, (255, 255, 255), True)
    else:
        draw_cta_9x16(draw, t)
    return img

def frame_teste_9x16(t, idx):
    img = bg_9_red.copy()
    draw = ImageDraw.Draw(img)
    draw_header_footer_9x16(draw)
    if t < 6.5:
        draw_auto_badge(draw, W9, "TESTE DE PERCEPÇÃO SONORA", 280, 32, (35, 15, 15), (255, 50, 50), (255, 100, 100))
        draw_fitted_text(draw, (W9//2, 460), "HUMANO OU", 920, 82, (255, 255, 255), True)
        draw_fitted_text(draw, (W9//2, 570), "INTELIGÊNCIA", 920, 82, (255, 100, 20), True)
        draw_fitted_text(draw, (W9//2, 670), "ARTIFICIAL?", 920, 82, (255, 255, 255), True)
        draw.rounded_rectangle([100, 850, W9-100, 1200], radius=32, fill=(18, 18, 24), outline=(255, 80, 20), width=2)
        draw_fitted_text(draw, (W9//2, 940), "Preste muita atenção no som...", 820, 42, (200, 200, 210), True)
        draw_fitted_text(draw, (W9//2, 1040), "Você consegue acertar?", 820, 56, (255, 140, 40), True)
    elif t < 12.0:
        draw_auto_badge(draw, W9, "OUÇA COM ATENÇÃO", 280, 32, (20, 30, 45), (0, 160, 255), (100, 200, 255))
        draw_fitted_text(draw, (W9//2, 430), "VOZ NÚMERO 1", 920, 80, (80, 190, 255), True)
        draw_fitted_text(draw, (W9//2, 520), '"No meio da escuridão, apenas os', 920, 40, (220, 220, 230), True)
        draw_fitted_text(draw, (W9//2, 580), 'mais corajosos encontram a verdade."', 920, 40, (220, 220, 230), True)
        draw.rounded_rectangle([W9//2 - 140, 700, W9//2 + 140, 980], radius=32, fill=(20, 24, 34), outline=(0, 160, 255), width=3)
        draw_fitted_text(draw, (W9//2, 840), "?", 200, 120, (80, 190, 255), True)
        bar_count = 20
        bar_w, spacing = 16, 18
        sx = W9//2 - (bar_count * (bar_w + spacing)) // 2
        for b in range(bar_count):
            bh = int(25 + 110 * abs(math.sin(t * 7 + b * 0.5)))
            bx = sx + b * (bar_w + spacing)
            by = 1180 - bh // 2
            draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=7, fill=(0, int(150 + 80 * (b/bar_count)), 255))
    elif t < 18.5:
        draw_auto_badge(draw, W9, "AGORA A SEGUNDA VOZ", 280, 32, (40, 25, 15), (255, 140, 0), (255, 170, 60))
        draw_fitted_text(draw, (W9//2, 430), "VOZ NÚMERO 2", 920, 80, (255, 150, 40), True)
        draw_fitted_text(draw, (W9//2, 520), '"O universo guarda mistérios que', 920, 40, (220, 220, 230), True)
        draw_fitted_text(draw, (W9//2, 580), 'a mente humana não consegue explicar."', 920, 40, (220, 220, 230), True)
        draw.rounded_rectangle([W9//2 - 140, 700, W9//2 + 140, 980], radius=32, fill=(34, 22, 16), outline=(255, 140, 0), width=3)
        draw_fitted_text(draw, (W9//2, 840), "?", 200, 120, (255, 150, 40), True)
        bar_count = 20
        bar_w, spacing = 16, 18
        sx = W9//2 - (bar_count * (bar_w + spacing)) // 2
        for b in range(bar_count):
            bh = int(25 + 110 * abs(math.sin(t * 7 + b * 0.5)))
            bx = sx + b * (bar_w + spacing)
            by = 1180 - bh // 2
            draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=7, fill=(255, int(80 + 120 * (b/bar_count)), 0))
    elif t < 24.8:
        draw_auto_badge(draw, W9, "QUAL É A INTELIGÊNCIA ARTIFICIAL?", 280, 32, (35, 18, 15), (255, 60, 20), (255, 110, 40))
        draw_fitted_text(draw, (W9//2, 450), "QUAL DELAS É A IA?", 920, 80, (255, 255, 255), True)
        draw_fitted_text(draw, (W9//2, 550), "Voz 1 ou Voz 2?", 920, 74, (255, 110, 20), True)
        draw.rounded_rectangle([100, 700, W9-100, 1020], radius=34, fill=(22, 18, 24), outline=(0, 230, 130), width=3)
        draw_fitted_text(draw, (W9//2, 790), "DEIXE SEU PALPITE", 820, 58, (0, 240, 140), True)
        draw_fitted_text(draw, (W9//2, 875), "NOS COMENTÁRIOS!", 820, 58, (255, 255, 255), True)
        draw_fitted_text(draw, (W9//2, 955), "Comente 1 ou 2 abaixo", 820, 40, (200, 200, 210), True)
        draw_fitted_text(draw, (W9//2, 1200), "Revelação nos próximos segundos...", 900, 40, (180, 180, 190), True)
    else:
        draw_auto_badge(draw, W9, "O SEGREDO REVELADO!", 270, 32, (16, 36, 22), (0, 220, 110), (0, 255, 130), pad_x=55, pad_y=18)
        draw_fitted_text(draw, (W9//2, 420), "AS DUAS VOZES FORAM", 920, 54, (255, 255, 255), True)
        draw_fitted_text(draw, (W9//2, 520), "GERADAS POR IA!", 920, 78, (255, 110, 20), True)
        draw_fitted_text(draw, (W9//2, 610), "Feitas no Clonavoz em Segundos", 900, 38, (200, 200, 210), True)
        pulse = int(math.sin(t * 6) * 4)
        btop = 740 + pulse
        bbot = btop + 130
        draw.rounded_rectangle([90, btop, W9 - 90, bbot], radius=38, fill=(255, 75, 0), outline=(255, 155, 80), width=3)
        draw_fitted_text(draw, (W9//2, (btop + bbot) // 2), "TESTE GRÁTIS HOJE MESMO!", 820, 46, (255, 255, 255), True)
        draw_fitted_text(draw, (W9//2, 1020), "CLONAVOZ AI", 900, 62, (255, 125, 30), True)
        draw_auto_badge(draw, W9, "Recarga Fácil no PIX por R$ 9,90", 1180, 36, (22, 35, 26), (0, 220, 120), (0, 240, 140), pad_x=55, pad_y=18)
        draw_auto_badge(draw, W9, "Mais Informações na Descrição", 1340, 36, (22, 22, 28), (180, 180, 195), (255, 255, 255), pad_x=55, pad_y=18)
    return img


if __name__ == "__main__":
    bgm_inspire = os.path.join(STATIC_DIR, "bgm", "bgm_inspire.mp3")
    bgm_corp = os.path.join(STATIC_DIR, "bgm", "bgm_corporate.mp3")
    bgm_cine = os.path.join(STATIC_DIR, "bgm", "bgm_cinematic.mp3")

    generate_all_clean_covers()

    f1 = "clonavoz-recarga-facil-pix-gerador-voz-ia.mp4"
    f2 = "video-canal-dark-passo-a-passo-clonavoz-recarga-facil.mp4"
    f3 = "3-ias-secretas-canal-dark-clonavoz-recarga-facil.mp4"
    f4 = "teste-cego-voz-humana-vs-ia-clonavoz-locucao.mp4"

    print("\n--- [3/4] Renderizando 4 Vídeos 1:1 para 1_INSTAGRAM (Sem @ e Sem Links)... ---")
    encode_video(W1, H1, frame_comercial_1x1, wav_comercial, bgm_inspire, [os.path.join(DIR_INSTAGRAM, "Videos_1x1", f1)])
    encode_video(W1, H1, frame_passo_1x1, wav_passo, bgm_inspire, [os.path.join(DIR_INSTAGRAM, "Videos_1x1", f2)])
    encode_video(W1, H1, frame_3ias_1x1, wav_3ias, bgm_corp, [os.path.join(DIR_INSTAGRAM, "Videos_1x1", f3)])
    encode_video(W1, H1, frame_teste_1x1, wav_teste, bgm_cine, [os.path.join(DIR_INSTAGRAM, "Videos_1x1", f4)])

    print("\n--- [4/4] Renderizando 4 Vídeos 9:16 para 2_TIKTOK e 3_YOUTUBE (Sem @ e Sem Links)... ---")
    encode_video(W9, H9, frame_comercial_9x16, wav_comercial, bgm_inspire, [
        os.path.join(DIR_TIKTOK, "Videos_9x16", f1),
        os.path.join(DIR_YOUTUBE, "Videos_Shorts_9x16", f1)
    ])
    encode_video(W9, H9, frame_passo_9x16, wav_passo, bgm_inspire, [
        os.path.join(DIR_TIKTOK, "Videos_9x16", f2),
        os.path.join(DIR_YOUTUBE, "Videos_Shorts_9x16", f2)
    ])
    encode_video(W9, H9, frame_3ias_9x16, wav_3ias, bgm_corp, [
        os.path.join(DIR_TIKTOK, "Videos_9x16", f3),
        os.path.join(DIR_YOUTUBE, "Videos_Shorts_9x16", f3)
    ])
    encode_video(W9, H9, frame_teste_9x16, wav_teste, bgm_cine, [
        os.path.join(DIR_TIKTOK, "Videos_9x16", f4),
        os.path.join(DIR_YOUTUBE, "Videos_Shorts_9x16", f4)
    ])

    shutil.rmtree(SCRATCH_ROOT, ignore_errors=True)
    print("\n=== TODOS OS VÍDEOS E CAPAS 100% LIMPOS (SEM @ E SEM LINKS) CONCLUÍDOS! ===")
