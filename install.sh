#!/bin/bash

# Script de instalação rápida do Binary Trading Bot

echo "🤖 Binary Trading Bot - Instalação Rápida"
echo "=========================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.11 ou superior."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION encontrado"

# Verificar Poetry
if ! command -v poetry &> /dev/null; then
    echo "📦 Instalando Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Adicionar ao PATH
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v poetry &> /dev/null; then
        echo "❌ Erro ao instalar Poetry. Instale manualmente: https://python-poetry.org/docs/#installation"
        exit 1
    fi
fi

echo "✅ Poetry encontrado"

# Instalar dependências
echo ""
echo "📦 Instalando dependências..."
poetry install

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo ""
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
fi

# Criar diretórios necessários
mkdir -p logs out

echo ""
echo "✅ Instalação concluída com sucesso!"
echo ""
echo "🚀 Próximos passos:"
echo ""
echo "1. Execute um backtest:"
echo "   poetry run python -m app backtest"
echo ""
echo "2. Ou inicie o modo demo:"
echo "   poetry run python -m app live --demo"
echo ""
echo "3. Veja o relatório gerado em: out/report.html"
echo ""
echo "📖 Leia o README.md para mais informações"
echo ""
