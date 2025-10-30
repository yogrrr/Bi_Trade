# Binary Trading Bot - Script de Inicialização Automática
# Execute este script para iniciar a API do bot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Binary Trading Bot - Inicializando" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Adicionar Poetry ao PATH
Write-Host "[1/4] Configurando Poetry..." -ForegroundColor Yellow
$env:Path += ";$env:APPDATA\Python\Scripts"

# Verificar se Poetry está disponível
try {
    $poetryVersion = poetry --version
    Write-Host "✓ Poetry encontrado: $poetryVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Erro: Poetry não encontrado!" -ForegroundColor Red
    Write-Host "Execute: (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""

# Ir para o diretório do projeto
Write-Host "[2/4] Acessando diretório do projeto..." -ForegroundColor Yellow
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath
Write-Host "✓ Diretório: $scriptPath" -ForegroundColor Green

Write-Host ""

# Verificar se precisa atualizar dependências
Write-Host "[3/4] Verificando dependências..." -ForegroundColor Yellow
if (Test-Path "poetry.lock") {
    Write-Host "✓ Dependências já instaladas" -ForegroundColor Green
} else {
    Write-Host "Instalando dependências (pode demorar alguns minutos)..." -ForegroundColor Yellow
    poetry lock
    poetry install
    Write-Host "✓ Dependências instaladas" -ForegroundColor Green
}

Write-Host ""

# Iniciar a API
Write-Host "[4/4] Iniciando API do Bot..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  API iniciada com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API rodando em: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Acesse a interface web em:" -ForegroundColor Cyan
Write-Host "https://3000-ieprctzfnse2hx9pa9iob-66b9b815.manusvm.computer" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o bot" -ForegroundColor Yellow
Write-Host ""

# Executar a API
poetry run python -m app.web.api
