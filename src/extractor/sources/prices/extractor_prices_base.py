"""
Base extractor class defining the interface for all data extractors.
Provides common functionality and standardized methods for data extraction,
validation, and transformation across different data sources.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Union
import logging
from pathlib import Path
import pandas as pd
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

class BaseExtractor(ABC):
    def __init__(self, cache_data: bool = True):
        """
        Initialize the base extractor with common settings.
        """
        # Set up directory structure
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.raw_data_dir = self.base_dir / "src" / "data" / "raw"
        self.processed_data_dir = self.base_dir / "src" / "data" / "processed"
        
        # Create directories if they don't exist
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def get_historical_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
        include_adj: bool = True
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
    def format_historical_prices(
        self,
        raw_data: Dict[str, any],
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
    
    def clean_price_data(
        self,
        df: pd.DataFrame,
        symbol: str,
        fill_method: str = 'ffill'
    ) -> pd.DataFrame:
        """
        Clean and validate price data.
        
        Parameters
        ----------
        df : pd.DataFrame
            Raw price data to clean
        symbol : str
            Symbol for the data being cleaned
        fill_method : str, optional
            Method for filling missing values, by default 'ffill'
            
        Returns
        -------
        pd.DataFrame
            Cleaned price data
            
        Raises
        ------
        ValueError
            If data validation fails
        """
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
            
        # Ensure required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            raise ValueError(f"Missing required columns for {symbol}: {missing_cols}")
            
        # Sort by date
        df = df.sort_index()
        
        # Remove duplicates
        df = df[~df.index.duplicated(keep='first')]
        
        # Handle missing values
        df = df.fillna(method=fill_method)
        
        # Validate price relationships
        invalid_prices = (
            (df['High'] < df['Low']) |
            (df['Close'] < df['Low']) |
            (df['Close'] > df['High']) |
            (df['Open'] < df['Low']) |
            (df['Open'] > df['High'])
        )
        if invalid_prices.any():
            logger.warning(f"Found {invalid_prices.sum()} invalid price relationships for {symbol}")
            df = df[~invalid_prices]
        
        # Convert volume to int
        df['Volume'] = df['Volume'].fillna(0).astype(int)
        
        # Add metadata
        df['Symbol'] = symbol
        
        return df
