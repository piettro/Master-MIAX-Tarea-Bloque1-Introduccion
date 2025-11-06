import yfinance as yf
from datetime import date, timedelta
from decouple import config
from src.extractor.extractor_base import BaseExtractor

class YahooExtractor(BaseExtractor):
    def __init__(self, api_key: str = config("API_KEY_YAHOO")):
        self.api_key = api_key

    def get_historical_prices(
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
        
        data = yf.download(
            tickers, 
            start=start_date, 
            end=end_date, 
            progress=False
        )

        return data

    def format_historical_prices(data):
        pass