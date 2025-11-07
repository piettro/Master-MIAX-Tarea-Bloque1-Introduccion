"""
Quickstart: Complete Portfolio Analysis Process Demonstration

This module demonstrates the end-to-end process of portfolio analysis using
multiple design patterns to ensure flexibility, extensibility, and maintainability.

Design Patterns:
    - Factory Method: Data source selection and instantiation
    - Strategy: Different data extraction and cleaning strategies
    - Facade: Simplified interface for complex data operations
    - Observer: Data processing and statistics monitoring
    - Chain of Responsibility: Data cleaning pipeline

Key Features:
    - Data download from multiple sources
    - Time series creation and manipulation
    - Portfolio construction
    - Analysis report generation
    - Data quality assessment
    - Statistical analysis

Technical Process:
    1. Data extraction setup
    2. Market data retrieval
    3. Statistical analysis
    4. Data cleaning
    5. Missing data handling
"""
from datetime import datetime
from numpy import DataSource
from src.extractor.prices_extractor import MarketDataExtractor, DataSource
from src.extractor.sources.prices.extractor_prices_base import Interval

def main():
    """
    Execute the main demonstration workflow of market data extraction and analysis.
    
    This function implements multiple design patterns to showcase the complete
    workflow of market data handling and analysis.
    
    Design Pattern Implementation:
        - Factory Method: Data extractor creation
        - Strategy: Data source selection
        - Facade: Simplified data operations
        - Observer: Data processing monitoring
        
    Process Flow:
        1. Extractor initialization
        2. Configuration setup
        3. Data retrieval
        4. Statistical analysis
        5. Data cleaning
        6. Results presentation
    """
    # Initialize market data extractor using Factory pattern
    extractor = MarketDataExtractor()

    # Configure extraction parameters
    symbols = ['AEP','AAPL','MSFT','GOOGL','AMZN']  # Major tech companies
    start_date = datetime(2020, 11, 5)  # 5-year historical data
    end_date = datetime(2025, 11, 5)    # Current date
    source = DataSource.YAHOO   # Selected data source

    # Fetch price data using Strategy pattern for data retrieval
    data = extractor.fetch_price_series(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        source=source,
        interval=Interval.MONTHLY  # Monthly data granularity
    )
    print(f"Initial DataFrame from {source.value}:")
    print(data.head())

    # Compute comprehensive statistics using Observer pattern
    data_statistics = extractor.compute_data_statistics(data)
    
    # Display basic statistical measures
    print("\nBasic Statistical Measures:")
    print(data_statistics['basic_stats'])

    # Analyze missing data patterns
    print("\nMissing Data Analysis:")
    print(data_statistics['missing_data'])

    # Assess data quality metrics
    print("\nData Quality Assessment:")
    print(data_statistics['data_quality'])

    # Display value distribution analysis
    print("\nValue Distribution Analysis:")
    print(data_statistics['value_counts'])

    # Retrieve source metadata using Factory pattern
    print(f"\nData Source Information ({source.value}):")
    source_info = extractor.get_source_info(source)
    print(source_info)

    # Apply data cleaning using Chain of Responsibility pattern
    data = extractor.clean_price_data(data)
    print(f"\nCleaned DataFrame ({source.value}):")
    print(data.head())

    # Handle missing data using Strategy pattern
    data = extractor.handle_missing_data(
        data, 
        method='ffill'  # Forward fill strategy
    )
    print(f"\nDataFrame after missing data treatment ({source.value}):")
    print(data.head())

if __name__ == "__main__":
    main()
