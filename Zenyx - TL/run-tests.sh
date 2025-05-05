#!/bin/bash

# Script para executar testes automatizados

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências de teste
pip install pytest pytest-asyncio pytest-cov

# Executar testes
echo "Executando testes unitários..."
pytest tests/ -v --cov=. --cov-report=html

# Verificar código
echo "Verificando código com flake8..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Verificar tipagem
echo "Verificando tipagem com mypy..."
mypy . --ignore-missing-imports

echo "Testes concluídos!"