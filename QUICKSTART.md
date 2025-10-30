# 🚀 Guia Rápido de Início

## Instalação em 3 Passos

### 1️⃣ Execute o instalador

```bash
./install.sh
```

Isso irá:
- Verificar Python 3.11+
- Instalar Poetry (se necessário)
- Instalar todas as dependências
- Configurar o ambiente

### 2️⃣ Execute um backtest

```bash
poetry run python -m app backtest
```

Isso irá:
- Gerar dados sintéticos para demonstração
- Executar backtest com as 3 estratégias
- Treinar o modelo de IA online
- Gerar relatório HTML em `out/report.html`

### 3️⃣ Veja os resultados

Abra o arquivo `out/report.html` no navegador para ver:
- 📈 Curva de equity
- 📉 Gráfico de drawdown
- 📊 Métricas de performance
- 📋 Lista de trades

## Modo Demo (Paper Trading)

Para testar em tempo real sem dinheiro:

```bash
poetry run python -m app live --demo
```

Pressione `Ctrl+C` para parar.

## Próximos Passos

1. **Personalize as configurações** em `config.yaml`
2. **Ajuste os parâmetros** das estratégias
3. **Teste diferentes símbolos** e timeframes
4. **Analise os resultados** e otimize

## Comandos Úteis

```bash
# Backtest com símbolo específico
poetry run python -m app backtest --symbol GBPUSD --timeframe 5m

# Demo com configurações personalizadas
poetry run python -m app live --demo --expiry 300

# Executar testes
poetry run pytest

# Ver versão
poetry run python -m app version
```

## ⚠️ Importante

- **NUNCA** opere com dinheiro real sem testar extensivamente em demo
- Opções binárias são de **alto risco**
- Este é um projeto **educacional**
- Leia o **README.md** completo antes de usar

## 🆘 Precisa de Ajuda?

Veja o **README.md** para:
- Explicação detalhada das métricas
- Como adicionar novas estratégias
- Solução de problemas comuns
- Avisos de risco importantes

---

**Boa sorte e bons trades! 🎯**
