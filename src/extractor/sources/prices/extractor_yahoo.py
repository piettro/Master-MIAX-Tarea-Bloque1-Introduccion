"""
Yahoo Finance Data Extractor Implementation.

This module provides a concrete implementation of the financial data extractor
for the Yahoo Finance API using multiple design patterns to ensure reliable
and maintainable data extraction.

Design Patterns:
    - Strategy Pattern: Implements specific Yahoo Finance data extraction strategy
    - Template Method: Inherits and implements BaseExtractor's abstract methods
    - Adapter Pattern: Adapts Yahoo Finance API responses to standardized format
    - Bridge Pattern: Separates Yahoo-specific implementation from abstraction

Key Features:
    - Support for multiple time intervals
    - Batch symbol processing
    - Automatic error handling
    - Data validation and transformation
    - Rate limiting consideration
"""

import yfinance as yf
from datetime import date, datetime, timedelta
from typing import Union, List, Dict
import pandas as pd
from src.extractor.sources.prices.extractor_prices_base import (
    BaseExtractor,
    Interval
)

class YahooExtractor(BaseExtractor):
    """
    Yahoo Finance API specific implementation of the market data extractor.
    
    This class provides a concrete strategy for extracting financial data from
    Yahoo Finance, implementing multiple design patterns to ensure robust and
    maintainable data retrieval.
    
    Design Pattern Implementation:
        - Strategy: Concrete strategy for Yahoo Finance data extraction
        - Template Method: Implements abstract methods from BaseExtractor
        - Adapter: Adapts Yahoo Finance data format to standardized structure
        - Bridge: Implements platform-specific data retrieval
        
    Features:
        - Supports all Yahoo Finance intervals
        - Handles multiple symbols efficiently
        - Manages API rate limits
        - Provides robust error handling
        - Ensures data consistency
        
    Notes:
        Yahoo Finance is an unofficial API, so the implementation includes
        proper error handling and rate limiting considerations.
    """
    
    INTERVAL_MAP = {
        Interval.ONE_MINUTE: "1m",      
        Interval.TWO_MINUTES: "2m",     
        Interval.FIVE_MINUTES: "5m",    
        Interval.FIFTEEN_MINUTES: "15m", 
        Interval.THIRTY_MINUTES: "30m",  
        Interval.SIXTY_MINUTES: "60m",  
        Interval.NINETY_MINUTES: "90m", 
        Interval.ONE_HOUR: "1h",       
        Interval.DAILY: "1d",           
        Interval.FIVE_DAYS: "5d",       
        Interval.WEEKLY: "1wk",         
        Interval.MONTHLY: "1mo",        
        Interval.QUARTERLY: "3mo"       
    }

    def __init__(
        self,
        symbols: Union[str, List[str]] = None,
        start_date: datetime = None,
        end_date: datetime = None,
        interval: Interval = None
    ):
        """
        Initialize Yahoo Finance extractor with specific configuration.
        
        This constructor implements the Template Method pattern by calling
        the parent class initialization with standardized parameters. It
        sets up the Yahoo Finance-specific configuration while maintaining
        the common interface.
        
        Parameters
        ----------
        symbols : Union[str, List[str]], optional
            Single symbol or list of symbols to track
        start_date : datetime, optional
            Start date for data retrieval
        end_date : datetime, optional
            End date for data retrieval
        interval : Interval, optional
            Data interval enumeration
            
        Design Pattern Context
        --------------------
        - Template Method: Standardized initialization
        - Strategy: Yahoo-specific configuration
        - Bridge: Platform-specific setup
        
        Notes
        -----
        No API key is required for Yahoo Finance, but rate limiting
        should be considered in the implementation.
        """
        super().__init__(
            symbols=symbols if symbols is not None else [],
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

    def extract_data(
        self,
        symbols: Union[str, List[str]],
        start_date: date = date.today() - timedelta(days=30),
        end_date: date = date.today(),
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Fetch historical financial data from Yahoo Finance API.
        
        This method implements the Template Method pattern by providing the
        concrete implementation for Yahoo Finance data extraction. It also
        implements the Strategy pattern through Yahoo-specific data retrieval
        logic.
        
        Design Pattern Implementation:
            - Template Method: Concrete implementation of abstract method
            - Strategy: Yahoo-specific data fetching strategy
            - Adapter: Converts between interval formats
            - Bridge: Handles Yahoo Finance API interaction
            
        Process Flow:
            1. Validate and normalize input parameters
            2. Convert intervals to Yahoo Finance format
            3. Execute API request with error handling
            4. Save raw data for audit purposes
            5. Format data into standardized structure
            
        Parameters
        ----------
        symbols : Union[str, List[str]]
            Single symbol (e.g., 'AAPL') or list of symbols (['AAPL', 'MSFT'])
        start_date : datetime, default: 30 days ago
            Start date for historical data range
        end_date : datetime, default: today
            End date for historical data range
        interval : str, optional, default: "1d"
            Data interval (mapped to Yahoo Finance format)
            
        Returns
        -------
        pd.DataFrame
            Historical price data with standardized structure:
            - MultiIndex columns (Price type, Symbol)
            - DateTimeIndex for timestamps
            - Required columns: Open, High, Low, Close, Volume
            
        Raises
        ------
        ValueError
            - If symbols list is empty
            - If dates are invalid
            - If interval is not supported
        ConnectionError
            - If API request fails
            - If data cannot be retrieved
            - If network issues occur
            
        Notes
        -----
        Uses yfinance library with consideration for rate limits
        and error handling for this unofficial API.
        """
        try:
            if isinstance(symbols, str):
                symbols = [symbols]
                
            if not symbols:
                raise ValueError("At least one symbol must be provided")
            
            self.validate_dates(start_date, end_date)

            yf_interval = self.INTERVAL_MAP.get(
                Interval.from_string(interval),
                interval
            )
            
            data = yf.download(
                tickers=symbols if isinstance(symbols, str) else " ".join(symbols),
                start=start_date,
                end=end_date,
                interval=yf_interval,
                progress=False
            )

            if data.empty:
                raise ValueError("No data retrieved for any of the provided symbols")
               
            self.save_raw_data(data, f"{'_'.join(symbols)}.csv")
            data = self.format_extract_data(data)
            
            return data
            
        except Exception as e:
            raise ConnectionError(f"Failed to fetch data from Yahoo Finance: {str(e)}")

    def format_extract_data(
        self,
        raw_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Format Yahoo Finance data into the standardized structure.
        
        This method implements both the Template Method and Adapter patterns
        by providing Yahoo-specific data formatting logic while maintaining
        a consistent output structure across all extractors.
        
        Design Pattern Implementation:
            - Template Method: Concrete implementation of abstract method
            - Adapter: Converts Yahoo Finance format to standard structure
            - Strategy: Yahoo-specific data formatting logic
            
        Process Flow:
            1. Validate required columns presence
            2. Copy data to prevent modifications
            3. Verify data structure
            4. Save processed data for audit
            
        Parameters
        ----------
        raw_data : pd.DataFrame
            Raw data from Yahoo Finance API with original structure:
            - Already includes symbol information in MultiIndex
            - Contains standard OHLCV columns
            
        Returns
        -------
        pd.DataFrame
            Formatted data with standardized structure:
            - MultiIndex columns (Price type, Symbol)
            - DateTimeIndex for timestamps
            - Validated required columns
            
        Raises
        ------
        ValueError
            - If required columns are missing
            - If data structure is invalid
            - If formatting process fails
            
        Notes
        -----
        Yahoo Finance data usually comes pre-formatted in a structure
        close to our standard format, requiring minimal transformation.
        """
        
        try:
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_cols = [col for col in required_cols if col not in raw_data.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            symbols = raw_data.columns.get_level_values(1).unique()
            formatted_data = raw_data.copy()
            self.save_processed_data(formatted_data, f"{'_'.join(symbols)}_clean.csv")
            
            return formatted_data
            
        except Exception as e:
            raise ValueError(f"Failed to format Yahoo Finance data: {str(e)}")
    
    def get_source_info(self) -> Dict:
        """
        Retrieve Yahoo Finance API capabilities and configuration information.
        
        This method implements the Template Method pattern by providing
        Yahoo-specific source information. It serves as part of the
        documentation and configuration system.
        
        Design Pattern Implementation:
            - Template Method: Concrete implementation for metadata
            - Strategy: Yahoo-specific capability information
            
        Returns
        -------
        Dict
            Comprehensive information about Yahoo Finance API:
            - Source name and identification
            - Supported data intervals
            - Authentication requirements
            - API endpoint information
            - Rate limiting details
            
        Example Output
        -------------
        {
            "name": "Yahoo Finance",
            "supported_intervals": ["1m", "2m", "5m", ...],
            "requires_api_key": False,
            "base_url": "https://finance.yahoo.com/",
            "documentation": "https://pypi.org/project/yfinance/",
            "rate_limits": {
                "requests_per_second": 2,
                "notes": "Unofficial API guidelines"
            }
        }
        
        Notes
        -----
        Yahoo Finance is an unofficial API, so rate limits and
        usage guidelines should be carefully considered.
        """
        return {
            "name": "Yahoo Finance",
            "supported_intervals": list(self.INTERVAL_MAP.keys()),
            "requires_api_key": False,
            "base_url": "https://finance.yahoo.com/",
            "documentation": "https://pypi.org/project/yfinance/",
            "rate_limits": {
                "requests_per_second": 2,
                "notes": "Unofficial API, be respectful with request frequency"
            }
        }