"""
Base extractor class defining the interface for all data extractors.
"""

from abc import abstractmethod
from asyncio.log import logger
from datetime import datetime
from typing import Dict
from pathlib import Path

class BaseExtractor:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.raw_data_dir = self.base_dir / "src"/ "data" / "raw"
        self.processed_data_dir = self.base_dir / "src"/ "data" / "processed"
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def get_historical_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ):
        """
        Get historical price data for a single symbol.
        
        Args:
            symbol: Ticker symbol
            start_date: Start date for data
            end_date: End date for data
            interval: Data interval ('1d', '1h', etc.)
        
        Returns:
            PriceSeries object with standardized data
        """
        pass

    @abstractmethod
    def format_historical_prices(
        self,
        raw_data: Dict[str, any]
    ):
        """
        Format raw historical price data into standardized PriceSeries.
        
        Args:
            raw_data: Raw data from the data source
        
        Returns:
            PriceSeries object with standardized data
        """
        pass