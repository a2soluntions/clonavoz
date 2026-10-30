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
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch_mkt_post")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(SCRATCH_DIR, exist_ok=True)

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

font_brand = get_font(34, bold=True)
font_badge = get_font(30, bold=True)
font_huge = get_font(72, bold=True)
font_title = get_font(54, bold=True)
font_subtitle = get_font(40, bold=True)
font_body = get_font(32, bold=False)
font_price = get_font(84, bold=True)
font_cta_btn = get_font(46, bold=True)
font_footer = get_font(24, bold=False)

# 1. Roteiro 100% em Português Puro (Zero palavras em inglês que possam embolar a dicção)
script_text = (
    "Pare de pagar mensalidade em dólar por voz de inteligência artificial! "
    "E o melhor: agora sem precisar de nenhum cadastro! "
    "Conheça o Clonavoz! A ferramenta brasileira de voz neural ultra-realista, "
    "feita para criar narrações humanas que prendem a atenção do início ao fim. "
    "Agora você gera suas locuções direto no Pícs a partir de apenas dois reais e quarenta e nove. "
    "Sem mensalidade fixa, sem cartão e com download imediato em MP3 na hora! "
    "E se você quiser economizar ainda mais, garanta trinta áudios por apenas dezenove e noventa, "
    "apenas sessenta e seis centavos por áudio! "
    "Toque no link da nossa bio e faça seu teste grátis agora mesmo!"
)

print("--- [1/5] Sintetizando locução com dicção 100% pura em português (Voz Eduarda) ---")
synth_res = tts_engine.synthesize_text(script_text, voice_key='eduarda', speed=1.0)
wav_path = synth_res['file_path']
duration = synth_res['duration_seconds']
total_duration = duration + 1.2
total_frames = int(total_duration * FPS)
print(f"Áudio gerado: {wav_path} ({duration:.2f}s | {total_frames} frames)")

# Carrega amplitude do áudio para o espectro animado
audio_data, sr = sf.read(wav_path)
if len(audio_data.shape) > 1:
    audio_data = np.mean(audio_data, axis=1)

samples_per_frame = int(sr / FPS)

# Logo Clonavoz
logo_path = os.path.join(STATIC_DIR, "logo_perfil_instagram.png")
if os.path.exists(logo_path):
    logo_base = Image.open(logo_path).convert("RGBA")
else:
    logo_base = Image.new("RGBA", (240, 240), (255, 85, 0, 255))

def draw_auto_badge(draw, text, y_center, font, fill_bg, outline_color, text_color, pad_x=40, pad_y=14, border_width=2):
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

print("--- [2/5] Renderizando quadros dinâmicos (Zero caixas de emoji e dicção perfeita) ---")

def render_frame(t, frame_idx):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (10, 10, 15, 255))
    draw = ImageDraw.Draw(img)

    # Ambient neon pulse in background
    pulse = math.sin(t * 3.5) * 0.12 + 0.88
    glow_color = (255, 85, 0, 32) if t < 12.0 else ((0, 225, 120, 28) if t < 21.0 else (255, 120, 30, 36))
    
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    radius = int(500 * pulse)
    g_draw.ellipse([WIDTH//2 - radius, 720 - radius, WIDTH//2 + radius, 720 + radius], fill=glow_color)
    glow = glow.filter(ImageFilter.GaussianBlur(130))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Top Brand Header (Sem links, 100% seguro para TikTok/Instagram)
    draw.text((WIDTH//2, 115), "CLONAVOZ AI", fill=(255, 130, 45, 240), font=font_brand, anchor="mm")
    draw.line([(WIDTH//2 - 110, 142), (WIDTH//2 + 110, 142)], fill=(255, 85, 0, 180), width=2)

    # Waveform live bars at bottom
    start_sample = int(frame_idx * samples_per_frame)
    end_sample = min(start_sample + samples_per_frame, len(audio_data))
    amp = float(np.max(np.abs(audio_data[start_sample:end_sample]))) if end_sample > start_sample else 0.05
    amp = min(1.0, max(0.08, amp * 2.2))

    num_bars = 28
    bar_w = 12
    gap = 14
    total_w = num_bars * (bar_w + gap) - gap
    start_bx = (WIDTH - total_w) // 2

    for b in range(num_bars):
        phase = b / num_bars
        bar_amp = amp * (0.45 + 0.55 * abs(math.sin(t * 9 + phase * 6)))
        bh = max(10, int(bar_amp * 130))
        bx = start_bx + b * (bar_w + gap)
        by = 1680 - bh // 2
        bcolor = (0, 255, 140) if t >= 12.0 and t < 21.0 else (255, int(90 + 130 * phase), 20)
        draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=6, fill=bcolor)

    # TIMELINE LOGIC:
    if t < 5.8:
        # CENA 1: O FIM DO DÓLAR & SEM CADASTRO
        draw_auto_badge(draw, "NOVIDADE NO BRASIL", 250, font_badge,
                        fill_bg=(36, 18, 16, 230), outline_color=(255, 75, 40, 220), text_color=(255, 120, 80))

        draw.text((WIDTH//2, 410), "PARE DE PAGAR", fill=(255, 255, 255), font=font_subtitle, anchor="mm")
        draw.text((WIDTH//2, 510), "EM DÓLAR", fill=(255, 70, 70), font=font_huge, anchor="mm")
        draw.text((WIDTH//2, 600), "POR VOZ DE IA!", fill=(255, 255, 255), font=font_title, anchor="mm")

        # Big Glass Card
        draw.rounded_rectangle([80, 720, WIDTH - 80, 1200], radius=32, fill=(20, 18, 24, 235), outline=(255, 85, 0, 100), width=2)
        
        # Pill inside
        draw_auto_badge(draw, "ZERO CADASTRO • DIRETO NO PIX", 800, font_badge,
                        fill_bg=(16, 36, 22, 230), outline_color=(0, 225, 120, 220), text_color=(0, 255, 140))

        draw.text((WIDTH//2, 915), "Chega de assinaturas abusivas", fill=(220, 220, 230), font=font_subtitle, anchor="mm")
        draw.text((WIDTH//2, 985), "Sem cartão internacional", fill=(255, 100, 100), font=font_title, anchor="mm")
        draw.text((WIDTH//2, 1060), "Sem formulários ou senhas", fill=(180, 180, 195), font=font_body, anchor="mm")
        draw.text((WIDTH//2, 1130), "Entre, digite e baixe na hora!", fill=(0, 255, 140), font=font_subtitle, anchor="mm")

        draw.text((WIDTH//2, 1420), "Conheça a IA 100% brasileira", fill=(255, 140, 40), font=font_subtitle, anchor="mm")

    elif t < 12.2:
        # CENA 2: A REVELAÇÃO DO CLONAVOZ (COM VISUAL POLIDO E SEM CAIXAS QUEBRADAS [])
        draw_auto_badge(draw, "100% NATURAL & EXPRESSIVA", 250, font_badge,
                        fill_bg=(28, 20, 12, 230), outline_color=(255, 110, 0, 220), text_color=(255, 160, 50))

        # Pulsing logo
        logo_sz = int(220 + math.sin(t * 4) * 10)
        logo_res = logo_base.resize((logo_sz, logo_sz), Image.Resampling.LANCZOS)
        img.paste(logo_res, (WIDTH//2 - logo_sz//2, 340), logo_res)
        draw = ImageDraw.Draw(img)

        draw.text((WIDTH//2, 630), "CLONAVOZ AI", fill=(255, 255, 255), font=font_huge, anchor="mm")
        draw.text((WIDTH//2, 715), "Vozes Neurais de Estúdio", fill=(255, 120, 30), font=font_title, anchor="mm")

        # Casos de Uso com bullets geométricos neon perfeitos (Zero caixas [])
        use_cases = [
            ("Vídeos com Retenção Máxima", "Prenda a atenção do público do início ao fim"),
            ("Locuções Naturais Sem Microfone", "Qualidade de estúdio profissional em segundos"),
            ("Alta Conversão para Vendas e Redes", "Sotaque brasileiro sem tom robótico")
        ]
        card_y = 800
        for title_uc, desc_uc in use_cases:
            draw.rounded_rectangle([80, card_y, WIDTH - 80, card_y + 135], radius=22, fill=(18, 18, 24, 235), outline=(255, 100, 20, 110), width=2)
            # Glowing neon bullet dot
            draw.ellipse([115, card_y + 35, 131, card_y + 51], fill=(255, 120, 30))
            draw.text((148, card_y + 43), title_uc, fill=(255, 155, 55), font=font_subtitle, anchor="lm")
            draw.text((120, card_y + 94), desc_uc, fill=(195, 195, 205), font=font_body, anchor="lm")
            card_y += 160

        draw.text((WIDTH//2, 1420), "Sotaque brasileiro sem tom robótico!", fill=(255, 255, 255), font=font_subtitle, anchor="mm")

    elif t < 20.2:
        # CENA 3: O GRANDE DIFERENCIAL (GERE NO PIX A PARTIR DE R$ 2,49)
        draw_auto_badge(draw, "CHEGOU O ÁUDIO AVULSO NO PIX", 250, font_badge,
                        fill_bg=(14, 38, 22, 235), outline_color=(0, 225, 120, 220), text_color=(0, 255, 140))

        draw.text((WIDTH//2, 390), "PAGOU NO PIX,", fill=(255, 255, 255), font=font_title, anchor="mm")
        draw.text((WIDTH//2, 480), "BAIXOU NA HORA!", fill=(0, 255, 140), font=font_huge, anchor="mm")

        # Card de Preço Esmeralda
        draw.rounded_rectangle([80, 580, WIDTH - 80, 1230], radius=32, fill=(16, 26, 20, 240), outline=(0, 225, 120, 140), width=3)

        draw.text((WIDTH//2, 660), "Áudios completos a partir de:", fill=(180, 220, 195), font=font_subtitle, anchor="mm")
        draw.text((WIDTH//2, 775), "R$ 2,49", fill=(0, 255, 140), font=font_price, anchor="mm")
        draw.text((WIDTH//2, 865), "Valor proporcional ao seu roteiro", fill=(160, 200, 180), font=font_body, anchor="mm")

        draw.line([(140, 915), (WIDTH - 140, 915)], fill=(0, 225, 120, 80), width=2)

        # Benefícios em bullets geométricos neon verdes
        bullets = [
            "Sem necessidade de cadastro",
            "Escaneie o QR Code no app do banco",
            "Síntese ultrarrápida em segundos",
            "Download automático do arquivo MP3"
        ]
        by = 970
        for btext in bullets:
            draw.ellipse([140, by - 8, 156, by + 8], fill=(0, 255, 140))
            draw.text((175, by), btext, fill=(240, 255, 245), font=font_body, anchor="lm")
            by += 58

        draw.text((WIDTH//2, 1420), "Ouça a prévia grátis antes de pagar!", fill=(255, 255, 255), font=font_subtitle, anchor="mm")

    else:
        # CENA 4: PACOTE BOAS-VINDAS & CTA FINAL (100% TIKTOK & REELS SAFE)
        draw_auto_badge(draw, "OFERTA EXCLUSIVA DE BOAS-VINDAS", 240, font_badge,
                        fill_bg=(36, 18, 12, 235), outline_color=(255, 110, 0, 220), text_color=(255, 160, 50))

        draw.text((WIDTH//2, 380), "QUER MAIS ECONOMIA?", fill=(215, 215, 225), font=font_subtitle, anchor="mm")
        draw.text((WIDTH//2, 480), "30 ÁUDIOS POR", fill=(255, 255, 255), font=font_title, anchor="mm")
        draw.text((WIDTH//2, 595), "R$ 19,90", fill=(0, 255, 140), font=font_price, anchor="mm")

        draw_auto_badge(draw, "APENAS R$ 0,66 POR ÁUDIO!", 695, font_subtitle,
                        fill_bg=(24, 20, 14, 230), outline_color=(255, 180, 0, 200), text_color=(255, 210, 60), pad_x=50, pad_y=16)

        # Pulsing CTA Button
        btn_pulse = math.sin(t * 6) * 5
        btn_top = int(820 + btn_pulse)
        btn_bottom = btn_top + 130
        draw.rounded_rectangle([80, btn_top, WIDTH - 80, btn_bottom], radius=38, fill=(255, 75, 0), outline=(255, 160, 80), width=3)
        draw.text((WIDTH//2, (btn_top + btn_bottom) // 2), "TESTAR GRÁTIS AGORA", fill=(255, 255, 255), font=font_cta_btn, anchor="mm")

        # Mensagem Segura sem Link na Tela
        draw.text((WIDTH//2, 1050), "Disponível para celular e computador", fill=(170, 170, 185), font=font_subtitle, anchor="mm")

        draw_auto_badge(draw, "TOQUE NO LINK DA BIO", 1170, font_cta_btn,
                        fill_bg=(24, 24, 32, 240), outline_color=(0, 225, 120, 220), text_color=(0, 255, 140), pad_x=65, pad_y=22)

        draw.text((WIDTH//2, 1310), "Gere sua primeira locução em 10 segundos!", fill=(255, 255, 255), font=font_subtitle, anchor="mm")

    # Footer
    draw.text((WIDTH//2, 1845), "Clonavoz AI • Inteligência Artificial de Voz no Brasil", fill=(110, 110, 125), font=font_footer, anchor="mm")

    return img

# Renderiza todos os frames
print("Renderizando frames...")
for i in range(total_frames):
    t_sec = i / FPS
    frame_img = render_frame(t_sec, i)
    frame_img.save(os.path.join(SCRATCH_DIR, f"frame_{i:05d}.png"))
    if i % 100 == 0:
        print(f"Progresso: {i}/{total_frames} ({(i/total_frames)*100:.0f}%)")

print("--- [3/5] Frames renderizados! Codificando vídeo MP4 com FFmpeg... ---")
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

print("--- [4/5] Mixando áudio: Locução Eduarda + Trilha BGM Inspire... ---")
bgm_path = os.path.join(STATIC_DIR, "bgm", "bgm_inspire.mp3")
final_audio = os.path.join(SCRATCH_DIR, "audio_mixed.m4a")

cmd_audio = [
    "ffmpeg", "-y",
    "-i", wav_path,
    "-i", bgm_path,
    "-filter_complex",
    "[0:a]volume=1.4[v];[1:a]volume=0.15,aloop=loop=-1:size=2e+09[bgm];[v][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
    "-map", "[aout]",
    "-c:a", "aac", "-b:a", "192k",
    final_audio
]
subprocess.run(cmd_audio, check=True)

print("--- [5/5] Exportando vídeo final em Full HD 9:16 (Sem caixas [] e com dicção pura)... ---")
static_output = os.path.join(STATIC_DIR, "video_marketing_post_redes_sociais.mp4")
desktop_output = r"C:\Users\User\Desktop\video_marketing_clonavoz_reels.mp4"

cmd_final = [
    "ffmpeg", "-y",
    "-i", video_raw,
    "-i", final_audio,
    "-c:v", "copy",
    "-c:a", "aac",
    "-shortest",
    static_output
]
subprocess.run(cmd_final, check=True)

try:
    shutil.copyfile(static_output, desktop_output)
    print(f"Copia criada no Desktop: {desktop_output}")
except Exception as e:
    print(f"Aviso ao copiar para Desktop: {e}")

try:
    shutil.rmtree(SCRATCH_DIR)
    print("Arquivos temporarios excluidos com sucesso!")
except Exception:
    pass

print(f"[OK] VIDEO CONCLUIDO COM SUCESSO: {static_output}")
