import os
import sys
import math
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf

BASE_DIR = r"e:\A2\projetos\gerador de voz com texto"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
STATIC_DIR = os.path.join(BASE_DIR, "static")
MARKETING_DIR = r"E:\A2\Projetos marcketing\clonavoz"
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch_cinematic")

os.makedirs(SCRATCH_DIR, exist_ok=True)
os.makedirs(MARKETING_DIR, exist_ok=True)
for sub in ["1_INSTAGRAM", "2_TIKTOK", "3_YOUTUBE"]:
    os.makedirs(os.path.join(MARKETING_DIR, sub), exist_ok=True)

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

font_category = get_font(26, bold=True)
font_line1 = get_font(42, bold=False)
font_line2_huge = get_font(60, bold=True)
font_huge_alert = get_font(66, bold=True)
font_cta_btn = get_font(40, bold=True)
font_url = get_font(44, bold=True)
font_footer = get_font(24, bold=False)

# Áudio sintetizado de 46.9s
wav_path = os.path.join(OUTPUT_DIR, "audio_eduarda_1792724851653.wav")
if not os.path.exists(wav_path):
    raise FileNotFoundError(f"Áudio não encontrado em {wav_path}")

info = sf.info(wav_path)
duration = info.duration
total_frames = int(duration * FPS)
print(f"Carregando áudio: {wav_path} ({duration:.2f}s, {total_frames} frames)")

audio_data, sr = sf.read(wav_path)
if len(audio_data.shape) > 1:
    audio_data = np.mean(audio_data, axis=1)
samples_per_frame = int(sr / FPS)

# Carrega imagem de fundo futurista
bg_path = r"E:\A2\imagens de modelos\imagem futurista.jpg"
if not os.path.exists(bg_path):
    bg_path = os.path.join(STATIC_DIR, "logo_perfil_instagram.png")

raw_bg = Image.open(bg_path).convert("RGB")
# Base crop central proporcional a 9:16
src_w, src_h = raw_bg.size
target_ratio = WIDTH / HEIGHT
curr_ratio = src_w / src_h

if curr_ratio > target_ratio:
    new_w = int(src_h * target_ratio)
    left = (src_w - new_w) // 2
    crop_box = (left, 0, left + new_w, src_h)
else:
    new_h = int(src_w / target_ratio)
    top = (src_h - new_h) // 2
    crop_box = (0, top, src_w, top + new_h)

base_bg = raw_bg.crop(crop_box).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

# Logo
logo_path = os.path.join(STATIC_DIR, "logo_perfil_instagram.png")
logo_img = Image.open(logo_path).convert("RGBA").resize((180, 180), Image.Resampling.LANCZOS) if os.path.exists(logo_path) else None

# Roteiro sincronizado com legendas de alto impacto
SEGMENTS = [
    (0.0, 4.5, "Como canais anônimos", "FATURAM MILHARES DE REAIS?", (255, 220, 50)),
    (4.5, 8.5, "Sem nunca precisar", "MOSTRAR O ROSTO NA CÂMERA?", (255, 255, 255)),
    (8.5, 14.5, "Eles não gastam horas gravando", "NEM FORTUNAS COM MICROFONES", (255, 190, 60)),
    (14.5, 20.0, "O segredo de tudo é a retenção:", "UMA VOZ ENVOLVENTE E NATURAL", (100, 230, 255)),
    (20.0, 25.5, "Que prende a atenção do público", "ATÉ A ÚLTIMA PALAVRA DO VÍDEO", (255, 220, 50)),
    (25.5, 32.5, "Enquanto muitos pagam em dólar...", "CRIADORES USAM IA BRASILEIRA", (255, 140, 40)),
    (32.5, 37.5, "Conheça o estúdio inteligente", "CLONAVOZ.COM.BR", (255, 100, 0)),
    (37.5, 42.5, "E o detalhe mais impressionante:", "ESSA VOZ NÃO É UMA PESSOA REAL!", (255, 60, 40)),
    (42.5, 47.5, "100% criada por IA em 2 segundos", "TESTE GRÁTIS NO LINK DA BIO", (255, 215, 0))
]

def get_current_segment(t):
    for start, end, l1, l2, color in SEGMENTS:
        if start <= t < end:
            return l1, l2, color, start, end
    return None, None, (255, 255, 255), 0, 0

frames_dir = os.path.join(SCRATCH_DIR, "frames")
if os.path.exists(frames_dir):
    shutil.rmtree(frames_dir)
os.makedirs(frames_dir, exist_ok=True)

# Pre-cria overlay de vinheta escura para garantir que o texto SEMPRE tenha contraste máximo
vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
for y in range(HEIGHT):
    # Gradiente escuro no terço inferior onde o texto fica
    if y > 800:
        alpha = int(min(240, ((y - 800) / (HEIGHT - 800)) * 235))
        v_draw.line([(0, y), (WIDTH, y)], fill=(5, 7, 12, alpha))
    elif y < 350:
        alpha = int(min(180, ((350 - y) / 350) * 160))
        v_draw.line([(0, y), (WIDTH, y)], fill=(5, 7, 12, alpha))

print("Renderizando frames cinematográficos com Ken Burns e legendas de alto contraste...")
for f_idx in range(total_frames):
    t_sec = f_idx / FPS
    
    # 1. Ken Burns Effect: Zoom suave contínuo de 1.0x a 1.08x
    zoom_factor = 1.0 + (t_sec / duration) * 0.08
    zw = int(WIDTH * zoom_factor)
    zh = int(HEIGHT * zoom_factor)
    zoomed = base_bg.resize((zw, zh), Image.Resampling.BILINEAR)
    crop_x = (zw - WIDTH) // 2
    crop_y = (zh - HEIGHT) // 2
    frame_bg = zoomed.crop((crop_x, crop_y, crop_x + WIDTH, crop_y + HEIGHT)).convert("RGBA")

    # 2. Aplica vinheta escura por cima para garantir 100% legibilidade
    frame_bg.alpha_composite(vignette)
    draw = ImageDraw.Draw(frame_bg)

    # 3. Badge Superior Elegante
    badge_title = "ESTRATÉGIA DE RETENÇÃO 2026" if t_sec < 32.5 else "INTELIGÊNCIA ARTIFICIAL BRASILEIRA"
    bw = 540
    bh = 52
    bx = (WIDTH - bw) // 2
    by = 180
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=26, fill=(10, 14, 22, 220), outline=(255, 255, 255, 60), width=1)
    draw.text((WIDTH // 2, by + bh // 2), f"🔥 {badge_title}", fill=(240, 240, 250), font=font_category, anchor="mm")

    # 4. Waveform sonoro central (indica voz neural ao vivo)
    sample_start = f_idx * samples_per_frame
    sample_end = min(sample_start + samples_per_frame, len(audio_data))
    chunk = audio_data[sample_start:sample_end]
    vol = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.04
    vol_norm = min(max(vol * 5.5, 0.08), 1.0)

    num_bars = 24
    bar_w = 6
    spacing = 10
    total_w = num_bars * (bar_w + spacing)
    start_x = (WIDTH - total_w) // 2
    center_y = 1040

    for b in range(num_bars):
        dist = abs(b - num_bars / 2) / (num_bars / 2)
        factor = math.cos(dist * math.pi / 2)
        h = int(8 + (vol_norm * 80 + math.sin(t_sec * 8.0 + b * 0.5) * 15) * factor)
        h = max(h, 6)
        bx_bar = start_x + b * (bar_w + spacing)
        # Bar color: cyan nos primeiros segundos, depois ouro e laranja
        if t_sec < 25.5:
            bar_color = (120, 230, 255, int(150 + factor * 105))
        elif t_sec < 37.5:
            bar_color = (255, 215, 0, int(150 + factor * 105))
        else:
            bar_color = (255, 80, 20, 255)
        draw.rounded_rectangle([bx_bar, center_y - h, bx_bar + bar_w, center_y + h], radius=3, fill=bar_color)

    # 5. Legendas em Cápsula Escura com Contraste Absoluto
    l1, l2, highlight_color, st, et = get_current_segment(t_sec)
    if l1 and l2:
        card_w = 980
        card_h = 240
        card_x = (WIDTH - card_w) // 2
        card_y = 1180

        # Fundo de vidro escuro translúcido atrás do texto
        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=32,
            fill=(5, 7, 12, 235),
            outline=(255, 255, 255, 40) if t_sec < 37.5 else (255, 77, 0, 180),
            width=2
        )

        # Linha 1 (Branco Puro com sombra escura)
        draw.text((WIDTH // 2 + 2, card_y + 62), l1, fill=(0, 0, 0, 200), font=font_line1, anchor="mm")
        draw.text((WIDTH // 2, card_y + 60), l1, fill=(255, 255, 255), font=font_line1, anchor="mm")

        # Linha 2 (Destaque em tamanho gigante e cor viva)
        use_font = font_huge_alert if (t_sec >= 37.5) else font_line2_huge
        draw.text((WIDTH // 2 + 2, card_y + 152), l2, fill=(0, 0, 0, 220), font=use_font, anchor="mm")
        draw.text((WIDTH // 2, card_y + 150), l2, fill=highlight_color, font=use_font, anchor="mm")

    # 6. Clímax Final: Logo e Botão de Ação (Últimos 10 segundos)
    if t_sec >= 37.5 and logo_img:
        logo_x = (WIDTH - logo_img.width) // 2
        logo_y = 810
        frame_bg.paste(logo_img, (logo_x, logo_y), logo_img)

    if t_sec >= 42.0:
        # Botão CTA de conversão imediata
        btn_w = 660
        btn_h = 90
        btn_x = (WIDTH - btn_w) // 2
        btn_y = 1480
        draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=28, fill=(255, 77, 0), outline=(255, 160, 80), width=3)
        draw.text((WIDTH // 2, btn_y + btn_h // 2), "TESTAR GRÁTIS NO PIX", fill=(0, 0, 0), font=font_cta_btn, anchor="mm")
        draw.text((WIDTH // 2, btn_y + btn_h + 45), "clonavoz.com.br • A partir de R$ 9,90", fill=(220, 220, 230), font=font_category, anchor="mm")

    # Rodapé de áudio
    draw.text((WIDTH // 2, 1830), "🎧 Ouça com som para perceber a dicção natural", fill=(160, 165, 185), font=font_footer, anchor="mm")

    # Salva frame em JPG de alta qualidade
    frame_bg.convert("RGB").save(os.path.join(frames_dir, f"frame_{f_idx:05d}.jpg"), quality=93)
    if f_idx % 180 == 0:
        print(f"Progresso: {f_idx}/{total_frames} frames ({(f_idx/total_frames)*100:.0f}%)")

print("Frames compilados com sucesso! Gerando vídeo MP4...")

raw_video_path = os.path.join(SCRATCH_DIR, "video_raw.mp4")
cmd_video = [
    "ffmpeg", "-y", "-framerate", str(FPS),
    "-i", os.path.join(frames_dir, "frame_%05d.jpg"),
    "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
    raw_video_path
]
subprocess.run(cmd_video, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# Trilha sonora cinematográfica
bgm_file = os.path.join(STATIC_DIR, "bgm", "bgm_cinematic.mp3")

# Arquivo principal temporário
final_temp = os.path.join(SCRATCH_DIR, "video_final_mixed.mp4")

if os.path.exists(bgm_file):
    # Mixa com BGM em volume sutil (0.11)
    cmd_audio = [
        "ffmpeg", "-y",
        "-i", raw_video_path,
        "-i", wav_path,
        "-i", bgm_file,
        "-filter_complex",
        "[1:a]volume=1.05[v_voice];[2:a]volume=0.10[v_bgm];[v_voice][v_bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        final_temp
    ]
else:
    cmd_audio = [
        "ffmpeg", "-y",
        "-i", raw_video_path,
        "-i", wav_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        final_temp
    ]

subprocess.run(cmd_audio, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# Distribui nas pastas solicitadas pelo cliente
targets = [
    os.path.join(MARKETING_DIR, "video_viral_segredo_canais_dark.mp4"),
    os.path.join(MARKETING_DIR, "1_INSTAGRAM", "Reels_Segredo_Canais_Dark.mp4"),
    os.path.join(MARKETING_DIR, "2_TIKTOK", "TikTok_Segredo_Canais_Dark.mp4"),
    os.path.join(MARKETING_DIR, "3_YOUTUBE", "Shorts_Segredo_Canais_Dark.mp4"),
    os.path.join(STATIC_DIR, "video_viral_segredo_canais_dark.mp4")
]

for t in targets:
    shutil.copy2(final_temp, t)
    print(f"Salvo em: {t}")

# Salva arquivo de roteiro e descrição pronto para postagem
desc_path = os.path.join(MARKETING_DIR, "Descricao_Video_Canais_Dark.txt")
desc_content = """TITULO / GANCHO DO VÍDEO:
O Maior Segredo dos Canais Anônimos que Faturam Milhares na Internet (Sem Mostrar o Rosto)

LEGENDA PRONTA PARA POSTAR (INSTAGRAM REELS, TIKTOK E YOUTUBE SHORTS):
Você já se perguntou como canais anônimos faturam milhares de reais sem nunca gravar o próprio rosto? 🤯

A chave está na retenção: narrativas cativantes com vozes humanas, expressivas e envolventes.

E o mais chocante de tudo: essa voz que você acabou de ouvir durante todo este vídeo NÃO existe. Ela foi 100% gerada por Inteligência Artificial no Clonavoz em menos de 2 segundos.

Chega de gastar horas gravando no microfone ou pagando mensalidades absurdas em dólar em plataformas gringas.

🎙️ Teste grátis agora mesmo:
👉 Acesse o link na bio ou digite: https://clonavoz.com.br
💳 Recarregue créditos no PIX a partir de R$ 9,90 (sem mensalidade fixa!).

#canaldark #inteligenciaartificial #clonavoz #cortes #afiliados #marketingdigital #chatgpt #locucao #edicaodevideo #capcut
"""

with open(desc_path, "w", encoding="utf-8") as f:
    f.write(desc_content)

print(f"Descrições e tags salvas em: {desc_path}")
print("PROCESSO CONCLUÍDO COM SUCESSO!")
