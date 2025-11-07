"""
Financial data extraction module that coordinates multiple data sources.
Implements Factory pattern for creating extractors and Facade pattern for simplified API.
"""

from typing import List, Dict, Union
from datetime import datetime
import pandas as pd
from src.extractor.sources.prices.extractor_yahoo import YahooExtractor
from src.extractor.sources.prices.extractor_eodhd import EODHDExtractor
from src.extractor.sources.prices.extractor_fmp import FMPExtractor
from src.extractor.sources.prices.extractor_alphavantage import AlphaVantageExtractor
from src.extractor.sources.prices.extractor_prices_base import (
    BaseExtractor,
    Interval,
    DataSource
)

class MarketDataExtractor:
    """
    A comprehensive facade for extracting and processing financial market data.
    
    This class serves as the main entry point for all market data operations,
    implementing multiple design patterns to provide a robust and flexible
    data extraction framework.
    
    Design Pattern Implementation:
        - Facade: Simplifies complex market data operations
        - Factory: Creates appropriate data source extractors
        - Strategy: Supports multiple data extraction strategies
        - Chain of Responsibility: Data processing pipeline
        - Template Method: Standard data handling procedures
    
    Key Components:
        - Multiple data source support
        - Automatic source selection and configuration
        - Data validation and cleaning
        - Quality metrics computation
        - Missing data and outlier handling
    """
    
    def __init__(self):
        """
        Initialize the market data extractor with all available data sources.
        
        This constructor implements multiple design patterns to set up the
        data extraction framework and initialize all available data sources.
        
        Design Pattern Implementation:
            - Factory: Sets up extractor creation system
            - Registry: Maintains mapping of sources to extractors
            - Strategy: Prepares multiple extraction strategies
            - Facade: Initializes unified interface
            
        The initialization process:
            1. Creates extractor registry
            2. Instantiates all available source extractors
            3. Maps data sources to their extractors
            4. Sets up the facade interface
        
        Note:
            Automatically handles API configuration for all sources
            and maintains singleton instances of extractors.
        """
        self._extractors: Dict[DataSource, BaseExtractor] = {
            DataSource.YAHOO: YahooExtractor(),
            DataSource.EODHD: EODHDExtractor(),
            DataSource.FMP: FMPExtractor(),
            DataSource.ALPHA_VANTAGE: AlphaVantageExtractor()
        }
    
    def fetch_price_series(
        self,
        symbols: Union[str, List[str]],
        start_date: datetime,
        end_date: datetime,
        source: DataSource,
        interval: Interval
    ) -> pd.DataFrame:
        """
        Fetch historical price series from a specific data source.
        
        This method implements multiple design patterns to provide a unified
        interface for data extraction while handling the complexity of
        different data sources and formats.
        
        Design Pattern Implementation:
            - Facade: Simplifies complex extraction process
            - Factory: Creates/uses appropriate extractor
            - Strategy: Uses source-specific extraction strategy
            - Template Method: Follows standard extraction steps
        
        Process Flow:
            1. Validate input parameters
            2. Select appropriate extractor
            3. Execute data extraction
            4. Validate and clean results
            5. Return standardized data
        
        Parameters
        ----------
        symbols : Union[str, List[str]]
            Single symbol (e.g., 'AAPL') or list of symbols (['AAPL', 'MSFT'])
        start_date : datetime
            Start date for historical data range
        end_date : datetime
            End date for historical data range
        source : DataSource
            Data source enumeration (e.g., DataSource.YAHOO)
        interval : Interval
            Data interval enumeration (e.g., Interval.DAILY)
            
        Returns
        -------
        pd.DataFrame
            Processed price data with standardized format:
            - MultiIndex columns (Price type, Symbol)
            - DateTimeIndex for timestamps
            - Required columns: Open, High, Low, Close, Volume
            
        Raises
        ------
        ValueError
            - If source is not available
            - If parameters are invalid
            - If symbols are not found
        RuntimeError
            - If extraction fails
            - If data validation fails
            
        Examples
        --------
        >>> extractor = MarketDataExtractor()
        >>> data = extractor.fetch_price_series(
        ...     symbols='AAPL',
        ...     start_date=datetime(2020, 1, 1),
        ...     end_date=datetime(2020, 12, 31),
        ...     source=DataSource.YAHOO,
        ...     interval=Interval.DAILY
        ... )
        >>> print(data.head())
        """
        if not isinstance(source, DataSource):
            raise ValueError(
                f"Invalid source. Must be one of: {[s.value for s in DataSource]}"
            )
        
        extractor = self._extractors[source]
        data = extractor.extract_data(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            interval=interval.value
        )

        # Validate DataFrame structure
        if not isinstance(data.columns, pd.MultiIndex):
            raise ValueError("Data must have a MultiIndex with (Price, Ticker) levels")
            
        if len(data.columns.levels) != 2:
            raise ValueError("MultiIndex must have exactly 2 levels: Price and Ticker")
            
        # Validate required price types
        required_columns = {'Open', 'High', 'Low', 'Close', 'Volume'}
        price_types = set(data.columns.get_level_values(0).unique())
        missing = required_columns - price_types
        if missing:
            raise ValueError(f"Missing required price types: {missing}")
            
        # Validate data types for each ticker
        for ticker in data.columns.get_level_values(1).unique():
            # Validate numeric columns for each price type
            for price_type in required_columns:
                if not pd.api.types.is_numeric_dtype(data[price_type, ticker]):
                    raise TypeError(f"{price_type} must be numeric type for ticker {ticker}")
                    
            # Validate price consistency for each ticker
            ticker_data = data.xs(ticker, axis=1, level=1)
            invalid_prices = ticker_data[
                (ticker_data['High'] < ticker_data['Low']) |
                (ticker_data['Close'] < ticker_data['Low']) |
                (ticker_data['Close'] > ticker_data['High']) |
                (ticker_data['Open'] < ticker_data['Low']) |
                (ticker_data['Open'] > ticker_data['High'])
            ]
            
            if not invalid_prices.empty:
                f"Invalid price relationships found for {ticker} at dates: "
                f"{invalid_prices.index.strftime('%Y-%m-%d').tolist()}"
                  
        return data
        
    def compute_data_statistics(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Compute comprehensive statistics and data quality metrics for price data.
        
        This method implements the Strategy pattern for data analysis, providing
        multiple analytical approaches and metrics computation strategies. It
        follows the Chain of Responsibility pattern for sequential analysis steps.
        
        Design Pattern Implementation:
            - Strategy: Multiple analysis strategies
            - Chain of Responsibility: Sequential analysis steps
            - Template Method: Standard analysis procedure
            
        Analysis Components:
            1. Basic Statistical Measures
               - Mean, standard deviation, min/max
               - Quartiles and median
               - Value distribution
               
            2. Missing Data Analysis
               - Missing value counts
               - Missing data patterns
               - Completeness metrics
               
            3. Value Distribution
               - Unique value counts
               - Frequency analysis
               - Distribution patterns
               
            4. Data Quality Metrics
               - Completeness scores
               - Consistency checks
               - Validity measures
        
        Parameters
        ----------
        data : pd.DataFrame
            Price data to analyze, expected to contain:
            - OHLCV columns
            - DateTimeIndex
            - Possibly multiple symbols
            
        Returns
        -------
        Dict[str, pd.DataFrame]
            Comprehensive analysis results:
            - 'basic_stats': Statistical measures
                * mean, std, min, max, quartiles
            - 'missing_data': Missing data analysis
                * count, percentage, patterns
            - 'value_counts': Distribution analysis
                * unique values, frequencies
            - 'data_quality': Quality metrics
                * completeness, consistency, validity
                
        Examples
        --------
        >>> stats = extractor.compute_data_statistics(price_data)
        >>> print(stats['basic_stats'])
        >>> print(stats['data_quality'])
        
        Notes
        -----
        The analysis adapts to both single-symbol and multi-symbol datasets,
        providing appropriate metrics for each case.
        """
        analysis = {}
        
        # Basic Statistics
        analysis['basic_stats'] = data.describe(include='all').transpose()
        
        # Missing Data
        missing_data = pd.DataFrame({
            'missing_count': data.isnull().sum(),
            'missing_percentage': round(data.isnull().sum() / len(data) * 100,2),
            'total_rows': len(data),
            'complete_rows': len(data.dropna())
        })
        analysis['missing_data'] = missing_data
        
        # Value Counts
        value_counts = pd.DataFrame({
            'unique_values': data.nunique(),
            'unique_percentage': round(data.nunique() / len(data) * 100,2)
        })
        analysis['value_counts'] = value_counts
        
        # Quality Metrics
        quality_metrics = pd.DataFrame(index=data.columns)
        quality_metrics['completeness'] = (1 - data.isnull().mean()) * 100

        def check_column_type_consistency(column):
            if len(column) == 0:
                return True
            
            column_type = column.dtype
            non_null_values = column.dropna()
            
            if len(non_null_values) == 0:
                return True
            try:
                pd.Series(non_null_values).astype(column_type)
                return True
            except (ValueError, TypeError):
                return False
        
        quality_metrics['consistent_types'] = data.apply(check_column_type_consistency)
        
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            col_exists = any(col in level for level in data.columns.levels) if isinstance(data.columns, pd.MultiIndex) else col in data.columns
            if col_exists:
                if isinstance(data.columns, pd.MultiIndex):
                    target_cols = [c for c in data.columns if col in c]
                else:
                    target_cols = [col]
                
                has_negatives = False
                for target_col in target_cols:
                    if data[target_col].dtype in ['int64', 'float64']:
                        if (data[target_col] < 0).any():
                            has_negatives = True
                            break
                
                quality_metrics.loc[col, 'has_negatives'] = has_negatives if target_cols else None
        
        if all(col in data.columns for col in ['High', 'Low', 'Open', 'Close']):
            invalid_prices = (
                (data['High'] < data['Low']) |
                (data['Close'] < data['Low']) |
                (data['Close'] > data['High']) |
                (data['Open'] < data['Low']) |
                (data['Open'] > data['High'])
            )
            quality_metrics.loc['price_relationships', 'invalid_count'] = invalid_prices.sum()
            quality_metrics.loc['price_relationships', 'invalid_percentage'] = round(
                invalid_prices.sum() / len(data) * 100,2
            )
        
        if isinstance(data.index, pd.DatetimeIndex):
            expected_freq = pd.infer_freq(data.index)
            if expected_freq:
                ideal_index = pd.date_range(
                    start=data.index.min(),
                    end=data.index.max(),
                    freq=expected_freq
                )
                gaps = ideal_index.difference(data.index)
                quality_metrics.loc['time_series', 'gaps_count'] = len(gaps)
                quality_metrics.loc['time_series', 'gaps_percentage'] = round(
                    len(gaps) / len(ideal_index) * 100,2
                )
        
        analysis['data_quality'] = quality_metrics
        
        return analysis

    def clean_price_data(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Clean and validate price data.
        
        Parameters
        ----------
        df : pd.DataFrame
            Raw price data to clean
        symbol : str
            Symbol for the data being cleaned
        fill_method : str, optional
            Method for filling missing values, by default 'ffill'
            
        Returns
        -------
        pd.DataFrame
            Cleaned price data
            
        Raises
        ------
        ValueError
            If data validation fails
        """
        if df.empty:
            raise ValueError(f"No data available")
        
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns.levels[0]]

        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        df = df.sort_index()
        df = df[~df.index.duplicated(keep='first')]
        
        if isinstance(df.columns, pd.MultiIndex):
            invalid_mask = pd.DataFrame(False, index=df.index, columns=df.columns.levels[1].unique())
            
            for symbol in df.columns.levels[1].unique():
                try:
                    invalid_prices = (
                        (df[('High', symbol)] < df[('Low', symbol)]) |
                        (df[('Close', symbol)] < df[('Low', symbol)]) |
                        (df[('Close', symbol)] > df[('High', symbol)]) |
                        (df[('Open', symbol)] < df[('Low', symbol)]) |
                        (df[('Open', symbol)] > df[('High', symbol)])
                    )
                    invalid_mask[symbol] = invalid_prices
                except KeyError:
                    continue 
            
            valid_rows = ~invalid_mask.any(axis=1)
            df = df.loc[valid_rows]
        
        df['Volume'] = df['Volume'].fillna(0).astype(int)
        
        return df

    def handle_missing_data(
        self,
        data: pd.DataFrame,
        method: str = 'ffill'
    ) -> pd.DataFrame:
        """
        Handle missing data in the price series using various strategies.
        
        This method implements the Strategy pattern to provide multiple
        approaches for handling missing data, allowing flexible selection
        of the appropriate strategy based on data characteristics.
        
        Design Pattern Implementation:
            - Strategy: Multiple missing data handling strategies
            - Template Method: Standard processing steps
            - Chain of Responsibility: Part of data cleaning pipeline
            
        Available Strategies:
            - 'ffill': Forward fill (last observation carried forward)
            - 'bfill': Backward fill (next observation carried backward)
            - 'linear': Linear interpolation between valid points
            - 'drop': Remove rows with missing values
            
        Parameters
        ----------
        data : pd.DataFrame
            Price data containing missing values
        method : str, default='ffill'
            Strategy to use for handling missing data:
            - 'ffill': Forward fill
            - 'bfill': Backward fill
            - 'linear': Linear interpolation
            - 'drop': Remove missing values
            
        Returns
        -------
        pd.DataFrame
            Data with missing values handled according to chosen strategy
            
        Examples
        --------
        >>> clean_data = extractor.handle_missing_data(
        ...     data, method='linear'
        ... )
        
        Notes
        -----
        The choice of method can significantly impact analysis results.
        Consider the nature of your data when selecting a strategy.
        """
        if method == 'ffill':
            return data.ffill()
        elif method == 'bfill':
            return data.bfill()
        elif method == 'linear':
            return data.interpolate(method='linear')
        elif method == 'drop':
            return data.dropna()
        else:
            return data
            
    def handle_outliers(
        self,
        data: pd.DataFrame,
        method: str = 'zscore',
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Handle outliers in the price series using statistical methods.
        
        This method implements the Strategy pattern to provide multiple
        approaches for outlier detection and handling. It's part of the
        data cleaning Chain of Responsibility.
        
        Design Pattern Implementation:
            - Strategy: Multiple outlier detection methods
            - Chain of Responsibility: Data cleaning step
            - Template Method: Standard processing procedure
            
        Detection Methods:
            1. Z-Score Method:
               - Identifies values beyond standard deviation threshold
               - Assumes normal distribution
               - Configurable threshold
               
            2. IQR (Interquartile Range) Method:
               - Uses quartile-based detection
               - More robust to non-normal distributions
               - Configurable threshold multiplier
        
        Parameters
        ----------
        data : pd.DataFrame
            Price data potentially containing outliers
        method : str, default='zscore'
            Outlier detection method:
            - 'zscore': Standard deviation based
            - 'iqr': Interquartile range based
            - 'none': No outlier handling
        threshold : float, default=3.0
            Detection sensitivity:
            - For zscore: number of standard deviations
            - For IQR: multiplier of IQR
            
        Returns
        -------
        pd.DataFrame
            Data with outliers handled according to chosen strategy
            
        Examples
        --------
        >>> clean_data = extractor.handle_outliers(
        ...     data,
        ...     method='iqr',
        ...     threshold=1.5
        ... )
        
        Notes
        -----
        - Outliers are replaced with NaN and then filled
        - Consider your data distribution when choosing method
        - Adjust threshold based on acceptable risk levels
        """
        if method == 'none':
            return data
            
        clean_data = data.copy()
        
        for column in data.select_dtypes(include=['float64', 'int64']).columns:
            if method == 'zscore':
                z_scores = abs((data[column] - data[column].mean()) / data[column].std())
                mask = z_scores > threshold
                clean_data.loc[mask, column] = None
                
            elif method == 'iqe':
                Q1 = data[column].quantile(0.25)
                Q3 = data[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                mask = (data[column] < lower_bound) | (data[column] > upper_bound)
                clean_data.loc[mask, column] = None
                
        clean_data = clean_data.ffill().bfill()
        
        return clean_data
    
    @property
    def available_sources(self) -> List[str]:
        """List all available data sources."""
        return [source.value for source in DataSource]
    
    def get_source_info(self, source: DataSource) -> Dict:
        """
        Retrieve detailed information about a specific data source.
        
        This method implements the Facade pattern by providing a unified
        interface to access source-specific information. It delegates to
        the appropriate extractor's implementation.
        
        Design Pattern Implementation:
            - Facade: Unified access to source information
            - Strategy: Source-specific information retrieval
            - Factory: Uses created extractor instance
            
        Retrieved Information:
            - Supported data intervals
            - API rate limits and quotas
            - Authentication requirements
            - Documentation references
            - Special features and limitations
        
        Parameters
        ----------
        source : DataSource
            Enumerated data source identifier (e.g., DataSource.YAHOO)
            
        Returns
        -------
        Dict
            Comprehensive source information:
            - name: Source identifier
            - supported_intervals: Available time intervals
            - requires_api_key: Authentication requirements
            - rate_limits: Request limitations
            - documentation: API documentation URL
            - base_url: API endpoint base
            - features: Special capabilities
            
        Raises
        ------
        ValueError
            If the specified source is not available
            
        Notes
        -----
        Information structure may vary by source but always
        includes core capabilities and limitations.
        """
        if not isinstance(source, DataSource):
            raise ValueError(f"Invalid source. Must be one of: {[s.value for s in DataSource]}")
            
        extractor = self._extractors[source]
        return extractor.get_source_info()