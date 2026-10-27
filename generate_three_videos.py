import os
import sys
import math
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf
import tts_engine

BASE_DIR = r"e:\A2\projetos\gerador de voz com texto"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
STATIC_DIR = os.path.join(BASE_DIR, "static")
SCRATCH_ROOT = os.path.join(BASE_DIR, "scratch_campaign")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCRATCH_ROOT, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920
FPS = 30

def get_font(size, bold=False):
    win_fonts = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"] if bold else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
    for f in win_fonts:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_brand = get_font(32, bold=True)
font_badge = get_font(32, bold=True)
font_subtitle = get_font(42, bold=True)
font_body = get_font(34, bold=False)
font_title = get_font(62, bold=True)
font_huge = get_font(84, bold=True)
font_cta = get_font(48, bold=True)
font_watermark = get_font(26, bold=False)

logo_path = os.path.join(STATIC_DIR, "logo_perfil_instagram.png")
if os.path.exists(logo_path):
    logo_base = Image.open(logo_path).convert("RGBA")
else:
    logo_base = Image.new("RGBA", (300, 300), (255, 85, 0, 255))

def draw_auto_badge(draw, text, y_center, font, fill_bg, outline_color, text_color, pad_x=45, pad_y=16, border_width=2):
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

def render_and_encode(frames_generator, total_frames, narration_wav, bgm_file, desktop_filename):
    scratch_dir = os.path.join(SCRATCH_ROOT, "temp_frames")
    if os.path.exists(scratch_dir):
        shutil.rmtree(scratch_dir)
    os.makedirs(scratch_dir, exist_ok=True)

    print(f"Renderizando {total_frames} frames PNG...")
    for i in range(total_frames):
        t_sec = i / FPS
        frame_img = frames_generator(t_sec, i)
        frame_img.save(os.path.join(scratch_dir, f"frame_{i:05d}.png"))
        if i % 90 == 0:
            print(f"Progresso: {i}/{total_frames} ({(i/total_frames)*100:.0f}%)")

    raw_video = os.path.join(SCRATCH_ROOT, "temp_video.mp4")
    cmd_video = [
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", os.path.join(scratch_dir, "frame_%05d.png"),
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        raw_video
    ]
    subprocess.run(cmd_video, check=True)

    mixed_audio = os.path.join(SCRATCH_ROOT, "temp_audio.m4a")
    cmd_audio = [
        "ffmpeg", "-y",
        "-i", narration_wav,
        "-i", bgm_file,
        "-filter_complex",
        "[0:a]volume=1.35[v];[1:a]volume=0.15,aloop=loop=-1:size=2e+09[bgm];[v][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "[aout]", "-c:a", "aac", "-b:a", "192k",
        mixed_audio
    ]
    subprocess.run(cmd_audio, check=True)

    dest_desktop = os.path.join(r"C:\Users\User\Desktop", desktop_filename)
    cmd_final = [
        "ffmpeg", "-y",
        "-i", raw_video, "-i", mixed_audio,
        "-c:v", "copy", "-c:a", "aac", "-shortest",
        dest_desktop
    ]
    subprocess.run(cmd_final, check=True)

    shutil.rmtree(scratch_dir)
    print(f"==> Vídeo salvo com sucesso em: {dest_desktop}\n")


# ==============================================================================
# VÍDEO 1 (FORMATO A): O Segredo Revelado (3 IAs que você precisa conhecer)
# ==============================================================================
def generate_video_1():
    print("\n==========================================")
    print("GERANDO VÍDEO 1: O Segredo Revelado (3 IAs)")
    print("==========================================")
    
    script = (
        "Três sites de inteligência artificial que você precisa conhecer hoje. "
        "Número um: ChatGPT, para criar roteiros e histórias em segundos. "
        "Número dois: CapCut, para editar seus vídeos de graça no celular. "
        "E número três: Clonavoz! A inteligência artificial brasileira que narra seus vídeos com voz humana sem pagar em dólar. "
        "Recarregue no Pícs por apenas nove reais e noventa. "
        "Acesse clonavoz ponto com ponto b r, e teste grátis!"
    )
    res = tts_engine.synthesize_text(script, voice_key="faber", speed=0.98)
    wav_path = res["file_path"]
    dur = res["duration_seconds"]
    total_sec = math.ceil(dur + 1.2)
    total_frames = int(total_sec * FPS)

    def draw_frame(t, idx):
        img = Image.new("RGBA", (WIDTH, HEIGHT), (10, 10, 14, 255))
        draw = ImageDraw.Draw(img)

        # Pulse glow
        pulse = math.sin(t * 3) * 0.15 + 0.85
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glow)
        radius = int(450 * pulse)
        g_draw.ellipse([WIDTH//2 - radius, 700 - radius, WIDTH//2 + radius, 700 + radius], fill=(255, 80, 0, 35))
        glow = glow.filter(ImageFilter.GaussianBlur(100))
        img = Image.alpha_composite(img, glow)
        draw = ImageDraw.Draw(img)

        draw.text((WIDTH//2, 130), "CLONAVOZ.COM.BR", fill=(255, 120, 40, 230), font=font_brand, anchor="mm")
        draw.line([(WIDTH//2 - 150, 160), (WIDTH//2 + 150, 160)], fill=(255, 85, 0, 160), width=2)

        if t < 4.0:
            draw_auto_badge(draw, "SITES SECRETOS DE IA", 280, font_badge, (20, 25, 40, 230), (0, 160, 255, 200), (100, 200, 255))
            draw.text((WIDTH//2, 480), "3 FERRAMENTAS", fill=(255, 255, 255), font=font_huge, anchor="mm")
            draw.text((WIDTH//2, 580), "QUE VOCÊ PRECISA", fill=(255, 100, 20), font=font_title, anchor="mm")
            draw.text((WIDTH//2, 660), "CONHECER HOJE!", fill=(255, 255, 255), font=font_huge, anchor="mm")
            
            draw.rounded_rectangle([100, 850, WIDTH-100, 1250], radius=32, fill=(18, 18, 24, 235), outline=(255, 85, 0, 100), width=2)
            draw.text((WIDTH//2, 950), "1. Roteiros em Segundos", fill=(200, 200, 210), font=font_subtitle, anchor="mm")
            draw.text((WIDTH//2, 1050), "2. Edição Automática", fill=(200, 200, 210), font=font_subtitle, anchor="mm")
            draw.text((WIDTH//2, 1150), "3. Voz Neural no PIX", fill=(255, 120, 30), font=font_title, anchor="mm")

        elif t < 8.5:
            draw_auto_badge(draw, "FERRAMENTA 1 & 2", 280, font_badge, (25, 25, 30, 230), (255, 255, 255, 80), (220, 220, 230))
            
            # Card 1
            draw.rounded_rectangle([90, 420, WIDTH-90, 720], radius=30, fill=(20, 20, 26, 235), outline=(0, 200, 120, 150), width=2)
            draw.text((150, 490), "1. CHATGPT", fill=(0, 230, 130), font=font_title, anchor="lm")
            draw.text((150, 570), "Criação de histórias e roteiros", fill=(200, 200, 210), font=font_subtitle, anchor="lm")
            draw.text((150, 640), "Pronto em menos de 10 segundos", fill=(160, 160, 170), font=font_body, anchor="lm")

            # Card 2
            draw.rounded_rectangle([90, 800, WIDTH-90, 1100], radius=30, fill=(20, 20, 26, 235), outline=(0, 160, 255, 150), width=2)
            draw.text((150, 870), "2. CAPCUT", fill=(80, 190, 255), font=font_title, anchor="lm")
            draw.text((150, 950), "Edição de vídeo profissional", fill=(200, 200, 210), font=font_subtitle, anchor="lm")
            draw.text((150, 1020), "Grátis no celular e computador", fill=(160, 160, 170), font=font_body, anchor="lm")

            draw.text((WIDTH//2, 1320), "E agora, o mais importante...", fill=(255, 120, 30), font=font_subtitle, anchor="mm")

        elif t < 16.5:
            draw_auto_badge(draw, "A FERRAMENTA SECRETA", 270, font_badge, (35, 18, 12, 230), (255, 100, 0, 200), (255, 140, 40))
            
            logo_w = int(220 + math.sin(t * 4) * 10)
            logo_resized = logo_base.resize((logo_w, logo_w), Image.Resampling.LANCZOS)
            img.paste(logo_resized, (WIDTH//2 - logo_w//2, 380), logo_resized)
            draw = ImageDraw.Draw(img)

            draw.text((WIDTH//2, 690), "3. CLONAVOZ AI", fill=(255, 255, 255), font=font_huge, anchor="mm")
            draw.text((WIDTH//2, 780), "A Voz Neural 100% Brasileira", fill=(255, 110, 20), font=font_title, anchor="mm")
            draw.text((WIDTH//2, 850), "Sem assinaturas abusivas em dólar", fill=(200, 200, 210), font=font_subtitle, anchor="mm")

            # Animated Soundwave Bars
            bar_count = 22
            bar_w = 16
            spacing = 18
            start_x = WIDTH//2 - (bar_count * (bar_w + spacing)) // 2
            for b in range(bar_count):
                bh = int(30 + 120 * abs(math.sin(t * 8 + b * 0.45)))
                bx = start_x + b * (bar_w + spacing)
                by = 1060 - bh // 2
                draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=7, fill=(255, int(80 + 120 * (b/bar_count)), 0))

            draw.text((WIDTH//2, 1260), "Narre seus vídeos em segundos!", fill=(255, 255, 255), font=font_subtitle, anchor="mm")

        else:
            draw_auto_badge(draw, "SEM ASSINATURAS • RECARGA NO PIX", 270, font_badge, (16, 36, 22, 235), (0, 220, 110, 190), (0, 255, 130), pad_x=55, pad_y=18)
            draw.text((WIDTH//2, 420), "Recarregue a Partir de", fill=(195, 195, 205), font=font_subtitle, anchor="mm")
            draw.text((WIDTH//2, 535), "R$ 9,90", fill=(0, 255, 135), font=font_huge, anchor="mm")
            draw.text((WIDTH//2, 625), "No PIX com Liberação Imediata", fill=(175, 175, 185), font=font_body, anchor="mm")

            cta_pulse = math.sin(t * 6) * 4
            btn_top = int(750 + cta_pulse)
            btn_bottom = btn_top + 130
            draw.rounded_rectangle([90, btn_top, WIDTH - 90, btn_bottom], radius=38, fill=(255, 75, 0), outline=(255, 155, 80), width=3)
            draw.text((WIDTH//2, (btn_top + btn_bottom) // 2), "TESTAR GRÁTIS AGORA", fill=(255, 255, 255), font=font_cta, anchor="mm")

            draw.text((WIDTH//2, 1020), "Acesse no seu navegador:", fill=(160, 160, 170), font=font_subtitle, anchor="mm")
            draw.text((WIDTH//2, 1105), "www.clonavoz.com.br", fill=(255, 125, 30), font=font_title, anchor="mm")

            draw_auto_badge(draw, "Instagram: @clonavozoficial", 1320, font_subtitle, (22, 22, 28, 230), (255, 255, 255, 60), (255, 255, 255), pad_x=60, pad_y=22)

        draw.text((WIDTH//2, 1830), "Desenvolvido por nx49 System Development", fill=(100, 100, 115), font=font_watermark, anchor="mm")
        return img

    bgm_path = os.path.join(STATIC_DIR, "bgm", "bgm_corporate.mp3")
    render_and_encode(draw_frame, total_frames, wav_path, bgm_path, "video_1_segredo_revelado.mp4")


# ==============================================================================
# VÍDEO 2 (FORMATO B): Passo a Passo Canal Dark (Voz Feminina Dii)
# ==============================================================================
def generate_video_2():
    print("\n=======================================================")
    print("GERANDO VÍDEO 2: Canal Dark em 60 Segundos (Voz Dii)")
    print("=======================================================")
    
    script = (
        "Como criar um canal Dark lucrativo no You Tube em menos de um minuto. "
        "Primeiro passo: peça um roteiro de curiosidades para o ChatGPT. "
        "Segundo passo: cole o texto no Clonavoz e escolha a voz neural brasileira. "
        "Terceiro passo: baixe o áudio em alta definição no seu computador ou celular. "
        "Quarto passo: junte com vídeos de fundo no CapCut e pronto! "
        "Sem microfone e sem mostrar o rosto. Teste grátis em clonavoz ponto com ponto b r!"
    )
    res = tts_engine.synthesize_text(script, voice_key="dii", speed=1.0)
    wav_path = res["file_path"]
    dur = res["duration_seconds"]
    total_sec = math.ceil(dur + 1.2)
    total_frames = int(total_sec * FPS)

    def draw_frame(t, idx):
        img = Image.new("RGBA", (WIDTH, HEIGHT), (12, 10, 16, 255))
        draw = ImageDraw.Draw(img)

        # Pulse glow purple/orange
        pulse = math.sin(t * 3) * 0.15 + 0.85
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glow)
        radius = int(460 * pulse)
        g_draw.ellipse([WIDTH//2 - radius, 650 - radius, WIDTH//2 + radius, 650 + radius], fill=(220, 60, 20, 35))
        glow = glow.filter(ImageFilter.GaussianBlur(100))
        img = Image.alpha_composite(img, glow)
        draw = ImageDraw.Draw(img)

        draw.text((WIDTH//2, 130), "CLONAVOZ.COM.BR", fill=(255, 120, 40, 230), font=font_brand, anchor="mm")
        draw.line([(WIDTH//2 - 150, 160), (WIDTH//2 + 150, 160)], fill=(255, 85, 0, 160), width=2)

        if t < 4.2:
            draw_auto_badge(draw, "TUTORIAL CANAL DARK", 280, font_badge, (30, 18, 40, 230), (180, 80, 255, 200), (210, 150, 255))
            draw.text((WIDTH//2, 470), "COMO CRIAR UM", fill=(255, 255, 255), font=font_huge, anchor="mm")
            draw.text((WIDTH//2, 570), "CANAL DARK", fill=(255, 90, 20), font=font_huge, anchor="mm")
            draw.text((WIDTH//2, 670), "EM 60 SEGUNDOS!", fill=(255, 255, 255), font=font_title, anchor="mm")

            draw.rounded_rectangle([90, 840, WIDTH-90, 1200], radius=32, fill=(22, 18, 26, 235), outline=(180, 80, 255, 100), width=2)
            draw.text((WIDTH//2, 930), "Sem Microfone", fill=(220, 220, 230), font=font_subtitle, anchor="mm")
            draw.text((WIDTH//2, 1010), "Sem Mostrar o Rosto", fill=(255, 140, 40), font=font_title, anchor="mm")
            draw.text((WIDTH//2, 1090), "100% no Piloto Automático", fill=(0, 230, 130), font=font_subtitle, anchor="mm")

        elif t < 10.5:
            draw_auto_badge(draw, "PASSO 1 & 2", 280, font_badge, (25, 20, 30, 230), (255, 120, 40, 180), (255, 160, 70))
            
            # Step 1
            draw.rounded_rectangle([80, 420, WIDTH-80, 720], radius=28, fill=(18, 18, 24, 235), outline=(0, 200, 130, 150), width=2)
            draw.text((130, 490), "PASSO 1: ROTEIRO", fill=(0, 230, 130), font=font_title, anchor="lm")
            draw.text((130, 570), "Peça a história ao ChatGPT", fill=(210, 210, 220), font=font_subtitle, anchor="lm")
            draw.text((130, 640), "Pronto em menos de 10 segundos", fill=(160, 160, 170), font=font_body, anchor="lm")

            # Step 2
            draw.rounded_rectangle([80, 800, WIDTH-80, 1150], radius=28, fill=(26, 18, 22, 235), outline=(255, 90, 20, 180), width=2)
            draw.text((130, 870), "PASSO 2: CLONAVOZ", fill=(255, 100, 20), font=font_title, anchor="lm")
            draw.text((130, 950), "Cole o texto e escolha a voz", fill=(220, 220, 230), font=font_subtitle, anchor="lm")
            draw.text((130, 1020), "Vozes neurais brasileiras ultra-realistas", fill=(160, 160, 170), font=font_body, anchor="lm")
            draw.text((130, 1085), "Gera a narração em 2 segundos!", fill=(255, 150, 50), font=font_badge, anchor="lm")

        elif t < 16.5:
            draw_auto_badge(draw, "PASSO 3 & 4", 280, font_badge, (20, 25, 35, 230), (0, 160, 255, 180), (100, 200, 255))
            
            # Step 3
            draw.rounded_rectangle([80, 420, WIDTH-80, 720], radius=28, fill=(18, 18, 24, 235), outline=(0, 160, 255, 150), width=2)
            draw.text((130, 490), "PASSO 3: DOWNLOAD DIRETO", fill=(80, 190, 255), font=font_title, anchor="lm")
            draw.text((130, 570), "Baixe o áudio em WAV ou MP3", fill=(210, 210, 220), font=font_subtitle, anchor="lm")
            draw.text((130, 640), "Arquivo pronto direto no seu dispositivo", fill=(160, 160, 170), font=font_body, anchor="lm")

            # Step 4
            draw.rounded_rectangle([80, 800, WIDTH-80, 1100], radius=28, fill=(18, 18, 24, 235), outline=(255, 80, 120, 150), width=2)
            draw.text((130, 870), "PASSO 4: JUNTE NO CAPCUT", fill=(255, 100, 140), font=font_title, anchor="lm")
            draw.text((130, 950), "Adicione vídeos de fundo gratuitos", fill=(210, 210, 220), font=font_subtitle, anchor="lm")
            draw.text((130, 1020), "Seu vídeo está pronto para viralizar!", fill=(160, 160, 170), font=font_body, anchor="lm")

        else:
            draw_auto_badge(draw, "CRIE SEU CANAL HOJE MESMO", 270, font_badge, (16, 36, 22, 235), (0, 220, 110, 190), (0, 255, 130), pad_x=55, pad_y=18)
            draw.text((WIDTH//2, 420), "Recarga Fácil no PIX por Apenas", fill=(195, 195, 205), font=font_subtitle, anchor="mm")
            draw.text((WIDTH//2, 535), "R$ 9,90", fill=(0, 255, 135), font=font_huge, anchor="mm")
            draw.text((WIDTH//2, 625), "Créditos Imediatos sem Assinatura", fill=(175, 175, 185), font=font_body, anchor="mm")

            cta_pulse = math.sin(t * 6) * 4
            btn_top = int(750 + cta_pulse)
            btn_bottom = btn_top + 130
            draw.rounded_rectangle([90, btn_top, WIDTH - 90, btn_bottom], radius=38, fill=(255, 75, 0), outline=(255, 155, 80), width=3)
            draw.text((WIDTH//2, (btn_top + btn_bottom) // 2), "TESTAR GRÁTIS AGORA", fill=(255, 255, 255), font=font_cta, anchor="mm")

            draw.text((WIDTH//2, 1020), "Acesse no seu navegador:", fill=(160, 160, 170), font=font_subtitle, anchor="mm")
            draw.text((WIDTH//2, 1105), "www.clonavoz.com.br", fill=(255, 125, 30), font=font_title, anchor="mm")

            draw_auto_badge(draw, "Instagram: @clonavozoficial", 1320, font_subtitle, (22, 22, 28, 230), (255, 255, 255, 60), (255, 255, 255), pad_x=60, pad_y=22)

        draw.text((WIDTH//2, 1830), "Desenvolvido por nx49 System Development", fill=(100, 100, 115), font=font_watermark, anchor="mm")
        return img

    bgm_path = os.path.join(STATIC_DIR, "bgm", "bgm_inspire.mp3")
    render_and_encode(draw_frame, total_frames, wav_path, bgm_path, "video_2_canal_dark_passo_a_passo.mp4")


# ==============================================================================
# VÍDEO 3 (FORMATO C): Teste Cego: Humano vs IA (Engajamento Máximo)
# ==============================================================================
def generate_video_3():
    print("\n=========================================================")
    print("GERANDO VÍDEO 3: Teste Cego: Humano vs IA (Alto Engajamento)")
    print("=========================================================")
    
    script = (
        "Teste de percepção sonora: você consegue descobrir qual dessas vozes é um locutor humano e qual é uma inteligência artificial? "
        "Ouça a voz número um... "
        "No meio da escuridão, apenas os mais corajosos encontram a verdade. "
        "Agora, ouça a voz número dois... "
        "O universo guarda mistérios que a mente humana ainda não consegue explicar. "
        "E aí, qual é a inteligência artificial? A número um ou a número dois? "
        "Deixe seu palpite nos comentários! "
        "O segredo? As duas foram geradas no Clonavoz! "
        "Acesse clonavoz ponto com ponto b r, e teste grátis!"
    )
    res = tts_engine.synthesize_text(script, voice_key="faber", speed=0.96)
    wav_path = res["file_path"]
    dur = res["duration_seconds"]
    total_sec = math.ceil(dur + 1.2)
    total_frames = int(total_sec * FPS)

    def draw_frame(t, idx):
        img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 8, 12, 255))
        draw = ImageDraw.Draw(img)

        # Subtle cinematic mystery glow
        pulse = math.sin(t * 3.5) * 0.15 + 0.85
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glow)
        radius = int(480 * pulse)
        g_draw.ellipse([WIDTH//2 - radius, 650 - radius, WIDTH//2 + radius, 650 + radius], fill=(255, 60, 0, 32))
        glow = glow.filter(ImageFilter.GaussianBlur(110))
        img = Image.alpha_composite(img, glow)
        draw = ImageDraw.Draw(img)

        draw.text((WIDTH//2, 130), "CLONAVOZ.COM.BR", fill=(255, 120, 40, 230), font=font_brand, anchor="mm")
        draw.line([(WIDTH//2 - 150, 160), (WIDTH//2 + 150, 160)], fill=(255, 85, 0, 160), width=2)

        if t < 6.5:
            draw_auto_badge(draw, "TESTE DE PERCEPÇÃO SONORA", 280, font_badge, (35, 15, 15, 230), (255, 50, 50, 200), (255, 100, 100))
            draw.text((WIDTH//2, 460), "HUMANO OU", fill=(255, 255, 255), font=font_huge, anchor="mm")
            draw.text((WIDTH//2, 570), "INTELIGÊNCIA", fill=(255, 100, 20), font=font_huge, anchor="mm")
            draw.text((WIDTH//2, 670), "ARTIFICIAL?", fill=(255, 255, 255), font=font_huge, anchor="mm")

            draw.rounded_rectangle([100, 850, WIDTH-100, 1200], radius=32, fill=(18, 18, 24, 235), outline=(255, 80, 20, 120), width=2)
            draw.text((WIDTH//2, 940), "Preste muita atenção no som...", fill=(200, 200, 210), font=font_subtitle, anchor="mm")
            draw.text((WIDTH//2, 1040), "Você consegue acertar?", fill=(255, 140, 40), font=font_title, anchor="mm")

        elif t < 12.0:
            # Voice 1
            draw_auto_badge(draw, "OUÇA COM ATENÇÃO", 280, font_badge, (20, 30, 45, 230), (0, 160, 255, 200), (100, 200, 255))
            
            draw.text((WIDTH//2, 430), "VOZ NÚMERO 1", fill=(80, 190, 255), font=font_huge, anchor="mm")
            draw.text((WIDTH//2, 520), '"No meio da escuridão, apenas os', fill=(220, 220, 230), font=font_subtitle, anchor="mm")
            draw.text((WIDTH//2, 580), 'mais corajosos encontram a verdade."', fill=(220, 220, 230), font=font_subtitle, anchor="mm")

            # Mystery Box
            draw.rounded_rectangle([WIDTH//2 - 140, 700, WIDTH//2 + 140, 980], radius=32, fill=(20, 24, 34, 240), outline=(0, 160, 255, 180), width=3)
            draw.text((WIDTH//2, 840), "?", fill=(80, 190, 255), font=get_font(120, bold=True), anchor="mm")

            # Sound bars blue
            bar_count = 20
            bar_w = 16
            spacing = 18
            start_x = WIDTH//2 - (bar_count * (bar_w + spacing)) // 2
            for b in range(bar_count):
                bh = int(25 + 110 * abs(math.sin(t * 7 + b * 0.5)))
                bx = start_x + b * (bar_w + spacing)
                by = 1180 - bh // 2
                draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=7, fill=(0, int(150 + 80 * (b/bar_count)), 255))

        elif t < 18.5:
            # Voice 2
            draw_auto_badge(draw, "AGORA A SEGUNDA VOZ", 280, font_badge, (40, 25, 15, 230), (255, 140, 0, 200), (255, 170, 60))
            
            draw.text((WIDTH//2, 430), "VOZ NÚMERO 2", fill=(255, 150, 40), font=font_huge, anchor="mm")
            draw.text((WIDTH//2, 520), '"O universo guarda mistérios que', fill=(220, 220, 230), font=font_subtitle, anchor="mm")
            draw.text((WIDTH//2, 580), 'a mente humana não consegue explicar."', fill=(220, 220, 230), font=font_subtitle, anchor="mm")

            # Mystery Box Orange
            draw.rounded_rectangle([WIDTH//2 - 140, 700, WIDTH//2 + 140, 980], radius=32, fill=(34, 22, 16, 240), outline=(255, 140, 0, 180), width=3)
            draw.text((WIDTH//2, 840), "?", fill=(255, 150, 40), font=get_font(120, bold=True), anchor="mm")

            # Sound bars orange
            bar_count = 20
            bar_w = 16
            spacing = 18
            start_x = WIDTH//2 - (bar_count * (bar_w + spacing)) // 2
            for b in range(bar_count):
                bh = int(25 + 110 * abs(math.sin(t * 7 + b * 0.5)))
                bx = start_x + b * (bar_w + spacing)
                by = 1180 - bh // 2
                draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=7, fill=(255, int(80 + 120 * (b/bar_count)), 0))

        elif t < 25.0:
            # Question & Call to comment
            draw_auto_badge(draw, "QUAL É A INTELIGÊNCIA ARTIFICIAL?", 280, font_badge, (35, 18, 15, 230), (255, 60, 20, 200), (255, 110, 40))
            
            draw.text((WIDTH//2, 450), "QUAL DELAS É A IA?", fill=(255, 255, 255), font=font_huge, anchor="mm")
            draw.text((WIDTH//2, 550), "Voz 1 ou Voz 2?", fill=(255, 110, 20), font=font_huge, anchor="mm")

            # Big Comment CTA Box
            draw.rounded_rectangle([100, 700, WIDTH-100, 1020], radius=34, fill=(22, 18, 24, 240), outline=(0, 230, 130, 180), width=3)
            draw.text((WIDTH//2, 790), "DEIXE SEU PALPITE", fill=(0, 240, 140), font=font_title, anchor="mm")
            draw.text((WIDTH//2, 875), "NOS COMENTÁRIOS! 👇", fill=(255, 255, 255), font=font_title, anchor="mm")
            draw.text((WIDTH//2, 955), "Comente 1 ou 2!", fill=(200, 200, 210), font=font_subtitle, anchor="mm")

            draw.text((WIDTH//2, 1200), "Revelação nos próximos segundos...", fill=(180, 180, 190), font=font_subtitle, anchor="mm")

        else:
            # The Reveal & CTA
            draw_auto_badge(draw, "O SEGREDO REVELADO!", 270, font_badge, (16, 36, 22, 235), (0, 220, 110, 190), (0, 255, 130), pad_x=55, pad_y=18)
            draw.text((WIDTH//2, 410), "AS DUAS VOZES FORAM", fill=(255, 255, 255), font=font_title, anchor="mm")
            draw.text((WIDTH//2, 490), "GERADAS POR IA!", fill=(255, 110, 20), font=font_huge, anchor="mm")
            draw.text((WIDTH//2, 580), "Feitas no Clonavoz em Segundos", fill=(200, 200, 210), font=font_subtitle, anchor="mm")

            cta_pulse = math.sin(t * 6) * 4
            btn_top = int(720 + cta_pulse)
            btn_bottom = btn_top + 130
            draw.rounded_rectangle([90, btn_top, WIDTH - 90, btn_bottom], radius=38, fill=(255, 75, 0), outline=(255, 155, 80), width=3)
            draw.text((WIDTH//2, (btn_top + btn_bottom) // 2), "TESTAR GRÁTIS AGORA", fill=(255, 255, 255), font=font_cta, anchor="mm")

            draw.text((WIDTH//2, 980), "Acesse no seu navegador:", fill=(160, 160, 170), font=font_subtitle, anchor="mm")
            draw.text((WIDTH//2, 1060), "www.clonavoz.com.br", fill=(255, 125, 30), font=font_title, anchor="mm")

            draw_auto_badge(draw, "Recarga PIX por apenas R$ 9,90", 1240, font_subtitle, (22, 35, 26, 230), (0, 220, 120, 160), (0, 240, 140), pad_x=60, pad_y=20)
            draw_auto_badge(draw, "Instagram: @clonavozoficial", 1400, font_subtitle, (22, 22, 28, 230), (255, 255, 255, 60), (255, 255, 255), pad_x=60, pad_y=22)

        draw.text((WIDTH//2, 1830), "Desenvolvido por nx49 System Development", fill=(100, 100, 115), font=font_watermark, anchor="mm")
        return img

    bgm_path = os.path.join(STATIC_DIR, "bgm", "bgm_cinematic.mp3")
    render_and_encode(draw_frame, total_frames, wav_path, bgm_path, "video_3_teste_cego_humano_vs_ia.mp4")


if __name__ == "__main__":
    generate_video_1()
    generate_video_2()
    generate_video_3()
    print("\n*******************************************************************")
    print("TODOS OS 3 VÍDEOS FORAM GERADOS COM SUCESSO NA ÁREA DE TRABALHO!")
    print("*******************************************************************")
