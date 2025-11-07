
# 🏗️ System Architecture

## Class Diagram

```mermaid
classDiagram
    %% Core Entities
    class TimeSeries {
        <<Abstract>>
        +str name
        +DataFrame data
        +date start_date
        +date end_date
        +Dict metadata
        +__post_init__()
        +summary() void
    }

    class PriceSeries {
        +List symbols
        +DataFrame stats
        +DataSource source
        +Interval interval
        +__post_init__()
        +_compute_stats() void
        +get_market_value() Series
        +get_initial_prices() Series
        +get_returns() DataFrame
        +describe() void
    }

    class MacroSeries {
        +List indicators
        +List countries
        +Dict stats
        +__post_init__()
        +_compute_stats() void
        +get_latest_values() DataFrame
        +get_changes() DataFrame
        +get_correlations() Dict
        +describe() void
    }

    class Portfolio {
        +str name
        +List quantity
        +List holdings
        +date start_date
        +date end_date
        +DataSource source
        +Interval interval
        +PriceSeries series
        +Dict positions
        +__post_init__()
        +get_prices() DataFrame
        +weights() Dict
        +total_value_per_holding() Series
        +total_value() float
        +total_value_initial() float
        +returns() DataFrame
    }

    %% Monte Carlo Simulations
    class MonteCarloBase {
        <<Abstract>>
        +Portfolio portfolio
        +int n_simulations
        +float risk_free_rate
        +float alpha
        +float initial_capital
        +DataFrame returns_df
        +DataFrame historical_returns
        +List assets
        +Array weights
        +DataFrame results
        +DataFrame simulations
        +__init__()
        +run()* DataFrame
        +generate_weights() Array
        +generate_simulated_returns() Array
        +get_weights() DataFrame
    }

    class MonteCarloReturn {
        +run() DataFrame
    }

    class MonteCarloPortfolio {
        +run() DataFrame
    }

    class MonteCarloCombined {
        +run() DataFrame
    }

    class MonteCarloCalculator {
        +DataFrame simulations
        +__init__()
        +calculate_basic_statistics() Dict
        +calculate_var_cvar() Dict
        +calculate_portfolio_statistics() DataFrame
        +calculate_correlations() DataFrame
        +calculate_drawdowns() Dict
    }

    %% Extractors Base
    class BaseExtractor {
        <<Abstract>>
        +List symbols
        +datetime start_date
        +datetime end_date
        +DataSource source
        +Interval interval
        +__init__()
        +_setup_directories() void
        +extract_data()* DataFrame
        +format_extract_data()* DataFrame
        +validate_dates() void
        +save_raw_data() void
        +save_processed_data() void
    }

    %% Concrete Extractors
    class YahooExtractor {
        +Dict INTERVAL_MAP
        +extract_data() DataFrame
        +format_extract_data() DataFrame
        +get_source_info() Dict
    }

    class EODHDExtractor {
        +Dict INTERVAL_MAP
        +str _api_key
        +APIClient _api_client
        +_initialize_client() void
        +extract_data() DataFrame
        +format_extract_data() DataFrame
        +get_source_info() Dict
    }

    class FMPExtractor {
        +Dict INTERVAL_MAP
        +str _api_key
        +extract_data() DataFrame
        +format_extract_data() DataFrame
        +get_source_info() Dict
    }

    class AlphaVantageExtractor {
        +Dict INTERVAL_MAP
        +str _api_key
        +extract_data() DataFrame
        +format_extract_data() DataFrame
        +get_source_info() Dict
    }

    class WorldBankExtractor {
        +str BASE_URL
        +Dict DEFAULT_PARAMS
        +List EU_ALTERNATIVES
        +List DEFAULT_COUNTRIES
        +Dict AVAILABLE_INDICATORS
        +get_macro_data() DataFrame
        +_fetch_indicator() DataFrame
        +_fetch_indicator_country() Series
        +format_macro_data() DataFrame
        +list_available_indicators() Dict
    }

    %% Facade and Manager Classes
    class MarketDataExtractor {
        +Dict _extractors
        +__init__()
        +fetch_price_series() DataFrame
        +compute_data_statistics() Dict
        +clean_price_data() DataFrame
        +handle_missing_data() DataFrame
        +handle_outliers() DataFrame
        +available_sources List
        +get_source_info() Dict
    }

    class MacroExtractor {
        +List AVAILABLE_SOURCES
        +Dict _extractors
        +__init__()
        +extract() DataFrame
        +list_available_indicators() Dict
    }

    class MonteCarloReport {
        +MonteCarlo simulation
        +str title
        +bool include_plots
        +bool include_tables
        +MonteCarloCalculator calculator
        +MonteCarloVisualizer visualizer
        +__init__()
        +generate() Union[str, Path]
        +_add_simulation_info() void
        +_add_performance_metrics() void
        +_add_risk_metrics() void
        +_add_visualizations() void
        +_add_conclusions() void
    }

    %% Enums
    class DataSource {
        <<Enum>>
        +YAHOO
        +EODHD
        +FMP
        +ALPHA_VANTAGE
    }

    class Interval {
        <<Enum>>
        +ONE_MINUTE
        +FIVE_MINUTES
        +DAILY
        +WEEKLY
        +MONTHLY
    }

    %% Relationships
    TimeSeries <|-- PriceSeries
    TimeSeries <|-- MacroSeries
    
    MonteCarloBase <|-- MonteCarloReturn
    MonteCarloBase <|-- MonteCarloPortfolio
    MonteCarloBase <|-- MonteCarloCombined
    
    BaseExtractor <|-- YahooExtractor
    BaseExtractor <|-- EODHDExtractor
    BaseExtractor <|-- FMPExtractor
    BaseExtractor <|-- AlphaVantageExtractor

    Portfolio --> PriceSeries
    Portfolio --> DataSource
    Portfolio --> Interval
    
    MonteCarloBase --> Portfolio
    MonteCarloCalculator --> MonteCarloBase
    
    MarketDataExtractor --> BaseExtractor
    MarketDataExtractor --> DataSource
    MarketDataExtractor --> Interval
    
    MacroExtractor --> WorldBankExtractor
    
    MonteCarloReport --> MonteCarloBase
    MonteCarloReport --> MonteCarloCalculator
```

## Key Design Patterns

- **Template Method**: MonteCarloBase, BaseExtractor
- **Strategy**: Multiple data sources and simulation types  
- **Factory**: MarketDataExtractor creates specific extractors
- **Facade**: Portfolio and MarketDataExtractor simplify complex operations
- **Observer**: Automatic statistics updates
- **Adapter**: API format standardization
```
