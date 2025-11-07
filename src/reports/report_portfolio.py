"""
Specialized report for portfolio analysis.
Generates complete reports with portfolio visualizations and performance analytics.
"""

from pathlib import Path
from typing import Union
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from src.reports.report_base import BaseReport
from src.plots.plot_portfolio import PortfolioVisualizer
from src.core.entities.portfolio import Portfolio

class PortfolioReport(BaseReport):
    """
    Specialized report for portfolio analysis.
    Generates a complete report with visualizations and metrics for
    investment portfolio analysis.
    """

    def __init__(
        self,
        portfolio: Portfolio,
        title: str = "Portfolio Analysis Report",
        include_plots: bool = True,
        include_tables: bool = True,
    ) -> None:
        """
        Initialize the PortfolioReport instance.

        Args:
            portfolio (Portfolio): Portfolio object containing portfolio data.
            title (str): Report title.
            include_plots (bool): If True, include visualizations.
            include_tables (bool): If True, include metric tables.
        """
        super().__init__(
            title=title,
            include_plots=include_plots,
            include_tables=include_tables,
        )

        self.portfolio = portfolio

        # Initialize visualizer
        returns = self.portfolio.returns()
        weights = self.portfolio.weights()
        self.visualizer = PortfolioVisualizer(returns, weights)

    def generate(self, auto_save: bool = True) -> Union[str, Path]:
        """
        Generate the portfolio report content and optionally save it to a file.

        Args:
            auto_save (bool, optional): If True, automatically saves the report
                after generating (default: True).

        Returns:
            Union[str, Path]: If auto_save=True, returns the saved file path.
                Otherwise, returns the report content as Markdown.
        """
        # Clear previous sections
        self.sections = []

        # Portfolio information
        self._add_portfolio_info()

        # Allocation analysis
        if self.include_plots:
            self._add_allocation_analysis()

        # Performance analysis
        self._add_performance_analysis()

        # Risk analysis
        self._add_risk_analysis()

        # Correlation analysis
        if self.include_plots:
            self._add_correlation_analysis()

        # Dashboard
        if self.include_plots:
            self._add_dashboard()

        if auto_save:
            symbols = list(self.portfolio.holdings)
            return self.save(symbols=symbols)

        # Combine all sections into a markdown string
        full_report = []
        for section in self.sections:
            if section["level"] > 0:
                full_report.append(f"{'#' * section['level']} {section['title']}")
            if section["content"]:
                full_report.append(section["content"])
            full_report.append("")

        return "\n".join(full_report)

    def _add_portfolio_info(self) -> None:
        """Add section with basic portfolio information."""
        self.add_section("Portfolio Information", level=2)

        info = [
            f"- **Name:** {self.portfolio.name}",
            "- **Composition:**",
        ]

        # Add asset weights
        for asset, weight in self.portfolio.weights().items():
            info.append(f"  - {asset}: {weight:.2%}")

        info.extend(
            [
                f"- **Period:** {self.portfolio.start_date} to {self.portfolio.end_date}",
                f"- **Number of Assets:** {len(self.portfolio.holdings)}",
                f"- **Total Value:** {self.portfolio.total_value():,.2f}",
            ]
        )

        self.add_section("", "\n".join(info))

    def _add_allocation_analysis(self) -> None:
        """Add allocation analysis section."""
        self.add_section("Allocation Analysis", level=2)

        # Portfolio allocation pie chart
        fig = self.visualizer.plot_allocation()
        self.add_plot(fig, "Portfolio Allocation", level=3)
        plt.close()

        # Asset risk-return scatter plot
        fig = self.visualizer.plot_return_vs_risk()
        self.add_plot(fig, "Asset Return vs Risk", level=3)
        plt.close()

    def _add_performance_analysis(self) -> None:
        """Add performance analysis section."""
        self.add_section("Performance Analysis", level=2)

        if self.include_plots:
            # Portfolio evolution
            fig = self.visualizer.plot_portfolio_evolution()
            self.add_plot(fig, "Portfolio Evolution", level=3)
            plt.close()

            # Return distribution
            fig = self.visualizer.plot_returns_distribution()
            self.add_plot(fig, "Return Distribution", level=3)
            plt.close()

        if self.include_tables:
            returns = self.portfolio.returns()
            portfolio_returns = returns.mean(axis=1)

            stats = pd.DataFrame(
                {
                    "Metric": [
                        "Average Daily Return",
                        "Annualized Return",
                        "Daily Volatility",
                        "Annualized Volatility",
                        "Sharpe Ratio",
                        "Maximum Drawdown",
                        "Value at Risk (95%)",
                        "Expected Shortfall (95%)",
                    ],
                    "Value": [
                        portfolio_returns.mean(),
                        portfolio_returns.mean() * 252,
                        portfolio_returns.std(),
                        portfolio_returns.std() * np.sqrt(252),
                        (portfolio_returns.mean() * 252)
                        / (portfolio_returns.std() * np.sqrt(252)),
                        self._calculate_max_drawdown(portfolio_returns),
                        portfolio_returns.quantile(0.05),
                        portfolio_returns[
                            portfolio_returns <= portfolio_returns.quantile(0.05)
                        ].mean(),
                    ],
                }
            )

            format_dict = {
                "Value": lambda x: (
                    f"{x:.2%}"
                    if any(
                        m in stats.loc[stats["Value"] == x, "Metric"].iloc[0]
                        for m in [
                            "Return",
                            "Volatility",
                            "Drawdown",
                            "VaR",
                            "Shortfall",
                        ]
                    )
                    else f"{x:.4f}"
                )
            }

            self.add_table(stats, "Performance Statistics", format_dict=format_dict)

    def _add_risk_analysis(self) -> None:
        """Add risk analysis section."""
        self.add_section("Risk Analysis", level=2)

        if self.include_plots:
            # Risk contribution
            fig = self.visualizer.plot_risk_contribution()
            self.add_plot(fig, "Risk Contribution by Asset", level=3)
            plt.close()

            # Drawdown
            fig = self.visualizer.plot_drawdown()
            self.add_plot(fig, "Drawdown Analysis", level=3)
            plt.close()

        if self.include_tables:
            returns = self.portfolio.returns()

            stats = []
            for asset in returns.columns:
                ret = returns[asset]
                stats.append(
                    {
                        "Asset": asset,
                        "Weight": self.portfolio.weights()[asset],
                        "Annual Return": ret.mean() * 252,
                        "Volatility": ret.std() * np.sqrt(252),
                        "Sharpe": (ret.mean() * 252)
                        / (ret.std() * np.sqrt(252)),
                        "VaR 95%": ret.quantile(0.05),
                    }
                )

            stats_df = pd.DataFrame(stats)
            format_dict = {
                "Weight": lambda x: f"{x:.2%}",
                "Annual Return": lambda x: f"{x:.2%}",
                "Volatility": lambda x: f"{x:.2%}",
                "Sharpe": lambda x: f"{x:.2f}",
                "VaR 95%": lambda x: f"{x:.2%}",
            }

            self.add_table(stats_df, "Asset Statistics", format_dict=format_dict)

    def _add_correlation_analysis(self) -> None:
        """Add correlation analysis section."""
        self.add_section("Correlation Analysis", level=2)

        # Correlation matrix
        fig = self.visualizer.plot_correlation()
        self.add_plot(fig, "Correlation Matrix", level=3)
        plt.close()

    def _add_dashboard(self) -> None:
        """Add complete dashboard section."""
        fig = self.visualizer.plot_dashboard()
        self.add_plot(fig, "Complete Dashboard", level=2)
        plt.close()

    @staticmethod
    def _calculate_max_drawdown(returns: pd.Series) -> float:
        """
        Calculate the maximum drawdown of a return series.

        Args:
            returns (pd.Series): Series of portfolio returns.

        Returns:
            float: Maximum drawdown value.
        """
        cum_returns = (1 + returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = (cum_returns - rolling_max) / rolling_max
        return drawdowns.min()
