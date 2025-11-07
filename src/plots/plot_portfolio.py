"""
Class for portfolio analysis visualization.
Implements various charts for investment portfolio analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict
from pathlib import Path


class PortfolioVisualizer:
    """Class responsible for generating charts for portfolio and investment analysis."""

    def __init__(self, returns: pd.DataFrame, weights: Dict[str, float]):
        """Initialize the visualizer with portfolio data.

        Args:
            returns (pd.DataFrame): DataFrame containing asset returns.
                The index must represent dates, and the columns the assets.
            weights (Dict[str, float]): Dictionary containing asset weights in the portfolio.

        Raises:
            ValueError: If returns DataFrame is empty or None.
            ValueError: If weights are missing or do not sum to 1.
        """
        if returns is None or returns.empty:
            raise ValueError("Returns DataFrame cannot be empty.")

        if not weights or not np.isclose(sum(weights.values()), 1.0):
            raise ValueError("Weights must sum to 1.")

        print("Initializing Portfolio Visualizer...")
        self.returns = returns.copy()
        print("Calculating portfolio returns...")
        self.weights = weights

        # Compute portfolio returns
        self.portfolio_returns = pd.DataFrame({
            'Portfolio': np.sum([
                returns[asset] * weight
                for asset, weight in weights.items()
            ], axis=0)
        })

    def plot_allocation(self) -> plt.Figure:
        """Generate a pie chart for portfolio allocation.

        Returns:
            plt.Figure: Figure object with the generated chart.
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Sort weights for better visualization
        sorted_weights = dict(
            sorted(self.weights.items(), key=lambda x: x[1], reverse=True)
        )

        # Generate pie chart
        wedges, texts, autotexts = ax.pie(
            sorted_weights.values(),
            labels=sorted_weights.keys(),
            autopct='%1.1f%%',
            textprops={'fontsize': 10}
        )

        ax.set_title('Portfolio Allocation')
        plt.setp(autotexts, size=8, weight="bold")
        plt.setp(texts, size=10)

        return fig

    def plot_portfolio_evolution(self) -> plt.Figure:
        """Generate a line chart showing portfolio value evolution.

        Returns:
            plt.Figure: Figure object with the generated chart.
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        portfolio_value = (1 + self.portfolio_returns).cumprod()
        ax.plot(portfolio_value.index, portfolio_value['Portfolio'],
                label='Portfolio', linewidth=2)

        ax.set_title('Portfolio Evolution')
        ax.set_xlabel('Date')
        ax.set_ylabel('Value (Base 1.0)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig

    def plot_correlation(self) -> plt.Figure:
        """Generate a heatmap showing correlations between assets.

        Returns:
            plt.Figure: Figure object with the generated heatmap.
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        corr = self.returns.corr()
        sns.heatmap(
            corr,
            annot=True,
            cmap='coolwarm',
            center=0,
            square=True,
            fmt='.2f',
            ax=ax
        )

        ax.set_title('Asset Correlation')

        return fig

    def plot_returns_distribution(self) -> plt.Figure:
        """Generate time series and histogram charts of portfolio returns.

        Returns:
            plt.Figure: Figure object with the generated charts.
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[2, 1])

        # Time series of returns
        ax1.plot(self.portfolio_returns.index,
                 self.portfolio_returns['Portfolio'],
                 linewidth=1, alpha=0.7)
        ax1.set_title('Portfolio Returns')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Return')
        ax1.grid(True, alpha=0.3)

        # Histogram of returns
        sns.histplot(
            data=self.portfolio_returns['Portfolio'],
            ax=ax2,
            bins=50,
            stat='density',
            alpha=0.6
        )
        sns.kdeplot(
            data=self.portfolio_returns['Portfolio'],
            ax=ax2,
            color='red',
            linewidth=2
        )

        ax2.set_title('Return Distribution')
        ax2.set_xlabel('Return')
        ax2.set_ylabel('Density')

        plt.tight_layout()
        return fig

    def plot_drawdown(self) -> plt.Figure:
        """Generate a drawdown chart for the portfolio.

        Returns:
            plt.Figure: Figure object with the generated chart.
        """
        portfolio_value = (1 + self.portfolio_returns).cumprod()
        roll_max = portfolio_value.expanding().max()
        drawdown = (portfolio_value - roll_max) / roll_max

        fig, ax = plt.subplots(figsize=(12, 4))

        ax.fill_between(drawdown.index, drawdown['Portfolio'], 0, color='r', alpha=0.3)
        ax.plot(drawdown.index, drawdown['Portfolio'], color='r', linewidth=1)

        ax.set_title('Portfolio Drawdown')
        ax.set_xlabel('Date')
        ax.set_ylabel('Drawdown (%)')
        ax.grid(True, alpha=0.3)

        return fig

    def plot_risk_contribution(self) -> plt.Figure:
        """Generate a horizontal bar chart showing risk contribution per asset.

        Returns:
            plt.Figure: Figure object with the generated chart.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        vol = self.returns.std() * np.sqrt(252)

        risk_contrib = pd.Series({
            asset: weight * vol[asset]
            for asset, weight in self.weights.items()
        })

        risk_contrib = risk_contrib / risk_contrib.sum() * 100
        risk_contrib = risk_contrib.sort_values(ascending=True)

        ax.barh(range(len(risk_contrib)), risk_contrib.values, alpha=0.6)
        ax.set_yticks(range(len(risk_contrib)))
        ax.set_yticklabels(risk_contrib.index)
        ax.set_title('Risk Contribution by Asset')
        ax.set_xlabel('Contribution (%)')

        for i, v in enumerate(risk_contrib.values):
            ax.text(v, i, f'{v:.1f}%', va='center')

        return fig

    def plot_return_vs_risk(self) -> plt.Figure:
        """Generate a scatter plot of return vs risk for each asset and the portfolio.

        Returns:
            plt.Figure: Figure object with the generated chart.
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        returns_annual = self.returns.mean() * 252
        vol_annual = self.returns.std() * np.sqrt(252)

        ax.scatter(vol_annual, returns_annual, s=100)

        for i, asset in enumerate(self.returns.columns):
            ax.annotate(asset, (vol_annual[i], returns_annual[i]),
                        xytext=(5, 5), textcoords='offset points')

        portfolio_return = self.portfolio_returns.mean() * 252
        portfolio_vol = self.portfolio_returns.std() * np.sqrt(252)

        ax.scatter(portfolio_vol, portfolio_return,
                   s=200, c='red', marker='*', label='Portfolio')

        ax.set_title('Return vs Risk')
        ax.set_xlabel('Risk (Annualized Volatility)')
        ax.set_ylabel('Annualized Return')
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig

    def plot_dashboard(self) -> plt.Figure:
        """Generate a complete dashboard with main portfolio charts.

        Returns:
            plt.Figure: Figure object with the generated dashboard.
        """
        fig = plt.figure(figsize=(15, 12))
        gs = fig.add_gridspec(3, 2)

        # Portfolio Evolution
        ax1 = fig.add_subplot(gs[0, :])
        portfolio_value = (1 + self.portfolio_returns).cumprod()
        ax1.plot(portfolio_value.index, portfolio_value['Portfolio'],
                 label='Portfolio', linewidth=2)
        ax1.set_title('Portfolio Evolution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Allocation
        ax2 = fig.add_subplot(gs[1, 0])
        sorted_weights = dict(sorted(
            self.weights.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        ax2.pie(sorted_weights.values(),
                labels=sorted_weights.keys(),
                autopct='%1.1f%%',
                textprops={'fontsize': 8})
        ax2.set_title('Allocation')

        # Returns Distribution
        ax3 = fig.add_subplot(gs[1, 1])
        sns.histplot(data=self.portfolio_returns['Portfolio'],
                     ax=ax3, bins=50, stat='density', alpha=0.6)
        sns.kdeplot(data=self.portfolio_returns['Portfolio'],
                    ax=ax3, color='red', linewidth=2)
        ax3.set_title('Return Distribution')

        # Correlation Heatmap
        ax4 = fig.add_subplot(gs[2, 0])
        sns.heatmap(self.returns.corr(), ax=ax4,
                    annot=True, cmap='coolwarm', center=0,
                    fmt='.2f', square=True, cbar=False)
        ax4.set_title('Correlations')

        # Drawdown
        ax5 = fig.add_subplot(gs[2, 1])
        roll_max = portfolio_value.expanding().max()
        drawdown = (portfolio_value - roll_max) / roll_max
        ax5.fill_between(drawdown.index, drawdown['Portfolio'], 0, color='r', alpha=0.3)
        ax5.plot(drawdown.index, drawdown['Portfolio'], color='r', linewidth=1)
        ax5.set_title('Drawdown')
        ax5.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig
