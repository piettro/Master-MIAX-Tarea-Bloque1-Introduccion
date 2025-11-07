"""EODHD API data extractor implementation."""

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
    """EODHD API specific implementation of the market data extractor."""

    # EODHD-specific interval mapping
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
        """Initialize EODHD extractor with API configuration."""
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
        """Initialize the EODHD API client."""
        try:
            self._api_client = APIClient(self._api_key)
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
        Fetch historical price data from EODHD API.

        Parameters
        ----------
        symbols : Union[str, List[str]]
            Single ticker or list of tickers to fetch
        start_date : date, optional
            Start date for data range, by default 30 days ago
        end_date : date, optional
            End date for data range, by default today
        interval : Interval, optional
            Data interval, by default Interval.DAILY

        Returns
        -------
        pd.DataFrame
            Historical price data in standardized format

        Raises
        ------
        ValueError
            If invalid parameters are provided
        ConnectionError
            If API request fails
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
        Format raw EODHD data into standardized format.

        Parameters
        ----------
        data : pd.DataFrame
            Raw data from EODHD API
        Returns
        -------
        pd.DataFrame
            Formatted and cleaned data
        """
        try:
            # Standardize column names
            data = data.rename(columns={
                "date": "Date",
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
                "symbol": "Symbol"
            })

            # Convert date column to datetime
            data['Date'] = pd.to_datetime(data['Date'])
            data.set_index('Date', inplace=True)

            # Remove adjusted close as it's not consistently available
            if 'adjusted_close' in data.columns:
                data.drop('adjusted_close', axis=1, inplace=True)

            # Create multi-level columns
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

    def _save_raw_data(self, data: pd.DataFrame, filename: str) -> None:
        """Save raw data to CSV file."""
        try:
            data.to_csv(self.raw_data_dir / filename)
        except Exception as e:
            logger.error(f"Failed to save raw data: {str(e)}")

    def _save_processed_data(self, data: pd.DataFrame, filename: str) -> None:
        """Save processed data to CSV file."""
        try:
            data.to_csv(self.processed_data_dir / filename)
        except Exception as e:
            logger.error(f"Failed to save processed data: {str(e)}")

    def get_source_info(self) -> Dict:
        """
        Get EODHD specific source information.

        Returns
        -------
        Dict
            Information about EODHD API capabilities
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

