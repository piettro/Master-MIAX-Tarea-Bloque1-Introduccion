"""
Interface de linha de comando (CLI) para o projeto.
Permite executar as principais funcionalidades através do terminal.
"""

import argparse
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from src.core.entities.portfolio import Portfolio
from src.core.entities.price_series import PriceSeries
from src.reports.report_portfolio import PortfolioReport
from src.reports.report_price_series import PriceSeriesReport
from src.reports.report_monte_carlo import MonteCarloReport
from src.analysis.entities.monte_carlo_portfolios import MonteCarloPortfolio
from src.analysis.entities.monte_carlo_returns import MonteCarloReturns
from src.extractor.prices_extractor import APIExtractor

def parse_args():
    """Configura e processa argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Ferramenta de Análise Financeira",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Comando principal
    subparsers = parser.add_subparsers(dest='command', help='Comando a executar')
    
    # Comando: extract
    extract_parser = subparsers.add_parser('extract', help='Extrai dados financeiros')
    extract_parser.add_argument(
        '--source',
        choices=['yahoo', 'fmp', 'eodhd'],
        required=True,
        help='Fonte dos dados'
    )
    extract_parser.add_argument(
        '--tickers',
        nargs='+',
        required=True,
        help='Lista de tickers'
    )
    extract_parser.add_argument(
        '--start-date',
        help='Data inicial (YYYY-MM-DD)'
    )
    extract_parser.add_argument(
        '--end-date',
        help='Data final (YYYY-MM-DD)'
    )
    extract_parser.add_argument(
        '--output',
        help='Arquivo de saída'
    )
    
    # Comando: analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analisa dados financeiros')
    analyze_parser.add_argument(
        '--type',
        choices=['portfolio', 'price', 'monte-carlo'],
        required=True,
        help='Tipo de análise'
    )
    analyze_parser.add_argument(
        '--input',
        required=True,
        help='Arquivo de entrada com dados'
    )
    analyze_parser.add_argument(
        '--tickers',
        nargs='+',
        help='Lista de tickers para análise'
    )
    analyze_parser.add_argument(
        '--weights',
        nargs='+',
        type=float,
        help='Pesos dos ativos para portfolio'
    )
    analyze_parser.add_argument(
        '--benchmark',
        help='Ticker do benchmark'
    )
    analyze_parser.add_argument(
        '--output-dir',
        help='Diretório para relatórios'
    )
    analyze_parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Não gerar gráficos'
    )
    
    # Comando: simulate
    simulate_parser = subparsers.add_parser('simulate', help='Executa simulações Monte Carlo')
    simulate_parser.add_argument(
        '--type',
        choices=['portfolio', 'returns'],
        required=True,
        help='Tipo de simulação'
    )
    simulate_parser.add_argument(
        '--input',
        required=True,
        help='Arquivo de entrada com dados'
    )
    simulate_parser.add_argument(
        '--n-sims',
        type=int,
        default=1000,
        help='Número de simulações'
    )
    simulate_parser.add_argument(
        '--n-days',
        type=int,
        default=252,
        help='Número de dias a simular'
    )
    simulate_parser.add_argument(
        '--seed',
        type=int,
        help='Semente aleatória'
    )
    simulate_parser.add_argument(
        '--output-dir',
        help='Diretório para relatórios'
    )
    
    return parser.parse_args()

def extract_data(args):
    """
    Extrai dados financeiros da fonte especificada.
    
    Parameters
    ----------
    args : argparse.Namespace
        Argumentos da linha de comando
    """
    extractor = APIExtractor()
    
    # Configura parâmetros
    start_date = args.start_date or '2010-01-01'
    end_date = args.end_date or datetime.now().strftime('%Y-%m-%d')
    output = args.output or f'data/raw/output_{args.source}.csv'
    
    # Extrai dados
    print(f"Extraindo dados de {args.source}...")
    df = extractor.extract(
        source=args.source,
        tickers=args.tickers,
        start_date=start_date,
        end_date=end_date
    )
    
    # Salva dados
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path)
    print(f"Dados salvos em {output_path}")

def analyze_data(args):
    """
    Analisa dados financeiros e gera relatórios.
    
    Parameters
    ----------
    args : argparse.Namespace
        Argumentos da linha de comando
    """
    # Carrega dados
    df = pd.read_csv(args.input, index_col=0, parse_dates=True)
    
    # Configura diretório de saída
    output_dir = Path(args.output_dir) if args.output_dir else Path(config.get('paths.reports'))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.type == 'portfolio':
        _analyze_portfolio(df, args, output_dir)
    elif args.type == 'price':
        _analyze_price_series(df, args, output_dir)
    else:  # monte-carlo
        _analyze_monte_carlo(df, args, output_dir)

def simulate_data(args):
    """
    Executa simulações Monte Carlo.
    
    Parameters
    ----------
    args : argparse.Namespace
        Argumentos da linha de comando
    """
    # Carrega dados
    df = pd.read_csv(args.input, index_col=0, parse_dates=True)
    
    # Configura diretório de saída
    output_dir = Path(args.output_dir) if args.output_dir else Path(config.get('paths.reports'))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configura parâmetros
    params = {
        'n_simulations': args.n_sims,
        'n_days': args.n_days,
        'seed': args.seed
    }
    
    if args.type == 'portfolio':
        _simulate_portfolio(df, params, output_dir)
    else:  # returns
        _simulate_returns(df, params, output_dir)

def _analyze_portfolio(df: pd.DataFrame, args, output_dir: Path):
    """Helper para análise de portfolio."""
    # Cria portfolio
    tickers = args.tickers or df.columns.get_level_values('Ticker').unique()
    weights = args.weights or [1/len(tickers)] * len(tickers)
    
    portfolio = Portfolio(
        data=df,
        tickers=tickers,
        weights=dict(zip(tickers, weights))
    )
    
    # Carrega benchmark se especificado
    benchmark = None
    if args.benchmark:
        benchmark = df[args.benchmark] if args.benchmark in df.columns else None
    
    # Gera relatório
    report = PortfolioReport(
        portfolio=portfolio,
        output_dir=output_dir,
        include_plots=not args.no_plots,
        benchmark=benchmark
    )
    report.generate()

def _analyze_price_series(df: pd.DataFrame, args, output_dir: Path):
    """Helper para análise de série temporal."""
    # Cria série temporal
    tickers = args.tickers or df.columns.get_level_values('Ticker').unique()
    price_series = PriceSeries(data=df, tickers=tickers)
    
    # Gera relatório
    report = PriceSeriesReport(
        price_series=price_series,
        output_dir=output_dir,
        include_plots=not args.no_plots
    )
    report.generate()

def _analyze_monte_carlo(df: pd.DataFrame, args, output_dir: Path):
    """Helper para análise Monte Carlo."""
    # Cria série temporal
    tickers = args.tickers or df.columns.get_level_values('Ticker').unique()
    price_series = PriceSeries(data=df, tickers=tickers)
    
    # Configura simulação
    mc = MonteCarloReturns(
        price_series=price_series,
        n_simulations=config.get('monte_carlo.n_simulations'),
        n_days=config.get('monte_carlo.n_days')
    )
    
    # Gera relatório
    report = MonteCarloReport(
        monte_carlo=mc,
        output_dir=output_dir,
        include_plots=not args.no_plots
    )
    report.generate()

def _simulate_portfolio(df: pd.DataFrame, params: dict, output_dir: Path):
    """Helper para simulação Monte Carlo de portfolio."""
    mc = MonteCarloPortfolio(df, **params)
    report = MonteCarloReport(
        monte_carlo=mc,
        output_dir=output_dir
    )
    report.generate()

def _simulate_returns(df: pd.DataFrame, params: dict, output_dir: Path):
    """Helper para simulação Monte Carlo de retornos."""
    mc = MonteCarloReturns(df, **params)
    report = MonteCarloReport(
        monte_carlo=mc,
        output_dir=output_dir
    )
    report.generate()

def main():
    """Função principal do CLI."""
    try:
        args = parse_args()
        
        if args.command == 'extract':
            extract_data(args)
        elif args.command == 'analyze':
            analyze_data(args)
        elif args.command == 'simulate':
            simulate_data(args)
        else:
            print("Comando inválido. Use --help para ver os comandos disponíveis.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Erro: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
