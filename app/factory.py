"""Factory para criar instâncias de brokers e data loaders."""

from typing import Any, Dict

from app.broker.base import BaseBroker
from app.broker.mock import MockBroker
from app.data.loaders import SyntheticDataLoader


def create_broker(config: Dict[str, Any]) -> BaseBroker:
    """Cria instância de broker baseado na configuração.
    
    Args:
        config: Dicionário de configuração.
    
    Returns:
        Instância de BaseBroker.
    """
    broker_config = config.get("broker", {})
    broker_type = broker_config.get("type", "mock")
    demo = broker_config.get("demo", True)
    
    if broker_type == "mock":
        print("Usando MockBroker (simulação)")
        return MockBroker()
    
    elif broker_type == "iqoption":
        from app.broker.iqoption import IQOptionBroker
        
        email = broker_config.get("email")
        password = broker_config.get("password")
        
        if not email or not password:
            raise ValueError(
                "Email e senha são obrigatórios para IQ Option.\n"
                "Configure em config.yaml ou use variáveis de ambiente:\n"
                "  IQOPTION_EMAIL e IQOPTION_PASSWORD"
            )
        
        print(f"Usando IQOptionBroker ({'DEMO' if demo else 'REAL'})")
        if not demo:
            print("⚠️  ATENÇÃO: Modo REAL ativado! Você usará dinheiro real!")
            confirm = input("Digite 'CONFIRMO' para continuar: ")
            if confirm != "CONFIRMO":
                raise ValueError("Operação cancelada pelo usuário")
        
        return IQOptionBroker(email, password, demo)
    
    elif broker_type == "quotex":
        from app.broker.iqoption import QuotexBroker
        
        email = broker_config.get("email")
        password = broker_config.get("password")
        
        if not email or not password:
            raise ValueError(
                "Email e senha são obrigatórios para Quotex.\n"
                "Configure em config.yaml"
            )
        
        print(f"Usando QuotexBroker ({'DEMO' if demo else 'REAL'})")
        return QuotexBroker(email, password, demo)
    
    else:
        raise ValueError(
            f"Tipo de broker desconhecido: {broker_type}\n"
            f"Opções: mock, iqoption, quotex"
        )


def create_data_loader(config: Dict[str, Any]):
    """Cria instância de data loader baseado na configuração.
    
    Args:
        config: Dicionário de configuração.
    
    Returns:
        Instância de data loader.
    """
    data_config = config.get("data", {})
    source = data_config.get("source", "synthetic")
    
    if source == "synthetic":
        print("Usando dados sintéticos (simulação)")
        return SyntheticDataLoader()
    
    elif source == "yfinance":
        from app.data.real_loader import RealDataLoader
        
        print("Usando dados reais do Yahoo Finance")
        return RealDataLoader()
    
    elif source == "alphavantage":
        from app.data.real_loader import AlphaVantageLoader
        
        api_key = data_config.get("alphavantage_api_key")
        if not api_key:
            raise ValueError(
                "API key do Alpha Vantage é obrigatória.\n"
                "Configure em config.yaml: data.alphavantage_api_key\n"
                "Obtenha uma chave gratuita em: https://www.alphavantage.co/support/#api-key"
            )
        
        print("Usando dados reais do Alpha Vantage")
        return AlphaVantageLoader(api_key)
    
    else:
        raise ValueError(
            f"Fonte de dados desconhecida: {source}\n"
            f"Opções: synthetic, yfinance, alphavantage"
        )
