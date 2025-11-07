"""
Base extractor class defining the interface for all financial data extractors.
Implements Template Method pattern for data extraction and processing pipeline.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
import pandas as pd
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Available data sources for price extraction"""
    YAHOO = "yfinance"
    EODHD = "eodhd"
    FMP = "fmp"
    ALPHA_VANTAGE = "alphavantage"

class Interval(Enum):
    """Supported time intervals for data extraction"""
    ONE_MINUTE = "1min"
    TWO_MINUTES = "2min"
    FIVE_MINUTES = "5min"
    FIFTEEN_MINUTES = "15min"
    THIRTY_MINUTES = "30min"
    SIXTY_MINUTES = "60min"
    NINETY_MINUTES = "90min"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    DAILY = "1d"
    FIVE_DAYS = "5d"
    WEEKLY = "1wk"
    MONTHLY = "1mo"
    QUARTERLY = "3mo"
    
    @classmethod
    def from_string(cls, interval: str) -> 'Interval':
        """
        Convert string to Interval enum.
        
        Parameters
        ----------
        interval : str
            Interval string to convert
            
        Returns
        -------
        Interval
            Corresponding Interval enum value
            
        Raises
        ------
        ValueError
            If interval is not supported
        """
        try:
            return cls(interval)
        except ValueError:
            valid_intervals = [i.value for i in cls]
            raise ValueError(
                f"Invalid interval: {interval}. "
                f"Supported intervals are: {', '.join(valid_intervals)}"
            )

class BaseExtractor(ABC):
    """
    Base financial data extractor implementing Template Method pattern.
    
    Attributes
    ----------
    REQUIRED_COLUMNS : List[str]
        Required columns for price data
    DEFAULT_INTERVAL : str
        Default time interval for data
    """
    
    REQUIRED_COLUMNS = ['Open', 'High', 'Low', 'Close', 'Volume']
    DEFAULT_INTERVAL = Interval.DAILY
    DEFAULT_SOURCE = DataSource.YAHOO
    
    def __init__(
            self,
            symbols:Union[str, List[str]],
            start_date:datetime = datetime.now() - timedelta(days=3650),
            end_date:datetime = datetime.now(),
            source:DataSource = DEFAULT_SOURCE,
            interval:Interval = DEFAULT_INTERVAL
        ):
        """Initialize the base extractor with common settings."""
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.source = source
        self.interval = interval
        self._setup_directories()
    
    def _setup_directories(self):
        """Set up data directories with source and date-specific folders"""
        # Base directory setup
        self.base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        
        # Main data directories
        self.raw_data_dir = self.base_dir / "data" / "raw"
        self.processed_data_dir = self.base_dir / "data" / "processed"
        
        # Ensure base directories exist
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up source-specific directories with current date
        if hasattr(self, 'source'):
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Raw data directory for current source and date
            self.current_raw_dir = self.raw_data_dir / self.source.value / today
            self.current_raw_dir.mkdir(parents=True, exist_ok=True)
            
            # Processed data directory for current source and date
            self.current_processed_dir = self.processed_data_dir / self.source.value / today
            self.current_processed_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def extract_data(
        self,
        symbol: Union[str, List[str]],
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Get historical price data for a single symbol.
        
        Parameters
        ----------
        symbol : str
            Ticker symbol to fetch data for
        start_date : datetime
            Start date for the data range
        end_date : datetime
            End date for the data range
        interval : str, optional
            Data interval ('1d', '1h', etc.), by default "1d"
        include_adj : bool, optional
            Whether to include adjusted prices, by default True
            
        Returns
        -------
        pd.DataFrame
            DataFrame with standardized price data including:
            - Date (index)
            - Open, High, Low, Close
            - Adjusted Close (if include_adj=True)
            - Volume
            
        Raises
        ------
        ValueError
            If invalid parameters are provided
        ConnectionError
            If data cannot be retrieved from source
        """
        pass

    @abstractmethod
    def format_extract_data(
        self,
        raw_data: pd.DataFrame,
        symbol: str
    ) -> pd.DataFrame:
        """
        Format raw historical price data into standardized DataFrame.
        
        Parameters
        ----------
        raw_data : Dict[str, any]
            Raw data from the data source
        symbol : str
            Symbol for the data being formatted
            
        Returns
        -------
        pd.DataFrame
            Standardized DataFrame with price data
            
        Raises
        ------
        ValueError
            If raw data is invalid or missing required fields
        """
        pass
        
    def validate_dates(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> None:
        """
        Validate date parameters for data extraction.
        
        Parameters
        ----------
        start_date : datetime
            Start date to validate
        end_date : datetime
            End date to validate
            
        Raises
        ------
        ValueError
            If dates are invalid or in wrong order
        """
       
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValueError("start_date and end_date must be datetime objects")
        
        if start_date > end_date:
            raise ValueError("start_date must be before end_date")
            
        if end_date > datetime.now():
            raise ValueError("end_date cannot be in the future")
    
    def save_raw_data(self, data: pd.DataFrame, filename: str) -> None:
        """
        Save raw data to CSV file in source and date-specific directory.
        
        Parameters
        ----------
        data : pd.DataFrame
            Data to save
        filename : str
            Name of the file to save
            
        Raises
        ------
        ValueError
            If saving fails
        """
        try:
            if not hasattr(self, 'current_raw_dir'):
                self._setup_directories()
            
            file_path = self.current_raw_dir / filename
            
            print(f"Saving raw data to {file_path}")
            data.to_csv(file_path)
            
        except Exception as e:
            raise ValueError(f"Failed to save raw data to {filename}: {str(e)}") from e
        
    def save_processed_data(self, data: pd.DataFrame, filename: str) -> None:
        """
        Save processed data to CSV file in source and date-specific directory.
        
        Parameters
        ----------
        data : pd.DataFrame
            Data to save
        filename : str
            Name of the file to save
            
        Raises
        ------
        ValueError
            If saving fails
        """
        try:
            if not hasattr(self, 'current_processed_dir'):
                self._setup_directories()
            
            file_path = self.current_processed_dir / filename
            
            data.to_csv(file_path)
            
        except Exception as e:
            raise ValueError(f"Failed to save processed data to {filename}: {str(e)}") from e
        