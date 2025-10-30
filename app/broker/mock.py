"""Broker mock para demonstração e testes."""

import random
import uuid
from datetime import datetime, timedelta
from typing import Optional

from app.broker.base import BrokerInterface, Trade


class MockBroker(BrokerInterface):
    """Broker mock para demonstração e paper trading."""
    
    def __init__(self, initial_balance: float = 1000.0, payout: float = 0.85) -> None:
        """Inicializa o broker mock.
        
        Args:
            initial_balance: Saldo inicial.
            payout: Payout padrão (ex: 0.85 para 85%).
        """
        self.balance = initial_balance
        self.payout = payout
        self.current_price = 1.1000  # Preço inicial simulado
        self.trades: list[Trade] = []
    
    def get_balance(self) -> float:
        """Retorna o saldo atual da conta."""
        return self.balance
    
    def get_payout(self, symbol: str, expiry: int) -> float:
        """Obtém o payout atual."""
        # Simular variação de payout
        variation = random.uniform(-0.05, 0.05)
        return max(0.70, min(0.95, self.payout + variation))
    
    def get_current_price(self, symbol: str) -> float:
        """Obtém o preço atual."""
        # Simular movimento de preço
        change = random.uniform(-0.0010, 0.0010)
        self.current_price += change
        return self.current_price
    
    def place_trade(
        self,
        symbol: str,
        direction: str,
        stake: float,
        expiry: int,
    ) -> Trade:
        """Abre um trade de opção binária."""
        # Obter payout e preço atual
        payout = self.get_payout(symbol, expiry)
        entry_price = self.get_current_price(symbol)
        
        # Criar trade
        trade = Trade(
            id=str(uuid.uuid4()),
            symbol=symbol,
            direction=direction,
            stake=stake,
            payout=payout,
            expiry=expiry,
            entry_time=datetime.now(),
            entry_price=entry_price,
        )
        
        # Deduzir stake do saldo
        self.balance -= stake
        
        # Armazenar trade
        self.trades.append(trade)
        
        return trade
    
    def check_trade_result(self, trade: Trade) -> Trade:
        """Verifica o resultado de um trade."""
        # Verificar se já expirou
        if trade.exit_time is not None:
            return trade
        
        # Verificar se deve expirar
        expiry_time = trade.entry_time + timedelta(seconds=trade.expiry)
        if datetime.now() < expiry_time:
            return trade  # Ainda não expirou
        
        # Simular preço de saída
        exit_price = self.get_current_price(trade.symbol)
        
        # Determinar resultado
        if trade.direction == "CALL":
            if exit_price > trade.entry_price:
                result = "win"
                profit = trade.stake * trade.payout
            elif exit_price < trade.entry_price:
                result = "loss"
                profit = 0.0
            else:
                result = "tie"
                profit = trade.stake
        else:  # PUT
            if exit_price < trade.entry_price:
                result = "win"
                profit = trade.stake * trade.payout
            elif exit_price > trade.entry_price:
                result = "loss"
                profit = 0.0
            else:
                result = "tie"
                profit = trade.stake
        
        # Atualizar trade
        trade.exit_time = datetime.now()
        trade.exit_price = exit_price
        trade.result = result
        trade.profit = profit
        
        # Atualizar saldo
        if result == "win":
            self.balance += trade.stake + profit
        elif result == "tie":
            self.balance += trade.stake
        
        return trade
    
    def is_market_open(self, symbol: str) -> bool:
        """Verifica se o mercado está aberto."""
        # Simular mercado sempre aberto para demo
        return True
    
    def simulate_price_movement(self, direction: str, expiry: int) -> float:
        """Simula movimento de preço para backtest.
        
        Args:
            direction: Direção esperada ('CALL' ou 'PUT').
            expiry: Expiração em segundos.
        
        Returns:
            Preço de saída simulado.
        """
        # Simular movimento aleatório com leve viés na direção
        bias = 0.0005 if direction == "CALL" else -0.0005
        noise = random.uniform(-0.0010, 0.0010)
        change = bias + noise
        
        return self.current_price + change
