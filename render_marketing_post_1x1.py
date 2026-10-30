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
MKT_BASE_DIR = r"E:\A2\Projetos marcketing\clonavoz"
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch_mkt_1x1")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(MKT_BASE_DIR, exist_ok=True)
os.makedirs(SCRATCH_DIR, exist_ok=True)

WIDTH = 1080
HEIGHT = 1080
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

font_brand = get_font(26, bold=True)
font_badge = get_font(24, bold=True)
font_huge = get_font(52, bold=True)
font_title = get_font(40, bold=True)
font_subtitle = get_font(30, bold=True)
font_body = get_font(25, bold=False)
font_price = get_font(68, bold=True)
font_cta_btn = get_font(34, bold=True)
font_footer = get_font(20, bold=False)

# Roteiro 100% puro em português (Zero termos em inglês)
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

# Verifica se o áudio já sintetizado existe para reuso perfeito
existing_wav = os.path.join(OUTPUT_DIR, "audio_eduarda_1793322536072.wav")
if os.path.exists(existing_wav):
    wav_path = existing_wav
    data, sr = sf.read(wav_path)
    duration = len(data) / sr
    print(f"--- [1/5] Reutilizando áudio com dicção perfeita: {wav_path} ({duration:.2f}s) ---")
else:
    print("--- [1/5] Sintetizando locução em português puro (Voz Eduarda) ---")
    synth_res = tts_engine.synthesize_text(script_text, voice_key='eduarda', speed=1.0)
    wav_path = synth_res['file_path']
    duration = synth_res['duration_seconds']

total_duration = duration + 1.2
total_frames = int(total_duration * FPS)
print(f"Duração total do vídeo 1:1: {total_duration:.2f}s | {total_frames} frames")

audio_data, sr = sf.read(wav_path)
if len(audio_data.shape) > 1:
    audio_data = np.mean(audio_data, axis=1)

samples_per_frame = int(sr / FPS)

# Logo Clonavoz
logo_path = os.path.join(STATIC_DIR, "logo_perfil_instagram.png")
if os.path.exists(logo_path):
    logo_base = Image.open(logo_path).convert("RGBA")
else:
    logo_base = Image.new("RGBA", (180, 180), (255, 85, 0, 255))

def draw_auto_badge(draw, text, y_center, font, fill_bg, outline_color, text_color, pad_x=30, pad_y=10, border_width=2):
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

print("--- [2/5] Renderizando quadros dinâmicos no formato 1:1 (Instagram Feed) ---")

def render_frame(t, frame_idx):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (10, 10, 15, 255))
    draw = ImageDraw.Draw(img)

    # Ambient neon pulse
    pulse = math.sin(t * 3.5) * 0.12 + 0.88
    glow_color = (255, 85, 0, 30) if t < 12.0 else ((0, 225, 120, 26) if t < 21.0 else (255, 120, 30, 32))
    
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    radius = int(380 * pulse)
    g_draw.ellipse([WIDTH//2 - radius, 520 - radius, WIDTH//2 + radius, 520 + radius], fill=glow_color)
    glow = glow.filter(ImageFilter.GaussianBlur(110))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Top Brand Header
    draw.text((WIDTH//2, 60), "CLONAVOZ AI", fill=(255, 130, 45, 240), font=font_brand, anchor="mm")
    draw.line([(WIDTH//2 - 90, 82), (WIDTH//2 + 90, 82)], fill=(255, 85, 0, 180), width=2)

    # Waveform live bars at bottom
    start_sample = int(frame_idx * samples_per_frame)
    end_sample = min(start_sample + samples_per_frame, len(audio_data))
    amp = float(np.max(np.abs(audio_data[start_sample:end_sample]))) if end_sample > start_sample else 0.05
    amp = min(1.0, max(0.08, amp * 2.2))

    num_bars = 32
    bar_w = 9
    gap = 10
    total_w = num_bars * (bar_w + gap) - gap
    start_bx = (WIDTH - total_w) // 2

    for b in range(num_bars):
        phase = b / num_bars
        bar_amp = amp * (0.45 + 0.55 * abs(math.sin(t * 9 + phase * 6)))
        bh = max(8, int(bar_amp * 90))
        bx = start_bx + b * (bar_w + gap)
        by = 980 - bh // 2
        bcolor = (0, 255, 140) if t >= 12.0 and t < 21.0 else (255, int(90 + 130 * phase), 20)
        draw.rounded_rectangle([bx, by, bx + bar_w, by + bh], radius=4, fill=bcolor)

    # TIMELINE LOGIC 1:1
    if t < 5.8:
        # CENA 1: O FIM DO DÓLAR & SEM CADASTRO
        draw_auto_badge(draw, "NOVIDADE NO BRASIL", 130, font_badge,
                        fill_bg=(36, 18, 16, 230), outline_color=(255, 75, 40, 220), text_color=(255, 120, 80))

        draw.text((WIDTH//2, 210), "PARE DE PAGAR EM DÓLAR", fill=(255, 255, 255), font=font_title, anchor="mm")
        draw.text((WIDTH//2, 270), "POR VOZ DE IA!", fill=(255, 70, 70), font=font_huge, anchor="mm")

        # Big Glass Card
        draw.rounded_rectangle([100, 330, WIDTH - 100, 840], radius=28, fill=(20, 18, 24, 235), outline=(255, 85, 0, 100), width=2)
        
        draw_auto_badge(draw, "ZERO CADASTRO • DIRETO NO PIX", 390, font_badge,
                        fill_bg=(16, 36, 22, 230), outline_color=(0, 225, 120, 220), text_color=(0, 255, 140))

        draw.text((WIDTH//2, 485), "Chega de assinaturas abusivas", fill=(220, 220, 230), font=font_subtitle, anchor="mm")
        draw.text((WIDTH//2, 550), "Sem cartão internacional", fill=(255, 100, 100), font=font_title, anchor="mm")
        draw.text((WIDTH//2, 620), "Sem formulários ou senhas", fill=(180, 180, 195), font=font_body, anchor="mm")
        draw.text((WIDTH//2, 695), "Entre, digite e baixe na hora!", fill=(0, 255, 140), font=font_title, anchor="mm")

        draw.text((WIDTH//2, 785), "Conheça a IA 100% brasileira", fill=(255, 140, 40), font=font_subtitle, anchor="mm")

    elif t < 12.2:
        # CENA 2: A REVELAÇÃO DO CLONAVOZ (COM VISUAL POLIDO 1:1)
        draw_auto_badge(draw, "100% NATURAL & EXPRESSIVA", 125, font_badge,
                        fill_bg=(28, 20, 12, 230), outline_color=(255, 110, 0, 220), text_color=(255, 160, 50))

        # Logo Clonavoz
        logo_sz = int(140 + math.sin(t * 4) * 8)
        logo_res = logo_base.resize((logo_sz, logo_sz), Image.Resampling.LANCZOS)
        img.paste(logo_res, (WIDTH//2 - logo_sz//2, 175), logo_res)
        draw = ImageDraw.Draw(img)

        draw.text((WIDTH//2, 350), "CLONAVOZ AI", fill=(255, 255, 255), font=font_huge, anchor="mm")
        draw.text((WIDTH//2, 405), "Vozes Neurais de Estúdio", fill=(255, 120, 30), font=font_title, anchor="mm")

        # Casos de Uso com bullets geométricos neon perfeitos (Zero caixas [])
        use_cases = [
            ("Vídeos com Retenção Máxima", "Prenda a atenção do público do início ao fim"),
            ("Locuções Naturais Sem Microfone", "Qualidade de estúdio profissional em segundos"),
            ("Alta Conversão para Vendas e Redes", "Sotaque brasileiro sem tom robótico")
        ]
        card_y = 475
        for title_uc, desc_uc in use_cases:
            draw.rounded_rectangle([100, card_y, WIDTH - 100, card_y + 105], radius=18, fill=(18, 18, 24, 235), outline=(255, 100, 20, 110), width=2)
            # Glowing neon bullet dot
            draw.ellipse([135, card_y + 27, 149, card_y + 41], fill=(255, 120, 30))
            draw.text((165, card_y + 34), title_uc, fill=(255, 155, 55), font=font_subtitle, anchor="lm")
            draw.text((140, card_y + 74), desc_uc, fill=(195, 195, 205), font=font_body, anchor="lm")
            card_y += 125

        draw.text((WIDTH//2, 885), "Sotaque brasileiro sem tom robótico!", fill=(255, 255, 255), font=font_subtitle, anchor="mm")

    elif t < 20.2:
        # CENA 3: O GRANDE DIFERENCIAL (GERE NO PIX A PARTIR DE R$ 2,49)
        draw_auto_badge(draw, "CHEGOU O ÁUDIO AVULSO NO PIX", 125, font_badge,
                        fill_bg=(14, 38, 22, 235), outline_color=(0, 225, 120, 220), text_color=(0, 255, 140))

        draw.text((WIDTH//2, 210), "PAGOU NO PIX, BAIXOU NA HORA!", fill=(255, 255, 255), font=font_title, anchor="mm")

        # Card de Preço Esmeralda
        draw.rounded_rectangle([100, 270, WIDTH - 100, 840], radius=28, fill=(16, 26, 20, 240), outline=(0, 225, 120, 140), width=3)

        draw.text((WIDTH//2, 335), "Áudios completos a partir de:", fill=(180, 220, 195), font=font_subtitle, anchor="mm")
        draw.text((WIDTH//2, 420), "R$ 2,49", fill=(0, 255, 140), font=font_price, anchor="mm")
        draw.text((WIDTH//2, 490), "Valor proporcional ao seu roteiro", fill=(160, 200, 180), font=font_body, anchor="mm")

        draw.line([(160, 530), (WIDTH - 160, 530)], fill=(0, 225, 120, 80), width=2)

        # Benefícios em bullets geométricos neon verdes
        bullets = [
            "Sem necessidade de cadastro",
            "Escaneie o QR Code no app do banco",
            "Síntese ultrarrápida em segundos",
            "Download automático do arquivo MP3"
        ]
        by = 580
        for btext in bullets:
            draw.ellipse([180, by - 6, 194, by + 8], fill=(0, 255, 140))
            draw.text((215, by), btext, fill=(240, 255, 245), font=font_body, anchor="lm")
            by += 55

        draw.text((WIDTH//2, 885), "Ouça a prévia grátis antes de pagar!", fill=(255, 255, 255), font=font_subtitle, anchor="mm")

    else:
        # CENA 4: PACOTE BOAS-VINDAS & CTA FINAL (100% TIKTOK & INSTAGRAM FEED SAFE)
        draw_auto_badge(draw, "OFERTA EXCLUSIVA DE BOAS-VINDAS", 125, font_badge,
                        fill_bg=(36, 18, 12, 235), outline_color=(255, 110, 0, 220), text_color=(255, 160, 50))

        draw.text((WIDTH//2, 205), "QUER MAIS ECONOMIA?", fill=(215, 215, 225), font=font_subtitle, anchor="mm")
        draw.text((WIDTH//2, 275), "30 ÁUDIOS POR R$ 19,90", fill=(0, 255, 140), font=font_huge, anchor="mm")

        draw_auto_badge(draw, "APENAS R$ 0,66 POR ÁUDIO!", 355, font_subtitle,
                        fill_bg=(24, 20, 14, 230), outline_color=(255, 180, 0, 200), text_color=(255, 210, 60), pad_x=40, pad_y=12)

        # Pulsing CTA Button
        btn_pulse = math.sin(t * 6) * 4
        btn_top = int(435 + btn_pulse)
        btn_bottom = btn_top + 105
        draw.rounded_rectangle([100, btn_top, WIDTH - 100, btn_bottom], radius=30, fill=(255, 75, 0), outline=(255, 160, 80), width=3)
        draw.text((WIDTH//2, (btn_top + btn_bottom) // 2), "TESTAR GRÁTIS AGORA", fill=(255, 255, 255), font=font_cta_btn, anchor="mm")

        draw.text((WIDTH//2, 595), "Disponível para celular e computador", fill=(170, 170, 185), font=font_body, anchor="mm")

        draw_auto_badge(draw, "TOQUE NO LINK DA BIO", 695, font_cta_btn,
                        fill_bg=(24, 24, 32, 240), outline_color=(0, 225, 120, 220), text_color=(0, 255, 140), pad_x=55, pad_y=18)

        draw.text((WIDTH//2, 800), "Gere sua primeira locução em 10 segundos!", fill=(255, 255, 255), font=font_subtitle, anchor="mm")

    # Footer
    draw.text((WIDTH//2, 1045), "Clonavoz AI • Inteligência Artificial de Voz no Brasil", fill=(110, 110, 125), font=font_footer, anchor="mm")

    return img

# Renderiza todos os frames 1:1
print("Renderizando frames 1:1...")
for i in range(total_frames):
    t_sec = i / FPS
    frame_img = render_frame(t_sec, i)
    frame_img.save(os.path.join(SCRATCH_DIR, f"frame_{i:05d}.png"))
    if i % 100 == 0:
        print(f"Progresso 1:1: {i}/{total_frames} ({(i/total_frames)*100:.0f}%)")

print("--- [3/5] Frames 1:1 renderizados! Codificando com FFmpeg... ---")
video_raw = os.path.join(SCRATCH_DIR, "video_raw_1x1.mp4")
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

print("--- [4/5] Mixando áudio com Trilha Sonora BGM... ---")
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

print("--- [5/5] Exportando vídeo final 1:1 para as pastas de marketing... ---")
static_output = os.path.join(STATIC_DIR, "video_marketing_post_feed_1x1.mp4")
desktop_output = r"C:\Users\User\Desktop\video_marketing_clonavoz_feed_1x1.mp4"

# Pastas solicitadas pelo usuário em E:\A2\Projetos marcketing\clonavoz
mkt_root_file = os.path.join(MKT_BASE_DIR, "video_marketing_post_feed_1x1.mp4")
mkt_ig_folder = os.path.join(MKT_BASE_DIR, "1_INSTAGRAM", "Videos_1x1")
os.makedirs(mkt_ig_folder, exist_ok=True)
mkt_ig_file = os.path.join(mkt_ig_folder, "video_marketing_post_feed_1x1.mp4")

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

# Copia para todas as pastas de destino
for dest in [desktop_output, mkt_root_file, mkt_ig_file]:
    try:
        shutil.copyfile(static_output, dest)
        print(f"Salvo em: {dest}")
    except Exception as e:
        print(f"Erro ao salvar em {dest}: {e}")

# Também copia a versão 9:16 (Reels/TikTok) já corrigida para as pastas de marketing
src_9x16 = os.path.join(STATIC_DIR, "video_marketing_post_redes_sociais.mp4")
if os.path.exists(src_9x16):
    dests_9x16 = [
        os.path.join(MKT_BASE_DIR, "video_marketing_reels_9x16.mp4"),
        os.path.join(MKT_BASE_DIR, "1_INSTAGRAM", "video_marketing_reels_9x16.mp4"),
        os.path.join(MKT_BASE_DIR, "2_TIKTOK", "video_marketing_tiktok_9x16.mp4"),
        os.path.join(MKT_BASE_DIR, "3_YOUTUBE", "video_marketing_shorts_9x16.mp4"),
    ]
    for d in dests_9x16:
        try:
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copyfile(src_9x16, d)
            print(f"Versao 9x16 salva em: {d}")
        except Exception as e:
            print(f"Erro ao salvar 9x16 em {d}: {e}")

try:
    shutil.rmtree(SCRATCH_DIR)
    print("Arquivos temporarios excluidos com sucesso!")
except Exception:
    pass

print(f"[OK] VIDEO 1:1 CONCLUIDO COM SUCESSO: {mkt_root_file}")
