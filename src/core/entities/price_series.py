from dataclasses import dataclass, field
from typing import Dict, List, Union
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
    PriceSeries represents price data for one or multiple symbols.


    On initialization it uses the extractor to fetch the price matrix and
    computes lightweight statistics.
    """
    
    symbols: Union[str, List[str]] = field(default_factory=list)
    stats: pd.DataFrame = field(default_factory=pd.DataFrame, init=False)
    source: DataSource = field(default_factory=DataSource.YAHOO)
    interval: Interval = field(default_factory=Interval.DAILY)
    
    def __post_init__(self):
        if isinstance(self.symbols, str):
            self.symbols = self.symbols.replace(",", " ").split()

        extractor = MarketDataExtractor()
        self.data = extractor.fetch_price_series(
            symbols=self.symbols,
            start_date=self.start_date,
            end_date=self.end_date,
            source=self.source,
            interval=self.interval
        )

        self._compute_stats()

    def _compute_stats(self):
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

    def get_market_value(self):
        """
        Return the most recent close price per ticker.
        Handles multi-index DataFrame with (Price, Symbol) hierarchy.
        
        Returns
        -------
        pd.Series
            Latest closing prices for each ticker
        """
        if self.data.empty:
            return pd.Series(dtype=float)

        try:
            # Usar xs para selecionar o nível 'Close' do primeiro nível do MultiIndex
            close_prices = self.data.xs('Close', axis=1, level=0)
            return close_prices.iloc[-1]
        except KeyError:
            return pd.Series(dtype=float)

    def get_returns(self):
        """
        Return daily returns for the Close price matrix.
        Handles multi-index DataFrame with (Price, Symbol) hierarchy.
        
        Returns
        -------
        pd.DataFrame
            Daily returns for each ticker based on closing prices
        """
        try:
            close_prices = self.data.xs('Close', axis=1, level=0)
            return close_prices.pct_change(fill_method=None).dropna()
        except KeyError:
            return pd.DataFrame()

    def describe(self):
        """
        Print basic stats computed for each ticker.
        Includes mean return, volatility, annual return and volatility.
        """
        print(f"\n=== Statistics for {self.name or 'Price Series'} ===")
        for symbol, stats in self.stats.items():
            print(f"\nStats for {symbol}:")
            for stat_name, value in stats.items():
                if 'return' in stat_name:
                    print(f"  {stat_name}: {value:.2%}")
                else:
                    print(f"  {stat_name}: {value:.4f}")
