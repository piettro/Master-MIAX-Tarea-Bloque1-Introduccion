"""
Classe para visualização de análises de portfolio.
Implementa diversos gráficos para análise de carteiras de investimento.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Union
from pathlib import Path

class VisualizadorPortfolio:
    """
    Classe responsável pela geração de gráficos para análise de portfolios
    e carteiras de investimento.
    """
    
    def __init__(self, returns: pd.DataFrame, weights: Dict[str, float]):
        """
        Inicializa o visualizador com os dados do portfolio.
        
        Parameters
        ----------
        returns : pd.DataFrame
            DataFrame com os retornos dos ativos.
            Index deve ser as datas e colunas os ativos.
        weights : Dict[str, float]
            Dicionário com os pesos dos ativos no portfolio
        """
        if returns is None or returns.empty:
            raise ValueError("DataFrame de retornos não pode ser vazio")
            
        if not weights or sum(weights.values()) != 1:
            raise ValueError("Pesos devem somar 1")
            
        self.returns = returns.copy()
        self.weights = weights
        
        # Calcula retorno do portfolio
        self.portfolio_returns = pd.DataFrame(
            {
                'Portfolio': np.sum([
                    returns[asset] * weight 
                    for asset, weight in weights.items()
                ], axis=0)
            }
        )
        
    def plot_alocacao(self) -> plt.Figure:
        """
        Gera gráfico de alocação do portfolio (pie chart).
        
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Ordena os pesos para melhor visualização
        sorted_weights = dict(
            sorted(self.weights.items(), key=lambda x: x[1], reverse=True)
        )
        
        # Gera o gráfico de pizza
        wedges, texts, autotexts = ax.pie(
            sorted_weights.values(),
            labels=sorted_weights.keys(),
            autopct='%1.1f%%',
            textprops={'fontsize': 10}
        )
        
        ax.set_title('Alocação do Portfolio')
        plt.setp(autotexts, size=8, weight="bold")
        plt.setp(texts, size=10)
        
        return fig
        
    def plot_evolucao_portfolio(self) -> plt.Figure:
        """
        Gera gráfico de evolução do valor do portfolio.
        
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Calcula valor acumulado (1 + retorno)
        portfolio_value = (1 + self.portfolio_returns).cumprod()
        ax.plot(portfolio_value.index, portfolio_value['Portfolio'],
                label='Portfolio', linewidth=2)
        
        ax.set_title('Evolução do Portfolio')
        ax.set_xlabel('Data')
        ax.set_ylabel('Valor (Base 1.0)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
        
    def plot_correlacao(self) -> plt.Figure:
        """
        Gera mapa de calor com correlações entre ativos.
        
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Calcula matriz de correlação
        corr = self.returns.corr()
        
        # Gera heatmap
        sns.heatmap(
            corr,
            annot=True,
            cmap='coolwarm',
            center=0,
            square=True,
            fmt='.2f',
            ax=ax
        )
        
        ax.set_title('Correlação entre Ativos')
        
        return fig
        
    def plot_retornos_distribuicao(self) -> plt.Figure:
        """
        Gera gráfico de distribuição dos retornos do portfolio.
        
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[2, 1])
        
        # Série temporal dos retornos
        ax1.plot(self.portfolio_returns.index,
                self.portfolio_returns['Portfolio'],
                linewidth=1, alpha=0.7)
        ax1.set_title('Retornos do Portfolio')
        ax1.set_xlabel('Data')
        ax1.set_ylabel('Retorno')
        ax1.grid(True, alpha=0.3)
        
        # Histograma dos retornos
        sns.histplot(
            data=self.portfolio_returns['Portfolio'],
            ax=ax2,
            bins=50,
            stat='density',
            alpha=0.6
        )
        sns.kdeplot(
            data=self.portfolio_returns['Portfolio'],
            ax=ax2,
            color='red',
            linewidth=2
        )
        
        ax2.set_title('Distribuição dos Retornos')
        ax2.set_xlabel('Retorno')
        ax2.set_ylabel('Densidade')
        
        plt.tight_layout()
        return fig
        
    def plot_drawdown(self) -> plt.Figure:
        """
        Gera gráfico de drawdown do portfolio.
        
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        # Calcula valor acumulado
        portfolio_value = (1 + self.portfolio_returns).cumprod()
        
        # Calcula drawdown
        roll_max = portfolio_value.expanding().max()
        drawdown = (portfolio_value - roll_max) / roll_max
        
        fig, ax = plt.subplots(figsize=(12, 4))
        
        ax.fill_between(
            drawdown.index,
            drawdown['Portfolio'],
            0,
            color='r',
            alpha=0.3
        )
        ax.plot(drawdown.index, drawdown['Portfolio'],
                color='r', linewidth=1)
        
        ax.set_title('Drawdown do Portfolio')
        ax.set_xlabel('Data')
        ax.set_ylabel('Drawdown (%)')
        ax.grid(True, alpha=0.3)
        
        return fig
        
    def plot_contribuicao_risco(self) -> plt.Figure:
        """
        Gera gráfico de contribuição ao risco por ativo.
        
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Calcula volatilidade individual dos ativos
        vol = self.returns.std() * np.sqrt(252)
        
        # Calcula contribuição ao risco
        risk_contrib = pd.Series({
            asset: weight * vol[asset]
            for asset, weight in self.weights.items()
        })
        
        # Normaliza para porcentagem
        risk_contrib = risk_contrib / risk_contrib.sum() * 100
        
        # Ordena para melhor visualização
        risk_contrib = risk_contrib.sort_values(ascending=True)
        
        # Gera gráfico de barras horizontais
        ax.barh(range(len(risk_contrib)),
                risk_contrib.values,
                alpha=0.6)
        
        ax.set_yticks(range(len(risk_contrib)))
        ax.set_yticklabels(risk_contrib.index)
        ax.set_title('Contribuição ao Risco por Ativo')
        ax.set_xlabel('Contribuição (%)')
        
        # Adiciona valores nas barras
        for i, v in enumerate(risk_contrib.values):
            ax.text(v, i, f'{v:.1f}%', va='center')
            
        return fig
        
    def plot_retorno_risco_ativos(self) -> plt.Figure:
        """
        Gera scatter plot de retorno vs risco dos ativos.
        
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Calcula retorno e risco anualizados
        returns_annual = self.returns.mean() * 252
        vol_annual = self.returns.std() * np.sqrt(252)
        
        # Scatter plot
        ax.scatter(vol_annual, returns_annual, s=100)
        
        # Adiciona labels para cada ponto
        for i, asset in enumerate(self.returns.columns):
            ax.annotate(
                asset,
                (vol_annual[i], returns_annual[i]),
                xytext=(5, 5),
                textcoords='offset points'
            )
            
        # Adiciona portfolio
        portfolio_return = self.portfolio_returns.mean() * 252
        portfolio_vol = self.portfolio_returns.std() * np.sqrt(252)
        
        ax.scatter(
            portfolio_vol,
            portfolio_return,
            s=200,
            c='red',
            marker='*',
            label='Portfolio'
        )
        
        ax.set_title('Retorno vs Risco')
        ax.set_xlabel('Risco (Volatilidade Anualizada)')
        ax.set_ylabel('Retorno Anualizado')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
        
    def plot_dashboard(self) -> plt.Figure:
        """
        Gera um dashboard completo com principais gráficos.
        
        Returns
        -------
        plt.Figure
            Figura com o dashboard
        """
        fig = plt.figure(figsize=(15, 12))
        gs = fig.add_gridspec(3, 2)
        
        # Evolução do Portfolio
        ax1 = fig.add_subplot(gs[0, :])
        portfolio_value = (1 + self.portfolio_returns).cumprod()
        ax1.plot(portfolio_value.index, portfolio_value['Portfolio'],
                label='Portfolio', linewidth=2)
        ax1.set_title('Evolução do Portfolio')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Alocação
        ax2 = fig.add_subplot(gs[1, 0])
        sorted_weights = dict(sorted(
            self.weights.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        ax2.pie(
            sorted_weights.values(),
            labels=sorted_weights.keys(),
            autopct='%1.1f%%',
            textprops={'fontsize': 8}
        )
        ax2.set_title('Alocação')
        
        # Retornos
        ax3 = fig.add_subplot(gs[1, 1])
        sns.histplot(
            data=self.portfolio_returns['Portfolio'],
            ax=ax3,
            bins=50,
            stat='density',
            alpha=0.6
        )
        sns.kdeplot(
            data=self.portfolio_returns['Portfolio'],
            ax=ax3,
            color='red',
            linewidth=2
        )
        ax3.set_title('Distribuição dos Retornos')
        
        # Correlação
        ax4 = fig.add_subplot(gs[2, 0])
        sns.heatmap(
            self.returns.corr(),
            ax=ax4,
            annot=True,
            cmap='coolwarm',
            center=0,
            fmt='.2f',
            square=True,
            cbar=False
        )
        ax4.set_title('Correlações')
        
        # Drawdown
        ax5 = fig.add_subplot(gs[2, 1])
        roll_max = portfolio_value.expanding().max()
        drawdown = (portfolio_value - roll_max) / roll_max
        ax5.fill_between(
            drawdown.index,
            drawdown['Portfolio'],
            0,
            color='r',
            alpha=0.3
        )
        ax5.plot(drawdown.index, drawdown['Portfolio'],
                color='r', linewidth=1)
        ax5.set_title('Drawdown')
        ax5.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
