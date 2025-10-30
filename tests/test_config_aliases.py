"""Testes para sincronização de aliases de risco."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.config import Config, synchronize_risk_aliases


def test_synchronize_risk_aliases_prefers_stake_percent() -> None:
    config_dict = {"risk": {"stake_percent": 0.02, "risk_per_trade": 0.01}}

    synchronize_risk_aliases(config_dict, prefer="stake_percent")

    assert config_dict["risk"]["risk_per_trade"] == pytest.approx(0.02)
    assert config_dict["risk"]["stake_percent"] == pytest.approx(0.02)


def test_synchronize_risk_aliases_adds_missing_alias() -> None:
    config_dict = {"risk": {"stake_percent": 0.03}}

    synchronize_risk_aliases(config_dict)

    assert config_dict["risk"]["risk_per_trade"] == pytest.approx(0.03)
    assert config_dict["risk"]["stake_percent"] == pytest.approx(0.03)


def test_config_initialization_synchronizes_aliases(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    raw_config = {
        "symbol": "EURUSD",
        "risk": {"stake_percent": 0.025},
    }

    config_path.write_text(yaml.safe_dump(raw_config), encoding="utf-8")

    cfg = Config(str(config_path))

    assert cfg._config["risk"]["stake_percent"] == pytest.approx(0.025)
    assert cfg._config["risk"]["risk_per_trade"] == pytest.approx(0.025)
