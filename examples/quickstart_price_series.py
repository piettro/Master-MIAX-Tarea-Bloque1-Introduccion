"""
Quickstart: Time Series Price Analysis System

This module demonstrates a comprehensive price series analysis workflow,
implementing multiple design patterns for robust financial data analysis.

Design Patterns:
    - Factory Method: Price series and extractor creation
    - Strategy: Data source selection and analysis methods
    - Observer: Time series monitoring and metrics
    - Template Method: Analysis workflow standardization
    - Builder: Series and report construction
    - Chain of Responsibility: Data processing pipeline

Key Features:
    - Market data extraction
    - Time series construction
    - Price analysis
    - Returns calculation
    - Statistical measures
    - Report generation

Technical Process:
    1. Data extractor setup
    2. Series initialization
    3. Price data retrieval
    4. Market value analysis
    5. Returns calculation
    6. Statistical analysis
    7. Report compilation

Components:
    - Market Data Extractor: Data acquisition
    - Price Series: Time series handling
    - Statistical Engine: Data analysis
    - Report Generator: Results presentation
"""

from datetime import datetime
import pandas as pd
from src.core.entities.price_series import PriceSeries
from src.core.entities.portfolio import Portfolio
from src.extractor.prices_extractor import MarketDataExtractor
from src.extractor.sources.prices.extractor_prices_base import Interval, DataSource
from src.reports.report_price_series import PriceSeriesReport

def main():
    """
    Execute the complete price series analysis workflow.
    
    This function implements multiple design patterns to orchestrate
    the entire analysis process from data acquisition to report generation.
    
    Design Pattern Implementation:
        - Factory Method: Component creation
        - Strategy: Analysis methodology
        - Observer: Data monitoring
        - Template Method: Analysis workflow
        - Chain of Responsibility: Data processing
        
    Process Flow:
        1. Extractor initialization
        2. Symbol selection
        3. Time series creation
        4. Data analysis
        5. Report generation
        
    Error Handling:
        - Exception management
        - Process validation
        - Error reporting
    """
    try:
        # Initialize data extractor using Factory pattern
        print("Initializing market data extractor...")
        extractor = MarketDataExtractor()

        # Example of full market coverage (commented for demonstration)
        '''
        symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',  # Technology sector
            'JPM', 'BAC', 'WFC', 'GS', 'MS',          # Financial sector
            'JNJ', 'PFE', 'UNH', 'MRK', 'ABBV',       # Healthcare sector
            'XOM', 'CVX', 'COP', 'SLB', 'EOG',        # Energy sector
            'PG', 'KO', 'PEP', 'WMT', 'COST'          # Consumer sector
        ]
        '''
        # Selected symbols for demonstration (diversified portfolio)
        symbols = [
            'GOOGL',  # Technology
            'JPM',    # Financial
            'MRK',    # Healthcare
            'XOM',    # Energy
            'WMT',    # Consumer
            '^GSPC'   # S&P 500 Index   
        ]
        
        # Configure analysis parameters using Strategy pattern
        start_date = datetime(2020, 1, 1)  # Recent historical period
        end_date = datetime(2025, 11, 5)   # Current date
        source = DataSource.YAHOO          # Market data provider

        # Initialize price series using Factory and Builder patterns
        price_series = PriceSeries(
            name='Quickstart Price Series', # Series identifier
            symbols=symbols,                # Selected market symbols
            start_date=start_date,          # Analysis start date
            end_date=end_date,             # Analysis end date
            source=source,                 # Data source strategy
            interval=Interval.MONTHLY      # Time series frequency
        )

        # Display analysis configuration using Observer pattern
        print("\nTime Series Analysis Summary:")
        print(f"Analysis Period: {price_series.data.index.min()} to {price_series.data.index.max()}")
        print(f"Number of Assets: {len(symbols)}")
        print(f"Time Series Length: {len(price_series.data)} observations")
        
        print("\nHistorical Price Sample:")
        print(price_series.data.head())

        # Calculate market metrics using Strategy pattern
        print("\nCalculating Market Analytics...")
        
        # Market value analysis using Observer pattern
        print("\nMarket Value Analysis:")
        market_value = price_series.get_market_value()
        print(market_value)

        # Returns calculation using Template Method
        print("\nReturns Analysis:")
        returns = price_series.get_returns()
        print(returns)
        
        # Statistical analysis using Chain of Responsibility
        print("\nStatistical Summary:")
        describe = price_series.describe()
        print(describe)
   
        # Generate comprehensive report using Builder pattern
        print("\nGenerating Price Series Analysis Report...")
        report = PriceSeriesReport(price_series)
        report.generate()
        print("\nReport Generation Completed Successfully!")
        
    except Exception as e:
        # Handle errors using Chain of Responsibility pattern
        print(f"\nExecution Error: {str(e)}")
        raise

if __name__ == "__main__":
    # Execute main analysis workflow
    main()
