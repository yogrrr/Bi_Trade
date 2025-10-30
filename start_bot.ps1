# Binary Trading Bot - Script de Inicialização Automática
# Execute este script para iniciar a API do bot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Binary Trading Bot - Inicializando" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Adicionar Poetry ao PATH
Write-Host "[1/5] Configurando Poetry..." -ForegroundColor Yellow
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
Write-Host "[2/5] Acessando diretório do projeto..." -ForegroundColor Yellow
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath
Write-Host "✓ Diretório: $scriptPath" -ForegroundColor Green

Write-Host ""

# Verificar atualizações do GitHub
Write-Host "[3/5] Verificando atualizações..." -ForegroundColor Yellow
try {
    # Buscar atualizações do repositório remoto
    git fetch origin main 2>$null
    
    # Verificar se há commits novos
    $localCommit = git rev-parse HEAD
    $remoteCommit = git rev-parse origin/main
    
    if ($localCommit -ne $remoteCommit) {
        Write-Host "⚠ Atualizações disponíveis no GitHub!" -ForegroundColor Yellow
        Write-Host ""
        $update = Read-Host "Deseja baixar as atualizações? (S/N)"
        
        if ($update -eq "S" -or $update -eq "s") {
            Write-Host "Baixando atualizações..." -ForegroundColor Yellow
            git pull origin main
            Write-Host "✓ Projeto atualizado!" -ForegroundColor Green
            
            # Atualizar dependências após pull
            Write-Host "Atualizando dependências..." -ForegroundColor Yellow
            poetry lock --no-update
            poetry install
        } else {
            Write-Host "✓ Continuando com versão local" -ForegroundColor Green
        }
    } else {
        Write-Host "✓ Projeto está atualizado" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ Não foi possível verificar atualizações (Git não configurado ou sem conexão)" -ForegroundColor Yellow
}

Write-Host ""

# Verificar se precisa atualizar dependências
Write-Host "[4/5] Verificando dependências..." -ForegroundColor Yellow
if (Test-Path "poetry.lock") {
    # Verificar se pyproject.toml foi modificado
    $needsUpdate = $false
    try {
        poetry check 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            $needsUpdate = $true
        }
    } catch {
        $needsUpdate = $true
    }
    
    if ($needsUpdate) {
        Write-Host "Atualizando dependências..." -ForegroundColor Yellow
        poetry lock --no-update
        poetry install
        Write-Host "✓ Dependências atualizadas" -ForegroundColor Green
    } else {
        Write-Host "✓ Dependências já instaladas" -ForegroundColor Green
    }
} else {
    Write-Host "Instalando dependências (pode demorar alguns minutos)..." -ForegroundColor Yellow
    poetry lock
    poetry install
    Write-Host "✓ Dependências instaladas" -ForegroundColor Green
}

Write-Host ""

# Iniciar a API
Write-Host "[5/5] Iniciando API do Bot..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  API iniciada com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API rodando em: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Documentação: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Acesse a interface web em:" -ForegroundColor Cyan
Write-Host "https://3000-ieprctzfnse2hx9pa9iob-66b9b815.manusvm.computer" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o bot" -ForegroundColor Yellow
Write-Host ""

# Executar a API
poetry run python -m app.web.api
