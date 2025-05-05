#!/bin/bash

# Script de teste local para Bot Zenyx (sem Docker)

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Bot Zenyx - Teste Local${NC}"
echo "------------------------"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 não encontrado!${NC}"
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}Python version: ${PYTHON_VERSION}${NC}"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Criando ambiente virtual...${NC}"
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo -e "${YELLOW}Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Atualizar pip
echo -e "${YELLOW}Atualizando pip...${NC}"
pip install --upgrade pip

# Instalar dependências
echo -e "${YELLOW}Instalando dependências...${NC}"
pip install -r requirements.txt

# Verificar se .env existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}Criando arquivo .env...${NC}"
    cp .env.example .env
    echo -e "${RED}Por favor, edite o arquivo .env com suas configurações!${NC}"
    exit 1
fi

# Criar diretórios necessários
echo -e "${YELLOW}Criando diretórios...${NC}"
mkdir -p data relatorios logs

# Iniciar Redis local (se disponível)
if command -v redis-server &> /dev/null; then
    echo -e "${YELLOW}Iniciando Redis local...${NC}"
    redis-server --daemonize yes
else
    echo -e "${YELLOW}Redis não encontrado. Usando fallback para arquivo.${NC}"
fi

# Iniciar bot
echo -e "${GREEN}Iniciando Bot Zenyx...${NC}"
python main.py