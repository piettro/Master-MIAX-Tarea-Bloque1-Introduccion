"""
Monte Carlo simulation: portfolio weight allocation using historical returns.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any
from src.analysis.entities.monte_carlo_base import MonteCarloBase


class MonteCarloPortfolio(MonteCarloBase):
    """
    Simulação de Monte Carlo variando pesos de alocação em um portfólio,
    utilizando retornos históricos reais dos ativos.

    Essa simulação mantém a estrutura temporal e as correlações reais do mercado,
    variando apenas as combinações de pesos para encontrar distribuições possíveis
    de retorno e risco.
    """

    def __init__(
        self,
        portfolio,
        n_simulacoes: int = 1000,
        taxa_livre_risco: float = 0.0,
        capital_inicial: float = 10000.0,
        metodo_pesos: str = "dirichlet",
        seed: int = None
    ):
        """
        Parâmetros
        ----------
        portfolio : Portfolio
            Instância da classe Portfolio, contendo os retornos históricos dos ativos.
        n_simulacoes : int
            Número de simulações a serem executadas.
        taxa_livre_risco : float
            Taxa livre de risco anualizada.
        capital_inicial : float
            Valor inicial do capital investido.
        seed : int, opcional
            Semente aleatória para reprodutibilidade.
        """
        super().__init__(
            portfolio=portfolio,
            n_simulacoes=n_simulacoes,
            taxa_livre_risco=taxa_livre_risco,
            seed=seed
        )

        self.capital_inicial = capital_inicial
        self.retornos_historicos = self.portfolio.series.get_returns()
        self.ativos = self.retornos_historicos.columns
        self.n_ativos = len(self.ativos)
        self.simulacoes: pd.DataFrame = pd.DataFrame(columns=["Retorno", "Valor", "Simulação"])
        self.metodo_pesos = metodo_pesos

    # --------------------------------------------------------------
    # Método principal da simulação
    # --------------------------------------------------------------
    def run(self) -> pd.DataFrame:
        """
        Executa a simulação de Monte Carlo variando apenas os pesos,
        utilizando os retornos históricos dos ativos.

        Returns:
            pd.DataFrame: DataFrame com simulações expandidas contendo:
                - Ativo: nome do ativo
                - Data: data da simulação
                - Peso: peso do ativo na carteira
                - Valor: valor do ativo
                - Valor Total: soma total da carteira
                - Retorno: retorno do ativo
                - Simulação: número da simulação
        """
        simulacoes_lista = []

        for sim in range(self.n_simulacoes):
            # 1. Gera pesos aleatórios
            pesos = self._gerar_pesos()

            # 2. Criar DataFrame de retornos históricos por ativo
            df_retornos = self.retornos_historicos.copy()

            # 3. Calcular valores e retornos para cada ativo
            for ativo in self.ativos:
                peso_ativo = pesos[list(self.ativos).index(ativo)]
                retornos_ativo = df_retornos[ativo]
                valores_ativo = self.capital_inicial * peso_ativo * (1 + retornos_ativo).cumprod()
                valor_total = self.capital_inicial * (1 + df_retornos).dot(pesos).cumprod()

                # Criar DataFrame para o ativo atual
                df_ativo = pd.DataFrame({
                    'Ativo': ativo,
                    'Data': df_retornos.index,
                    'Peso': peso_ativo,
                    'Valor': valores_ativo,
                    'Valor Total': valor_total,
                    'Retorno': retornos_ativo,
                    'Simulação': sim + 1
                })

                simulacoes_lista.append(df_ativo)

        # Consolidar todas as simulações em um único DataFrame
        self.simulacoes = pd.concat(simulacoes_lista, ignore_index=True)
        
        # Calcular métricas agregadas por simulação
        self.metricas_simulacoes = (self.simulacoes
            .groupby('Simulação')
            .agg({
                'Valor Total': lambda x: x.iloc[-1],
                'Retorno': ['mean', 'std']
            })
            .round(4))
        
        return self.simulacoes

    # --------------------------------------------------------------
    # Métodos auxiliares
    # --------------------------------------------------------------
    def _gerar_pesos(self) -> np.ndarray:
        """Gera pesos aleatórios que somam 1."""
        if self.metodo_pesos == "dirichlet":
            pesos = np.random.dirichlet(np.ones(self.n_ativos))
        else:
            w = np.abs(np.random.randn(self.n_ativos))
            pesos = w / np.sum(w)
        return pesos
