import os
import io
import time
import json
import tarfile
import urllib.request
import subprocess
import tempfile
import numpy as np
from scipy import signal
import soundfile as sf
import sherpa_onnx

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CUSTOM_VOICES_DIR = os.path.join(BASE_DIR, "custom_voices")
CUSTOM_VOICES_META = os.path.join(CUSTOM_VOICES_DIR, "voices.json")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(CUSTOM_VOICES_DIR, exist_ok=True)

# Standard Piper Neural voices
VOICES = {
    "sarah": {
        "label": "Sarah (Feminina - Expressiva Natural)",
        "gender": "Feminina",
        "quality": "Alta (Neural Expressiva)",
        "model_id": "vits-piper-pt_BR-dii-high",
        "onnx_file": "pt_BR-dii-high.onnx",
        "tar_url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-dii-high.tar.bz2",
        "base_pitch": 204.0,
        "pitch_shift": -0.85,
        "default_speed": 0.97,
        "dsp_filter": "equalizer=f=320:t=q:w=1.2:g=3.5,equalizer=f=2200:t=q:w=1.5:g=-3.5,equalizer=f=4000:t=q:w=1.0:g=1.5,acompressor=threshold=-16dB:ratio=2.5:attack=5:release=50",
    },
    "duda": {
        "label": "Duda (Feminina - Jovem & Dinâmica)",
        "gender": "Feminina",
        "quality": "Alta (Neural Dinâmica)",
        "model_id": "vits-piper-pt_BR-dii-high",
        "onnx_file": "pt_BR-dii-high.onnx",
        "tar_url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-dii-high.tar.bz2",
        "base_pitch": 180.0,
        "pitch_shift": -2.85,
        "default_speed": 1.12,
        "dsp_filter": "highpass=f=140,equalizer=f=2800:t=q:w=1.2:g=4.0,equalizer=f=5000:t=q:w=1.0:g=2.5,equalizer=f=500:t=q:w=1.5:g=-2.0,acompressor=threshold=-14dB:ratio=3:attack=3:release=40",
    },
    "dii": {
        "label": "Dii (Feminina - Alta Definição)",
        "gender": "Feminina",
        "quality": "Alta (High)",
        "model_id": "vits-piper-pt_BR-dii-high",
        "onnx_file": "pt_BR-dii-high.onnx",
        "tar_url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-dii-high.tar.bz2",
        "base_pitch": 215.0,
    },
    "faber": {
        "label": "Faber (Masculina - Narrador)",
        "gender": "Masculina",
        "quality": "Média (Medium)",
        "model_id": "vits-piper-pt_BR-faber-medium",
        "onnx_file": "pt_BR-faber-medium.onnx",
        "tar_url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-faber-medium.tar.bz2",
        "base_pitch": 125.0,
    },
    "cadu": {
        "label": "Cadu (Masculina - Natural)",
        "gender": "Masculina",
        "quality": "Média (Medium)",
        "model_id": "vits-piper-pt_BR-cadu-medium",
        "onnx_file": "pt_BR-cadu-medium.onnx",
        "tar_url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-cadu-medium.tar.bz2",
        "base_pitch": 130.0,
    },
    "miro": {
        "label": "Miro (Masculina - Alta Definição)",
        "gender": "Masculina",
        "quality": "Alta (High)",
        "model_id": "vits-piper-pt_BR-miro-high",
        "onnx_file": "pt_BR-miro-high.onnx",
        "tar_url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-miro-high.tar.bz2",
        "base_pitch": 120.0,
    },
    "jeff": {
        "label": "Jeff (Masculina - Expressiva)",
        "gender": "Masculina",
        "quality": "Média (Medium)",
        "model_id": "vits-piper-pt_BR-jeff-medium",
        "onnx_file": "pt_BR-jeff-medium.onnx",
        "tar_url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-jeff-medium.tar.bz2",
        "base_pitch": 135.0,
    },
    "edresson": {
        "label": "Edresson (Masculina - Rápida)",
        "gender": "Masculina",
        "quality": "Padrão (Low/Rápida)",
        "model_id": "vits-piper-pt_BR-edresson-low",
        "onnx_file": "pt_BR-edresson-low.onnx",
        "tar_url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-edresson-low.tar.bz2",
        "base_pitch": 140.0,
    },
}

_tts_cache = {}


def is_model_downloaded(voice_key: str) -> bool:
    if voice_key not in VOICES:
        return False
    info = VOICES[voice_key]
    model_path = os.path.join(MODELS_DIR, info["model_id"])
    onnx_path = os.path.join(model_path, info["onnx_file"])
    tokens_path = os.path.join(model_path, "tokens.txt")
    data_dir = os.path.join(model_path, "espeak-ng-data")
    return os.path.exists(onnx_path) and os.path.exists(tokens_path) and os.path.exists(data_dir)


def download_model(voice_key: str, progress_callback=None) -> str:
    info = VOICES[voice_key]
    target_dir = os.path.join(MODELS_DIR, info["model_id"])
    if is_model_downloaded(voice_key):
        return target_dir

    url = info["tar_url"]
    tar_path = os.path.join(MODELS_DIR, f"{info['model_id']}.tar.bz2")

    def report_hook(block_num, block_size, total_size):
        if progress_callback and total_size > 0:
            downloaded = block_num * block_size
            pct = min(1.0, downloaded / total_size)
            progress_callback(pct, f"Baixando modelo {info['label']} ({pct * 100:.0f}%)...")

    urllib.request.urlretrieve(url, tar_path, reporthook=report_hook)

    if progress_callback:
        progress_callback(0.99, "Extraindo modelo...")

    with tarfile.open(tar_path, "r:bz2") as tar:
        tar.extractall(path=MODELS_DIR)

    if os.path.exists(tar_path):
        os.remove(tar_path)

    if progress_callback:
        progress_callback(1.0, "Modelo pronto para uso!")

    return target_dir


def get_tts_engine(voice_key: str, num_threads: int = 4):
    info = VOICES[voice_key]
    cache_key = f"{info['model_id']}_{num_threads}"
    if cache_key in _tts_cache:
        return _tts_cache[cache_key]

    ensure_model_ready(voice_key)
    model_dir = os.path.join(MODELS_DIR, info["model_id"])

    vits_config = sherpa_onnx.OfflineTtsVitsModelConfig(
        model=os.path.join(model_dir, info["onnx_file"]),
        tokens=os.path.join(model_dir, "tokens.txt"),
        data_dir=os.path.join(model_dir, "espeak-ng-data"),
        noise_scale=0.667,
        noise_scale_w=0.8,
        length_scale=1.0,
    )
    tts_config = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(vits=vits_config, num_threads=num_threads),
        max_num_sentences=2,
        silence_scale=0.25,
    )
    tts = sherpa_onnx.OfflineTts(tts_config)
    _tts_cache[cache_key] = tts
    return tts


def ensure_model_ready(voice_key: str, progress_callback=None):
    if not is_model_downloaded(voice_key):
        download_model(voice_key, progress_callback=progress_callback)


# -------------------------------------------------------------
# Acoustic Analysis & Universal Audio Decoding
# -------------------------------------------------------------

def decode_audio_to_wav(audio_bytes: bytes, output_path: str, target_sr: int = 22050, filename: str = "audio.wav") -> tuple:
    """Decodes any audio file format (MP3, AAC, M4A, WAV, OGG, FLAC) to normalized mono WAV using native FFmpeg or SoundFile."""
    ext = os.path.splitext(filename)[1].lower() if filename else ".wav"
    if not ext:
        ext = ".wav"

    try:
        # Try direct read with SoundFile (for WAV, FLAC, OGG)
        audio_data, orig_sr = sf.read(io.BytesIO(audio_bytes), dtype='float32')
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        if orig_sr != target_sr:
            num_samples = int(len(audio_data) * target_sr / orig_sr)
            audio_data = signal.resample(audio_data, num_samples).astype(np.float32)
    except Exception:
        # Fallback to FFmpeg subprocess (installed in Linux Docker container and Windows system)
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_in:
            tmp_in.write(audio_bytes)
            tmp_in_path = tmp_in.name

        try:
            cmd = [
                "ffmpeg", "-y", "-i", tmp_in_path,
                "-vn", "-ac", "1", "-ar", str(target_sr),
                "-f", "wav", output_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            audio_data, _ = sf.read(output_path, dtype='float32')
        finally:
            if os.path.exists(tmp_in_path):
                try:
                    os.remove(tmp_in_path)
                except Exception:
                    pass

    if len(audio_data) == 0:
        raise ValueError("O arquivo de áudio decodificado está vazio.")

    # Normalize volume
    peak = np.max(np.abs(audio_data))
    if peak > 0:
        audio_data = (audio_data / peak) * 0.95

    sf.write(output_path, audio_data, target_sr)
    duration = len(audio_data) / target_sr
    return audio_data, target_sr, duration


def estimate_pitch(audio: np.ndarray, sr: int) -> float:
    """Estimates the median fundamental pitch (F0) in Hz from audio."""
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    audio = audio.flatten()
    if len(audio) < sr // 4:
        return 180.0

    # Pick an active middle segment
    n = len(audio)
    chunk = audio[n // 4 : 3 * n // 4]
    if len(chunk) < sr // 4:
        chunk = audio

    # Autocorrelation
    corr = np.correlate(chunk, chunk, mode="full")
    corr = corr[len(corr) // 2 :]
    d = np.diff(corr)
    start_idx = np.where(d > 0)[0]
    if len(start_idx) == 0:
        return 180.0

    start = start_idx[0]
    peak = np.argmax(corr[start:]) + start
    if peak == 0:
        return 180.0

    pitch = sr / peak
    if 65.0 <= pitch <= 450.0:
        return float(pitch)
    return 180.0


def pitch_shift_ffmpeg(wav_path: str, semitones: float, target_sr: int = 22050, extra_filter: str = ""):
    """Pitch-shifts and shapes acoustic profile of a WAV file in-place using FFmpeg."""
    if abs(semitones) < 0.15 and not extra_filter:
        return
    
    filters = []
    if abs(semitones) >= 0.15:
        factor = 2.0 ** (semitones / 12.0)
        tempo = 1.0 / factor

        tempo_filters = []
        curr_tempo = tempo
        while curr_tempo < 0.5:
            tempo_filters.append("atempo=0.5")
            curr_tempo /= 0.5
        while curr_tempo > 2.0:
            tempo_filters.append("atempo=2.0")
            curr_tempo /= 2.0
        tempo_filters.append(f"atempo={curr_tempo:.4f}")
        tempo_str = ",".join(tempo_filters)

        new_rate = int(round(target_sr * factor))
        filters.append(f"asetrate={new_rate},{tempo_str},aresample={target_sr}")
    
    if extra_filter:
        filters.append(extra_filter)

    af_filter = ",".join(filters)

    tmp_out = wav_path + ".tmp.wav"
    cmd = [
        "ffmpeg", "-y", "-i", wav_path,
        "-af", af_filter,
        "-ar", str(target_sr),
        tmp_out
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(tmp_out):
            os.replace(tmp_out, wav_path)
    except Exception as e:
        if os.path.exists(tmp_out):
            try:
                os.remove(tmp_out)
            except Exception:
                pass
        print(f"[FFmpeg pitch shift error] {e}")


def load_custom_voices_metadata() -> dict:
    if os.path.exists(CUSTOM_VOICES_META):
        try:
            with open(CUSTOM_VOICES_META, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_custom_voices_metadata(meta: dict):
    with open(CUSTOM_VOICES_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def add_custom_voice(name: str, gender: str, audio_bytes: bytes, filename: str) -> dict:
    """Decodes, standardizes to WAV, extracts acoustic profile and saves custom voice."""
    voice_id = f"custom_{int(time.time() * 1000)}"
    sample_filename = f"{voice_id}.wav"
    sample_path = os.path.join(CUSTOM_VOICES_DIR, sample_filename)

    # Universal audio decode using PyAV / FFmpeg with original extension
    audio_data, sr, duration = decode_audio_to_wav(audio_bytes, sample_path, target_sr=22050, filename=filename)
    pitch = estimate_pitch(audio_data, sr)

    base_voice = "dii" if gender.lower() == "feminina" else "faber"
    base_pitch = VOICES[base_voice]["base_pitch"]

    semitones = float(12.0 * np.log2(max(pitch, 60.0) / base_pitch))
    semitones = float(np.clip(semitones, -7.0, 7.0))

    meta = load_custom_voices_metadata()
    voice_entry = {
        "id": voice_id,
        "name": name,
        "gender": gender,
        "sample_filename": sample_filename,
        "sample_url": f"/custom-voices/sample/{sample_filename}",
        "duration": round(duration, 2),
        "pitch_hz": round(pitch, 1),
        "semitones_shift": round(semitones, 2),
        "base_voice": base_voice,
        "created_at": time.time(),
    }
    meta[voice_id] = voice_entry
    save_custom_voices_metadata(meta)
    return voice_entry


def get_custom_voices() -> list:
    meta = load_custom_voices_metadata()
    voices = list(meta.values())
    voices.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    return voices


def delete_custom_voice(voice_id: str) -> bool:
    meta = load_custom_voices_metadata()
    if voice_id in meta:
        entry = meta.pop(voice_id)
        sample_path = os.path.join(CUSTOM_VOICES_DIR, entry.get("sample_filename", ""))
        if os.path.exists(sample_path):
            try:
                os.remove(sample_path)
            except Exception:
                pass
        save_custom_voices_metadata(meta)
        return True
    return False


# -------------------------------------------------------------
# Synthesis Engine
# -------------------------------------------------------------

def synthesize_text(
    text: str,
    voice_key: str = "dii",
    speed: float = 1.0,
    num_threads: int = 4,
    progress_callback=None,
) -> dict:
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("O texto fornecido está vazio.")

    start_time = time.time()

    if voice_key.startswith("custom_"):
        custom_meta = load_custom_voices_metadata()
        if voice_key not in custom_meta:
            raise ValueError("Voz personalizada não encontrada.")
        cv = custom_meta[voice_key]
        base_key = cv.get("base_voice", "dii")
        ensure_model_ready(base_key, progress_callback=progress_callback)
        tts = get_tts_engine(base_key, num_threads=num_threads)
        audio = tts.generate(clean_text, sid=0, speed=speed)
        samples = np.array(audio.samples, dtype=np.float32)
        sample_rate = audio.sample_rate

        timestamp = int(time.time() * 1000)
        filename = f"audio_{voice_key}_{timestamp}.wav"
        output_path = os.path.join(OUTPUTS_DIR, filename)
        sf.write(output_path, samples, sample_rate)

        # Apply acoustic profile shift (pitch matching) using FFmpeg
        semitones = cv.get("semitones_shift", 0.0)
        if abs(semitones) > 0.15:
            pitch_shift_ffmpeg(output_path, semitones, sample_rate)

        info = sf.info(output_path)
        duration = info.duration
        with open(output_path, "rb") as f:
            audio_bytes = f.read()
    else:
        ensure_model_ready(voice_key, progress_callback=progress_callback)
        tts = get_tts_engine(voice_key, num_threads=num_threads)
        effective_speed = speed * VOICES.get(voice_key, {}).get("default_speed", 1.0)
        audio = tts.generate(clean_text, sid=0, speed=effective_speed)
        samples = np.array(audio.samples, dtype=np.float32)
        sample_rate = audio.sample_rate

        duration = len(samples) / sample_rate
        timestamp = int(time.time() * 1000)
        filename = f"audio_{voice_key}_{timestamp}.wav"
        output_path = os.path.join(OUTPUTS_DIR, filename)
        sf.write(output_path, samples, sample_rate)

        # Apply calibrated acoustic pitch shift and DSP equalization if defined for the voice
        pitch_shift = VOICES.get(voice_key, {}).get("pitch_shift", 0.0)
        dsp_filter = VOICES.get(voice_key, {}).get("dsp_filter", "")
        if abs(pitch_shift) > 0.05 or dsp_filter:
            pitch_shift_ffmpeg(output_path, pitch_shift, sample_rate, extra_filter=dsp_filter)
            try:
                info = sf.info(output_path)
                duration = info.duration
            except Exception:
                pass

        with open(output_path, "rb") as f:
            audio_bytes = f.read()

    elapsed = time.time() - start_time

    return {
        "file_path": output_path,
        "filename": filename,
        "audio_bytes": audio_bytes,
        "duration_seconds": duration,
        "sample_rate": sample_rate,
        "elapsed_seconds": elapsed,
        "rtf": elapsed / max(duration, 0.001),
    }
