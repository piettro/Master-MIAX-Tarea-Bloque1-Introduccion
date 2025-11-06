import pandas as pd
from datetime import date, timedelta
from decouple import config
import requests
from src.extractor.sources.prices.extractor_prices_base import BaseExtractor

class AlphaVantageExtractor(BaseExtractor):
    def __init__(self, api_key: str = config('API_KEY_ALPHAVANTAGE')):
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
        
        data = pd.DataFrame()

        for ticker in tickers:
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={self.api_key}'
            r = requests.get(url)
            json_data = r.json()
            ts_data = json_data['Time Series (Daily)']

            # Converter para DataFrame
            df = pd.DataFrame.from_dict(ts_data, orient='index')

            # Renomear colunas
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

            df['Open'] = df['Open'].astype(float)
            df['High'] = df['High'].astype(float)
            df['Low'] = df['Low'].astype(float)
            df['Close'] = df['Close'].astype(float)
            df['Volume'] = df['Volume'].astype(int)

            # Converter índice para datetime e ordenar
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df = df.loc[start_date:end_date]
            df['ticker'] = ticker
            data = pd.concat([data,df])
        
        data.to_csv(self.raw_data_dir / 'output_finfut.csv')
    
    
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
            "open":"Open",
            "high":"High",
            "low":"Low",
            "close":"Close",
            "volume":"Volume",
            "ticker":"Ticker",
            'Unnamed: 0':'Date'
        },inplace=True)

        df_pivot = data.pivot_table(
            index='Date',
            columns="Ticker",
            values=["Open", "High", "Low", "Close", "Volume"]
        )

        df_pivot.columns.set_names(["Price", "Ticker"], inplace=True)
        df_pivot = df_pivot.sort_index(axis=1, level=[0, 1])    
        df_pivot.to_csv(self.processed_data_dir / 'output_finfut_clean.csv')
        
        return df_pivot

