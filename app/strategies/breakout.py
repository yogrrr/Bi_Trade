"""Estratégia de breakout baseada em Canal de Donchian."""

from typing import Any, Optional

import pandas as pd


class BreakoutStrategy:
    """Estratégia de breakout com Canal de Donchian."""
    
    def __init__(self, config: dict[str, Any]) -> None:
        """Inicializa a estratégia de breakout.
        
        Args:
            config: Dicionário de configuração.
        """
        self.config = config
        self.donchian_period = config["strategies"]["breakout"]["donchian_period"]
    
    def generate_signal(self, df: pd.DataFrame, idx: int) -> Optional[str]:
        """Gera sinal de trading baseado em breakout.
        
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
        if "donchian_upper" not in row or "donchian_lower" not in row:
            return None
        
        close = row["close"]
        prev_close = prev_row["close"]
        donchian_upper = row["donchian_upper"]
        donchian_lower = row["donchian_lower"]
        prev_donchian_upper = prev_row["donchian_upper"]
        prev_donchian_lower = prev_row["donchian_lower"]
        
        # Breakout de alta: preço rompe acima da banda superior
        if prev_close <= prev_donchian_upper and close > donchian_upper:
            return "CALL"
        
        # Breakout de baixa: preço rompe abaixo da banda inferior
        elif prev_close >= prev_donchian_lower and close < donchian_lower:
            return "PUT"
        
        return None
    
    def get_name(self) -> str:
        """Retorna o nome da estratégia."""
        return "breakout"
