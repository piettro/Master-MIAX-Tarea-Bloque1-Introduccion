"""
Monte Carlo simulation: combined scenario (returns + portfolio weights).
"""
import numpy as np
import pandas as pd
from typing import Dict, Any
from src.analysis.entities.monte_carlo_base import MonteCarloBase


class MonteCarloCombinado(MonteCarloBase):
    """
    Simulação de Monte Carlo combinada:
    - Gera retornos logarítmicos simulados (log-based)
    - Gera pesos estocásticos para os ativos
    """

    def __init__(
        self,
        portfolio,
        n_simulacoes: int = 1000,
        taxa_livre_risco: float = 0.0,
        capital_inicial: float = 10000.0,
        seed: int = None,
        metodo_pesos: str = "dirichlet"
    ):
        """
        Parâmetros
        ----------
        portfolio : Portfolio
            Instância da classe Portfolio, com retornos históricos.
        n_simulacoes : int
            Número de simulações de Monte Carlo.
        taxa_livre_risco : float
            Taxa livre de risco anualizada.
        capital_inicial : float
            Capital inicial investido.
        seed : int
            Semente para reprodutibilidade.
        metodo_pesos : str
            Método para gerar pesos estocásticos ("dirichlet" ou "normalizada").
        """
        super().__init__(
            portfolio=portfolio,
            n_simulacoes=n_simulacoes,
            taxa_livre_risco=taxa_livre_risco,
            seed=seed
        )

        self.capital_inicial = capital_inicial
        self.metodo_pesos = metodo_pesos
        self.retornos_historicos = self.portfolio.series.get_returns()
        self.ativos = self.retornos_historicos.columns
        self.n_ativos = len(self.ativos)
        self.simulacoes: pd.DataFrame = pd.DataFrame(columns=["Retorno", "Valor", "Simulação"])

    # --------------------------------------------------------------
    # Métodos auxiliares
    # --------------------------------------------------------------
    def _gerar_pesos(self) -> np.ndarray:
        """
        Gera um vetor de pesos que somam 1.
        Pode usar distribuição Dirichlet ou normalização de ruído aleatório.
        """
        if self.metodo_pesos == "dirichlet":
            pesos = np.random.dirichlet(np.ones(self.n_ativos))
        else:
            w = np.abs(np.random.randn(self.n_ativos))
            pesos = w / np.sum(w)
        return pesos

    def _gerar_retornos_simulados(self, n_periodos: int) -> np.ndarray:
        """
        Gera retornos logarítmicos multivariados simulados.
        """
        medias = self.retornos_historicos.mean()
        cov = self.retornos_historicos.cov()
        simulated_log_returns = np.random.multivariate_normal(
            mean=medias, cov=cov, size=n_periodos
        )
        return np.exp(simulated_log_returns) - 1

    # --------------------------------------------------------------
    # Execução principal
    # --------------------------------------------------------------
    def run(self) -> pd.DataFrame:
        """
        Executa simulações combinadas variando pesos e retornos.

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
            # 1. Gerar pesos estocásticos
            pesos = self._gerar_pesos()

            # 2. Gerar retornos logarítmicos simulados
            simulated_returns = self._gerar_retornos_simulados(len(self.retornos_historicos))

            # 3. Criar DataFrame de retornos simulados
            df_retornos = pd.DataFrame(
                simulated_returns,
                columns=self.ativos,
                index=self.retornos_historicos.index
            )

            # 4. Calcular valores e retornos para cada ativo
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
