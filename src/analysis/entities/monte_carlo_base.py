"""
Monte Carlo simulation base class with pluggable distribution strategies.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd
from src.core.entities.portfolio import Portfolio
from src.analysis.entities.distribuition_generator import DistribuicaoBase, DistribuicaoNormal
import matplotlib.pyplot as plt
import seaborn as sns

class MonteCarloBase(ABC):
    """
    Classe base para simulações de Monte Carlo de portfólios.
    Implementa lógica comum e delega a geração de retornos à estratégia de distribuição.
    """

    def __init__(
        self,
        portfolio: Portfolio,
        n_simulacoes: int = 1000,
        taxa_livre_risco: float = 0.0,
        alpha: float = 0.05,
        distribution: Optional[DistribuicaoBase] = None,
        seed: Optional[int] = None,
    ):
        self.portfolio = portfolio
        self.returns_df = self.portfolio.series.get_returns()
        self.n_simulacoes = n_simulacoes
        self.taxa_livre_risco = taxa_livre_risco
        self.alpha = alpha
        self.resultados: Optional[pd.DataFrame] = None
        self.simulacoes: Optional[pd.DataFrame] = None

        # Estratégia de distribuição (Strategy)
        self.distribution = distribution or DistribuicaoNormal()

        if seed is not None:
            np.random.seed(seed)

    @abstractmethod
    def run(self) -> Any:
        """Executa a simulação Monte Carlo."""
        pass
