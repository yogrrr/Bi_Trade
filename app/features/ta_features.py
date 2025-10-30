"""Cálculo de indicadores técnicos e features."""

from typing import Any

import numpy as np
import pandas as pd


class TechnicalFeatures:
    """Classe para calcular indicadores técnicos."""
    
    @staticmethod
    def ema(series: pd.Series, period: int) -> pd.Series:
        """Calcula a Média Móvel Exponencial (EMA).
        
        Args:
            series: Série de preços.
            period: Período da EMA.
        
        Returns:
            Série com valores da EMA.
        """
        return series.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def sma(series: pd.Series, period: int) -> pd.Series:
        """Calcula a Média Móvel Simples (SMA).
        
        Args:
            series: Série de preços.
            period: Período da SMA.
        
        Returns:
            Série com valores da SMA.
        """
        return series.rolling(window=period).mean()
    
    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Calcula o Índice de Força Relativa (RSI).
        
        Args:
            series: Série de preços.
            period: Período do RSI.
        
        Returns:
            Série com valores do RSI.
        """
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcula o Average True Range (ATR).
        
        Args:
            df: DataFrame com colunas high, low, close.
            period: Período do ATR.
        
        Returns:
            Série com valores do ATR.
        """
        high = df["high"]
        low = df["low"]
        close = df["close"]
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def donchian_channel(df: pd.DataFrame, period: int = 20) -> tuple[pd.Series, pd.Series]:
        """Calcula o Canal de Donchian.
        
        Args:
            df: DataFrame com colunas high, low.
            period: Período do canal.
        
        Returns:
            Tupla com (upper_band, lower_band).
        """
        upper = df["high"].rolling(window=period).max()
        lower = df["low"].rolling(window=period).min()
        
        return upper, lower
    
    @staticmethod
    def add_all_features(df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
        """Adiciona todas as features técnicas ao DataFrame.
        
        Args:
            df: DataFrame com dados OHLCV.
            config: Dicionário de configuração.
        
        Returns:
            DataFrame com features adicionadas.
        """
        df = df.copy()
        
        # EMAs para estratégia de tendência
        if config.get("strategies", {}).get("trend", {}).get("enabled", False):
            ema_fast = config["strategies"]["trend"]["ema_fast"]
            ema_slow = config["strategies"]["trend"]["ema_slow"]
            atr_period = config["strategies"]["trend"]["atr_period"]
            
            df["ema_fast"] = TechnicalFeatures.ema(df["close"], ema_fast)
            df["ema_slow"] = TechnicalFeatures.ema(df["close"], ema_slow)
            df["atr"] = TechnicalFeatures.atr(df, atr_period)
        
        # RSI para estratégia de reversão
        if config.get("strategies", {}).get("meanrev", {}).get("enabled", False):
            rsi_period = config["strategies"]["meanrev"]["rsi_period"]
            df["rsi"] = TechnicalFeatures.rsi(df["close"], rsi_period)
        
        # Donchian para estratégia de breakout
        if config.get("strategies", {}).get("breakout", {}).get("enabled", False):
            donchian_period = config["strategies"]["breakout"]["donchian_period"]
            df["donchian_upper"], df["donchian_lower"] = TechnicalFeatures.donchian_channel(
                df, donchian_period
            )
        
        # Features adicionais
        df["returns"] = df["close"].pct_change()
        df["volatility"] = df["returns"].rolling(window=20).std()
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        df["day_of_week"] = pd.to_datetime(df["timestamp"]).dt.dayofweek
        
        # Remover NaN
        df = df.dropna()
        
        return df
    
    @staticmethod
    def extract_feature_vector(row: pd.Series, config: dict[str, Any]) -> np.ndarray:
        """Extrai vetor de features de uma linha do DataFrame.
        
        Args:
            row: Linha do DataFrame com features.
            config: Dicionário de configuração.
        
        Returns:
            Array numpy com features.
        """
        features = []
        
        # Features de tendência
        if config.get("strategies", {}).get("trend", {}).get("enabled", False):
            features.extend([
                row["ema_fast"],
                row["ema_slow"],
                row["ema_fast"] - row["ema_slow"],
                row["atr"],
            ])
        
        # Features de reversão
        if config.get("strategies", {}).get("meanrev", {}).get("enabled", False):
            features.append(row["rsi"])
        
        # Features de breakout
        if config.get("strategies", {}).get("breakout", {}).get("enabled", False):
            features.extend([
                row["donchian_upper"],
                row["donchian_lower"],
                row["close"] - row["donchian_upper"],
                row["close"] - row["donchian_lower"],
            ])
        
        # Features adicionais
        features.extend([
            row["returns"],
            row["volatility"],
            row["hour"],
            row["day_of_week"],
        ])
        
        return np.array(features, dtype=np.float32)
