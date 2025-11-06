"""
Gerador de relatórios em Markdown para simulações Monte Carlo.
"""

from pathlib import Path
from typing import Optional, Union
import matplotlib.pyplot as plt
import pandas as pd
from src.analysis.entities.monte_carlo_returns import MonteCarloRetorno
from src.analysis.entities.monte_carlo_portfolios import MonteCarloPortfolio
from src.analysis.entities.monte_carlo_combined import MonteCarloCombinado
from src.core.entities.portfolio import Portfolio
from src.analysis.entities.monte_carlo_metrics import CalculadorMonteCarlo
from src.plots.plot_monte_carlo import VisualizadorMonteCarlo
from src.reports.report_base import BaseReport

class MonteCarloReport(BaseReport):
    """
    Relatório especializado para simulações Monte Carlo.
    Gera um relatório completo com visualizações e métricas.
    """
    
    def __init__(
        self,
        simulacao: Union[MonteCarloRetorno, MonteCarloPortfolio, MonteCarloCombinado],
        titulo: str = "Relatório de Simulação Monte Carlo",
        output_dir: Optional[Path] = None,
        include_plots: bool = True,
        include_tables: bool = True
    ):
        """
        Parameters
        ----------
        simulacao : MonteCarloRetorno | MonteCarloPortfolio | MonteCarloCombinado
            Simulação Monte Carlo já executada
        titulo : str
            Título do relatório
        output_dir : Path, opcional
            Diretório para salvar o relatório
        include_plots : bool
            Se True, inclui visualizações
        include_tables : bool
            Se True, inclui tabelas de métricas
        """
        super().__init__(
            titulo=titulo,
            output_dir=output_dir,
            include_plots=include_plots,
            include_tables=include_tables
        )
        
        if simulacao.simulacoes is None:
            raise ValueError("A simulação precisa ser executada antes de gerar o relatório")

        self.simulacao = simulacao
        # Calculador e visualizador baseados no DataFrame de simulações
        self.calculador = CalculadorMonteCarlo(simulacao.simulacoes)
        self.visualizador = VisualizadorMonteCarlo(simulacao.simulacoes)
        
    def generate(self) -> str:
        """
        Gera o conteúdo do relatório Monte Carlo.
        
        Returns
        -------
        str
            Conteúdo do relatório em formato Markdown
        """        
        # Informações gerais sobre a simulação e o portfolio
        self._add_simulation_info()

        # Performance e risco (tabelas)
        if self.include_tables:
            self._add_performance_metrics()
            self._add_risk_metrics()

        # Visualizações
        if self.include_plots:
            self._add_visualizations()

        # Conclusões (mantém a lógica original)
        self._add_conclusions()

        return "Relatório Monte Carlo gerado com sucesso!"

    def _add_simulation_info(self) -> None:
        """Adiciona informações básicas sobre a simulação e o portfolio."""
        self.add_section("Informações do Portfolio", level=2)

        portfolio = self.simulacao.portfolio
        portfolio_info = [
            f"- **Nome:** {portfolio.name}",
            "- **Ativos:**"
        ]
        for ativo, peso in portfolio.weights().items():
            portfolio_info.append(f"  - {ativo}: {peso:.2%}")
        portfolio_info.extend([
            f"- **Período:** {portfolio.start_date} a {portfolio.end_date}",
            f"- **Número de Simulações:** {self.simulacao.n_simulacoes}"
        ])
        self.add_section("", "\n".join(portfolio_info))

    def _add_performance_metrics(self) -> None:
        """Monta tabelas com estatísticas de performance da simulação."""
        self.add_section("Métricas de Performance", level=2)

        stats = self.calculador.calcular_estatisticas_basicas()
        stats_df = pd.DataFrame({
            'Métrica': ['Retorno Médio', 'Retorno Mediano', 'Desvio Padrão', 'Retorno Mínimo', 'Retorno Máximo'],
            'Valor': [
                stats['retorno_medio'],
                stats['retorno_mediano'],
                stats['desvio_padrao'],
                stats['retorno_minimo'],
                stats['retorno_maximo']
            ]
        })
        self.add_table(stats_df, "Estatísticas Básicas", format_dict={'Valor': lambda x: f"{x:.2%}"})

    def _add_risk_metrics(self) -> None:
        """Monta tabelas com métricas de risco (VaR/CVaR/drawdown)."""
        # VaR / CVaR
        var_cvar = self.calculador.calcular_var_cvar()
        risk_df = pd.DataFrame({'Métrica': ['VaR 95%', 'CVaR 95%'], 'Valor': [var_cvar['var'], var_cvar['cvar']]})
        self.add_table(risk_df, "Métricas de Risco", format_dict={'Valor': lambda x: f"{x:.2%}"})

        # Drawdowns
        drawdowns = self.calculador.calcular_drawdowns()
        dd_df = pd.DataFrame({
            'Métrica': ['Máximo Drawdown', 'Drawdown Médio', 'Desvio Drawdown'],
            'Valor': [drawdowns['max_drawdown'], drawdowns['avg_drawdown'], drawdowns['drawdown_std']]
        })
        self.add_table(dd_df, "Métricas de Drawdown", format_dict={'Valor': lambda x: f"{x:.2%}"})

    def _add_visualizations(self) -> None:
        """Adiciona plots principais da simulação."""
        self.add_section("Visualizações", level=2)

        # Evolução do valor
        plt.figure(figsize=(12, 6))
        self.visualizador.plot_evolucao_valor()
        self.add_plot(plt.gcf(), "Evolução do Valor da Carteira")
        plt.close()

        # Distribuição dos retornos
        plt.figure(figsize=(10, 6))
        self.visualizador.plot_distribuicao_retornos()
        self.add_plot(plt.gcf(), "Distribuição dos Retornos")
        plt.close()

        # Evolução dos pesos (quando aplicável)
        try:
            plt.figure(figsize=(12, 6))
            self.visualizador.plot_evolucao_pesos()
            self.add_plot(plt.gcf(), "Evolução dos Pesos")
            plt.close()
        except Exception:
            # Alguns tipos de simulação podem não ter pesos
            pass

        # Dashboard de métricas
        plt.figure(figsize=(15, 12))
        self.visualizador.plot_metricas()
        self.add_plot(plt.gcf(), "Dashboard de Métricas")
        plt.close()

    def _add_conclusions(self) -> None:
        """Mantém a seção de conclusões original, resumindo resultados e diferenças por tipo de simulação."""
        self.add_section("Conclusões", level=2)

        stats = self.calculador.calcular_estatisticas_basicas()
        var_cvar = self.calculador.calcular_var_cvar()

        conclusions = [
            "\nCom base nas simulações realizadas, podemos concluir:",
            f"\n1. O retorno médio esperado é de {stats['retorno_medio']:.2%}, com um desvio padrão de {stats['desvio_padrao']:.2%}",
            f"2. Existe um risco de {var_cvar['var']:.2%} de perda (VaR 95%)",
            f"3. Em cenários extremos, a perda média esperada é de {var_cvar['cvar']:.2%} (CVaR 95%)"
        ]

        if isinstance(self.simulacao, MonteCarloPortfolio):
            conclusions.append("4. A simulação de pesos mostra diversas composições possíveis para a carteira")
        elif isinstance(self.simulacao, MonteCarloRetorno):
            conclusions.append("4. A simulação de retornos mantém os pesos fixos e explora diferentes cenários de mercado")

        self.add_section("", "\n".join(conclusions))

