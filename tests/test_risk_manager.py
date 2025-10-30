"""Testes para o gerenciador de risco."""

import pytest

from app.risk.manager import RiskManager


@pytest.fixture
def config():
    """Fixture com configuração de teste."""
    return {
        "risk": {
            "risk_per_trade": 0.01,
            "daily_loss_limit": -0.02,
            "daily_profit_target": 0.03,
            "min_payout": 0.80,
            "safety_margin": 0.02,
        }
    }


@pytest.fixture
def risk_manager(config):
    """Fixture com risk manager."""
    return RiskManager(config)


def test_calculate_stake(risk_manager):
    """Testa cálculo de stake."""
    balance = 1000.0
    stake = risk_manager.calculate_stake(balance)
    assert stake == 10.0  # 1% de 1000


def test_should_trade_low_payout(risk_manager):
    """Testa rejeição por payout baixo."""
    should_trade, reason = risk_manager.should_trade(
        p_win=0.60,
        payout=0.75,  # Abaixo do mínimo
        balance=1000.0,
    )
    assert not should_trade
    assert "Payout muito baixo" in reason


def test_should_trade_low_probability(risk_manager):
    """Testa rejeição por probabilidade baixa."""
    payout = 0.85
    p_star = 1 / (1 + payout)  # ~0.54
    threshold = p_star + 0.02  # ~0.56
    
    should_trade, reason = risk_manager.should_trade(
        p_win=0.55,  # Abaixo do threshold
        payout=payout,
        balance=1000.0,
    )
    assert not should_trade
    assert "threshold" in reason.lower()


def test_should_trade_success(risk_manager):
    """Testa aceitação de trade válido."""
    should_trade, reason = risk_manager.should_trade(
        p_win=0.65,  # Acima do threshold
        payout=0.85,
        balance=1000.0,
    )
    assert should_trade
    assert reason == "OK"


def test_daily_loss_limit(risk_manager):
    """Testa limite de perda diária."""
    risk_manager.daily_pnl = -2.5  # Abaixo do limite
    
    should_trade, reason = risk_manager.should_trade(
        p_win=0.70,
        payout=0.85,
        balance=1000.0,
    )
    assert not should_trade
    assert "perda diária" in reason.lower()


def test_daily_profit_target(risk_manager):
    """Testa meta de lucro diária."""
    risk_manager.daily_pnl = 3.5  # Acima da meta
    
    should_trade, reason = risk_manager.should_trade(
        p_win=0.70,
        payout=0.85,
        balance=1000.0,
    )
    assert not should_trade
    assert "lucro diária" in reason.lower()


def test_calculate_expectancy(risk_manager):
    """Testa cálculo de expectância."""
    expectancy = risk_manager.calculate_expectancy(p_win=0.60, payout=0.85)
    expected = (0.60 * 0.85) - (0.40 * 1.0)
    assert abs(expectancy - expected) < 0.001


def test_update_daily_pnl(risk_manager):
    """Testa atualização de PnL diário."""
    risk_manager.update_daily_pnl(1.5)
    assert risk_manager.daily_pnl == 1.5
    assert risk_manager.daily_trades == 1
    
    risk_manager.update_daily_pnl(-0.5)
    assert risk_manager.daily_pnl == 1.0
    assert risk_manager.daily_trades == 2


def test_reset_daily_stats(risk_manager):
    """Testa reset de estatísticas diárias."""
    risk_manager.update_daily_pnl(2.0)
    risk_manager.reset_daily_stats()

    assert risk_manager.daily_pnl == 0.0
    assert risk_manager.daily_trades == 0


def test_percent_normalization_from_integers(config):
    """Garante compatibilidade com valores antigos (inteiros)."""
    config["risk"]["daily_loss_limit"] = -2.0
    config["risk"]["daily_profit_target"] = 3.0

    manager = RiskManager(config)

    assert manager.daily_loss_limit_percent == pytest.approx(-0.02)
    assert manager.daily_profit_target_percent == pytest.approx(0.03)
