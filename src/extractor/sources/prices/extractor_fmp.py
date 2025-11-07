"""
Financial Modeling Prep (FMP) API data extractor implementation.

This module implements the Strategy Pattern through the BaseExtractor interface,
providing a concrete strategy for fetching financial data from the FMP API.
It also follows the Template Method pattern by implementing the abstract methods
defined in the base class.

Design Patterns:
    - Strategy Pattern: Implements BaseExtractor interface to provide FMP-specific data extraction
    - Template Method: Inherits and implements abstract methods from BaseExtractor
    - Factory Method: Can be used as part of a factory to create different extractor instances
    - Singleton Pattern (optional): Can be implemented to ensure single API connection

Key Features:
    - Historical price data retrieval from FMP API
    - Support for multiple symbols
    - Customizable date ranges
    - Data format standardization
    - Error handling and validation
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Union
from urllib.request import urlopen
from io import StringIO
import certifi
import pandas as pd
from decouple import config

from src.extractor.sources.prices.extractor_prices_base import (
    BaseExtractor,
    Interval
)

class FMPExtractor(BaseExtractor):
    """
    Financial Modeling Prep (FMP) API specific implementation of the market data extractor.
    
    This class provides a concrete implementation of the BaseExtractor interface
    for retrieving financial data from the Financial Modeling Prep API. It handles
    authentication, data fetching, and format standardization.
    
    Design Pattern Implementation:
        - Strategy: Concrete strategy for FMP API data extraction
        - Template Method: Implements abstract methods from BaseExtractor
        
    Attributes:
        INTERVAL_MAP (dict): Maps standard intervals to FMP-specific formats
        _api_key (str): FMP API authentication key from environment variables
    """
    
    INTERVAL_MAP = {
        Interval.DAILY: "1day"
    }
    
    def __init__(
        self,
        symbols: Union[str, List[str]] = None,
        start_date: datetime = None,
        end_date: datetime = None,
        interval: Interval = None
    ):
        """
        Initialize FMP extractor with API configuration and settings.
        
        This constructor sets up the FMP extractor with the necessary configuration
        and validates the API key availability. It follows the Template Method pattern
        by calling the parent class initialization with standardized parameters.
        
        Parameters
        ----------
        symbols : Union[str, List[str]], optional
            Single symbol or list of symbols to track
        start_date : datetime, optional
            Start date for data retrieval period
        end_date : datetime, optional
            End date for data retrieval period
        interval : Interval, optional
            Data interval enumeration (e.g., DAILY)
            
        Raises
        ------
        ValueError
            If the FMP API key is not found in environment variables
        """
        super().__init__(
            symbols=symbols if symbols is not None else [],
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        
        self._api_key = config('API_KEY_FMP')

        if not self._api_key:
            raise ValueError("FMP API key not found in environment variables")

    def extract_data(
        self,
        symbols: Union[str, List[str]],
        start_date: date = date.today() - timedelta(days=30),
        end_date: date = date.today(),
        interval: str = "1day"
    ) -> pd.DataFrame:
        """
        Fetch historical price data from the FMP API for given symbols and date range.
        
        This method implements the Template Method pattern by providing the concrete
        implementation for data extraction from FMP API. It handles multiple symbols,
        performs data validation, and manages error scenarios.
        
        Design Pattern Implementation:
            - Template Method: Concrete implementation of abstract method
            - Strategy: FMP-specific data fetching strategy
            
        Process Flow:
            1. Validate input parameters
            2. Convert symbols to list format if needed
            3. Fetch data for each symbol from FMP API
            4. Combine and format the retrieved data
            5. Save raw data for audit purposes
            6. Format data into standardized structure
        
        Parameters
        ----------
        symbols : Union[str, List[str]]
            Single symbol or list of symbols to fetch (e.g., 'AAPL' or ['AAPL', 'MSFT'])
        start_date : datetime, default: 30 days ago
            Start date for historical data range
        end_date : datetime, default: today
            End date for historical data range
        interval : str, optional, default: "1day"
            Data interval, currently only supports daily data
            
        Returns
        -------
        pd.DataFrame
            Historical price data in standardized format with MultiIndex columns
            for price types (Open, High, Low, Close, Volume) and symbols
            
        Raises
        ------
        ValueError
            If symbols list is empty or dates are invalid
        ConnectionError
            If API request fails or data cannot be retrieved
        RuntimeError
            If retrieved data is empty or invalid
        """
        try:
            if isinstance(symbols, str):
                symbols = [symbols]
                
            if not symbols:
                raise ValueError("At least one symbol must be provided")
                
            self.validate_dates(start_date, end_date)

            # Fetch data for each symbol
            data = pd.DataFrame()
            for symbol in symbols:
                try:
                    start_date = start_date.strftime('%Y-%m-%d')
                    end_date = end_date.strftime('%Y-%m-%d')

                    url = (f"https://financialmodelingprep.com/stable/historical-price-eod/full?from={start_date}&to={end_date}&symbol={symbol}&apikey={self._api_key}")
                    response = urlopen(url, cafile=certifi.where())
                    json_data = response.read().decode("utf-8")
                    prices = pd.read_json(StringIO(json_data))
                    prices['symbol'] = symbol
                    data = pd.concat([data, prices], ignore_index=True)
                    
                except Exception as e:
                    raise ConnectionError(f"Failed to fetch data from FMP: {str(e)}")
            
            if data.empty:
                raise ValueError("No data retrieved for any of the provided symbols")

            self.save_raw_data(data, f"{'_'.join(symbols)}.csv")    
            data = self.format_extract_data(data)

            return data
            
        except Exception as e:
            raise ConnectionError(f"Failed to fetch data from FMP: {str(e)}")

    def format_extract_data(
        self,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Format raw FMP data into a standardized structure for analysis.
        
        This method implements part of the Template Method pattern by providing
        the concrete implementation for data formatting specific to FMP API data.
        It handles data cleaning, column renaming, and restructuring into a
        standardized format used across the application.
        
        Design Pattern Implementation:
            - Template Method: Concrete implementation for FMP-specific formatting
            - Strategy: Part of the FMP data handling strategy
            
        Transformation Steps:
            1. Rename columns to standard format
            2. Convert date strings to datetime objects
            3. Set date as index
            4. Remove unnecessary columns
            5. Pivot data for multi-symbol support
            6. Save processed data for audit purposes
        
        Parameters
        ----------
        data : pd.DataFrame
            Raw data from FMP API with original column names and structure
        
        Returns
        -------
        pd.DataFrame
            Clean, formatted data with standardized MultiIndex columns:
            - Level 0: Price type (Open, High, Low, Close, Volume)
            - Level 1: Symbol
            Index: DateTime
            
        Raises
        ------
        ValueError
            If data transformation fails or results in invalid format
        """
        try:
            data = data.rename(columns={
                "date": "Date",
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
                "symbol": "Symbol"
            })
            
            data['Date'] = pd.to_datetime(data['Date'])
            data.set_index('Date', inplace=True)
            
            cols_to_drop = ['change', 'changePercent', 'vwap', 'label', 'changeOverTime']
            data = data.drop([col for col in cols_to_drop if col in data.columns], axis=1)
            
            data = data.pivot_table(
                index=data.index,
                columns="Symbol",
                values=["Open", "High", "Low", "Close", "Volume"]
            )
            
            data.columns.set_names(["Price", "Symbol"], inplace=True)
            data = data.sort_index(axis=1, level=[0, 1])

            symbols = data.columns.get_level_values(1).unique()
            self.save_processed_data(data, f"{'_'.join(symbols)}_clean.csv")
            
            return data
            
        except Exception as e:
            raise ValueError("Failed to format FMP data") from e
    
    
    def get_source_info(self) -> Dict:
        """
        Retrieve FMP API source information and capabilities.
        
        This method implements the Template Method pattern by providing
        FMP-specific information about the data source. It includes details
        about supported features, API limitations, and documentation references.
        
        Design Pattern Implementation:
            - Template Method: Concrete implementation for FMP metadata
            - Strategy: Part of the FMP-specific implementation
            
        Returns
        -------
        Dict
            Comprehensive information about FMP API including:
            - Source name
            - Supported data intervals
            - API authentication requirements
            - Base URL and documentation links
            - Rate limiting information
            
        Example Output
        -------------
        {
            "name": "Financial Modeling Prep",
            "supported_intervals": ["DAILY"],
            "requires_api_key": True,
            "base_url": "https://financialmodelingprep.com/",
            "documentation": "https://site.financialmodelingprep.com/developer/docs",
            "rate_limits": {
                "requests_per_minute": 300,
                "daily_limit": "Depends on subscription plan"
            }
        }
        """
        return {
            "name": "Financial Modeling Prep",
            "supported_intervals": list(self.INTERVAL_MAP.keys()),
            "requires_api_key": True,
            "base_url": "https://financialmodelingprep.com/",
            "documentation": "https://site.financialmodelingprep.com/developer/docs",
            "rate_limits": {
                "requests_per_minute": 300,
                "daily_limit": "Depends on subscription plan"
            }
        }
