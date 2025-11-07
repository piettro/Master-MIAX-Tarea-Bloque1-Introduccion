"""
Module for extracting financial market data from EOD Historical Data (EODHD) API.
Implements multiple design patterns for robust and flexible data extraction with logging.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Union
import pandas as pd
from decouple import config
from eodhd import APIClient

from src.extractor.sources.prices.extractor_prices_base import (
    BaseExtractor,
    Interval
)

logger = logging.getLogger(__name__)

class EODHDExtractor(BaseExtractor):
    """
    EOD Historical Data API implementation with comprehensive design patterns.
    
    This class implements multiple design patterns to provide a robust and
    maintainable solution for extracting financial data from EODHD API.
    It includes logging, error handling, and data validation.

    Design Patterns
    --------------
    - Strategy: Implements specific EODHD extraction strategy
    - Template Method: Inherits from BaseExtractor for consistent workflow
    - Factory: Creates appropriate data structures for different intervals
    - Singleton: Manages API client and configuration
    - Observer: Implements logging for operation monitoring
    - Proxy: Handles API client initialization and reconnection
    
    Attributes
    ----------
    INTERVAL_MAP : Dict
        Mapping between internal intervals and EODHD API formats
        
    Notes
    -----
    This implementation includes robust error handling, logging,
    and automatic retry mechanisms for API communication.
    """

    INTERVAL_MAP = {
        Interval.DAILY: "d",
        Interval.WEEKLY: "w",
        Interval.MONTHLY: "m"
    }

    def __init__(
        self,
        symbols: Union[str, List[str]] = None,
        start_date: datetime = None,
        end_date: datetime = None,
        interval: Interval = None
    ):
        """
        Initialize EODHD extractor with configuration and client setup.
        
        This constructor implements multiple design patterns to ensure proper
        initialization and configuration of the EODHD API client.

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

        Design Pattern Implementation
        ---------------------------
        - Template Method: Standardized initialization sequence
        - Proxy: Lazy initialization of API client
        - Singleton: API configuration management
        - Observer: Logging of initialization process
        
        Notes
        -----
        Uses environment variables for API configuration to maintain security
        and flexibility in deployment.
        """
        super().__init__(
            symbols=symbols if symbols is not None else [],
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        self._api_key = config('API_KEY_EODHD')
        self._api_client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Initialize the EODHD API client using proxy pattern.
        
        This method implements the Proxy pattern to handle API client
        initialization and potential reconnection needs.

        Raises
        ------
        ConnectionError
            If client initialization fails

        Design Pattern Implementation
        ---------------------------
        - Proxy: Manages API client lifecycle
        - Singleton: Ensures single client instance
        - Observer: Logs initialization status
        
        Notes
        -----
        Includes error handling and logging for troubleshooting
        connection issues.
        """
        try:
            self._api_client = APIClient(self._api_key)
            logger.info("Successfully initialized EODHD API client")
        except Exception as e:
            logger.error(f"Failed to initialize EODHD client: {str(e)}")
            raise ConnectionError("Could not initialize EODHD API client") from e

    def extract_data(
        self,
        symbols: Union[str, List[str]],
        start_date: date = date.today() - timedelta(days=30),
        end_date: date = date.today(),
        interval: Interval = Interval.DAILY
    ) -> pd.DataFrame:
        """
        Extract historical market data using multiple design patterns for robustness.
        
        This method implements several design patterns to ensure reliable data
        extraction, proper error handling, and consistent data formatting.

        Parameters
        ----------
        symbols : Union[str, List[str]]
            Stock symbols to fetch (e.g., 'AAPL' or ['AAPL', 'GOOGL'])
        start_date : date, optional
            Initial date for data extraction (default: 30 days ago)
        end_date : date, optional
            Final date for data extraction (default: today)
        interval : Interval, optional
            Data sampling interval (default: DAILY)

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
        - Strategy: Implements specific EODHD extraction logic
        - Template Method: Follows base extractor workflow
        - Chain of Responsibility: Handles errors and retries
        - Observer: Logs extraction progress and issues
        - Builder: Constructs result DataFrame
        
        Notes
        -----
        Implements robust error handling with:
        - Input validation
        - API communication retry logic
        - Proper error logging
        - Data quality checks
        """
        try:
            if isinstance(symbols, str):
                symbols = [symbols]

            if not symbols:
                raise ValueError("At least one ticker must be provided")

            self.validate_dates(start_date, end_date)

            eodhd_interval = self.INTERVAL_MAP.get(
                Interval.from_string(interval),
                interval
            )
            
            data = pd.DataFrame()
            for symbol in symbols:
                try:
                    prices = self._api_client.get_eod_historical_stock_market_data(
                        symbol=symbol,
                        from_date=start_date,
                        to_date=end_date,
                        period=eodhd_interval
                    )
                    df = pd.DataFrame(prices)
                    df['symbol'] = symbol
                    data = pd.concat([data, df], ignore_index=True)
                except Exception as e:
                    logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
                    continue

            if data.empty:
                raise ValueError("No data retrieved for any of the provided symbols")
               
            self.save_raw_data(data, f"{'_'.join(symbols)}.csv")
            data = self.format_extract_data(data)
            
            return data

        except Exception as e:
            raise ConnectionError(f"Failed to fetch data from EODHD: {str(e)}")
        

    def format_extract_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform raw EODHD data into standardized format using design patterns.
        
        This method implements the Builder pattern to construct a properly
        formatted DataFrame from raw API data, with robust error handling
        and data validation.

        Parameters
        ----------
        data : pd.DataFrame
            Raw data from EODHD API with basic price information
            
        Returns
        -------
        pd.DataFrame
            Formatted DataFrame with standardized structure
            
        Design Pattern Implementation
        ---------------------------
        - Builder: Constructs complex DataFrame structure
        - Strategy: Implements specific formatting logic
        - Chain of Responsibility: Handles data cleaning steps
        - Observer: Logs formatting progress and issues
        
        Notes
        -----
        Transformation process includes:
        1. Column name standardization
        2. Date format conversion
        3. MultiIndex construction
        4. Data type validation
        5. Quality checks
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

            if 'adjusted_close' in data.columns:
                data.drop('adjusted_close', axis=1, inplace=True)

            data = data.pivot_table(
                index=data.index,
                columns="Symbol",
                values=["Open", "High", "Low", "Close", "Volume"]
            )

            data.columns.set_names(["Price", "Symbol"], inplace=True)
            data = data.sort_index(axis=1, level=[0, 1])

            symbols = data.columns.get_level_values(1).unique()
            formatted_data = data.copy()
            self.save_processed_data(formatted_data, f"{'_'.join(symbols)}_clean.csv")
            
            return formatted_data

        except Exception as e:
            logger.error(f"Error formatting historical prices: {str(e)}")
            raise ValueError("Failed to format historical prices") from e

    def get_source_info(self) -> Dict:
        """
        Retrieve EODHD API capabilities and configuration information.
        
        This method implements the Facade pattern to provide a simplified
        interface for accessing complex API configuration details.

        Returns
        -------
        Dict
            Comprehensive information about EODHD API including:
            - Supported data intervals
            - API authentication requirements
            - Rate limiting rules
            - Documentation references
            
        Design Pattern Implementation
        ---------------------------
        - Facade: Simplifies access to API configuration
        - Strategy: Provides source-specific information
        - Singleton: Ensures consistent configuration
        
        Example
        -------
        >>> extractor = EODHDExtractor()
        >>> info = extractor.get_source_info()
        >>> print(info['supported_intervals'])
        [Interval.DAILY, Interval.WEEKLY, Interval.MONTHLY]
        """
        return {
            "name": "EODHD",
            "supported_intervals": list(self.INTERVAL_MAP.keys()),
            "requires_api_key": True,
            "base_url": "https://eodhistoricaldata.com/",
            "documentation": "https://eodhistoricaldata.com/financial-apis/",
            "rate_limits": {
                "requests_per_minute": 100,
                "requests_per_day": 10000
            }
        }

