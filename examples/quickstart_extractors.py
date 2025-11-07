"""
Quickstart: Demonstração do processo completo de análise de portfolio.
Inclui download de dados, criação de séries temporais, montagem de portfolio
e geração de relatórios de análise.
"""
from datetime import datetime
from numpy import DataSource
from src.extractor.prices_extractor import MarketDataExtractor, DataSource
from src.extractor.sources.prices.extractor_prices_base import Interval

def main():
    extractor = MarketDataExtractor()

    symbols = ['AEP','AAPL','MSFT','GOOGL','AMZN']  
    start_date = datetime(2020, 11, 5) 
    end_date = datetime(2025, 11, 5) 
    source = DataSource.YAHOO   

    data = extractor.fetch_price_series(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        source=source,
        interval=Interval.MONTHLY
    )
    print(f"Dataframe {source.value}:")
    print(data.head())

    data_statistics = extractor.compute_data_statistics(data)
    print(f"Basic Statistics")
    print(data_statistics['basic_stats'])

    print(f"Missing Values Statistics")
    print(data_statistics['missing_data'])

    print(f"Data Quality Statistics")
    print(data_statistics['data_quality'])

    print(f"Value Counts Statistics")
    print(data_statistics['value_counts'])

    print(f"Source Information {source.value}:")
    source_info = extractor.get_source_info(source)
    print(source_info)

    data = extractor.clean_price_data(data)
    print(f"Cleaned Dataframe {source.value}:")
    print(data.head())

    data = extractor.handle_missing_data(data, method='ffill')
    print(f"Dataframe after handling missing data {source.value}:")
    print(data.head())

if __name__ == "__main__":
    main()
