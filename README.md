# 🤖 Binary Trading Bot

Robô de trading de **opções binárias** com **IA** e **aprendizado online**. O sistema aprende continuamente com os próprios resultados e opera apenas quando o valor esperado é positivo.

## 🎯 Características Principais

- **IA com Aprendizado Online**: Modelo atualizado após cada trade (River ou scikit-learn)
- **Decisão Inteligente**: Opera apenas se `P(win) > 1/(1+payout) + margem_segurança`
- **Três Estratégias Modulares**:
  - **Tendência**: Cruzamento EMA(9/21) + filtro ATR
  - **Reversão**: RSI(2) extremos (<5 ou >95)
  - **Breakout**: Canal de Donchian(20)
- **Bandit Contextual**: Seleciona automaticamente a melhor estratégia por contexto
- **Gestão de Risco Rigorosa**:
  - Stake fixo de 0,5-1% do saldo (sem martingale!)
  - Limites diários em percentual (compatível com valores antigos em R):
    - Stop loss diário: -2% (insira -2 ou -0.02)
    - Take profit diário: +3% (insira 3 ou 0.03)
  - Ignora payouts < 80%
- **Backtest Completo**: Walk-forward com payout variável, latência e slippage simulados
- **Modo Live/Demo**: Paper trading com broker mock incluso
- **Relatórios HTML**: Métricas detalhadas, gráficos interativos e análise de performance

## 📋 Requisitos

- Python 3.11+
- Poetry (gerenciador de dependências)

## 🚀 Instalação Rápida

### 1. Clone o repositório (ou extraia o ZIP)

```bash
cd binary-trading-bot
```

### 2. Instale as dependências com Poetry

```bash
# Instalar Poetry (se ainda não tiver)
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependências do projeto
poetry install
```

### 3. Configure o ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações (opcional para demo)
nano config.yaml
```

## 🎮 Uso

### Backtest

Execute um backtest completo com relatório HTML:

```bash
poetry run python -m app backtest
```

O relatório será gerado em `out/report.html` com:
- Curva de equity
- Gráfico de drawdown
- Métricas detalhadas (win rate, expectancy, Brier score)
- Tabela dos últimos trades

**Opções disponíveis:**

```bash
poetry run python -m app backtest --symbol EURUSD --timeframe 1m --expiry 120 --report out/report.html
```

### Live Demo (Paper Trading)

Execute o robô em modo demo (sem dinheiro real):

```bash
poetry run python -m app live --demo
```

O bot irá:
1. Carregar dados em tempo real (simulados)
2. Calcular indicadores técnicos
3. Gerar sinais das estratégias
4. Predizer P(win) com IA
5. Operar apenas se expectativa for positiva
6. Atualizar o modelo após cada trade

**Opções disponíveis:**

```bash
poetry run python -m app live --demo --symbol EURUSD --timeframe 1m --expiry 120
```

### Live Real (⚠️ Dinheiro Real)

```bash
poetry run python -m app live --broker your_broker
```

**ATENÇÃO**: Modo real ainda não implementado. Use sempre `--demo` primeiro!

## ⚙️ Configuração

### config.yaml

Todas as configurações do robô estão em `config.yaml`:

```yaml
# Símbolo e timeframe
symbol: "EURUSD"
timeframe: "1m"
expiry: 120  # segundos

# Gestão de risco
risk:
  risk_per_trade: 0.01  # 1% do saldo por trade
  daily_loss_limit: -2  # Aceita -2 (=> -2%) ou -0.02
  daily_profit_target: 3  # Aceita 3 (=> +3%) ou 0.03
  min_payout: 0.80  # Ignorar payouts < 80%
  safety_margin: 0.02  # Margem adicional sobre breakeven

# Estratégias (habilitar/desabilitar)
strategies:
  trend:
    enabled: true
    ema_fast: 9
    ema_slow: 21
  meanrev:
    enabled: true
    rsi_period: 2
  breakout:
    enabled: true
    donchian_period: 20

# Modelo de IA
model:
  type: "river"  # river ou sklearn
  update_online: true
  calibration: "isotonic"  # isotonic, platt ou null

# Bandit contextual
bandit:
  enabled: true
  epsilon: 0.1  # Exploração vs exploitação
```

### .env

Variáveis de ambiente para broker real (não necessário para demo):

```bash
BROKER_API_KEY=your_api_key_here
BROKER_API_SECRET=your_api_secret_here
TRADING_MODE=demo  # demo ou live
```

## 📊 Métricas Explicadas

### Win Rate
Percentual de trades vencedores. Para opções binárias com payout de 85%, você precisa de **win rate > 54%** para ser lucrativo.

### Expectancy (Expectância)
Lucro esperado por trade em múltiplos de R (risco). Fórmula:
```
E = (P(win) × Payout) - (P(loss) × 1)
```
**Expectancy > 0** = estratégia lucrativa a longo prazo.

### Max Drawdown
Maior queda percentual do pico ao vale na curva de equity. Indica o risco máximo histórico.

### Brier Score
Mede a calibração das probabilidades preditas (0 = perfeito, 1 = péssimo). Valores baixos (<0.2) indicam que o modelo está bem calibrado.

### P(win) e Breakeven
- **P(win)**: Probabilidade de vitória predita pela IA
- **Breakeven**: `1/(1+payout)` - probabilidade mínima para não perder
- **Threshold**: Breakeven + margem de segurança

**Regra**: Opera apenas se `P(win) > Threshold`

## 🧩 Como Adicionar Novas Estratégias

1. Crie um arquivo em `app/strategies/` (ex: `my_strategy.py`)
2. Implemente a classe com método `generate_signal()`:

```python
from typing import Optional
import pandas as pd

class MyStrategy:
    def __init__(self, config: dict) -> None:
        self.config = config
    
    def generate_signal(self, df: pd.DataFrame, idx: int) -> Optional[str]:
        """Retorna 'CALL', 'PUT' ou None."""
        # Sua lógica aqui
        return "CALL"  # ou "PUT" ou None
    
    def get_name(self) -> str:
        return "my_strategy"
```

3. Adicione no `config.yaml`:

```yaml
strategies:
  my_strategy:
    enabled: true
    param1: value1
```

4. Registre em `app/backtest/engine.py` e `app/live/runner.py`

## 🧪 Testes

Execute os testes unitários:

```bash
poetry run pytest
```

Com cobertura:

```bash
poetry run pytest --cov=app --cov-report=html
```

## 📁 Estrutura do Projeto

```
binary-trading-bot/
├── app/
│   ├── data/           # Carregadores de dados
│   ├── features/       # Indicadores técnicos
│   ├── models/         # IA online e bandit
│   ├── strategies/     # Estratégias de trading
│   ├── risk/           # Gestão de risco
│   ├── broker/         # Interface de broker
│   ├── backtest/       # Engine de backtest
│   ├── live/           # Execução live
│   ├── utils/          # Utilidades
│   ├── config.py       # Gerenciamento de config
│   └── main.py         # CLI principal
├── tests/              # Testes unitários
├── out/                # Relatórios gerados
├── logs/               # Logs de execução
├── config.yaml         # Configuração principal
├── .env.example        # Exemplo de variáveis de ambiente
├── pyproject.toml      # Dependências Poetry
└── README.md           # Este arquivo
```

## ⚠️ Avisos Importantes

### Risco de Perda de Capital
Opções binárias são instrumentos de **alto risco**. Você pode perder todo o capital investido. Este software é fornecido "como está", sem garantias de lucro.

### Paper Trading Recomendado
**SEMPRE** teste em modo demo (`--demo`) por pelo menos 30 dias antes de considerar dinheiro real.

### Não é Conselho Financeiro
Este projeto é apenas para fins educacionais e de pesquisa. Não constitui conselho de investimento.

### Regulamentação
Verifique se opções binárias são legais na sua jurisdição. Em muitos países são proibidas ou altamente regulamentadas.

### Sem Martingale
Este bot usa **stake fixo** proporcional ao saldo. Nunca implementa martingale ou estratégias de recuperação agressivas.

## 🔧 Solução de Problemas

### Erro: "Arquivo de configuração não encontrado"
Certifique-se de estar no diretório do projeto e que `config.yaml` existe.

### Erro: "ModuleNotFoundError"
Execute `poetry install` para instalar todas as dependências.

### Backtest muito lento
Reduza o período no `config.yaml` ou use timeframe maior (5m, 15m).

### Win rate muito baixo
- Ajuste os parâmetros das estratégias
- Aumente `safety_margin` para ser mais conservador
- Desabilite estratégias com performance ruim

## 📚 Recursos Adicionais

- **Documentação River**: https://riverml.xyz/
- **Opções Binárias**: https://www.investopedia.com/terms/b/binary-option.asp
- **Análise Técnica**: https://www.investopedia.com/technical-analysis-4689657

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas features
- Adicionar novas estratégias
- Melhorar a documentação

## 📄 Licença

Este projeto é fornecido para uso educacional. Use por sua conta e risco.

## 🎓 Créditos

Desenvolvido como exemplo de sistema de trading automatizado com IA e aprendizado online.

---

**Lembre-se**: Trading algorítmico requer conhecimento, testes extensivos e gestão de risco disciplinada. Boa sorte! 🚀
