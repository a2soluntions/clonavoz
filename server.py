import datetime
import hashlib
import json
import os
import glob
import subprocess
from typing import Optional
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
MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN", "").strip()
BASE_URL = os.getenv("BASE_URL", "https://api.clonavoz.com.br").strip()

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

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
OUTPUTS_DIR = tts_engine.OUTPUTS_DIR
CUSTOM_VOICES_DIR = tts_engine.CUSTOM_VOICES_DIR

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# /outputs/{filename} é servido dinamicamente por @app.get("/outputs/{filename}") para garantir conversão WAV/MP3 on-the-fly

bgm_dir = os.path.join(STATIC_DIR, "bgm")
if os.path.exists(bgm_dir):
    app.mount("/bgm", StaticFiles(directory=bgm_dir), name="bgm")

demos_dir = os.path.join(STATIC_DIR, "demos")
if os.path.exists(demos_dir):
    app.mount("/demos", StaticFiles(directory=demos_dir), name="demos")

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

def load_analytics() -> dict:
    if os.path.exists(ANALYTICS_FILE):
        try:
            with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Auto-correção para histórico que havia sido gravado no UTC antigo
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

                if changed:
                    try:
                        with open(ANALYTICS_FILE, "w", encoding="utf-8") as wf:
                            json.dump(data, wf, ensure_ascii=False, indent=2)
                    except Exception:
                        pass

                return data
        except Exception:
            pass
    return {
        "total_views": 0,
        "unique_visitors": [],
        "today": get_brasil_now().date().isoformat(),
        "today_views": 0,
        "today_uniques": [],
        "last_visit": "Nenhuma visita registrada ainda"
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

    return {
        "total_views": data.get("total_views", 0),
        "unique_visitors": len(data.get("unique_visitors", [])),
        "today_views": today_views,
        "today_uniques": today_uniques,
        "last_visit": data.get("last_visit", "Nenhuma visita registrada ainda"),
        "date": today_str
    }

@app.post("/api/reset-stats")
def reset_stats():
    """Zera os contadores analíticos para iniciar uma contagem limpa de visitas reais."""
    br_now = get_brasil_now()
    data = {
        "total_views": 0,
        "unique_visitors": [],
        "today": br_now.date().isoformat(),
        "today_views": 0,
        "today_uniques": [],
        "last_visit": "Nenhuma visita registrada ainda"
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
    voice: str = "sarah"
    speed: float = 1.0
    threads: int = 4
    bgm: Optional[str] = "none"
    bgm_volume: Optional[float] = 0.15
    save_history: Optional[bool] = True


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

    if payment_id and MERCADO_PAGO_ACCESS_TOKEN and supabase_admin:
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
        except Exception as e:
            print(f"[PIX Webhook Processing Error] {e}")

    return {"status": "ok"}


class SimulateRechargeRequest(BaseModel):
    package_id: str = "criador"
    credits: int = 12
    price: str = "27,90"


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
    # 1. Standard voices
    for key, info in tts_engine.VOICES.items():
        sample_path = os.path.join(STATIC_DIR, "demos", f"{key}_sample.mp3")
        sample_url = f"/static/demos/{key}_sample.mp3" if os.path.exists(sample_path) else ""
        results.append(
            {
                "key": key,
                "label": info["label"],
                "gender": info["gender"],
                "quality": info["quality"],
                "type": "standard",
                "is_downloaded": tts_engine.is_model_downloaded(key),
                "sample_url": sample_url,
            }
        )

    # 2. ElevenLabs VIP Ultra-HD Voices
    if ELEVENLABS_API_KEY:
        for el_key, el_info in ELEVENLABS_VOICES.items():
            results.append({
                "key": el_key,
                "label": el_info["label"],
                "gender": el_info["gender"],
                "quality": el_info["quality"],
                "type": "vip_elevenlabs",
                "is_downloaded": True,
                "sample_url": f"/demos/{el_key}_sample.mp3"
            })

    # 3. Custom uploaded voices
    custom_list = tts_engine.get_custom_voices()
    for cv in custom_list:
        is_el = bool(cv.get("eleven_voice_id"))
        results.append(
            {
                "key": cv["id"],
                "label": f"{cv['name']} [Clone Ultra-HD]" if is_el else f"{cv['name']} (Personalizada)",
                "gender": cv["gender"],
                "quality": "ElevenLabs Multilingual v2" if is_el else f"Clone ({cv.get('pitch_hz', 0)} Hz)",
                "type": "custom",
                "is_downloaded": True,
                "sample_url": cv.get("sample_url", ""),
                "duration": cv.get("duration", 0),
                "eleven_voice_id": cv.get("eleven_voice_id"),
            }
        )
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


@app.post("/api/synthesize")
def synthesize(
    req: SynthesizeRequest,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None)
):
    normalized_text = req.text.replace("\r\n", "\n").strip()
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
        import time
        start_time = time.time()
        
        eleven_voice_id = None
        fb_voice = "dii"
        fb_semi = 0.0

        if req.voice.startswith("el_") and req.voice in ELEVENLABS_VOICES and ELEVENLABS_API_KEY:
            el_voice = ELEVENLABS_VOICES[req.voice]
            eleven_voice_id = el_voice["voice_id"]
            fb_voice = el_voice.get("fallback_voice", "dii")
            fb_semi = el_voice.get("fallback_semitones", 0.0)
        elif req.voice in ["su", "custom_su"] and ELEVENLABS_API_KEY:
            eleven_voice_id = "qE4bxNbWYcb8hs72HJEO"
            fb_voice = "su"
            fb_semi = 0.0
        elif req.voice.startswith("custom_") and ELEVENLABS_API_KEY:
            c_meta = tts_engine.load_custom_voices_metadata()
            if req.voice in c_meta and c_meta[req.voice].get("eleven_voice_id"):
                eleven_voice_id = c_meta[req.voice]["eleven_voice_id"]
                fb_voice = c_meta[req.voice].get("base_voice", "dii")
                fb_semi = c_meta[req.voice].get("semitones_shift", 0.0)

        if eleven_voice_id and ELEVENLABS_API_KEY:
            voice_id = eleven_voice_id
            timestamp = int(time.time() * 1000)
            mp3_filename = f"synth_{req.voice}_{timestamp}.mp3"
            wav_filename = f"synth_{req.voice}_{timestamp}.wav"
            mp3_path = os.path.join(OUTPUTS_DIR, mp3_filename)
            wav_path = os.path.join(OUTPUTS_DIR, wav_filename)

            try:
                synthesize_elevenlabs(voice_id, req.text, mp3_path)
                # Converte para WAV também para waveform visual
                try:
                    cmd = ["ffmpeg", "-y", "-i", mp3_path, "-f", "wav", wav_path]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                except Exception:
                    pass
            except Exception as el_err:
                print(f"[ElevenLabs Quota/API Warning - Usando Motor Neural Local Garantido]: {el_err}")
                fb_voice = el_voice.get("fallback_voice", "dii")
                fb_semi = el_voice.get("fallback_semitones", 0.0)
                fb_res = tts_engine.synthesize_text(
                    text=req.text,
                    voice_key=fb_voice,
                    speed=req.speed,
                    num_threads=req.threads,
                )
                os.replace(fb_res["file_path"], wav_path)
                if abs(fb_semi) > 0.15:
                    tts_engine.pitch_shift_ffmpeg(wav_path, fb_semi, fb_res.get("sample_rate", 22050))
                convert_wav_to_mp3(wav_path, mp3_path)

            # Aplica Trilha Sonora de Fundo (BGM) se selecionada
            if req.bgm and req.bgm != "none" and req.bgm in BGM_TRACKS and os.path.exists(wav_path):
                bgm_file = os.path.join(STATIC_DIR, "bgm", BGM_TRACKS[req.bgm]["file"])
                if os.path.exists(bgm_file):
                    if mix_audio_with_bgm(wav_path, bgm_file, req.bgm_volume or 0.15):
                        try:
                            cmd_mp3 = ["ffmpeg", "-y", "-i", wav_path, "-b:a", "192k", mp3_path]
                            subprocess.run(cmd_mp3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                        except Exception:
                            pass

            elapsed = round(time.time() - start_time, 2)
            est_duration = 2.0
            if os.path.exists(wav_path):
                try:
                    import soundfile as sf
                    est_duration = round(sf.info(wav_path).duration, 2)
                except Exception:
                    word_count = len(req.text.split())
                    est_duration = max(round(word_count / 2.6, 1), 1.5)

            result = {
                "filename": wav_filename if os.path.exists(wav_path) else mp3_filename,
                "duration_seconds": est_duration,
                "elapsed_seconds": elapsed,
            }
        else:
            result = tts_engine.synthesize_text(
                text=req.text,
                voice_key=req.voice,
                speed=req.speed,
                num_threads=req.threads,
            )
            wav_filename = result["filename"]
            mp3_filename = wav_filename.replace(".wav", ".mp3")
            wav_path = os.path.join(OUTPUTS_DIR, wav_filename)
            mp3_path = os.path.join(OUTPUTS_DIR, mp3_filename)

            # Aplica Trilha Sonora de Fundo (BGM) se selecionada antes de converter para MP3
            if req.bgm and req.bgm != "none" and req.bgm in BGM_TRACKS and os.path.exists(wav_path):
                bgm_file = os.path.join(STATIC_DIR, "bgm", BGM_TRACKS[req.bgm]["file"])
                if os.path.exists(bgm_file):
                    mix_audio_with_bgm(wav_path, bgm_file, req.bgm_volume or 0.15)

            # Dispara conversão MP3 em background (não bloqueia a resposta para o usuário)
            if os.path.exists(wav_path):
                background_tasks.add_task(convert_wav_to_mp3, wav_path, mp3_path)

        remaining_credits = profile.get("credits", 1) if profile else 999

        # Atualiza créditos e salva histórico no Supabase
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
                    size_kb = round(os.path.getsize(wav_path) / 1024, 1) if os.path.exists(wav_path) else 0
                    title = req.text.strip().replace("\n", " ")[:60]
                    supabase_admin.table("audio_generations").insert({
                        "user_id": user.id,
                        "title": title,
                        "text_prompt": req.text,
                        "voice_key": req.voice,
                        "speed": req.speed,
                        "duration_seconds": round(result["duration_seconds"], 2),
                        "audio_url_wav": f"/outputs/{wav_filename}",
                        "audio_url_mp3": f"/outputs/{mp3_filename}",
                        "file_size_kb": size_kb
                    }).execute()
                except Exception as ex:
                    print(f"[Supabase Generation Save Error] {ex}")

        active_filename = wav_filename if os.path.exists(wav_path) else mp3_filename
        active_url = f"/outputs/{active_filename}"

        return {
            "success": True,
            "filename": active_filename,
            "url": active_url,
            "mp3_url": f"/outputs/{mp3_filename}",
            "duration": round(result["duration_seconds"], 2),
            "elapsed": round(result["elapsed_seconds"], 2),
            "speed_factor": round(result["duration_seconds"] / max(result["elapsed_seconds"], 0.001), 1),
            "voice": req.voice,
            "text": req.text,
            "credits": remaining_credits,
            "saved_history": bool(req.save_history),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/outputs/{filename}")
def get_output_file(filename: str):
    file_path = os.path.join(OUTPUTS_DIR, filename)

    # Se solicitou MP3 e o MP3 ainda não existe, converte do WAV equivalente
    if filename.endswith(".mp3"):
        wav_path = os.path.join(OUTPUTS_DIR, filename[:-4] + ".wav")
        if not os.path.exists(file_path) and os.path.exists(wav_path):
            try:
                convert_wav_to_mp3(wav_path, file_path)
            except Exception as e:
                print(f"[MP3 conversion error] {e}")
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="audio/mpeg", filename=filename)

    # Se solicitou WAV e o WAV ainda não existe, converte do MP3 equivalente
    if filename.endswith(".wav"):
        mp3_path = os.path.join(OUTPUTS_DIR, filename[:-4] + ".mp3")
        if not os.path.exists(file_path) and os.path.exists(mp3_path):
            try:
                cmd = ["ffmpeg", "-y", "-i", mp3_path, "-f", "wav", file_path]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except Exception as e:
                print(f"[WAV conversion error] {e}")
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="audio/wav", filename=filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo de áudio não encontrado")

    media_type = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
    return FileResponse(file_path, media_type=media_type, filename=filename)


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

    # Fallback para histórico local em disco (se deslogado ou local dev)
    files = glob.glob(os.path.join(OUTPUTS_DIR, "*.wav"))
    files.sort(key=os.path.getmtime, reverse=True)
    history = []
    for f in files[:20]:
        fname = os.path.basename(f)
        size_kb = round(os.path.getsize(f) / 1024, 1)
        history.append({
            "id": fname,
            "title": fname,
            "filename": fname,
            "url": f"/outputs/{fname}",
            "mp3_url": f"/outputs/{fname.replace('.wav', '.mp3')}",
            "voice": "standard",
            "size_kb": size_kb,
            "created_at": os.path.getmtime(f),
        })
    return history


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
