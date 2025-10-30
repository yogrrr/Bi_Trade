"""Engine de backtest para opções binárias."""

import random
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

from app.broker.base import Trade
from app.features.ta_features import TechnicalFeatures
from app.models.bandit import ContextualBandit
from app.models.online import create_model
from app.risk.manager import RiskManager
from app.strategies.breakout import BreakoutStrategy
from app.strategies.meanrev import MeanReversionStrategy
from app.strategies.trend import TrendStrategy


class BacktestEngine:
    """Engine para realizar backtest de estratégias."""
    
    def __init__(self, config: dict[str, Any]) -> None:
        """Inicializa o engine de backtest.
        
        Args:
            config: Dicionário de configuração.
        """
        self.config = config
        self.risk_manager = RiskManager(config)
        
        # Criar modelo de IA
        model_type = config.get("model", {}).get("type", "river")
        calibration = config.get("model", {}).get("calibration")
        self.model = create_model(model_type, calibration)
        
        # Criar estratégias
        self.strategies = []
        if config.get("strategies", {}).get("trend", {}).get("enabled", False):
            self.strategies.append(TrendStrategy(config))
        if config.get("strategies", {}).get("meanrev", {}).get("enabled", False):
            self.strategies.append(MeanReversionStrategy(config))
        if config.get("strategies", {}).get("breakout", {}).get("enabled", False):
            self.strategies.append(BreakoutStrategy(config))
        
        # Criar bandit contextual
        self.bandit = None
        if config.get("bandit", {}).get("enabled", False):
            strategy_names = [s.get_name() for s in self.strategies]
            epsilon = config["bandit"]["epsilon"]
            self.bandit = ContextualBandit(strategy_names, epsilon)
        
        # Configurações de backtest
        self.initial_balance = config.get("backtest", {}).get("initial_balance", 1000.0)
        self.latency_ms = config.get("backtest", {}).get("latency_ms", 100)
        self.slippage = config.get("backtest", {}).get("slippage", 0.0)
        
        # Estado
        self.balance = self.initial_balance
        self.trades: list[dict[str, Any]] = []
        self.opportunities: list[dict[str, Any]] = []  # Todas as oportunidades analisadas
        self.equity_curve: list[float] = [self.initial_balance]
    
    def run(self, df: pd.DataFrame) -> dict[str, Any]:
        """Executa o backtest.
        
        Args:
            df: DataFrame com dados de mercado e features.
        
        Returns:
            Dicionário com resultados do backtest.
        """
        print(f"Iniciando backtest com {len(df)} barras...")
        
        for idx in range(len(df)):
            row = df.iloc[idx]
            
            # Gerar sinais de todas as estratégias
            signals = []
            for strategy in self.strategies:
                signal = strategy.generate_signal(df, idx)
                if signal is not None:
                    signals.append((strategy.get_name(), signal))
            
            # Se não houver sinais, continuar
            if not signals:
                self.equity_curve.append(self.balance)
                continue
            
            # Selecionar estratégia (com bandit ou primeira disponível)
            if self.bandit and len(signals) > 0:
                context = {
                    "hour": row["hour"],
                    "volatility": row["volatility"],
                }
                selected_strategy = self.bandit.select_strategy(context)
                
                # Encontrar sinal da estratégia selecionada
                signal = None
                for strat_name, strat_signal in signals:
                    if strat_name == selected_strategy:
                        signal = strat_signal
                        break
                
                if signal is None:
                    signal = signals[0][1]
                    selected_strategy = signals[0][0]
            else:
                selected_strategy = signals[0][0]
                signal = signals[0][1]
            
            # Extrair features
            features = TechnicalFeatures.extract_feature_vector(row, self.config)
            
            # Predizer probabilidade de vitória
            p_win = self.model.predict_proba(features)
            
            # Simular payout
            payout = self._simulate_payout()
            
            # Verificar se deve operar
            should_trade, reason = self.risk_manager.should_trade(p_win, payout, self.balance)
            
            # Registrar oportunidade (executada ou rejeitada)
            opportunity = {
                "timestamp": row["timestamp"],
                "strategy": selected_strategy,
                "signal": signal,
                "p_win": p_win,
                "payout": payout,
                "should_trade": should_trade,
                "reason": reason,
                "balance": self.balance,
            }
            self.opportunities.append(opportunity)
            
            if not should_trade:
                self.equity_curve.append(self.balance)
                continue
            
            # Calcular stake
            stake = self.risk_manager.calculate_stake(self.balance)
            
            # Simular trade
            entry_price = row["close"]
            exit_price = self._simulate_exit_price(df, idx, signal)
            
            # Determinar resultado
            if signal == "CALL":
                win = exit_price > entry_price
            else:  # PUT
                win = exit_price < entry_price
            
            # Calcular profit
            if win:
                profit = stake * payout
                result = "win"
            else:
                profit = -stake
                result = "loss"
            
            # Atualizar saldo
            self.balance += profit
            
            # Atualizar modelo
            y = 1 if win else 0
            self.model.update(features, y)
            
            # Atualizar bandit
            if self.bandit:
                self.bandit.update(selected_strategy, float(y))
            
            # Atualizar risk manager
            pnl_r = profit / stake
            self.risk_manager.update_daily_pnl(pnl_r)
            
            # Registrar trade
            trade_record = {
                "timestamp": row["timestamp"],
                "strategy": selected_strategy,
                "signal": signal,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "stake": stake,
                "payout": payout,
                "p_win": p_win,
                "result": result,
                "profit": profit,
                "balance": self.balance,
            }
            self.trades.append(trade_record)
            
            # Atualizar curva de equity
            self.equity_curve.append(self.balance)
        
        # Calcular métricas
        metrics = self._calculate_metrics()
        
        print(f"Backtest concluído: {len(self.trades)} trades executados")
        
        return {
            "trades": self.trades,
            "opportunities": self.opportunities,
            "equity_curve": self.equity_curve,
            "metrics": metrics,
        }
    
    def _simulate_payout(self) -> float:
        """Simula payout variável."""
        base_payout = 0.85
        variation = random.uniform(-0.05, 0.05)
        return max(0.70, min(0.95, base_payout + variation))
    
    def _simulate_exit_price(self, df: pd.DataFrame, idx: int, signal: str) -> float:
        """Simula preço de saída com base na expiração."""
        expiry_bars = max(1, self.config["expiry"] // 60)  # Converter segundos para barras
        exit_idx = min(idx + expiry_bars, len(df) - 1)
        
        # Usar preço de fechamento da barra de expiração
        exit_price = df.iloc[exit_idx]["close"]
        
        # Adicionar slippage
        if self.slippage > 0:
            slippage_amount = exit_price * self.slippage * random.choice([-1, 1])
            exit_price += slippage_amount
        
        return exit_price
    
    def _calculate_metrics(self) -> dict[str, Any]:
        """Calcula métricas de performance."""
        if not self.trades:
            return {}
        
        trades_df = pd.DataFrame(self.trades)
        
        # Métricas básicas
        total_trades = len(trades_df)
        wins = len(trades_df[trades_df["result"] == "win"])
        losses = len(trades_df[trades_df["result"] == "loss"])
        win_rate = wins / total_trades if total_trades > 0 else 0
        
        # Profit/Loss
        total_profit = trades_df["profit"].sum()
        avg_profit = trades_df["profit"].mean()
        
        # Expectancy
        avg_win = trades_df[trades_df["result"] == "win"]["profit"].mean() if wins > 0 else 0
        avg_loss = abs(trades_df[trades_df["result"] == "loss"]["profit"].mean()) if losses > 0 else 0
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        # Drawdown
        equity_series = pd.Series(self.equity_curve)
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Brier score (calibração)
        brier_score = np.mean((trades_df["p_win"] - (trades_df["result"] == "win").astype(int)) ** 2)
        
        # Retorno
        total_return = (self.balance - self.initial_balance) / self.initial_balance
        
        metrics = {
            "total_trades": total_trades,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "total_profit": total_profit,
            "avg_profit": avg_profit,
            "expectancy": expectancy,
            "max_drawdown": max_drawdown,
            "brier_score": brier_score,
            "total_return": total_return,
            "final_balance": self.balance,
        }
        
        return metrics
