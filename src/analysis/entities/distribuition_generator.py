from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from src.core.entities.portfolio import Portfolio

class DistribuicaoBase(ABC):
    """Interface para geração de distribuições de retornos simulados."""

    @abstractmethod
    def gerar_amostras(self, media: np.ndarray, cov: np.ndarray, n_amostras: int) -> np.ndarray:
        pass


class DistribuicaoNormal(DistribuicaoBase):
    """Distribuição normal multivariada padrão (Markowitz)."""

    def gerar_amostras(self, media, cov, n_amostras):
        return np.random.multivariate_normal(media, cov, n_amostras)


class DistribuicaoLogNormal(DistribuicaoBase):
    """Distribuição lognormal (para retornos sempre positivos)."""

    def gerar_amostras(self, media, cov, n_amostras):
        normais = np.random.multivariate_normal(media, cov, n_amostras)
        return np.exp(normais) - 1

class DistribuicaoEmpirica(DistribuicaoBase):
    """Distribuição baseada em amostragem bootstrap dos retornos históricos."""

    def __init__(self, retornos_historicos: pd.DataFrame):
        self.retornos_historicos = retornos_historicos.values

    def gerar_amostras(self, media, cov, n_amostras):
        n_periodos, n_ativos = self.retornos_historicos.shape
        idx = np.random.choice(n_periodos, n_amostras, replace=True)
        return self.retornos_historicos[idx, :]
