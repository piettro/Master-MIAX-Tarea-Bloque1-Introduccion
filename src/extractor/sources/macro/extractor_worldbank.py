"""
Module for extracting macroeconomic data from the World Bank API.
Implements multiple design patterns for robust and flexible data extraction.
"""

import requests
import pandas as pd
import warnings
from typing import Dict, List
from requests.exceptions import HTTPError

class WorldBankExtractor:
    """
    A robust World Bank data extractor implementing several design patterns.
    
    This class is designed to fetch, transform, and structure macroeconomic data
    from the World Bank API. It uses various design patterns to provide a 
    modular, extensible, and fault-tolerant architecture.

    Design Patterns
    ---------------
    - **Singleton:** Maintains a single, consistent API configuration.
    - **Strategy:** Supports different transformation strategies for indicators.
    - **Factory Method:** Creates appropriate data structures for each indicator.
    - **Template Method:** Defines the high-level data extraction workflow.
    """

    BASE_URL = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"
    DEFAULT_PARAMS = {
        "format": "json",
        "per_page": 25000
    }

    EU_ALTERNATIVES = ["EUU", "EU27_2020", "EU28"]
    DEFAULT_COUNTRIES = ["ESP", "EUU"]

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
        Retrieve macroeconomic data from the World Bank API using multiple strategies.
        
        This method defines the overall algorithm for data extraction (Template Method),
        delegating specific tasks such as fetching and transforming indicators to
        specialized helper methods.

        Parameters
        ----------
        indicators : List[str]
            List of economic indicators to extract (e.g., ['GDP growth', 'Inflation'])
        countries : List[str]
            List of ISO country codes to include in the analysis (e.g., ['USA', 'ESP'])
        start_date : str
            Start date in 'YYYY-MM-DD' format
        end_date : str
            End date in 'YYYY-MM-DD' format
            
        Returns
        -------
        pd.DataFrame
            A MultiIndex DataFrame containing the extracted and formatted data.

        Design Patterns
        ----------------
        - **Template Method:** Defines the main extraction process.
        - **Strategy:** Applies transformations depending on indicator types.
        - **Factory:** Builds appropriate data structures.
        - **Observer:** Tracks progress and handles warnings.
        """
        start_year = int(start_date[:4])
        end_year = int(end_date[:4])

        data_frames = {}
        for indicator in indicators:
            if indicator not in cls.AVAILABLE_INDICATORS:
                warnings.warn(f"Unsupported indicator: {indicator}")
                continue

            code, transform = cls.AVAILABLE_INDICATORS[indicator]
            df = cls._fetch_indicator(code, countries, start_year, end_year)

            # Strategy Pattern — apply transformation if defined
            if transform is not None:
                df = df.apply(transform)

            data_frames[indicator] = df

        if not data_frames:
            raise ValueError("No data extracted for the selected indicators.")

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
        Retrieve a specific indicator for multiple countries, implementing
        fallback strategies and structured error handling.
        
        Parameters
        ----------
        indicator_code : str
            The World Bank indicator code (e.g., 'NY.GDP.MKTP.CD')
        countries : list
            List of ISO country codes
        start_year : int
            Starting year for extraction
        end_year : int
            Ending year for extraction
            
        Returns
        -------
        pd.DataFrame
            A DataFrame containing the indicator data by country.
        
        Design Patterns
        ----------------
        - **Strategy:** Uses different retrieval strategies per country.
        - **Chain of Responsibility:** Provides fallback mechanisms for EU data.
        - **Factory:** Builds country-specific DataFrames.
        - **Observer:** Handles extraction progress and warnings.
        """
        cols = {}
        for country in countries:
            tried = []
            alternatives = cls.EU_ALTERNATIVES if country == "EUU" else [country]
            success = False

            for alt_country in alternatives:
                tried.append((alt_country, start_year, end_year))
                try:
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
                    f"No data available for {indicator_code} in {country}. Tried: {tried}"
                )

        if not cols:
            raise ValueError(f"No data retrieved for {indicator_code} in {countries}")

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
        Retrieve a specific indicator for one country.
        
        Parameters
        ----------
        indicator_code : str
            World Bank indicator code.
        country : str
            ISO country code.
        start_year : int
            Initial year.
        end_year : int
            Final year.
            
        Returns
        -------
        pd.Series
            A time series containing the indicator values by year.
        """
        url = cls.BASE_URL.format(countries=country, indicator=indicator_code)
        params = cls.DEFAULT_PARAMS.copy()
        params["date"] = f"{start_year}:{end_year}"

        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or len(data) < 2 or data[1] is None:
            return pd.Series(dtype=float)

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

        series = pd.Series(dict(rows)).sort_index()
        return series

    @staticmethod
    def format_macro_data(indicator_frames: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Format macroeconomic data into a structured MultiIndex DataFrame.
        
        This method assembles multiple indicator DataFrames into a unified,
        easy-to-analyze structure using the Builder pattern.
        
        Parameters
        ----------
        indicator_frames : Dict[str, pd.DataFrame]
            A dictionary mapping indicator names to their respective DataFrames.
            
        Returns
        -------
        pd.DataFrame
            A formatted DataFrame with MultiIndex columns ['Country', 'Indicator'].
        
        Design Patterns
        ----------------
        - **Builder:** Combines and structures multiple DataFrames.
        - **Factory:** Creates appropriate index structures.
        - **Strategy:** Handles formatting based on data characteristics.
        
        Notes
        -----
        The final structure uses:
        - Columns: MultiIndex ['Country', 'Indicator']
        - Index: Year (time index)
        - Values: Numeric indicator data
        """
        all_data = []

        for indicator, df in indicator_frames.items():
            for country in df.columns:
                series = df[country]
                series.name = (country, indicator)
                all_data.append(series)

        panel = pd.concat(all_data, axis=1)
        panel.columns.names = ['Country', 'Indicator']

        return panel.sort_index(axis=1)

    @classmethod
    def list_available_indicators(cls) -> Dict[str, str]:
        """
        Retrieve the catalog of supported macroeconomic indicators.
        
        This method provides a simplified interface (Facade Pattern) for
        accessing the complex internal indicator configuration.

        Returns
        -------
        Dict[str, str]
            Mapping of readable indicator names to their World Bank codes.

        Design Patterns
        ----------------
        - **Facade:** Simplifies access to internal configuration.
        - **Singleton:** Ensures consistent indicator catalog.
        - **Factory:** Builds a dictionary structure dynamically.
        """
        return {k: v[0] for k, v in cls.AVAILABLE_INDICATORS.items()}
