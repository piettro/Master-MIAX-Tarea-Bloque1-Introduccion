"""
Quickstart: Demonstração do processo completo de análise de portfolio.
Inclui download de dados, criação de séries temporais, montagem de portfolio
e geração de relatórios de análise.
"""

from datetime import date, timedelta
from pathlib import Path
import pandas as pd
from src.core.entities.price_series import PriceSeries
from src.core.entities.portfolio import Portfolio
from src.analysis.entities.monte_carlo_returns import MonteCarloRetorno
from src.reports.report_price_series import PriceSeriesReport
from src.reports.report_portfolio import PortfolioReport
from src.reports.report_monte_carlo import MonteCarloReport

def criar_portfolio() -> Portfolio:
    """
    Cria um portfolio com os ativos baixados.
    
    Parameters
    ----------
    series : Dict[str, PriceSeries]
        Dicionário com as séries temporais dos ativos
    
    Returns
    -------
    Portfolio
        Portfolio montado com os ativos
    """
    # Define período de análise
    end_date = date.today()
    start_date = end_date - timedelta(days=365)  # 1 ano de dados
    
    # Carrega e seleciona aleatoriamente 5 ativos do SP500
    sp500_df = pd.read_csv('data/raw/sp500.csv')
    symbols = sp500_df['Symbol'].sample(n=5).tolist()
    print(f"Ativos selecionados: {symbols}")

    # Cria portfolio
    portfolio = Portfolio(
        name="Portfolio Tecnologia",
        quantity=0.2,  # Pesos iguais para 5 ativos
        holdings=symbols,
        start_date=start_date,
        end_date=end_date,
        source='yfinance'
    )
    
    return portfolio

def analisar_ativos(portfolio: Portfolio, output_dir: Path) -> None:
    """
    Gera relatórios individuais para cada ativo do portfolio.
    
    Parameters
    ----------
    portfolio : Portfolio
        Portfolio contendo os ativos a serem analisados
    output_dir : Path
        Diretório para salvar os relatórios
    """
    # Obtém os dados do portfolio
    df = portfolio.series.data.copy()
    
    # Obtém lista de tickers do portfolio
    tickers = portfolio.holdings
    
    for ticker in tickers:
        print(f"\nGerando relatório para {ticker}...")
        
        # Cria série temporal para o ativo
        price_series = PriceSeries(
            name=f"Série de Preços {ticker}",
            tickers=ticker,
            source=portfolio.source,
            start_date=portfolio.start_date,
            end_date=portfolio.end_date
        )
        
        # Cria relatório
        report = PriceSeriesReport(
            price_series=price_series,
            titulo=f"Análise do Ativo {ticker}",
            output_dir=output_dir,
            moving_averages=[20, 50, 200]
        )
        
        # Salva relatório
        output_path = report.save(f"relatorio_{ticker.lower()}")
        print(f"Relatório salvo em: {output_path}")

def analisar_portfolio(portfolio: Portfolio, output_dir: Path) -> None:
    """
    Gera relatório de análise do portfolio.
    
    Parameters
    ----------
    portfolio : Portfolio
        Portfolio a ser analisado
    output_dir : Path
        Diretório para salvar os relatórios
    """
    print("\nGerando relatório do portfolio...")
    
    # Cria relatório do portfolio
    report = PortfolioReport(
        portfolio=portfolio,
        titulo="Análise de Portfolio Tech",
        output_dir=output_dir
    )
    
    # Salva relatório
    output_path = report.save("relatorio_portfolio_tech")
    print(f"Relatório salvo em: {output_path}")

def simular_monte_carlo(portfolio: Portfolio, output_dir: Path) -> None:
    """
    Executa e analisa simulação Monte Carlo do portfolio.
    
    Parameters
    ----------
    portfolio : Portfolio
        Portfolio a ser simulado
    output_dir : Path
        Diretório para salvar os relatórios
    """
    print("\nExecutando simulação Monte Carlo...")
    
    # Configura e executa simulação
    simulador = MonteCarloRetorno(
        portfolio=portfolio,
        n_simulacoes=1000,
        taxa_livre_risco=0.03,
        capital_inicial=100000.0
    )
    simulador.run()
    
    # Gera relatório da simulação
    report = MonteCarloReport(
        simulacao=simulador,
        titulo="Simulação Monte Carlo - Portfolio Tech",
        output_dir=output_dir
    )
    
    # Salva relatório
    output_path = report.save("relatorio_montecarlo_tech")
    print(f"Relatório salvo em: {output_path}")

def main():
    """Função principal com o fluxo completo de análise."""
    try:
        output_dir = Path('data/output/reports')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("\nCriando portfolio...")
        portfolio = criar_portfolio()
        
        print("\nAnalisando ativos individuais...")
        analisar_ativos(portfolio, output_dir)
        
        print("\nAnalisando portfolio...")
        analisar_portfolio(portfolio, output_dir)
        
        print("\nExecutando simulação Monte Carlo...")
        simular_monte_carlo(portfolio, output_dir)
        
        print("\nTodas as análises foram concluídas com sucesso!")
        
    except Exception as e:
        print(f"\nErro durante a execução: {str(e)}")

if __name__ == "__main__":
    main()
