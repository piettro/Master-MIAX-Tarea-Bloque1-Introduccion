"""
Specialized report for price time series analysis.
Generates complete reports with visualizations and analytics for financial assets.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from src.reports.report_base import BaseReport
from src.plots.plot_price_series import PriceSeriesVisualizer
from src.core.entities.price_series import PriceSeries


class PriceSeriesReport(BaseReport):
    """Specialized report for price time series analysis.

    Produces detailed reports (individual and consolidated) containing
    technical charts, statistical tables, return analysis and risk metrics.
    """

    def __init__(
        self,
        price_series: PriceSeries,
        title: str = "Price Time Series Analysis Report",
        include_plots: bool = True,
        include_tables: bool = True,
        moving_averages: Optional[List[int]] = None,
    ) -> None:
        """Initialize PriceSeriesReport.

        Args:
            price_series (PriceSeries): Domain object with time series data.
            title (str, optional): Report title. Defaults to
                "Price Time Series Analysis Report".
            include_plots (bool, optional): Whether to include plots.
                Defaults to True.
            include_tables (bool, optional): Whether to include tables.
                Defaults to True.
            moving_averages (Optional[List[int]], optional): List of MA
                windows to include. Defaults to [20, 50, 200].
        """
        super().__init__(title=title, include_plots=include_plots, include_tables=include_tables)

        self.price_series = price_series
        self.data = price_series.data
        self.moving_averages = moving_averages if moving_averages is not None else [20, 50, 200]

        # Expect a MultiIndex on columns with levels ['Price', 'Ticker']
        if not isinstance(self.data.columns, pd.MultiIndex):
            raise ValueError("DataFrame must have a MultiIndex on columns (Price, Ticker).")

        if self.data.columns.names != ["Price", "Ticker"]:
            raise ValueError("MultiIndex must have levels ['Price', 'Ticker'].")

        self.required_columns = ["Open", "High", "Low", "Close", "Volume"]
        price_level_values = self.data.columns.get_level_values("Price")
        if not all(col in price_level_values for col in self.required_columns):
            raise ValueError(f"PriceSeries must contain columns: {', '.join(self.required_columns)}")

        self.symbols: List[str] = (
            price_series.symbols if isinstance(price_series.symbols, list) else [price_series.symbols]
        )
        self.symbol_data: Dict[str, pd.DataFrame] = {}
        self.visualizers: Dict[str, PriceSeriesVisualizer] = {}

    def generate(self) -> List[Path]:
        """Generate individual reports for each symbol and a consolidated report.

        Returns:
            List[Path]: Paths to all generated reports (individual + consolidated).
        """
        saved_reports: List[Path] = []
        consolidated_sections: List[Dict[str, Any]] = []

        for idx, symbol in enumerate(self.symbols):
            print(f"\nGenerating report for {symbol}...")

            # Reset sections for the individual report
            self.sections = []

            # Prepare symbol data and visualizer
            self._prepare_symbol_data(symbol)

            # Header for the symbol
            self.add_section(f"Report: {symbol}", level=1)

            # Basic information
            self._add_info_section(symbol)

            # Technical analysis (charts)
            if self.include_plots:
                self._add_technical_analysis(symbol)

            # Statistical analysis (tables)
            if self.include_tables:
                self._add_statistical_analysis(symbol)

            # Returns analysis
            self._add_returns_analysis(symbol)

            # Risk analysis
            self._add_risk_analysis(symbol)

            # Save individual report
            individual_path = self.save(symbols=[symbol])
            saved_reports.append(individual_path)

            # Collect sections for consolidated report
            consolidated_sections.extend(self.sections)
            if idx != len(self.symbols) - 1:
                # add separator between symbols when consolidating
                consolidated_sections.append({"title": "", "content": "---\n", "level": 0})

        # Generate consolidated report
        self.sections = consolidated_sections
        consolidated_path = self.save(symbols=self.symbols)
        saved_reports.append(consolidated_path)

        print("\nReports successfully generated:")
        print(f"- Individual reports: {len(self.symbols)}")
        print("- Consolidated report: 1")
        print(f"Total reports: {len(saved_reports)}")

        return saved_reports

    def _prepare_symbol_data(self, symbol: str) -> None:
        """Prepare and cache the DataFrame for a specific symbol.

        Args:
            symbol (str): Asset ticker/symbol.
        """
        if symbol in self.symbol_data:
            return

        # Build DataFrame for the symbol from the multi-index source
        symbol_df = pd.DataFrame()
        for col in self.required_columns:
            symbol_df[col] = self.data[(col, symbol)]

        self.symbol_data[symbol] = symbol_df
        self.visualizers[symbol] = PriceSeriesVisualizer(symbol_df)

    def _add_info_section(self, symbol: str) -> None:
        """Add a section with basic information about the asset.

        Args:
            symbol (str): Asset symbol.
        """
        self.add_section("Asset Information", level=2)

        df = self.symbol_data[symbol]
        first_price = df["Close"].iloc[0]
        last_price = df["Close"].iloc[-1]

        info_lines = [
            f"- **Symbol:** {symbol}",
            f"- **Period:** {self.price_series.start_date} to {self.price_series.end_date}",
            f"- **Number of Observations:** {len(df)}",
            f"- **First Price:** {first_price:.2f}",
            f"- **Last Price:** {last_price:.2f}",
            f"- **Total Change:** {(last_price / first_price - 1):.2%}",
        ]

        self.add_section("", "\n".join(info_lines))

    def _add_technical_analysis(self, symbol: str) -> None:
        """Add technical analysis plots for the symbol.

        Includes price series with moving averages, candlestick chart and volume.
        """
        self.add_section("Technical Analysis", level=2)

        visualizer = self.visualizers[symbol]

        # Prices and moving averages
        fig = visualizer.plot_prices(window_ma=self.moving_averages)
        self.add_plot(fig, "Price Evolution and Moving Averages", level=3)
        plt.close()

        # Candlestick chart
        fig = visualizer.plot_candlestick()
        self.add_plot(fig, "Candlestick Chart", level=3)
        plt.close()

        # Volume plot
        fig = visualizer.plot_volume()
        self.add_plot(fig, "Trading Volume", level=3)
        plt.close()

    def _add_statistical_analysis(self, symbol: str) -> None:
        """Add descriptive statistics tables for the symbol.

        Args:
            symbol (str): Asset symbol.
        """
        self.add_section("Statistical Analysis", level=2)
        df = self.symbol_data[symbol]

        stats = pd.DataFrame(
            {
                "Metric": [
                    "Mean",
                    "Median",
                    "StdDev",
                    "Min",
                    "Max",
                    "Skewness",
                    "Kurtosis",
                ],
                "Close": [
                    df["Close"].mean(),
                    df["Close"].median(),
                    df["Close"].std(),
                    df["Close"].min(),
                    df["Close"].max(),
                    df["Close"].skew(),
                    df["Close"].kurtosis(),
                ],
                "Volume": [
                    df["Volume"].mean(),
                    df["Volume"].median(),
                    df["Volume"].std(),
                    df["Volume"].min(),
                    df["Volume"].max(),
                    df["Volume"].skew(),
                    df["Volume"].kurtosis(),
                ],
            }
        )

        format_dict = {"Close": lambda x: f"{x:.2f}", "Volume": lambda x: f"{x:,.0f}"}

        self.add_table(stats, "Descriptive Statistics", format_dict=format_dict)

    def _add_returns_analysis(self, symbol: str) -> None:
        """Add returns analysis: plots and summary statistics.

        Args:
            symbol (str): Asset symbol.
        """
        self.add_section("Returns Analysis", level=2)

        visualizer = self.visualizers[symbol]

        # Return distribution plot (log returns)
        if self.include_plots:
            fig = visualizer.plot_returns(return_type="log")
            self.add_plot(fig, "Returns Distribution", level=3)
            plt.close()

        # Return statistics table
        if self.include_tables:
            df = self.symbol_data[symbol]
            returns = np.log(df["Close"] / df["Close"].shift(1)).dropna()

            stats = pd.DataFrame(
                {
                    "Metric": [
                        "Average Daily Return",
                        "Annualized Return",
                        "Daily Volatility",
                        "Annualized Volatility",
                        "Sharpe Ratio",
                        "Skewness",
                        "Kurtosis",
                    ],
                    "Value": [
                        returns.mean(),
                        returns.mean() * 252,
                        returns.std(),
                        returns.std() * np.sqrt(252),
                        (returns.mean() * 252) / (returns.std() * np.sqrt(252)),
                        returns.skew(),
                        returns.kurtosis(),
                    ],
                }
            )

            format_dict = {
                "Value": lambda x: f"{x:.2%}" if isinstance(x, (float, np.floating)) and abs(x) < 10 else f"{x:.4f}"
            }

            self.add_table(stats, "Return Statistics", format_dict=format_dict)

    def _add_risk_analysis(self, symbol: str) -> None:
        """Add risk-related charts and the dashboard for the symbol.

        Args:
            symbol (str): Asset symbol.
        """
        self.add_section("Risk Analysis", level=2)

        visualizer = self.visualizers[symbol]

        if self.include_plots:
            # Volatility
            fig = visualizer.plot_volatility()
            self.add_plot(fig, "Rolling Volatility", level=3)
            plt.close()

            # Drawdown
            fig = visualizer.plot_drawdown()
            self.add_plot(fig, "Drawdown Analysis", level=3)
            plt.close()

            # Full dashboard (includes MA windows)
            fig = visualizer.plot_dashboard(window_ma=self.moving_averages)
            self.add_plot(fig, "Complete Dashboard", level=2)
            plt.close()
