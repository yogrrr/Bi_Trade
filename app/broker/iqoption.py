"""Integração com IQ Option para trading real."""

import time
from datetime import datetime
from typing import Optional

from app.broker.base import BaseBroker, Trade


class IQOptionBroker(BaseBroker):
    """Broker para IQ Option (requer biblioteca iqoptionapi)."""
    
    def __init__(self, email: str, password: str, demo: bool = True):
        """Inicializa conexão com IQ Option.
        
        Args:
            email: Email da conta IQ Option.
            password: Senha da conta.
            demo: Se True, usa conta demo. Se False, usa conta real.
        """
        self.email = email
        self.password = password
        self.demo = demo
        self.api = None
        self.connected = False
        
        print(f"Inicializando IQ Option Broker ({'DEMO' if demo else 'REAL'})")
    
    def connect(self) -> bool:
        """Conecta ao broker.
        
        Returns:
            True se conectou com sucesso.
        """
        try:
            # Importar biblioteca (precisa ser instalada separadamente)
            try:
                from iqoptionapi.stable_api import IQ_Option
            except ImportError:
                raise ImportError(
                    "Biblioteca iqoptionapi não encontrada. Instale com:\n"
                    "pip install iqoptionapi"
                )
            
            print(f"Conectando ao IQ Option como {self.email}...")
            
            self.api = IQ_Option(self.email, self.password)
            check, reason = self.api.connect()
            
            if not check:
                print(f"✗ Falha na conexão: {reason}")
                return False
            
            # Mudar para conta demo/real
            if self.demo:
                self.api.change_balance("PRACTICE")
                print("✓ Conectado à conta DEMO")
            else:
                self.api.change_balance("REAL")
                print("⚠️  Conectado à conta REAL")
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"✗ Erro ao conectar: {e}")
            return False
    
    def disconnect(self) -> None:
        """Desconecta do broker."""
        if self.api:
            print("Desconectando do IQ Option...")
            self.connected = False
            self.api = None
    
    def place_order(
        self,
        symbol: str,
        direction: str,
        amount: float,
        expiry: int,
    ) -> Optional[Trade]:
        """Coloca uma ordem no broker.
        
        Args:
            symbol: Par de moedas (ex: EURUSD).
            direction: "CALL" ou "PUT".
            amount: Valor a investir.
            expiry: Tempo de expiração em segundos.
        
        Returns:
            Trade com informações da ordem, ou None se falhar.
        """
        if not self.connected or not self.api:
            print("✗ Não conectado ao broker")
            return None
        
        try:
            # Converter símbolo para formato IQ Option
            # EURUSD -> EURUSD-OTC ou EURUSD
            iq_symbol = symbol
            
            # Converter direção
            iq_direction = "call" if direction == "CALL" else "put"
            
            # Converter expiração (segundos -> minutos)
            expiry_minutes = max(1, expiry // 60)
            
            print(f"Colocando ordem: {iq_symbol} {iq_direction.upper()} ${amount} {expiry_minutes}min")
            
            # Obter preço atual
            price = self.api.get_realtime_candles(iq_symbol, 60)
            if not price:
                print("✗ Não foi possível obter preço atual")
                return None
            
            entry_price = list(price.values())[0]['close']
            
            # Colocar ordem
            status, order_id = self.api.buy(
                amount,
                iq_symbol,
                iq_direction,
                expiry_minutes
            )
            
            if not status:
                print(f"✗ Ordem rejeitada")
                return None
            
            print(f"✓ Ordem aceita: ID {order_id}")
            
            # Criar objeto Trade
            trade = Trade(
                id=str(order_id),
                symbol=symbol,
                direction=direction,
                amount=amount,
                entry_price=entry_price,
                entry_time=datetime.now(),
                expiry=expiry,
                status="open",
            )
            
            return trade
            
        except Exception as e:
            print(f"✗ Erro ao colocar ordem: {e}")
            return None
    
    def check_trade_result(self, trade: Trade) -> Optional[str]:
        """Verifica o resultado de um trade.
        
        Args:
            trade: Trade a verificar.
        
        Returns:
            "win", "loss" ou None se ainda não finalizou.
        """
        if not self.connected or not self.api:
            return None
        
        try:
            # Verificar se trade já expirou
            elapsed = (datetime.now() - trade.entry_time).total_seconds()
            if elapsed < trade.expiry:
                return None  # Ainda não expirou
            
            # Obter resultado
            result = self.api.check_win_v3(int(trade.id))
            
            if result is None:
                return None  # Resultado ainda não disponível
            
            if result > 0:
                return "win"
            elif result < 0:
                return "loss"
            else:
                return "draw"  # Empate (raro)
                
        except Exception as e:
            print(f"✗ Erro ao verificar resultado: {e}")
            return None
    
    def get_balance(self) -> float:
        """Obtém saldo atual.
        
        Returns:
            Saldo disponível.
        """
        if not self.connected or not self.api:
            return 0.0
        
        try:
            balance = self.api.get_balance()
            return float(balance)
        except Exception as e:
            print(f"✗ Erro ao obter saldo: {e}")
            return 0.0
    
    def get_payout(self, symbol: str) -> float:
        """Obtém payout atual para um símbolo.
        
        Args:
            symbol: Símbolo do ativo.
        
        Returns:
            Payout em decimal (ex: 0.85 para 85%).
        """
        if not self.connected or not self.api:
            return 0.80  # Valor padrão
        
        try:
            # Obter informações do ativo
            all_assets = self.api.get_all_open_time()
            
            if symbol in all_assets.get('binary', {}):
                profit = all_assets['binary'][symbol].get('profit', 80)
                return profit / 100.0
            
            return 0.80  # Valor padrão se não encontrar
            
        except Exception as e:
            print(f"✗ Erro ao obter payout: {e}")
            return 0.80


class QuotexBroker(BaseBroker):
    """Broker para Quotex (estrutura base - requer implementação)."""
    
    def __init__(self, email: str, password: str, demo: bool = True):
        """Inicializa conexão com Quotex.
        
        Args:
            email: Email da conta.
            password: Senha da conta.
            demo: Se True, usa conta demo.
        """
        self.email = email
        self.password = password
        self.demo = demo
        self.connected = False
        
        print(f"Quotex Broker ({'DEMO' if demo else 'REAL'})")
        print("⚠️  Implementação Quotex ainda não disponível")
        print("Use IQOptionBroker ou implemente a integração Quotex")
    
    def connect(self) -> bool:
        """Conecta ao broker."""
        print("✗ Quotex não implementado ainda")
        return False
    
    def disconnect(self) -> None:
        """Desconecta do broker."""
        pass
    
    def place_order(
        self,
        symbol: str,
        direction: str,
        amount: float,
        expiry: int,
    ) -> Optional[Trade]:
        """Coloca uma ordem."""
        print("✗ Quotex não implementado ainda")
        return None
    
    def check_trade_result(self, trade: Trade) -> Optional[str]:
        """Verifica resultado."""
        return None
    
    def get_balance(self) -> float:
        """Obtém saldo."""
        return 0.0
    
    def get_payout(self, symbol: str) -> float:
        """Obtém payout."""
        return 0.80
