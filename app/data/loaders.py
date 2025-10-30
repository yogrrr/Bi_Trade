"""Carregadores de dados de mercado."""

from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd


class DataLoader:
    """Classe base para carregamento de dados."""
    
    def load(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Carrega dados de mercado.
        
        Args:
            symbol: Símbolo do ativo (ex: EURUSD).
            timeframe: Timeframe (ex: 1m, 5m, 15m).
            start_date: Data inicial (formato: YYYY-MM-DD).
            end_date: Data final (formato: YYYY-MM-DD).
        
        Returns:
            DataFrame com colunas: timestamp, open, high, low, close, volume.
        """
        raise NotImplementedError


class SyntheticDataLoader(DataLoader):
    """Carregador de dados sintéticos para demonstração."""
    
    def load(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Gera dados sintéticos para demonstração.
        
        Args:
            symbol: Símbolo do ativo (ex: EURUSD).
            timeframe: Timeframe (ex: 1m, 5m, 15m).
            start_date: Data inicial (formato: YYYY-MM-DD).
            end_date: Data final (formato: YYYY-MM-DD).
        
        Returns:
            DataFrame com dados sintéticos.
        """
        # Converter timeframe para minutos
        timeframe_minutes = self._parse_timeframe(timeframe)
        
        # Definir datas
        if start_date is None:
            start = datetime.now() - timedelta(days=30)
        else:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        
        if end_date is None:
            end = datetime.now()
        else:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Gerar timestamps
        timestamps = pd.date_range(start=start, end=end, freq=f"{timeframe_minutes}min")
        n = len(timestamps)
        
        # Gerar preços sintéticos com tendência e ruído
        np.random.seed(42)
        trend = np.linspace(1.1000, 1.1200, n)
        noise = np.random.normal(0, 0.0010, n)
        close = trend + noise
        
        # Gerar OHLC
        high = close + np.abs(np.random.normal(0, 0.0005, n))
        low = close - np.abs(np.random.normal(0, 0.0005, n))
        open_price = close + np.random.normal(0, 0.0003, n)
        volume = np.random.randint(100, 1000, n)
        
        # Criar DataFrame
        df = pd.DataFrame({
            "timestamp": timestamps,
            "open": open_price,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        })
        
        return df
    
    def _parse_timeframe(self, timeframe: str) -> int:
        """Converte timeframe para minutos.
        
        Args:
            timeframe: Timeframe (ex: 1m, 5m, 15m, 1h).
        
        Returns:
            Número de minutos.
        """
        if timeframe.endswith("m"):
            return int(timeframe[:-1])
        elif timeframe.endswith("h"):
            return int(timeframe[:-1]) * 60
        elif timeframe.endswith("d"):
            return int(timeframe[:-1]) * 1440
        else:
            raise ValueError(f"Timeframe inválido: {timeframe}")


class CSVDataLoader(DataLoader):
    """Carregador de dados de arquivos CSV."""
    
    def __init__(self, csv_path: str) -> None:
        """Inicializa o carregador CSV.
        
        Args:
            csv_path: Caminho para o arquivo CSV.
        """
        self.csv_path = csv_path
    
    def load(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Carrega dados de um arquivo CSV.
        
        Args:
            symbol: Símbolo do ativo (ex: EURUSD).
            timeframe: Timeframe (ex: 1m, 5m, 15m).
            start_date: Data inicial (formato: YYYY-MM-DD).
            end_date: Data final (formato: YYYY-MM-DD).
        
        Returns:
            DataFrame com dados do CSV.
        """
        df = pd.read_csv(self.csv_path)
        
        # Converter timestamp para datetime
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Filtrar por data
        if start_date:
            df = df[df["timestamp"] >= start_date]
        if end_date:
            df = df[df["timestamp"] <= end_date]
        
        return df
