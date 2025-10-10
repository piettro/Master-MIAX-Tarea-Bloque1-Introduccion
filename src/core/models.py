import pandas as pd
from datetime import date, timedelta
from dataclasses import dataclass, field
from typing import Union, List

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
