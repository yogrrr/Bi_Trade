"""Gerenciamento de configurações."""

import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Literal

import yaml
from dotenv import load_dotenv


def synchronize_risk_aliases(
    config_data: dict[str, Any],
    prefer: Literal["stake_percent", "risk_per_trade", None] = None,
) -> None:
    """Mantém os aliases de risco em sincronia.

    A interface utiliza ``stake_percent`` como representação em percentual
    enquanto os componentes internos utilizam ``risk_per_trade``. Esta função
    garante que ambos os valores permaneçam iguais independentemente de qual
    foi alterado.

    Args:
        config_data: Dicionário completo de configuração.
        prefer: Campo que deve prevalecer caso ambos existam com valores
            diferentes. Quando ``None`` é utilizado, ``stake_percent`` tem
            prioridade por representar o valor exibido na interface.
    """

    risk_config = config_data.get("risk")
    if not isinstance(risk_config, dict):
        return

    stake_percent = risk_config.get("stake_percent")
    risk_per_trade = risk_config.get("risk_per_trade")

    if prefer == "stake_percent" and stake_percent is not None:
        risk_config["risk_per_trade"] = stake_percent
    elif prefer == "risk_per_trade" and risk_per_trade is not None:
        risk_config["stake_percent"] = risk_per_trade
    else:
        if stake_percent is None and risk_per_trade is not None:
            risk_config["stake_percent"] = risk_per_trade
            stake_percent = risk_per_trade
        elif risk_per_trade is None and stake_percent is not None:
            risk_config["risk_per_trade"] = stake_percent
            risk_per_trade = stake_percent

        if (
            stake_percent is not None
            and risk_per_trade is not None
            and stake_percent != risk_per_trade
        ):
            # Priorizar o valor exibido na interface para manter consistência visual
            risk_config["risk_per_trade"] = stake_percent
            risk_config["stake_percent"] = stake_percent


def deep_merge_dicts(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """Realiza merge profundo entre dois dicionários sem mutar os originais."""

    result: dict[str, Any] = deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def apply_config_overrides(
    base_config: dict[str, Any],
    overrides: dict[str, Any],
    *,
    prefer_alias: Literal["stake_percent", "risk_per_trade", None] | None = None,
) -> dict[str, Any]:
    """Aplica overrides mantendo aliases de risco sincronizados."""

    merged = deep_merge_dicts(base_config, overrides)

    prefer = prefer_alias
    risk_override = overrides.get("risk") if isinstance(overrides, dict) else None
    if prefer is None and isinstance(risk_override, dict):
        if "stake_percent" in risk_override:
            prefer = "stake_percent"
        elif "risk_per_trade" in risk_override:
            prefer = "risk_per_trade"

    synchronize_risk_aliases(merged, prefer=prefer)
    return merged


class Config:
    """Classe para gerenciar configurações do projeto."""

    def __init__(self, config_path: str = "config.yaml") -> None:
        """Inicializa as configurações.
        
        Args:
            config_path: Caminho para o arquivo de configuração YAML.
        """
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Carregar configurações do YAML
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        
        with open(config_file, "r", encoding="utf-8") as f:
            self._config: dict[str, Any] = yaml.safe_load(f)

        # Garantir que aliases permaneçam sincronizados
        synchronize_risk_aliases(self._config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração.
        
        Args:
            key: Chave de configuração (suporta notação de ponto, ex: 'risk.risk_per_trade').
            default: Valor padrão se a chave não existir.
        
        Returns:
            Valor da configuração.
        """
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_env(self, key: str, default: str = "") -> str:
        """Obtém uma variável de ambiente.
        
        Args:
            key: Nome da variável de ambiente.
            default: Valor padrão se a variável não existir.
        
        Returns:
            Valor da variável de ambiente.
        """
        return os.getenv(key, default)
    
    @property
    def symbol(self) -> str:
        """Retorna o símbolo configurado."""
        return str(self.get("symbol", "EURUSD"))
    
    @property
    def timeframe(self) -> str:
        """Retorna o timeframe configurado."""
        return str(self.get("timeframe", "1m"))
    
    @property
    def expiry(self) -> int:
        """Retorna a expiração em segundos."""
        return int(self.get("expiry", 120))
    
    @property
    def risk_per_trade(self) -> float:
        """Retorna o risco por trade."""
        return float(self.get("risk.risk_per_trade", 0.01))
    
    @property
    def daily_loss_limit(self) -> float:
        """Retorna o limite de perda diária."""
        return float(self.get("risk.daily_loss_limit", -0.02))

    @property
    def daily_profit_target(self) -> float:
        """Retorna a meta de lucro diária."""
        return float(self.get("risk.daily_profit_target", 0.03))
    
    @property
    def min_payout(self) -> float:
        """Retorna o payout mínimo aceitável."""
        return float(self.get("risk.min_payout", 0.80))
    
    @property
    def safety_margin(self) -> float:
        """Retorna a margem de segurança."""
        return float(self.get("risk.safety_margin", 0.02))
    
    @property
    def initial_balance(self) -> float:
        """Retorna o saldo inicial."""
        mode = self.get_env("TRADING_MODE", "demo")
        if mode == "demo":
            return float(self.get("live.initial_balance", 1000.0))
        return float(self.get("backtest.initial_balance", 1000.0))


# Instância global de configuração
config = Config()
