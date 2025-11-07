"""Alpha Vantage API data extractor implementation."""

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
    """Alpha Vantage API specific implementation of the market data extractor."""
    
    # Alpha Vantage-specific interval mapping
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
        """Initialize Alpha Vantage extractor with API configuration."""
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
        Fetch historical data from Alpha Vantage API.
        
        Parameters
        ----------
        symbols : Union[str, List[str]]
            Single symbol or list of symbols to fetch
        start_date : datetime
            Start date for data range
        end_date : datetime
            End date for data range
        interval : str, optional
            Data interval, by default "daily"
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
            If data cannot be retrieved from Alpha Vantage
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
        Format Alpha Vantage data into standardized format.
        
        Parameters
        ----------
        data : pd.DataFrame
            Raw data from Alpha Vantage API            
        Returns
        -------
        pd.DataFrame
            Formatted data with standardized structure
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
        Get Alpha Vantage specific source information.
        
        Returns
        -------
        Dict
            Information about Alpha Vantage API capabilities
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

