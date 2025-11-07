import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from src.analysis.entities.monte_carlo_metrics import MonteCarloCalculator

class MonteCarloVisualizer:
    """Class responsible for visualizing Monte Carlo simulation results.

    Compatible with MonteCarloPortfolio, MonteCarloReturn, and MonteCarloCombined.
    Works with the expanded DataFrame format containing:
        - Asset: asset name
        - Date: simulation date
        - Weight: asset weight in the portfolio
        - Value: asset value
        - Total Value: total portfolio value
        - Return: asset return
        - Simulation: simulation number
    """

    def __init__(self, simulations: pd.DataFrame):
        """Initialize MonteCarloVisualizer.

        Args:
            simulations (pd.DataFrame): Expanded DataFrame with Monte Carlo
                simulation results. The DataFrame must contain the columns:
                ['Date', 'Simulation', 'Asset', 'Weight', 'Value',
                'Total Value', 'Return'].

        Raises:
            ValueError: If the DataFrame is empty or missing required columns.
        """
        if simulations is None or simulations.empty:
            raise ValueError("Simulation DataFrame cannot be empty.")

        required_columns = [
            "Date", "Simulation", "Asset", "Weight",
            "Value", "Total Value", "Return"
        ]
        missing_columns = [col for col in required_columns if col not in simulations.columns]

        if missing_columns:
            raise ValueError(
                f"Missing required columns in simulation DataFrame: {missing_columns}"
            )

        self.simulations = simulations.copy()
        self.calculator = MonteCarloCalculator(simulations)

    def plot_portfolio_value_evolution(self, title: str = "Portfolio Value Evolution") -> plt.Figure:
        """Plot the total portfolio value evolution for all simulations.

        Args:
            title (str, optional): Plot title. Defaults to "Portfolio Value Evolution".

        Returns:
            plt.Figure: Matplotlib figure object.
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.set_style("whitegrid")

        # Group by Date and Simulation to get total portfolio values
        values_by_sim = (
            self.simulations.groupby(["Date", "Simulation"])["Total Value"]
            .first()
            .unstack()
        )

        # Plot all simulations
        for sim in values_by_sim.columns:
            ax.plot(values_by_sim.index, values_by_sim[sim], alpha=0.08, color="blue")

        # Plot mean portfolio value
        mean_values = values_by_sim.mean(axis=1)
        ax.plot(mean_values.index, mean_values, color="red", linewidth=2, label="Mean")

        ax.set_title(title)
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Portfolio Value")
        ax.legend()
        fig.tight_layout()
        return fig

    def plot_return_distribution(self, title: str = "Portfolio Return Distribution") -> plt.Figure:
        """Plot the distribution of portfolio returns across all simulations.

        Args:
            title (str, optional): Plot title. Defaults to "Portfolio Return Distribution".

        Returns:
            plt.Figure: Matplotlib figure object.
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.set_style("whitegrid")

        # Compute mean return per simulation
        returns = self.simulations.groupby("Simulation")["Return"].mean()

        # Plot histogram
        sns.histplot(data=returns, bins=30, kde=True, ax=ax)
        ax.axvline(returns.mean(), color="red", linestyle="--", label=f"Mean: {returns.mean():.2%}")

        ax.set_title(title)
        ax.set_xlabel("Return")
        ax.set_ylabel("Frequency")
        ax.legend()
        fig.tight_layout()
        return fig

    def plot_asset_weight_evolution(self, title: str = "Portfolio Weights by Simulation") -> plt.Figure:
        """Plot asset weights for each simulation as a stacked column chart.

        Args:
            title (str, optional): Plot title. Defaults to "Portfolio Weights by Simulation".

        Returns:
            plt.Figure: Matplotlib figure object showing stacked column chart of
                       asset weights for each simulation.
        """
        fig, ax = plt.subplots(figsize=(15, 7))
        sns.set_style("whitegrid")

        pivot_df = self.simulations.pivot_table(index="Simulation", columns="Asset", values="Weight", aggfunc="sum")
        pivot_df.plot.area(alpha=0.8)

        # Customize plot
        ax.set_title(title, pad=20)
        ax.set_xlabel("Simulation Number")
        ax.set_ylabel("Portfolio Weight")
        ax.legend(
            title="Assets",
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
            borderaxespad=0
        )
        
        # Reduce number of x-axis labels
        total_sims = pivot_df.shape[0]
        step = max(1, total_sims // 10)  # Show about 10 labels
        ax.set_xticks(range(0, total_sims, step))
        ax.set_xticklabels(range(0, total_sims, step))
        plt.xticks(rotation=0)  # Horizontal labels
        
        ax.margins(x=0)
        fig.tight_layout()
        return fig

    def plot_metrics_dashboard(self) -> plt.Figure:
        """Plot a dashboard summarizing key Monte Carlo metrics.

        Returns:
            plt.Figure: Matplotlib figure object.
        """
        basic_stats = self.calculator.calculate_basic_statistics()
        var_cvar = self.calculator.calculate_var_cvar()
        drawdowns = self.calculator.calculate_drawdowns()

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Monte Carlo Metrics Dashboard", fontsize=16)

        # Risk-return metrics
        stats_df = pd.DataFrame(
            {
                "Value": [
                    basic_stats["mean_return"],
                    basic_stats["std_deviation"],
                    var_cvar["var"],
                    var_cvar["cvar"],
                ]
            },
            index=["Mean Return", "Volatility", "VaR 95%", "CVaR 95%"],
        )
        sns.barplot(data=stats_df, y=stats_df.index, x="Value", ax=axes[0, 0])
        axes[0, 0].set_title("Risk-Return Metrics")

        # Asset-level statistics
        asset_stats = self.calculator.calculate_portfolio_statistics()
        sns.scatterplot(
            data=asset_stats,
            x="Volatility",
            y="Average Return",
            size="Average Weight",
            ax=axes[0, 1],
        )
        axes[0, 1].set_title("Risk-Return by Asset")

        # Correlation matrix
        corr = self.calculator.calculate_correlations()
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=axes[1, 0])
        axes[1, 0].set_title("Asset Correlation Matrix")

        # Drawdowns
        dd_series = pd.Series(drawdowns)
        sns.barplot(x=dd_series.index, y=dd_series.values, ax=axes[1, 1])
        axes[1, 1].set_title("Drawdown Metrics")
        axes[1, 1].tick_params(axis="x", rotation=45)

        fig.tight_layout()
        return fig

    def plot_efficient_frontier(self) -> plt.Figure:
        """Plot simulated efficient frontier: risk vs return, colored by Sharpe ratio.

        Returns:
            plt.Figure: Matplotlib figure object.

        Raises:
            ValueError: If the DataFrame or required columns are missing.
        """
        df = getattr(self, "results", None)
        if df is None:
            raise ValueError("No results DataFrame available for efficient frontier plot.")
        if "Sharpe" not in df.columns:
            raise ValueError("Results DataFrame must contain the 'Sharpe' column.")

        fig, ax = plt.subplots(figsize=(10, 6))
        scatter = ax.scatter(
            df.get("Mean Risk", df.get("Risk")),
            df.get("Mean Return", df.get("Return")),
            c=df["Sharpe"],
            cmap="viridis",
            alpha=0.7,
            s=50,
        )
        fig.colorbar(scatter, ax=ax, label="Sharpe Ratio")

        ax.set_title("Simulated Efficient Frontier (Monte Carlo)")
        ax.set_xlabel("Risk (Standard Deviation)")
        ax.set_ylabel("Expected Return")
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    def plot_return_histogram(self) -> plt.Figure:
        """Plot histogram of simulated returns (MonteCarloReturn)."""
        results = getattr(self, "results", None)

        if isinstance(results, dict):
            returns = results.get("returns", None)
        elif isinstance(results, pd.Series):
            returns = results
        else:
            raise ValueError("Invalid results format for return distribution plot.")

        if returns is None:
            raise ValueError("No return series found for plotting.")

        fig, ax = plt.subplots(figsize=(9, 5))
        sns.histplot(returns, bins=50, kde=True, color="steelblue", ax=ax)
        ax.set_title("Simulated Return Distribution")
        ax.set_xlabel("Simulated Return")
        ax.set_ylabel("Frequency")
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    def plot_sharpe_map(self) -> plt.Figure:
        """Plot Sharpe ratio heatmap (risk vs return) for MonteCarloCombined."""
        df = getattr(self, "results", None)

        required = ["Mean Risk", "Mean Return", "Sharpe"]
        if df is None or not all(col in df.columns for col in required):
            raise ValueError("Results DataFrame must contain 'Mean Risk', 'Mean Return', and 'Sharpe'.")

        fig, ax = plt.subplots(figsize=(8, 6))
        scatter = ax.scatter(
            df["Mean Risk"], df["Mean Return"], c=df["Sharpe"], cmap="plasma", s=40, alpha=0.8
        )
        fig.colorbar(scatter, ax=ax, label="Sharpe Ratio")

        ax.set_title("Sharpe Ratio Map — Monte Carlo Combined")
        ax.set_xlabel("Risk (Standard Deviation)")
        ax.set_ylabel("Expected Return")
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    def plot_risk_adjusted_boxplots(self) -> plt.Figure:
        """Plot boxplots for Sharpe, Sortino, VaR, and CVaR metrics."""
        df = getattr(self, "results", None)
        if df is None:
            raise ValueError("No results DataFrame available for risk-adjusted boxplots.")

        metrics = ["Sharpe", "Sortino", "VaR", "CVaR"]
        available_metrics = [m for m in metrics if m in df.columns]

        if not available_metrics:
            raise ValueError("No risk-adjusted metrics available for boxplot.")

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=df[available_metrics], palette="Set2", ax=ax)
        ax.set_title("Risk-Adjusted Metrics Distribution")
        ax.set_ylabel("Value")
        ax.grid(True, linestyle="--", alpha=0.3)
        return fig

    def plot_correlation_matrix(self, asset_returns: pd.DataFrame) -> plt.Figure:
        """Plot the correlation matrix of asset returns.

        Args:
            asset_returns (pd.DataFrame): DataFrame containing daily asset returns.

        Returns:
            plt.Figure: Matplotlib figure object.
        """
        corr = asset_returns.corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            corr, annot=True, fmt=".2f", cmap="coolwarm", square=True,
            cbar_kws={"shrink": 0.8}, ax=ax
        )
        ax.set_title("Asset Return Correlation Matrix")
        return fig

    def plot_simulations(self, sims: np.ndarray) -> plt.Figure:
        """Plot Monte Carlo simulation paths over time.

        Args:
            sims (np.ndarray): Simulation matrix (rows = days, columns = simulations).

        Returns:
            plt.Figure: Matplotlib figure object.
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot all simulation paths
        if sims.ndim == 2:
            ax.plot(sims, color="lightgray", alpha=0.3)
        else:
            ax.plot(sims, color="lightgray", alpha=0.7)

        ax.set_title("Monte Carlo Simulations Over Time")
        ax.set_xlabel("Days")
        ax.set_ylabel("Portfolio Value")
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    def plot_final_value_distribution(self, sims: np.ndarray) -> plt.Figure:
        """Plot the distribution of final portfolio values.

        Args:
            sims (np.ndarray): Simulation matrix (rows = days, columns = simulations).

        Returns:
            plt.Figure: Matplotlib figure object.
        """
        final_values = sims[-1, :]
        fig, ax = plt.subplots(figsize=(9, 5))
        sns.histplot(final_values, bins=50, kde=True, color="coral", ax=ax)
        ax.set_title("Distribution of Final Simulation Values")
        ax.set_xlabel("Final Portfolio Value")
        ax.set_ylabel("Frequency")
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    def plot_var_cvar(self, sims: np.ndarray, alpha: float = 0.05) -> plt.Figure:
        """Plot Value at Risk (VaR) and Conditional VaR (CVaR).

        Args:
            sims (np.ndarray): Simulation matrix (rows = days, columns = simulations).
            alpha (float, optional): Confidence level. Defaults to 0.05.

        Returns:
            plt.Figure: Matplotlib figure object.
        """
        final_values = sims[-1, :]
        start_values = sims[0, :].copy()
        start_values[start_values == 0] = np.nan

        returns = final_values / start_values - 1
        returns = returns[~np.isnan(returns)]

        var = np.percentile(returns, 100 * alpha)
        cvar = returns[returns <= var].mean()

        fig, ax = plt.subplots(figsize=(9, 5))
        sns.histplot(returns, bins=50, kde=True, color="seagreen", ax=ax)
        ax.axvline(var, color="red", linestyle="--", label=f"VaR ({alpha*100:.1f}%) = {var:.2%}")
        ax.axvline(cvar, color="blue", linestyle="--", label=f"CVaR ({alpha*100:.1f}%) = {cvar:.2%}")

        ax.set_title("Final Return Distribution with VaR and CVaR")
        ax.set_xlabel("Final Portfolio Return")
        ax.set_ylabel("Frequency")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    def plot_asset_correlation(self, asset_returns: pd.DataFrame) -> plt.Figure:
        """Plot the correlation matrix of assets.

        Args:
            asset_returns (pd.DataFrame): DataFrame containing daily asset returns.

        Returns:
            plt.Figure: Matplotlib figure object.
        """
        corr = asset_returns.corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            corr, annot=True, fmt=".2f", cmap="coolwarm", square=True,
            cbar_kws={"shrink": 0.8}, ax=ax
        )
        ax.set_title("Asset Correlation Matrix")
        return fig
