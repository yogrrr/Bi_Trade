"""Runner para execução live/demo."""

import time
from datetime import datetime
from typing import Any

import pandas as pd

from app.broker.base import BrokerInterface, Trade
from app.broker.mock import MockBroker
from app.data.loaders import SyntheticDataLoader
from app.features.ta_features import TechnicalFeatures
from app.models.bandit import ContextualBandit
from app.models.online import create_model
from app.risk.manager import RiskManager
from app.strategies.breakout import BreakoutStrategy
from app.strategies.meanrev import MeanReversionStrategy
from app.strategies.trend import TrendStrategy
from app.utils.logging import get_logger


class LiveRunner:
    """Runner para execução live/demo de trading."""
    
    def __init__(
        self,
        config: dict[str, Any],
        broker: BrokerInterface,
    ) -> None:
        """Inicializa o runner live.
        
        Args:
            config: Dicionário de configuração.
            broker: Interface do broker.
        """
        self.config = config
        self.broker = broker
        self.logger = get_logger("live")
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
        
        # Carregador de dados
        self.data_loader = SyntheticDataLoader()
        
        # Estado
        self.active_trades: list[Trade] = []
        self.historical_data: pd.DataFrame = pd.DataFrame()
        self.is_running = False
    
    def start(self) -> None:
        """Inicia a execução live."""
        self.is_running = True
        self.logger.info("Iniciando execução live...")
        
        symbol = self.config["symbol"]
        timeframe = self.config["timeframe"]
        expiry = self.config["expiry"]
        check_interval = self.config.get("live", {}).get("check_interval", 1)
        
        try:
            while self.is_running:
                # Atualizar dados históricos
                self._update_historical_data()
                
                # Verificar trades ativos
                self._check_active_trades()
                
                # Verificar se mercado está aberto
                if not self.broker.is_market_open(symbol):
                    self.logger.info("Mercado fechado, aguardando...")
                    time.sleep(60)
                    continue
                
                # Verificar se pode operar
                balance = self.broker.get_balance()
                max_concurrent = self.config.get("live", {}).get("max_concurrent_trades", 1)
                
                if len(self.active_trades) >= max_concurrent:
                    time.sleep(check_interval)
                    continue
                
                # Gerar sinais
                if len(self.historical_data) < 50:
                    self.logger.info("Aguardando dados históricos...")
                    time.sleep(check_interval)
                    continue
                
                signals = self._generate_signals()
                
                if not signals:
                    time.sleep(check_interval)
                    continue
                
                # Selecionar estratégia
                selected_strategy, signal = self._select_strategy(signals)
                
                # Extrair features
                features = TechnicalFeatures.extract_feature_vector(
                    self.historical_data.iloc[-1],
                    self.config,
                )
                
                # Predizer probabilidade
                p_win = self.model.predict_proba(features)
                
                # Obter payout
                payout = self.broker.get_payout(symbol, expiry)
                
                # Verificar se deve operar
                should_trade, reason = self.risk_manager.should_trade(p_win, payout, balance)
                
                if not should_trade:
                    self.logger.info(f"Trade rejeitado: {reason}")
                    time.sleep(check_interval)
                    continue
                
                # Calcular stake
                stake = self.risk_manager.calculate_stake(balance)
                
                # Abrir trade
                trade = self.broker.place_trade(symbol, signal, stake, expiry)
                self.active_trades.append(trade)
                
                self.logger.info(
                    f"Trade aberto: {signal} | P(win)={p_win:.2%} | "
                    f"Payout={payout:.2%} | Stake=${stake:.2f}"
                )
                
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            self.logger.info("Execução interrompida pelo usuário")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Para a execução live."""
        self.is_running = False
        self.logger.info("Execução live finalizada")
        
        # Exibir estatísticas
        stats = self.risk_manager.get_daily_stats()
        balance = self.broker.get_balance()
        
        self.logger.info(f"Saldo final: ${balance:.2f}")
        self.logger.info(
            "PnL diário: %.2fR (%.2f%%)",
            stats["daily_pnl"],
            stats["daily_pnl_percent"] * 100,
        )
        self.logger.info(f"Trades diários: {stats['daily_trades']}")
    
    def _update_historical_data(self) -> None:
        """Atualiza dados históricos."""
        # Carregar dados recentes (últimos 100 pontos)
        df = self.data_loader.load(
            self.config["symbol"],
            self.config["timeframe"],
        )
        
        # Adicionar features
        df = TechnicalFeatures.add_all_features(df, self.config)
        
        # Manter apenas últimos 100 pontos
        self.historical_data = df.tail(100).reset_index(drop=True)
    
    def _check_active_trades(self) -> None:
        """Verifica e atualiza trades ativos."""
        for trade in self.active_trades[:]:
            # Verificar resultado
            updated_trade = self.broker.check_trade_result(trade)
            
            # Se trade foi finalizado
            if updated_trade.result is not None:
                # Atualizar modelo
                features = TechnicalFeatures.extract_feature_vector(
                    self.historical_data.iloc[-1],
                    self.config,
                )
                y = 1 if updated_trade.result == "win" else 0
                self.model.update(features, y)
                
                # Atualizar bandit
                if self.bandit:
                    # Encontrar estratégia do trade (simplificado)
                    self.bandit.update(self.strategies[0].get_name(), float(y))
                
                # Atualizar risk manager
                pnl_r = (updated_trade.profit or 0) / updated_trade.stake
                self.risk_manager.update_daily_pnl(pnl_r)
                
                # Logar resultado
                self.logger.info(
                    f"Trade finalizado: {updated_trade.result.upper()} | "
                    f"Profit=${updated_trade.profit:.2f} | "
                    f"Balance=${self.broker.get_balance():.2f}"
                )
                
                # Remover da lista de ativos
                self.active_trades.remove(trade)
    
    def _generate_signals(self) -> list[tuple[str, str]]:
        """Gera sinais de todas as estratégias."""
        signals = []
        idx = len(self.historical_data) - 1
        
        for strategy in self.strategies:
            signal = strategy.generate_signal(self.historical_data, idx)
            if signal is not None:
                signals.append((strategy.get_name(), signal))
        
        return signals
    
    def _select_strategy(self, signals: list[tuple[str, str]]) -> tuple[str, str]:
        """Seleciona estratégia e sinal."""
        if self.bandit and len(signals) > 0:
            row = self.historical_data.iloc[-1]
            context = {
                "hour": row["hour"],
                "volatility": row["volatility"],
            }
            selected_strategy = self.bandit.select_strategy(context)
            
            # Encontrar sinal da estratégia selecionada
            for strat_name, strat_signal in signals:
                if strat_name == selected_strategy:
                    return strat_name, strat_signal
        
        # Retornar primeiro sinal disponível
        return signals[0]


def create_live_runner(config: dict[str, Any], demo: bool = True) -> LiveRunner:
    """Cria um runner live.
    
    Args:
        config: Dicionário de configuração.
        demo: Se True, usa MockBroker (simulação local). Se False, usa broker real do config.
    
    Returns:
        Instância do LiveRunner.
    """
    if demo:
        # Usar MockBroker para simulação local (paper trading)
        initial_balance = config.get("live", {}).get("initial_balance", 1000.0)
        broker = MockBroker(initial_balance=initial_balance)
    else:
        # Usar broker real configurado no config.yaml
        from app.broker.iqoption import IQOptionBroker
        
        broker_config = config.get("broker", {})
        broker_type = broker_config.get("type", "mock")
        
        if broker_type == "mock":
            # Se tipo for mock, usar MockBroker mesmo com demo=False
            initial_balance = config.get("live", {}).get("initial_balance", 1000.0)
            broker = MockBroker(initial_balance=initial_balance)
        elif broker_type == "iqoption":
            # Usar IQ Option
            email = broker_config.get("email")
            password = broker_config.get("password")
            
            if not email or not password:
                raise ValueError(
                    "Credenciais do IQ Option não configuradas. \n"
                    "Edite config.yaml e adicione:\n"
                    "broker:\n"
                    "  type: iqoption\n"
                    "  email: seu-email\n"
                    "  password: sua-senha\n"
                    "  demo: true  # ou false para conta real"
                )
            
            # Usar configuração de demo do config.yaml
            use_demo = broker_config.get("demo", True)
            broker = IQOptionBroker(email=email, password=password, demo=use_demo)
        else:
            raise ValueError(f"Broker '{broker_type}' não suportado. Use 'mock' ou 'iqoption'")
    
    return LiveRunner(config, broker)
