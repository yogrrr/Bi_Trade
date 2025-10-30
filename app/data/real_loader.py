"""Loader de dados reais de mercado."""

from datetime import datetime
from typing import Optional

import pandas as pd
import yfinance as yf


class RealDataLoader:
    """Carrega dados reais de mercado usando Yahoo Finance."""
    
    def load(
        self,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """Carrega dados históricos reais.
        
        Args:
            symbol: Símbolo do ativo (ex: EURUSD=X para forex).
            timeframe: Intervalo (1m, 5m, 15m, 1h, 1d).
            start_date: Data inicial (YYYY-MM-DD).
            end_date: Data final (YYYY-MM-DD).
        
        Returns:
            DataFrame com colunas: timestamp, open, high, low, close, volume.
        """
        # Mapear timeframe para formato do yfinance
        interval_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "1d": "1d",
        }
        
        interval = interval_map.get(timeframe, "1m")
        
        # Converter símbolo para formato Yahoo Finance
        # EURUSD -> EURUSD=X
        if len(symbol) == 6 and symbol[:3].isalpha() and symbol[3:].isalpha():
            yf_symbol = f"{symbol}=X"
        else:
            yf_symbol = symbol
        
        print(f"Carregando dados reais: {yf_symbol} ({timeframe})")
        
        try:
            # Baixar dados
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=True,
            )
            
            if df.empty:
                raise ValueError(f"Nenhum dado encontrado para {yf_symbol}")
            
            # Renomear colunas para formato padrão
            df = df.reset_index()
            df.columns = [col.lower() for col in df.columns]
            
            # Ajustar nome da coluna de timestamp
            if 'datetime' in df.columns:
                df.rename(columns={'datetime': 'timestamp'}, inplace=True)
            elif 'date' in df.columns:
                df.rename(columns={'date': 'timestamp'}, inplace=True)
            
            # Garantir que temos as colunas necessárias
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    if col == 'volume':
                        df[col] = 0  # Volume pode não estar disponível para forex
                    else:
                        raise ValueError(f"Coluna {col} não encontrada nos dados")
            
            # Selecionar apenas colunas necessárias
            df = df[required_cols]
            
            # Garantir tipos corretos
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            # Remover linhas com valores nulos
            df = df.dropna()
            
            print(f"✓ Carregados {len(df)} barras de dados reais")
            
            return df
            
        except Exception as e:
            print(f"✗ Erro ao carregar dados reais: {e}")
            print(f"Tentando símbolos alternativos...")
            
            # Tentar formatos alternativos
            alt_symbols = [
                symbol,  # Original
                f"{symbol}=X",  # Forex
                f"{symbol}.FX",  # Forex alternativo
            ]
            
            for alt_symbol in alt_symbols:
                try:
                    ticker = yf.Ticker(alt_symbol)
                    df = ticker.history(
                        start=start_date,
                        end=end_date,
                        interval=interval,
                        auto_adjust=True,
                    )
                    if not df.empty:
                        print(f"✓ Dados encontrados com símbolo: {alt_symbol}")
                        # Processar como acima
                        df = df.reset_index()
                        df.columns = [col.lower() for col in df.columns]
                        if 'datetime' in df.columns:
                            df.rename(columns={'datetime': 'timestamp'}, inplace=True)
                        elif 'date' in df.columns:
                            df.rename(columns={'date': 'timestamp'}, inplace=True)
                        df = df[required_cols]
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        for col in ['open', 'high', 'low', 'close', 'volume']:
                            df[col] = df[col].astype(float)
                        df = df.dropna()
                        return df
                except:
                    continue
            
            raise ValueError(
                f"Não foi possível carregar dados para {symbol}. "
                f"Verifique se o símbolo está correto. "
                f"Exemplos: EURUSD=X (forex), AAPL (ações), BTC-USD (crypto)"
            )


class AlphaVantageLoader:
    """Loader alternativo usando Alpha Vantage (requer API key)."""
    
    def __init__(self, api_key: str):
        """Inicializa o loader.
        
        Args:
            api_key: Chave da API do Alpha Vantage.
        """
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    def load(
        self,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """Carrega dados do Alpha Vantage.
        
        Args:
            symbol: Símbolo do ativo.
            timeframe: Intervalo.
            start_date: Data inicial.
            end_date: Data final.
        
        Returns:
            DataFrame com dados de mercado.
        """
        import requests
        
        # Mapear timeframe para função do Alpha Vantage
        function_map = {
            "1m": "TIME_SERIES_INTRADAY",
            "5m": "TIME_SERIES_INTRADAY",
            "15m": "TIME_SERIES_INTRADAY",
            "30m": "TIME_SERIES_INTRADAY",
            "1h": "TIME_SERIES_INTRADAY",
            "1d": "TIME_SERIES_DAILY",
        }
        
        interval_map = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "1h": "60min",
        }
        
        function = function_map.get(timeframe, "TIME_SERIES_INTRADAY")
        interval = interval_map.get(timeframe, "1min")
        
        params = {
            "function": function,
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": "full",
        }
        
        if function == "TIME_SERIES_INTRADAY":
            params["interval"] = interval
        
        print(f"Carregando dados do Alpha Vantage: {symbol}")
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        # Processar resposta
        if "Error Message" in data:
            raise ValueError(f"Erro da API: {data['Error Message']}")
        
        # Extrair série temporal
        time_series_key = [k for k in data.keys() if "Time Series" in k][0]
        time_series = data[time_series_key]
        
        # Converter para DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Renomear colunas
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df = df.reset_index().rename(columns={'index': 'timestamp'})
        
        # Filtrar por data
        df = df[
            (df['timestamp'] >= start_date) &
            (df['timestamp'] <= end_date)
        ]
        
        # Converter tipos
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        print(f"✓ Carregados {len(df)} barras do Alpha Vantage")
        
        return df
