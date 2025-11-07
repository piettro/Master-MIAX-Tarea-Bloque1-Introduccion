"""
Quickstart: Macroeconomic Data Analysis and Visualization

This module demonstrates the usage of macroeconomic data functionality with
visualizations and report generation using multiple design patterns.

Design Patterns:
    - Factory Method: Data extractor creation and management
    - Strategy: Different data extraction strategies per source
    - Observer: Data processing and monitoring
    - Builder: Report construction
    - Facade: Simplified interface for complex operations

Key Features:
    - Macroeconomic data extraction
    - Multi-country analysis
    - Multiple indicator handling
    - Automated report generation
    - Data visualization
    - Time series analysis

Technical Process:
    1. Data source initialization
    2. Indicator selection
    3. Data extraction
    4. Series creation
    5. Report generation
"""

from datetime import datetime
import pandas as pd

from src.core.entities.macro_series import MacroSeries
from src.extractor.macro_extractor import MacroExtractor
from src.reports.report_macro import MacroReport

def main():
    """
    Execute the main demonstration workflow for macroeconomic data analysis.
    
    This function implements multiple design patterns to showcase the complete
    workflow of macroeconomic data handling and analysis.
    
    Design Pattern Implementation:
        - Factory Method: Extractor instantiation
        - Strategy: Data retrieval approaches
        - Builder: Series construction
        - Observer: Data processing monitoring
        
    Process Flow:
        1. Extractor initialization
        2. Indicator discovery
        3. Data configuration
        4. Series creation
        5. Report generation
    """
    print("\n=== Quickstart: Macroeconomic Data Analysis ===")

    # Initialize data extraction using Factory pattern
    print("\n1. Extracting macroeconomic data...")
    
    extractor = MacroExtractor()
    indicators = extractor.list_available_indicators()
    print(f"Available indicators: {len(indicators)}")

    # Display sample of available indicators
    for name, code in list(indicators.items())[:5]:
        print(f"- {name}: {code}")

    # Configure data selection using Strategy pattern
    selected_indicators = [
        "GDP growth (annual %)",
        "Inflation, GDP deflator (annual %)",
        "Exports of goods and services (% of GDP)",
        "Imports of goods and services (% of GDP)"
    ]
    countries = ["ESP", "USA"]  # Country codes: Spain and USA
    
    # Create macro series using Builder pattern
    macro = MacroSeries(
        name="Example Macroeconomic Series",
        indicators=selected_indicators,
        countries=countries,
        start_date="2000-01-01",
        end_date=datetime.now().strftime("%Y-%m-%d")
    )

    # Display data structure using Observer pattern
    print("\nDataFrame Structure:")
    print("Columns:", macro.data.columns)
    print("Index:", macro.data.index)
    print("\nData Sample:")
    print(macro.data.head())

    # Generate report using Builder and Template patterns
    print("\n3. Generating macroeconomic report...")
    report = MacroReport(macro_series=macro)
    report.generate()

if __name__ == "__main__":
    # Execute main workflow
    main()
