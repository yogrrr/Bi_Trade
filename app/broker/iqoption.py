"""Integração com IQ Option para trading real."""

import time
import logging
from datetime import datetime
from typing import Optional

from app.broker.base import BrokerInterface, Trade


logger = logging.getLogger(__name__)


class IQOptionBroker(BrokerInterface):
    """Broker para IQ Option real."""
    
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
        self.trades: dict[str, Trade] = {}
        
        # Conectar
        self._connect()
    
    def _connect(self) -> None:
        """Conecta ao IQ Option."""
        try:
            # Importar biblioteca
            try:
                from iqoptionapi.stable_api import IQ_Option
            except ImportError:
                raise ImportError(
                    "Biblioteca iqoptionapi não encontrada. Instale com:\n"
                    "pip install git+https://github.com/Lu-Yi-Hsun/iqoptionapi.git"
                )
            
            logger.info(f"Conectando ao IQ Option (email: {self.email}, demo: {self.demo})...")
            
            self.api = IQ_Option(self.email, self.password)
            check, reason = self.api.connect()
            
            if not check:
                raise ConnectionError(f"Falha ao conectar com IQ Option: {reason}")
            
            # Mudar para conta demo/real
            if self.demo:
                self.api.change_balance("PRACTICE")
                logger.info("Conectado à conta DEMO")
            else:
                self.api.change_balance("REAL")
                logger.warning("⚠️  Conectado à conta REAL - USE COM CUIDADO!")
            
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            raise
    
    def _ensure_connected(self) -> None:
        """Garante que está conectado, reconecta se necessário."""
        if self.api is None or not self.api.check_connect():
            logger.warning("Conexão perdida, reconectando...")
            self._connect()
    
    def get_balance(self) -> float:
        """Retorna o saldo atual da conta."""
        self._ensure_connected()
        
        try:
            balance = self.api.get_balance()
            return float(balance)
        except Exception as e:
            logger.error(f"Erro ao obter saldo: {e}")
            return 0.0
    
    def get_payout(self, symbol: str, expiry: int) -> float:
        """Obtém o payout atual.
        
        Args:
            symbol: Par de moedas (ex: "EURUSD").
            expiry: Expiração em segundos.
        
        Returns:
            Payout em decimal (ex: 0.85 para 85%).
        """
        self._ensure_connected()
        
        try:
            # Obter todos os payouts
            all_profit = self.api.get_all_profit()
            
            # Determinar tipo (turbo para < 5min, binary para >= 5min)
            option_type = "turbo" if expiry < 300 else "binary"
            
            # Obter payout do símbolo
            if symbol in all_profit and option_type in all_profit[symbol]:
                payout_percent = all_profit[symbol][option_type]
                return payout_percent / 100.0  # Converter de % para decimal
            
            # Fallback: payout padrão
            logger.warning(f"Payout não encontrado para {symbol} ({option_type}), usando 80%")
            return 0.80
            
        except Exception as e:
            logger.error(f"Erro ao obter payout: {e}")
            return 0.80
    
    def get_current_price(self, symbol: str) -> float:
        """Obtém o preço atual.
        
        Args:
            symbol: Par de moedas (ex: "EURUSD").
        
        Returns:
            Preço atual.
        """
        self._ensure_connected()
        
        try:
            # Obter candle mais recente
            candles = self.api.get_candles(symbol, 60, 1, time.time())
            
            if candles and len(candles) > 0:
                return float(candles[-1]["close"])
            
            raise ValueError(f"Não foi possível obter preço para {symbol}")
            
        except Exception as e:
            logger.error(f"Erro ao obter preço: {e}")
            raise
    
    def place_trade(
        self,
        symbol: str,
        direction: str,
        stake: float,
        expiry: int,
    ) -> Trade:
        """Abre um trade de opção binária.
        
        Args:
            symbol: Par de moedas (ex: "EURUSD").
            direction: "CALL" ou "PUT".
            stake: Valor a investir.
            expiry: Expiração em segundos.
        
        Returns:
            Objeto Trade com informações do trade.
        """
        self._ensure_connected()
        
        try:
            # Converter direção para formato IQ Option
            action = "call" if direction.upper() == "CALL" else "put"
            
            # Converter expiração de segundos para minutos
            expiry_minutes = max(1, expiry // 60)
            
            # Obter payout e preço antes de abrir
            payout = self.get_payout(symbol, expiry)
            entry_price = self.get_current_price(symbol)
            
            # Abrir trade
            logger.info(f"Abrindo trade: {symbol} {direction} ${stake} {expiry}s")
            check, trade_id = self.api.buy(stake, symbol, action, expiry_minutes)
            
            if not check:
                raise RuntimeError(f"Falha ao abrir trade: {symbol} {direction}")
            
            # Criar objeto Trade
            trade = Trade(
                id=str(trade_id),
                symbol=symbol,
                direction=direction.upper(),
                stake=stake,
                payout=payout,
                expiry=expiry,
                entry_time=datetime.now(),
                entry_price=entry_price,
            )
            
            # Armazenar trade
            self.trades[trade.id] = trade
            
            logger.info(f"✓ Trade aberto com sucesso! ID: {trade_id}")
            
            return trade
            
        except Exception as e:
            logger.error(f"Erro ao abrir trade: {e}")
            raise
    
    def check_trade_result(self, trade: Trade) -> Trade:
        """Verifica o resultado de um trade.
        
        Args:
            trade: Trade a verificar.
        
        Returns:
            Trade atualizado com resultado.
        """
        # Se já tem resultado, retornar
        if trade.exit_time is not None:
            return trade
        
        self._ensure_connected()
        
        try:
            # Verificar resultado usando check_win_v3 (mais eficiente)
            result_str = self.api.check_win_v3(int(trade.id))
            
            # Mapear resultado
            if result_str == "win":
                trade.result = "win"
                trade.profit = trade.stake * trade.payout
            elif result_str == "loose":  # API usa "loose" em vez de "loss"
                trade.result = "loss"
                trade.profit = 0.0
            elif result_str == "equal":
                trade.result = "tie"
                trade.profit = trade.stake
            else:
                # Trade ainda não finalizou
                return trade
            
            # Obter preço de saída
            trade.exit_price = self.get_current_price(trade.symbol)
            trade.exit_time = datetime.now()
            
            logger.info(f"Trade {trade.id} finalizado: {trade.result} (${trade.profit:.2f})")
            
        except Exception as e:
            logger.error(f"Erro ao verificar resultado do trade {trade.id}: {e}")
        
        return trade
    
    def is_market_open(self, symbol: str) -> bool:
        """Verifica se o mercado está aberto.
        
        Args:
            symbol: Par de moedas.
        
        Returns:
            True se mercado está aberto.
        """
        self._ensure_connected()
        
        try:
            # Obter informações do ativo
            all_init = self.api.get_all_init()
            
            # Verificar se ativo está aberto
            if "binary" in all_init and "actives" in all_init["binary"]:
                actives = all_init["binary"]["actives"]
                if symbol in actives:
                    return actives[symbol]["enabled"]
            
            # Fallback: tentar obter preço
            self.get_current_price(symbol)
            return True
            
        except Exception:
            return False
    
    def close(self) -> None:
        """Fecha conexão com o broker."""
        if self.api is not None:
            logger.info("Fechando conexão com IQ Option...")
            # A API não tem método close explícito
            self.api = None


class QuotexBroker(BrokerInterface):
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
        
        logger.warning("⚠️  Quotex Broker ainda não implementado")
        logger.info("Use IQOptionBroker ou implemente a integração Quotex")
        
        raise NotImplementedError("Broker Quotex ainda não implementado")
    
    def get_balance(self) -> float:
        """Obtém saldo."""
        return 0.0
    
    def get_payout(self, symbol: str, expiry: int) -> float:
        """Obtém payout."""
        return 0.80
    
    def get_current_price(self, symbol: str) -> float:
        """Obtém preço atual."""
        return 0.0
    
    def place_trade(
        self,
        symbol: str,
        direction: str,
        stake: float,
        expiry: int,
    ) -> Trade:
        """Coloca uma ordem."""
        raise NotImplementedError("Quotex não implementado")
    
    def check_trade_result(self, trade: Trade) -> Trade:
        """Verifica resultado."""
        return trade
    
    def is_market_open(self, symbol: str) -> bool:
        """Verifica se mercado está aberto."""
        return False
