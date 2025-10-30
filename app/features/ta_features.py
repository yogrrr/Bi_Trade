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
    def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
        """Calcula o MACD (Moving Average Convergence Divergence).
        
        Args:
            series: Série de preços.
            fast: Período da EMA rápida.
            slow: Período da EMA lenta.
            signal: Período da linha de sinal.
        
        Returns:
            Tupla com (macd_line, signal_line, histogram).
        """
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
        """Calcula as Bandas de Bollinger.
        
        Args:
            series: Série de preços.
            period: Período da média móvel.
            std_dev: Número de desvios padrão.
        
        Returns:
            Tupla com (upper_band, middle_band, lower_band).
        """
        middle = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper, middle, lower
    
    @staticmethod
    def stochastic(df: pd.DataFrame, period: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> tuple[pd.Series, pd.Series]:
        """Calcula o Oscilador Estocástico.
        
        Args:
            df: DataFrame com colunas high, low, close.
            period: Período do estocástico.
            smooth_k: Período de suavização do %K.
            smooth_d: Período de suavização do %D.
        
        Returns:
            Tupla com (%K, %D).
        """
        low_min = df["low"].rolling(window=period).min()
        high_max = df["high"].rolling(window=period).max()
        
        k = 100 * ((df["close"] - low_min) / (high_max - low_min))
        k = k.rolling(window=smooth_k).mean()
        d = k.rolling(window=smooth_d).mean()
        
        return k, d
    
    @staticmethod
    def adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcula o Average Directional Index (ADX).
        
        Args:
            df: DataFrame com colunas high, low, close.
            period: Período do ADX.
        
        Returns:
            Série com valores do ADX.
        """
        high = df["high"]
        low = df["low"]
        close = df["close"]
        
        # Calcular +DM e -DM
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # Calcular TR (True Range)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Suavizar com EMA
        atr = tr.ewm(span=period, adjust=False).mean()
        plus_di = 100 * (plus_dm.ewm(span=period, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(span=period, adjust=False).mean() / atr)
        
        # Calcular DX e ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.ewm(span=period, adjust=False).mean()
        
        return adx
    
    @staticmethod
    def cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calcula o Commodity Channel Index (CCI).
        
        Args:
            df: DataFrame com colunas high, low, close.
            period: Período do CCI.
        
        Returns:
            Série com valores do CCI.
        """
        tp = (df["high"] + df["low"] + df["close"]) / 3
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean())
        
        cci = (tp - sma_tp) / (0.015 * mad)
        
        return cci
    
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
        
        # Indicadores adicionais (sempre calculados para enriquecer o modelo)
        df["macd"], df["macd_signal"], df["macd_hist"] = TechnicalFeatures.macd(df["close"])
        df["bb_upper"], df["bb_middle"], df["bb_lower"] = TechnicalFeatures.bollinger_bands(df["close"])
        df["stoch_k"], df["stoch_d"] = TechnicalFeatures.stochastic(df)
        df["adx"] = TechnicalFeatures.adx(df)
        df["cci"] = TechnicalFeatures.cci(df)
        
        # Features derivadas
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]  # Largura das bandas normalizada
        df["bb_position"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])  # Posição nas bandas
        df["price_to_sma20"] = df["close"] / TechnicalFeatures.sma(df["close"], 20)  # Distância da SMA20
        
        # Features adicionais
        df["returns"] = df["close"].pct_change()
        df["volatility"] = df["returns"].rolling(window=20).std()
        df["volume_sma"] = df["volume"].rolling(window=20).mean() if "volume" in df.columns else 0
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
        
        # Indicadores adicionais (sempre incluídos)
        features.extend([
            row["macd"],
            row["macd_signal"],
            row["macd_hist"],
            row["bb_upper"],
            row["bb_middle"],
            row["bb_lower"],
            row["bb_width"],
            row["bb_position"],
            row["stoch_k"],
            row["stoch_d"],
            row["adx"],
            row["cci"],
            row["price_to_sma20"],
        ])
        
        # Features adicionais
        features.extend([
            row["returns"],
            row["volatility"],
            row["volume_sma"] if "volume_sma" in row else 0,
            row["hour"],
            row["day_of_week"],
        ])
        
        return np.array(features, dtype=np.float32)
