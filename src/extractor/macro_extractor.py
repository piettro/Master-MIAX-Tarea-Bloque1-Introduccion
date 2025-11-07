"""
Módulo para extração de dados macroeconômicos de diferentes fontes.
"""

from typing import List, Optional
from datetime import datetime
import pandas as pd

from src.extractor.sources.macro.extractor_worldbank import WorldBankExtractor

class MacroExtractor:
    """
    Classe para extrair dados macroeconômicos de diferentes fontes.
    
    Attributes
    ----------
    AVAILABLE_SOURCES : List[str]
        Lista de fontes de dados disponíveis
    """
    
    AVAILABLE_SOURCES = ['worldbank']
    
    def __init__(self):
        """Inicializa o extrator de dados macroeconômicos."""
        self._extractors = {
            'worldbank': WorldBankExtractor
        }
    
    def extract(
        self,
        indicators: List[str],
        countries: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Busca dados macroeconômicos de uma fonte específica.
        
        Parameters
        ----------
        indicators : List[str]
            Lista de indicadores para extrair
        countries : List[str], opcional
            Lista de países para extrair
        start_date : str, opcional
            Data inicial (YYYY-MM-DD)
        end_date : str, opcional
            Data final (YYYY-MM-DD)

        Returns
        -------
        pd.DataFrame
            DataFrame com os dados extraídos
            
        Raises
        ------
        ValueError
            Se a fonte especificada não estiver disponível
        """

        # Define valores padrão
        countries = countries or WorldBankExtractor.DEFAULT_COUNTRIES
        start_date = start_date or "1990-01-01"
        end_date = end_date or datetime.now().strftime("%Y-%m-%d")
        
        # Obtém o extrator e busca os dados
        extractor = self._extractors['worldbank']
        data = extractor.get_macro_data(
            indicators=indicators,
            countries=countries,
            start_date=start_date,
            end_date=end_date
        )
        
        return data
    
  
    def list_available_indicators(self) -> dict:
        """
        Retorna a lista de indicadores disponíveis para uma fonte.
        
        Returns
        -------
        dict
            Dicionário com nome e código dos indicadores
        """
            
        return self._extractors['worldbank'].list_available_indicators()