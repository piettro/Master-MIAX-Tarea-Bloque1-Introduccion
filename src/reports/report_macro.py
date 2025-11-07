"""
Specialized report for macroeconomic time series analysis.
Generates complete reports with visualizations and analyses of indicators.
"""

from pathlib import Path
from typing import List, Union
import pandas as pd
from src.core.entities.macro_series import MacroSeries
from src.reports.report_base import BaseReport
from src.plots.plot_macro import MacroSeriesVisualizer

class MacroReport(BaseReport):
    """Report generator for macroeconomic series analysis."""

    def __init__(
        self,
        macro_series: MacroSeries,
        title: str = "Macroeconomic Analysis Report",
        include_plots: bool = True,
        include_tables: bool = True,
    ) -> None:
        """Initialize MacroReport.

        Args:
            macro_series (MacroSeries): Domain object that contains the
                multi-country, multi-indicator DataFrame in `.data`.
            title (str, optional): Report title. Defaults to
                "Macroeconomic Analysis Report".
            include_plots (bool, optional): Whether to include plots.
                Defaults to True.
            include_tables (bool, optional): Whether to include tables.
                Defaults to True.

        Raises:
            ValueError: If the underlying DataFrame columns are not a
                MultiIndex with names ['Country', 'Indicator'].
        """
        super().__init__(title=title, include_plots=include_plots, include_tables=include_tables)

        self.macro_series = macro_series
        self.data = macro_series.data

        # Expecting a MultiIndex on columns with levels: ['Country', 'Indicator']
        if not isinstance(self.data.columns, pd.MultiIndex) or self.data.columns.names != ['Country', 'Indicator']:
            raise ValueError("Expected DataFrame with MultiIndex columns: ['Country', 'Indicator']")

        self.countries: List[str] = self.data.columns.get_level_values('Country').unique().tolist()
        self.indicators: List[str] = self.data.columns.get_level_values('Indicator').unique().tolist()
        self.visualizers: dict = {}

    def _prepare_indicator_data(self, indicator: str) -> pd.DataFrame:
        """Prepare a DataFrame containing the specified indicator for all countries.

        The returned DataFrame has countries as columns and a PeriodIndex (yearly).

        Args:
            indicator (str): Indicator name to extract.

        Returns:
            pd.DataFrame: Cleaned DataFrame for the indicator.

        Raises:
            ValueError: If no valid data exists for the given indicator or
                an error occurs during preparation.
        """
        try:
            # Select all countries for the given indicator
            df = self.data.xs(indicator, level='Indicator', axis=1)

            # Drop columns that are entirely NaN
            df = df.dropna(how='all')

            if df.empty:
                raise ValueError(f"No valid data available for indicator '{indicator}'.")

            # Convert index to yearly PeriodIndex for consistent handling
            df.index = pd.PeriodIndex(df.index, freq='Y')

            return df

        except Exception as exc:
            raise ValueError(f"Error preparing data for indicator '{indicator}': {exc}") from exc

    def _add_info_section(self, indicator: str) -> None:
        """Add a brief information section about the indicator.

        Includes analysis period and total variation per country.

        Args:
            indicator (str): Indicator to describe.
        """
        df = self._prepare_indicator_data(indicator)

        # Ensure chronological order
        df = df.sort_index()

        start = str(df.index.min())
        end = str(df.index.max())

        # Prepare variation info per country
        country_infos: List[str] = []
        for country in df.columns:
            series = df[country].dropna()
            if not series.empty:
                first_value = series.iloc[0]
                last_value = series.iloc[-1]
                if pd.notna(first_value) and pd.notna(last_value) and first_value != 0:
                    variation = f"{(last_value / first_value - 1) * 100:.2f}%"
                else:
                    variation = "N/A"
                country_infos.append(f"- **{country}**: {variation}")

        content = (
            f"### Analysis Period\n"
            f"- From: {start}\n"
            f"- To: {end}\n\n"
            f"### Total Variation by Country\n" +
            ("\n".join(country_infos) if country_infos else "No valid series available for any country.")
        )

        self.add_section(f"Indicator Summary: {indicator}", content, level=2)

    def _add_statistical_analysis(self, indicator: str) -> None:
        """Add descriptive statistics table for the indicator across countries.

        Args:
            indicator (str): Indicator to analyze.
        """
        df = self._prepare_indicator_data(indicator)

        # Compute descriptive statistics per country
        stats_list = []
        for country in df.columns:
            stats = df[country].describe()
            stats.name = country
            stats_list.append(stats)

        stats_df = pd.concat(stats_list, axis=1)
        stats_df = stats_df.reset_index(names='Stats')

        # Formatting function for numeric values
        format_dict = {col: (lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x) for col in stats_df.columns}

        self.add_table(stats_df, f"Descriptive Statistics: {indicator}", level=3, format_dict=format_dict)

    def _add_variation_analysis(self, indicator: str) -> None:
        """Add annual percentage variation analysis and corresponding table.

        Args:
            indicator (str): Indicator to analyze.
        """
        df = self._prepare_indicator_data(indicator)

        variations_list = []
        for country in df.columns:
            var = df[country].pct_change(periods=1).dropna()
            if not var.empty:
                stats = var.describe()
                stats.name = country
                variations_list.append(stats)

        if variations_list:
            variations_df = pd.concat(variations_list, axis=1)
            variations_df = variations_df.reset_index(names='Stats')
            format_dict = {col: (lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x) for col in variations_df.columns}
            self.add_table(variations_df, f"Annual Percentage Variation: {indicator}", level=3, format_dict=format_dict)
        else:
            self.add_section(
                f"Annual Percentage Variation: {indicator}",
                "Not enough data to compute annual variations.",
                level=3
            )

    def _add_visualizations(self, indicator: str) -> None:
        """Generate and add visualization plots for the indicator.

        Plots include:
            - Time series for all countries
            - Annual variation (if available)
            - Decomposition and seasonality per country

        Args:
            indicator (str): Indicator to visualize.
        """
        df = self._prepare_indicator_data(indicator)
        viz = MacroSeriesVisualizer(df)

        if self.include_plots:
            # Time series for all countries
            fig1 = viz.plot_time_series()
            self.add_plot(fig1, f"Time Series - {indicator}", level=3)

            # Annual variation (may fail if not applicable)
            try:
                fig2 = viz.plot_annual_variation()
                self.add_plot(fig2, f"Annual Variation - {indicator}", level=3)
            except Exception as exc:
                self.add_section(
                    f"Warning - Annual Variation {indicator}",
                    f"Could not generate annual variation plot: {exc}",
                    level=3
                )

            # Decomposition and seasonality — do per country since the analysis is specific
            for country in df.columns:
                country_df = pd.DataFrame({country: df[country]})
                country_viz = MacroSeriesVisualizer(country_df)

                # Use a safe call for decomposition (some series may not be decomposable)
                try:
                    fig3 = country_viz.plot_decomposition(indicator=country)
                    self.add_plot(fig3, f"Decomposition: {indicator} - {country}", level=3)
                except Exception as exc:
                    self.add_section(
                        f"Warning - Decomposition {indicator} - {country}",
                        f"Could not generate decomposition: {exc}",
                        level=3
                    )

    def _add_correlation_analysis(self, indicator: str) -> None:
        """Perform correlation analysis between countries for a given indicator.

        Adds both a correlation table and an optional heatmap plot.

        Args:
            indicator (str): Indicator to analyze.
        """
        try:
            # Extract data for this indicator
            df_corr = self.data.xs(indicator, level='Indicator', axis=1)

            # Drop rows or columns with missing data before correlation
            df_corr = df_corr.dropna()

            if df_corr.empty:
                raise ValueError(f"No valid data for correlation on indicator '{indicator}'.")

            # Compute correlation matrix and round to 3 decimals
            corr = df_corr.corr().round(3)

            # Formatting for table display
            format_dict = {col: (lambda x: f"{x:.3f}") for col in corr.columns}

            self.add_table(corr, f"Country Correlation Matrix ({indicator})", level=3, format_dict=format_dict)

            # Add heatmap if plots are enabled
            if self.include_plots:
                import matplotlib.pyplot as plt  # local import to avoid heavy import when not plotting
                import seaborn as sns

                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, fmt='.3f', ax=ax)
                ax.set_title(f"Correlation Heatmap: {indicator}")
                plt.tight_layout()
                self.add_plot(fig, f"Correlation Heatmap: {indicator}", level=3)

        except Exception as exc:
            self.add_section(
                f"Error in Correlation Analysis ({indicator})",
                f"Could not generate correlation analysis: {exc}",
                level=3
            )

    def generate(self, auto_save: bool = True) -> Union[str, Path]:
        """Generate the full macroeconomic report and optionally save it.

        The report composes sections for each indicator:
            - Basic info and period
            - Descriptive statistics
            - Annual variation tables
            - Visualizations (time series, variation, decomposition)
            - Correlation analysis

        Args:
            auto_save (bool, optional): If True, automatically saves the report
                after generation. Defaults to True.

        Returns:
            Union[str, Path]: If auto_save is True returns the saved Path.
                Otherwise returns the report content in Markdown as a string.
        """
        # Reset previous sections
        self.sections = []

        generated_reports: List[str] = []
        for indicator in self.indicators:
            try:
                self._add_info_section(indicator)
                self._add_statistical_analysis(indicator)
                self._add_variation_analysis(indicator)
                self._add_visualizations(indicator)
                self._add_correlation_analysis(indicator)
                generated_reports.append(indicator)
            except Exception as exc:
                self.add_section(
                    f"Error processing {indicator}",
                    f"Details: {exc}",
                    level=3
                )
            # Separator between indicators
            self.add_section("---", "", level=1)

        if auto_save:
            # `save` is expected to be implemented by BaseReport
            return self.save(custom_name=self.macro_series.name)

        # Build Markdown content if not saving to file
        full_report: List[str] = []
        for section in self.sections:
            if section.get('level', 0) > 0:
                full_report.append(f"{'#' * section['level']} {section.get('title', '')}")
            if section.get('content'):
                full_report.append(section['content'])
            full_report.append("")

        return "\n".join(full_report)
