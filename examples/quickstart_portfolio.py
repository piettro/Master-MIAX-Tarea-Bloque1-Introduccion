"""
Quickstart: Comprehensive Portfolio Analysis System

This module demonstrates a complete portfolio analysis workflow,
implementing multiple design patterns for robust financial analysis.

Design Patterns:
    - Factory Method: Portfolio and data extractor creation
    - Strategy: Data source selection and analysis methods
    - Observer: Portfolio monitoring and metrics
    - Template Method: Analysis workflow standardization
    - Builder: Portfolio and report construction
    - Chain of Responsibility: Analysis pipeline

Key Features:
    - Market data extraction
    - Time series creation
    - Portfolio construction
    - Performance analysis
    - Statistical metrics
    - Report generation

Technical Process:
    1. Data source configuration
    2. Portfolio initialization
    3. Price data retrieval
    4. Performance calculation
    5. Statistical analysis
    6. Report compilation

Components:
    - Market Data Extractor: Data acquisition
    - Portfolio: Asset management
    - Price Series: Time series handling
    - Report Generator: Results presentation
"""

from datetime import datetime
import pandas as pd
from src.core.entities.price_series import PriceSeries
from src.core.entities.portfolio import Portfolio
from src.extractor.prices_extractor import MarketDataExtractor
from src.extractor.sources.prices.extractor_prices_base import Interval, DataSource
from src.reports.report_portfolio import PortfolioReport
from src.reports.report_price_series import PriceSeriesReport

def main():
    """
    Execute the complete portfolio analysis workflow.
    
    This function implements multiple design patterns to orchestrate
    the entire analysis process from data acquisition to report generation.
    
    Design Pattern Implementation:
        - Factory Method: Component instantiation
        - Strategy: Analysis methodology selection
        - Observer: Portfolio monitoring
        - Template Method: Analysis workflow
        - Chain of Responsibility: Data processing
        
    Process Flow:
        1. Symbol selection
        2. Data extraction
        3. Portfolio construction
        4. Performance analysis
        5. Report generation
        
    Error Handling:
        - Exception management
        - Process validation
        - Error reporting
    """
    try:
        # Full market coverage example (commented for demonstration)
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
            'MSFT',  # Technology representation
            'WFC',   # Financial sector
            'SLB',   # Energy sector
            'PFE',   # Healthcare sector
            'COST'   # Consumer sector
        ]
        
        # Configure analysis parameters using Strategy pattern
        start_date = datetime(2000, 1, 1)  # Extended historical period
        end_date = datetime(2025, 11, 5)   # Current date
        source = DataSource.YAHOO          # Data source strategy

        # Initialize portfolio using Factory and Builder patterns
        portfolio = Portfolio(
            name='Quickstart Portfolio',    # Portfolio identifier
            holdings=symbols,               # Selected market symbols
            quantity=1000,                  # Position size per holding
            start_date=start_date,          # Analysis start date
            end_date=end_date,             # Analysis end date
            source=source,                 # Data source strategy
            interval=Interval.MONTHLY      # Analysis frequency
        )
        
        # Extract price data using Strategy pattern
        data = portfolio.get_prices()
        print(data)

        # Display portfolio analysis information using Observer pattern
        print("\nPortfolio Analysis Summary:")
        print(f"Analysis Period: {data.index.min()} to {data.index.max()}")
        print(f"Portfolio Size: {len(symbols)} assets")
        print(f"Data Points: {len(data)} observations")
        
        print("\nHistorical Price Sample:")
        print(data.head())

        # Calculate portfolio metrics using Strategy pattern
        print("\nCalculating Portfolio Metrics...")
        
        # Asset allocation analysis using Observer pattern
        print("\nPortfolio Weights Distribution:")
        market_value = portfolio.weights()
        print(market_value)

        # Individual holdings analysis using Template Method
        print("\nTotal Value by Asset:")
        returns = portfolio.total_value_per_holding()
        print(returns)
        
        # Portfolio valuation using Chain of Responsibility
        print("\nAggregate Portfolio Value:")
        describe = portfolio.total_value()
        print(describe)

        # Performance analysis using Strategy pattern
        print("\nPortfolio Returns Analysis:")
        describe = portfolio.returns()
        print(describe)
   
        # Generate comprehensive report using Builder pattern
        print("\nGenerating Portfolio Analysis Report...")
        report = PortfolioReport(portfolio)
        report.generate()
        print("\nReport Generation Completed Successfully!")
        
    except Exception as e:
        # Handle errors using Chain of Responsibility pattern
        print(f"\nExecution Error: {str(e)}")
        raise

if __name__ == "__main__":
    # Execute main analysis workflow
    main()
