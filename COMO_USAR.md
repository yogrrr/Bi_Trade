# 🚀 Como Usar o Binary Trading Bot

## 📦 Instalação (Primeira Vez)

### 1. Instalar Python
- Baixe em: https://www.python.org/downloads/
- **Importante:** Marque "Add Python to PATH" durante a instalação

### 2. Instalar Git
- Baixe em: https://git-scm.com/download/win
- Ou via winget: `winget install --id Git.Git -e`

### 3. Instalar Poetry
Abra o PowerShell e execute:
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### 4. Clonar o Repositório
```powershell
cd C:\Users\$env:USERNAME\Desktop
git clone https://github.com/yogrrr/Bi_Trade.git
cd Bi_Trade
```

### 5. Instalar Dependências
```powershell
poetry lock
poetry install
```

---

## 🎯 Uso Diário (Forma Fácil)

### Opção 1: Duplo Clique (Recomendado)
1. Vá até a pasta `Bi_Trade`
2. Dê **duplo clique** em `start_bot.bat`
3. Aguarde a API iniciar
4. Acesse a interface web no navegador

### Opção 2: PowerShell
1. Clique com botão direito em `start_bot.ps1`
2. Selecione "Executar com PowerShell"

---

## 🌐 Acessar a Interface Web

Após iniciar o bot, abra o navegador e acesse:

**https://3000-ieprctzfnse2hx9pa9iob-66b9b815.manusvm.computer**

A interface permite:
- ✅ Executar backtests
- ✅ Iniciar bot em modo demo/live
- ✅ Configurar estratégias
- ✅ Ver relatórios e métricas

---

## 🛑 Como Parar o Bot

Pressione `Ctrl + C` na janela do PowerShell/CMD onde o bot está rodando.

---

## 🔧 Solução de Problemas

### "Poetry não encontrado"
Execute no PowerShell:
```powershell
$env:Path += ";$env:APPDATA\Python\Scripts"
```

### "ModuleNotFoundError"
Execute:
```powershell
poetry lock
poetry install
```

### "Git não encontrado"
Instale o Git: https://git-scm.com/download/win

---

## 📖 Documentação Completa

Veja o arquivo `README.md` para documentação técnica completa.

---

## ⚠️ Aviso Importante

Este é um projeto **educacional**. Opções binárias são de **alto risco**.

**Sempre teste em modo demo antes de qualquer operação real.**
