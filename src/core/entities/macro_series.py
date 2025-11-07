"""
Module for representing and analyzing macroeconomic time series data.
Implements the Strategy pattern for data extraction and the Observer pattern for statistics updates.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Union, Optional
import pandas as pd
from src.core.entities.time_series import TimeSeries
from src.extractor.macro_extractor import MacroExtractor

@dataclass
class MacroSeries(TimeSeries):
    """
    A container class for macroeconomic time series data implementing the Strategy pattern.
    
    This class extends TimeSeries to handle macroeconomic indicators across different countries.
    It uses MacroExtractor as a strategy for data acquisition and maintains statistical metrics
    following the Observer pattern (stats are automatically updated when data changes).

    Attributes
    ----------
    indicators : Union[str, List[str]]
        Economic indicators to track (e.g., 'GDP', 'CPI', 'UNEMPLOYMENT')
    countries : Union[str, List[str]]
        Countries to analyze, default ['ESP', 'EUU']
    stats : Dict[str, Dict[str, float]]
        Statistical metrics for each indicator and country
        
    Design Patterns
    --------------
    - Strategy Pattern: Uses MacroExtractor for data acquisition
    - Observer Pattern: Auto-updates statistics when data changes
    - Template Method: Inherits from TimeSeries base class
    """
    
    indicators: Union[str, List[str]] = field(default_factory=list)
    countries: Union[str, List[str]] = field(default_factory=lambda: ["ESP", "EUU"])
    stats: Dict[str, Dict[str, float]] = field(default_factory=dict, init=False)
    
    def __post_init__(self) -> None:
        """
        Initialize the time series and compute initial statistics.
        
        This method implements the Template Method pattern by:
        1. Processing input parameters
        2. Extracting data using the strategy pattern
        3. Computing initial statistics as an observer
        """
        if isinstance(self.indicators, str):
            self.indicators = self.indicators.replace(",", " ").split()
            
        if isinstance(self.countries, str):
            self.countries = self.countries.replace(",", " ").split()
            
        extractor = MacroExtractor()
        self.data = extractor.extract(
            indicators=self.indicators,
            countries=self.countries,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        self._compute_stats()
        
    def _compute_stats(self) -> None:
        """
        Compute comprehensive statistics for each indicator and country.
        
        Statistical Metrics:
        - Mean: Average value over the period
        - Standard Deviation: Measure of volatility
        - Min/Max: Range boundaries
        - Total Change: Overall percentage change
        - Average Annual Change: Annualized rate of change
        
        This method implements the Observer pattern by automatically
        updating statistics when called after data changes.
        """
        if self.data.empty:
            self.stats = {}
            return
            
        self.stats = {}
        
        for indicator in self.data.columns.get_level_values(0).unique():
            indicator_data = self.data[indicator]
            country_stats = {}
            for country in indicator_data.columns:
                series = indicator_data[country].dropna()
                
                if not series.empty:
                    total_change = (series.iloc[-1] / series.iloc[0] - 1) if len(series) > 1 else 0
                    avg_change = (
                        (series.pct_change().mean() * len(series))
                        if len(series) > 1 else 0
                    )
                    
                    country_stats[country] = {
                        "mean": float(series.mean()),
                        "std": float(series.std()),
                        "min": float(series.min()),
                        "max": float(series.max()),
                        "total_change": float(total_change),
                        "avg_annual_change": float(avg_change)
                    }
                    
            self.stats[indicator] = country_stats
    
    def get_latest_values(self) -> pd.DataFrame:
        """
        Retrieve the most recent values for each indicator and country.
        
        This method provides a snapshot of the current state of all
        macroeconomic indicators across countries.

        Returns
        -------
        pd.DataFrame
            DataFrame with indicators as columns and countries as index,
            containing the most recent available values
        """
        if self.data.empty:
            return pd.DataFrame()
            
        latest = {}
        for indicator in self.data.columns.get_level_values(0).unique():
            latest[indicator] = self.data[indicator].iloc[-1]
            
        return pd.DataFrame(latest)
    
    def get_changes(
        self,
        periods: Optional[int] = None,
        annualized: bool = True
    ) -> pd.DataFrame:
        """
        Calculate percentage changes in indicators over specified periods.
        
        This method implements a flexible change calculation strategy that can
        handle both total and annualized changes over any time period.

        Parameters
        ----------
        periods : int, optional
            Number of periods to calculate change over
            If None, uses entire available period
        annualized : bool, default True
            If True, converts changes to annual rates
            
        Returns
        -------
        pd.DataFrame
            DataFrame with calculated changes for each indicator and country
        """
        if self.data.empty:
            return pd.DataFrame()
            
        changes = {}
        for indicator in self.data.columns.get_level_values(0).unique():
            indicator_data = self.data[indicator]
            
            if periods:
                start_values = indicator_data.iloc[-periods-1]
                end_values = indicator_data.iloc[-1]
            else:
                start_values = indicator_data.iloc[0]
                end_values = indicator_data.iloc[-1]
                
            total_change = (end_values / start_values - 1)
            
            if annualized and periods:
                changes[indicator] = (1 + total_change) ** (1 / (periods/12)) - 1
            else:
                changes[indicator] = total_change
                
        return pd.DataFrame(changes)
    
    def get_correlations(self) -> Dict[str, pd.DataFrame]:
        """
        Calculate correlation matrices between countries for each indicator.
        
        This method provides insight into the relationships between different
        countries' economic indicators, useful for analyzing economic integration
        and spillover effects.

        Returns
        -------
        Dict[str, pd.DataFrame]
            Dictionary mapping each indicator to its country correlation matrix
        """
        if self.data.empty:
            return {}
            
        correlations = {}
        for indicator in self.data.columns.get_level_values(0).unique():
            correlations[indicator] = self.data[indicator].corr()
            
        return correlations
    
    def describe(self) -> None:
        """
        Print comprehensive descriptive statistics for all indicators.
        
        This method provides a human-readable summary of the macroeconomic data,
        including key statistics and changes for each indicator and country.
        Implements the Template Method pattern for consistent data presentation.
        """
        print(f"=== Statistics for {self.name} ===")
        
        for indicator, country_stats in self.stats.items():
            print(f"\nIndicator: {indicator}")
            for country, stats in country_stats.items():
                print(f"\n{country}:")
                for stat, value in stats.items():
                    if "change" in stat:
                        print(f"  {stat}: {value:.2%}")
                    else:
                        print(f"  {stat}: {value:.4f}")