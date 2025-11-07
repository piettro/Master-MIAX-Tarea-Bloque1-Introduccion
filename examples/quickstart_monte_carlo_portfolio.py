"""
Quickstart: Portfolio Monte Carlo Simulation Analysis

This module demonstrates a comprehensive portfolio analysis workflow using
Monte Carlo simulation. It implements multiple design patterns to ensure
robust and flexible portfolio analysis.

Design Patterns:
    - Strategy: Monte Carlo simulation approach selection
    - Template Method: Standardized simulation process
    - Factory Method: Portfolio and data extractor creation
    - Observer: Data monitoring and collection
    - Chain of Responsibility: Analysis pipeline
    - Builder: Report construction
    
Key Features:
    - Market data extraction
    - Time series analysis
    - Portfolio construction
    - Monte Carlo simulation
    - Risk analysis
    - Report generation

Technical Process:
    1. Data source configuration
    2. Portfolio initialization
    3. Time series construction
    4. Monte Carlo simulation
    5. Analysis and reporting
    
Components:
    - Market Data Extractor: Data acquisition
    - Portfolio: Asset management
    - Monte Carlo Simulator: Risk analysis
    - Report Generator: Results presentation
"""

from datetime import datetime
import pandas as pd
from src.analysis.entities.monte_carlo_portfolios import MonteCarloPortfolio
from src.core.entities.portfolio import Portfolio
from src.extractor.sources.prices.extractor_prices_base import Interval, DataSource
from src.reports.report_monte_carlo import MonteCarloReport

def main():
    """
    Execute the complete portfolio Monte Carlo analysis workflow.
    
    This function implements multiple design patterns to orchestrate
    the entire analysis process from data acquisition to report generation.
    
    Design Pattern Implementation:
        - Strategy: Simulation methodology selection
        - Template Method: Analysis workflow standardization
        - Factory Method: Component initialization
        - Observer: Data and process monitoring
        - Chain of Responsibility: Analysis pipeline
        
    Process Flow:
        1. Configuration setup
        2. Data extraction
        3. Portfolio construction
        4. Monte Carlo simulation
        5. Report generation
        
    Error Handling:
        - Comprehensive exception management
        - Process validation
        - Error reporting
    """
    try:
        # Complete market coverage example (commented for demonstration)
        '''
        symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',  # Technology sector
            'JPM', 'BAC', 'WFC', 'GS', 'MS',          # Financial sector
            'JNJ', 'PFE', 'UNH', 'MRK', 'ABBV',       # Healthcare sector
            'XOM', 'CVX', 'COP', 'SLB', 'EOG',        # Energy sector
            'PG', 'KO', 'PEP', 'WMT', 'COST'          # Consumer sector
        ]
        '''
        # Selected symbols for demonstration (cross-sector representation)
        symbols = [
            'MSFT',  # Technology
            'WFC',   # Financial
            'SLB',   # Energy
            'PFE',   # Healthcare
            'COST'   # Consumer
        ]
        
        # Configure analysis timeframe and data source using Strategy pattern
        start_date = datetime(2000, 1, 1)  # Extended historical period
        end_date = datetime(2025, 11, 5)   # Current date
        source = DataSource.YAHOO          # Selected data provider

        # Initialize portfolio using Factory and Builder patterns
        portfolio = Portfolio(
            name='Quickstart Portfolio',    # Portfolio identifier
            holdings=symbols,               # Selected market symbols
            quantity=1000,                  # Position size per holding
            start_date=start_date,          # Analysis start date
            end_date=end_date,             # Analysis end date
            source=source,                 # Data source strategy
            interval=Interval.MONTHLY      # Data granularity
        )
        
        # Extract price data using Strategy pattern
        data = portfolio.get_prices()
        print(data)

        # Display portfolio analysis information using Observer pattern
        print("\nData Analysis Summary:")
        print(f"Analysis Period: {data.index.min()} to {data.index.max()}")
        print(f"Portfolio Assets: {len(symbols)}")
        print(f"Time Series Length: {len(data)}")
        
        print("\nPrice Data Sample:")
        print(data.head())

        # Initialize Monte Carlo simulation using Strategy pattern
        monte_carlo_portfolio = MonteCarloPortfolio(
            portfolio=portfolio 
        )

        # Execute simulation using Template Method pattern
        monte_carlo_portfolio.run()

        # Generate analysis report using Builder pattern
        report = MonteCarloReport(
            simulation=monte_carlo_portfolio,
            title="Monte Carlo Simulation Report - Quickstart Portfolio"
        )
        
        # Generate comprehensive report using Chain of Responsibility
        report.generate()

    except Exception as e:
        # Handle errors using Chain of Responsibility pattern
        print(f"\nExecution Error: {str(e)}")
        raise

if __name__ == "__main__":
    # Execute main analysis workflow
    main()
