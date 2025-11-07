"""
Monte Carlo Simulation: Portfolio weight allocation using historical returns.
"""

import numpy as np
import pandas as pd
from typing import Optional
from src.analysis.entities.monte_carlo_base import MonteCarloBase

class MonteCarloPortfolio(MonteCarloBase):
    """
    Monte Carlo simulation varying portfolio allocation weights,
    using real historical returns of assets.

    This simulation preserves the temporal structure and actual
    market correlations, varying only the weight combinations to
    explore possible distributions of return and risk.
    """

    def __init__(
        self,
        portfolio,
        n_simulations: int = 1000,
        risk_free_rate: float = 0.0,
        seed: Optional[int] = None,
    ):
        """
        Initializes the Monte Carlo Portfolio simulation.

        Args:
            portfolio: Portfolio
                Instance of the Portfolio class containing historical asset returns.
            n_simulations: int, optional
                Number of Monte Carlo simulations to be executed. Default is 1000.
            risk_free_rate: float, optional
                Annualized risk-free rate. Default is 0.0.
            initial_capital: float, optional
                Initial amount of invested capital. Default is 10,000.
            weight_method: str, optional
                Method for generating random weights ("dirichlet" or "normalized").
                Default is "dirichlet".
            seed: int, optional
                Random seed for reproducibility. Default is None.
        """
        super().__init__(
            portfolio=portfolio,
            n_simulations=n_simulations,
            risk_free_rate=risk_free_rate,
            seed=seed,
        )

    def run(self) -> pd.DataFrame:
        """
        Runs the Monte Carlo simulation by varying only portfolio weights,
        using real historical asset returns.

        Returns:
            pd.DataFrame: Expanded simulation results containing:
                - Asset: asset name
                - Date: timestamp of the simulated period
                - Weight: asset weight in the portfolio
                - Value: asset value evolution
                - Total Value: total portfolio value
                - Return: asset return
                - Simulation: simulation number
        """
        simulation_results = []

        for sim in range(self.n_simulations):
            # 1. Generate random weights
            weights = self.generate_weights()

            # 2. Copy historical returns
            returns_df = self.historical_returns.copy()

            # 3. Compute values and returns per asset
            for asset in self.assets:
                asset_weight = weights[list(self.assets).index(asset)]
                asset_returns = returns_df[asset]

                asset_values = self.initial_capital * asset_weight * (1 + asset_returns).cumprod()
                total_value = self.initial_capital * (1 + returns_df).dot(weights).cumprod()

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

        # Consolidate all simulations into one DataFrame
        self.simulations = pd.concat(simulation_results, ignore_index=True)

        # Compute aggregate metrics by simulation
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
