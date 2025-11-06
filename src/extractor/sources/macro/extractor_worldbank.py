"""
Módulo para extração de dados do World Bank.
"""

import requests
import pandas as pd
import warnings
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
from requests.exceptions import HTTPError

class WorldBankExtractor:
    """
    Classe para extrair dados macroeconômicos do World Bank.
    """
    
    # API Base URL
    BASE_URL = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"
    DEFAULT_PARAMS = {
        "format": "json",
        "per_page": 25000
    }
    
    # Países e agregados disponíveis
    EU_ALTERNATIVES = ["EUU", "EU27_2020", "EU28"]
    DEFAULT_COUNTRIES = ["ESP", "EUU"]
    
    # Mapeamento de indicadores
    AVAILABLE_INDICATORS = {
        "GDP (current US$) (billions)": ("NY.GDP.MKTP.CD", lambda s: s / 1e9),
        "GDP per capita, PPP (constant 2017 international $)": ("NY.GDP.PCAP.PP.KD", None),
        "GDP growth (annual %)": ("NY.GDP.MKTP.KD.ZG", None),
        "Inflation, GDP deflator (annual %)": ("NY.GDP.DEFL.KD.ZG", None),
        "Agriculture, forestry, and fishing, value added (% of GDP)": ("NV.AGR.TOTL.ZS", None),
        "Industry (including construction), value added (% of GDP)": ("NV.IND.TOTL.ZS", None),
        "Exports of goods and services (% of GDP)": ("NE.EXP.GNFS.ZS", None),
        "Imports of goods and services (% of GDP)": ("NE.IMP.GNFS.ZS", None),
        "Gross capital formation (% of GDP)": ("NE.GDI.TOTL.ZS", None),
        "Revenue, excluding grants (% of GDP)": ("GC.REV.XGRT.GD.ZS", None),
        "Central government debt, total (% of GDP)": ("GC.DOD.TOTL.GD.ZS", None),
        "Central government debt, total (current US$)": ("GC.DOD.TOTL.CN", lambda s: s / 1e9),
        "Net lending (+) / net borrowing (-) (% of GDP)": ("GC.NLD.TOTL.GD.ZS", None),
        "Domestic credit provided by financial sector (% of GDP)": ("FS.AST.DOMS.GD.ZS", None),
        "Tax revenue (% of GDP)": ("GC.TAX.TOTL.GD.ZS", None),
        "Military expenditure (% of GDP)": ("MS.MIL.XPND.GD.ZS", None),
        "Mobile cellular subscriptions (per 100 people)": ("IT.CEL.SETS.P2", None),
        "Individuals using the Internet (% of population)": ("IT.NET.USER.ZS", None),
        "High-technology exports (% of manufactured exports)": ("TX.VAL.TECH.MF.ZS", None),
    }
    
    @classmethod
    def get_macro_data(
        cls,
        indicators: List[str],
        countries: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Obtém dados macroeconômicos do World Bank.
        
        Parameters
        ----------
        indicators : List[str]
            Lista de indicadores para extrair
        countries : List[str]
            Lista de países para extrair
        start_date : str
            Data inicial (YYYY-MM-DD)
        end_date : str
            Data final (YYYY-MM-DD)
            
        Returns
        -------
        pd.DataFrame
            DataFrame com os dados extraídos
        """
        start_year = int(start_date[:4])
        end_year = int(end_date[:4])
        
        data_frames = {}
        for indicator in indicators:
            if indicator not in cls.AVAILABLE_INDICATORS:
                warnings.warn(f"Indicador não suportado: {indicator}")
                continue
                
            code, transform = cls.AVAILABLE_INDICATORS[indicator]
            df = cls._fetch_indicator(
                code,
                countries,
                start_year,
                end_year
            )
            
            # Aplica transformação se necessário
            if transform is not None:
                df = df.apply(transform)
                
            data_frames[indicator] = df
            
        if not data_frames:
            raise ValueError("Nenhum dado extraído")
            
        return cls.format_macro_data(data_frames)
    
    @classmethod
    def _fetch_indicator(
        cls,
        indicator_code: str,
        countries: List[str],
        start_year: int,
        end_year: int
    ) -> pd.DataFrame:
        """
        Extrai um indicador específico para múltiplos países.
        
        Parameters
        ----------
        indicator_code : str
            Código do indicador World Bank
        countries : list
            Lista de países
        start_year : int
            Ano inicial
        end_year : int
            Ano final
            
        Returns
        -------
        pd.DataFrame
            DataFrame com os dados do indicador
        """
        cols = {}
        for country in countries:
            tried = []
            alternatives = cls.EU_ALTERNATIVES if country == "EUU" else [country]
            success = False
            
            # Tenta cada alternativa de código de país
            for alt_country in alternatives:
                tried.append((alt_country, start_year, end_year))
                try:
                    # Tenta primeiro com o ano final especificado
                    series = cls._fetch_indicator_country(
                        indicator_code,
                        alt_country,
                        start_year,
                        end_year
                    )
                    if not series.empty:
                        cols[country] = series
                        success = True
                        break
                        
                except HTTPError:
                    # Se falhar, tenta com o ano anterior
                    if end_year > start_year:
                        try:
                            series = cls._fetch_indicator_country(
                                indicator_code,
                                alt_country,
                                start_year,
                                end_year - 1
                            )
                            if not series.empty:
                                cols[country] = series
                                success = True
                                break
                        except HTTPError:
                            continue
                            
            if not success:
                warnings.warn(
                    f"Dados não disponíveis para {indicator_code} "
                    f"em {country}. Tentativas: {tried}"
                )
                
        if not cols:
            raise ValueError(
                f"Sem dados para {indicator_code} nos países {countries}"
            )
            
        # Constrói DataFrame final
        df = pd.DataFrame(cols)
        df.index.name = "year"
        return df
    
    @classmethod
    def _fetch_indicator_country(
        cls,
        indicator_code: str,
        country: str,
        start_year: int,
        end_year: int
    ) -> pd.Series:
        """
        Extrai um indicador para um país específico.
        
        Parameters
        ----------
        indicator_code : str
            Código do indicador World Bank
        country : str
            Código do país
        start_year : int
            Ano inicial
        end_year : int
            Ano final
            
        Returns
        -------
        pd.Series
            Série temporal com os dados do indicador
        """
        # Constrói URL
        url = cls.BASE_URL.format(
            countries=country,
            indicator=indicator_code
        )
        
        # Adiciona parâmetros
        params = cls.DEFAULT_PARAMS.copy()
        params["date"] = f"{start_year}:{end_year}"
        
        # Faz requisição
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # Valida resposta
        if not isinstance(data, list) or len(data) < 2 or data[1] is None:
            return pd.Series(dtype=float)
            
        # Processa dados
        rows = []
        for record in data[1]:
            try:
                year = int(record.get("date"))
                value = record.get("value")
                if value is not None:
                    rows.append((year, float(value)))
            except (ValueError, TypeError):
                continue
                
        if not rows:
            return pd.Series(dtype=float)
            
        # Cria e ordena série temporal
        series = pd.Series(dict(rows)).sort_index()
        return series
    
    @staticmethod
    def format_macro_data(indicator_frames: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Formata os dados macroeconômicos em um DataFrame com MultiIndex.
        
        Parameters
        ----------
        indicator_frames : dict
            Dicionário com DataFrames por indicador
            
        Returns
        -------
        pd.DataFrame
            DataFrame formatado com MultiIndex nas colunas ['Country', 'Indicator']
        """
        # Primeiro, cria um DataFrame vazio para acumular os dados
        all_data = []
        
        # Para cada indicador
        for indicator, df in indicator_frames.items():
            # Para cada país no DataFrame do indicador
            for country in df.columns:
                # Cria uma Series com o MultiIndex correto
                series = df[country]
                series.name = (country, indicator)  # Define o MultiIndex (Country, Indicator)
                all_data.append(series)
        
        # Combina todas as séries em um DataFrame
        panel = pd.concat(all_data, axis=1)
        
        # Define explicitamente os nomes dos níveis do MultiIndex
        panel.columns.names = ['Country', 'Indicator']
        
        return panel.sort_index(axis=1)
    
    @classmethod
    def list_available_indicators(cls) -> Dict[str, str]:
        """
        Retorna o dicionário de indicadores disponíveis.
        
        Returns
        -------
        Dict[str, str]
            Dicionário com nome e código dos indicadores
        """
        return {k: v[0] for k, v in cls.AVAILABLE_INDICATORS.items()}
