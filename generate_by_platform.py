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
SCRATCH_ROOT = os.path.join(BASE_DIR, "scratch_platforms")

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

def draw_auto_badge(draw, width_canvas, text, y_center, start_size, fill_bg, outline_color, text_color, pad_x=45, pad_y=16, border_width=2):
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
    cx, cy = w // 2, int(h * 0.45)
    g_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=glow_color)
    glow = glow.filter(ImageFilter.GaussianBlur(95))
    img = Image.alpha_composite(img, glow)
    return img.convert("RGB")

def encode_video(w, h, draw_fn, wav_path, bgm_path, output_path):
    info = sf.info(wav_path)
    dur = info.duration
    total_sec = math.ceil(dur + 1.2)
    total_frames = int(total_sec * FPS)

    frames_dir = os.path.join(SCRATCH_ROOT, "frames")
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir, exist_ok=True)

    print(f"Renderizando {os.path.basename(output_path)} ({w}x{h}, {total_frames} frames)...")
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
        output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"OK -> {output_path}")


# ==============================================================================
# GERADOR 9:16 PARAMETRIZADO POR PLATAFORMA ("TIKTOK" vs "YOUTUBE")
# ==============================================================================
W9, H9 = 1080, 1920
bg_9_orange = make_base_bg(W9, H9, (255, 75, 0, 42))
bg_9_purple = make_base_bg(W9, H9, (200, 60, 255, 38))
bg_9_red = make_base_bg(W9, H9, (255, 50, 20, 38))

def draw_header_footer_9x16(draw, platform):
    if platform == "TIKTOK":
        # Zero links, zero mention of Instagram/YouTube
        draw.text((W9//2, 130), "CLONAVOZ AI • VOZ NEURAL", fill=(255, 120, 40), font=get_font(32, True), anchor="mm")
    else:
        # YouTube allows domain
        draw.text((W9//2, 130), "CLONAVOZ.COM.BR", fill=(255, 120, 40), font=get_font(32, True), anchor="mm")
    draw.line([(W9//2 - 160, 160), (W9//2 + 160, 160)], fill=(255, 85, 0), width=2)
    draw.text((W9//2, 1830), "Desenvolvido por nx49 System Development", fill=(100, 100, 115), font=get_font(26, False), anchor="mm")

def draw_cta_9x16(draw, t, platform):
    draw_auto_badge(draw, W9, "SEM ASSINATURAS • RECARGA NO PIX", 270, 32, (16, 36, 22), (0, 220, 110), (0, 255, 130), pad_x=55, pad_y=18)
    draw_fitted_text(draw, (W9//2, 420), "Comece Agora Por Apenas", 900, 42, (195, 195, 205), True)
    draw_fitted_text(draw, (W9//2, 535), "R$ 9,90", 900, 88, (0, 255, 135), True)
    draw_fitted_text(draw, (W9//2, 625), "No PIX com Liberação Imediata", 900, 34, (175, 175, 185), False)

    pulse = int(math.sin(t * 6) * 4)
    btop = 750 + pulse
    bbot = btop + 130
    draw.rounded_rectangle([90, btop, W9 - 90, bbot], radius=38, fill=(255, 75, 0), outline=(255, 155, 80), width=3)

    if platform == "TIKTOK":
        draw_fitted_text(draw, (W9//2, (btop + bbot) // 2), "CLIQUE NO LINK DO PERFIL!", 820, 46, (255, 255, 255), True)
        draw_fitted_text(draw, (W9//2, 1020), "Siga Nosso Perfil Oficial:", 900, 40, (160, 160, 170), True)
        draw_fitted_text(draw, (W9//2, 1105), "@clonavozoficial", 900, 62, (255, 125, 30), True)
        draw_auto_badge(draw, W9, "Teste Grátis no Link da Bio!", 1320, 40, (22, 22, 28), (180, 180, 195), (255, 255, 255), pad_x=60, pad_y=22)
    else:
        # YOUTUBE
        draw_fitted_text(draw, (W9//2, (btop + bbot) // 2), "TESTAR GRÁTIS AGORA", 820, 48, (255, 255, 255), True)
        draw_fitted_text(draw, (W9//2, 1020), "Acesse no seu navegador:", 900, 40, (160, 160, 170), True)
        draw_fitted_text(draw, (W9//2, 1105), "www.clonavoz.com.br", 900, 62, (255, 125, 30), True)
        draw_auto_badge(draw, W9, "Inscreva-se no Canal e Deixe seu Like!", 1320, 38, (35, 18, 18), (255, 60, 60), (255, 255, 255), pad_x=55, pad_y=22)


def make_comercial_9x16(platform):
    def fn(t, idx):
        img = bg_9_orange.copy()
        draw = ImageDraw.Draw(img)
        draw_header_footer_9x16(draw, platform)

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
            draw_cta_9x16(draw, t, platform)
        return img
    return fn


def make_passo_9x16(platform):
    def fn(t, idx):
        img = bg_9_purple.copy()
        draw = ImageDraw.Draw(img)
        draw_header_footer_9x16(draw, platform)

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
            draw_cta_9x16(draw, t, platform)
        return img
    return fn


def make_3ias_9x16(platform):
    def fn(t, idx):
        img = bg_9_orange.copy()
        draw = ImageDraw.Draw(img)
        draw_header_footer_9x16(draw, platform)

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
            draw_cta_9x16(draw, t, platform)
        return img
    return fn


def make_teste_9x16(platform):
    def fn(t, idx):
        img = bg_9_red.copy()
        draw = ImageDraw.Draw(img)
        draw_header_footer_9x16(draw, platform)

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
            draw_cta_9x16(draw, t, platform)
        return img
    return fn


if __name__ == "__main__":
    bgm_inspire = os.path.join(STATIC_DIR, "bgm", "bgm_inspire.mp3")
    bgm_corp = os.path.join(STATIC_DIR, "bgm", "bgm_corporate.mp3")
    bgm_cine = os.path.join(STATIC_DIR, "bgm", "bgm_cinematic.mp3")

    # Audio files without URLs (for TikTok & Instagram)
    wav_com_nolink = os.path.join(OUTPUT_DIR, "audio_faber_1792374880752.wav")
    wav_pas_nolink = os.path.join(OUTPUT_DIR, "audio_dii_1792374886152.wav")
    wav_3ia_nolink = os.path.join(OUTPUT_DIR, "audio_faber_1792374888328.wav")
    wav_tst_nolink = os.path.join(OUTPUT_DIR, "audio_faber_1792374891221.wav")

    # Audio files with URLs (for YouTube)
    wav_com_yt = os.path.join(OUTPUT_DIR, "audio_faber_1792352807972.wav")
    wav_pas_yt = os.path.join(OUTPUT_DIR, "audio_dii_1792356208698.wav")
    wav_3ia_yt = os.path.join(OUTPUT_DIR, "audio_faber_1792355976915.wav")
    wav_tst_yt = os.path.join(OUTPUT_DIR, "audio_faber_1792356450956.wav")

    # 1. Organize 1_INSTAGRAM (already rendered 1:1 without links/other platforms)
    old_ig_dir = os.path.join(MKT_ROOT, "instagran")
    if os.path.exists(old_ig_dir):
        for f in os.listdir(old_ig_dir):
            src = os.path.join(old_ig_dir, f)
            if f.endswith(".mp4"):
                shutil.copyfile(src, os.path.join(DIR_INSTAGRAM, "Videos_1x1", f))
            elif f.endswith(".png"):
                shutil.copyfile(src, os.path.join(DIR_INSTAGRAM, "Capas_1x1", f))

    # 2. Render 2_TIKTOK (9:16 exclusive for TikTok - ZERO Instagram mention, ZERO URLs)
    print("\n--- Renderizando Vídeos Exclusivos para 2_TIKTOK (Sem citar Instagram e Sem Links) ---")
    encode_video(W9, H9, make_comercial_9x16("TIKTOK"), wav_com_nolink, bgm_inspire,
                 os.path.join(DIR_TIKTOK, "Videos_9x16", "clonavoz-recarga-facil-pix-gerador-voz-ia.mp4"))
    encode_video(W9, H9, make_passo_9x16("TIKTOK"), wav_pas_nolink, bgm_inspire,
                 os.path.join(DIR_TIKTOK, "Videos_9x16", "video-canal-dark-passo-a-passo-clonavoz-recarga-facil.mp4"))
    encode_video(W9, H9, make_3ias_9x16("TIKTOK"), wav_3ia_nolink, bgm_corp,
                 os.path.join(DIR_TIKTOK, "Videos_9x16", "3-ias-secretas-canal-dark-clonavoz-recarga-facil.mp4"))
    encode_video(W9, H9, make_teste_9x16("TIKTOK"), wav_tst_nolink, bgm_cine,
                 os.path.join(DIR_TIKTOK, "Videos_9x16", "teste-cego-voz-humana-vs-ia-clonavoz-locucao.mp4"))

    # Copy 9:16 covers to TikTok
    old_vcapas = os.path.join(MKT_ROOT, "Capas_de_Alta_Conversao", "Capas_Reels_TikTok_Shorts_9x16")
    if os.path.exists(old_vcapas):
        for f in os.listdir(old_vcapas):
            shutil.copyfile(os.path.join(old_vcapas, f), os.path.join(DIR_TIKTOK, "Capas_9x16", f))

    # 3. Render 3_YOUTUBE (9:16 Shorts exclusive for YouTube - ZERO Instagram/TikTok mention)
    print("\n--- Renderizando Vídeos Exclusivos para 3_YOUTUBE (Sem citar Instagram/TikTok) ---")
    encode_video(W9, H9, make_comercial_9x16("YOUTUBE"), wav_com_yt, bgm_inspire,
                 os.path.join(DIR_YOUTUBE, "Videos_Shorts_9x16", "clonavoz-recarga-facil-pix-gerador-voz-ia.mp4"))
    encode_video(W9, H9, make_passo_9x16("YOUTUBE"), wav_pas_yt, bgm_inspire,
                 os.path.join(DIR_YOUTUBE, "Videos_Shorts_9x16", "video-canal-dark-passo-a-passo-clonavoz-recarga-facil.mp4"))
    encode_video(W9, H9, make_3ias_9x16("YOUTUBE"), wav_3ia_yt, bgm_corp,
                 os.path.join(DIR_YOUTUBE, "Videos_Shorts_9x16", "3-ias-secretas-canal-dark-clonavoz-recarga-facil.mp4"))
    encode_video(W9, H9, make_teste_9x16("YOUTUBE"), wav_tst_yt, bgm_cine,
                 os.path.join(DIR_YOUTUBE, "Videos_Shorts_9x16", "teste-cego-voz-humana-vs-ia-clonavoz-locucao.mp4"))

    # Copy 16:9 Thumbnails to YouTube
    old_thumbs = os.path.join(MKT_ROOT, "Capas_de_Alta_Conversao", "Thumbnails_YouTube_16x9")
    if os.path.exists(old_thumbs):
        for f in os.listdir(old_thumbs):
            shutil.copyfile(os.path.join(old_thumbs, f), os.path.join(DIR_YOUTUBE, "Thumbnails_16x9", f))

    # Remove old mixed directories so there is zero confusion
    for old_d in ["instagran", "Videos_Instagram_1x1", "Videos_Instagram_Reels_9x16_Sem_Link", "Videos_TikTok_Tela_Cheia", "Capas_de_Alta_Conversao"]:
        p = os.path.join(MKT_ROOT, old_d)
        if os.path.exists(p):
            shutil.rmtree(p, ignore_errors=True)

    shutil.rmtree(SCRATCH_ROOT, ignore_errors=True)
    print("\n=== SEPARAÇÃO TOTAL POR PLATAFORMA CONCLUÍDA COM SUCESSO! ===")
