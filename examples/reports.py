"""
Exemplo de geração de relatórios para análise de ativos e portfolios.
Demonstra o uso das diferentes classes de relatório implementadas.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

from src.core.entities.portfolio import Portfolio
from src.core.entities.price_series import PriceSeries
from src.analysis.entities.monte_carlo_portfolios import MonteCarloPortfolio
from src.reports.report_price_series import PriceSeriesReport
from src.reports.report_portfolio import PortfolioReport
from src.reports.report_monte_carlo import MonteCarloReport

def carregar_dados_exemplo():
    """
    Carrega dados de exemplo para demonstração.
    Em um caso real, estes dados viriam de uma fonte externa.
    """
    # Define período de análise
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Carrega dados processados
    dados = pd.read_csv(
        'data/processed/output_eodhd_clean_v2.csv',
        parse_dates=['Date']
    )
    
    # Filtra período
    dados = dados[
        (dados['Date'] >= start_date) &
        (dados['Date'] <= end_date)
    ]
    
    return dados

def criar_price_series_exemplo(dados: pd.DataFrame, symbol: str) -> PriceSeries:
    """
    Cria um objeto PriceSeries para um ativo específico.
    
    Parameters
    ----------
    dados : pd.DataFrame
        DataFrame com os dados de todos os ativos
    symbol : str
        Símbolo do ativo desejado
    
    Returns
    -------
    PriceSeries
        Objeto com a série temporal do ativo
    """
    dados_ativo = dados[dados['Symbol'] == symbol].copy()
    dados_ativo.set_index('Date', inplace=True)
    
    return PriceSeries(
        symbol=symbol,
        data=dados_ativo
    )

def criar_portfolio_exemplo(dados: pd.DataFrame, symbols: list, weights: list) -> Portfolio:
    """
    Cria um objeto Portfolio com os ativos especificados.
    
    Parameters
    ----------
    dados : pd.DataFrame
        DataFrame com os dados de todos os ativos
    symbols : list
        Lista de símbolos dos ativos
    weights : list
        Lista de pesos dos ativos
        
    Returns
    -------
    Portfolio
        Objeto com o portfolio criado
    """
    # Cria séries de preços para cada ativo
    price_series = []
    for symbol in symbols:
        ps = criar_price_series_exemplo(dados, symbol)
        price_series.append(ps)
    
    # Cria portfolio
    portfolio = Portfolio(
        name="Portfolio de Exemplo",
        assets=price_series,
        weights=dict(zip(symbols, weights))
    )
    
    return portfolio

def gerar_relatorio_price_series():
    """Exemplo de geração de relatório para um ativo individual."""
    print("Gerando relatório de série temporal...")
    
    # Carrega dados
    dados = carregar_dados_exemplo()
    
    # Cria PriceSeries para AAPL
    aapl = criar_price_series_exemplo(dados, 'AAPL')
    
    # Cria e salva relatório
    report = PriceSeriesReport(
        price_series=aapl,
        titulo="Análise do Ativo AAPL",
        moving_averages=[20, 50, 200]
    )
    
    output_path = report.save("relatorio_aapl")
    print(f"Relatório salvo em: {output_path}")

def gerar_relatorio_portfolio():
    """Exemplo de geração de relatório para um portfolio."""
    print("Gerando relatório de portfolio...")
    
    # Carrega dados
    dados = carregar_dados_exemplo()
    
    # Define composição do portfolio
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    weights = [0.3, 0.3, 0.2, 0.2]
    
    # Cria portfolio
    portfolio = criar_portfolio_exemplo(dados, symbols, weights)
    
    # Cria benchmark (S&P 500 como exemplo)
    benchmark = criar_price_series_exemplo(dados, 'SPY')
    benchmark_returns = benchmark.returns()
    
    # Cria e salva relatório
    report = PortfolioReport(
        portfolio=portfolio,
        titulo="Análise de Portfolio Tech",
        benchmark=benchmark_returns
    )
    
    output_path = report.save("relatorio_portfolio_tech")
    print(f"Relatório salvo em: {output_path}")

def gerar_relatorio_monte_carlo():
    """Exemplo de geração de relatório para simulação Monte Carlo."""
    print("Gerando relatório de simulação Monte Carlo...")
    
    # Carrega dados
    dados = carregar_dados_exemplo()
    
    # Cria portfolio
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    weights = [0.3, 0.3, 0.2, 0.2]
    portfolio = criar_portfolio_exemplo(dados, symbols, weights)
    
    # Executa simulação Monte Carlo
    mc = MonteCarloPortfolio(
        portfolio=portfolio,
        n_simulacoes=1000,
        janela_rebalanceamento=21  # Mensal
    )
    mc.executar()
    
    # Cria e salva relatório
    report = MonteCarloReport(
        simulacao=mc,
        titulo="Simulação Monte Carlo - Portfolio Tech"
    )
    
    output_path = report.save("relatorio_montecarlo_tech")
    print(f"Relatório salvo em: {output_path}")

def main():
    """Função principal com exemplos de uso dos relatórios."""
    try:
        # Configura diretório de saída
        output_dir = Path('data/output/reports')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Gera relatórios
        gerar_relatorio_price_series()
        gerar_relatorio_portfolio()
        gerar_relatorio_monte_carlo()
        
        print("\nTodos os relatórios foram gerados com sucesso!")
        
    except Exception as e:
        print(f"\nErro ao gerar relatórios: {str(e)}")

if __name__ == "__main__":
    main()
