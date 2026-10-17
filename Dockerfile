# Clonavoz AI Backend - Dockerfile para VPS Hostinger
FROM python:3.11-slim

# Evita buffering no stdout e stderr
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Instala dependências do sistema necessárias para áudio (FFmpeg e libs de C++)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia dependências primeiro para aproveitar cache do Docker
COPY requirements.txt .

# Instala pacotes Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte da aplicação
COPY server.py .
COPY tts_engine.py .
COPY static static

# Cria os diretórios necessários
RUN mkdir -p models custom_voices outputs

# Expõe a porta 8000 da API
EXPOSE 8000

# Executa o servidor FastAPI com Uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
