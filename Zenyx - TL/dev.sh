#!/bin/bash

# Script de desenvolvimento com hot reload

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Bot Zenyx - Modo Desenvolvimento${NC}"

# Verificar ambiente virtual
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install watchdog
else
    source venv/bin/activate
fi

# Usar arquivo de configuração de desenvolvimento
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
else
    export $(cat .env | grep -v '^#' | xargs)
fi

# Executar com watchdog para hot reload
echo -e "${YELLOW}Iniciando em modo desenvolvimento com hot reload...${NC}"
watchmedo auto-restart \
    --patterns="*.py" \
    --recursive \
    --ignore-patterns="*/.*" \
    -- python main.py