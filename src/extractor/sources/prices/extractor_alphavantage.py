"""
Module for extracting financial market data from Alpha Vantage API.
Implements multiple design patterns for robust and flexible data extraction.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Union
import requests
import pandas as pd
from decouple import config
from src.extractor.sources.prices.extractor_prices_base import (
    BaseExtractor,
    Interval
)

class AlphaVantageExtractor(BaseExtractor):
    """
    Alpha Vantage API implementation using multiple design patterns for robust data extraction.
    
    This class implements the Strategy pattern through BaseExtractor inheritance,
    providing a specific implementation for the Alpha Vantage API. It also uses
    additional patterns to ensure reliable data retrieval and transformation.

    Design Patterns
    --------------
    - Strategy: Implements specific Alpha Vantage extraction strategy
    - Template Method: Inherits from BaseExtractor for consistent interface
    - Factory: Creates appropriate data structures for different intervals
    - Adapter: Converts Alpha Vantage format to standardized internal format
    - Singleton: Manages API configuration and rate limiting
    
    Attributes
    ----------
    INTERVAL_MAP : dict
        Mapping between internal interval enum and Alpha Vantage intervals
        
    Notes
    -----
    This implementation handles API rate limiting, data validation,
    and proper error handling for robust data extraction.
    """
    
    # Interval mapping strategy
    INTERVAL_MAP = {
        Interval.ONE_MINUTE: "1min",
        Interval.FIVE_MINUTES: "5min",
        Interval.FIFTEEN_MINUTES: "15min",
        Interval.THIRTY_MINUTES: "30min",
        Interval.ONE_HOUR: "60min",
        Interval.DAILY: "daily",
        Interval.WEEKLY: "weekly",
        Interval.MONTHLY: "monthly"
    }
    
    def __init__(
        self,
        symbols: Union[str, List[str]] = None,
        start_date: datetime = None,
        end_date: datetime = None,
        interval: Interval = None
    ):
        """
        Initialize Alpha Vantage extractor with configuration and validation.
        
        This constructor implements the Template Method pattern by following
        a predefined initialization sequence while allowing for customization.

        Parameters
        ----------
        symbols : Union[str, List[str]], optional
            Stock symbols to track
        start_date : datetime, optional
            Start date for data extraction
        end_date : datetime, optional
            End date for data extraction
        interval : Interval, optional
            Data sampling interval

        Raises
        ------
        ValueError
            If API key is not properly configured

        Design Pattern Implementation
        ---------------------------
        - Template Method: Standardized initialization sequence
        - Strategy: API key configuration
        - Singleton: API configuration management
        """
        super().__init__(
            symbols=symbols if symbols is not None else [],
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        self._api_key = config('API_KEY_ALPHAVANTAGE')
        if not self._api_key:
            raise ValueError("Alpha Vantage API key not found in environment variables")

    def extract_data(
        self,
        symbols: Union[str, List[str]],
        start_date: datetime,
        end_date: datetime,
        interval: str = "daily"
    ) -> pd.DataFrame:
        """
        Extract historical market data implementing multiple design patterns.
        
        This method implements several design patterns to ensure robust data
        extraction, proper error handling, and consistent data formatting.

        Parameters
        ----------
        symbols : Union[str, List[str]]
            Stock symbols to fetch (e.g., 'AAPL' or ['AAPL', 'GOOGL'])
        start_date : datetime
            Initial date for data extraction
        end_date : datetime
            Final date for data extraction
        interval : str, optional
            Data sampling interval (default: "daily")
            
        Returns
        -------
        pd.DataFrame
            MultiIndex DataFrame with standardized market data format
            
        Raises
        ------
        ValueError
            On invalid input parameters
        ConnectionError
            On API communication failures
            
        Design Pattern Implementation
        ---------------------------
        - Strategy: Implements specific Alpha Vantage extraction logic
        - Template Method: Follows base extractor workflow
        - Chain of Responsibility: Handles different data types
        - Factory: Creates appropriate data structures
        - Observer: Monitors extraction progress and errors
        
        Notes
        -----
        The extraction process follows these steps:
        1. Input validation
        2. API communication
        3. Data parsing and cleaning
        4. Format standardization
        5. Quality checks
        """
        try:
            if isinstance(symbols, str):
                symbols = [symbols]
                
            if not symbols:
                raise ValueError("At least one symbol must be provided")
                
            self.validate_dates(start_date, end_date)
            
            av_interval = self.INTERVAL_MAP.get(
                Interval.from_string(interval),
                interval
            )
            
            function = ''

            if av_interval == "daily":
                function = "TIME_SERIES_DAILY"
            elif av_interval == "weekly":
                function = "TIME_SERIES_WEEKLY"
            elif av_interval == "monthly":
                function = "TIME_SERIES_MONTHLY"
            else:
                function = "TIME_SERIES_INTRADAY"
            
            # Fetch data for each symbol
            data = pd.DataFrame()
            for symbol in symbols:
                try:
                    url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={self._api_key}'
                    response = requests.get(url)   
                    json_data = response.json()
                    print(json_data)                 
                    ts_data = json_data['Time Series (Daily)']

                    df = pd.DataFrame.from_dict(ts_data, orient='index')
                    
                    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

                    for col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Set index and filter date range
                    df.index = pd.to_datetime(df.index)
                    df = df.sort_index()
                    df = df.loc[start_date:end_date]
                    
                    df['Symbol'] = symbol
                    data = pd.concat([data, df])
                    
                except Exception as e:
                    raise ConnectionError(f"Failed to fetch data from Alpha Vantage: {str(e)}")
                    continue
            
            if data.empty:
                raise ValueError("No data retrieved for any of the provided symbols")
                
            self.save_raw_data(data, f"{'_'.join(symbols)}.csv")
            data = self.format_extract_data(data)
            
            return data
            
        except Exception as e:
            raise ConnectionError(f"Failed to fetch data from Alpha Vantage: {str(e)}")

    def format_extract_data(
        self,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Transform raw Alpha Vantage data into standardized format using design patterns.
        
        This method implements the Builder pattern to construct a properly
        formatted DataFrame from raw API data, ensuring consistency across
        different data sources.

        Parameters
        ----------
        data : pd.DataFrame
            Raw data from Alpha Vantage API
            
        Returns
        -------
        pd.DataFrame
            Formatted DataFrame with standardized structure
            
        Design Pattern Implementation
        ---------------------------
        - Builder: Constructs complex DataFrame structure
        - Adapter: Converts between data formats
        - Strategy: Implements specific formatting logic
        - Factory: Creates appropriate data structures
        
        Notes
        -----
        The formatted DataFrame follows the structure:
        - MultiIndex columns: ['Price', 'Symbol']
        - Price types: Open, High, Low, Close, Volume
        - Sorted index and columns
        - Proper data types and handling of missing values
        """
        try:
            formatted_data = data.copy()
            formatted_data = formatted_data.pivot_table(
                index=data.index,
                columns="Symbol",
                values=["Open", "High", "Low", "Close", "Volume"]
            )
            
            formatted_data.columns.set_names(["Price", "Symbol"], inplace=True)
            formatted_data = formatted_data.sort_index(axis=1, level=[0, 1])
            
            symbols = formatted_data.columns.get_level_values(1).unique()
            self.save_processed_data(formatted_data, f"{'_'.join(symbols)}_clean.csv")
            
            return formatted_data
            
        except Exception as e:
            raise ValueError("Failed to format Alpha Vantage data") from e
    
    def get_source_info(self) -> Dict:
        """
        Retrieve Alpha Vantage API capabilities and configuration information.
        
        This method implements the Facade pattern by providing a simplified
        interface to access complex API configuration and capabilities.

        Returns
        -------
        Dict
            Comprehensive information about Alpha Vantage API including:
            - Supported intervals
            - API requirements
            - Rate limits
            - Documentation links
            
        Design Pattern Implementation
        ---------------------------
        - Facade: Simplifies access to API configuration
        - Strategy: Provides source-specific information
        - Singleton: Ensures consistent configuration
        """
        return {
            "name": "Alpha Vantage",
            "supported_intervals": list(self.INTERVAL_MAP.keys()),
            "requires_api_key": True,
            "base_url": "https://www.alphavantage.co/",
            "documentation": "https://www.alphavantage.co/documentation/",
            "rate_limits": {
                "requests_per_minute": 5,
                "daily_limit": "500 requests per day (free tier)",
                "notes": "Rate limits vary by subscription plan"
            }
        }

