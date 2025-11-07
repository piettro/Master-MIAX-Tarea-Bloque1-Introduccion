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
from src.reports.report_portfolio import PortfolioReport
from src.reports.report_price_series import PriceSeriesReport

def main():
    """Função principal com o fluxo completo de análise."""
    try:
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
            'MSFT',
            'WFC',
            'SLB',
            'PFE',
            'COST'
        ]
        
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2025, 11, 5)
        source = DataSource.YAHOO

        portfolio = Portfolio(
            name='Quickstart Portfolio',
            holdings=symbols,
            quantity=1000,
            start_date=start_date,
            end_date=end_date,
            source=source,
            interval=Interval.MONTHLY
        )
        
        data = portfolio.get_prices()
        print(data)

        # Exibir algumas informações básicas
        print("\nResumo dos dados:")
        print(f"Período: {data.index.min()} até {data.index.max()}")
        print(f"Número de ativos: {len(symbols)}")
        print(f"Número de observações: {len(data)}")
        
        print("\nPrimeiras linhas dos dados:")
        print(data.head())

        # Calcular estatísticas e métricas
        print("Calculando estatísticas...")
        print("Weights")
        market_value = portfolio.weights()
        print(market_value)

        print("Total Value Per Holding")
        returns = portfolio.total_value_per_holding()
        print(returns)
        
        print("Total Value")
        describe = portfolio.total_value()
        print(describe)

        print("Returns")
        describe = portfolio.returns()
        print(describe)
   
        # Gerar relatório
        print("Gerando relatório...")
        report = PortfolioReport(portfolio)
        report.generate()
        print("\nRelatório gerado com sucesso!")
        
    except Exception as e:
        print(f"\nErro durante a execução: {str(e)}")
        raise

if __name__ == "__main__":
    main()
