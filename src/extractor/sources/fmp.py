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


def format_data_fmp(data):
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
    data.drop(['change','changePercent','vwap','Date'],axis=1,inplace=True)


    data = data.pivot_table(
        index="Date",
        columns="Ticker",
        values=["Open", "High", "Low", "Close", "Volume"]
    )

    data.columns.set_names(["Price", "Ticker"], inplace=True)
    data = data.sort_index(axis=1, level=[0, 1])    

    return data