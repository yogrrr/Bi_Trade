"""Estratégia de reversão à média baseada em RSI."""

from typing import Any, Optional

import pandas as pd


class MeanReversionStrategy:
    """Estratégia de reversão à média com RSI extremo."""
    
    def __init__(self, config: dict[str, Any]) -> None:
        """Inicializa a estratégia de reversão à média.
        
        Args:
            config: Dicionário de configuração.
        """
        self.config = config
        self.rsi_period = config["strategies"]["meanrev"]["rsi_period"]
        self.rsi_oversold = config["strategies"]["meanrev"]["rsi_oversold"]
        self.rsi_overbought = config["strategies"]["meanrev"]["rsi_overbought"]
    
    def generate_signal(self, df: pd.DataFrame, idx: int) -> Optional[str]:
        """Gera sinal de trading baseado em reversão à média.
        
        Args:
            df: DataFrame com dados e features.
            idx: Índice da linha atual.
        
        Returns:
            'CALL' para compra, 'PUT' para venda, None para sem sinal.
        """
        row = df.iloc[idx]
        
        # Verificar se temos a feature necessária
        if "rsi" not in row:
            return None
        
        rsi = row["rsi"]
        
        # RSI extremamente sobrevendido: esperar reversão para cima
        if rsi < self.rsi_oversold:
            return "CALL"
        
        # RSI extremamente sobrecomprado: esperar reversão para baixo
        elif rsi > self.rsi_overbought:
            return "PUT"
        
        return None
    
    def get_name(self) -> str:
        """Retorna o nome da estratégia."""
        return "meanrev"
