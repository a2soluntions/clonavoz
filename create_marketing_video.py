import os
import sys
import math
import subprocess
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf
import tts_engine

BASE_DIR = r"e:\A2\projetos\gerador de voz com texto"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch_video")
os.makedirs(SCRATCH_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920
FPS = 30

# 1. Synthesize Narration with refined diction & breathing pauses
print("--- [1/5] Sintetizando locução com dicção aprimorada e pausas humanas... ---")

# Carefully punctuated script:
# - "Pícs" produces the exact single-syllable PT-BR pronunciation for PIX (avoiding "pixis")
# - "You Tube" with space and commas separates the words cleanly
# - Commas and periods create natural breathing pauses between items
narration_script = (
    "Cansado de pagar assinaturas em dólar no cartão internacional para ter voz de inteligência artificial? "
    "Conheça o Clonavoz! A inteligência artificial de voz feita para o Brasil, com sotaque cem por cento natural. "
    "Perfeito para seus canais Dark, para vídeos do You Tube, Reels, e anúncios de alta conversão. "
    "Crie áudios profissionais em segundos. "
    "Sem assinaturas fixas. Recarregue no Pícs a partir de apenas nove reais e noventa. "
    "Acesse clonavoz ponto com ponto b r, e teste grátis agora mesmo!"
)

narration_res = tts_engine.synthesize_text(narration_script, voice_key="faber", speed=0.98)
narration_wav = narration_res["file_path"]
narration_duration = narration_res["duration_seconds"]
print(f"Locução gerada: {narration_wav} ({narration_duration:.2f}s)")

# Total video duration with small outro padding
TOTAL_DURATION = math.ceil(narration_duration + 1.5)
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)
print(f"Duração total do vídeo: {TOTAL_DURATION}s ({TOTAL_FRAMES} frames @ {FPS}fps)")

# Font loading helper
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
font_title = get_font(64, bold=True)
font_huge = get_font(88, bold=True)
font_cta = get_font(48, bold=True)
font_watermark = get_font(26, bold=False)

# Load Brand Logo
logo_path = os.path.join(BASE_DIR, "static", "logo_perfil_instagram.png")
if os.path.exists(logo_path):
    logo_base = Image.open(logo_path).convert("RGBA")
else:
    logo_base = Image.new("RGBA", (300, 300), (255, 85, 0, 255))

# Helper to draw dynamic, auto-sizing pills/badges with ZERO text overflow
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

print("--- [2/5] Renderizando quadros do vídeo comercial com design corrigido... ---")

def draw_scene(t, frame_idx):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (10, 10, 14, 255))
    draw = ImageDraw.Draw(img)

    # Ambient subtle background grid / glow
    pulse = math.sin(t * 3) * 0.15 + 0.85
    glow_y = 650 + int(math.sin(t * 1.5) * 50)
    
    # Glowing orb in background
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    radius = int(480 * pulse)
    g_draw.ellipse([WIDTH//2 - radius, glow_y - radius, WIDTH//2 + radius, glow_y + radius], fill=(255, 75, 0, 36))
    glow = glow.filter(ImageFilter.GaussianBlur(110))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Top Brand Header
    draw.text((WIDTH//2, 130), "CLONAVOZ.COM.BR", fill=(255, 120, 40, 230), font=font_brand, anchor="mm")
    draw.line([(WIDTH//2 - 150, 160), (WIDTH//2 + 150, 160)], fill=(255, 85, 0, 160), width=2)

    if t < 5.2:
        # SCENE 1: O PROBLEMA (Dólar / Assinaturas abusivas)
        draw_auto_badge(draw, "CHEGA DE PAGAR EM DÓLAR", 280, font_badge, 
                        fill_bg=(35, 18, 18, 230), outline_color=(255, 60, 60, 200), text_color=(255, 110, 110), pad_x=50, pad_y=16)

        draw.text((WIDTH//2, 460), "Cansado de", fill=(210, 210, 220), font=font_subtitle, anchor="mm")
        draw.text((WIDTH//2, 560), "ASSINATURAS", fill=(255, 70, 70), font=font_huge, anchor="mm")
        draw.text((WIDTH//2, 660), "ABUSIVAS?", fill=(255, 255, 255), font=font_huge, anchor="mm")

        # Problem comparison box (auto centered, generous margins)
        draw.rounded_rectangle([90, 810, WIDTH - 90, 1200], radius=32, fill=(20, 16, 20, 235), outline=(255, 60, 60, 90), width=2)
        draw.text((WIDTH//2, 885), "Plataformas Estrangeiras:", fill=(160, 160, 175), font=font_subtitle, anchor="mm")
        draw.text((WIDTH//2, 970), "R$ 150 a R$ 550 / mês", fill=(255, 90, 90), font=font_title, anchor="mm")
        
        # Draw clean bullets without broken emojis
        draw.ellipse([140, 1055, 154, 1069], fill=(255, 80, 80))
        draw.text((175, 1062), "Exigem Cartão Internacional", fill=(225, 225, 225), font=font_body, anchor="lm")
        
        draw.ellipse([140, 1125, 154, 1139], fill=(255, 80, 80))
        draw.text((175, 1132), "Cobram IOF e taxas em Dólar", fill=(225, 225, 225), font=font_body, anchor="lm")

        draw.text((WIDTH//2, 1480), "Existe uma solução brasileira...", fill=(255, 130, 45), font=font_subtitle, anchor="mm")

    elif t < 11.8:
        # SCENE 2: A REVELAÇÃO (Clonavoz AI Brasil)
        draw_auto_badge(draw, "100% FEITO NO BRASIL", 280, font_badge, 
                        fill_bg=(28, 20, 12, 230), outline_color=(255, 110, 0, 200), text_color=(255, 155, 55), pad_x=50, pad_y=16)

        # Pulsing logo
        logo_w = int(270 + math.sin(t * 4) * 12)
        logo_resized = logo_base.resize((logo_w, logo_w), Image.Resampling.LANCZOS)
        img.paste(logo_resized, (WIDTH//2 - logo_w//2, 400), logo_resized)
        draw = ImageDraw.Draw(img)

        draw.text((WIDTH//2, 760), "CLONAVOZ AI", fill=(255, 255, 255), font=font_huge, anchor="mm")
        draw.text((WIDTH//2, 850), "Voz Neural Hiper-Realista", fill=(255, 115, 25), font=font_title, anchor="mm")
        draw.text((WIDTH//2, 930), "Sem sotaque robótico ou estrangeiro", fill=(195, 195, 205), font=font_subtitle, anchor="mm")

        # Animated Soundwave Bars
        bar_count = 24
        bar_w = 14
        spacing = 18
        start_x = WIDTH//2 - (bar_count * (bar_w + spacing)) // 2
        for b in range(bar_count):
            bh = int(30 + 130 * abs(math.sin(t * 8 + b * 0.4)))
            bx = start_x + b * (bar_w + spacing)
            by = 1150 - bh // 2
            draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=7, fill=(255, int(80 + 120 * (b/bar_count)), 0))

        draw.text((WIDTH//2, 1360), "Narração gerada em 2 segundos!", fill=(255, 255, 255), font=font_subtitle, anchor="mm")

    elif t < 18.5:
        # SCENE 3: CASOS DE USO (Canais Dark, You Tube, Reels, VSLs)
        draw_auto_badge(draw, "ONDE VOCÊ PODE USAR?", 280, font_badge, 
                        fill_bg=(16, 25, 38, 230), outline_color=(0, 165, 255, 180), text_color=(110, 205, 255), pad_x=50, pad_y=16)

        draw.text((WIDTH//2, 400), "Turbine sua Produção:", fill=(255, 255, 255), font=font_huge, anchor="mm")

        cards = [
            ("CANAIS DARK NO YOUTUBE", "Histórias, mistérios e curiosidades sem microfone"),
            ("REELS, SHORTS & TIKTOK", "Áudios persuasivos com retenção máxima"),
            ("VSLs & ANÚNCIOS DE VENDA", "Locução de cinema para alta conversão"),
        ]

        card_y = 520
        for title_card, desc_card in cards:
            draw.rounded_rectangle([80, card_y, WIDTH - 80, card_y + 190], radius=26, fill=(18, 18, 24, 235), outline=(255, 85, 0, 120), width=2)
            
            # Glowing accent dot
            draw.ellipse([125, card_y + 55, 143, card_y + 73], fill=(255, 100, 20))
            draw.text((165, card_y + 64), title_card, fill=(255, 145, 45), font=font_subtitle, anchor="lm")
            draw.text((125, card_y + 130), desc_card, fill=(195, 195, 205), font=font_body, anchor="lm")
            card_y += 240

        draw.text((WIDTH//2, 1420), "Download Direto em WAV e MP3", fill=(255, 255, 255), font=font_subtitle, anchor="mm")

    else:
        # SCENE 4: CTA FINAL & PREÇO PIX (Com bordas dinâmicas corrigidas!)
        draw_auto_badge(draw, "SEM ASSINATURAS • RECARGA NO PIX", 270, font_badge, 
                        fill_bg=(16, 36, 22, 235), outline_color=(0, 220, 110, 190), text_color=(0, 255, 130), pad_x=55, pad_y=18)

        draw.text((WIDTH//2, 420), "Comece Agora Por Apenas", fill=(195, 195, 205), font=font_subtitle, anchor="mm")
        draw.text((WIDTH//2, 535), "R$ 9,90", fill=(0, 255, 135), font=font_huge, anchor="mm")
        draw.text((WIDTH//2, 625), "No PIX com Liberação Imediata", fill=(175, 175, 185), font=font_body, anchor="mm")

        # Big CTA Box (auto centered and sized without emoji box)
        cta_pulse = math.sin(t * 6) * 4
        btn_top = int(750 + cta_pulse)
        btn_bottom = btn_top + 130
        draw.rounded_rectangle([90, btn_top, WIDTH - 90, btn_bottom], radius=38, fill=(255, 75, 0), outline=(255, 155, 80), width=3)
        draw.text((WIDTH//2, (btn_top + btn_bottom) // 2), "TESTAR GRÁTIS AGORA", fill=(255, 255, 255), font=font_cta, anchor="mm")

        draw.text((WIDTH//2, 1020), "Acesse no seu navegador:", fill=(160, 160, 170), font=font_subtitle, anchor="mm")
        draw.text((WIDTH//2, 1105), "www.clonavoz.com.br", fill=(255, 125, 30), font=font_title, anchor="mm")

        # Instagram Pill with dynamic auto-sizing (ZERO overflow!)
        draw_auto_badge(draw, "Instagram: @clonavozoficial", 1320, font_subtitle,
                        fill_bg=(22, 22, 28, 230), outline_color=(255, 255, 255, 60), text_color=(255, 255, 255), pad_x=60, pad_y=22)

    # Footer watermark
    draw.text((WIDTH//2, 1830), "Desenvolvido por nx49 System Development", fill=(100, 100, 115), font=font_watermark, anchor="mm")

    return img

# Render frames to disk in batches
print("Renderizando frames corrigidos...")
for i in range(TOTAL_FRAMES):
    t_sec = i / FPS
    frame_img = draw_scene(t_sec, i)
    frame_img.save(os.path.join(SCRATCH_DIR, f"frame_{i:05d}.png"))
    if i % 90 == 0:
        print(f"Frame {i}/{TOTAL_FRAMES} ({(i/TOTAL_FRAMES)*100:.0f}%)")

print("--- [3/5] Frames renderizados! Codificando vídeo com FFmpeg... ---")
video_raw = os.path.join(SCRATCH_DIR, "video_raw.mp4")

cmd_video = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(SCRATCH_DIR, "frame_%05d.png"),
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-pix_fmt", "yuv420p",
    video_raw
]
subprocess.run(cmd_video, check=True)

print("--- [4/5] Mixando áudio: Locução Faber corrigida + Trilha Sonora... ---")
bgm_path = os.path.join(BASE_DIR, "static", "bgm", "bgm_inspire.mp3")
final_audio = os.path.join(SCRATCH_DIR, "audio_mixed.m4a")

cmd_audio = [
    "ffmpeg", "-y",
    "-i", narration_wav,
    "-i", bgm_path,
    "-filter_complex",
    "[0:a]volume=1.35[v];[1:a]volume=0.16,aloop=loop=-1:size=2e+09[bgm];[v][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
    "-map", "[aout]",
    "-c:a", "aac", "-b:a", "192k",
    final_audio
]
subprocess.run(cmd_audio, check=True)

print("--- [5/5] Finalizando vídeo para o Desktop... ---")
desktop_output = r"C:\Users\User\Desktop\comercial_clonavoz_reels.mp4"
static_output = os.path.join(BASE_DIR, "static", "comercial_clonavoz_reels.mp4")

cmd_final = [
    "ffmpeg", "-y",
    "-i", video_raw,
    "-i", final_audio,
    "-c:v", "copy",
    "-c:a", "aac",
    "-shortest",
    desktop_output
]
subprocess.run(cmd_final, check=True)

# Also copy to static folder
shutil.copyfile(desktop_output, static_output)

# Clean up frames
try:
    shutil.rmtree(SCRATCH_DIR)
    print("Arquivos temporários limpos com sucesso!")
except Exception:
    pass

print("--- SUCESSO ABSOLUTO! NOVO VÍDEO PRONTO NO DESKTOP! ---")
