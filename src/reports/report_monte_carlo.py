"""
Markdown report generator for Monte Carlo simulations.
"""

from pathlib import Path
from typing import Union, List
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from src.analysis.entities.monte_carlo_returns import MonteCarloReturn
from src.analysis.entities.monte_carlo_portfolios import MonteCarloPortfolio
from src.analysis.entities.monte_carlo_combined import MonteCarloCombined
from src.analysis.entities.monte_carlo_metrics import MonteCarloCalculator
from src.plots.plot_monte_carlo import MonteCarloVisualizer
from src.reports.report_base import BaseReport

class MonteCarloReport(BaseReport):
    """Specialized report for Monte Carlo simulations.
    Generates a complete report with visualizations and performance metrics.
    """

    def __init__(
        self,
        simulation: Union[MonteCarloReturn, MonteCarloPortfolio, MonteCarloCombined],
        title: str = "Monte Carlo Simulation Report",
        include_plots: bool = True,
        include_tables: bool = True,
    ) -> None:
        """Initialize MonteCarloReport.

        Args:
            simulation (Union[MonteCarloRetorno, MonteCarloPortfolio, MonteCarloCombinado]):
                Monte Carlo simulation object already executed.
            title (str, optional): Report title. Defaults to "Monte Carlo Simulation Report".
            include_plots (bool, optional): Whether to include visualizations. Defaults to True.
            include_tables (bool, optional): Whether to include metrics tables. Defaults to True.

        Raises:
            ValueError: If the simulation has not been executed yet.
        """
        super().__init__(title=title, include_plots=include_plots, include_tables=include_tables)

        if simulation.simulations is None:
            raise ValueError("Simulation must be executed before generating the report.")

        self.simulation = simulation
        self.calculator = MonteCarloCalculator(simulation.simulations)
        self.visualizer = MonteCarloVisualizer(simulation.simulations)

    def generate(self, auto_save: bool = True) -> Union[str, Path]:
        """Generate Monte Carlo simulation report and optionally save it.

        Args:
            auto_save (bool, optional): If True, automatically saves the report after generating.
                Defaults to True.

        Returns:
            Union[str, Path]: Path of the saved file if auto_save=True, otherwise Markdown string content.
        """
        # Clear previous sections
        self.sections = []

        # General info about the simulation and portfoli
        self._add_simulation_info()

        # Performance and risk tables
        if self.include_tables:
            self._add_performance_metrics()
            self._add_risk_metrics()

        # Visualizations
        if self.include_plots:
            self._add_visualizations()

        # Conclusions
        self._add_conclusions()

        if auto_save:
            # Use portfolio symbols for file naming
            portfolio = self.simulation.portfolio
            symbols = list(portfolio.holdings)

            sim_type = self.simulation.__class__.__name__.replace("MonteCarlo", "").lower()
            filename = f"montecarlo_{sim_type}_{datetime.now().strftime('%H%M%S')}"

            return self.save(symbols=symbols, custom_name=filename)

        # If not saving, return Markdown string
        full_report: List[str] = []
        for section in self.sections:
            if section["level"] > 0:
                full_report.append(f"{'#' * section['level']} {section['title']}")
            if section["content"]:
                full_report.append(section["content"])
            full_report.append("")

        return "\n".join(full_report)

    def _add_simulation_info(self) -> None:
        """Add basic information about the simulation and portfolio."""
        self.add_section("Portfolio Information", level=2)

        portfolio = self.simulation.portfolio
        portfolio_info = [
            f"- **Name:** {portfolio.name}",
            "- **Assets:**",
        ]

        for asset in self.simulation.assets:
            portfolio_info.append(f"  - {asset}")
        
        portfolio_info.extend(
            [
                f"- **Period:** {portfolio.start_date} to {portfolio.end_date}",
                f"- **Number of Simulations:** {self.simulation.n_simulations}",
            ]
        )
        self.add_section("", "\n".join(portfolio_info))

    def _add_performance_metrics(self) -> None:
        """Create performance statistics tables for the simulation."""
        self.add_section("Performance Metrics", level=2)

        stats = self.calculator.calculate_basic_statistics()
        stats_df = pd.DataFrame(
            {
                "Metric": [
                    "Mean Return",
                    "Median Return",
                    "Standard Deviation",
                    "Minimum Return",
                    "Maximum Return",
                ],
                "Value": [
                    stats["mean_return"],
                    stats["median_return"],
                    stats["std_deviation"],
                    stats["min_return"],
                    stats["max_return"],
                ],
            }
        )
        self.add_table(stats_df, "Basic Statistics", format_dict={"Value": lambda x: f"{x:.2%}"})

    def _add_risk_metrics(self) -> None:
        """Create risk metric tables (VaR, CVaR, drawdowns)."""
        var_cvar = self.calculator.calculate_var_cvar()
        risk_df = pd.DataFrame(
            {"Metric": ["VaR 95%", "CVaR 95%"], "Value": [var_cvar["var"], var_cvar["cvar"]]}
        )
        self.add_table(risk_df, "Risk Metrics", format_dict={"Value": lambda x: f"{x:.2%}"})

        drawdowns = self.calculator.calculate_drawdowns()
        dd_df = pd.DataFrame(
            {
                "Metric": ["Max Drawdown", "Average Drawdown", "Drawdown Std"],
                "Value": [
                    drawdowns["max_drawdown"],
                    drawdowns["avg_drawdown"],
                    drawdowns["drawdown_std"],
                ],
            }
        )
        self.add_table(dd_df, "Drawdown Metrics", format_dict={"Value": lambda x: f"{x:.2%}"})

    def _add_visualizations(self) -> None:
        """Add main simulation plots."""
        self.add_section("Visualizations", level=2)

        # Portfolio value evolution
        plt.figure(figsize=(12, 6))
        self.visualizer.plot_portfolio_value_evolution()
        self.add_plot(plt.gcf(), "Portfolio Value Evolution")
        plt.close()

        # Returns distribution
        plt.figure(figsize=(10, 6))
        self.visualizer.plot_return_distribution()
        self.add_plot(plt.gcf(), "Returns Distribution")
        plt.close()

        # Portfolio weights evolution (if applicable)
        try:
            plt.figure(figsize=(12, 6))
            self.visualizer.plot_asset_weight_evolution()
            self.add_plot(plt.gcf(), "Weights Distribution")
            plt.close()
        except Exception:
            # Some simulation types may not include dynamic weights
            pass

        # Metrics dashboard
        plt.figure(figsize=(15, 12))
        self.visualizer.plot_metrics_dashboard()
        self.add_plot(plt.gcf(), "Metrics Dashboard")
        plt.close()

    def _add_conclusions(self) -> None:
        """Add a summary section with key results and interpretation."""
        self.add_section("Conclusions", level=2)

        stats = self.calculator.calculate_basic_statistics()
        var_cvar = self.calculator.calculate_var_cvar()

        conclusions = [
            "\nBased on the Monte Carlo simulations, we can conclude:",
            f"\n1. The expected mean return is {stats['mean_return']:.2%}, "
            f"with a standard deviation of {stats['std_deviation']:.2%}.",
            f"2. There is a {var_cvar['var']:.2%} risk of loss (VaR 95%).",
            f"3. In extreme scenarios, the expected average loss is {var_cvar['cvar']:.2%} (CVaR 95%).",
        ]

        if isinstance(self.simulation, MonteCarloPortfolio):
            conclusions.append(
                "4. The portfolio simulation shows multiple possible compositions for the portfolio."
            )
        elif isinstance(self.simulation, MonteCarloReturn):
            conclusions.append(
                "4. The return simulation keeps portfolio weights fixed and explores different market scenarios."
            )

        self.add_section("", "\n".join(conclusions))
