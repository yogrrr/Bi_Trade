"""Interface base para brokers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Trade:
    """Representa um trade de opção binária."""
    
    id: str
    symbol: str
    direction: str  # 'CALL' ou 'PUT'
    stake: float
    payout: float
    expiry: int  # segundos
    entry_time: datetime
    entry_price: float
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    result: Optional[str] = None  # 'win', 'loss', 'tie'
    profit: Optional[float] = None


class BrokerInterface(ABC):
    """Interface abstrata para brokers de opções binárias."""
    
    @abstractmethod
    def get_balance(self) -> float:
        """Retorna o saldo atual da conta.
        
        Returns:
            Saldo em unidades monetárias.
        """
        pass
    
    @abstractmethod
    def get_payout(self, symbol: str, expiry: int) -> float:
        """Obtém o payout atual para um símbolo e expiração.
        
        Args:
            symbol: Símbolo do ativo (ex: EURUSD).
            expiry: Expiração em segundos.
        
        Returns:
            Payout (ex: 0.85 para 85%).
        """
        pass
    
    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        """Obtém o preço atual de um símbolo.
        
        Args:
            symbol: Símbolo do ativo (ex: EURUSD).
        
        Returns:
            Preço atual.
        """
        pass
    
    @abstractmethod
    def place_trade(
        self,
        symbol: str,
        direction: str,
        stake: float,
        expiry: int,
    ) -> Trade:
        """Abre um trade de opção binária.
        
        Args:
            symbol: Símbolo do ativo (ex: EURUSD).
            direction: Direção ('CALL' ou 'PUT').
            stake: Valor da aposta.
            expiry: Expiração em segundos.
        
        Returns:
            Objeto Trade com informações do trade.
        """
        pass
    
    @abstractmethod
    def check_trade_result(self, trade: Trade) -> Trade:
        """Verifica o resultado de um trade.
        
        Args:
            trade: Objeto Trade a ser verificado.
        
        Returns:
            Objeto Trade atualizado com resultado.
        """
        pass
    
    @abstractmethod
    def is_market_open(self, symbol: str) -> bool:
        """Verifica se o mercado está aberto.
        
        Args:
            symbol: Símbolo do ativo (ex: EURUSD).
        
        Returns:
            True se o mercado estiver aberto.
        """
        pass
