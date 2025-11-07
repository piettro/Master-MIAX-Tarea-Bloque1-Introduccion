"""Financial Modeling Prep (FMP) API data extractor implementation."""

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
    """FMP API specific implementation of the market data extractor."""
    
    # FMP-specific interval mapping
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
        """Initialize FMP extractor with API configuration."""
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
        Fetch historical data from FMP API.
        
        Parameters
        ----------
        symbols : Union[str, List[str]]
            Single symbol or list of symbols to fetch
        start_date : datetime
            Start date for data range
        end_date : datetime
            End date for data range
        interval : str, optional
            Data interval, by default "1day"
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
            If data cannot be retrieved from FMP
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
        Format FMP data into standardized format.
        
        Parameters
        ----------
        data : pd.DataFrame
            Raw data from FMP API
        
        Returns
        -------
        pd.DataFrame
            Formatted data with standardized structure
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
        Get FMP specific source information.
        
        Returns
        -------
        Dict
            Information about FMP API capabilities
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
