"""Yahoo Finance data extractor implementation."""

import yfinance as yf
from datetime import date, datetime, timedelta
from typing import Union, List, Dict
import pandas as pd
from src.extractor.sources.prices.extractor_prices_base import (
    BaseExtractor,
    Interval
)

class YahooExtractor(BaseExtractor):
    """Yahoo Finance API specific implementation of the market data extractor."""
    
    # Yahoo-specific interval mapping
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
        """Initialize Yahoo Finance extractor."""
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
        Fetch historical data from Yahoo Finance.
        
        Parameters
        ----------
        symbols : Union[str, List[str]]
            Single symbol or list of symbols to fetch
        start_date : datetime
            Start date for data range
        end_date : datetime
            End date for data range
        interval : str, optional
            Data interval, by default "1d"
        include_adj : bool, optional
            Whether to include adjusted prices, by default True
            
        Returns
        -------
        pd.DataFrame
            Historical price data
            
        Raises
        ------
        ValueError
            If invalid parameters are provided
        ConnectionError
            If data cannot be retrieved from Yahoo Finance
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
            
            # Download data from Yahoo Finance
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
        Format Yahoo Finance data into standardized format.
        
        Parameters
        ----------
        raw_data : pd.DataFrame
            Raw data from Yahoo Finance
        symbol : str
            Symbol for the data being formatted
            
        Returns
        -------
        pd.DataFrame
            Formatted data with standardized structure
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
        Get Yahoo Finance specific source information.
        
        Returns
        -------
        Dict
            Information about Yahoo Finance capabilities
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