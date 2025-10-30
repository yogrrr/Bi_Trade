"""Sistema de logging estruturado."""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formatter para logs em formato JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o log em JSON.
        
        Args:
            record: Registro de log.
        
        Returns:
            String JSON formatada.
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Adicionar campos extras
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


def setup_logging(config: dict[str, Any]) -> None:
    """Configura o sistema de logging.
    
    Args:
        config: Dicionário de configuração.
    """
    log_level = config.get("logging", {}).get("level", "INFO")
    log_format = config.get("logging", {}).get("format", "json")
    log_file = config.get("logging", {}).get("file", "logs/trading.log")
    
    # Criar diretório de logs
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configurar formato
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Configurar handlers
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Obtém um logger.
    
    Args:
        name: Nome do logger.
    
    Returns:
        Instância do logger.
    """
    return logging.getLogger(name)
