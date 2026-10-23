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
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch_viral")

os.makedirs(OUTPUT_DIR, exist_ok=True)
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

font_tag = get_font(28, bold=True)
font_huge = get_font(72, bold=True)
font_highlight = get_font(80, bold=True)
font_sub = get_font(44, bold=False)
font_cta_btn = get_font(42, bold=True)
font_url = get_font(48, bold=True)

# 1. Gera ou recupera áudio da narração com a voz Eduarda
script_text = (
    "Você já percebeu como o seu cérebro tenta te enganar o tempo todo? "
    "Se você prestar atenção na voz que está escutando agora, sua mente automaticamente imagina uma pessoa real falando. "
    "Você sente a entonação, a clareza e o ritmo natural das palavras. "
    "Parece humano demais, não é? "
    "Mas aqui está o segredo: essa voz não existe no mundo real. "
    "Ela foi cem por cento criada por inteligência artificial no Clonavoz. "
    "Acesse o link da bio e crie as suas de graça."
)

print("Sintetizando áudio com voz Eduarda...")
synth_res = tts_engine.synthesize_text(script_text, voice_key='eduarda', speed=1.0)
wav_path = synth_res['file_path']
duration = synth_res['duration_seconds']
total_frames = int(duration * FPS)
print(f"Áudio gerado: {wav_path} ({duration:.2f}s, {total_frames} frames)")

# Carrega amplitude do áudio para o waveform animado
audio_data, sr = sf.read(wav_path)
if len(audio_data.shape) > 1:
    audio_data = np.mean(audio_data, axis=1)

# Divide áudio em blocos por frame
samples_per_frame = int(sr / FPS)

# Segmentos de texto sincronizados com o tempo (em segundos)
SUBTITLES = [
    (0.0, 3.8, "Você já percebeu como o seu cérebro", "tenta te enganar o tempo todo?"),
    (3.8, 8.5, "Se você prestar atenção na voz", "que está escutando agora..."),
    (8.5, 12.8, "sua mente automaticamente imagina", "uma pessoa real falando."),
    (12.8, 16.2, "Você sente a entonação, o ritmo", "e a emoção natural das palavras."),
    (16.2, 18.5, "Parece humano demais,", "não é?"),
    (18.5, 21.6, "Mas aqui está o segredo:", "essa voz NÃO EXISTE."),
    (21.6, 25.5, "Ela foi 100% criada por IA no", "CLONAVOZ.COM.BR")
]

# Logo do Clonavoz
logo_path = os.path.join(STATIC_DIR, "logo_perfil_instagram.png")
if os.path.exists(logo_path):
    logo_img = Image.open(logo_path).convert("RGBA").resize((220, 220), Image.Resampling.LANCZOS)
else:
    logo_img = None

def get_current_subtitle(t):
    for start, end, l1, l2 in SUBTITLES:
        if start <= t < end:
            return l1, l2, start, end
    return None, None, 0, 0

frames_dir = os.path.join(SCRATCH_DIR, "frames")
if os.path.exists(frames_dir):
    shutil.rmtree(frames_dir)
os.makedirs(frames_dir, exist_ok=True)

print("Renderizando frames cinematográficos em 9:16 (1080x1920)...")
for f_idx in range(total_frames):
    t_sec = f_idx / FPS
    
    # Base Image com degradê profundo moderno
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 9, 13, 255))
    draw = ImageDraw.Draw(img)

    # Brilho de fundo pulsante sutil
    pulse = (math.sin(t_sec * 3.0) + 1.0) / 2.0
    glow_radius = int(320 + pulse * 60)
    glow_color = (255, 77, 0, int(18 + pulse * 14))
    draw.ellipse(
        [WIDTH // 2 - glow_radius, HEIGHT // 2 - 100 - glow_radius, WIDTH // 2 + glow_radius, HEIGHT // 2 - 100 + glow_radius],
        fill=glow_color
    )

    # Tag Superior Flutuante
    tag_text = "💡 EXPERIMENTO PSICOLÓGICO" if t_sec < 18.5 else "🎙️ INTELIGÊNCIA ARTIFICIAL"
    tag_bg = (255, 255, 255, 12) if t_sec < 18.5 else (255, 77, 0, 35)
    tag_border = (255, 255, 255, 30) if t_sec < 18.5 else (255, 77, 0, 140)
    tag_color = (220, 220, 230, 255) if t_sec < 18.5 else (255, 120, 40, 255)

    # Desenha Tag
    bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    px, py = 35, 12
    bx = (WIDTH - tw - px * 2) // 2
    by = 380
    draw.rounded_rectangle([bx, by, bx + tw + px * 2, by + th + py * 2], radius=24, fill=tag_bg, outline=tag_border, width=2)
    draw.text((WIDTH // 2, by + th // 2 + py), tag_text, fill=tag_color, font=font_tag, anchor="mm")

    # Waveform Dinâmico Central (barras dançantes que reagem ao áudio)
    sample_start = f_idx * samples_per_frame
    sample_end = min(sample_start + samples_per_frame, len(audio_data))
    if sample_start < len(audio_data) and sample_end > sample_start:
        chunk = audio_data[sample_start:sample_end]
        vol = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.05
    else:
        vol = 0.05

    vol_norm = min(max(vol * 5.5, 0.08), 1.0)
    
    num_bars = 28
    bar_w = 8
    spacing = 14
    total_w = num_bars * (bar_w + spacing)
    start_x = (WIDTH - total_w) // 2
    center_y = 660

    for b in range(num_bars):
        dist_from_center = abs(b - num_bars / 2) / (num_bars / 2)
        bar_factor = math.cos(dist_from_center * math.pi / 2)
        wave_motion = math.sin(t_sec * 6.0 + b * 0.4) * 0.25
        h = int(12 + (vol_norm * 110 + wave_motion * 30) * bar_factor)
        h = max(h, 8)
        bx = start_x + b * (bar_w + spacing)
        
        # Cor das barras (laranja vibrante no clímax, branco/prata antes)
        if t_sec < 18.5:
            b_color = (255, 255, 255, int(140 + bar_factor * 100))
        else:
            b_color = (255, int(70 + bar_factor * 80), int(10 + bar_factor * 20), 255)
            
        draw.rounded_rectangle([bx, center_y - h, bx + bar_w, center_y + h], radius=4, fill=b_color)

    # Legendas Cinematográficas Sincronizadas
    l1, l2, start_t, end_t = get_current_subtitle(t_sec)
    if l1 and l2:
        y_text = 980
        
        # Destaque especial na revelação final
        if t_sec >= 18.5 and t_sec < 21.6:
            draw.text((WIDTH // 2, y_text), l1, fill=(240, 240, 245), font=font_sub, anchor="mm")
            # Texto NÃO EXISTE gigante em vermelho/laranja neon
            draw.text((WIDTH // 2, y_text + 95), l2, fill=(255, 60, 20), font=font_highlight, anchor="mm")
        elif t_sec >= 21.6:
            draw.text((WIDTH // 2, y_text - 40), l1, fill=(240, 240, 245), font=font_sub, anchor="mm")
            draw.text((WIDTH // 2, y_text + 45), l2, fill=(255, 95, 0), font=font_huge, anchor="mm")
            
            # Badge de CTA no final
            btn_w = 640
            btn_h = 95
            btn_x = (WIDTH - btn_w) // 2
            btn_y = 1220
            draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=28, fill=(255, 77, 0), outline=(255, 140, 60), width=3)
            draw.text((WIDTH // 2, btn_y + btn_h // 2), "TESTE GRÁTIS NO PIX", fill=(0, 0, 0), font=font_cta_btn, anchor="mm")
            
            draw.text((WIDTH // 2, btn_y + btn_h + 55), "Link na Bio • clonavoz.com.br", fill=(180, 180, 195), font=font_tag, anchor="mm")
            
            # Mostra Logo se disponível
            if logo_img:
                logo_x = (WIDTH - logo_img.width) // 2
                logo_y = 750
                img.paste(logo_img, (logo_x, logo_y), logo_img)
        else:
            # Estilo padrão elegante com 2 linhas
            draw.text((WIDTH // 2, y_text), l1, fill=(255, 255, 255), font=font_sub, anchor="mm")
            draw.text((WIDTH // 2, y_text + 85), l2, fill=(255, 205, 120), font=font_huge, anchor="mm")

    # Rodapé sutil de fone de ouvido para incentivar o áudio
    draw.text((WIDTH // 2, 1780), "🎧 ATIVE O SOM PARA ESCUTAR", fill=(120, 120, 135, 180), font=font_tag, anchor="mm")

    # Salva frame
    img.convert("RGB").save(os.path.join(frames_dir, f"frame_{f_idx:05d}.jpg"), quality=92)
    if f_idx % 120 == 0:
        print(f"Progresso: {f_idx}/{total_frames} frames ({(f_idx/total_frames)*100:.0f}%)")

print("Frames gerados com sucesso! Compilando vídeo MP4...")

# Compilação do vídeo com ffmpeg e trilha sonora
raw_video_path = os.path.join(SCRATCH_DIR, "video_raw.mp4")
cmd_video = [
    "ffmpeg", "-y", "-framerate", str(FPS),
    "-i", os.path.join(frames_dir, "frame_%05d.jpg"),
    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
    raw_video_path
]
subprocess.run(cmd_video, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# Trilha sonora de fundo mixada sutilmente
bgm_file = os.path.join(STATIC_DIR, "bgm", "bgm_cinematic.mp3")
final_video_name = "video_viral_revelacao_clonavoz.mp4"
final_video_path = os.path.join(STATIC_DIR, final_video_name)

print("Mixando voz neural com trilha cinematográfica...")
if os.path.exists(bgm_file):
    # Mixa áudio da voz (volume 1.0) com BGM sutil (volume 0.12)
    cmd_audio = [
        "ffmpeg", "-y",
        "-i", raw_video_path,
        "-i", wav_path,
        "-i", bgm_file,
        "-filter_complex",
        "[1:a]volume=1.0[v_voice];[2:a]volume=0.12[v_bgm];[v_voice][v_bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        final_video_path
    ]
else:
    cmd_audio = [
        "ffmpeg", "-y",
        "-i", raw_video_path,
        "-i", wav_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        final_video_path
    ]

subprocess.run(cmd_audio, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

print(f"\n==========================================")
print(f"🎉 VÍDEO VIRAL GERADO COM SUCESSO!")
print(f"Arquivo final: {final_video_path}")
print(f"Duração: {duration:.1f}s")
print(f"Formato: 1080x1920 (9:16 vertical Reels/TikTok)")
print(f"==========================================")
