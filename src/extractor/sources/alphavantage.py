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

def clean_data_alphavantage(data):
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
    df_pivot.to_csv(PROCESSED_DATA_DIR / 'output_finfut_clean.csv')
    
    return df_pivot