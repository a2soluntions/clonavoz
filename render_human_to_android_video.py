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
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch_human_android")

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
font_line2_huge = get_font(58, bold=True)
font_huge_alert = get_font(64, bold=True)
font_cta_btn = get_font(40, bold=True)
font_footer = get_font(24, bold=False)

# 1. Carrega áudio da narração (46.91s)
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

# Pré-computa envelopes de volume do áudio para sincronização labial fluida
vol_envelopes = []
for f_i in range(total_frames):
    s_start = f_i * samples_per_frame
    s_end = min(s_start + samples_per_frame, len(audio_data))
    chunk = audio_data[s_start:s_end]
    v = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.01
    vol_envelopes.append(v)

# Suavização temporal do volume (evita tremor brusco)
vol_smooth = []
window = 3
for i in range(len(vol_envelopes)):
    w_start = max(0, i - window)
    w_end = min(len(vol_envelopes), i + window + 1)
    vol_smooth.append(float(np.mean(vol_envelopes[w_start:w_end])))

# 2. Carrega as duas imagens: Humana (antes) e Androide (depois)
path_human = r"E:\A2\imagens de modelos\antes (1).jpg"
path_droid = r"E:\A2\imagens de modelos\depois (1).jpg"

im_human_raw = Image.open(path_human).convert("RGB")
im_droid_raw = Image.open(path_droid).convert("RGB")

src_w, src_h = im_human_raw.size
target_ratio = WIDTH / HEIGHT
new_w = int(src_h * target_ratio)
left = (src_w - new_w) // 2
crop_box = (left, 0, left + new_w, src_h)

base_human = im_human_raw.crop(crop_box).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).convert("RGBA")
base_droid = im_droid_raw.crop(crop_box).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).convert("RGBA")

# Coordenadas da boca no formato 1080x1920
scale_x = WIDTH / new_w
scale_y = HEIGHT / src_h
mx1 = int((440 - left) * scale_x)
mx2 = int((680 - left) * scale_x)
my1 = int(700 * scale_y)
my2 = int(860 * scale_y)
mouth_w = mx2 - mx1
mouth_h = my2 - my1

# Máscara elíptica suave de difusão para a boca
mouth_mask = Image.new("L", (mouth_w, mouth_h), 0)
m_draw = ImageDraw.Draw(mouth_mask)
m_draw.ellipse([18, 14, mouth_w - 18, mouth_h - 14], fill=255)
mouth_mask_blur = mouth_mask.filter(ImageFilter.GaussianBlur(16))

# Logo Clonavoz
logo_path = os.path.join(STATIC_DIR, "logo_perfil_instagram.png")
logo_img = Image.open(logo_path).convert("RGBA").resize((180, 180), Image.Resampling.LANCZOS) if os.path.exists(logo_path) else None

# Segmentos de Legendas e Cores
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

# Pré-cria vinheta escura para garantir contraste perfeito no terço inferior
vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)
for y in range(HEIGHT):
    if y > 850:
        alpha = int(min(240, ((y - 850) / (HEIGHT - 850)) * 235))
        v_draw.line([(0, y), (WIDTH, y)], fill=(5, 7, 12, alpha))
    elif y < 350:
        alpha = int(min(180, ((350 - y) / 350) * 160))
        v_draw.line([(0, y), (WIDTH, y)], fill=(5, 7, 12, alpha))

frames_dir = os.path.join(SCRATCH_DIR, "frames")
if os.path.exists(frames_dir):
    shutil.rmtree(frames_dir)
os.makedirs(frames_dir, exist_ok=True)

# Função para aplicar modulação labial sincronizada com o áudio
def apply_lip_sync(base_img, vol):
    vol_clamped = min(max(vol * 5.5, 0.0), 1.0)
    if vol_clamped < 0.06:
        return base_img # Boca fechada/repouso
    
    # Fator de abertura labial (até +20% na vertical)
    stretch_factor = 1.0 + vol_clamped * 0.20
    new_h = int(mouth_h * stretch_factor)
    
    mouth_crop = base_img.crop((mx1, my1, mx2, my2))
    mouth_stretched = mouth_crop.resize((mouth_w, new_h), Image.Resampling.BILINEAR)
    mask_stretched = mouth_mask_blur.resize((mouth_w, new_h), Image.Resampling.BILINEAR)
    
    out_img = base_img.copy()
    # Centraliza o esticamento suave na boca
    y_offset = my1 - (new_h - mouth_h) // 4
    out_img.paste(mouth_stretched, (mx1, y_offset), mask_stretched)
    return out_img

print("Renderizando vídeo com transição Humana -> Androide e animação de fala...")
for f_idx in range(total_frames):
    t_sec = f_idx / FPS
    vol = vol_smooth[f_idx]
    
    # 1. Movimento suave de respiração (micro-oscilação de 2 pixels)
    breath = math.sin(t_sec * 3.5) * 2.0
    
    # 2. Definição da cena (Humana vs Transição vs Androide)
    # Transição acontece entre 32.5s e 36.5s
    if t_sec < 32.5:
        # CENA 1: MULHER HUMANA
        frame_face = apply_lip_sync(base_human, vol)
    elif t_sec < 36.5:
        # CENA DE TRANSIÇÃO CIBERNÉTICA (SCANLINE / RAIO-X REVELANDO A ANDROIDE)
        trans_progress = (t_sec - 32.5) / 4.0
        scan_y = int(HEIGHT * trans_progress)
        
        # Gera o rosto de ambas com lábios sincronizados
        human_speaking = apply_lip_sync(base_human, vol)
        droid_speaking = apply_lip_sync(base_droid, vol)
        
        frame_face = human_speaking.copy()
        # Parte superior já varrida pelo laser revela a Androide
        if scan_y > 0:
            top_droid = droid_speaking.crop((0, 0, WIDTH, min(scan_y, HEIGHT)))
            frame_face.paste(top_droid, (0, 0))
            
        # Linha de Laser Holográfica Brilhante (Cyan + Branco)
        f_draw = ImageDraw.Draw(frame_face)
        for offset in range(-8, 9):
            glow_alpha = int(255 * (1 - abs(offset) / 9))
            f_draw.line([(0, scan_y + offset), (WIDTH, scan_y + offset)], fill=(0, 225, 255), width=2)
        f_draw.line([(0, scan_y), (WIDTH, scan_y)], fill=(255, 255, 255), width=3)
        
        # Pulso cibernético no momento do scan
        if int(t_sec * 12) % 2 == 0:
            f_draw.text((WIDTH // 2, scan_y - 28), "⚡ DETECTANDO INTELIGÊNCIA ARTIFICIAL", fill=(0, 240, 255), font=font_category, anchor="mm")
    else:
        # CENA 2: MULHER ANDROIDE CIBERNÉTICA
        frame_face = apply_lip_sync(base_droid, vol)

    # 3. Aplica a vinheta escura para contraste absoluto
    frame_face.alpha_composite(vignette)
    draw = ImageDraw.Draw(frame_face)

    # 4. Badge Superior
    badge_title = "ESTRATÉGIA DE RETENÇÃO 2026" if t_sec < 32.5 else "INTELIGÊNCIA ARTIFICIAL BRASILEIRA"
    bw = 540
    bh = 52
    bx = (WIDTH - bw) // 2
    by = 180
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=26, fill=(10, 14, 22, 220), outline=(255, 255, 255, 60), width=1)
    badge_icon = "🔥" if t_sec < 32.5 else "🤖"
    draw.text((WIDTH // 2, by + bh // 2), f"{badge_icon} {badge_title}", fill=(240, 240, 250), font=font_category, anchor="mm")

    # 5. Legendas em Cápsula Escura com Contraste Absoluto
    l1, l2, highlight_color, st, et = get_current_segment(t_sec)
    if l1 and l2:
        card_w = 980
        card_h = 240
        card_x = (WIDTH - card_w) // 2
        card_y = 1180

        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=32,
            fill=(5, 7, 12, 235),
            outline=(255, 255, 255, 40) if t_sec < 37.5 else (255, 77, 0, 180),
            width=2
        )

        draw.text((WIDTH // 2 + 2, card_y + 62), l1, fill=(0, 0, 0, 200), font=font_line1, anchor="mm")
        draw.text((WIDTH // 2, card_y + 60), l1, fill=(255, 255, 255), font=font_line1, anchor="mm")

        use_font = font_huge_alert if (t_sec >= 37.5) else font_line2_huge
        draw.text((WIDTH // 2 + 2, card_y + 152), l2, fill=(0, 0, 0, 220), font=use_font, anchor="mm")
        draw.text((WIDTH // 2, card_y + 150), l2, fill=highlight_color, font=use_font, anchor="mm")

    # 6. Logo e CTA nos últimos segundos
    if t_sec >= 37.5 and logo_img:
        logo_x = (WIDTH - logo_img.width) // 2
        logo_y = 810
        frame_face.paste(logo_img, (logo_x, logo_y), logo_img)

    if t_sec >= 42.0:
        btn_w = 660
        btn_h = 90
        btn_x = (WIDTH - btn_w) // 2
        btn_y = 1480
        draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=28, fill=(255, 77, 0), outline=(255, 160, 80), width=3)
        draw.text((WIDTH // 2, btn_y + btn_h // 2), "TESTAR GRÁTIS NO PIX", fill=(0, 0, 0), font=font_cta_btn, anchor="mm")
        draw.text((WIDTH // 2, btn_y + btn_h + 45), "clonavoz.com.br • A partir de R$ 9,90", fill=(220, 220, 230), font=font_category, anchor="mm")

    # Rodapé sutil
    draw.text((WIDTH // 2, 1830), "🎧 Ouça com som para perceber a dicção natural", fill=(160, 165, 185), font=font_footer, anchor="mm")

    # Salva frame em JPG de alta qualidade
    frame_face.convert("RGB").save(os.path.join(frames_dir, f"frame_{f_idx:05d}.jpg"), quality=93)
    if f_idx % 180 == 0:
        print(f"Progresso: {f_idx}/{total_frames} frames ({(f_idx/total_frames)*100:.0f}%)")

print("Frames compilados! Codificando com FFmpeg...")

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
final_temp = os.path.join(SCRATCH_DIR, "video_final_mixed.mp4")

if os.path.exists(bgm_file):
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

# Distribui nas pastas do projeto
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

print("VÍDEO VIRAL COM TRANSIÇÃO HUMANA -> ANDROIDE CONCLUÍDO COM SUCESSO!")
