@echo off
REM Binary Trading Bot - Script de Inicialização Automática
REM Execute este arquivo para iniciar a API do bot

title Binary Trading Bot
color 0A

echo ========================================
echo   Binary Trading Bot - Inicializando
echo ========================================
echo.

REM Adicionar Poetry ao PATH
set PATH=%PATH%;%APPDATA%\Python\Scripts

REM Ir para o diretório do script
cd /d "%~dp0"

echo [1/5] Verificando Poetry...
poetry --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Poetry nao encontrado!
    echo.
    echo Instale o Poetry primeiro:
    echo ^(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing^).Content ^| python -
    echo.
    pause
    exit /b 1
)
echo OK - Poetry encontrado
echo.

echo [2/5] Verificando Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Git nao encontrado - pulando verificacao de atualizacoes
    goto skip_update
)
echo OK - Git encontrado
echo.

echo [3/5] Verificando atualizacoes...
git fetch origin main >nul 2>&1

REM Comparar commits local e remoto
for /f %%i in ('git rev-parse HEAD') do set LOCAL_COMMIT=%%i
for /f %%i in ('git rev-parse origin/main') do set REMOTE_COMMIT=%%i

if "%LOCAL_COMMIT%" NEQ "%REMOTE_COMMIT%" (
    echo [AVISO] Atualizacoes disponiveis no GitHub!
    echo.
    set /p UPDATE="Deseja baixar as atualizacoes? (S/N): "
    
    if /i "%UPDATE%"=="S" (
        echo Baixando atualizacoes...
        git pull origin main
        echo OK - Projeto atualizado!
        echo.
        echo Atualizando dependencias...
        poetry lock --no-update
        poetry install
    ) else (
        echo OK - Continuando com versao local
    )
) else (
    echo OK - Projeto esta atualizado
)
echo.

:skip_update

echo [4/5] Verificando dependencias...
if not exist "poetry.lock" (
    echo Instalando dependencias...
    poetry lock
    poetry install
) else (
    echo OK - Dependencias prontas
)
echo.

echo [5/5] Iniciando API do Bot...
echo.
echo ========================================
echo   API iniciada com sucesso!
echo ========================================
echo.
echo API rodando em: http://localhost:8000
echo Documentacao: http://localhost:8000/docs
echo.
echo Acesse a interface web em:
echo https://3000-ieprctzfnse2hx9pa9iob-66b9b815.manusvm.computer
echo.
echo Pressione Ctrl+C para parar o bot
echo.

poetry run python -m app.web.api

pause
