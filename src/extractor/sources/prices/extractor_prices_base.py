"""
Base Financial Data Extractor Framework.

This module implements a robust framework for extracting financial data from various sources
using multiple design patterns to ensure flexibility, maintainability, and extensibility.

Design Patterns:
    - Template Method: Defines the skeleton of the data extraction algorithm in BaseExtractor
    - Strategy: Each concrete extractor provides a specific implementation strategy
    - Factory: Can be used to create specific extractors based on data source
    - Abstract Factory: Supports creating families of related extractors
    - Bridge: Separates abstraction (data extraction) from implementation (specific APIs)

Key Features:
    - Standardized interface for all data extractors
    - Configurable data sources and intervals
    - Automated directory management for data storage
    - Comprehensive error handling and validation
    - Flexible data formatting and processing pipeline

Module Structure:
    - DataSource: Enumeration of supported data sources
    - Interval: Enumeration of supported time intervals
    - BaseExtractor: Abstract base class for all extractors
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
import pandas as pd
from pathlib import Path

# Configure logging for data extraction operations
logger = logging.getLogger(__name__)

class DataSource(Enum):
    """
    Enumeration of supported financial data sources.
    
    This enum serves as a registry of available data sources and their corresponding
    identifiers, supporting the Strategy pattern by allowing dynamic source selection.
    
    Attributes:
        YAHOO: Yahoo Finance API source
        EODHD: End of Day Historical Data API source
        FMP: Financial Modeling Prep API source
        ALPHA_VANTAGE: Alpha Vantage API source
    """
    YAHOO = "yfinance"
    EODHD = "eodhd"
    FMP = "fmp"
    ALPHA_VANTAGE = "alphavantage"

class Interval(Enum):
    """
    Enumeration of supported time intervals for financial data extraction.
    
    This enum implements part of the Strategy pattern by providing standardized
    interval options that can be mapped to source-specific interval formats.
    It ensures consistent interval handling across different data sources.
    
    Attributes:
        ONE_MINUTE: 1-minute interval data
        TWO_MINUTES: 2-minute interval data
        FIVE_MINUTES: 5-minute interval data
        FIFTEEN_MINUTES: 15-minute interval data
        THIRTY_MINUTES: 30-minute interval data
        SIXTY_MINUTES: 1-hour interval data
        NINETY_MINUTES: 90-minute interval data
        ONE_HOUR: 1-hour interval data (alternative format)
        FOUR_HOURS: 4-hour interval data
        DAILY: Daily interval data
        FIVE_DAYS: 5-day interval data
        WEEKLY: Weekly interval data
        MONTHLY: Monthly interval data
        QUARTERLY: Quarterly interval data
    
    Note:
        Not all intervals may be supported by every data source.
        Concrete extractors should map these standard intervals to
        their source-specific formats.
    """
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
    Abstract base class for financial data extractors implementing multiple design patterns.
    
    This class serves as the foundation for all financial data extractors, implementing
    several design patterns to provide a flexible and extensible framework:
    
    Design Patterns:
        - Template Method: Defines the skeleton algorithm in extract_data and format_extract_data
        - Strategy: Allows different extraction strategies through concrete implementations
        - Bridge: Separates extraction interface from source-specific implementations
        - Factory: Can be created by a factory based on DataSource enum
    
    The class provides:
        1. Standard interface for data extraction
        2. Common validation methods
        3. File management functionality
        4. Error handling framework
        
    Attributes
    ----------
    REQUIRED_COLUMNS : List[str]
        Standard columns that must be present in extracted data
    DEFAULT_INTERVAL : Interval
        Default time interval for data extraction
    DEFAULT_SOURCE : DataSource
        Default data source if none specified
        
    Template Methods
    ---------------
    - extract_data: Main algorithm for data extraction
    - format_extract_data: Data standardization process
    - validate_dates: Date validation logic
    
    Hook Methods (can be overridden)
    ------------------------------
    - save_raw_data: Raw data persistence
    - save_processed_data: Processed data storage
    
    Notes
    -----
    Concrete implementations must provide:
    1. Source-specific data extraction logic
    2. Custom data formatting as needed
    3. Error handling for API-specific issues
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
        """
        Initialize the base extractor with common configuration settings.
        
        This constructor implements part of the Template Method pattern by
        setting up the basic configuration that all concrete extractors will use.
        It also initializes the file system structure for data storage.
        
        Parameters
        ----------
        symbols : Union[str, List[str]]
            Single symbol or list of symbols to extract data for
        start_date : datetime, optional
            Start date for data extraction, defaults to 10 years ago
        end_date : datetime, optional
            End date for data extraction, defaults to current date
        source : DataSource, optional
            Data source to use, defaults to DEFAULT_SOURCE
        interval : Interval, optional
            Time interval for data, defaults to DEFAULT_INTERVAL
            
        Design Pattern Context
        ---------------------
        - Template Method: Provides basic initialization logic
        - Strategy: Configures specific extraction strategy
        - Bridge: Sets up abstraction parameters
        
        Notes
        -----
        - Automatically creates required directory structure
        - Validates basic parameters
        - Sets up logging configuration
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.source = source
        self.interval = interval
        self._setup_directories()
    
    def _setup_directories(self):
        """
        Set up the directory structure for data storage.
        
        This helper method implements part of the Template Method pattern by providing
        a standard directory structure for all extractors. It creates and manages:
        1. Base directory structure
        2. Raw data storage
        3. Processed data storage
        4. Source-specific subdirectories
        5. Date-based organization
        
        Directory Structure:
        project_root/
        ├── data/
        │   ├── raw/
        │   │   └── {source}/
        │   │       └── {date}/
        │   └── processed/
        │       └── {source}/
        │           └── {date}/
        
        Notes
        -----
        - Creates directories if they don't exist
        - Organizes by data source and date
        - Maintains separation of raw and processed data
        - Handles path resolution automatically
        """
        self.base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        
        self.raw_data_dir = self.base_dir / "data" / "raw"
        self.processed_data_dir = self.base_dir / "data" / "processed"
        
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        if hasattr(self, 'source'):
            today = datetime.now().strftime('%Y-%m-%d')
            
            self.current_raw_dir = self.raw_data_dir / self.source.value / today
            self.current_raw_dir.mkdir(parents=True, exist_ok=True)
            
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
        Validate date parameters for data extraction requests.
        
        This method is part of the Template Method pattern, providing a standard
        validation mechanism for all extractors. It implements the validation step
        of the data extraction algorithm.
        
        Validation Rules:
        1. Both dates must be datetime objects
        2. Start date must be before end date
        3. End date cannot be in the future
        
        Parameters
        ----------
        start_date : datetime
            Start date of the data range to validate
        end_date : datetime
            End date of the data range to validate
            
        Raises
        ------
        ValueError
            - If dates are not datetime objects
            - If start_date is after end_date
            - If end_date is in the future
            
        Design Pattern Context
        --------------------
        - Template Method: Standard validation step
        - Chain of Responsibility: Part of validation chain
        
        Notes
        -----
        This method ensures data consistency across all extractors
        and prevents invalid API requests.
        """
       
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValueError("start_date and end_date must be datetime objects")
        
        if start_date > end_date:
            raise ValueError("start_date must be before end_date")
            
        if end_date > datetime.now():
            raise ValueError("end_date cannot be in the future")
    
    def save_raw_data(self, data: pd.DataFrame, filename: str) -> None:
        """
        Save raw data to CSV file in the source and date-specific directory.
        
        This method implements part of the Template Method pattern by providing
        a standard mechanism for persisting raw data. It ensures proper data
        organization and error handling during the storage process.
        
        Implementation Details:
        1. Verifies directory structure
        2. Constructs appropriate file path
        3. Saves data in CSV format
        4. Handles potential errors
        
        Parameters
        ----------
        data : pd.DataFrame
            Raw data frame to be saved
        filename : str
            Name of the output file
            
        Raises
        ------
        ValueError
            - If directory setup fails
            - If file writing fails
            - If data is invalid
            
        Design Pattern Context
        --------------------
        - Template Method: Standard data persistence
        - Chain of Responsibility: Part of data processing chain
        
        Notes
        -----
        - Creates directories if they don't exist
        - Uses source-specific paths
        - Maintains data organization
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
        Save processed data to CSV file in the source and date-specific directory.
        
        This method is part of the Template Method pattern, providing standardized
        storage for processed (cleaned and transformed) data. It maintains data
        organization and ensures proper error handling.
        
        Implementation Details:
        1. Validates directory structure
        2. Constructs processed data path
        3. Saves formatted data
        4. Handles potential errors
        
        Parameters
        ----------
        data : pd.DataFrame
            Processed and formatted data frame to save
        filename : str
            Name of the output file
            
        Raises
        ------
        ValueError
            - If directory structure is invalid
            - If file writing fails
            - If data format is incorrect
            
        Design Pattern Context
        --------------------
        - Template Method: Standard data storage step
        - Chain of Responsibility: Final step in data processing
        
        Notes
        -----
        - Maintains separate storage for processed data
        - Ensures consistent organization
        - Supports data versioning through date-based folders
        """
        try:
            if not hasattr(self, 'current_processed_dir'):
                self._setup_directories()
            
            file_path = self.current_processed_dir / filename
            
            data.to_csv(file_path)
            
        except Exception as e:
            raise ValueError(f"Failed to save processed data to {filename}: {str(e)}") from e
        