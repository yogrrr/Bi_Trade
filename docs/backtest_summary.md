# Backtest Report — Binary Trading Bot

## Principais Métricas
- **Retorno total:** +23,68%
- **Saldo final:** US$ 1.236,77
- **Win rate:** 75%
- **Total de trades executados:** 28
- **Oportunidades analisadas:** 191.546 (28 executadas, 191.518 rejeitadas)
- **Max drawdown:** -2,27%
- **Expectância por trade:** 8,4562
- **Probabilidade média de vitória (P(win)) nas oportunidades analisadas:** 44,56%

## Por que a maioria das oportunidades foi rejeitada
- Filtros rígidos priorizando segurança e metas diárias.
- Muitas entradas descartadas por já terem atingido a meta de lucro diária.
- Diversos sinais abaixo do threshold mínimo de probabilidade de vitória.

## Interpretação Prática
- Estratégia com alto aproveitamento nos trades executados, combinando 75% de vitórias com drawdown reduzido.
- Baixa taxa de execução indica filtros e metas potencialmente conservadores demais, limitando o uso do capital.
- Expectância elevada mostra consistência de resultados quando a estratégia é acionada.

## Recomendações
- Relaxar gradualmente os thresholds de P(win) para aumentar o volume de trades sem perder controle de risco.
- Reavaliar a meta de lucro diária para liberar mais oportunidades qualificadas.
- Conduzir análise de sensibilidade por faixas de P(win) para identificar melhor trade-off entre frequência e performance.

## Conclusão
O backtest apresenta sólida relação entre rentabilidade e risco, mas aproveita apenas uma fração das oportunidades disponíveis. Ajustes controlados nos filtros e metas podem ampliar a amostragem de trades, potencialmente elevando o retorno sem deteriorar significativamente o perfil de risco.
