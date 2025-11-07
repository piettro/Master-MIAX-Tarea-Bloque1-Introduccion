"""
Module for managing and analyzing financial price time series data.
Implements multiple design patterns for robust price data handling and analysis.
"""

from dataclasses import dataclass, field
from typing import List, Union
from src.core.entities.time_series import TimeSeries
from src.extractor.prices_extractor import MarketDataExtractor
import pandas as pd
import numpy as np
from src.extractor.sources.prices.extractor_prices_base import (
    Interval,
    DataSource
)

@dataclass
class PriceSeries(TimeSeries):
    """
    A sophisticated price series manager implementing multiple design patterns for financial data analysis.
    
    This class extends TimeSeries to handle price data for multiple financial instruments.
    It implements several design patterns to ensure robust data handling and efficient analysis.

    Design Patterns
    --------------
    - Strategy Pattern: Uses MarketDataExtractor for flexible data acquisition
    - Observer Pattern: Auto-updates statistics when price data changes
    - Template Method: Inherits from TimeSeries for consistent time series handling
    - Factory Method: Creates appropriate data structures based on input types
    
    Attributes
    ----------
    symbols : Union[str, List[str]]
        Financial instruments to track (e.g., 'AAPL', 'GOOGL')
    stats : pd.DataFrame
        Statistical metrics computed from price data
    source : DataSource
        Data source strategy for price information
    interval : Interval
        Time interval for price data sampling
    """
    
    symbols: Union[str, List[str]] = field(default_factory=list)
    stats: pd.DataFrame = field(default_factory=pd.DataFrame, init=False)
    source: DataSource = field(default_factory=DataSource.YAHOO)
    interval: Interval = field(default_factory=Interval.DAILY)
    
    def __post_init__(self):
        """
        Initialize price series and compute initial statistics.
        
        This method implements both the Template Method and Factory patterns by:
        1. Normalizing input symbols
        2. Fetching price data using the strategy pattern
        3. Computing initial statistics as an observer
        
        The initialization process follows a template ensuring consistent setup
        across all instances while allowing for flexible data sources.
        """
        if isinstance(self.symbols, str):
            self.symbols = self.symbols.replace(",", " ").split()

        # Strategy pattern: Use extractor to fetch data
        extractor = MarketDataExtractor()
        self.data = extractor.fetch_price_series(
            symbols=self.symbols,
            start_date=self.start_date,
            end_date=self.end_date,
            source=self.source,
            interval=self.interval
        )

        # Observer pattern: Compute initial statistics
        self._compute_stats()

    def _compute_stats(self):
        """
        Compute comprehensive price statistics for all symbols.
        
        This method implements the Observer pattern by automatically updating
        statistics when called. It calculates key financial metrics including:
        - Mean Return: Average daily return
        - Volatility: Standard deviation of returns
        - Annualized Metrics: Both return and volatility
        
        Raises
        ------
        ValueError
            If the data structure doesn't match expected format
        """
        if self.data.empty:
            self.stats = {}
            return

        if not isinstance(self.data.columns, pd.MultiIndex):
            raise ValueError("Data must have a MultiIndex with (Price, Symbol) levels")

        try:
            close_prices = self.data.xs('Close', axis=1, level=0)
        except KeyError:
            self.stats = {}
            return

        returns = close_prices.pct_change(fill_method=None).dropna()

        means = returns.mean()
        stds = returns.std()

        self.stats = {
            symbol: {
                "mean_return": float(means[symbol]),
                "volatility": float(stds[symbol]),
                "annual_return": float((1 + means[symbol]) ** 252 - 1),
                "annual_volatility": float(stds[symbol] * np.sqrt(252)),
            }
            for symbol in returns.columns
        }

        self.stats = pd.DataFrame(self.stats)

    def get_market_value(self) -> pd.Series:
        """
        Retrieve most recent market prices for all tracked symbols.
        
        This method implements the Strategy pattern for accessing price data,
        handling multi-index data structures with error protection.

        Returns
        -------
        pd.Series
            Latest closing prices for each symbol, indexed by symbol name
        """
        if self.data.empty:
            return pd.Series(dtype=float)

        try:
            close_prices = self.data.xs('Close', axis=1, level=0)
            return close_prices.iloc[-1]
        except KeyError:
            return pd.Series(dtype=float)

    def get_returns(self) -> pd.DataFrame:
        """
        Calculate historical returns for all symbols.
        
        This method implements the Strategy pattern for return calculations,
        providing a consistent interface for accessing return data.
        
        The calculation handles:
        - Missing data through proper NA handling
        - Multi-index data structures
        - Period-over-period returns

        Returns
        -------
        pd.DataFrame
            Historical returns for each symbol, with dates as index
        """
        try:
            close_prices = self.data.xs('Close', axis=1, level=0)
            return close_prices.pct_change(fill_method=None).dropna()
        except KeyError:
            return pd.DataFrame()

    def describe(self) -> None:
        """
        Generate detailed statistical summary for all symbols.
        
        This method implements the Template Method pattern for consistent
        reporting across different types of financial instruments. It provides:
        - Return metrics in percentage format
        - Volatility measures with appropriate precision
        - Clear per-symbol breakdowns
        """
        print(f"\n=== Statistics for {self.name or 'Price Series'} ===")
        for symbol, stats in self.stats.items():
            print(f"\nStats for {symbol}:")
            for stat_name, value in stats.items():
                if 'return' in stat_name:
                    print(f"  {stat_name}: {value:.2%}")
                else:
                    print(f"  {stat_name}: {value:.4f}")
