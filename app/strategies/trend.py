"""Estratégia de tendência baseada em EMA."""

from typing import Any, Optional

import pandas as pd


class TrendStrategy:
    """Estratégia de tendência com cruzamento de EMAs e filtro ATR."""
    
    def __init__(self, config: dict[str, Any]) -> None:
        """Inicializa a estratégia de tendência.
        
        Args:
            config: Dicionário de configuração.
        """
        self.config = config
        self.ema_fast = config["strategies"]["trend"]["ema_fast"]
        self.ema_slow = config["strategies"]["trend"]["ema_slow"]
        self.atr_period = config["strategies"]["trend"]["atr_period"]
        self.atr_multiplier = config["strategies"]["trend"]["atr_multiplier"]
    
    def generate_signal(self, df: pd.DataFrame, idx: int) -> Optional[str]:
        """Gera sinal de trading baseado em tendência.
        
        Args:
            df: DataFrame com dados e features.
            idx: Índice da linha atual.
        
        Returns:
            'CALL' para compra, 'PUT' para venda, None para sem sinal.
        """
        if idx < 1:
            return None
        
        row = df.iloc[idx]
        prev_row = df.iloc[idx - 1]
        
        # Verificar se temos as features necessárias
        if "ema_fast" not in row or "ema_slow" not in row or "atr" not in row:
            return None
        
        ema_fast = row["ema_fast"]
        ema_slow = row["ema_slow"]
        prev_ema_fast = prev_row["ema_fast"]
        prev_ema_slow = prev_row["ema_slow"]
        atr = row["atr"]
        close = row["close"]
        
        # Filtro de volatilidade: operar apenas se ATR for significativo
        if atr < close * 0.0001:  # ATR muito baixo
            return None
        
        # Cruzamento de alta: EMA rápida cruza acima da EMA lenta
        if prev_ema_fast <= prev_ema_slow and ema_fast > ema_slow:
            # Confirmar com distância mínima (filtro ATR)
            if (ema_fast - ema_slow) > (atr * self.atr_multiplier * 0.1):
                return "CALL"
        
        # Cruzamento de baixa: EMA rápida cruza abaixo da EMA lenta
        elif prev_ema_fast >= prev_ema_slow and ema_fast < ema_slow:
            # Confirmar com distância mínima (filtro ATR)
            if (ema_slow - ema_fast) > (atr * self.atr_multiplier * 0.1):
                return "PUT"
        
        return None
    
    def get_name(self) -> str:
        """Retorna o nome da estratégia."""
        return "trend"
