# Clonavoz AI Backend - Dockerfile para VPS Hostinger
FROM python:3.11-slim

# Evita buffering no stdout e stderr
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Instala dependências do sistema necessárias para áudio (FFmpeg, libs C++ e Node.js 22 LTS para SDK @google/genai)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    curl \
    ca-certificates \
    gnupg \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia dependências primeiro para aproveitar cache do Docker
COPY requirements.txt .
COPY package.json .
COPY package-lock.json* ./

# Instala pacotes Python e Node.js (@google/genai)
RUN pip install --no-cache-dir -r requirements.txt \
    && npm install --omit=dev

# Copia o código fonte da aplicação
COPY server.py .
COPY tts_engine.py .
COPY text_normalizer.py .
COPY gemini_tts_service.mjs .
COPY scripts scripts
COPY public public
COPY static static

# Cria os diretórios necessários
RUN mkdir -p models custom_voices outputs outputs/cache public/voice-samples

# Expõe a porta 8000 da API
EXPOSE 8000

# Executa o servidor FastAPI com Uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
