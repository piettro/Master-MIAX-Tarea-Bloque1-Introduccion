"""
Relatório especializado para análise de séries temporais de preços.
Gera relatórios completos com visualizações e análises de ativos.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from src.reports.report_base import BaseReport
from src.plots.plot_price_series import VisualizadorPriceSeries
from src.core.entities.price_series import PriceSeries

class PriceSeriesReport(BaseReport):
    """
    Relatório especializado para análise de séries temporais de preços.
    Gera um relatório completo com visualizações e métricas para análise
    técnica e estatística de ativos financeiros.
    """
    
    def __init__(
        self,
        price_series: PriceSeries,
        titulo: str = "Relatório de Análise de Série Temporal",
        output_dir: Optional[Path] = None,
        include_plots: bool = True,
        include_tables: bool = True,
        moving_averages: Optional[List[int]] = [20, 50, 200]
    ):
        """
        Parameters
        ----------
        price_series : PriceSeries
            Objeto PriceSeries com os dados do ativo
        titulo : str
            Título do relatório
        output_dir : Path, opcional
            Diretório para salvar o relatório
        include_plots : bool
            Se True, inclui visualizações
        include_tables : bool
            Se True, inclui tabelas de métricas
        moving_averages : List[int], opcional
            Lista com períodos para médias móveis
        """
        super().__init__(
            titulo=titulo,
            output_dir=output_dir,
            include_plots=include_plots,
            include_tables=include_tables
        )
        
        self.price_series = price_series
        self.data = price_series.data
        self.moving_averages = moving_averages or []

        # Verifica se o DataFrame tem a estrutura esperada de MultiIndex
        if not isinstance(self.data.columns, pd.MultiIndex):
            raise ValueError("O DataFrame deve ter um MultiIndex (Price, Ticker)")
            
        if self.data.columns.names != ['Price', 'Ticker']:
            raise ValueError("O MultiIndex deve ter os níveis ['Price', 'Ticker']")
            
        self.required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in self.data.columns.get_level_values('Price') for col in self.required_columns):
            raise ValueError(
                f"PriceSeries deve conter as colunas: {', '.join(self.required_columns)}"
            )
        
        # Obtém lista de tickers
        self.tickers = price_series.tickers if isinstance(price_series.tickers, list) else [price_series.tickers]
        
        # Dicionário para armazenar dados e visualizadores por ticker
        self.ticker_data = {}
        self.visualizadores = {}
        
    def generate(self) -> str:
        """
        Gera o conteúdo do relatório de série temporal para cada ticker.
        
        Returns
        -------
        str
            Conteúdo do relatório em formato Markdown
        """
        relatorios_gerados = []
        
        for ticker in self.tickers:
            print(f"\nGerando relatório para {ticker}...")
            
            # Prepara dados do ticker atual
            self._prepare_ticker_data(ticker)
            
            # Adiciona cabeçalho do ticker
            self.add_section(f"Relatório: {ticker}", level=1)
            
            # Informações Básicas
            self._add_info_section(ticker)
            
            # Análise Técnica
            if self.include_plots:
                self._add_technical_analysis(ticker)
            
            # Análise Estatística
            if self.include_tables:
                self._add_statistical_analysis(ticker)
            
            # Análise de Retornos
            self._add_returns_analysis(ticker)
            
            # Análise de Risco
            self._add_risk_analysis(ticker)
            
            relatorios_gerados.append(ticker)
            
            # Adiciona separador entre relatórios
            if ticker != self.tickers[-1]:
                self.add_section("---", level=0)
        
        return f"Relatórios gerados com sucesso para: {', '.join(relatorios_gerados)}"
    
    #Bem feito
    def _prepare_ticker_data(self, ticker: str) -> None:
        """
        Prepara os dados para um ticker específico.
        
        Parameters
        ----------
        ticker : str
            Símbolo do ativo
        """
        # Se já temos os dados deste ticker, não precisamos processar novamente
        if ticker in self.ticker_data:
            return
            
        # Obtém os dados do ticker
        ticker_df = pd.DataFrame()
        for col in self.required_columns:
            ticker_df[col] = self.data[col, ticker]

        # Armazena os dados e cria visualizador
        self.ticker_data[ticker] = ticker_df
        self.visualizadores[ticker] = VisualizadorPriceSeries(ticker_df)
        
    def _add_info_section(self, ticker: str) -> None:
        """
        Adiciona seção com informações básicas do ativo.
        
        Parameters
        ----------
        ticker : str
            Símbolo do ativo
        """
        self.add_section(
            "Informações do Ativo",
            level=2
        )
        
        # Obtém informações do ticker atual
        df = self.ticker_data[ticker]
        primeiro_preco = df['Close'].iloc[0]
        ultimo_preco = df['Close'].iloc[-1]
        
        info = [
            f"- **Ativo:** {ticker}",
            f"- **Período:** {self.price_series.start_date} a {self.price_series.end_date}",
            f"- **Número de Observações:** {len(self.ticker_data)}",
            f"- **Primeiro Preço:** {primeiro_preco:.2f}",
            f"- **Último Preço:** {ultimo_preco:.2f}",
            f"- **Variação Total:** {((ultimo_preco / primeiro_preco) - 1):.2%}"
        ]
        
        self.add_section("", "\n".join(info))

        print('estou aqui agor')
        
    def _add_technical_analysis(self, ticker: str) -> None:
        """
        Adiciona seção com análise técnica.
        
        Parameters
        ----------
        ticker : str
            Símbolo do ativo
        """
        self.add_section("Análise Técnica", level=2)
        
        visualizador = self.visualizadores[ticker]
        
        # Preços e Médias Móveis
        fig = visualizador.plot_precos(window_ma=self.moving_averages)
        self.add_plot(
            fig,
            "Evolução do Preço e Médias Móveis",
            level=3
        )
        plt.close()
        
        # Candlestick
        fig = visualizador.plot_candlestick()
        self.add_plot(
            fig,
            "Gráfico de Candlestick",
            level=3
        )
        plt.close()
        
        # Volume
        fig = visualizador.plot_volume()
        self.add_plot(
            fig,
            "Volume de Negociação",
            level=3
        )
        plt.close()
        
    def _add_statistical_analysis(self, ticker: str) -> None:
        """
        Adiciona seção com análise estatística.
        
        Parameters
        ----------
        ticker : str
            Símbolo do ativo
        """
        self.add_section("Análise Estatística", level=2)
        df = self.ticker_data[ticker]
        
        # Estatísticas básicas dos preços
        stats = pd.DataFrame({
            'Métrica': [
                'Média',
                'Mediana',
                'Desvio Padrão',
                'Mínimo',
                'Máximo',
                'Assimetria',
                'Curtose'
            ],
            'Preço': [
                df['Close'].mean(),
                df['Close'].median(),
                df['Close'].std(),
                df['Close'].min(),
                df['Close'].max(),
                df['Close'].skew(),
                df['Close'].kurtosis()
            ],
            'Volume': [
                df['Volume'].mean(),
                df['Volume'].median(),
                df['Volume'].std(),
                df['Volume'].min(),
                df['Volume'].max(),
                df['Volume'].skew(),
                df['Volume'].kurtosis()
            ]
        })
        
        # Formata valores
        format_dict = {
            'Preço': lambda x: f"{x:.2f}",
            'Volume': lambda x: f"{x:,.0f}"
        }
        
        self.add_table(
            stats,
            "Estatísticas Descritivas",
            format_dict=format_dict
        )
        
    def _add_returns_analysis(self, ticker: str) -> None:
        """
        Adiciona seção com análise de retornos.
        
        Parameters
        ----------
        ticker : str
            Símbolo do ativo
        """
        self.add_section("Análise de Retornos", level=2)
        
        # Distribuição dos retornos
        if self.include_plots:
            fig = self.visualizadores[ticker].plot_retornos(tipo='log')
            self.add_plot(
                fig,
                "Distribuição dos Retornos",
                level=3
            )
            plt.close()
            
        # Estatísticas dos retornos
        if self.include_tables:
            # Calcula retornos logarítmicos
            df = self.ticker_data[ticker]
            returns = np.log(df['Close'] / df['Close'].shift(1))
            
            stats = pd.DataFrame({
                'Métrica': [
                    'Retorno Médio Diário',
                    'Retorno Médio Anualizado',
                    'Volatilidade Diária',
                    'Volatilidade Anualizada',
                    'Índice Sharpe',
                    'Assimetria',
                    'Curtose'
                ],
                'Valor': [
                    returns.mean(),
                    returns.mean() * 252,
                    returns.std(),
                    returns.std() * np.sqrt(252),
                    (returns.mean() * 252) / (returns.std() * np.sqrt(252)),
                    returns.skew(),
                    returns.kurtosis()
                ]
            })
            
            format_dict = {
                'Valor': lambda x: (
                    f"{x:.2%}" if "Retorno" in stats.loc[stats['Valor'] == x, 'Métrica'].iloc[0]
                    else f"{x:.4f}"
                )
            }
            
            self.add_table(
                stats,
                "Estatísticas dos Retornos",
                format_dict=format_dict
            )
            
    def _add_risk_analysis(self, ticker: str) -> None:
        """
        Adiciona seção com análise de risco.
        
        Parameters
        ----------
        ticker : str
            Símbolo do ativo
        """
        self.add_section("Análise de Risco", level=2)
        
        visualizador = self.visualizadores[ticker]
        
        if self.include_plots:
            # Volatilidade
            fig = visualizador.plot_volatilidade()
            self.add_plot(
                fig,
                "Volatilidade Móvel",
                level=3
            )
            plt.close()
            
            # Drawdown
            fig = visualizador.plot_drawdown()
            self.add_plot(
                fig,
                "Análise de Drawdown",
                level=3
            )
            plt.close()
            
        if self.include_plots:
            # Dashboard completo
            fig = visualizador.plot_dashboard(
                window_ma=self.moving_averages
            )
            self.add_plot(
                fig,
                "Dashboard Completo",
                level=2
            )
            plt.close()
