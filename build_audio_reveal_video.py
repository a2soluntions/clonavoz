import os
import sys
import math
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import soundfile as sf
import tts_engine

BASE_DIR = r"e:\A2\projetos\gerador de voz com texto"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
STATIC_DIR = os.path.join(BASE_DIR, "static")
MARKETING_DIR = r"E:\A2\Projetos marcketing\clonavoz"
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch_audio_reveal")

os.makedirs(SCRATCH_DIR, exist_ok=True)
os.makedirs(MARKETING_DIR, exist_ok=True)
for sub in ["1_INSTAGRAM", "2_TIKTOK", "3_YOUTUBE"]:
    os.makedirs(os.path.join(MARKETING_DIR, sub), exist_ok=True)

WIDTH = 1080
HEIGHT = 1920
FPS = 30

# Texto motivacional puro (que aparece na folha)
text_paper = (
    "Hoje é uma nova oportunidade para recomeçar com o coração leve e a mente aberta. "
    "Não carregue o peso do ontem nem se preocupe antecipadamente com o amanhã. "
    "Cada pequeno passo dado com coragem e esperança constrói o caminho para grandes realizações e conquistas. "
    "Lembre-se de que a sua energia molda o seu mundo: escolha sorrir, respirar fundo e dar o seu melhor hoje. "
    "Você é mais forte do que imagina e capaz de transformar qualquer desafio em sabedoria. "
    "Tenha um dia incrível e repleto de luz!"
)

# Texto completo para o áudio com revelação somente por áudio no final
text_audio = text_paper + " Esse áudio foi gerado com o Clonavoz."

# 1. Síntese do áudio
print("Sintetizando áudio completo com voz Eduarda (speed 0.95)...")
synth_res = tts_engine.synthesize_text(text_audio, voice_key='eduarda', speed=0.95)
voice_wav = synth_res['file_path']
voice_dur = synth_res['duration_seconds']

total_duration = voice_dur + 1.5
total_frames = int(total_duration * FPS)
print(f"Áudio sintetizado: {voice_wav} ({voice_dur:.2f}s, total vídeo: {total_duration:.2f}s, {total_frames} frames)")

# 2. Geração da trilha SFX da máquina de escrever (apenas durante a digitação do texto motivacional)
typing_end_time = 25.8
sr = 44100
total_samples = int(total_duration * sr)
sfx_audio = np.zeros(total_samples, dtype=np.float32)

def generate_keystroke(is_space=False, is_punct=False):
    dur = 0.038
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    click = np.random.normal(0, 0.35, n) * np.exp(-t * 160)
    freq = 950 if is_space else (2800 if is_punct else 1750 + np.random.uniform(-150, 150))
    metal = np.sin(2 * np.pi * freq * t) * np.exp(-t * 110) * 0.25
    thump = np.sin(2 * np.pi * 95 * t) * np.exp(-t * 70) * 0.35
    sig = click + metal + thump
    sig = sig / (np.max(np.abs(sig)) + 1e-6)
    vol = 0.45 if is_space else (0.85 if is_punct else 0.70)
    return sig * vol

def generate_ding():
    dur = 0.45
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    bell = (np.sin(2 * np.pi * 2350 * t) + 0.35 * np.sin(2 * np.pi * 4700 * t)) * np.exp(-t * 9)
    return bell * 0.45

bell_ding = generate_ding()
total_chars = len(text_paper)

for c_idx in range(total_chars):
    char_time = (c_idx / total_chars) * typing_end_time
    sample_pos = int(char_time * sr)
    ch = text_paper[c_idx]
    
    is_space = (ch == ' ')
    is_punct = (ch in '.,:;!?')
    click = generate_keystroke(is_space, is_punct)
    
    end_s = min(sample_pos + len(click), total_samples)
    sfx_audio[sample_pos:end_s] += click[:end_s - sample_pos]
    
    if ch in '.!' and c_idx > 40:
        ding_end = min(sample_pos + len(bell_ding), total_samples)
        sfx_audio[sample_pos:ding_end] += bell_ding[:ding_end - sample_pos]

sfx_wav_path = os.path.join(SCRATCH_DIR, "typewriter_sfx.wav")
sf.write(sfx_wav_path, sfx_audio, sr)

# 3. Quebra de linhas na folha
font_title = ImageFont.truetype('C:/Windows/Fonts/georgiab.ttf', 44)
font_date = ImageFont.truetype('C:/Windows/Fonts/courbd.ttf', 24)
font_typewriter = ImageFont.truetype('C:/Windows/Fonts/courbd.ttf', 36)

px1, py1 = 80, 200
px2, py2 = WIDTH - 80, HEIGHT - 200
paper_w = px2 - px1
paper_h = py2 - py1
max_text_w = paper_w - 120

words = text_paper.split()
wrapped_lines = []
cur_words = []
for w in words:
    trial = ' '.join(cur_words + [w])
    bbox = font_typewriter.getbbox(trial)
    if bbox[2] - bbox[0] > max_text_w:
        wrapped_lines.append(' '.join(cur_words))
        cur_words = [w]
    else:
        cur_words.append(w)
if cur_words:
    wrapped_lines.append(' '.join(cur_words))

char_map = []
for l_idx, line in enumerate(wrapped_lines):
    for c_in_l, char in enumerate(line):
        char_map.append((l_idx, c_in_l, char))
    if l_idx < len(wrapped_lines) - 1:
        char_map.append((l_idx, len(line), ' '))

# 4. Renderização dos frames (FOLHA LIMPA SEM ENDEREÇOS OU URLS)
frames_dir = os.path.join(SCRATCH_DIR, "frames")
if os.path.exists(frames_dir):
    shutil.rmtree(frames_dir)
os.makedirs(frames_dir, exist_ok=True)

print("Renderizando vídeo com revelação exclusivamente por áudio...")
start_y = py1 + 175
line_h = 58

for f_idx in range(total_frames):
    t_sec = f_idx / FPS
    
    # Fundo amadeirado suave e acolhedor
    img = Image.new("RGBA", (WIDTH, HEIGHT), (22, 17, 14, 255))
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        factor = y / HEIGHT
        r = int(27 * (1 - factor * 0.4) + 12 * factor)
        g = int(21 * (1 - factor * 0.4) + 10 * factor)
        b = int(17 * (1 - factor * 0.4) + 8 * factor)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # Luz de sol da manhã
    sun_glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(sun_glow)
    s_draw.ellipse([WIDTH - 650, -220, WIDTH + 450, 850], fill=(255, 215, 145, 24))
    img.alpha_composite(sun_glow)

    # Sombra da folha
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sh_draw = ImageDraw.Draw(shadow)
    sh_draw.rounded_rectangle([px1 + 8, py1 + 14, px2 + 8, py2 + 14], radius=28, fill=(0, 0, 0, 115))
    img.alpha_composite(shadow)

    # Folha de papel marfim linho puro
    paper = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(paper)
    p_draw.rounded_rectangle([px1, py1, px2, py2], radius=24, fill=(250, 248, 242, 255), outline=(225, 218, 204, 255), width=2)

    # Cabeçalho decorativo
    p_draw.line([(px1 + 50, py1 + 135), (px2 - 50, py1 + 135)], fill=(225, 218, 205, 255), width=1)
    p_draw.text((px1 + 55, py1 + 60), "REFLEXÃO DO DIA", fill=(105, 90, 75, 255), font=font_title)
    p_draw.text((px1 + 55, py1 + 105), "CAPÍTULO DE HOJE • LEIA COM O CORAÇÃO", fill=(145, 130, 115, 255), font=font_date)

    # Caracteres ativos
    if t_sec < typing_end_time:
        active_chars_count = int((t_sec / typing_end_time) * len(char_map))
    else:
        active_chars_count = len(char_map)

    rendered_lines = {l_i: "" for l_i in range(len(wrapped_lines))}
    cursor_pos = None

    for i in range(min(active_chars_count, len(char_map))):
        l_i, c_in_l, char = char_map[i]
        rendered_lines[l_i] += char
        cursor_pos = (l_i, len(rendered_lines[l_i]))

    for l_idx in range(len(wrapped_lines)):
        line_text = rendered_lines[l_idx]
        ly = start_y + l_idx * line_h
        if line_text:
            p_draw.text((px1 + 60, ly), line_text, fill=(26, 28, 33, 255), font=font_typewriter)

    # Cursor piscante (|)
    if cursor_pos and t_sec < typing_end_time + 1.0:
        c_line, c_len = cursor_pos
        if int(t_sec * 5) % 2 == 0:
            current_line_text = rendered_lines[c_line]
            bbox_line = font_typewriter.getbbox(current_line_text)
            cx = px1 + 60 + (bbox_line[2] - bbox_line[0]) + 3
            cy = start_y + c_line * line_h
            p_draw.text((cx, cy), "|", fill=(210, 70, 15, 255), font=font_typewriter)

    # Rodapé sutil da folha (SEM ENDEREÇO OU PROPAGANDA VISUAL)
    p_draw.line([(px1 + 50, py2 - 100), (px2 - 50, py2 - 100)], fill=(225, 218, 205, 255), width=1)
    p_draw.text((WIDTH // 2, py2 - 65), "✨ Guarde esta mensagem com você", fill=(155, 140, 125, 255), font=font_date, anchor="mm")

    img.alpha_composite(paper)

    img.convert("RGB").save(os.path.join(frames_dir, f"frame_{f_idx:05d}.jpg"), quality=94)
    if f_idx % 150 == 0:
        print(f"Progresso: {f_idx}/{total_frames} frames ({(f_idx/total_frames)*100:.0f}%)")

print("Frames gerados! Compilando MP4...")

raw_video = os.path.join(SCRATCH_DIR, "raw_video.mp4")
cmd_raw = [
    "ffmpeg", "-y", "-framerate", str(FPS),
    "-i", os.path.join(frames_dir, "frame_%05d.jpg"),
    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
    raw_video
]
subprocess.run(cmd_raw, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# 5. Mixagem do Áudio: Voz com Revelação Final + SFX Máquina + Música Suave
bgm_calm = os.path.join(STATIC_DIR, "bgm", "bgm_calm.mp3")
final_mixed_mp4 = os.path.join(SCRATCH_DIR, "final_mixed.mp4")

print("Mixando áudio com trilha suave e revelação...")
if os.path.exists(bgm_calm):
    cmd_mix = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", voice_wav,
        "-i", sfx_wav_path,
        "-i", bgm_calm,
        "-filter_complex",
        "[1:a]volume=1.05[a_voice];"
        "[2:a]volume=0.22[a_sfx];"
        "[3:a]volume=0.10[a_music];"
        "[a_voice][a_sfx][a_music]amix=inputs=3:duration=first:dropout_transition=2[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        final_mixed_mp4
    ]
else:
    cmd_mix = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", voice_wav,
        "-i", sfx_wav_path,
        "-filter_complex",
        "[1:a]volume=1.05[a_voice];"
        "[2:a]volume=0.22[a_sfx];"
        "[a_voice][a_sfx]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        final_mixed_mp4
    ]

subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# 6. Salva EXATAMENTE com o nome do texto (SEM palavra Reels)
file_basename = "Hoje e uma nova oportunidade para recomecar.mp4"

destinations = [
    os.path.join(MARKETING_DIR, file_basename),
    os.path.join(MARKETING_DIR, "1_INSTAGRAM", file_basename),
    os.path.join(MARKETING_DIR, "2_TIKTOK", file_basename),
    os.path.join(MARKETING_DIR, "3_YOUTUBE", file_basename),
    os.path.join(STATIC_DIR, file_basename)
]

for d in destinations:
    shutil.copy2(final_mixed_mp4, d)
    print(f"Salvo em: {d}")

# 7. Salva descrição sem URLs visíveis agressivas
desc_path = os.path.join(MARKETING_DIR, "Hoje e uma nova oportunidade para recomecar - Descricao.txt")
desc_content = """LEGENDA PRONTA PARA POSTAR:
Hoje é uma nova oportunidade para recomeçar com o coração leve e a mente aberta. ✨

Não carregue o peso do ontem nem se preocupe antecipadamente com o amanhã. Cada pequeno passo dado com coragem e esperança constrói o caminho para grandes realizações.

Você é mais forte do que imagina. Tenha um dia incrível e abençoado! 🙏❤️

---
Gostou da voz deste vídeo?
Ela foi 100% gerada com o Clonavoz em menos de 2 segundos.
👉 Link na bio para criar suas próprias narrações!

#bomdia #motivacao #reflexao #pensamentododia #paz #esperanca #clonavoz #asmr #reelsbrasil
"""

with open(desc_path, "w", encoding="utf-8") as f:
    f.write(desc_content)

print("TUDO CONCLUÍDO COM SUCESSO!")
