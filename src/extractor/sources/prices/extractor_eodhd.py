import pandas as pd
from datetime import date, timedelta
from decouple import config
from eodhd import APIClient
from src.extractor.sources.prices.extractor_prices_base import BaseExtractor

class EODHDExtractor(BaseExtractor):
    def __init__(self, api_key: str = config('API_KEY_EODHD')):
        self.api_key = api_key

    def get_historical_prices(
        self,
        tickers,
        start_date=date.today()- timedelta(days=30),
        end_date=date.today()
    ):
        """
        Generate a Markdown report for a single price series.
        
        Args:
            price_series: PriceSeries to report on
            include_validation: Include data quality validation
            include_statistics: Include statistical analysis
        
        Returns:
            Markdown formatted report
        """

        api = APIClient(self.api_key)
        
        data = pd.DataFrame()

        for ticker in tickers:
            prices = api.get_eod_historical_stock_market_data(symbol=ticker, from_date=start_date, to_date=end_date)
            prices = pd.DataFrame(prices)
            prices['ticker'] = ticker
            data = pd.concat([data,prices])
        
        data.to_csv(self.raw_data_dir / 'output_eodhd.csv')

        return data
    
    
    def format_historical_prices(self, data):
        """
        Generate a Markdown report for a single price series.
        
        Args:
            price_series: PriceSeries to report on
            include_validation: Include data quality validation
            include_statistics: Include statistical analysis
        
        Returns:
            Markdown formatted report
        """
        
        data.rename(columns={
            "date":"Date",
            "open":"Open",
            "high":"High",
            "low":"Low",
            "close":"Close",
            "volume":"Volume",
            "ticker":"Ticker"
        },inplace=True)
        data.index = data['Date']
        data.drop(['adjusted_close','Date'],axis=1,inplace=True)


        data = data.pivot_table(
            index="Date",
            columns="Ticker",
            values=["Open", "High", "Low", "Close", "Volume"]
        )

        data.columns.set_names(["Price", "Ticker"], inplace=True)
        data = data.sort_index(axis=1, level=[0, 1])              

        data.to_csv(self.processed_data_dir / 'output_eodhd_clean.csv')

        return data   

