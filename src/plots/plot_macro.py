"""
Macroeconomic Time Series Visualization Framework.

This module implements a comprehensive visualization system for macroeconomic
time series analysis using multiple design patterns to ensure flexibility,
maintainability, and extensibility.

Design Patterns used in this implementation:
    - Builder Pattern: Constructs complex visualization dashboards and composite figures.
    - Strategy Pattern: Allows swapping visualization/analysis strategies (e.g., decomposition,
      correlation, distribution) without modifying the visualizer core.
    - Template Method: Centralized standard formatting, validation and plotting conventions
      so all visualizations follow a consistent style.
    - Facade Pattern: Exposes a simplified high-level API (single class) that wraps complex
      plotting and analysis steps (e.g., decomposition + dashboard assembly).

Key Features:
    - Time series plotting (single/multiple series)
    - Year-over-year (annual) variation analysis
    - Rolling correlation analysis
    - Scatter / regression relationships between indicators
    - Seasonal decomposition (trend, seasonal, residual)
    - Multi-component statistical dashboard for a chosen indicator
"""

from pathlib import Path
from typing import List, Optional, Union, Dict

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose


class MacroSeriesVisualizer:
    """
    A flexible visualizer for macroeconomic time series.

    This class provides a high-level facade for multiple common visualizations
    used in macroeconomic analysis. Internally it uses several design patterns:

      - Template Method: The constructor prepares and validates the data once;
        individual plotting methods rely on that standardized data format.
      - Strategy: Each plotting method implements a different "strategy" (time
        series, annual variation, rolling correlation, scatter/regression,
        decomposition). Strategies can be extended or replaced independently.
      - Builder: Methods that assemble multi-panel dashboards build the final
        figure from smaller components (subplots, annotations, grids).
      - Facade: This class provides a single, convenient API surface so users
        don't need to know the low-level plot assembly details.

    Responsibilities:
      - Ensure the input DataFrame has a DateTimeIndex and numeric values.
      - Provide descriptive and consistent plot formatting and labels.
      - Handle typical edge-cases (missing data, insufficient observations).
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the visualizer with time series data and perform standardized
        data preparation steps (Template Method).

        Required data format:
          - index: convertible to pandas.DatetimeIndex (strings, PeriodIndex, etc. are accepted)
          - columns: each column is a numeric indicator (different countries, aggregates or indicators)
          - values: numeric or convertible to numeric (non-numeric will raise later)

        Steps performed:
          1. Validate that the DataFrame is not empty.
          2. Deep copy the data to prevent outside mutation.
          3. Convert PeriodIndex to timestamps if needed, otherwise attempt to
             coerce the index to pandas.DatetimeIndex.
          4. Leave columns and values as provided (plot methods will handle NaNs).

        Raises
        ------
        ValueError
            If data is None/empty, or the index cannot be converted to datetime.
        """
        if data is None or data.empty:
            raise ValueError("Input DataFrame must not be None or empty.")

        # Work with a copy to avoid side-effects
        self.data = data.copy()

        # Convert PeriodIndex to timestamps (commonly found in economic datasets)
        if isinstance(self.data.index, pd.PeriodIndex):
            self.data.index = self.data.index.to_timestamp()
        # Ensure DatetimeIndex for time-based plotting
        elif not isinstance(self.data.index, pd.DatetimeIndex):
            try:
                self.data.index = pd.to_datetime(self.data.index)
            except Exception as e:
                raise ValueError(f"Could not convert index to datetime: {e}")

    def plot_time_series(self) -> plt.Figure:
        """
        Plot all series in the DataFrame on a single time axis.

        Purpose:
          - Provide a standardized multi-series line chart for quick inspection
            of the historical evolution of all indicators present in the DataFrame.

        Design patterns involved:
          - Template Method: applies standard figure size, grid, legend placement.
          - Strategy: implements the 'time series' visualization approach.
          - Builder: composes lines, legend, axes formatting into one figure.

        Returns
        -------
        matplotlib.figure.Figure
            A Figure object containing the time series plot.

        Behavior / Features
          - Each column is plotted as a separate line.
          - Legend is placed outside the plot for clarity.
          - Grid and tight layout applied automatically.
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        for col in self.data.columns:
            # If a column contains non-numeric values, matplotlib will raise.
            ax.plot(self.data.index, self.data[col], label=col, linewidth=1)

        ax.set_title("Time Series Evolution")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return fig

    def plot_annual_variation(self) -> plt.Figure:
        """
        Plot year-over-year percentage changes for each series.

        Purpose:
          - Visualize the year-over-year percentage change (annual variation)
            for each indicator in the dataset. Useful to inspect growth rates
            and sign changes across time.

        Steps:
          1. Compute percent change with a 12-period shift (assuming monthly data).
          2. Plot each series with markers.
          3. Add a zero reference line and annotate the most recent non-NaN
             value for each series.

        Design patterns involved:
          - Strategy: this method is a particular analysis strategy (annual % change).
          - Template Method: consistent figure formatting and labeling.
          - Builder: assembles lines, markers, annotations and reference lines.

        Notes:
          - If the input frequency is not monthly, the 12-period assumption should
            be adapted by the caller or by extending the method.
          - Missing data is handled by pandas pct_change and dropna logic.

        Returns
        -------
        matplotlib.figure.Figure
            Figure object with the annual variation lines and annotations.
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Store last non-NaN points to annotate later
        last_points = {}

        for col in self.data.columns:
            # compute year-over-year percent change (12 periods)
            annual_pct = self.data[col].pct_change(periods=12) * 100
            annual_pct = annual_pct.dropna()

            if annual_pct.empty:
                # skip series with no valid annual changes
                continue

            ax.plot(annual_pct.index, annual_pct, marker="o", label=col, alpha=0.7)
            # remember last point for annotation
            last_valid_idx = annual_pct.last_valid_index()
            if last_valid_idx is not None:
                last_points[col] = (last_valid_idx, annual_pct.loc[last_valid_idx])

        # Zero reference line
        ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)

        ax.set_title("Year-over-Year Variation (%)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Percentage change (%)")
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax.grid(True, alpha=0.3)

        # Annotate the most recent value for each series (keeps plot readable)
        for col, (idx, val) in last_points.items():
            # convert x position to integer index for text placement relative to axis
            # annotate near the point (+ offset up for positive, down for negative)
            offset = 0.5 if val >= 0 else -2.0
            try:
                ax.text(idx, val + offset, f"{val:.1f}%", ha="center",
                        va="bottom" if val >= 0 else "top")
            except Exception:
                # if text placement by datetime index fails, skip annotation
                pass

        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

    def plot_rolling_correlation(self, indicators: List[str], window: int = 12) -> plt.Figure:
        """
        Plot rolling correlation between exactly two indicators.

        Purpose:
          - Show how the linear correlation between two indicators evolves over time,
            using a rolling window.

        Parameters
        ----------
        indicators : list[str]
            A list with exactly two column names present in the DataFrame (e.g. ['GDP', 'Inflation']).
        window : int, optional (default=12)
            Window size (in number of observations) for the rolling correlation calculation.

        Design patterns involved:
          - Strategy: implements correlation-as-a-strategy.
          - Template Method: applies standard axis, title, grid format.

        Returns
        -------
        matplotlib.figure.Figure
            Figure with the rolling correlation line and a horizontal 0 reference.

        Raises
        ------
        ValueError
            - if not exactly two indicators are provided
            - if either indicator is missing from the DataFrame
            - if window is less than 1
        """
        # Input validation
        if len(indicators) != 2:
            raise ValueError("Exactly two indicators must be provided for correlation analysis.")

        for name in indicators:
            if name not in self.data.columns:
                raise ValueError(f"Indicator '{name}' not found in the DataFrame.")

        if window < 1:
            raise ValueError("Window size must be a positive integer.")

        # compute rolling correlation (pandas aligns by index)
        corr_series = self.data[indicators[0]].rolling(window=window).corr(self.data[indicators[1]])

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(self.data.index, corr_series, linewidth=1, label=f"RollingCorr({window})")
        ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)

        ax.set_title(f"Rolling Correlation ({window} periods): {indicators[0]} vs {indicators[1]}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Correlation coefficient")
        ax.set_ylim(-1.05, 1.05)
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()
        return fig

    def plot_scatter_indicators(self, x: str, y: str) -> plt.Figure:
        """
        Draw a scatter plot between two indicators and fit a regression line.

        Purpose:
          - Visualize the bivariate relationship between two indicators.
          - Show linear fit (regression) and a confidence envelope (provided by seaborn).

        Parameters
        ----------
        x : str
            Column name for the x-axis indicator (e.g. 'GDP_Growth').
        y : str
            Column name for the y-axis indicator (e.g. 'Inflation_Rate').

        Design patterns involved:
          - Strategy: this visualization implements the scatter/regression strategy.
          - Template Method: consistent figure formatting.

        Returns
        -------
        matplotlib.figure.Figure
            A Figure with scatter points, a regression line and (by seaborn) a CI band.

        Raises
        ------
        ValueError
            If either x or y is not a column in the DataFrame or if there is not enough
            data to produce a meaningful plot.
        """
        if x not in self.data.columns or y not in self.data.columns:
            raise ValueError("Both x and y indicators must exist in the DataFrame.")

        # Drop rows where either value is missing for plotting
        plot_df = self.data[[x, y]].dropna()
        if plot_df.empty:
            raise ValueError("Insufficient data available to produce scatter plot.")

        fig, ax = plt.subplots(figsize=(10, 8))

        # Use seaborn regplot to draw scatter + regression line + confidence interval
        sns.regplot(data=plot_df, x=x, y=y, ax=ax, scatter_kws={"alpha": 0.5})

        ax.set_title(f"Relationship between {x} and {y}")
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def plot_decomposition(self, indicator: str, period: Optional[int] = 12) -> plt.Figure:
        """
        Perform a seasonal decomposition and plot observed, trend, seasonal and residual components.

        Purpose:
          - Decompose a single time series into additive components: observed, trend,
            seasonal and residual (irregular) using statsmodels' seasonal_decompose.

        Parameters
        ----------
        indicator : str
            Column name to be decomposed (must exist in the DataFrame).
        period : int or None, optional (default=12)
            Seasonal period to use for decomposition. If None, the function will try
            to infer it; for monthly data, 12 is typical.

        Design patterns involved:
          - Strategy: decomposition is treated as an analysis strategy.
          - Facade: this method hides the complexity of the statsmodels API and plotting.

        Returns
        -------
        matplotlib.figure.Figure
            A figure with four stacked subplots: observed, trend, seasonal, residual.

        Raises
        ------
        ValueError
            - If the indicator is missing.
            - If data is insufficient for decomposition or the decomposition fails.
        """
        if indicator not in self.data.columns:
            raise ValueError(f"Indicator '{indicator}' not found in the DataFrame.")

        series = self.data[indicator].dropna()
        if series.empty:
            raise ValueError(f"No data available for indicator '{indicator}' to decompose.")

        # Attempt decomposition; statsmodels will raise if not possible
        decomposition = seasonal_decompose(series, period=period, model="additive", extrapolate_trend="freq")

        fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

        axes[0].plot(series.index, decomposition.observed)
        axes[0].set_title("Observed")
        axes[0].grid(True, alpha=0.3)

        axes[1].plot(series.index, decomposition.trend)
        axes[1].set_title("Trend")
        axes[1].grid(True, alpha=0.3)

        axes[2].plot(series.index, decomposition.seasonal)
        axes[2].set_title("Seasonal")
        axes[2].grid(True, alpha=0.3)

        axes[3].plot(series.index, decomposition.resid)
        axes[3].set_title("Residual")
        axes[3].grid(True, alpha=0.3)

        axes[-1].set_xlabel("Date")
        plt.tight_layout()
        return fig

    def plot_macro_dashboard(self, indicator: str) -> plt.Figure:
        """
        Build a multi-panel dashboard for a single indicator.

        Dashboard layout and components:
          - Top row (full width): historical time series for the indicator.
          - Middle-left: year-over-year percentage changes (bar chart, green/red for sign).
          - Middle-right: distribution (histogram + KDE).
          - Bottom-left: seasonal pattern (monthly average line).
          - Bottom-right: monthly distribution (boxplot) or message when insufficient.

        Purpose:
          - Provide a compact but informative visual summary for a single macro indicator:
            history, variability, distribution, seasonality, monthly dispersion.

        Design patterns involved:
          - Builder: assembles a grid of subplots into a coherent dashboard.
          - Strategy: combines multiple analysis strategies (trend, distribution, seasonality).
          - Template Method: applies consistent labels, grid, and layout rules.
          - Facade: single call that hides multi-step figure assembly.

        Parameters
        ----------
        indicator : str
            Column name to analyze (e.g. 'GDP', 'Inflation').

        Returns
        -------
        matplotlib.figure.Figure
            A composite figure with multiple analytical panels for the requested indicator.

        Raises
        ------
        ValueError
            If the indicator is not present in the DataFrame or there is insufficient data.
        """
        if indicator not in self.data.columns:
            raise ValueError(f"Indicator '{indicator}' not found in the DataFrame.")

        # Basic check for existence of numeric data
        if self.data[indicator].dropna().empty:
            raise ValueError(f"No data available for indicator '{indicator}' to build dashboard.")

        fig = plt.figure(figsize=(15, 12))
        gs = fig.add_gridspec(3, 2)

        # Top (full width) - historical series
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(self.data.index, self.data[indicator], label="Value", linewidth=1)
        ax1.set_title(f"{indicator} - Historical Evolution")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Middle-left - annual variation (12-period percent change)
        ax2 = fig.add_subplot(gs[1, 0])
        annual_pct = self.data[indicator].pct_change(periods=12) * 100
        # Color array: green for non-negative, red for negative (np.where)
        colors = np.where(annual_pct >= 0, "g", "r")
        ax2.bar(self.data.index, annual_pct, color=colors, alpha=0.5)
        ax2.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
        ax2.set_title("Year-over-Year Variation (%)")
        ax2.grid(True, alpha=0.3)

        # Middle-right - distribution (histogram + KDE)
        ax3 = fig.add_subplot(gs[1, 1])
        sns.histplot(data=self.data[indicator].dropna(), ax=ax3, bins=30, stat="density", alpha=0.6)
        # seaborn kdeplot may issue warnings for short series; still useful visually
        try:
            sns.kdeplot(data=self.data[indicator].dropna(), ax=ax3, linewidth=2)
        except Exception:
            # If KDE fails (too few points), ignore and keep histogram
            pass
        ax3.set_title("Value Distribution")
        ax3.grid(True, alpha=0.3)

        # Bottom-left - monthly seasonal pattern (monthly means)
        ax4 = fig.add_subplot(gs[2, 0])
        # Create a temporary 'Month' column for grouping by month-of-year
        month_series = self.data[indicator].copy()
        month_index = self.data.index
        month_numbers = pd.Series(month_index.month, index=month_index)
        monthly_means = month_series.groupby(month_numbers).mean()
        # Reindex to ensure months 1..12 are represented (NaN for missing months)
        monthly_means = monthly_means.reindex(range(1, 13))

        months_with_values = monthly_means.dropna().index
        values_with_data = monthly_means.dropna().values
        if len(months_with_values) > 0:
            ax4.plot(months_with_values, values_with_data, marker="o")
            ax4.set_xticks(range(1, 13))
        else:
            ax4.text(0.5, 0.5, "Not enough data for seasonal pattern",
                     horizontalalignment="center", verticalalignment="center", transform=ax4.transAxes)
        ax4.set_title("Monthly Average (Seasonal Pattern)")
        ax4.grid(True, alpha=0.3)

        # Bottom-right - monthly distribution (boxplot) or fallback message
        ax5 = fig.add_subplot(gs[2, 1])
        # Rebuild the temporary DataFrame with month column for boxplot grouping
        df_month = pd.DataFrame({
            "Month": month_numbers,
            "Value": self.data[indicator]
        }).dropna()

        if df_month["Month"].nunique() > 1 and not df_month["Value"].empty:
            sns.boxplot(data=df_month, x="Month", y="Value", ax=ax5)
            ax5.set_xlabel("Month")
        else:
            ax5.text(0.5, 0.5, "Insufficient data for monthly boxplot",
                     horizontalalignment="center", verticalalignment="center", transform=ax5.transAxes)
        ax5.set_title("Monthly Distribution")
        ax5.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig