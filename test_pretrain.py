#!/usr/bin/env python3
"""Script de teste para pré-treinamento do modelo."""

import sys
sys.path.insert(0, '.')

from app.config import Config
from app.data.loaders import SyntheticDataLoader
from app.features.ta_features import TechnicalFeatures
from app.backtest.engine import BacktestEngine
import pandas as pd

config = Config()
loader = SyntheticDataLoader()
df = loader.load('EURUSD', '1m', '2024-01-01', '2024-01-02')
df = TechnicalFeatures.add_all_features(df, config._config)

engine = BacktestEngine(config._config)
results = engine.run(df)

print(f'\n=== RESULTADOS ===')
print(f'Trades executados: {len(results["trades"])}')
print(f'Oportunidades analisadas: {len(results["opportunities"])}')

if results['opportunities']:
    opp_df = pd.DataFrame(results['opportunities'])
    print(f'P(win) médio: {opp_df["p_win"].mean():.4f}')
    print(f'Executadas: {opp_df["should_trade"].sum()}')
    print(f'Rejeitadas: {(~opp_df["should_trade"]).sum()}')

if results['trades']:
    trades_df = pd.DataFrame(results['trades'])
    wins = (trades_df['result'] == 'win').sum()
    print(f'\nWin Rate Real: {wins}/{len(trades_df)} = {wins/len(trades_df)*100:.2f}%')
    print(f'Saldo Final: ${results["metrics"]["final_balance"]:.2f}')
    print(f'Retorno: {results["metrics"]["total_return"]*100:.2f}%')
