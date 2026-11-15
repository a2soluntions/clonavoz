import datetime
import hashlib
import json
import os
import glob
import shutil
import subprocess
import threading
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header, Depends, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tts_engine

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN", "").strip()
BASE_URL = os.getenv("BASE_URL", "https://api.clonavoz.com.br").strip()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEMINI_SERVICE_SCRIPT = os.path.join(BASE_DIR, "gemini_tts_service.mjs")
PUBLIC_VOICE_SAMPLES_DIR = os.path.join(BASE_DIR, "public", "voice-samples")
os.makedirs(PUBLIC_VOICE_SAMPLES_DIR, exist_ok=True)

# Catálogo oficial das 30 vozes do Google Gemini TTS
GEMINI_TTS_VOICES = [
    {"key": "Kore", "label": "Kore", "gender": "Feminina", "timbre": "Firme & Comercial", "default_style": "Voz firme, natural, clara e persuasiva", "fallback_voice": "su"},
    {"key": "Charon", "label": "Charon", "gender": "Masculina", "timbre": "Grave & Narrativo", "default_style": "Voz grave, informativa, segura e envolvente", "fallback_voice": "miro"},
    {"key": "Puck", "label": "Puck", "gender": "Masculina", "timbre": "Jovem & Dinâmico", "default_style": "Voz animada, ágil e expressiva", "fallback_voice": "jeff"},
    {"key": "Fenrir", "label": "Fenrir", "gender": "Masculina", "timbre": "Expressivo & Quente", "default_style": "Voz vibrante, intensa e empolgante", "fallback_voice": "cadu"},
    {"key": "Zephyr", "label": "Zephyr", "gender": "Feminina", "timbre": "Sereno & Claro", "default_style": "Voz brilhante, leve e articulada", "fallback_voice": "sarah"},
    {"key": "Aoede", "label": "Aoede", "gender": "Feminina", "timbre": "Suave & Acolhedor", "default_style": "Voz fluida, leve e natural", "fallback_voice": "eduarda"},
    {"key": "Leda", "label": "Leda", "gender": "Feminina", "timbre": "Jovem & Dinâmico", "default_style": "Voz jovem, doce e espontânea", "fallback_voice": "duda"},
    {"key": "Orus", "label": "Orus", "gender": "Masculina", "timbre": "Firme & Comercial", "default_style": "Voz firme, direta e autoritativa", "fallback_voice": "faber"},
    {"key": "Callirrhoe", "label": "Callirrhoe", "gender": "Feminina", "timbre": "Suave & Acolhedor", "default_style": "Voz tranquila, amigável e descontraída", "fallback_voice": "dii"},
    {"key": "Autonoe", "label": "Autonoe", "gender": "Feminina", "timbre": "Sereno & Claro", "default_style": "Voz luminosa, otimista e nítida", "fallback_voice": "sarah"},
    {"key": "Enceladus", "label": "Enceladus", "gender": "Masculina", "timbre": "Suave & Acolhedor", "default_style": "Voz suave, íntima e relaxada", "fallback_voice": "edresson"},
    {"key": "Iapetus", "label": "Iapetus", "gender": "Masculina", "timbre": "Sereno & Claro", "default_style": "Voz limpa, clara e equilibrada", "fallback_voice": "edresson"},
    {"key": "Umbriel", "label": "Umbriel", "gender": "Masculina", "timbre": "Suave & Acolhedor", "default_style": "Voz relaxada, calorosa e acessível", "fallback_voice": "cadu"},
    {"key": "Algieba", "label": "Algieba", "gender": "Masculina", "timbre": "Suave & Acolhedor", "default_style": "Voz macia, polida e agradável", "fallback_voice": "jeff"},
    {"key": "Despina", "label": "Despina", "gender": "Feminina", "timbre": "Suave & Acolhedor", "default_style": "Voz suave, elegante e fluida", "fallback_voice": "dii"},
    {"key": "Erinome", "label": "Erinome", "gender": "Feminina", "timbre": "Sereno & Claro", "default_style": "Voz cristalina, didática e bem articulada", "fallback_voice": "eduarda"},
    {"key": "Algenib", "label": "Algenib", "gender": "Masculina", "timbre": "Grave & Narrativo", "default_style": "Voz texturizada, grave e marcante", "fallback_voice": "miro"},
    {"key": "Rasalgethi", "label": "Rasalgethi", "gender": "Masculina", "timbre": "Sereno & Claro", "default_style": "Voz informativa, jornalística e objetiva", "fallback_voice": "jeff"},
    {"key": "Laomedeia", "label": "Laomedeia", "gender": "Feminina", "timbre": "Jovem & Dinâmico", "default_style": "Voz alegre, viva e carismática", "fallback_voice": "duda"},
    {"key": "Achernar", "label": "Achernar", "gender": "Feminina", "timbre": "Suave & Acolhedor", "default_style": "Voz gentil, macia e acolhedora", "fallback_voice": "dii"},
    {"key": "Alnilam", "label": "Alnilam", "gender": "Masculina", "timbre": "Firme & Comercial", "default_style": "Voz forte, decidida e confiável", "fallback_voice": "faber"},
    {"key": "Schedar", "label": "Schedar", "gender": "Masculina", "timbre": "Sereno & Claro", "default_style": "Voz equilibrada e realista", "fallback_voice": "edresson"},
    {"key": "Gacrux", "label": "Gacrux", "gender": "Feminina", "timbre": "Grave & Narrativo", "default_style": "Voz madura, experiente e envolvente", "fallback_voice": "dii"},
    {"key": "Pulcherrima", "label": "Pulcherrima", "gender": "Feminina", "timbre": "Expressivo & Quente", "default_style": "Voz emotiva, expressiva e cativante", "fallback_voice": "thalita"},
    {"key": "Achird", "label": "Achird", "gender": "Masculina", "timbre": "Suave & Acolhedor", "default_style": "Voz amigável, próxima e simpática", "fallback_voice": "jeff"},
    {"key": "Zubenelgenubi", "label": "Zubenelgenubi", "gender": "Masculina", "timbre": "Jovem & Dinâmico", "default_style": "Voz casual, cotidiana e espontânea", "fallback_voice": "cadu"},
    {"key": "Vindemiatrix", "label": "Vindemiatrix", "gender": "Feminina", "timbre": "Suave & Acolhedor", "default_style": "Voz meiga, delicada e calma", "fallback_voice": "dii"},
    {"key": "Sadachbia", "label": "Sadachbia", "gender": "Feminina", "timbre": "Expressivo & Quente", "default_style": "Voz vivaz, enérgica e expressiva", "fallback_voice": "duda"},
    {"key": "Sadaltager", "label": "Sadaltager", "gender": "Masculina", "timbre": "Grave & Narrativo", "default_style": "Voz sábia, explicativa e segura", "fallback_voice": "miro"},
    {"key": "Sulafat", "label": "Sulafat", "gender": "Feminina", "timbre": "Expressivo & Quente", "default_style": "Voz calorosa, envolvente e humana", "fallback_voice": "sarah"},
]

GEMINI_VOICE_MAP = {v["key"].lower(): v for v in GEMINI_TTS_VOICES}
_gemini_tts_mem_cache: Dict[str, Dict[str, Any]] = {}

# Catálogo de Trilhas Sonoras de Fundo (BGM)
BGM_TRACKS = {
    "inspire": {"label": "Inspirador / VSL", "file": "bgm_inspire.mp3", "description": "Piano e ambiência acolhedora para vídeos de alta conversão"},
    "corporate": {"label": "Corporativo / Tech", "file": "bgm_corporate.mp3", "description": "Batida acústica limpa para notícias e empresas"},
    "calm": {"label": "Calmo / Reflexivo", "file": "bgm_calm.mp3", "description": "Pad suave e relaxante para meditação e podcasts"},
    "cinematic": {"label": "Cinemático / Dark", "file": "bgm_cinematic.mp3", "description": "Harmonia dramática com suspense para canais Dark"}
}

# Vozes VIP da ElevenLabs mapeadas
ELEVENLABS_VOICES = {
    # Femininas
    "el_su": {"voice_id": "qE4bxNbWYcb8hs72HJEO", "label": "Su", "gender": "Feminina", "quality": "ElevenLabs Multilingual v2", "sample_url": "/demos/su_sample.mp3", "fallback_voice": "dii", "fallback_semitones": -2.35},
    "el_bella": {"voice_id": "hpp4J3VqNfWAUOO0d1Us", "label": "Bella", "gender": "Feminina", "quality": "ElevenLabs Multilingual v2", "fallback_voice": "eduarda", "fallback_semitones": 0.0},
    "el_alice": {"voice_id": "Xb7hH8MSUJpSbSDYk0k2", "label": "Alice", "gender": "Feminina", "quality": "ElevenLabs Multilingual v2", "fallback_voice": "sarah", "fallback_semitones": 0.0},
    "el_jessica": {"voice_id": "cgSgspJ2msm6clMCkdW9", "label": "Jessica", "gender": "Feminina", "quality": "ElevenLabs Multilingual v2", "fallback_voice": "duda", "fallback_semitones": 0.0},
    "el_laura": {"voice_id": "FGY2WhTYpPnrIDTdsKH5", "label": "Laura", "gender": "Feminina", "quality": "ElevenLabs Multilingual v2", "fallback_voice": "dii", "fallback_semitones": 0.5},
    "el_rachel": {"voice_id": "pFZP5JQG7iQjIQuC4Bku", "label": "Rachel", "gender": "Feminina", "quality": "ElevenLabs Multilingual v2", "fallback_voice": "dii", "fallback_semitones": -0.6},
    # Masculinas
    "el_adam": {"voice_id": "pNInz6obpgDQGcFmaJgB", "label": "Adam", "gender": "Masculina", "quality": "ElevenLabs Multilingual v2", "fallback_voice": "miro", "fallback_semitones": -0.8},
    "el_brian": {"voice_id": "nPczCjzI2devNBz1zQrb", "label": "Brian", "gender": "Masculina", "quality": "ElevenLabs Multilingual v2", "fallback_voice": "faber", "fallback_semitones": -1.2},
    "el_daniel": {"voice_id": "onwK4e9ZLuTAKqWW03F9", "label": "Daniel", "gender": "Masculina", "quality": "ElevenLabs Multilingual v2", "fallback_voice": "jeff", "fallback_semitones": 0.0},
    "el_liam": {"voice_id": "TX3LPaxmHKxFdv7VOQHJ", "label": "Liam", "gender": "Masculina", "quality": "ElevenLabs Multilingual v2", "fallback_voice": "cadu", "fallback_semitones": 0.5},
    "el_george": {"voice_id": "JBFqnCBsd6RMkjVDRZzb", "label": "George", "gender": "Masculina", "quality": "ElevenLabs Multilingual v2", "fallback_voice": "faber", "fallback_semitones": -1.0},
    "el_charlie": {"voice_id": "IKne3meq5aSn9XLyUdCD", "label": "Charlie", "gender": "Masculina", "quality": "ElevenLabs Multilingual v2", "fallback_voice": "cadu", "fallback_semitones": 0.6},
    "el_chris": {"voice_id": "iP95p4xoKVk53GoZ742B", "label": "Chris", "gender": "Masculina", "quality": "ElevenLabs Multilingual v2", "fallback_voice": "jeff", "fallback_semitones": -0.4},
}

def synthesize_elevenlabs(voice_id: str, text: str, output_path: str):
    """Gera áudio de ultra-fidelidade usando a API oficial da ElevenLabs com suporte a Português."""
    import urllib.request
    import json
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        audio_content = resp.read()
    with open(output_path, "wb") as f:
        f.write(audio_content)

supabase_admin = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        from supabase import create_client
        supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print(f"[Supabase] Conectado com sucesso ao projeto: {SUPABASE_URL}")
    except Exception as e:
        print(f"[Supabase] Erro ao conectar ao cliente admin: {e}")

app = FastAPI(title="Clonavoz AI - Neural Speech Studio")

# Habilita CORS para conexão com Vercel e produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(BASE_DIR, "static")
OUTPUTS_DIR = tts_engine.OUTPUTS_DIR
GEMINI_CACHE_DIR = os.path.join(OUTPUTS_DIR, "cache")
os.makedirs(GEMINI_CACHE_DIR, exist_ok=True)
CUSTOM_VOICES_DIR = tts_engine.CUSTOM_VOICES_DIR

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# /outputs/{filename} e /outputs/cache/{filename} são servidos dinamicamente para garantir conversão WAV/MP3 on-the-fly

bgm_dir = os.path.join(STATIC_DIR, "bgm")
if os.path.exists(bgm_dir):
    app.mount("/bgm", StaticFiles(directory=bgm_dir), name="bgm")

demos_dir = os.path.join(STATIC_DIR, "demos")
if os.path.exists(demos_dir):
    app.mount("/demos", StaticFiles(directory=demos_dir), name="demos")

if os.path.exists(PUBLIC_VOICE_SAMPLES_DIR):
    app.mount("/voice-samples", StaticFiles(directory=PUBLIC_VOICE_SAMPLES_DIR), name="voice_samples")

@app.get("/favicon.ico")
def get_favicon():
    fav = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(fav):
        return FileResponse(fav, media_type="image/x-icon")
    raise HTTPException(status_code=404)


# -------------------------------------------------------------
# Analytics & Visit Tracker (Armazenado com persistência em OUTPUTS_DIR/analytics.json)
# Fuso horário padronizado no Horário Oficial de Brasília (UTC-3)
# -------------------------------------------------------------
ANALYTICS_FILE = os.path.join(OUTPUTS_DIR, "analytics.json")

def get_brasil_now():
    """Retorna datetime no fuso horário oficial de Brasília (UTC-3)."""
    tz_br = datetime.timezone(datetime.timedelta(hours=-3))
    return datetime.datetime.now(tz_br)

def get_analytics_series(daily_history: dict, br_now: datetime.datetime, sales_by_day: dict = None) -> dict:
    """Gera séries temporais agregadas para os gráficos de Dia, Mês e Ano com visitas, únicos e vendas (R$)."""
    if sales_by_day is None:
        sales_by_day = {}

    month_names_pt = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    # 1. Dias: últimos 7 dias
    days = []
    for i in range(6, -1, -1):
        d = br_now.date() - datetime.timedelta(days=i)
        d_str = d.isoformat()
        entry = daily_history.get(d_str, {})
        days.append({
            "date": d_str,
            "label": d.strftime("%d/%m"),
            "views": entry.get("views", 0),
            "uniques": entry.get("uniques", 0),
            "revenue": round(sales_by_day.get(d_str, 0.0), 2)
        })

    # 2. Meses: últimos 6 meses
    months_map = {}
    for i in range(5, -1, -1):
        y = br_now.year
        m = br_now.month - i
        while m <= 0:
            m += 12
            y -= 1
        m_key = f"{y:04d}-{m:02d}"
        months_map[m_key] = {
            "month": m_key,
            "label": f"{month_names_pt[m]}/{str(y)[2:]}",
            "views": 0,
            "uniques": 0,
            "revenue": 0.0
        }

    for d_str, entry in daily_history.items():
        m_key = d_str[:7]
        if m_key in months_map:
            months_map[m_key]["views"] += entry.get("views", 0)
            months_map[m_key]["uniques"] += entry.get("uniques", 0)

    for d_str, rev in sales_by_day.items():
        m_key = d_str[:7]
        if m_key in months_map:
            months_map[m_key]["revenue"] = round(months_map[m_key]["revenue"] + rev, 2)

    months = list(months_map.values())

    # 3. Anos: últimos 3 anos
    years_map = {}
    for y in range(br_now.year - 2, br_now.year + 1):
        y_key = str(y)
        years_map[y_key] = {
            "year": y_key,
            "label": y_key,
            "views": 0,
            "uniques": 0,
            "revenue": 0.0
        }

    for d_str, entry in daily_history.items():
        y_key = d_str[:4]
        if y_key in years_map:
            years_map[y_key]["views"] += entry.get("views", 0)
            years_map[y_key]["uniques"] += entry.get("uniques", 0)

    for d_str, rev in sales_by_day.items():
        y_key = d_str[:4]
        if y_key in years_map:
            years_map[y_key]["revenue"] = round(years_map[y_key]["revenue"] + rev, 2)

    years = list(years_map.values())

    return {
        "days": days,
        "months": months,
        "years": years
    }

def load_analytics() -> dict:
    if os.path.exists(ANALYTICS_FILE):
        try:
            with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                changed = False
                lv = data.get("last_visit", "")
                if "27/10/2026 00:" in lv:
                    data["last_visit"] = lv.replace("27/10/2026 00:", "26/10/2026 21:")
                    changed = True
                
                br_today = get_brasil_now().date().isoformat()
                if data.get("today") == "2026-10-27" and br_today == "2026-10-26":
                    data["today"] = "2026-10-26"
                    if data.get("today_views", 0) == 0:
                        data["today_views"] = data.get("total_views", 0)
                        data["today_uniques"] = data.get("unique_visitors", [])
                    changed = True

                # Garante que daily_history exista e contenha as visitas atuais
                if "daily_history" not in data:
                    data["daily_history"] = {}
                    changed = True

                if not data["daily_history"] and data.get("total_views", 0) > 0:
                    data["daily_history"][br_today] = {
                        "views": data.get("total_views", 0),
                        "uniques": len(data.get("unique_visitors", []))
                    }
                    changed = True

                if changed:
                    try:
                        with open(ANALYTICS_FILE, "w", encoding="utf-8") as wf:
                            json.dump(data, wf, ensure_ascii=False, indent=2)
                    except Exception:
                        pass

                return data
        except Exception:
            pass

    br_today = get_brasil_now().date().isoformat()
    return {
        "total_views": 0,
        "unique_visitors": [],
        "today": br_today,
        "today_views": 0,
        "today_uniques": [],
        "last_visit": "Nenhuma visita registrada ainda",
        "daily_history": {
            br_today: {"views": 0, "uniques": 0}
        }
    }

def save_analytics(data: dict):
    try:
        with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Analytics Save Error] {e}")

@app.post("/api/track-visit")
async def track_visit(request: Request):
    try:
        # 1. Ignora acessos do dono/administrador
        try:
            body = await request.json()
        except Exception:
            body = {}

        if body.get("is_owner") or request.headers.get("x-clonavoz-owner") == "true":
            return {"success": True, "ignored": "owner_flag"}

        auth_header = request.headers.get("authorization")
        if auth_header and supabase_admin:
            u = get_current_user_from_header(auth_header)
            if u and getattr(u, "email", "") == "araujoexcel@gmail.com":
                return {"success": True, "ignored": "owner_account"}

        forwarded = request.headers.get("x-forwarded-for")
        ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")
        # Anonimiza o IP com SHA-256 (conformidade total com LGPD)
        ip_hash = hashlib.sha256(f"clonavoz_salt_{ip}".encode()).hexdigest()[:16]

        br_now = get_brasil_now()
        today_str = br_now.date().isoformat()
        data = load_analytics()

        # Reseta contador diário na virada do dia (Horário de Brasília)
        if data.get("today") != today_str:
            data["today"] = today_str
            data["today_views"] = 0
            data["today_uniques"] = []

        data["total_views"] = data.get("total_views", 0) + 1
        data["today_views"] = data.get("today_views", 0) + 1

        uniques = set(data.get("unique_visitors", []))
        uniques.add(ip_hash)
        data["unique_visitors"] = list(uniques)[-3000:]

        today_uniques = set(data.get("today_uniques", []))
        today_uniques.add(ip_hash)
        data["today_uniques"] = list(today_uniques)[-1000:]
        data["last_visit"] = br_now.strftime("%d/%m/%Y %H:%M:%S")

        # Atualiza histórico diário para os gráficos
        daily_hist = data.setdefault("daily_history", {})
        if today_str not in daily_hist:
            daily_hist[today_str] = {"views": 0, "uniques": 0, "unique_ips": []}
        
        day_entry = daily_hist[today_str]
        day_entry["views"] = day_entry.get("views", 0) + 1
        
        day_ips = set(day_entry.get("unique_ips", []))
        day_ips.add(ip_hash)
        day_entry["unique_ips"] = list(day_ips)[-1000:]
        day_entry["uniques"] = len(day_entry["unique_ips"])

        save_analytics(data)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/stats")
def get_stats():
    data = load_analytics()
    br_now = get_brasil_now()
    today_str = br_now.date().isoformat()
    today_views = data.get("today_views", 0) if data.get("today") == today_str else 0
    today_uniques = len(data.get("today_uniques", [])) if data.get("today") == today_str else 0

    daily_hist = data.get("daily_history", {})
    if today_str not in daily_hist and today_views > 0:
        daily_hist[today_str] = {"views": today_views, "uniques": today_uniques}

    # Consulta vendas reais aprovadas no Supabase (pix_transactions)
    sales_total_brl = 0.0
    sales_count = 0
    sales_today_brl = 0.0
    sales_today_count = 0
    sales_by_day = {}

    if supabase_admin:
        try:
            tx_res = supabase_admin.table("pix_transactions").select("amount_brl,status,paid_at,created_at").eq("status", "paid").execute()
            if tx_res.data:
                tz_br = datetime.timezone(datetime.timedelta(hours=-3))
                for tx in tx_res.data:
                    amt = float(tx.get("amount_brl") or 0.0)
                    sales_total_brl += amt
                    sales_count += 1

                    paid_ts = tx.get("paid_at") or tx.get("created_at")
                    if paid_ts:
                        try:
                            dt = datetime.datetime.fromisoformat(paid_ts.replace("Z", "+00:00")).astimezone(tz_br)
                            d_key = dt.date().isoformat()
                            sales_by_day[d_key] = sales_by_day.get(d_key, 0.0) + amt
                            if d_key == today_str:
                                sales_today_brl += amt
                                sales_today_count += 1
                        except Exception:
                            pass
        except Exception as ex:
            print(f"[Stats Sales Query Warning] {ex}")

    series = get_analytics_series(daily_hist, br_now, sales_by_day)
    unique_total = len(data.get("unique_visitors", []))
    conversion_rate = round((sales_count / max(unique_total, 1)) * 100, 1) if unique_total > 0 else 0.0

    return {
        "total_views": data.get("total_views", 0),
        "unique_visitors": unique_total,
        "today_views": today_views,
        "today_uniques": today_uniques,
        "sales_total_brl": round(sales_total_brl, 2),
        "sales_count": sales_count,
        "sales_today_brl": round(sales_today_brl, 2),
        "sales_today_count": sales_today_count,
        "conversion_rate": conversion_rate,
        "last_visit": data.get("last_visit", "Nenhuma visita registrada ainda"),
        "date": today_str,
        "series": series
    }

@app.post("/api/reset-stats")
def reset_stats():
    """Zera os contadores analíticos para iniciar uma contagem limpa de visitas reais."""
    br_now = get_brasil_now()
    br_today = br_now.date().isoformat()
    data = {
        "total_views": 0,
        "unique_visitors": [],
        "today": br_today,
        "today_views": 0,
        "today_uniques": [],
        "last_visit": "Nenhuma visita registrada ainda",
        "daily_history": {
            br_today: {"views": 0, "uniques": 0, "unique_ips": []}
        }
    }
    save_analytics(data)
    return {"success": True, "message": "Contadores zerados com sucesso."}


def get_current_user_from_header(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Valida o token JWT do Supabase recebido no header Authorization."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1].strip()
    if not token or not supabase_admin:
        return None
    try:
        user_res = supabase_admin.auth.get_user(token)
        if user_res and user_res.user:
            return user_res.user
    except Exception as e:
        pass
    return None


def get_or_create_profile(user) -> dict:
    """Busca ou cria o registro do perfil com 1 crédito grátis se ainda não existir."""
    if not supabase_admin:
        return {"id": user.id, "credits": 999, "full_name": "Local User"}
    
    # 1. Tenta buscar perfil existente com retry resiliente
    for attempt in range(2):
        try:
            res = supabase_admin.table("profiles").select("*").eq("id", user.id).limit(1).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            break
        except Exception as e:
            print(f"[Profile Query Attempt {attempt+1} Error] {e}")
            import time
            time.sleep(0.3)

    # 2. Cria o profile caso não exista
    try:
        full_name = "Criador"
        if hasattr(user, "user_metadata") and user.user_metadata:
            full_name = user.user_metadata.get("full_name") or (user.email.split("@")[0] if user.email else "Criador")
        elif getattr(user, "email", None):
            full_name = user.email.split("@")[0]
            
        new_profile = {
            "id": user.id,
            "email": getattr(user, "email", ""),
            "full_name": full_name,
            "credits": 1
        }
        ins = supabase_admin.table("profiles").insert(new_profile).execute()
        if ins.data:
            return ins.data[0]
    except Exception as e:
        print(f"[Profile Insert Warning/Duplicate] {e}")
        # Se falhou por conflito/já existente, busca novamente o registro original
        try:
            retry_res = supabase_admin.table("profiles").select("*").eq("id", user.id).limit(1).execute()
            if retry_res.data and len(retry_res.data) > 0:
                return retry_res.data[0]
        except Exception:
            pass

    return {"id": user.id, "email": getattr(user, "email", ""), "full_name": "Criador", "credits": 1}


class EnhanceTextRequest(BaseModel):
    text: str


@app.post("/api/enhance-text")
def enhance_text_endpoint(req: EnhanceTextRequest):
    import text_normalizer
    if not req.text or not req.text.strip():
        return {"original": "", "enhanced": "", "changes": 0, "analysis": {}}
    return text_normalizer.enhance_text_for_display(req.text)


@app.post("/api/analyze-text")
def analyze_text_endpoint(req: EnhanceTextRequest):
    import text_normalizer
    if not req.text or not req.text.strip():
        return {
            "has_issues": False,
            "issues_count": 0,
            "issues_details": [],
            "original_text": "",
            "suggested_text": "",
            "risk_explanation": "",
            "disclaimer": ""
        }
    return text_normalizer.analyze_text_quality(req.text)


class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "Kore"
    speed: float = 1.0
    threads: int = 4
    bgm: Optional[str] = "none"
    bgm_volume: Optional[float] = 0.15
    save_history: Optional[bool] = True
    mode: Optional[str] = "single"
    model: Optional[str] = None
    style: Optional[str] = "Voz natural, clara e expressiva"
    dialogue: Optional[List[Dict[str, Any]]] = None
    speakers: Optional[List[Dict[str, Any]]] = None


class DownloadVoiceRequest(BaseModel):
    voice: str


@app.get("/api/bgm-tracks")
def get_bgm_tracks():
    """Retorna as trilhas sonoras de fundo disponíveis com preview."""
    tracks = []
    for key, info in BGM_TRACKS.items():
        tracks.append({
            "key": key,
            "label": info["label"],
            "description": info["description"],
            "url": f"/static/bgm/{info['file']}"
        })
    return tracks


@app.get("/")
def get_landing():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/studio")
def get_studio():
    studio_path = os.path.join(STATIC_DIR, "studio.html")
    if os.path.exists(studio_path):
        return FileResponse(studio_path)
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/config")
def get_config():
    """Retorna chaves públicas e status de configuração de autenticação para o frontend."""
    return {
        "supabase_url": SUPABASE_URL,
        "supabase_anon_key": SUPABASE_ANON_KEY,
        "auth_enabled": bool(supabase_admin),
    }


@app.get("/api/me")
def get_me(authorization: Optional[str] = Header(None)):
    """Retorna os dados do perfil do usuário logado (saldo de créditos, nome, etc.)."""
    user = get_current_user_from_header(authorization)
    if not user:
        return {"authenticated": False}
    profile = get_or_create_profile(user)
    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "email": getattr(user, "email", ""),
            "full_name": profile.get("full_name", "Criador"),
            "credits": profile.get("credits", 0),
            "created_at": profile.get("created_at"),
        }
    }


class CreatePixRequest(BaseModel):
    package_id: str = "criador"
    credits: int = 12
    price: str = "27,90"


@app.post("/api/pix/create")
def create_pix_payment(req: CreatePixRequest, authorization: Optional[str] = Header(None)):
    """Cria uma cobrança PIX via Mercado Pago ou simulação para adicionar créditos."""
    user = None
    if supabase_admin:
        user = get_current_user_from_header(authorization)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Você precisa estar conectado na sua conta para recarregar créditos.",
            )

    import time
    import datetime
    import uuid
    import json
    import urllib.request

    raw_price = req.price.replace("R$", "").replace(" ", "").replace(",", ".").strip()
    try:
        amount_num = float(raw_price) if raw_price else 27.90
    except ValueError:
        amount_num = 27.90

    user_email = getattr(user, "email", "cliente@clonavoz.com.br") if user else "cliente@clonavoz.com.br"
    user_name = "Cliente"
    if user and hasattr(user, "user_metadata") and user.user_metadata:
        user_name = user.user_metadata.get("full_name") or user_email.split("@")[0]
    elif user and user_email:
        user_name = user_email.split("@")[0]

    payment_id = None
    qr_code = ""
    qr_code_base64 = ""
    is_simulated = True

    # 1. Tenta criar cobrança real no Mercado Pago se houver token configurado
    if MERCADO_PAGO_ACCESS_TOKEN:
        try:
            mp_url = "https://api.mercadopago.com/v1/payments"
            mp_payload = {
                "transaction_amount": amount_num,
                "description": f"Clonavoz - {req.credits} Creditos ({req.package_id})",
                "payment_method_id": "pix",
                "payer": {
                    "email": user_email,
                    "first_name": user_name
                },
                "notification_url": f"{BASE_URL}/api/pix/webhook"
            }
            req_headers = {
                "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
                "Content-Type": "application/json",
                "X-Idempotency-Key": str(uuid.uuid4())
            }
            req_obj = urllib.request.Request(
                mp_url,
                data=json.dumps(mp_payload).encode("utf-8"),
                headers=req_headers,
                method="POST"
            )
            with urllib.request.urlopen(req_obj, timeout=10) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                payment_id = str(resp_data.get("id"))
                tx_data = resp_data.get("point_of_interaction", {}).get("transaction_data", {})
                qr_code = tx_data.get("qr_code", "")
                qr_code_base64 = tx_data.get("qr_code_base64", "")
                is_simulated = False
        except Exception as mp_err:
            print(f"[Mercado Pago API Warning - Usando Fallback]: {mp_err}")

    # 2. Fallback / Simulação de desenvolvimento se token não configurado ou em teste
    if not payment_id:
        payment_id = f"sim_{int(time.time() * 1000)}"
        qr_code = f"00020126580014br.gov.bcb.pix0136clonavoz-recarga-{payment_id}520400005303986540{len(str(amount_num)):02d}{amount_num:.2f}5802BR5916CLONAVOZ STUDIO6009SAO PAULO62070503***6304"
        is_simulated = True

    # 3. Registra na tabela pix_transactions se Supabase estiver ativo
    if supabase_admin and user:
        try:
            supabase_admin.table("pix_transactions").insert({
                "user_id": user.id,
                "gateway_txid": payment_id,
                "package_id": req.package_id,
                "credits_amount": req.credits,
                "amount_brl": amount_num,
                "status": "pending",
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }).execute()
        except Exception as ex:
            print(f"[PIX Insert Warning] {ex}")

    return {
        "success": True,
        "payment_id": payment_id,
        "qr_code": qr_code,
        "qr_code_base64": qr_code_base64,
        "amount": amount_num,
        "credits": req.credits,
        "package_id": req.package_id,
        "is_simulated": is_simulated,
        "status": "pending"
    }


@app.get("/api/pix/status/{payment_id}")
def check_pix_status(payment_id: str, authorization: Optional[str] = Header(None)):
    """Verifica se o pagamento PIX foi aprovado e credita saldo na conta."""
    user = get_current_user_from_header(authorization) if supabase_admin else None

    # Se for cobrança real no Mercado Pago
    if not payment_id.startswith("sim_") and MERCADO_PAGO_ACCESS_TOKEN:
        try:
            import urllib.request
            import json
            req_obj = urllib.request.Request(
                f"https://api.mercadopago.com/v1/payments/{payment_id}",
                headers={"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
            )
            with urllib.request.urlopen(req_obj, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                mp_status = data.get("status")
                if mp_status == "approved":
                    if supabase_admin:
                        try:
                            tx_res = supabase_admin.table("pix_transactions").select("*").eq("gateway_txid", payment_id).execute()
                            if tx_res.data:
                                tx = tx_res.data[0]
                                if tx.get("status") != "paid":
                                    import datetime
                                    supabase_admin.table("pix_transactions").update({
                                        "status": "paid",
                                        "paid_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                                    }).eq("gateway_txid", payment_id).execute()
                                    
                                    u_id = tx.get("user_id")
                                    prof_res = supabase_admin.table("profiles").select("credits").eq("id", u_id).execute()
                                    current_cred = prof_res.data[0]["credits"] if prof_res.data else 0
                                    new_cred = current_cred + tx.get("credits_amount", 1)
                                    supabase_admin.table("profiles").update({"credits": new_cred}).eq("id", u_id).execute()
                                    return {"status": "approved", "credits": new_cred, "added": tx.get("credits_amount", 1)}
                        except Exception as e:
                            print(f"[PIX Approval Update Error] {e}")
                    return {"status": "approved"}
                return {"status": mp_status or "pending"}
        except Exception as e:
            print(f"[PIX Status Query Error] {e}")

    # Se for em ambiente de teste ou Supabase
    if supabase_admin and user:
        try:
            tx_res = supabase_admin.table("pix_transactions").select("*").eq("gateway_txid", payment_id).execute()
            if tx_res.data:
                tx = tx_res.data[0]
                if tx.get("status") == "paid":
                    profile = get_or_create_profile(user)
                    return {"status": "approved", "credits": profile.get("credits", 0), "added": tx.get("credits_amount", 1)}
        except Exception:
            pass

    return {"status": "pending"}


@app.post("/api/pix/simulate-approve/{payment_id}")
def simulate_approve_pix(payment_id: str, credits: Optional[int] = None, package_id: Optional[str] = None, authorization: Optional[str] = Header(None)):
    """Simula a aprovação imediata de um pagamento PIX em ambiente de testes."""
    if not supabase_admin:
        return {"status": "approved", "credits": 999, "added": credits or 12}

    user = get_current_user_from_header(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não autenticado.")

    import datetime
    credits_to_add = credits or 12
    try:
        tx_res = supabase_admin.table("pix_transactions").select("*").eq("gateway_txid", payment_id).execute()
        if tx_res.data:
            tx = tx_res.data[0]
            credits_to_add = tx.get("credits_amount") or credits or 12
            supabase_admin.table("pix_transactions").update({
                "status": "paid",
                "paid_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }).eq("gateway_txid", payment_id).execute()
        else:
            # Se não existia o registro prévio, cria agora como pago
            supabase_admin.table("pix_transactions").insert({
                "user_id": user.id,
                "gateway_txid": payment_id,
                "package_id": package_id or "pacote",
                "credits_amount": credits_to_add,
                "amount_brl": 0.0,
                "status": "paid",
                "paid_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }).execute()
    except Exception as ex:
        print(f"[PIX Simulate Approve Warning] {ex}")

    # Atualiza saldo de forma resiliente consultando o saldo mais atual no Supabase
    try:
        prof_res = supabase_admin.table("profiles").select("credits").eq("id", user.id).execute()
        current_db_credits = prof_res.data[0]["credits"] if prof_res.data else 0
        new_credits = current_db_credits + credits_to_add
        supabase_admin.table("profiles").update({"credits": new_credits}).eq("id", user.id).execute()
    except Exception as e:
        profile = get_or_create_profile(user)
        new_credits = profile.get("credits", 0) + credits_to_add
        supabase_admin.table("profiles").update({"credits": new_credits}).eq("id", user.id).execute()

    return {"status": "approved", "credits": new_credits, "added": credits_to_add}


@app.post("/api/pix/webhook")
async def pix_webhook(request: Request):
    """Webhook do Mercado Pago para notificação instantânea de pagamentos aprovados."""
    try:
        data = await request.json()
    except Exception:
        data = {}

    payment_id = None
    if "data" in data and "id" in data["data"]:
        payment_id = str(data["data"]["id"])
    elif "id" in data:
        payment_id = str(data["id"])

    if payment_id and MERCADO_PAGO_ACCESS_TOKEN:
        try:
            import urllib.request
            import json
            req_obj = urllib.request.Request(
                f"https://api.mercadopago.com/v1/payments/{payment_id}",
                headers={"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
            )
            with urllib.request.urlopen(req_obj, timeout=8) as resp:
                mp_data = json.loads(resp.read().decode("utf-8"))
                if mp_data.get("status") == "approved":
                    is_single_order = payment_id in single_audio_orders
                    if is_single_order:
                        single_audio_orders[payment_id]["status"] = "approved"

                    if supabase_admin:
                        tx_res = supabase_admin.table("pix_transactions").select("*").eq("gateway_txid", payment_id).execute()
                        if tx_res.data:
                            tx = tx_res.data[0]
                            if tx.get("status") != "paid":
                                import datetime
                                supabase_admin.table("pix_transactions").update({
                                    "status": "paid",
                                    "paid_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                                }).eq("gateway_txid", payment_id).execute()

                                u_id = tx.get("user_id")
                                pkg_id = str(tx.get("package_id") or "")
                                if (
                                    not is_single_order
                                    and not pkg_id.startswith("single_")
                                    and u_id
                                    and u_id != "00000000-0000-0000-0000-000000000000"
                                ):
                                    prof_res = supabase_admin.table("profiles").select("credits").eq("id", u_id).execute()
                                    current_cred = prof_res.data[0]["credits"] if prof_res.data else 0
                                    new_cred = current_cred + tx.get("credits_amount", 1)
                                    supabase_admin.table("profiles").update({"credits": new_cred}).eq("id", u_id).execute()
        except Exception as e:
            print(f"[PIX Webhook Processing Error] {e}")

    return {"status": "ok"}


class SimulateRechargeRequest(BaseModel):
    package_id: str = "criador"
    credits: int = 12
    price: str = "27,90"



# -------------------------------------------------------------
# Sistema de Venda de Áudio Avulso no PIX (Pay-as-you-go)
# -------------------------------------------------------------
single_audio_orders = {}

def calculate_single_audio_price(char_count: int) -> float:
    """Calcula preço dinâmico do áudio avulso com margem segura de lucro."""
    if char_count <= 300:
        return 2.49
    elif char_count <= 700:
        return 3.90
    elif char_count <= 1500:
        return 5.90
    else:
        return 9.90


def resolve_gemini_model(mode: Optional[str] = "single", model: Optional[str] = None) -> str:
    """Seleciona o modelo oficial Gemini TTS conforme o modo solicitado."""
    norm_mode = (mode or "single").strip().lower()
    if norm_mode == "dialogue":
        return "gemini-3.8-flash-tts"
    if norm_mode == "expressive":
        return "gemini-3.8-flash-tts"
    if model and model.strip() in {"gemini-3.8-flash-lite-tts", "gemini-3.8-flash-tts"}:
        return model.strip()
    return "gemini-3.8-flash-lite-tts"


def build_tts_cache_key(
    model_name: str,
    mode: str,
    text: str,
    voice: str,
    style: str,
    speed: float = 1.0,
    bgm: Optional[str] = "none",
    bgm_volume: float = 0.15,
    dialogue: Optional[List[Dict[str, Any]]] = None,
    speakers: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Gera hash SHA-256 determinístico indexado por (modelo + texto + voz + estilo + diálogo + velocidade + BGM)."""
    payload = {
        "model": model_name,
        "mode": (mode or "single").strip().lower(),
        "text": text,
        "voice": voice,
        "style": style or "Voz natural, clara e expressiva",
        "speed": round(float(speed or 1.0), 2),
        "bgm": bgm or "none",
        "bgm_volume": round(float(bgm_volume or 0.15), 2) if (bgm and bgm != "none") else 0.0,
        "dialogue": dialogue or [],
        "speakers": speakers or [],
    }
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:24]


def apply_speed_ffmpeg(wav_path: str, speed: float) -> bool:
    """Ajusta a velocidade da fala preservando o pitch via filtro atempo do FFmpeg."""
    if not os.path.exists(wav_path) or abs(float(speed) - 1.0) < 0.04:
        return False
    sp = max(0.5, min(2.0, float(speed)))
    temp_path = wav_path + ".speed.wav"
    try:
        cmd = ["ffmpeg", "-y", "-i", wav_path, "-filter:a", f"atempo={sp:.2f}", temp_path]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:
            os.replace(temp_path, wav_path)
            return True
    except Exception as e:
        print(f"[FFmpeg Speed Error] {e}")
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except Exception:
            pass
    return False


def synthesize_with_gemini_sdk(
    text: str,
    voice: str,
    output_wav_path: str,
    mode: str = "single",
    model: Optional[str] = None,
    style: Optional[str] = "Voz natural, clara e expressiva",
    dialogue: Optional[List[Dict[str, Any]]] = None,
    speakers: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Executa geração TTS somente áudio via SDK oficial @google/genai (gemini_tts_service.mjs)."""
    api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada no servidor.")
    if not os.path.exists(GEMINI_SERVICE_SCRIPT):
        raise RuntimeError(f"Worker Node.js não encontrado: {GEMINI_SERVICE_SCRIPT}")

    payload = {
        "text": text,
        "voice": voice,
        "style": style or "Voz natural, clara e expressiva",
        "mode": (mode or "single").strip().lower(),
        "model": resolve_gemini_model(mode, model),
        "language": "pt-BR",
        "dialogue": dialogue,
        "speakers": speakers,
        "outputWavPath": output_wav_path,
    }
    env = os.environ.copy()
    env["GEMINI_API_KEY"] = api_key

    res = subprocess.run(
        ["node", GEMINI_SERVICE_SCRIPT],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        encoding="utf-8",
        capture_output=True,
        env=env,
        timeout=120,
    )
    if res.returncode != 0:
        err_msg = (res.stderr or res.stdout or "Falha no worker Gemini TTS").strip()
        raise RuntimeError(err_msg)

    try:
        return json.loads(res.stdout.strip())
    except Exception:
        return {"success": os.path.exists(output_wav_path), "model": payload["model"], "mode": payload["mode"]}


def execute_synthesis(
    text: str,
    voice: str = "Kore",
    speed: float = 1.0,
    bgm: Optional[str] = "none",
    bgm_volume: float = 0.15,
    threads: int = 4,
    mode: str = "single",
    model: Optional[str] = None,
    style: Optional[str] = "Voz natural, clara e expressiva",
    dialogue: Optional[List[Dict[str, Any]]] = None,
    speakers: Optional[List[Dict[str, Any]]] = None,
):
    """Executa a síntese neural com cache SHA-256 em memória/disco e Gemini TTS oficial (@google/genai)."""
    import time
    start_time = time.time()

    norm_mode = (mode or "single").strip().lower()
    active_model = resolve_gemini_model(norm_mode, model)
    effective_style = (style or "Voz natural, clara e expressiva").strip()

    # 1. Verifica cache em memória e em disco por hash (modelo + texto + voz + estilo + speakers + ritmo + BGM)
    cache_hash = build_tts_cache_key(
        model_name=active_model,
        mode=norm_mode,
        text=text,
        voice=voice,
        style=effective_style,
        speed=speed,
        bgm=bgm,
        bgm_volume=bgm_volume,
        dialogue=dialogue,
        speakers=speakers,
    )
    cached_wav_name = f"cache_{cache_hash}.wav"
    cached_mp3_name = f"cache_{cache_hash}.mp3"
    cached_wav_path = os.path.join(GEMINI_CACHE_DIR, cached_wav_name)
    cached_mp3_path = os.path.join(GEMINI_CACHE_DIR, cached_mp3_name)

    if cache_hash in _gemini_tts_mem_cache:
        mem_entry = _gemini_tts_mem_cache[cache_hash]
        mem_wav = os.path.join(GEMINI_CACHE_DIR, os.path.basename(mem_entry["filename"]))
        if os.path.exists(mem_wav) and os.path.getsize(mem_wav) > 500:
            res_copy = dict(mem_entry)
            res_copy["cached"] = True
            res_copy["elapsed_seconds"] = round(time.time() - start_time, 3)
            return res_copy

    if os.path.exists(cached_wav_path) and os.path.getsize(cached_wav_path) > 500:
        if not os.path.exists(cached_mp3_path):
            convert_wav_to_mp3(cached_wav_path, cached_mp3_path)
        est_duration = 2.0
        try:
            import soundfile as sf
            est_duration = round(sf.info(cached_wav_path).duration, 2)
        except Exception:
            est_duration = max(round(len(text.split()) / 2.6, 1), 1.5)
        cached_res = {
            "filename": cached_wav_name,
            "url": f"/outputs/cache/{cached_wav_name}",
            "mp3_url": f"/outputs/cache/{cached_mp3_name}",
            "duration": est_duration,
            "elapsed_seconds": round(time.time() - start_time, 3),
            "voice": voice,
            "model": active_model,
            "mode": norm_mode,
            "char_count": len(text),
            "cached": True,
        }
        _gemini_tts_mem_cache[cache_hash] = dict(cached_res)
        return cached_res

    wav_path = cached_wav_path
    mp3_path = cached_mp3_path
    wav_filename = cached_wav_name
    mp3_filename = cached_mp3_name
    used_gemini = False

    eleven_voice_id = None
    fb_voice = "dii"
    fb_semi = 0.0

    is_explicit_legacy_vip = voice.startswith("el_") and voice in ELEVENLABS_VOICES
    is_explicit_custom = voice.startswith("custom_")

    # 2. Motor Principal Oficial: Google Gemini TTS via @google/genai (Interactions API)
    active_gemini_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "").strip()
    gemini_error_msg = ""
    if not active_gemini_key:
        gemini_error_msg = "GEMINI_API_KEY não configurada no servidor (.env / container)."
        print(f"[Gemini TTS Warning]: {gemini_error_msg}")
    elif not is_explicit_legacy_vip and not is_explicit_custom:
        try:
            sdk_res = synthesize_with_gemini_sdk(
                text=text,
                voice=voice,
                output_wav_path=wav_path,
                mode=norm_mode,
                model=active_model,
                style=effective_style,
                dialogue=dialogue,
                speakers=speakers,
            )
            if os.path.exists(wav_path) and os.path.getsize(wav_path) > 500:
                used_gemini = True
                active_model = sdk_res.get("model", active_model)
                apply_speed_ffmpeg(wav_path, speed)
        except Exception as gem_err:
            gemini_error_msg = str(gem_err)
            print(f"[Gemini TTS SDK Warning - Usando Fallback]: {gem_err}")

    # 3. Fallback legado (ElevenLabs / Motor Local VITS) se Gemini não estiver ativo ou for voz custom/clonada
    if not used_gemini:
        if is_explicit_legacy_vip and ELEVENLABS_API_KEY:
            el_voice = ELEVENLABS_VOICES[voice]
            eleven_voice_id = el_voice["voice_id"]
            fb_voice = el_voice.get("fallback_voice", "dii")
            fb_semi = el_voice.get("fallback_semitones", 0.0)
        elif is_explicit_custom and ELEVENLABS_API_KEY:
            c_meta = tts_engine.load_custom_voices_metadata()
            if voice in c_meta and c_meta[voice].get("eleven_voice_id"):
                eleven_voice_id = c_meta[voice]["eleven_voice_id"]
                fb_voice = c_meta[voice].get("base_voice", "dii")
                fb_semi = c_meta[voice].get("semitones_shift", 0.0)

        if eleven_voice_id and ELEVENLABS_API_KEY:
            try:
                synthesize_elevenlabs(eleven_voice_id, text, mp3_path)
                cmd = ["ffmpeg", "-y", "-i", mp3_path, "-f", "wav", wav_path]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except Exception as el_err:
                print(f"[ElevenLabs Quota/API Warning - Fallback Local]: {el_err}")
                fb_res = tts_engine.synthesize_text(
                    text=text,
                    voice_key=fb_voice,
                    speed=speed,
                    num_threads=threads,
                )
                shutil.move(fb_res["file_path"], wav_path)
                if abs(fb_semi) > 0.15:
                    tts_engine.pitch_shift_ffmpeg(wav_path, fb_semi, fb_res.get("sample_rate", 22050))
        else:
            if gemini_error_msg:
                raise RuntimeError(f"Gemini TTS falhou: {gemini_error_msg}")
            gem_info = GEMINI_VOICE_MAP.get(voice.lower())
            local_voice_key = gem_info["fallback_voice"] if gem_info else voice
            if local_voice_key not in tts_engine.VOICES and not local_voice_key.startswith("custom_"):
                local_voice_key = next(iter(tts_engine.VOICES.keys()), None)
            if not local_voice_key:
                raise RuntimeError(gemini_error_msg or "Motor Gemini TTS indisponível e nenhuma voz local de fallback carregada.")
            result = tts_engine.synthesize_text(
                text=text,
                voice_key=local_voice_key,
                speed=speed,
                num_threads=threads,
            )
            shutil.move(result["file_path"], wav_path)

    # Aplica Trilha Sonora de Fundo (BGM) se selecionada
    if bgm and bgm != "none" and bgm in BGM_TRACKS and os.path.exists(wav_path):
        bgm_file = os.path.join(STATIC_DIR, "bgm", BGM_TRACKS[bgm]["file"])
        if os.path.exists(bgm_file):
            mix_audio_with_bgm(wav_path, bgm_file, bgm_volume or 0.15)
            convert_wav_to_mp3(wav_path, mp3_path)

    if os.path.exists(wav_path) and not os.path.exists(mp3_path):
        convert_wav_to_mp3(wav_path, mp3_path)

    elapsed = round(time.time() - start_time, 2)
    est_duration = 2.0
    if os.path.exists(wav_path):
        try:
            import soundfile as sf
            est_duration = round(sf.info(wav_path).duration, 2)
        except Exception:
            word_count = len(text.split())
            est_duration = max(round(word_count / 2.6, 1), 1.5)

    active_filename = wav_filename if os.path.exists(wav_path) else mp3_filename
    res_obj = {
        "filename": active_filename,
        "url": f"/outputs/cache/{active_filename}",
        "mp3_url": f"/outputs/cache/{mp3_filename}",
        "duration": est_duration,
        "elapsed_seconds": elapsed,
        "voice": voice,
        "model": active_model,
        "mode": norm_mode,
        "char_count": len(text),
        "cached": False,
    }
    _gemini_tts_mem_cache[cache_hash] = dict(res_obj)
    return res_obj


class CreateSinglePixRequest(BaseModel):
    text: str
    voice: str = "Kore"
    speed: float = 1.0
    bgm: Optional[str] = "none"
    bgm_volume: Optional[float] = 0.15
    email: Optional[str] = None
    mode: Optional[str] = "single"
    model: Optional[str] = None
    style: Optional[str] = "Voz natural, clara e expressiva"
    dialogue: Optional[List[Dict[str, Any]]] = None
    speakers: Optional[List[Dict[str, Any]]] = None
    auto_correct_fee: bool = False


def _build_dialogue_fallback_text(dialogue: Optional[List[Dict[str, Any]]]) -> str:
    """Concatena texto de um array de falas de diálogo quando req.text não vier preenchido."""
    if not dialogue:
        return ""
    lines = []
    for item in dialogue:
        sp = str(item.get("speaker") or "Locutor").strip()
        tx = str(item.get("text") or "").strip()
        if tx:
            lines.append(f"{sp}: {tx}")
    return "\n".join(lines).strip()


def _synthesize_single_order_if_needed(order: Dict[str, Any]):
    """Executa ou reaproveita o áudio sintetizado para um pedido avulso pago."""
    if not order.get("audio_result"):
        order["audio_result"] = execute_synthesis(
            text=order["text"],
            voice=order["voice"],
            speed=order["speed"],
            bgm=order.get("bgm"),
            bgm_volume=order.get("bgm_volume", 0.15),
            mode=order.get("mode", "single"),
            model=order.get("model"),
            style=order.get("style", "Voz natural, clara e expressiva"),
            dialogue=order.get("dialogue"),
            speakers=order.get("speakers"),
        )
    return order["audio_result"]


@app.post("/api/pix/create-single")
def create_single_audio_pix(req: CreateSinglePixRequest, authorization: Optional[str] = Header(None)):
    """Cria uma cobrança PIX para geração de um único áudio avulso (sem cadastro)."""
    import time
    import datetime
    import uuid
    import json
    import urllib.request

    clean_text = (req.text or "").replace("\r\n", "\n").strip()
    if not clean_text and req.dialogue:
        clean_text = _build_dialogue_fallback_text(req.dialogue)
    if not clean_text:
        raise HTTPException(status_code=400, detail="O texto não pode estar vazio.")
    if len(clean_text) > 3000:
        raise HTTPException(status_code=400, detail="O texto ultrapassou o limite máximo de 3.000 caracteres.")

    char_count = len(clean_text)
    amount_num = calculate_single_audio_price(char_count)
    if req.auto_correct_fee:
        amount_num = round(amount_num + 0.10, 2)

    user = get_current_user_from_header(authorization) if supabase_admin and authorization else None
    user_email = req.email or (getattr(user, "email", None) if user else "cliente@clonavoz.com.br")
    user_name = "Cliente Avulso"

    payment_id = None
    qr_code = ""
    qr_code_base64 = ""
    is_simulated = True

    if MERCADO_PAGO_ACCESS_TOKEN:
        try:
            mp_url = "https://api.mercadopago.com/v1/payments"
            mp_payload = {
                "transaction_amount": amount_num,
                "description": f"Clonavoz - Audio Avulso ({char_count} carac.)",
                "payment_method_id": "pix",
                "payer": {
                    "email": user_email,
                    "first_name": user_name
                },
                "notification_url": f"{BASE_URL}/api/pix/webhook"
            }
            req_headers = {
                "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
                "Content-Type": "application/json",
                "X-Idempotency-Key": str(uuid.uuid4())
            }
            req_obj = urllib.request.Request(
                mp_url,
                data=json.dumps(mp_payload).encode("utf-8"),
                headers=req_headers,
                method="POST"
            )
            with urllib.request.urlopen(req_obj, timeout=10) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                payment_id = str(resp_data.get("id"))
                tx_data = resp_data.get("point_of_interaction", {}).get("transaction_data", {})
                qr_code = tx_data.get("qr_code", "")
                qr_code_base64 = tx_data.get("qr_code_base64", "")
                is_simulated = False
        except Exception as mp_err:
            print(f"[Mercado Pago Single Audio Warning]: {mp_err}")

    if not payment_id:
        payment_id = f"sim_single_{int(time.time() * 1000)}"
        qr_code = f"00020126580014br.gov.bcb.pix0136clonavoz-avulso-{payment_id}520400005303986540{len(str(amount_num)):02d}{amount_num:.2f}5802BR5916CLONAVOZ STUDIO6009SAO PAULO62070503***6304"
        is_simulated = True

    # Registra o pedido avulso em memória
    single_audio_orders[payment_id] = {
        "text": clean_text,
        "voice": req.voice,
        "speed": req.speed,
        "bgm": req.bgm,
        "bgm_volume": req.bgm_volume,
        "mode": req.mode or "single",
        "model": req.model,
        "style": req.style or "Voz natural, clara e expressiva",
        "dialogue": req.dialogue,
        "speakers": req.speakers,
        "amount": amount_num,
        "char_count": char_count,
        "status": "pending",
        "created_at": time.time(),
        "audio_result": None
    }

    # Registra no Supabase para métricas financeiras se ativo
    if supabase_admin:
        try:
            supabase_admin.table("pix_transactions").insert({
                "user_id": user.id if user else "00000000-0000-0000-0000-000000000000",
                "gateway_txid": payment_id,
                "package_id": f"single_{char_count}c",
                "credits_amount": 1,
                "amount_brl": amount_num,
                "status": "pending",
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }).execute()
        except Exception as ex:
            print(f"[PIX Single Supabase Insert Warning]: {ex}")

    return {
        "success": True,
        "payment_id": payment_id,
        "qr_code": qr_code,
        "qr_code_base64": qr_code_base64,
        "amount": amount_num,
        "char_count": char_count,
        "is_simulated": is_simulated,
        "status": "pending"
    }


@app.get("/api/pix/status-single/{payment_id}")
def check_single_audio_pix_status(payment_id: str):
    """Consulta se o pagamento do áudio avulso foi aprovado e entrega o áudio sintetizado."""
    order = single_audio_orders.get(payment_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido avulso não encontrado.")

    is_approved = False

    if not payment_id.startswith("sim_") and MERCADO_PAGO_ACCESS_TOKEN:
        try:
            import urllib.request
            import json
            req_obj = urllib.request.Request(
                f"https://api.mercadopago.com/v1/payments/{payment_id}",
                headers={"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
            )
            with urllib.request.urlopen(req_obj, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "approved":
                    is_approved = True
        except Exception as e:
            print(f"[MP Single Status Query Error]: {e}")
    elif order.get("status") == "approved":
        is_approved = True

    if is_approved:
        order["status"] = "approved"
        if not order.get("audio_result"):
            _synthesize_single_order_if_needed(order)

            # Atualiza no Supabase se existir
            if supabase_admin:
                try:
                    import datetime
                    supabase_admin.table("pix_transactions").update({
                        "status": "paid",
                        "paid_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }).eq("gateway_txid", payment_id).execute()
                except Exception:
                    pass

        return {
            "status": "approved",
            "audio": order["audio_result"],
            "amount": order["amount"],
            "char_count": order["char_count"]
        }

    return {"status": "pending", "amount": order["amount"]}


@app.post("/api/pix/simulate-single/{payment_id}")
def simulate_single_audio_pix(payment_id: str):
    """Simula a aprovação imediata do áudio avulso em ambiente de testes/desenvolvimento."""
    order = single_audio_orders.get(payment_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido avulso não encontrado.")
    order["status"] = "approved"
    audio_res = _synthesize_single_order_if_needed(order)
    return {"status": "approved", "audio": audio_res}


@app.post("/api/recharge/simulate")
def simulate_recharge(req: SimulateRechargeRequest, authorization: Optional[str] = Header(None)):
    """Simula a confirmação de pagamento PIX e credita o saldo diretamente no Supabase."""
    if not supabase_admin:
        return {"success": True, "credits": 999, "added": req.credits}

    user = get_current_user_from_header(authorization)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Você precisa estar conectado na sua conta para recarregar créditos.",
        )

    profile = get_or_create_profile(user)
    current_credits = profile.get("credits", 0)
    new_credits = current_credits + max(req.credits, 1)

    try:
        supabase_admin.table("profiles").update({"credits": new_credits}).eq("id", user.id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao creditar saldo no banco: {str(e)}")

    try:
        import datetime
        raw_price = req.price.replace("R$", "").replace(" ", "").replace(",", ".").strip()
        amount_num = float(raw_price) if raw_price else 0.0
        supabase_admin.table("pix_transactions").insert({
            "user_id": user.id,
            "package_id": req.package_id,
            "credits_amount": req.credits,
            "amount_brl": amount_num,
            "status": "paid",
            "paid_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }).execute()
    except Exception as ex:
        print(f"[PIX Transaction Warning] {ex}")

    return {"success": True, "credits": new_credits, "added": req.credits}


@app.get("/api/voices")
def get_voices():
    results = []

    # 1. Catálogo oficial das 30 vozes Google Gemini TTS (Principal)
    for gv in GEMINI_TTS_VOICES:
        wav_sample = os.path.join(PUBLIC_VOICE_SAMPLES_DIR, f"{gv['key'].lower()}.wav")
        if os.path.exists(wav_sample) and os.path.getsize(wav_sample) > 500:
            sample_url = f"/voice-samples/{gv['key'].lower()}.wav"
        else:
            fb_key = gv.get("fallback_voice", "su")
            sample_url = f"/demos/{fb_key}_sample.mp3"
        results.append({
            "key": gv["key"],
            "label": gv["label"],
            "gender": gv["gender"],
            "timbre": gv["timbre"],
            "default_style": gv["default_style"],
            "quality": "Gemini TTS Studio (24kHz WAV)",
            "type": "gemini_tts",
            "is_downloaded": True,
            "sample_url": sample_url,
        })

    return results


@app.post("/api/download-voice")
def download_voice(req: DownloadVoiceRequest):
    if req.voice not in tts_engine.VOICES:
        raise HTTPException(status_code=404, detail="Voz não encontrada")
    try:
        tts_engine.ensure_model_ready(req.voice)
        return {"success": True, "message": "Modelo pronto para uso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-voice")
async def upload_voice(
    file: UploadFile = File(...),
    name: str = Form(...),
    gender: str = Form("Feminina"),
):
    if not name.strip():
        raise HTTPException(status_code=400, detail="O nome da voz é obrigatório.")

    allowed_exts = [".wav", ".mp3", ".ogg", ".m4a", ".flac"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de áudio não suportado ({ext}). Use .wav, .mp3, .ogg ou .m4a",
        )

    audio_bytes = await file.read()
    if len(audio_bytes) < 1024:
        raise HTTPException(status_code=400, detail="Arquivo de áudio muito pequeno ou corrompido.")

    try:
        entry = tts_engine.add_custom_voice(
            name=name.strip(),
            gender=gender.strip(),
            audio_bytes=audio_bytes,
            filename=file.filename,
        )
        return {"success": True, "voice": entry}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar áudio: {str(e)}")


@app.get("/api/custom-voices")
def get_custom_voices():
    return tts_engine.get_custom_voices()


@app.delete("/api/custom-voices/{voice_id}")
def delete_custom_voice(voice_id: str):
    if tts_engine.delete_custom_voice(voice_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Voz não encontrada")


@app.get("/custom-voices/sample/{filename}")
def get_sample_file(filename: str):
    file_path = os.path.join(CUSTOM_VOICES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Amostra de áudio não encontrada")
    return FileResponse(file_path)


def convert_wav_to_mp3(wav_path: str, mp3_path: str):
    """Converte arquivo WAV para MP3 usando FFmpeg (ou PyAV fallback) com qualidade de 192kbps."""
    try:
        cmd = ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-b:a", "192k", mp3_path]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 500:
            return
    except Exception as e:
        print(f"[FFmpeg MP3 Error] {e}")
    try:
        import av
        inp = av.open(wav_path)
        out = av.open(mp3_path, mode="w", format="mp3")
        in_stream = inp.streams.audio[0]
        out_stream = out.add_stream("mp3", rate=in_stream.rate)
        out_stream.bit_rate = 192000
        for frame in inp.decode(in_stream):
            for packet in out_stream.encode(frame):
                out.mux(packet)
        for packet in out_stream.encode():
            out.mux(packet)
        inp.close()
        out.close()
    except Exception as e:
        print(f"[PyAV MP3 Fallback Error] {e}")


def mix_audio_with_bgm(voice_wav_path: str, bgm_file_path: str, volume: float = 0.15) -> bool:
    """Mixes background music into voice wav using ffmpeg with smooth fadeout."""
    temp_mixed = voice_wav_path + ".mixed.wav"
    try:
        vol = max(0.01, min(float(volume), 1.0))
        # duration=first ensures the output ends right when voice finishes
        # dropout_transition=2 ensures a smooth 2-second fadeout
        filter_str = f"[0:a]volume=1.0[v];[1:a]volume={vol:.2f}[m];[v][m]amix=inputs=2:duration=first:dropout_transition=2[a]"
        cmd = [
            "ffmpeg", "-y",
            "-i", voice_wav_path,
            "-stream_loop", "-1",
            "-i", bgm_file_path,
            "-filter_complex", filter_str,
            "-map", "[a]",
            temp_mixed
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and os.path.exists(temp_mixed) and os.path.getsize(temp_mixed) > 1000:
            os.replace(temp_mixed, voice_wav_path)
            return True
    except Exception as e:
        print(f"[BGM Mix Error] {e}")
        if os.path.exists(temp_mixed):
            try:
                os.remove(temp_mixed)
            except Exception:
                pass
    return False


MAX_FREE_PREVIEWS = 3
PREVIEW_USAGE_FILE = os.path.join(OUTPUTS_DIR, "preview_usage.json")
_preview_usage_lock = threading.Lock()


def _extract_client_ip(request: Request) -> str:
    """Extrai o IP real do visitante considerando proxies (Cloudflare/Nginx)."""
    for header in ("cf-connecting-ip", "x-forwarded-for", "x-real-ip"):
        val = (request.headers.get(header) or "").strip()
        if val:
            return val.split(",")[0].strip()
    return (request.client.host if request.client else "unknown") or "unknown"


def _load_preview_usage() -> Dict[str, int]:
    try:
        if os.path.exists(PREVIEW_USAGE_FILE):
            with open(PREVIEW_USAGE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return {str(k): int(v) for k, v in data.items()}
    except Exception:
        pass
    return {}


def _save_preview_usage(data: Dict[str, int]) -> None:
    try:
        os.makedirs(os.path.dirname(PREVIEW_USAGE_FILE), exist_ok=True)
        with open(PREVIEW_USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[PreviewUsage] Erro ao salvar preview_usage.json: {e}")


def _get_preview_attempts(ip: str, client_id: Optional[str]) -> int:
    with _preview_usage_lock:
        usage = _load_preview_usage()
        ip_count = usage.get(f"ip:{ip}", 0) if ip else 0
        cid = (client_id or "").strip()
        cid_count = usage.get(f"cid:{cid}", 0) if cid else 0
        return max(ip_count, cid_count)


def _increment_preview_attempts(ip: str, client_id: Optional[str]) -> int:
    with _preview_usage_lock:
        usage = _load_preview_usage()
        cid = (client_id or "").strip()
        ip_key = f"ip:{ip}" if ip else ""
        cid_key = f"cid:{cid}" if cid else ""
        current = max(usage.get(ip_key, 0) if ip_key else 0, usage.get(cid_key, 0) if cid_key else 0)
        new_count = current + 1
        if ip_key:
            usage[ip_key] = new_count
        if cid_key:
            usage[cid_key] = new_count
        _save_preview_usage(usage)
        return new_count


class PreviewRequest(BaseModel):
    text: str
    voice: str = "Kore"
    speed: float = 1.0
    mode: Optional[str] = "single"
    model: Optional[str] = None
    style: Optional[str] = "Voz natural, clara e expressiva"
    dialogue: Optional[List[Dict[str, Any]]] = None
    speakers: Optional[List[Dict[str, Any]]] = None
    client_id: Optional[str] = None


@app.post("/api/preview")
def generate_preview(req: PreviewRequest, request: Request):
    """Gera uma prévia curta e gratuita (máx. 3 tentativas por visitante e tamanho reduzido para segurança de custo)."""
    client_ip = _extract_client_ip(request)
    attempts = _get_preview_attempts(client_ip, req.client_id)
    if attempts >= MAX_FREE_PREVIEWS:
        raise HTTPException(
            status_code=429,
            detail="Testes gratuitos encerrados (limite de 3 prévias atingido). Para gerar seu áudio completo, clique em Pagar no PIX e Gerar.",
        )

    clean_text = (req.text or "").replace("\r\n", "\n").strip()
    if not clean_text and req.dialogue:
        clean_text = _build_dialogue_fallback_text(req.dialogue)
    if not clean_text:
        raise HTTPException(status_code=400, detail="Digite algum texto para ouvir a prévia.")

    norm_mode = (req.mode or "single").strip().lower()
    preview_dialogue = None
    max_single_len = 80
    max_dialogue_len = 100

    if norm_mode == "dialogue" and req.dialogue:
        total_len = 0
        preview_dialogue = []
        for turn in req.dialogue:
            t_txt = str(turn.get("text") or "").strip()
            if not t_txt:
                continue
            remaining = max_dialogue_len - total_len
            if remaining <= 12:
                break
            snippet = t_txt[:remaining].strip()
            preview_dialogue.append({**turn, "text": snippet})
            total_len += len(snippet)
        preview_text = _build_dialogue_fallback_text(preview_dialogue) or clean_text[:max_dialogue_len]
    else:
        preview_text = clean_text[:max_single_len].strip()
        if len(clean_text) > max_single_len:
            last_space = preview_text.rfind(" ")
            if last_space > 45:
                preview_text = preview_text[:last_space] + "..."
            else:
                preview_text = preview_text + "..."

    try:
        audio_res = execute_synthesis(
            text=preview_text,
            voice=req.voice,
            speed=req.speed,
            bgm="none",
            bgm_volume=0.0,
            mode=norm_mode,
            model=req.model,
            style=req.style or "Voz natural, clara e expressiva",
            dialogue=preview_dialogue,
            speakers=req.speakers,
        )
    except HTTPException:
        raise
    except Exception as synth_err:
        print(f"[Preview Error] {type(synth_err).__name__}: {synth_err}")
        raise HTTPException(status_code=500, detail=f"Falha ao gerar prévia de áudio: {synth_err}")

    new_attempts = _increment_preview_attempts(client_ip, req.client_id)

    return {
        "success": True,
        "preview_text": preview_text,
        "preview_attempts": new_attempts,
        "max_previews": MAX_FREE_PREVIEWS,
        "remaining_previews": max(0, MAX_FREE_PREVIEWS - new_attempts),
        "audio": audio_res
    }


@app.post("/api/synthesize")
def synthesize(
    req: SynthesizeRequest,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None)
):
    normalized_text = (req.text or "").replace("\r\n", "\n").strip()
    if not normalized_text and req.dialogue:
        normalized_text = _build_dialogue_fallback_text(req.dialogue)
    if not normalized_text:
        raise HTTPException(status_code=400, detail="Texto não pode estar vazio")

    if len(normalized_text) > 3500:
        raise HTTPException(
            status_code=400,
            detail="O texto ultrapassou o limite máximo de 3.000 caracteres por áudio.",
        )
    req.text = normalized_text

    user = None
    profile = None
    if supabase_admin:
        user = get_current_user_from_header(authorization)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Acesso não autorizado. Faça login ou crie sua conta para gerar áudios.",
            )
        profile = get_or_create_profile(user)
        current_credits = profile.get("credits", 0)
        if current_credits < 1:
            raise HTTPException(
                status_code=402,
                detail="Você utilizou todos os seus créditos. Adquira uma recarga para continuar gerando áudios.",
            )

    try:
        synth_res = execute_synthesis(
            text=req.text,
            voice=req.voice,
            speed=req.speed,
            bgm=req.bgm,
            bgm_volume=req.bgm_volume or 0.15,
            threads=req.threads,
            mode=req.mode or "single",
            model=req.model,
            style=req.style or "Voz natural, clara e expressiva",
            dialogue=req.dialogue,
            speakers=req.speakers,
        )

        remaining_credits = profile.get("credits", 1) if profile else 999
        active_filename = synth_res["filename"]
        active_url = synth_res["url"]
        mp3_url = synth_res["mp3_url"]
        duration_sec = float(synth_res.get("duration") or 2.0)
        elapsed_sec = float(synth_res.get("elapsed_seconds") or 0.1)

        if supabase_admin and user:
            try:
                prof_cur = supabase_admin.table("profiles").select("credits").eq("id", user.id).execute()
                current_db_credits = prof_cur.data[0]["credits"] if prof_cur.data and len(prof_cur.data) > 0 else (profile.get("credits", 1) if profile else 1)
                remaining_credits = max(current_db_credits - 1, 0)
                supabase_admin.table("profiles").update({"credits": remaining_credits}).eq("id", user.id).execute()
            except Exception as ex:
                print(f"[Supabase Credit Update Error] {ex}")
                remaining_credits = max(profile.get("credits", 1) - 1, 0) if profile else 999

            if req.save_history:
                try:
                    cached_file = os.path.join(GEMINI_CACHE_DIR, active_filename)
                    size_kb = round(os.path.getsize(cached_file) / 1024, 1) if os.path.exists(cached_file) else 0
                    title = req.text.strip().replace("\n", " ")[:60]
                    supabase_admin.table("audio_generations").insert({
                        "user_id": user.id,
                        "title": title,
                        "text_prompt": req.text,
                        "voice_key": req.voice,
                        "speed": req.speed,
                        "duration_seconds": round(duration_sec, 2),
                        "audio_url_wav": active_url,
                        "audio_url_mp3": mp3_url,
                        "file_size_kb": size_kb
                    }).execute()
                except Exception as ex:
                    print(f"[Supabase Generation Save Error] {ex}")

        return {
            "success": True,
            "filename": active_filename,
            "url": active_url,
            "mp3_url": mp3_url,
            "duration": round(duration_sec, 2),
            "elapsed": round(elapsed_sec, 2),
            "speed_factor": round(duration_sec / max(elapsed_sec, 0.001), 1),
            "voice": req.voice,
            "model": synth_res.get("model"),
            "mode": synth_res.get("mode"),
            "cached": synth_res.get("cached", False),
            "text": req.text,
            "credits": remaining_credits,
            "saved_history": bool(req.save_history),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _serve_audio_from_directory(directory: str, filename: str):
    """Serve arquivos WAV/MP3 com conversão automática sob demanda e proteção de path."""
    safe_name = os.path.basename(filename)
    file_path = os.path.join(directory, safe_name)

    if safe_name.endswith(".mp3"):
        wav_path = os.path.join(directory, safe_name[:-4] + ".wav")
        if not os.path.exists(file_path) and os.path.exists(wav_path):
            try:
                convert_wav_to_mp3(wav_path, file_path)
            except Exception as e:
                print(f"[MP3 conversion error] {e}")
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="audio/mpeg", filename=safe_name)

    if safe_name.endswith(".wav"):
        mp3_path = os.path.join(directory, safe_name[:-4] + ".mp3")
        if not os.path.exists(file_path) and os.path.exists(mp3_path):
            try:
                cmd = ["ffmpeg", "-y", "-i", mp3_path, "-f", "wav", file_path]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except Exception as e:
                print(f"[WAV conversion error] {e}")
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="audio/wav", filename=safe_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo de áudio não encontrado")

    media_type = "audio/mpeg" if safe_name.endswith(".mp3") else "audio/wav"
    return FileResponse(file_path, media_type=media_type, filename=safe_name)


@app.get("/outputs/cache/{filename}")
def get_cached_output_file(filename: str):
    return _serve_audio_from_directory(GEMINI_CACHE_DIR, filename)


@app.get("/outputs/{filename}")
def get_output_file(filename: str):
    return _serve_audio_from_directory(OUTPUTS_DIR, filename)


@app.get("/api/history")
def get_history(authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization) if supabase_admin else None

    # Se o usuário está autenticado no Supabase, busca da tabela audio_generations
    if supabase_admin and user:
        try:
            res = (
                supabase_admin.table("audio_generations")
                .select("*")
                .eq("user_id", user.id)
                .order("created_at", desc=True)
                .limit(40)
                .execute()
            )
            generations = []
            for g in res.data:
                fname = os.path.basename(g.get("audio_url_wav", ""))
                generations.append({
                    "id": g.get("id"),
                    "title": g.get("title") or fname,
                    "filename": fname,
                    "url": g.get("audio_url_wav"),
                    "mp3_url": g.get("audio_url_mp3"),
                    "voice": g.get("voice_key"),
                    "duration": g.get("duration_seconds", 0),
                    "size_kb": g.get("file_size_kb", 0),
                    "created_at": g.get("created_at"),
                })
            return generations
        except Exception as e:
            print(f"[History Query Error] {e}")

    # Se não houver usuário autenticado, o histórico é estritamente vazio (privacidade total)
    return []


@app.delete("/api/history/{item_id}")
def delete_history_item(item_id: str, authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization) if supabase_admin else None

    # Se autenticado, deleta do Supabase
    if supabase_admin and user:
        try:
            res = (
                supabase_admin.table("audio_generations")
                .select("*")
                .eq("id", item_id)
                .eq("user_id", user.id)
                .execute()
            )
            if res.data:
                record = res.data[0]
                supabase_admin.table("audio_generations").delete().eq("id", item_id).eq("user_id", user.id).execute()
                if record.get("audio_url_wav"):
                    fname = os.path.basename(record["audio_url_wav"])
                    wav_file = os.path.join(OUTPUTS_DIR, fname)
                    mp3_file = os.path.join(OUTPUTS_DIR, fname.replace(".wav", ".mp3"))
                    if os.path.exists(wav_file):
                        os.remove(wav_file)
                    if os.path.exists(mp3_file):
                        os.remove(mp3_file)
                return {"success": True}
        except Exception as e:
            print(f"[History Delete Error] {e}")

    # Fallback para exclusão por nome de arquivo em disco
    wav_path = os.path.join(OUTPUTS_DIR, item_id)
    mp3_path = os.path.join(OUTPUTS_DIR, item_id.replace(".wav", ".mp3"))
    if os.path.exists(wav_path):
        os.remove(wav_path)
    if os.path.exists(mp3_path):
        os.remove(mp3_path)
    return {"success": True}
