from typing import Dict, List, Union, Optional, Any
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
import pandas as pd

@dataclass
class TimeSeries:
    """
    Represents a generic financial time series.


    Responsibilities:
    - Hold a DataFrame with a time index and one or more series
    - Provide basic cleaning utilities
    - Store lightweight metadata


    Attributes:
    name: Human-friendly name of the series.
    data: A pandas DataFrame with a DatetimeIndex.
    start_date: Start date used to build/query the series.
    end_date: End date used to build/query the series.
    source: Identifier for the data source.
    clean_method: Default cleaning policy ('interpolate', 'ffill', 'bfill').
    metadata: Auto-populated metadata dictionary.
    """

    name: str
    data: pd.DataFrame = field(default_factory=pd.DataFrame)
    start_date: date = field(default_factory=lambda: date.today() - timedelta(days=30))
    end_date: date = field(default_factory=date.today)
    source: Optional[str] = 'yfinance'
    clean_method: Optional[str] = 'interpolate'
    metadata: Dict[str, Any] = field(default_factory=dict,init=False)

    def __post_init__(self):
        """Populate metadata after construction."""

        self.metadata["created_at"] = datetime.utcnow()
        self.metadata["source"] = self.source
        self.metadata["missing_ratio"] = self.data.isna().mean().mean()

    def clean(self):
        """
        Clean missing values according to :pyattr:`clean_method`.

        Returns:
        The same instance (allows method chaining).
        """

        if self.clean_method == 'interpolate':
            self.data = self.data.interpolate(method='time')
        elif self.clean_method == 'ffill':
            self.data = self.data.fillna(method='ffill')
        elif self.clean_method == 'bfill':
            self.data = self.data.fillna(method='bfill')

        return self
    
    def clean_outlier_return(self, limite=0.2, ohlc='Close'):
        """
        Mark extreme returns as NaN and re-clean the series.

        Args:
        limit: Maximum absolute return allowed for a single period.
        ohlc: Price field to inspect ("Open", "High", "Low", "Close").

        Returns:
        The cleaned DataFrame.
        """

        ohlc_options = ['Open', 'High', 'Low', 'Close']
    
        if ohlc not in ohlc_options:
            raise ValueError(f"O parâmetro deve ser uma das seguintes opções: {ohlc_options}")
        
        if not isinstance(self.data.columns, pd.MultiIndex) or self.data.columns.names != ['Price', 'Ticker']:
            raise ValueError("As colunas precisam ter MultiIndex com níveis ['Price', 'Ticker'].")

        for ticker in self.data.columns.levels[1]:
            if (ohlc, ticker) not in self.data.columns:
                continue

            ohlc_data = self.data[ohlc, ticker]
            returns = ohlc_data.pct_change()

            ohlc_data_clean = ohlc_data.copy()
            ohlc_data_clean[returns.abs() > limite] = np.nan

            self.data[(f'{ohlc}_Clean', ticker)] = ohlc_data_clean

        self.clean()
        self.data = self.data.sort_index(axis=1, level=[1, 0])

        return self.data
    
    def summary(self):
        """Print a brief summary of the series (rows, period, source)."""

        print(f"📈 Série: {self.name}")
        print(f"Período: {self.start_date} → {self.end_date}")
        print(f"Linhas: {len(self.data)}")
