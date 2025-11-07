"""
Monte Carlo simulation: combined scenario (asset returns + portfolio weights).
"""

import numpy as np
import pandas as pd
from src.analysis.entities.monte_carlo_base import MonteCarloBase

class MonteCarloCombined(MonteCarloBase):
    """Monte Carlo Combined Simulation.

    Simulates both asset returns and stochastic portfolio weights:
    - Generates log-based simulated returns.
    - Generates stochastic weights for each asset using Dirichlet or normalized random noise.
    """

    def __init__(
        self,
        portfolio,
        n_simulations: int = 1000,
        risk_free_rate: float = 0.0,
        initial_capital: float = 10000.0,
        seed: int = None,
        weight_method: str = "dirichlet",
    ) -> None:
        """Initialize MonteCarloCombined.

        Args:
            portfolio: Portfolio instance with historical returns.
            n_simulations (int): Number of Monte Carlo simulations. Defaults to 1000.
            risk_free_rate (float): Annualized risk-free rate. Defaults to 0.0.
            initial_capital (float): Initial invested capital. Defaults to 10000.0.
            seed (int): Random seed for reproducibility. Defaults to None.
            weight_method (str): Method to generate stochastic weights.
                Options: `"dirichlet"` or `"normalized"`. Defaults to `"dirichlet"`.
        """
        super().__init__(
            portfolio=portfolio,
            n_simulations=n_simulations,
            risk_free_rate=risk_free_rate,
            seed=seed,
        )

        self.initial_capital = initial_capital
        self.weight_method = weight_method
        self.historical_returns = self.portfolio.series.get_returns()
        self.assets = self.historical_returns.columns
        self.n_assets = len(self.assets)
        self.simulations: pd.DataFrame = pd.DataFrame(columns=["Return", "Value", "Simulation"])

    def _generate_weights(self) -> np.ndarray:
        """Generate a vector of portfolio weights that sum to 1.

        Returns:
            np.ndarray: Array of weights (length = number of assets).
        """
        if self.weight_method == "dirichlet":
            weights = np.random.dirichlet(np.ones(self.n_assets))
        else:
            w = np.abs(np.random.randn(self.n_assets))
            weights = w / np.sum(w)
        return weights

    def _generate_simulated_returns(self, n_periods: int) -> np.ndarray:
        """Generate multivariate simulated log returns.

        Args:
            n_periods (int): Number of periods to simulate.

        Returns:
            np.ndarray: Matrix of simulated returns.
        """
        means = self.historical_returns.mean()
        cov = self.historical_returns.cov()

        simulated_log_returns = np.random.multivariate_normal(mean=means, cov=cov, size=n_periods)
        return np.exp(simulated_log_returns) - 1

    def run(self) -> pd.DataFrame:
        """Run combined Monte Carlo simulations varying both weights and returns.

        Returns:
            pd.DataFrame: Expanded simulation DataFrame containing:
                - Asset: Asset name
                - Date: Simulation date
                - Weight: Asset weight in the portfolio
                - Value: Asset value
                - Total Value: Total portfolio value
                - Return: Asset return
                - Simulation: Simulation number
        """
        simulations_list = []

        for sim in range(self.n_simulations):
            # 1. Generate stochastic weights
            weights = self._generate_weights()

            # 2. Generate simulated log returns
            simulated_returns = self._generate_simulated_returns(len(self.historical_returns))

            # 3. Build DataFrame of simulated returns
            df_returns = pd.DataFrame(
                simulated_returns,
                columns=self.assets,
                index=self.historical_returns.index,
            )

            # 4. Compute individual and total portfolio values
            for asset in self.assets:
                asset_weight = weights[list(self.assets).index(asset)]
                asset_returns = df_returns[asset]
                asset_values = self.initial_capital * asset_weight * (1 + asset_returns).cumprod()
                total_value = self.initial_capital * (1 + df_returns).dot(weights).cumprod()

                # DataFrame for the current asset
                df_asset = pd.DataFrame(
                    {
                        "Asset": asset,
                        "Date": df_returns.index,
                        "Weight": asset_weight,
                        "Value": asset_values,
                        "Total Value": total_value,
                        "Return": asset_returns,
                        "Simulation": sim + 1,
                    }
                )

                simulations_list.append(df_asset)

        # Combine all simulations
        self.simulations = pd.concat(simulations_list, ignore_index=True)

        # Aggregate metrics per simulation
        self.simulation_metrics = (
            self.simulations.groupby("Simulation")
            .agg(
                {
                    "Total Value": lambda x: x.iloc[-1],
                    "Return": ["mean", "std"],
                }
            )
            .round(4)
        )

        return self.simulations
