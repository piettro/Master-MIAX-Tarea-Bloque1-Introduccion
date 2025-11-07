"""
Module for portfolio management and analysis implementing various design patterns.
This module provides a robust framework for creating and managing investment portfolios.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Union
from datetime import date, timedelta
from src.core.entities.price_series import PriceSeries
from src.extractor.sources.prices.extractor_prices_base import (
    Interval,
    DataSource
)

@dataclass
class Portfolio:
    """
    A high-level portfolio entity implementing multiple design patterns for robust portfolio management.
    
    This class serves as a Facade for portfolio operations, implementing both the Facade and
    Strategy patterns to coordinate analysis modules and delegate computations efficiently.

    Design Patterns
    --------------
    - Facade Pattern: Provides a simplified interface to the complex subsystem of portfolio analysis
    - Strategy Pattern: Uses different strategies for price data extraction and analysis
    - Observer Pattern: Automatically updates portfolio metrics when holdings change
    - Delegate Pattern: Delegates complex calculations to specialized analysis modules

    Attributes
    ----------
    name : str
        Unique identifier for the portfolio
    quantity : Union[float, List[float]]
        Quantity of each holding (single float for uniform quantities)
    holdings : Union[str, List[str]]
        List of asset symbols in the portfolio
    start_date : date
        Beginning of the analysis period (default: 30 days ago)
    end_date : date
        End of the analysis period (default: today)
    source : DataSource
        Data source strategy for price information
    interval : Interval
        Time interval for price data

    Internal Attributes
    -----------------
    series : PriceSeries
        Price data container implementing the Strategy pattern
    positions : Dict[str, float]
        Mapping of holdings to their quantities
    """

    name: str
    quantity: Union[float, List[float]]
    holdings: Union[str, List[str]] = field(default_factory=list)
    start_date: date = field(default_factory=lambda: date.today() - timedelta(days=30))
    end_date: date = field(default_factory=date.today)
    source: DataSource = field(default_factory=DataSource.YAHOO)
    interval: Interval = field(default_factory=Interval.DAILY)

    # Internal state implementing Observer pattern
    series: PriceSeries = field(default_factory=dict, init=False)
    positions: Dict[str, float] = field(init=False)

    def __post_init__(self):
        """
        Initialize portfolio state and validate inputs.
        
        This method implements the Template Method pattern by:
        1. Normalizing input parameters
        2. Validating portfolio configuration
        3. Setting up price data strategy
        4. Initializing position tracking
        
        Raises
        ------
        ValueError
            If the number of quantities doesn't match the number of holdings
        """

        if isinstance(self.holdings, str):
            holdings = [self.holdings]
        else:
            holdings = list(self.holdings)
        
        if isinstance(self.quantity, (int, float)):
            quantities = [float(self.quantity)] * len(holdings)
        else:
            quantities = [float(q) for q in self.quantity]
        
        if len(quantities) != len(holdings):
            raise ValueError("Number of quantities must match number of holdings.")

        if any(q < 0 for q in quantities):
            raise ValueError("Quantities must be non-negative.")

        self.positions = dict(zip(holdings, quantities))
        
        self.series = PriceSeries(
            name=self.name,
            symbols=holdings,
            start_date=self.start_date,
            end_date=self.end_date,
            source=self.source,
            interval=self.interval
        )

    def get_prices(self) -> pd.DataFrame:
        """
        Retrieve historical price data for all holdings.
        
        This method implements the Facade pattern by providing a simple
        interface to access the underlying price data structure.

        Returns
        -------
        pd.DataFrame
            Historical price data with dates as index and holdings as columns
        """
        return self.series.data

    def weights(self) -> Dict[str, float]:
        """
        Calculate current portfolio weights based on position sizes.
        
        This method implements the Strategy pattern for weight calculation,
        handling edge cases such as zero total value.

        Returns
        -------
        Dict[str, float]
            Mapping of holdings to their weights in the portfolio
        """
        quantities = list(self.positions.values())
        total = sum(quantities)
        
        if total == 0:
            return {k: 0.0 for k in self.positions.keys()}
        return {k: q / total for k, q in self.positions.items()}
    
    def total_value_per_holding(self) -> pd.Series:
        """
        Calculate current market value for each holding.
        
        This method implements the Observer pattern by automatically
        updating values based on the latest market prices.

        Returns
        -------
        pd.Series
            Market values indexed by holding symbols
        """
        latest = self.series.get_market_value()
        qty = pd.Series(self.positions)

        return latest.mul(qty)

    def total_value(self) -> float:
        """
        Calculate total portfolio market value.
        
        This method implements the Facade pattern by providing a simple
        interface to access the total portfolio value.

        Returns
        -------
        float
            Total portfolio market value
        """
        return float(self.total_value_per_holding().sum())
    
    def total_value_initial(self) -> float:
        """
        Calculate initial portfolio market value.

        This method implements the Facade pattern by providing a simple
        interface to access the initial portfolio value.

        Returns
        -------
        float
            Initial portfolio market value
        """
        initial = self.series.get_initial_prices()
        qty = pd.Series(self.positions)

        return float(initial.mul(qty).sum())

    def returns(self) -> pd.DataFrame:
        """
        Calculate historical returns for the portfolio.
        
        This method implements the Strategy pattern by delegating
        return calculations to the price series component.

        Returns
        -------
        pd.DataFrame
            Historical returns data for all holdings
        """
        return self.series.get_returns()
    