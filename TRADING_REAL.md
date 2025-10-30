# 🚀 Guia de Trading Real

Este guia explica como usar o bot com **dados reais** e **brokers reais**.

## ⚠️ AVISOS IMPORTANTES

1. **SEMPRE comece em modo DEMO**
2. **NUNCA use dinheiro que você não pode perder**
3. **Teste extensivamente antes de usar dinheiro real**
4. **Opções binárias são de alto risco**
5. **Verifique a legalidade na sua jurisdição**

---

## 📊 Usando Dados Reais

### Opção 1: Yahoo Finance (Gratuito, Recomendado)

1. **Configurar** `config.yaml`:
```yaml
data:
  source: "yfinance"
```

2. **Símbolos disponíveis**:
   - Forex: `EURUSD=X`, `GBPUSD=X`, `USDJPY=X`
   - Ações: `AAPL`, `GOOGL`, `MSFT`
   - Crypto: `BTC-USD`, `ETH-USD`

3. **Executar backtest**:
```bash
poetry run python -m app backtest
```

### Opção 2: Alpha Vantage (Requer API Key)

1. **Obter API key gratuita**: https://www.alphavantage.co/support/#api-key

2. **Configurar** `config.yaml`:
```yaml
data:
  source: "alphavantage"
  alphavantage_api_key: "SUA_API_KEY_AQUI"
```

3. **Executar backtest**:
```bash
poetry run python -m app backtest
```

---

## 🤖 Usando Broker Real

### IQ Option (Implementado)

#### 1. Instalar Biblioteca

```bash
pip install iqoptionapi
```

#### 2. Configurar Conta DEMO

Edite `config.yaml`:

```yaml
broker:
  type: "iqoption"
  demo: true  # SEMPRE comece com demo!
  email: "seu_email@exemplo.com"
  password: "sua_senha"
```

**⚠️ SEGURANÇA:** Nunca commite senhas no Git! Use variáveis de ambiente:

```bash
# Windows PowerShell
$env:IQOPTION_EMAIL = "seu_email@exemplo.com"
$env:IQOPTION_PASSWORD = "sua_senha"

# Linux/Mac
export IQOPTION_EMAIL="seu_email@exemplo.com"
export IQOPTION_PASSWORD="sua_senha"
```

#### 3. Executar em Modo DEMO

```bash
poetry run python -m app live --demo
```

#### 4. Testar por SEMANAS/MESES

- Mínimo 500 trades em demo
- Win rate consistente > 55%
- Drawdown < 20%
- Documentar TODOS os resultados

#### 5. Migrar para Conta REAL (Apenas se tiver sucesso em demo)

**⚠️ CUIDADO EXTREMO!**

Edite `config.yaml`:

```yaml
broker:
  type: "iqoption"
  demo: false  # ATENÇÃO: Modo REAL!
  email: "seu_email@exemplo.com"
  password: "sua_senha"

risk:
  risk_per_trade: 0.005  # Reduza para 0.5% em real!
  max_daily_loss: 0.01   # Stop loss diário: 1%
  max_daily_profit: 0.02  # Take profit: 2%
```

Execute:

```bash
poetry run python -m app live
```

O bot vai pedir confirmação:

```
⚠️  ATENÇÃO: Modo REAL ativado! Você usará dinheiro real!
Digite 'CONFIRMO' para continuar:
```

---

## 📋 Checklist Antes de Usar Dinheiro Real

### Testes Obrigatórios

- [ ] Backtest com dados reais (mínimo 6 meses)
- [ ] Win rate > 55% consistente
- [ ] Expectância positiva comprovada
- [ ] Drawdown máximo < 20%
- [ ] Teste em demo por mínimo 3 meses
- [ ] Mínimo 500 trades em demo
- [ ] Documentação completa de todos os trades
- [ ] Análise de diferentes condições de mercado

### Configuração de Segurança

- [ ] Stake reduzido (0.5% ou menos)
- [ ] Stop loss diário configurado (1-2%)
- [ ] Take profit diário configurado (2-3%)
- [ ] Alertas de monitoramento ativos
- [ ] Backup de configurações
- [ ] Logs de auditoria habilitados

### Legal e Financeiro

- [ ] Verificar legalidade na sua jurisdição
- [ ] Consultar contador sobre impostos
- [ ] Ler TODOS os termos do broker
- [ ] Entender riscos de perda total
- [ ] Capital que PODE perder (não é dinheiro de contas/empréstimos)

### Preparação Psicológica

- [ ] Aceitar que pode perder tudo
- [ ] Não operar com emoção
- [ ] Seguir o plano de trading rigorosamente
- [ ] Parar se atingir limites diários
- [ ] Não aumentar stake após perdas

---

## 🔐 Segurança de Credenciais

### Método 1: Variáveis de Ambiente (Recomendado)

```bash
# Windows
$env:IQOPTION_EMAIL = "email@exemplo.com"
$env:IQOPTION_PASSWORD = "senha"

# Linux/Mac
export IQOPTION_EMAIL="email@exemplo.com"
export IQOPTION_PASSWORD="senha"
```

### Método 2: Arquivo .env (Não commitar!)

Crie `.env` na raiz do projeto:

```
IQOPTION_EMAIL=email@exemplo.com
IQOPTION_PASSWORD=senha
```

Adicione ao `.gitignore`:

```
.env
```

### Método 3: Prompt Interativo

Deixe vazio no `config.yaml` e o bot vai pedir:

```yaml
broker:
  email: ""
  password: ""
```

---

## 📊 Monitoramento

### Logs

Todos os trades são registrados em:

```
logs/
  trading_YYYY-MM-DD.log
  audit_YYYY-MM-DD.json
```

### Relatórios

Relatórios HTML são gerados em:

```
out/
  backtest_YYYY-MM-DD_HH-MM-SS.html
```

### Alertas

Configure alertas para:

- Drawdown > 10%
- Perda diária > limite
- Erro de conexão com broker
- Win rate < 50% nas últimas 20 trades

---

## 🆘 Problemas Comuns

### "Não foi possível conectar ao broker"

- Verifique email e senha
- Confirme que a conta existe
- Tente fazer login manual no site do broker
- Verifique conexão com internet

### "Nenhum dado encontrado"

- Verifique símbolo (ex: `EURUSD=X` para forex)
- Confirme que o mercado está aberto
- Tente símbolo alternativo

### "Ordem rejeitada"

- Verifique saldo suficiente
- Confirme que o ativo está disponível
- Verifique horário de funcionamento
- Reduza o valor do stake

---

## 📚 Recursos Adicionais

### Documentação de APIs

- **IQ Option**: https://github.com/Lu-Yi-Hsun/iqoptionapi
- **Yahoo Finance**: https://pypi.org/project/yfinance/
- **Alpha Vantage**: https://www.alphavantage.co/documentation/

### Comunidade

- Reporte bugs no GitHub
- Compartilhe resultados (sem revelar estratégias)
- Contribua com melhorias

---

## ⚖️ Disclaimer

**Este software é fornecido "como está", sem garantias de qualquer tipo.**

- Você é 100% responsável por suas decisões de trading
- Os desenvolvedores NÃO se responsabilizam por perdas
- Trading de opções binárias é de alto risco
- Resultados passados não garantem resultados futuros
- Use por sua conta e risco

**SEMPRE comece em modo DEMO. NUNCA use dinheiro que não pode perder.**
