"""
Quickstart: Demonstração do processo completo de análise de portfolio.
Inclui download de dados, criação de séries temporais, montagem de portfolio
e geração de relatórios de análise.
"""

from datetime import datetime
import pandas as pd
from src.core.entities.price_series import PriceSeries
from src.core.entities.portfolio import Portfolio
from src.extractor.prices_extractor import MarketDataExtractor
from src.extractor.sources.prices.extractor_prices_base import Interval, DataSource
from src.reports.report_price_series import PriceSeriesReport

def main():
    """Função principal com o fluxo completo de análise."""
    try:
        # Inicializar o extrator de dados
        print("Inicializando extrator de dados...")
        extractor = MarketDataExtractor()

        # Definir parâmetros para extração
        '''
        symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',  # Tech
            'JPM', 'BAC', 'WFC', 'GS', 'MS',          # Financials
            'JNJ', 'PFE', 'UNH', 'MRK', 'ABBV',       # Healthcare
            'XOM', 'CVX', 'COP', 'SLB', 'EOG',        # Energy
            'PG', 'KO', 'PEP', 'WMT', 'COST'          # Consumer
        ]
        '''
        symbols = [
            'GOOGL',
            'JPM',
            'MRK',
            'XOM',
            'WMT'
        ]
        
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2025, 11, 5)
        source = DataSource.YAHOO

        price_series = PriceSeries(
            name='Quickstart Price Series',
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            source=source,
            interval=Interval.MONTHLY
        )

        # Exibir algumas informações básicas
        print("\nResumo dos dados:")
        print(f"Período: {price_series.data.index.min()} até {price_series.data.index.max()}")
        print(f"Número de ativos: {len(symbols)}")
        print(f"Número de observações: {len(price_series.data)}")
        
        print("\nPrimeiras linhas dos dados:")
        print(price_series.data.head())

        # Calcular estatísticas e métricas
        print("Calculando estatísticas...")
        print("Market Value")
        market_value = price_series.get_market_value()
        print(market_value)

        print("Returns")
        returns = price_series.get_returns()
        print(returns)
        
        print("Describe")
        describe = price_series.describe()
        print(describe)
   
        # Gerar relatório
        print("Gerando relatório...")
        report = PriceSeriesReport(price_series)
        report.generate()
        print("\nRelatório gerado com sucesso!")
        
    except Exception as e:
        print(f"\nErro durante a execução: {str(e)}")
        raise

if __name__ == "__main__":
    main()
