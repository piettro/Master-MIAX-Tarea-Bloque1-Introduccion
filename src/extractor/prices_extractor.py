"""
Financial data extraction module that coordinates multiple data sources.
Implements Factory pattern for creating extractors and Facade pattern for simplified API.
"""

from typing import List, Dict, Union, Optional
from datetime import datetime
import pandas as pd
from enum import Enum

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
    Facade for extracting financial market data from multiple sources.
    Implements Factory pattern for creating specific extractors.
    """
    
    def __init__(self):
        """Initialize the market data extractor with available data sources."""
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
        
        Parameters
        ----------
        symbols : Union[str, List[str]]
            Single symbol or list of symbols to fetch
        start_date : datetime
            Start date for the data range
        end_date : datetime
            End date for the data range
        source : DataSource
            Data source to use
        interval : Interval, optional
            Data interval, by default Interval.DAILY
            
        Returns
        -------
        pd.DataFrame
            Processed price data with standardized format
            
        Raises
        ------
        ValueError
            If source is not available or parameters are invalid
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
               
        return data
        
    def compute_data_statistics(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Compute comprehensive statistics and data quality metrics of the price data.
        
        Parameters
        ----------
        data : pd.DataFrame
            Price data to analyze
            
        Returns
        -------
        Dict[str, pd.DataFrame]
            Dictionary containing multiple DataFrames with different analyses:
            - 'basic_stats': Basic statistical measures (mean, std, etc.)
            - 'missing_data': Missing data analysis
            - 'value_counts': Unique values count and frequency
            - 'data_quality': Quality metrics (completeness, consistency)
        """
        analysis = {}
        
        # 1. Basic Statistics
        analysis['basic_stats'] = data.describe(include='all').transpose()
        
        # Missing Data
        missing_data = pd.DataFrame({
            'missing_count': data.isnull().sum(),
            'missing_percentage': (data.isnull().sum() / len(data) * 100).round(2),
            'total_rows': len(data),
            'complete_rows': len(data.dropna())
        })
        analysis['missing_data'] = missing_data
        
        # Value Counts
        value_counts = pd.DataFrame({
            'unique_values': data.nunique(),
            'unique_percentage': (data.nunique() / len(data) * 100).round(2)
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
            quality_metrics.loc['price_relationships', 'invalid_percentage'] = (
                invalid_prices.sum() / len(data) * 100
            ).round(2)
        
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
                quality_metrics.loc['time_series', 'gaps_percentage'] = (
                    len(gaps) / len(ideal_index) * 100
                ).round(2)
        
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
        
        print('oi 4')
        df['Volume'] = df['Volume'].fillna(0).astype(int)
        
        return df

    def handle_missing_data(
        self,
        data: pd.DataFrame,
        method: str = 'ffill'
    ) -> pd.DataFrame:
        """
        Handle missing data in the price series.
        
        Parameters
        ----------
        data : pd.DataFrame
            Price data to clean
        method : MissingDataMethod
            Method to use for handling missing data
            
        Returns
        -------
        pd.DataFrame
            Data with missing values handled
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
        Handle outliers in the price series.
        
        Parameters
        ----------
        data : pd.DataFrame
            Price data to clean
        method : OutlierMethod
            Method to use for detecting outliers
        threshold : float, optional
            Threshold for outlier detection, by default 3.0
            
        Returns
        -------
        pd.DataFrame
            Data with outliers handled
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
                
        # Fill NaN values created by outlier removal using forward fill
        clean_data = clean_data.ffill().bfill()
        
        return clean_data
    
    @property
    def available_sources(self) -> List[str]:
        """List all available data sources."""
        return [source.value for source in DataSource]
    
    def get_source_info(self, source: DataSource) -> Dict:
        """
        Get information about a specific data source.
        
        Parameters
        ----------
        source : DataSource
            Data source to get information for
            
        Returns
        -------
        Dict
            Information about the data source including:
            - Supported intervals
            - Rate limits
            - API documentation URL
            - etc.
        """
        if not isinstance(source, DataSource):
            raise ValueError(f"Invalid source. Must be one of: {[s.value for s in DataSource]}")
            
        extractor = self._extractors[source]
        return extractor.get_source_info()