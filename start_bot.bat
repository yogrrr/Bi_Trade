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

echo [1/3] Verificando Poetry...
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

echo [2/3] Verificando dependencias...
if not exist "poetry.lock" (
    echo Instalando dependencias...
    poetry lock
    poetry install
)
echo OK - Dependencias prontas
echo.

echo [3/3] Iniciando API do Bot...
echo.
echo ========================================
echo   API iniciada com sucesso!
echo ========================================
echo.
echo API rodando em: http://localhost:8000
echo.
echo Acesse a interface web em:
echo https://3000-ieprctzfnse2hx9pa9iob-66b9b815.manusvm.computer
echo.
echo Pressione Ctrl+C para parar o bot
echo.

poetry run python -m app.web.api

pause
