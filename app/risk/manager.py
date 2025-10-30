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
        self.daily_loss_limit = config["risk"]["daily_loss_limit"]
        self.daily_profit_target = config["risk"]["daily_profit_target"]
        self.min_payout = config["risk"]["min_payout"]
        self.safety_margin = config["risk"]["safety_margin"]
        
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
        return balance * self.risk_per_trade
    
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
        
        # Verificar limite de perda diária
        if self.daily_pnl <= self.daily_loss_limit:
            return False, f"Limite de perda diária atingido: {self.daily_pnl:.2f}R"
        
        # Verificar meta de lucro diária
        if self.daily_pnl >= self.daily_profit_target:
            return False, f"Meta de lucro diária atingida: {self.daily_pnl:.2f}R"
        
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
    
    def reset_daily_stats(self) -> None:
        """Reseta as estatísticas diárias."""
        self.daily_pnl = 0.0
        self.daily_trades = 0
    
    def get_daily_stats(self) -> dict[str, Any]:
        """Retorna estatísticas diárias.
        
        Returns:
            Dicionário com estatísticas.
        """
        return {
            "daily_pnl": self.daily_pnl,
            "daily_trades": self.daily_trades,
        }
    
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
