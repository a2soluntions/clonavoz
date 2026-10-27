import os
import sys
import math
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf

BASE_DIR = r"e:\A2\projetos\gerador de voz com texto"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
STATIC_DIR = os.path.join(BASE_DIR, "static")
SCRATCH_ROOT = os.path.join(BASE_DIR, "scratch_fast")
DESKTOP_DIR = r"C:\Users\User\Desktop"
TIKTOK_DIR = os.path.join(DESKTOP_DIR, "Videos_TikTok_Tela_Cheia")

os.makedirs(SCRATCH_ROOT, exist_ok=True)
os.makedirs(TIKTOK_DIR, exist_ok=True)

FPS = 30

# Font cache
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

def draw_auto_badge(draw, width_canvas, text, y_center, start_size, fill_bg, outline_color, text_color, pad_x=40, pad_y=14, border_width=2):
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

# Load Logo
logo_path = os.path.join(STATIC_DIR, "logo_perfil_instagram.png")
if os.path.exists(logo_path):
    logo_base = Image.open(logo_path).convert("RGBA")
else:
    logo_base = Image.new("RGBA", (300, 300), (255, 85, 0, 255))

def make_base_bg(w, h, glow_color=(255, 75, 0, 42)):
    img = Image.new("RGBA", (w, h), (10, 10, 14, 255))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    r = int(min(w, h) * 0.42)
    cx, cy = w // 2, int(h * 0.48)
    g_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=glow_color)
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.alpha_composite(img, glow)
    return img.convert("RGB")

def encode_video_from_generator(w, h, draw_fn, wav_path, bgm_path, output_filepath):
    info = sf.info(wav_path)
    dur = info.duration
    total_sec = math.ceil(dur + 1.2)
    total_frames = int(total_sec * FPS)

    frames_dir = os.path.join(SCRATCH_ROOT, "frames")
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir, exist_ok=True)

    print(f"Renderizando {os.path.basename(output_filepath)} ({w}x{h}, {total_frames} frames)...")
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
        output_filepath
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"OK -> {output_filepath}")


# ==============================================================================
# GERADOR 1:1 (1080 x 1080) PARA INSTAGRAM (Cabe 100% na tela sem cortar!)
# ==============================================================================
W1, H1 = 1080, 1080
bg_1x1_orange = make_base_bg(W1, H1, (255, 75, 0, 42))
bg_1x1_purple = make_base_bg(W1, H1, (200, 60, 255, 38))
bg_1x1_red = make_base_bg(W1, H1, (255, 50, 20, 38))

def draw_header_footer_1x1(draw):
    draw.text((W1//2, 52), "CLONAVOZ.COM.BR", fill=(255, 120, 40), font=get_font(26, True), anchor="mm")
    draw.line([(W1//2 - 120, 72), (W1//2 + 120, 72)], fill=(255, 85, 0), width=2)
    draw.text((W1//2, 1042), "Desenvolvido por nx49 System Development", fill=(105, 105, 120), font=get_font(22, False), anchor="mm")

def draw_cta_1x1(draw, t):
    draw_auto_badge(draw, W1, "SEM ASSINATURAS • RECARGA FÁCIL PIX", 140, 28, (16, 36, 22), (0, 220, 110), (0, 255, 130))
    draw_fitted_text(draw, (W1//2, 240), "Comece Agora Por Apenas", 900, 36, (200, 200, 210), True)
    draw_fitted_text(draw, (W1//2, 330), "R$ 9,90", 900, 82, (0, 255, 135), True)
    draw_fitted_text(draw, (W1//2, 405), "No PIX com Liberação Imediata", 900, 30, (175, 175, 185), False)

    pulse = int(math.sin(t * 6) * 4)
    btop = 475 + pulse
    bbot = btop + 110
    draw.rounded_rectangle([110, btop, W1 - 110, bbot], radius=34, fill=(255, 75, 0), outline=(255, 160, 90), width=3)
    draw_fitted_text(draw, (W1//2, (btop + bbot)//2), "TESTAR GRÁTIS AGORA", 800, 44, (255, 255, 255), True)

    draw_fitted_text(draw, (W1//2, 675), "Acesse no seu navegador:", 900, 32, (160, 160, 170), True)
    draw_fitted_text(draw, (W1//2, 740), "www.clonavoz.com.br", 920, 56, (255, 125, 30), True)
    draw_auto_badge(draw, W1, "Instagram: @clonavozoficial", 880, 34, (22, 22, 28), (180, 180, 195), (255, 255, 255), pad_x=50, pad_y=16)


# --- Video A (Comercial Principal) 1:1 ---
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

    elif t < 18.5:
        draw_auto_badge(draw, W1, "ONDE VOCÊ PODE USAR?", 140, 28, (16, 25, 38), (0, 165, 255), (110, 205, 255))
        draw_fitted_text(draw, (W1//2, 230), "Turbine sua Produção:", 920, 58, (255, 255, 255), True)

        cards = [
            ("CANAIS DARK NO YOUTUBE", "Histórias, mistérios e curiosidades sem microfone"),
            ("REELS, SHORTS & TIKTOK", "Áudios persuasivos com retenção máxima"),
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


# --- Video B (Canal Dark Passo a Passo) 1:1 ---
def frame_passo_a_passo_1x1(t, idx):
    img = bg_1x1_purple.copy()
    draw = ImageDraw.Draw(img)
    draw_header_footer_1x1(draw)

    if t < 4.2:
        draw_auto_badge(draw, W1, "TUTORIAL CANAL DARK", 145, 28, (30, 18, 40), (180, 80, 255), (210, 150, 255))
        draw_fitted_text(draw, (W1//2, 255), "COMO CRIAR UM", 920, 64, (255, 255, 255), True)
        draw_fitted_text(draw, (W1//2, 340), "CANAL DARK", 920, 74, (255, 95, 20), True)
        draw_fitted_text(draw, (W1//2, 420), "EM 60 SEGUNDOS!", 920, 52, (255, 255, 255), True)

        draw.rounded_rectangle([85, 510, W1 - 85, 840], radius=28, fill=(22, 18, 26), outline=(180, 80, 255), width=2)
        draw_fitted_text(draw, (W1//2, 585), "• Sem Usar Microfone", 820, 38, (220, 220, 230), True)
        draw_fitted_text(draw, (W1//2, 670), "• Sem Mostrar o Rosto", 820, 44, (255, 140, 40), True)
        draw_fitted_text(draw, (W1//2, 755), "• 100% no Piloto Automático", 820, 38, (0, 230, 130), True)

    elif t < 10.5:
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

    elif t < 16.5:
        draw_auto_badge(draw, W1, "PASSO 3 & PASSO 4", 145, 28, (20, 25, 35), (0, 160, 255), (100, 200, 255))

        # Step 3 - 100% Fitted inside card!
        draw.rounded_rectangle([75, 235, W1 - 75, 525], radius=26, fill=(18, 18, 24), outline=(0, 160, 255), width=2)
        draw_fitted_text(draw, (W1//2, 305), "PASSO 3: DOWNLOAD DIRETO", W1 - 210, 46, (80, 190, 255), True)
        draw_fitted_text(draw, (W1//2, 385), "Baixe o áudio em WAV ou MP3", W1 - 210, 36, (215, 215, 225), True)
        draw_fitted_text(draw, (W1//2, 455), "Arquivo pronto direto no seu dispositivo", W1 - 210, 30, (165, 165, 175), False)

        # Step 4 - 100% Fitted inside card!
        draw.rounded_rectangle([75, 565, W1 - 75, 855], radius=26, fill=(18, 18, 24), outline=(255, 80, 120), width=2)
        draw_fitted_text(draw, (W1//2, 635), "PASSO 4: JUNTE NO CAPCUT", W1 - 210, 46, (255, 100, 140), True)
        draw_fitted_text(draw, (W1//2, 715), "Adicione vídeos de fundo gratuitos", W1 - 210, 36, (215, 215, 225), True)
        draw_fitted_text(draw, (W1//2, 785), "Seu vídeo está pronto para viralizar!", W1 - 210, 30, (165, 165, 175), False)

    else:
        draw_cta_1x1(draw, t)
    return img


# --- Video C (3 IAs Secretas) 1:1 ---
def frame_3_ias_1x1(t, idx):
    img = bg_1x1_orange.copy()
    draw = ImageDraw.Draw(img)
    draw_header_footer_1x1(draw)

    if t < 4.0:
        draw_auto_badge(draw, W1, "SITES SECRETOS DE IA", 145, 28, (20, 25, 40), (0, 160, 255), (100, 200, 255))
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

    elif t < 16.5:
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


# --- Video D (Teste Cego Humano vs IA) 1:1 ---
def frame_teste_cego_1x1(t, idx):
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

    elif t < 25.0:
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
        draw.rounded_rectangle([110, btop, W1 - 110, bbot], radius=34, fill=(255, 75, 0), outline=(255, 160, 90), width=3)
        draw_fitted_text(draw, (W1//2, (btop + bbot)//2), "TESTAR GRÁTIS AGORA", 800, 44, (255, 255, 255), True)

        draw_fitted_text(draw, (W1//2, 650), "www.clonavoz.com.br", 920, 54, (255, 125, 30), True)
        draw_auto_badge(draw, W1, "Recarga Fácil no PIX por R$ 9,90", 770, 32, (22, 35, 26), (0, 220, 120), (0, 240, 140), pad_x=45, pad_y=14)
        draw_auto_badge(draw, W1, "Instagram: @clonavozoficial", 895, 32, (22, 22, 28), (180, 180, 195), (255, 255, 255), pad_x=45, pad_y=14)
    return img


# ==============================================================================
# GERADOR 9:16 (1080 x 1920) CORRIGIDO PARA TIKTOK / REELS TELA CHEIA
# ==============================================================================
W9, H9 = 1080, 1920
bg_9x16_purple = make_base_bg(W9, H9, (200, 60, 255, 38))

def frame_passo_a_passo_9x16_fixed(t, idx):
    img = bg_9x16_purple.copy()
    draw = ImageDraw.Draw(img)
    draw.text((W9//2, 130), "CLONAVOZ.COM.BR", fill=(255, 120, 40), font=get_font(32, True), anchor="mm")
    draw.line([(W9//2 - 150, 160), (W9//2 + 150, 160)], fill=(255, 85, 0), width=2)
    draw.text((W9//2, 1830), "Desenvolvido por nx49 System Development", fill=(100, 100, 115), font=get_font(26, False), anchor="mm")

    if t < 4.2:
        draw_auto_badge(draw, W9, "TUTORIAL CANAL DARK", 280, 32, (30, 18, 40), (180, 80, 255), (210, 150, 255))
        draw_fitted_text(draw, (W9//2, 470), "COMO CRIAR UM", 920, 80, (255, 255, 255), True)
        draw_fitted_text(draw, (W9//2, 570), "CANAL DARK", 920, 84, (255, 90, 20), True)
        draw_fitted_text(draw, (W9//2, 670), "EM 60 SEGUNDOS!", 920, 60, (255, 255, 255), True)

        draw.rounded_rectangle([90, 840, W9-90, 1200], radius=32, fill=(22, 18, 26), outline=(180, 80, 255), width=2)
        draw_fitted_text(draw, (W9//2, 930), "Sem Microfone", 820, 42, (220, 220, 230), True)
        draw_fitted_text(draw, (W9//2, 1010), "Sem Mostrar o Rosto", 820, 56, (255, 140, 40), True)
        draw_fitted_text(draw, (W9//2, 1090), "100% no Piloto Automático", 820, 42, (0, 230, 130), True)

    elif t < 10.5:
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

    elif t < 16.5:
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
        draw_auto_badge(draw, W9, "CRIE SEU CANAL HOJE MESMO", 270, 32, (16, 36, 22), (0, 220, 110), (0, 255, 130))
        draw_fitted_text(draw, (W9//2, 420), "Recarga Fácil no PIX por Apenas", 900, 42, (195, 195, 205), True)
        draw_fitted_text(draw, (W9//2, 535), "R$ 9,90", 900, 84, (0, 255, 135), True)
        draw_fitted_text(draw, (W9//2, 625), "Créditos Imediatos sem Assinatura", 900, 34, (175, 175, 185), False)

        pulse = int(math.sin(t * 6) * 4)
        btop = 750 + pulse
        bbot = btop + 130
        draw.rounded_rectangle([90, btop, W9 - 90, bbot], radius=38, fill=(255, 75, 0), outline=(255, 155, 80), width=3)
        draw_fitted_text(draw, (W9//2, (btop + bbot) // 2), "TESTAR GRÁTIS AGORA", 800, 48, (255, 255, 255), True)

        draw_fitted_text(draw, (W9//2, 1020), "Acesse no seu navegador:", 900, 42, (160, 160, 170), True)
        draw_fitted_text(draw, (W9//2, 1105), "www.clonavoz.com.br", 900, 62, (255, 125, 30), True)
        draw_auto_badge(draw, W9, "Instagram: @clonavozoficial", 1320, 42, (22, 22, 28), (180, 180, 195), (255, 255, 255), pad_x=60, pad_y=22)
    return img


if __name__ == "__main__":
    wav_comercial = os.path.join(OUTPUT_DIR, "audio_faber_1792352807972.wav")
    wav_3_ias = os.path.join(OUTPUT_DIR, "audio_faber_1792355976915.wav")
    wav_passo = os.path.join(OUTPUT_DIR, "audio_dii_1792356208698.wav")
    wav_teste = os.path.join(OUTPUT_DIR, "audio_faber_1792356450956.wav")

    bgm_inspire = os.path.join(STATIC_DIR, "bgm", "bgm_inspire.mp3")
    bgm_corp = os.path.join(STATIC_DIR, "bgm", "bgm_corporate.mp3")
    bgm_cine = os.path.join(STATIC_DIR, "bgm", "bgm_cinematic.mp3")

    # 1. Generate all 4 SEO-named 1:1 (1080x1080) videos directly on Desktop
    encode_video_from_generator(
        W1, H1, frame_comercial_1x1, wav_comercial, bgm_inspire,
        os.path.join(DESKTOP_DIR, "clonavoz-recarga-facil-pix-gerador-voz-ia.mp4")
    )
    encode_video_from_generator(
        W1, H1, frame_passo_a_passo_1x1, wav_passo, bgm_inspire,
        os.path.join(DESKTOP_DIR, "video-canal-dark-passo-a-passo-clonavoz-recarga-facil.mp4")
    )
    encode_video_from_generator(
        W1, H1, frame_3_ias_1x1, wav_3_ias, bgm_corp,
        os.path.join(DESKTOP_DIR, "3-ias-secretas-canal-dark-clonavoz-recarga-facil.mp4")
    )
    encode_video_from_generator(
        W1, H1, frame_teste_cego_1x1, wav_teste, bgm_cine,
        os.path.join(DESKTOP_DIR, "teste-cego-voz-humana-vs-ia-clonavoz-locucao.mp4")
    )

    # 2. Generate the fixed 9:16 video 2 and move all 9:16 videos to TikTok folder with SEO names
    encode_video_from_generator(
        W9, H9, frame_passo_a_passo_9x16_fixed, wav_passo, bgm_inspire,
        os.path.join(TIKTOK_DIR, "video-canal-dark-passo-a-passo-clonavoz-recarga-facil.mp4")
    )

    old_v1 = os.path.join(DESKTOP_DIR, "video_1_segredo_revelado.mp4")
    if os.path.exists(old_v1):
        shutil.move(old_v1, os.path.join(TIKTOK_DIR, "3-ias-secretas-canal-dark-clonavoz-recarga-facil.mp4"))

    old_v3 = os.path.join(DESKTOP_DIR, "video_3_teste_cego_humano_vs_ia.mp4")
    if os.path.exists(old_v3):
        shutil.move(old_v3, os.path.join(TIKTOK_DIR, "teste-cego-voz-humana-vs-ia-clonavoz-locucao.mp4"))

    old_v2 = os.path.join(DESKTOP_DIR, "video_2_canal_dark_passo_a_passo.mp4")
    if os.path.exists(old_v2):
        os.remove(old_v2)

    old_comercial = os.path.join(STATIC_DIR, "comercial_clonavoz_reels.mp4")
    if os.path.exists(old_comercial):
        shutil.copyfile(old_comercial, os.path.join(TIKTOK_DIR, "clonavoz-recarga-facil-pix-gerador-voz-ia.mp4"))

    shutil.rmtree(SCRATCH_ROOT, ignore_errors=True)
    print("\n=== TODOS OS VÍDEOS 1:1 E 9:16 COM NOMES SEO CONCLUÍDOS! ===")
