"""
Monte Carlo simulation: portfolio return scenarios (log-based).
"""
import numpy as np
import pandas as pd
from typing import Dict, Any
from src.analysis.entities.monte_carlo_base import MonteCarloBase


class MonteCarloRetorno(MonteCarloBase):
    """
    Simulação de Monte Carlo com retornos logarítmicos (log-based),
    mantendo os pesos fixos definidos no portfólio.

    Nesta simulação, a incerteza vem da geração de retornos,
    não da variação dos pesos.
    """

    def __init__(
        self,
        portfolio,
        n_simulacoes: int = 10,
        taxa_livre_risco: float = 0.0,
        capital_inicial: float = 10000.0,
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
        self.pesos = np.array(list(self.portfolio.weights().values()))
        self.simulacoes: pd.DataFrame = pd.DataFrame(columns=["Retorno", "Valor", "Simulação"])

    # --------------------------------------------------------------
    # Método principal da simulação
    # --------------------------------------------------------------
    def run(self) -> pd.DataFrame:
        """
        Executa a simulação de Monte Carlo variando os retornos logarítmicos
        dos ativos, mantendo os pesos fixos do portfólio.
        
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
        medias = self.retornos_historicos.mean()
        cov = self.retornos_historicos.cov()
        simulacoes_lista = []

        for sim in range(self.n_simulacoes):
            # Simular retornos logarítmicos
            simulated_log_returns = np.random.multivariate_normal(
                mean=medias, cov=cov, size=len(self.retornos_historicos)
            )
            simulated_returns = np.exp(simulated_log_returns) - 1

            # Criar DataFrame de retornos
            df_retornos = pd.DataFrame(
                simulated_returns, 
                columns=self.ativos,
                index=self.retornos_historicos.index
            )

            # Calcular valores e retornos para cada ativo
            for ativo in self.ativos:
                peso_ativo = self.pesos[list(self.ativos).index(ativo)]
                valores_ativo = self.capital_inicial * peso_ativo * (1 + df_retornos[ativo]).cumprod()
                retornos_ativo = df_retornos[ativo]
                valor_total = self.capital_inicial * (1 + df_retornos).dot(self.pesos).cumprod()

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

