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
        include_plots : bool
            Se True, inclui visualizações
        include_tables : bool
            Se True, inclui tabelas de métricas
        moving_averages : List[int], opcional
            Lista com períodos para médias móveis
        """
        super().__init__(
            titulo=titulo,
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
        
        self.symbols = price_series.symbols if isinstance(price_series.symbols, list) else [price_series.symbols]
        self.symbol_data = {}
        self.visualizadores = {}
        
    def generate(self) -> List[Path]:
        """
        Gera relatórios individuais para cada symbol e um relatório consolidado.
        
        Returns
        -------
        List[Path]
            Lista com os caminhos de todos os relatórios gerados
        """
        saved_reports = []
        all_sections = []  # Para o relatório consolidado
        
        for symbol in self.symbols:
            print(f"\nGerando relatório para {symbol}...")
            
            # Limpa as seções anteriores para o relatório individual
            self.sections = []
            
            # Prepara dados do symbol atual
            self._prepare_symbol_data(symbol)
            
            # Adiciona cabeçalho do symbol
            self.add_section(f"Relatório: {symbol}", level=1)
            
            # Informações Básicas
            self._add_info_section(symbol)
            
            # Análise Técnica
            if self.include_plots:
                self._add_technical_analysis(symbol)
            
            # Análise Estatística
            if self.include_tables:
                self._add_statistical_analysis(symbol)
            
            # Análise de Retornos
            self._add_returns_analysis(symbol)
            
            # Análise de Risco
            self._add_risk_analysis(symbol)
            
            # Salva relatório individual
            individual_path = self.save(symbols=[symbol])
            saved_reports.append(individual_path)
            
            # Guarda as seções para o relatório consolidado
            all_sections.extend(self.sections)
            if symbol != self.symbols[-1]:
                all_sections.append({'title': '', 'content': '---\n', 'level': 0})
        
        # Gera relatório consolidado
        self.sections = all_sections
        consolidated_path = self.save(symbols=self.symbols)
        saved_reports.append(consolidated_path)
        
        print(f"\nRelatórios gerados com sucesso:")
        print(f"- Relatórios individuais: {len(self.symbols)}")
        print(f"- Relatório consolidado: 1")
        print(f"Total de relatórios: {len(saved_reports)}")
        
        return saved_reports
        
    def _prepare_symbol_data(self, symbol: str) -> None:
        """
        Prepara os dados para um symbol específico.
        
        Parameters
        ----------
        symbol : str
            Símbolo do ativo
        """
        # Se já temos os dados deste symbol, não precisamos processar novamente
        if symbol in self.symbol_data:
            return
            
        # Obtém os dados do symbol
        symbol_df = pd.DataFrame()
        for col in self.required_columns:
            symbol_df[col] = self.data[col, symbol]

        # Armazena os dados e cria visualizador
        self.symbol_data[symbol] = symbol_df
        self.visualizadores[symbol] = VisualizadorPriceSeries(symbol_df)
        
    def _add_info_section(self, symbol: str) -> None:
        """
        Adiciona seção com informações básicas do ativo.
        
        Parameters
        ----------
        symbol : str
            Símbolo do ativo
        """
        self.add_section(
            "Informações do Ativo",
            level=2
        )
        
        # Obtém informações do symbol atual
        df = self.symbol_data[symbol]
        primeiro_preco = df['Close'].iloc[0]
        ultimo_preco = df['Close'].iloc[-1]
        
        info = [
            f"- **Ativo:** {symbol}",
            f"- **Período:** {self.price_series.start_date} a {self.price_series.end_date}",
            f"- **Número de Observações:** {len(self.symbol_data)}",
            f"- **Primeiro Preço:** {primeiro_preco:.2f}",
            f"- **Último Preço:** {ultimo_preco:.2f}",
            f"- **Variação Total:** {((ultimo_preco / primeiro_preco) - 1):.2%}"
        ]
        
        self.add_section("", "\n".join(info))
        
    def _add_technical_analysis(self, symbol: str) -> None:
        """
        Adiciona seção com análise técnica.
        
        Parameters
        ----------
        symbol : str
            Símbolo do ativo
        """
        self.add_section("Análise Técnica", level=2)
        
        visualizador = self.visualizadores[symbol]
        
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
        
    def _add_statistical_analysis(self, symbol: str) -> None:
        """
        Adiciona seção com análise estatística.
        
        Parameters
        ----------
        symbol : str
            Símbolo do ativo
        """
        self.add_section("Análise Estatística", level=2)
        df = self.symbol_data[symbol]
        
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
            'Close': [
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
        
    def _add_returns_analysis(self, symbol: str) -> None:
        """
        Adiciona seção com análise de retornos.
        
        Parameters
        ----------
        symbol : str
            Símbolo do ativo
        """
        self.add_section("Análise de Retornos", level=2)
        
        # Distribuição dos retornos
        if self.include_plots:
            fig = self.visualizadores[symbol].plot_retornos(tipo='log')
            self.add_plot(
                fig,
                "Distribuição dos Retornos",
                level=3
            )
            plt.close()
            
        # Estatísticas dos retornos
        if self.include_tables:
            # Calcula retornos logarítmicos
            df = self.symbol_data[symbol]
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
            
    def _add_risk_analysis(self, symbol: str) -> None:
        """
        Adiciona seção com análise de risco.
        
        Parameters
        ----------
        symbol : str
            Símbolo do ativo
        """
        self.add_section("Análise de Risco", level=2)
        
        visualizador = self.visualizadores[symbol]
        
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
