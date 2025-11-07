"""
Monte Carlo Simulation: portfolio return scenarios (log-based).
"""

import numpy as np
import pandas as pd
from typing import Optional
from src.analysis.entities.monte_carlo_base import MonteCarloBase

class MonteCarloReturn(MonteCarloBase):
    """
    Monte Carlo simulation using log-based returns while keeping
    portfolio weights fixed.

    In this simulation, uncertainty comes from the generation of
    simulated returns rather than weight variation.
    """

    def __init__(
        self,
        portfolio,
        n_simulations: int = 10,
        risk_free_rate: float = 0.0,
        initial_capital: float = 10000.0,
        seed: Optional[int] = None,
    ):
        """
        Initializes the Monte Carlo Return simulation.

        Args:
            portfolio: Portfolio
                Instance of the Portfolio class containing historical asset returns.
            n_simulations: int, optional
                Number of simulations to execute. Default is 10.
            risk_free_rate: float, optional
                Annualized risk-free rate. Default is 0.0.
            initial_capital: float, optional
                Initial invested capital. Default is 10,000.
            seed: int, optional
                Random seed for reproducibility. Default is None.
        """
        super().__init__(
            portfolio=portfolio,
            n_simulations=n_simulations,
            risk_free_rate=risk_free_rate,
            seed=seed,
        )

        self.initial_capital = initial_capital
        self.historical_returns = self.portfolio.series.get_returns()
        self.assets = self.historical_returns.columns
        self.n_assets = len(self.assets)
        self.weights = np.array(list(self.portfolio.weights().values()))
        self.simulations: pd.DataFrame = pd.DataFrame(columns=["Return", "Value", "Simulation"])

    def run(self) -> pd.DataFrame:
        """
        Runs the Monte Carlo simulation by varying log-based asset returns,
        keeping portfolio weights fixed.

        Returns:
            pd.DataFrame: Expanded simulation results containing:
                - Asset: asset name
                - Date: simulation timestamp
                - Weight: asset weight in the portfolio
                - Value: asset value evolution
                - Total Value: total portfolio value
                - Return: asset return
                - Simulation: simulation number
        """
        means = self.historical_returns.mean()
        cov = self.historical_returns.cov()
        simulation_results = []

        for sim in range(self.n_simulations):
            # Generate simulated log returns
            simulated_log_returns = np.random.multivariate_normal(
                mean=means, cov=cov, size=len(self.historical_returns)
            )
            simulated_returns = np.exp(simulated_log_returns) - 1

            # Create DataFrame of simulated returns
            returns_df = pd.DataFrame(
                simulated_returns,
                columns=self.assets,
                index=self.historical_returns.index,
            )

            # Compute asset and portfolio value evolution
            for asset in self.assets:
                asset_weight = self.weights[list(self.assets).index(asset)]
                asset_returns = returns_df[asset]

                asset_values = self.initial_capital * asset_weight * (1 + asset_returns).cumprod()
                total_value = self.initial_capital * (1 + returns_df).dot(self.weights).cumprod()

                asset_df = pd.DataFrame({
                    "Asset": asset,
                    "Date": returns_df.index,
                    "Weight": asset_weight,
                    "Value": asset_values,
                    "Total Value": total_value,
                    "Return": asset_returns,
                    "Simulation": sim + 1,
                })

                simulation_results.append(asset_df)

        # Combine all simulations into one DataFrame
        self.simulations = pd.concat(simulation_results, ignore_index=True)

        # Compute aggregated metrics per simulation
        self.simulation_metrics = (
            self.simulations
            .groupby("Simulation")
            .agg({
                "Total Value": lambda x: x.iloc[-1],
                "Return": ["mean", "std"],
            })
            .round(4)
        )

        return self.simulations
