#!/bin/bash
# ========================================================
# Script de Deploy Automático - Clonavoz AI na Hostinger VPS
# ========================================================
set -e

echo "🚀 Iniciando configuração do Clonavoz AI no Ubuntu..."

# 1. Atualiza repositórios do sistema
sudo apt-get update && sudo apt-get upgrade -y

# 2. Instala dependências básicas, FFmpeg e Docker se não existirem
sudo apt-get install -y ffmpeg curl git python3 python3-pip python3-venv

if ! command -v docker &> /dev/null; then
    echo "🐳 Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    sudo apt-get install -y docker-compose-plugin
fi

# 3. Garante permissões de pastas
mkdir -p models custom_voices outputs static

echo "✅ Servidor preparado com sucesso!"
echo "Para rodar com Docker: docker compose up -d --build"
echo "Para verificar os logs: docker compose logs -f"
