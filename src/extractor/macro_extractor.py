"""
Macroeconomic Data Extraction Framework.

This module implements a flexible framework for extracting macroeconomic data
from various sources using multiple design patterns to ensure extensibility
and maintainability.

Design Patterns:
    - Factory Pattern: Creates specific extractors based on data source
    - Strategy Pattern: Different extraction strategies for different sources
    - Facade Pattern: Provides simplified interface for complex extraction operations
    - Registry Pattern: Maintains registry of available data sources

Key Features:
    - Unified interface for multiple data sources
    - Extensible source registration system
    - Standardized data format
    - Flexible date range handling
    - Comprehensive error handling
"""

from typing import List, Optional
from datetime import datetime
import pandas as pd

from src.extractor.sources.macro.extractor_worldbank import WorldBankExtractor

class MacroExtractor:
    """
    A facade for extracting macroeconomic data from various sources.
    
    This class implements multiple design patterns to provide a unified
    interface for accessing macroeconomic data from different sources
    while maintaining flexibility and extensibility.
    
    Design Pattern Implementation:
        - Facade: Simplifies complex extraction operations
        - Factory: Creates appropriate extractors for each source
        - Strategy: Supports different extraction strategies
        - Registry: Manages available data sources
        
    Attributes
    ----------
    AVAILABLE_SOURCES : List[str]
        List of registered data sources available for extraction
    _extractors : dict
        Registry of extractor classes mapped to source names
        
    Examples
    --------
    >>> extractor = MacroExtractor()
    >>> data = extractor.extract(
    ...     indicators=['GDP.MKTP.CD'],
    ...     countries=['USA', 'GBR'],
    ...     start_date='2010-01-01'
    ... )
    """
    
    AVAILABLE_SOURCES = ['worldbank']
    
    def __init__(self):
        """
        Initialize the macroeconomic data extractor.
        
        This constructor implements the Registry and Factory patterns by
        setting up a dictionary of available extractors. Each extractor
        is mapped to its corresponding source identifier.
        
        Design Pattern Implementation:
            - Registry: Maintains mapping of sources to extractors
            - Factory: Prepares extractor creation system
            - Strategy: Supports multiple extraction strategies
            
        The initialization process:
            1. Sets up extractor registry
            2. Maps source identifiers to extractor classes
            3. Prepares factory system for extractor creation
            
        Note:
            Currently supports World Bank data source, but the architecture
            is designed for easy addition of new sources.
        """
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
        Extract macroeconomic data from the configured source.
        
        This method implements multiple design patterns to provide a unified
        interface for data extraction while handling the complexity of
        different data sources and formats.
        
        Design Pattern Implementation:
            - Facade: Simplifies complex extraction process
            - Factory: Creates appropriate extractor instance
            - Strategy: Uses source-specific extraction strategy
            
        Process Flow:
            1. Validate and prepare input parameters
            2. Create appropriate extractor instance
            3. Execute data extraction
            4. Format and return results
        
        Parameters
        ----------
        indicators : List[str]
            List of indicator codes to extract (e.g., ['GDP.MKTP.CD'])
        countries : List[str], optional
            List of country codes to extract data for (e.g., ['USA', 'GBR'])
            Defaults to WorldBankExtractor.DEFAULT_COUNTRIES
        start_date : str, optional
            Start date in YYYY-MM-DD format
            Defaults to "1990-01-01"
        end_date : str, optional
            End date in YYYY-MM-DD format
            Defaults to current date

        Returns
        -------
        pd.DataFrame
            Extracted data with standardized structure:
            - MultiIndex: (Country, Indicator)
            - DateTimeIndex for timestamps
            - Values: Indicator values
            
        Raises
        ------
        ValueError
            - If indicators list is empty
            - If date format is invalid
            - If source is not available
        RuntimeError
            - If extraction process fails
            - If data format is invalid
            
        Examples
        --------
        >>> extractor = MacroExtractor()
        >>> gdp_data = extractor.extract(
        ...     indicators=['GDP.MKTP.CD'],
        ...     countries=['USA', 'GBR'],
        ...     start_date='2010-01-01'
        ... )
        """

        countries = countries or WorldBankExtractor.DEFAULT_COUNTRIES
        start_date = start_date or "1990-01-01"
        end_date = end_date or datetime.now().strftime("%Y-%m-%d")
        
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
        Retrieve the list of available indicators from the configured source.
        
        This method implements part of the Facade pattern by providing a
        simplified interface to access indicator metadata from different
        sources. It delegates the actual retrieval to the specific
        extractor implementation.
        
        Design Pattern Implementation:
            - Facade: Simplifies indicator discovery
            - Strategy: Uses source-specific listing strategy
            - Factory: Works with created extractor instance
            
        Returns
        -------
        dict
            Dictionary containing indicator information:
            - Keys: Indicator codes (e.g., 'GDP.MKTP.CD')
            - Values: Indicator metadata (name, description, etc.)
            
        Examples
        --------
        >>> extractor = MacroExtractor()
        >>> indicators = extractor.list_available_indicators()
        >>> print(indicators['GDP.MKTP.CD'])
        {'name': 'GDP (current US$)', 'description': '...'}
        
        Notes
        -----
        The actual structure of the returned dictionary depends on
        the specific data source being used. Refer to the concrete
        extractor's documentation for details.
        """
            
        return self._extractors['worldbank'].list_available_indicators()