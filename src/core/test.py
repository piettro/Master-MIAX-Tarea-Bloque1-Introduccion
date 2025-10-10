import pandas as pd
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import json
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from urllib.request import urlopen
import certifi
from decouple import config
import requests
from eodhd import APIClient
from bs4 import BeautifulSoup
from pathlib import Path
from dataclasses import dataclass, field
from typing import Union, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "src"/ "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "src"/ "data" / "processed"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

#Index e Stock
def get_data_yfinance(tickers,start_date=date.today()- timedelta(days=30),end_date=date.today()):
    data = yf.download(tickers, 
                      start=start_date, 
                      end=end_date, 
                      progress=False)
    
    data.to_csv(RAW_DATA_DIR / 'output_yfinance.csv')

    return data

#Stock
def get_data_eodhd(tickers,start_date=date.today()- timedelta(days=30),end_date=date.today()):
    API_KEY_EODHD = config('API_KEY_EODHD')
    api = APIClient(API_KEY_EODHD)
    
    data = pd.DataFrame()

    for ticker in tickers:
        prices = api.get_eod_historical_stock_market_data(symbol=ticker, from_date=start_date, to_date=end_date)
        prices = pd.DataFrame(prices)
        prices['ticker'] = ticker
        data = pd.concat([data,prices])
    
    data.to_csv(RAW_DATA_DIR / 'output_eodhd.csv')

    return data

#Index e Stock
def get_data_fmp(tickers,start_date=date.today()- timedelta(days=30),end_date=date.today()):
    API_KEY_FMP = config('API_KEY_FMP')

    data = pd.DataFrame()

    for ticker in tickers:
        url = (f"https://financialmodelingprep.com/stable/historical-price-eod/full?from={start_date}&to={end_date}&symbol={ticker}&apikey={API_KEY_FMP}")
        response = urlopen(url, cafile=certifi.where())
        prices = response.read().decode("utf-8")

        prices = pd.read_json(prices)
        prices['ticker'] = ticker
        data = pd.concat([data,prices])
        data.to_csv(RAW_DATA_DIR / 'output_fmp.csv')

    return data

#Stock
def get_data_alphavantage(tickers,start_date=date.today()- timedelta(days=30),end_date=date.today()):
    API_KEY_ALPHAVANTAGE = config('API_KEY_ALPHAVANTAGE')

    data = pd.DataFrame()

    for ticker in tickers:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY_ALPHAVANTAGE}'
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
    
    data.to_csv(RAW_DATA_DIR / 'output_finfut.csv')

    return data

def get_historical_data(tickers,start_date=date.today()- timedelta(days=30),end_date=date.today(),source='yfinance'):
    source_options = ['yfinance', 'eodhd', 'fmp','alphavantage']
    
    if source not in source_options:
        raise ValueError(f"O parâmetro deve ser uma das seguintes opções: {source}")
    
    if source == 'yfinance':
        data = get_data_yfinance(tickers=tickers,start_date=start_date,end_date=end_date)
        return data
    elif source == 'eodhd':
        data = get_data_eodhd(tickers=tickers,start_date=start_date,end_date=end_date)

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


        df_pivot = data.pivot_table(
            index="Date",
            columns="Ticker",
            values=["Open", "High", "Low", "Close", "Volume"]
        )

        df_pivot.columns.set_names(["Price", "Ticker"], inplace=True)
        df_pivot = df_pivot.sort_index(axis=1, level=[0, 1])              

        df_pivot.to_csv(PROCESSED_DATA_DIR / 'output_eodhd_clean_v2.csv')
        
        return df_pivot
    elif source == 'fmp':
        data =  get_data_fmp(tickers=tickers,start_date=start_date,end_date=end_date)

        data.rename(columns={
            "date":"Date",
            "open":"Open",
            "high":"High",
            "low":"Low",
            "close":"Close",
            "volume":"Volume",
            "symbol":"Ticker"
        },inplace=True)
        data.index = data['Date']
        data.drop(['change','changePercent','vwap','Date'],axis=1,inplace=True)

        df_pivot = data.pivot_table(
            index="Date",
            columns="Ticker",
            values=["Open", "High", "Low", "Close", "Volume"]
        )

        df_pivot.columns.set_names(["Price", "Ticker"], inplace=True)
        df_pivot = df_pivot.sort_index(axis=1, level=[0, 1])    
        df_pivot.to_csv(PROCESSED_DATA_DIR / 'output_fmp_clean_v2.csv')

        return df_pivot
    elif source == 'alphavantage':
        #data =  get_data_alphavantage(tickers=tickers,start_date=start_date,end_date=end_date)
        data = pd.read_csv(RAW_DATA_DIR / 'output_finfut.csv')
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
        df_pivot.to_csv(PROCESSED_DATA_DIR / 'output_finfut_clean_v2.csv')

        return df_pivot
    else:
        return ""

@dataclass
class PricesSeries():
    tickers:Union[str, List[str]] = field(default_factory=list)
    source:str = 'yfinance'
    data:pd.DataFrame = field(init=False)
    start_date:str = date.today()- timedelta(days=30)
    end_date:str = date.today()

    def __post_init__(self):
        if isinstance(self.tickers, str):
            self.tickers = self.tickers.replace(',', ' ').split()
        elif isinstance(self.tickers, (set, tuple)):
            self.tickers = list(self.tickers)

        self.data = get_historical_data(tickers=self.tickers,source=self.source)
    
    def generate_stats(self):
        print(self.data)

if __name__ == "__main__":
    test = PricesSeries(tickers=['AAPL','GOOG'],source='eodhd')
    test.generate_stats()
