"""Gerenciamento de risco e sizing."""

from typing import Any


class RiskManager:
    """Gerenciador de risco para trading de opções binárias."""
    
    def __init__(self, config: dict[str, Any]) -> None:
        """Inicializa o gerenciador de risco.
        
        Args:
            config: Dicionário de configuração.
        """
        self.config = config
        self.risk_per_trade = config["risk"]["risk_per_trade"]
        self.daily_loss_limit_percent = self._normalize_percent(
            config["risk"].get("daily_loss_limit", -0.02)
        )
        self.daily_profit_target_percent = self._normalize_percent(
            config["risk"].get("daily_profit_target", 0.03)
        )
        self.min_payout = config["risk"]["min_payout"]
        self.safety_margin = config["risk"]["safety_margin"]
        
        # Martingale
        self.martingale_enabled = config["risk"].get("martingale_enabled", False)
        self.martingale_multiplier = config["risk"].get("martingale_multiplier", 1.5)
        self.martingale_max_steps = config["risk"].get("martingale_max_steps", 3)
        self.martingale_step = 0
        self.consecutive_losses = 0
        
        # Estado diário
        self.daily_pnl = 0.0
        self.daily_trades = 0
    
    def calculate_stake(self, balance: float) -> float:
        """Calcula o tamanho da aposta baseado no saldo.
        
        Args:
            balance: Saldo atual.
        
        Returns:
            Tamanho da aposta.
        """
        base_stake = balance * self.risk_per_trade
        
        # Aplicar martingale se habilitado
        if self.martingale_enabled and self.martingale_step > 0:
            multiplier = self.martingale_multiplier ** self.martingale_step
            return base_stake * multiplier
        
        return base_stake
    
    def should_trade(
        self,
        p_win: float,
        payout: float,
        balance: float,
    ) -> tuple[bool, str]:
        """Determina se deve realizar o trade.
        
        Args:
            p_win: Probabilidade de vitória (0-1).
            payout: Payout oferecido (ex: 0.85 para 85%).
            balance: Saldo atual.
        
        Returns:
            Tupla (should_trade, reason).
        """
        # Verificar payout mínimo
        if payout < self.min_payout:
            return False, f"Payout muito baixo: {payout:.2%} < {self.min_payout:.2%}"
        
        # Calcular p_star (breakeven probability)
        p_star = 1 / (1 + payout)
        
        # Verificar se P(win) > p_star + margem
        threshold = p_star + self.safety_margin
        if p_win <= threshold:
            return False, f"P(win) {p_win:.2%} <= threshold {threshold:.2%}"
        
        # Verificar limites percentuais diários
        daily_return = self.daily_pnl * self.risk_per_trade

        if daily_return <= self.daily_loss_limit_percent:
            return False, (
                "Limite de perda diária atingido: "
                f"{daily_return:.2%} <= {self.daily_loss_limit_percent:.2%}"
            )

        if daily_return >= self.daily_profit_target_percent:
            return False, (
                "Meta de lucro diária atingida: "
                f"{daily_return:.2%} >= {self.daily_profit_target_percent:.2%}"
            )
        
        # Verificar saldo mínimo
        stake = self.calculate_stake(balance)
        if stake > balance:
            return False, f"Saldo insuficiente: {balance:.2f} < {stake:.2f}"
        
        return True, "OK"
    
    def update_daily_pnl(self, pnl: float) -> None:
        """Atualiza o PnL diário.
        
        Args:
            pnl: Lucro/prejuízo do trade em múltiplos de R.
        """
        self.daily_pnl += pnl
        self.daily_trades += 1
        
        # Atualizar estado do martingale
        if self.martingale_enabled:
            if pnl < 0:  # Loss
                self.consecutive_losses += 1
                if self.martingale_step < self.martingale_max_steps:
                    self.martingale_step += 1
            else:  # Win
                self.consecutive_losses = 0
                self.martingale_step = 0  # Reset martingale após win
    
    def reset_daily_stats(self) -> None:
        """Reseta as estatísticas diárias."""
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.martingale_step = 0
        self.consecutive_losses = 0
    
    def get_daily_stats(self) -> dict[str, Any]:
        """Retorna estatísticas diárias.
        
        Returns:
            Dicionário com estatísticas.
        """
        return {
            "daily_pnl": self.daily_pnl,
            "daily_pnl_percent": self.daily_pnl * self.risk_per_trade,
            "daily_trades": self.daily_trades,
            "martingale_step": self.martingale_step,
            "consecutive_losses": self.consecutive_losses,
        }

    @staticmethod
    def _normalize_percent(value: float) -> float:
        """Normaliza valores percentuais recebidos da configuração."""

        if value is None:
            return 0.0

        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0

        if abs(numeric) > 1:
            return numeric / 100.0

        return numeric
    
    def calculate_expectancy(self, p_win: float, payout: float) -> float:
        """Calcula a expectância matemática do trade.
        
        Args:
            p_win: Probabilidade de vitória (0-1).
            payout: Payout oferecido (ex: 0.85 para 85%).
        
        Returns:
            Expectância em múltiplos de R.
        """
        p_loss = 1 - p_win
        expectancy = (p_win * payout) - (p_loss * 1.0)
        return expectancy
