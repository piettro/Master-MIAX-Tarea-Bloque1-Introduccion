import pandas as pd
import yfinance as yf

from datetime import date, timedelta
from decouple import config
from pathlib import Path

#Index e Stock
def get_data_yfinance(tickers,start_date=date.today()- timedelta(days=30),end_date=date.today()):
    data = yf.download(tickers, 
                      start=start_date, 
                      end=end_date, 
                      progress=False)
    
    return data