"""
Relatório especializado para análise de portfolios.
Gera relatórios completos com visualizações e análises de carteiras.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from src.reports.report_base import BaseReport
from src.plots.plot_portfolio import VisualizadorPortfolio
from src.core.entities.portfolio import Portfolio

class PortfolioReport(BaseReport):
    """
    Relatório especializado para análise de portfolios.
    Gera um relatório completo com visualizações e métricas para análise
    de carteiras de investimento.
    """
    
    def __init__(
        self,
        portfolio: Portfolio,
        titulo: str = "Relatório de Análise de Portfolio",
        output_dir: Optional[Path] = None,
        include_plots: bool = True,
        include_tables: bool = True,
        benchmark: Optional[pd.Series] = None
    ):
        """
        Parameters
        ----------
        portfolio : Portfolio
            Objeto Portfolio com os dados da carteira
        titulo : str
            Título do relatório
        output_dir : Path, opcional
            Diretório para salvar o relatório
        include_plots : bool
            Se True, inclui visualizações
        include_tables : bool
            Se True, inclui tabelas de métricas
        benchmark : pd.Series, opcional
            Série temporal com retornos do benchmark para comparação
        """
        super().__init__(
            titulo=titulo,
            output_dir=output_dir,
            include_plots=include_plots,
            include_tables=include_tables
        )
        
        self.portfolio = portfolio
        self.benchmark = benchmark
        
        # Inicializa visualizador
        returns = self.portfolio.returns()
        weights = self.portfolio.weights()
        self.visualizador = VisualizadorPortfolio(returns, weights)
        
    def generate(self) -> str:
        """
        Gera o conteúdo do relatório de portfolio.
        
        Returns
        -------
        str
            Conteúdo do relatório em formato Markdown
        """
        # Informações do Portfolio
        self._add_portfolio_info()
        
        # Análise de Alocação
        if self.include_plots:
            self._add_allocation_analysis()
            
        # Análise de Performance
        self._add_performance_analysis()
        
        # Análise de Risco
        self._add_risk_analysis()
        
        # Análise de Correlações
        if self.include_plots:
            self._add_correlation_analysis()
            
        # Dashboard Completo
        if self.include_plots:
            self._add_dashboard()
        
        return "Relatório de Portfolio gerado com sucesso!"
        
    def _add_portfolio_info(self) -> None:
        """Adiciona seção com informações básicas do portfolio."""
        self.add_section(
            "Informações do Portfolio",
            level=2
        )
        
        info = [
            f"- **Nome:** {self.portfolio.name}",
            "- **Composição:**"
        ]
        
        # Adiciona informação dos ativos e seus pesos
        for ativo, peso in self.portfolio.weights().items():
            info.append(f"  - {ativo}: {peso:.2%}")
            
        info.extend([
            f"- **Período:** {self.portfolio.start_date} a {self.portfolio.end_date}",
            f"- **Número de Ativos:** {len(self.portfolio.holdings)}",
            f"- **Patrimônio Total:** {self.portfolio.total_value():,.2f}"
        ])
        
        self.add_section("", "\n".join(info))
        
    def _add_allocation_analysis(self) -> None:
        """Adiciona seção com análise de alocação."""
        self.add_section("Análise de Alocação", level=2)
        
        # Gráfico de pizza com alocação
        fig = self.visualizador.plot_alocacao()
        self.add_plot(
            fig,
            "Alocação do Portfolio",
            level=3
        )
        plt.close()
        
        # Gráfico de risco x retorno dos ativos
        fig = self.visualizador.plot_retorno_risco_ativos()
        self.add_plot(
            fig,
            "Retorno vs Risco dos Ativos",
            level=3
        )
        plt.close()
        
    def _add_performance_analysis(self) -> None:
        """Adiciona seção com análise de performance."""
        self.add_section("Análise de Performance", level=2)
        
        if self.include_plots:
            # Evolução do portfolio
            fig = self.visualizador.plot_evolucao_portfolio(self.benchmark)
            self.add_plot(
                fig,
                "Evolução do Portfolio",
                level=3
            )
            plt.close()
            
            # Distribuição dos retornos
            fig = self.visualizador.plot_retornos_distribuicao()
            self.add_plot(
                fig,
                "Distribuição dos Retornos",
                level=3
            )
            plt.close()
            
        if self.include_tables:
            # Estatísticas de performance
            returns = self.portfolio.returns()
            portfolio_returns = returns.mean(axis=1)
            
            stats = pd.DataFrame({
                'Métrica': [
                    'Retorno Médio Diário',
                    'Retorno Médio Anualizado',
                    'Volatilidade Diária',
                    'Volatilidade Anualizada',
                    'Índice Sharpe',
                    'Máximo Drawdown',
                    'Value at Risk (95%)',
                    'Expected Shortfall (95%)'
                ],
                'Valor': [
                    portfolio_returns.mean(),
                    portfolio_returns.mean() * 252,
                    portfolio_returns.std(),
                    portfolio_returns.std() * np.sqrt(252),
                    (portfolio_returns.mean() * 252) / (portfolio_returns.std() * np.sqrt(252)),
                    self._calculate_max_drawdown(portfolio_returns),
                    portfolio_returns.quantile(0.05),
                    portfolio_returns[portfolio_returns <= portfolio_returns.quantile(0.05)].mean()
                ]
            })
            
            # Adiciona métricas do benchmark se disponível
            if self.benchmark is not None:
                stats['Benchmark'] = [
                    self.benchmark.mean(),
                    self.benchmark.mean() * 252,
                    self.benchmark.std(),
                    self.benchmark.std() * np.sqrt(252),
                    (self.benchmark.mean() * 252) / (self.benchmark.std() * np.sqrt(252)),
                    self._calculate_max_drawdown(self.benchmark),
                    self.benchmark.quantile(0.05),
                    self.benchmark[self.benchmark <= self.benchmark.quantile(0.05)].mean()
                ]
            
            format_dict = {
                'Valor': lambda x: (
                    f"{x:.2%}" if any(m in stats.loc[stats['Valor'] == x, 'Métrica'].iloc[0] 
                                    for m in ['Retorno', 'Volatilidade', 'Drawdown', 'VaR', 'Shortfall'])
                    else f"{x:.4f}"
                )
            }
            if 'Benchmark' in stats.columns:
                format_dict['Benchmark'] = format_dict['Valor']
            
            self.add_table(
                stats,
                "Estatísticas de Performance",
                format_dict=format_dict
            )
            
    def _add_risk_analysis(self) -> None:
        """Adiciona seção com análise de risco."""
        self.add_section("Análise de Risco", level=2)
        
        if self.include_plots:
            # Contribuição ao risco
            fig = self.visualizador.plot_contribuicao_risco()
            self.add_plot(
                fig,
                "Contribuição ao Risco por Ativo",
                level=3
            )
            plt.close()
            
            # Drawdown
            fig = self.visualizador.plot_drawdown()
            self.add_plot(
                fig,
                "Análise de Drawdown",
                level=3
            )
            plt.close()
            
        if self.include_tables:
            # Estatísticas individuais dos ativos
            returns = self.portfolio.returns()
            
            stats = []
            for ativo in returns.columns:
                ret = returns[ativo]
                stats.append({
                    'Ativo': ativo,
                    'Peso': self.portfolio.weights()[ativo],
                    'Retorno Anual': ret.mean() * 252,
                    'Volatilidade': ret.std() * np.sqrt(252),
                    'Sharpe': (ret.mean() * 252) / (ret.std() * np.sqrt(252)),
                    'VaR 95%': ret.quantile(0.05),
                    'Beta': self._calculate_beta(ret, self.benchmark) if self.benchmark is not None else None
                })
                
            stats_df = pd.DataFrame(stats)
            format_dict = {
                'Peso': lambda x: f"{x:.2%}",
                'Retorno Anual': lambda x: f"{x:.2%}",
                'Volatilidade': lambda x: f"{x:.2%}",
                'Sharpe': lambda x: f"{x:.2f}",
                'VaR 95%': lambda x: f"{x:.2%}",
                'Beta': lambda x: f"{x:.2f}" if x is not None else "N/A"
            }
            
            self.add_table(
                stats_df,
                "Estatísticas por Ativo",
                format_dict=format_dict
            )
            
    def _add_correlation_analysis(self) -> None:
        """Adiciona seção com análise de correlações."""
        self.add_section("Análise de Correlações", level=2)
        
        # Matriz de correlação
        fig = self.visualizador.plot_correlacao()
        self.add_plot(
            fig,
            "Matriz de Correlação",
            level=3
        )
        plt.close()
        
    def _add_dashboard(self) -> None:
        """Adiciona dashboard completo."""
        fig = self.visualizador.plot_dashboard(self.benchmark)
        self.add_plot(
            fig,
            "Dashboard Completo",
            level=2
        )
        plt.close()
        
    @staticmethod
    def _calculate_max_drawdown(returns: pd.Series) -> float:
        """Calcula o máximo drawdown de uma série de retornos."""
        cum_returns = (1 + returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = (cum_returns - rolling_max) / rolling_max
        return drawdowns.min()
        
    @staticmethod
    def _calculate_beta(returns: pd.Series, benchmark: pd.Series) -> float:
        """Calcula o beta de uma série de retornos em relação ao benchmark."""
        if benchmark is None:
            return None
        cov = returns.cov(benchmark)
        var = benchmark.var()
        return cov / var if var != 0 else 0
