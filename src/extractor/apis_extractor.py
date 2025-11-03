import pandas as pd
from datetime import date, timedelta
from decouple import config
from pathlib import Path
from src.extractor.sources.eodhd import get_data_eodhd, format_data_eodhd
from src.extractor.sources.fmp import get_data_fmp, format_data_fmp
from src.extractor.sources.alphavantage import get_data_alphavantage, format_data_alphavantage
from src.extractor.sources.yahoo import get_data_yfinance

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "src"/ "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "src"/ "data" / "processed"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_historical_data(tickers,start_date=date.today()- timedelta(days=30),end_date=date.today(),source='yfinance'):
    source_options = ['yfinance', 'eodhd', 'fmp','alphavantage']
    
    if source not in source_options:
        raise ValueError(f"O parâmetro deve ser uma das seguintes opções: {source}")
    
    if source == 'yfinance':
        data = get_data_yfinance(tickers=tickers,start_date=start_date,end_date=end_date)
        
        return data
    elif source == 'eodhd':
        data = get_data_eodhd(tickers=tickers,start_date=start_date,end_date=end_date)
        data = format_data_eodhd(data)
        
        return data
    elif source == 'fmp':
        data =  get_data_fmp(tickers=tickers,start_date=start_date,end_date=end_date)
        data = format_data_fmp(data)
        
        return data
    elif source == 'alphavantage':
        data =  get_data_alphavantage(tickers=tickers,start_date=start_date,end_date=end_date)
        data = format_data_fmp(data)

        return data
    else:
        return ""