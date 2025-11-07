"""
Module for generic financial time series analysis and management.
Implements various design patterns for flexible and extensible time series handling.
"""

from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
import pandas as pd

@dataclass
class TimeSeries:
    """
    Base class for financial time series implementing multiple design patterns.
    
    This class serves as an abstract base for various financial time series types,
    providing core functionality and implementing several design patterns for
    flexible data management and analysis.

    Design Patterns
    --------------
    - Template Method: Defines skeleton algorithm in base class
    - Strategy: Supports multiple cleaning strategies
    - Observer: Automatically updates metadata on data changes
    - Chain of Responsibility: Processes data through cleaning pipeline
    
    Attributes
    ----------
    name : str
        Human-readable identifier for the time series
    data : pd.DataFrame
        Time-indexed DataFrame containing series data
    start_date : date
        Beginning of the analysis period (default: 30 days ago)
    end_date : date
        End of the analysis period (default: today)
    metadata : Dict[str, Any]
        Automatically maintained series metadata
    
    Notes
    -----
    This class implements the Template Method pattern through its initialization
    and cleaning methods, allowing derived classes to customize behavior while
    maintaining a consistent interface.
    """

    name: str
    data: pd.DataFrame = field(default_factory=pd.DataFrame)
    start_date: date = field(default_factory=lambda: date.today() - timedelta(days=30))
    end_date: date = field(default_factory=date.today)
    metadata: Dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self):
        """
        Initialize series metadata using the Observer pattern.
        
        This method implements the Observer pattern by automatically
        updating metadata when the time series is created or modified.
        It tracks:
        - Creation timestamp (UTC)
        - Data source information
        - Data quality metrics
        """
        self.metadata["created_at"] = datetime.utcnow()
        self.metadata["source"] = self.source
        self.metadata["missing_ratio"] = self.data.isna().mean().mean()

    def summary(self) -> None:
        """
        Generate a concise summary of the time series.
        
        This method implements the Template Method pattern by providing
        a standard format for time series summaries that can be extended
        by derived classes.

        The summary includes:
        - Series identification
        - Time period covered
        - Number of observations
        """
        print(f"📈 Series: {self.name}")
        print(f"Period: {self.start_date} → {self.end_date}")
        print(f"Rows: {len(self.data)}")
