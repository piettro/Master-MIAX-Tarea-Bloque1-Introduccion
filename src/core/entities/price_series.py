from dataclasses import dataclass, field
from typing import Dict, List, Union
from src.core.entities.time_series import TimeSeries
from src.extractor.prices_extractor import APIExtractor
import pandas as pd
import numpy as np

@dataclass
class PriceSeries(TimeSeries):
    """
    PriceSeries represents price data for one or multiple tickers.


    On initialization it uses the extractor to fetch the price matrix and
    computes lightweight statistics.
    """
    
    tickers: Union[str, List[str]] = field(default_factory=list)
    stats: Dict[str, float] = field(default_factory=dict, init=False)

    def __post_init__(self):
        if isinstance(self.tickers, str):
            self.tickers = self.tickers.replace(",", " ").split()

        extractor = APIExtractor()
        self.data = extractor.fetch_price_series(
            tickers=self.tickers,
            source=self.source,
            start_date=self.start_date,
            end_date=self.end_date
        )

        self._compute_stats()

    def _compute_stats(self):
        """Compute per-ticker mean return and volatility from Close prices."""

        if self.data.empty or "Close" not in self.data:
            self.stats = {}

        close = self.data["Close"]
        # Especifica fill_method=None para evitar o aviso de depreciação
        returns = close.pct_change(fill_method=None).dropna()

        means = returns.mean()
        stds = returns.std()

        self.stats = {
            ticker: {
                "mean_return": float(means[ticker]),
                "volatility": float(stds[ticker]),
                "annual_return": float((1 + means[ticker]) ** 252 - 1),
                "annual_volatility": float(stds[ticker] * np.sqrt(252)),
            }
            for ticker in returns.columns
        }

    def get_market_value(self):
        """Return the most recent close price per ticker."""
        if self.data.empty:
            return pd.Series(dtype=float)

        return self.data["Close"].iloc[-1]

    def get_returns(self):
        """Return daily returns for the Close price matrix."""
        return self.data["Close"].pct_change(fill_method=None).dropna()

    def describe(self):
        """Print basic stats computed for each ticker."""

        print(f"=== Statistics for {self.name} ===")
        for k, v in self.stats.items():
            print(f"{k}: {v:.4f}")
