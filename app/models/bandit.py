"""Bandit contextual para seleção de estratégias."""

import random
from typing import Any

import numpy as np


class ContextualBandit:
    """Bandit contextual epsilon-greedy para seleção de estratégias."""
    
    def __init__(self, strategies: list[str], epsilon: float = 0.1) -> None:
        """Inicializa o bandit contextual.
        
        Args:
            strategies: Lista de nomes de estratégias.
            epsilon: Taxa de exploração (0-1).
        """
        self.strategies = strategies
        self.epsilon = epsilon
        self.rewards: dict[str, list[float]] = {s: [] for s in strategies}
        self.counts: dict[str, int] = {s: 0 for s in strategies}
    
    def select_strategy(self, context: dict[str, Any]) -> str:
        """Seleciona uma estratégia baseada no contexto.
        
        Args:
            context: Dicionário com informações contextuais (horário, volatilidade, etc.).
        
        Returns:
            Nome da estratégia selecionada.
        """
        # Exploração: escolher aleatoriamente
        if random.random() < self.epsilon:
            return random.choice(self.strategies)
        
        # Exploitação: escolher a melhor estratégia
        best_strategy = max(
            self.strategies,
            key=lambda s: self._get_average_reward(s),
        )
        
        return best_strategy
    
    def update(self, strategy: str, reward: float) -> None:
        """Atualiza as recompensas de uma estratégia.
        
        Args:
            strategy: Nome da estratégia.
            reward: Recompensa obtida (1 para vitória, 0 para derrota).
        """
        self.rewards[strategy].append(reward)
        self.counts[strategy] += 1
    
    def _get_average_reward(self, strategy: str) -> float:
        """Calcula a recompensa média de uma estratégia.
        
        Args:
            strategy: Nome da estratégia.
        
        Returns:
            Recompensa média.
        """
        if self.counts[strategy] == 0:
            return 0.5  # Valor neutro para estratégias não testadas
        
        return np.mean(self.rewards[strategy])
    
    def get_stats(self) -> dict[str, dict[str, float]]:
        """Retorna estatísticas das estratégias.
        
        Returns:
            Dicionário com estatísticas de cada estratégia.
        """
        stats = {}
        
        for strategy in self.strategies:
            stats[strategy] = {
                "count": self.counts[strategy],
                "avg_reward": self._get_average_reward(strategy),
                "win_rate": self._get_average_reward(strategy),
            }
        
        return stats
