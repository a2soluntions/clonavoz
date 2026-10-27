#!/bin/bash
# ========================================================
# Clonavoz - Script de Sincronização e Atualização Automática
# Roda na VPS de forma segura (Zero-Trust Pull)
# ========================================================
cd /app || exit 1

# 1. Busca novidades no GitHub silenciosamente
git fetch origin main --quiet 2>/dev/null

LOCAL=$(git rev-parse HEAD 2>/dev/null)
REMOTE=$(git rev-parse origin/main 2>/dev/null)

# 2. Se a versão local for diferente da do GitHub, atualiza
if [ -n "$LOCAL" ] && [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 Novo código detectado! Atualizando..."
    git stash --quiet
    git pull origin main --quiet
    docker compose restart
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Clonavoz atualizado com sucesso!"
fi
