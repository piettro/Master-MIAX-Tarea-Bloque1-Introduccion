"""
Módulo para extração de dados de preços de diferentes APIs financeiras.
"""

from typing import List
from datetime import date
import pandas as pd

from src.extractor.sources.prices.extractor_yahoo import YahooExtractor
from src.extractor.sources.prices.extractor_eodhd import EODHDExtractor
from src.extractor.sources.prices.extractor_fmp import FMPExtractor
from src.extractor.sources.prices.extractor_alphavantage import AlphaVantageExtractor

class APIExtractor:
    """
    Classe para extrair dados de preços de diferentes APIs financeiras.
    
    Attributes
    ----------
    AVAILABLE_SOURCES : List[str]
        Lista de fontes de dados disponíveis
    """
    
    AVAILABLE_SOURCES = ['yfinance', 'eodhd', 'fmp', 'alphavantage']
    
    def __init__(self):
        """Inicializa o extrator de APIs."""
        self._extractors = {
            'yfinance': YahooExtractor,
            'eodhd': EODHDExtractor,
            'fmp': FMPExtractor,
            'alphavantage': AlphaVantageExtractor
        }
    
    def fetch_price_series(
        self,
        tickers: List[str],
        start_date: date,
        end_date: date,
        source: str
    ) -> pd.DataFrame:
        """
        Busca séries históricas de preços de uma fonte específica.
        
        Parameters
        ----------
        tickers : List[str]
            Lista de símbolos dos ativos
        start_date : date
            Data inicial do período
        end_date : date
            Data final do período
        source : str
            Fonte dos dados ('yfinance', 'eodhd', 'fmp' ou 'alphavantage')
            
        Returns
        -------
        pd.DataFrame
            DataFrame com os preços históricos
            
        Raises
        ------
        ValueError
            Se a fonte especificada não estiver disponível
        """
        if source not in self.AVAILABLE_SOURCES:
            raise ValueError(
                f"Fonte inválida. As opções disponíveis são: {self.AVAILABLE_SOURCES}"
            )
        
        extractor = self._extractors[source]
        data = extractor.get_historical_prices(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date
        )
        
        # Formatação específica para algumas fontes
        if source in ['eodhd', 'fmp', 'alphavantage']:
            data = extractor.format_historical_prices(data)
        
        return data
    
    @classmethod
    def list_available_sources(cls) -> List[str]:
        """
        Retorna a lista de fontes de dados disponíveis.
        
        Returns
        -------
        List[str]
            Lista com os nomes das fontes disponíveis
        """
        return cls.AVAILABLE_SOURCES.copy()