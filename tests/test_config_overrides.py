"""Testes para merges de configuração e overrides."""

from __future__ import annotations

import pytest

from app.config import apply_config_overrides


def test_apply_config_overrides_merges_without_mutating_original() -> None:
    base = {
        "risk": {"risk_per_trade": 0.01, "stake_percent": 0.01, "min_payout": 0.8},
        "strategies": {"trend": {"enabled": True}},
    }
    overrides = {
        "risk": {"stake_percent": 0.03},
        "strategies": {"trend": {"enabled": False}},
    }

    merged = apply_config_overrides(base, overrides)

    assert merged["risk"]["risk_per_trade"] == pytest.approx(0.03)
    assert merged["risk"]["stake_percent"] == pytest.approx(0.03)
    assert merged["risk"]["min_payout"] == pytest.approx(0.8)
    assert merged["strategies"]["trend"]["enabled"] is False

    # Garantir que base permanece inalterado
    assert base["risk"]["risk_per_trade"] == pytest.approx(0.01)
    assert base["risk"]["stake_percent"] == pytest.approx(0.01)
    assert base["strategies"]["trend"]["enabled"] is True


def test_apply_config_overrides_prefers_risk_per_trade_when_specified() -> None:
    base = {"risk": {"risk_per_trade": 0.02, "stake_percent": 0.02}}
    overrides = {"risk": {"risk_per_trade": 0.05}}

    merged = apply_config_overrides(base, overrides)

    assert merged["risk"]["risk_per_trade"] == pytest.approx(0.05)
    assert merged["risk"]["stake_percent"] == pytest.approx(0.05)
