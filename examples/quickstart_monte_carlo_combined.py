"""
Quickstart: Combined Monte Carlo Portfolio Analysis Process

This module demonstrates a comprehensive portfolio analysis workflow using
Monte Carlo simulation with multiple combined strategies. It implements
various design patterns for robust and flexible analysis.

Design Patterns:
    - Strategy: Different Monte Carlo simulation approaches
    - Template Method: Standardized simulation process
    - Factory Method: Portfolio and series creation
    - Observer: Data monitoring and collection
    - Chain of Responsibility: Analysis pipeline
    - Composite: Combined simulation strategies
    
Key Features:
    - Data acquisition from multiple sources
    - Time series construction
    - Portfolio assembly and management
    - Combined Monte Carlo simulation
    - Comprehensive analysis reports
    - Multiple strategy integration

Technical Process:
    1. Data extraction configuration
    2. Portfolio construction
    3. Time series analysis
    4. Monte Carlo simulation
    5. Report generation
"""

from datetime import datetime
import pandas as pd
from src.analysis.entities.monte_carlo_combined import MonteCarloCombined
from src.core.entities.portfolio import Portfolio
from src.extractor.sources.prices.extractor_prices_base import Interval, DataSource
from src.reports.report_monte_carlo import MonteCarloReport

def main():
    """
    Execute the complete combined Monte Carlo analysis workflow.
    
    This function implements multiple design patterns to orchestrate
    the entire analysis process from data acquisition to report generation.
    
    Design Pattern Implementation:
        - Strategy: Multiple simulation strategies combination
        - Template Method: Standardized analysis workflow
        - Factory Method: Object creation and management
        - Observer: Progress monitoring and data collection
        - Composite: Combined analysis approach
        
    Process Flow:
        1. Configuration setup
        2. Data acquisition
        3. Portfolio construction
        4. Combined simulation execution
        5. Report generation
        
    Error Handling:
        - Exception catching and reporting
        - Graceful error management
        - Process validation
    """
    try:
        # Example of full market sector coverage (commented for quick demo)
        '''
        symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',  # Technology sector
            'JPM', 'BAC', 'WFC', 'GS', 'MS',          # Financial sector
            'JNJ', 'PFE', 'UNH', 'MRK', 'ABBV',       # Healthcare sector
            'XOM', 'CVX', 'COP', 'SLB', 'EOG',        # Energy sector
            'PG', 'KO', 'PEP', 'WMT', 'COST'          # Consumer sector
        ]
        '''
        # Selected representative symbols for demonstration
        symbols = [
            'MSFT',  # Technology
            'WFC',   # Financial
            'SLB',   # Energy
            'PFE',   # Healthcare
            'COST'   # Consumer
        ]
        
        # Configure analysis parameters using Strategy pattern
        start_date = datetime(2000, 1, 1)  # Long-term historical analysis
        end_date = datetime(2025, 11, 5)   # Current date
        source = DataSource.YAHOO          # Data source strategy

        # Create portfolio using Factory and Builder patterns
        portfolio = Portfolio(
            name='Quickstart Portfolio',
            holdings=symbols,              # Selected market symbols
            quantity=1000,                 # Standard position size
            start_date=start_date,
            end_date=end_date,
            source=source,
            interval=Interval.MONTHLY      # Monthly data granularity
        )
        
        # Retrieve price data using Strategy pattern
        data = portfolio.get_prices()
        print(data)

        # Display basic analysis information using Observer pattern
        print("\nData Summary:")
        print(f"Period: {data.index.min()} to {data.index.max()}")
        print(f"Number of assets: {len(symbols)}")
        print(f"Number of observations: {len(data)}")
        
        print("\nData Sample (First Rows):")
        print(data.head())

        # Initialize combined Monte Carlo simulation using Composite pattern
        monte_carlo_portfolio = MonteCarloCombined(
            portfolio=portfolio  # Target portfolio for analysis
        )

        # Execute simulation using Template Method pattern
        monte_carlo_portfolio.run()

        # Generate comprehensive report using Builder pattern
        report = MonteCarloReport(
            simulation=monte_carlo_portfolio,
            title="Monte Carlo Simulation Combined - Quickstart Portfolio"
        )
        report.generate()

    except Exception as e:
        # Error handling using Chain of Responsibility pattern
        print(f"\nExecution error: {str(e)}")
        raise

if __name__ == "__main__":
    # Execute main analysis workflow
    main()
