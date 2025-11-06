import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Union, Optional
from datetime import date, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from src.core.entities.price_series import PriceSeries

@dataclass
class Portfolio:
    """
    High-level portfolio entity that coordinates analysis modules.
    Responsibilities:
    - Hold position sizes
    - Provide thin helpers to compute portfolio-level metrics
    - Delegate heavy computations to modules under `analysis/`
    """

    name: str
    quantity: Union[float, List[float]]
    holdings:Union[str, List[str]]  = field(default_factory=list)
    start_date: date = field(default_factory=lambda: date.today() - timedelta(days=30))
    end_date: date = field(default_factory=date.today)
    source: Optional[str] = 'yfinance'

    #internal attributes
    series:PriceSeries = field(default_factory=dict,init=False)
    positions: Dict[str, float] = field(init=False)

    def __post_init__(self):
        # normalize holdings
        if isinstance(self.holdings, str):
            holdings = [self.holdings]
        else:
            holdings = list(self.holdings)
        
        # normalize quantities
        if isinstance(self.quantity, (int, float)):
            quantities = [float(self.quantity)] * len(holdings)
        else:
            quantities = [float(q) for q in self.quantity]
        
        if len(quantities) != len(holdings):
            raise ValueError("Number of quantities must match number of holdings.")
        
        self.positions = dict(zip(holdings, quantities))
        
        # build a price series for the holdings (delegation)
        self.series = PriceSeries(
            name=self.name,
            tickers=holdings,
            start_date=self.start_date,
            end_date=self.end_date,
            source=self.source,
        )

    def weights(self) -> Dict[str, float]:
        """Return portfolio weights implied by the provided position sizes."""
        quantities = list(self.positions.values())
        total = sum(quantities)
        
        if total == 0:
            return {k: 0.0 for k in self.positions.keys()}
        return {k: q / total for k, q in self.positions.items()}
    
    def total_value_per_holding(self) -> float:
        """Compute the current market value per holding using latest prices."""
        latest = self.series.get_market_value()
        qty = pd.Series(self.positions)

        return latest.mul(qty)

    def total_value(self) -> float:
        """Return the portfolio total market value (float)."""
        return float(self.total_value_per_holding().sum())
    
    def returns(self) -> pd.Series:
        """Return the historical returns DataFrame (Close returns)."""
        return self.series.get_returns()
    