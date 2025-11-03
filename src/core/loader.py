from pathlib import Path
from datetime import date, timedelta
from typing import List, Union, Optional

import pandas as pd
import yfinance as yf

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_historical_data(tickers: Union[str, List[str]], start_date: date = date.today() - timedelta(days=30), end_date: date = date.today(), source: str = "yfinance") -> pd.DataFrame:
	"""Fetch historical price data for tickers.

	Currently supports yfinance. Returns a DataFrame. For multi-ticker yfinance returns a
	DataFrame with a MultiIndex columns (Price, Ticker) similar to project expectations.
	"""
	if isinstance(tickers, str):
		tickers = tickers.replace(",", " ").split()

	if source != "yfinance":
		raise NotImplementedError(f"Only 'yfinance' source is supported in this loader implementation (asked: {source})")

	# yfinance can download multiple tickers at once
	try:
		df = yf.download(tickers, start=start_date, end=end_date, progress=False, group_by='ticker', auto_adjust=False)
	except Exception as e:
		raise RuntimeError(f"Failed to download data from yfinance: {e}")

	# If single ticker, yfinance returns a plain DataFrame; convert to MultiIndex (Price, Ticker)
	if isinstance(tickers, list) and len(tickers) == 1:
		t = tickers[0]
		if isinstance(df.columns, pd.Index):
			# make a multiindex columns with Price and Ticker
			df.columns = pd.MultiIndex.from_product([df.columns, [t]])
			df = df.swaplevel(0, 1, axis=1).sort_index(axis=1)
	return df


def get_macro_data(indicators: Union[str, List[str]], start_date: Optional[date] = None, end_date: Optional[date] = None, source: str = "fred") -> pd.DataFrame:
	"""Stub for macro indicator retrieval.

	For now this returns an empty DataFrame. In future we can hook pandas_datareader or FRED API.
	"""
	# normalize indicators
	if isinstance(indicators, str):
		indicators = indicators.replace(",", " ").split()

	# Return empty DataFrame as placeholder
	return pd.DataFrame()

