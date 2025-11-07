"""
Classe para visualização de séries temporais de preços.
Implementa diversos gráficos para análise de ativos financeiros.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Union
from pathlib import Path

class VisualizadorPriceSeries:
    """
    Classe responsável pela geração de gráficos para análise de séries temporais
    de preços de ativos financeiros.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Inicializa o visualizador com os dados da série temporal.
        
        Parameters
        ----------
        data : pd.DataFrame
            DataFrame com os dados das séries temporais.
            Deve conter colunas: 'Date', 'Close', 'Open', 'High', 'Low', 'Volume'
        """
        if data is None or data.empty:
            raise ValueError("DataFrame não pode ser vazio")
            
        required_columns = ['Close', 'Open', 'High', 'Low', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Colunas ausentes no DataFrame: {missing_columns}")
            
        self.data = data.copy()
        
    def plot_precos(self, window_ma: Optional[List[int]] = None) -> plt.Figure:
        """
        Gera gráfico de preços com médias móveis opcionais.
        
        Parameters
        ----------
        window_ma : List[int], opcional
            Lista com períodos para médias móveis
            
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Preços de fechamento
        ax.plot(self.data.index, self.data['Close'], label='Preço', linewidth=1)
        
        # Médias móveis
        if window_ma:
            for window in window_ma:
                ma = self.data['Close'].rolling(window=window).mean()
                ax.plot(self.data.index, ma, 
                       label=f'Média Móvel ({window} períodos)',
                       linewidth=1, alpha=0.8)
                
        ax.set_title('Evolução do Preço e Médias Móveis')
        ax.set_xlabel('Data')
        ax.set_ylabel('Preço')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
        
    def plot_candlestick(self) -> plt.Figure:
        """
        Gera gráfico de candlestick.
        
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Converte o índice para números para plotagem
        x = np.arange(len(self.data.index))
        
        # Largura das velas (ajuste conforme necessário)
        width = 0.6
        
        # Velas de alta (close > open)
        mask_alta = self.data['Close'] > self.data['Open']
        ax.bar(x[mask_alta], 
               self.data[mask_alta]['Close'] - self.data[mask_alta]['Open'],
               bottom=self.data[mask_alta]['Open'],
               width=width, color='g', alpha=0.5)
        
        # Velas de baixa (close < open)
        mask_baixa = self.data['Close'] <= self.data['Open']
        ax.bar(x[mask_baixa],
               self.data[mask_baixa]['Close'] - self.data[mask_baixa]['Open'],
               bottom=self.data[mask_baixa]['Open'],
               width=width, color='r', alpha=0.5)
        
        # Sombras
        ax.vlines(x, self.data['Low'], self.data['High'],
                 color='black', linewidth=1)
                 
        # Configura o eixo x para mostrar as datas
        ax.set_xticks(x[::len(x)//10])  # Mostra aproximadamente 10 labels
        ax.set_xticklabels(self.data.index[::len(x)//10].strftime('%Y-%m-%d'),
                          rotation=45)
        
        ax.set_title('Gráfico de Candlestick')
        ax.set_xlabel('Data')
        ax.set_ylabel('Preço')
        ax.grid(True, alpha=0.3)
        
        return fig
        
    def plot_retornos(self, tipo: str = 'log') -> plt.Figure:
        """
        Gera gráfico de retornos e sua distribuição.
        
        Parameters
        ----------
        tipo : str
            Tipo de retorno: 'log' para log-retornos, 'simple' para retornos simples
            
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        # Calcula retornos
        if tipo == 'log':
            returns = np.log(self.data['Close'] / self.data['Close'].shift(1))
        else:
            returns = self.data['Close'].pct_change()
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[2, 1])
        
        # Série temporal dos retornos
        ax1.plot(returns.index, returns, linewidth=1, alpha=0.7)
        ax1.set_title(f'{"Log-" if tipo == "log" else ""}Retornos Diários')
        ax1.set_xlabel('Data')
        ax1.set_ylabel('Retorno')
        ax1.grid(True, alpha=0.3)
        
        # Histograma dos retornos
        sns.histplot(data=returns, ax=ax2, bins=50, stat='density', alpha=0.6)
        sns.kdeplot(data=returns, ax=ax2, color='red', linewidth=2)
        
        ax2.set_title('Distribuição dos Retornos')
        ax2.set_xlabel('Retorno')
        ax2.set_ylabel('Densidade')
        
        plt.tight_layout()
        return fig
        
    def plot_volume(self) -> plt.Figure:
        """
        Gera gráfico de volume negociado.
        
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        fig, ax = plt.subplots(figsize=(12, 4))
        
        # Volume com cores baseadas na variação do preço
        cores = np.where(self.data['Close'] > self.data['Open'], 'g', 'r')
        ax.bar(self.data.index, self.data['Volume'], color=cores, alpha=0.5)
        
        ax.set_title('Volume de Negociação')
        ax.set_xlabel('Data')
        ax.set_ylabel('Volume')
        ax.grid(True, alpha=0.3)
        
        return fig
        
    def plot_volatilidade(self, window: int = 21) -> plt.Figure:
        """
        Gera gráfico de volatilidade móvel.
        
        Parameters
        ----------
        window : int
            Janela para cálculo da volatilidade
            
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        # Calcula log-retornos
        returns = np.log(self.data['Close'] / self.data['Close'].shift(1))
        
        # Calcula volatilidade móvel (anualizada)
        vol = returns.rolling(window=window).std() * np.sqrt(252)
        
        fig, ax = plt.subplots(figsize=(12, 4))
        
        ax.plot(vol.index, vol, linewidth=1)
        ax.set_title(f'Volatilidade Móvel ({window} dias)')
        ax.set_xlabel('Data')
        ax.set_ylabel('Volatilidade Anualizada')
        ax.grid(True, alpha=0.3)
        
        return fig
        
    def plot_drawdown(self) -> plt.Figure:
        """
        Gera gráfico de drawdown.
        
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        # Calcula drawdown
        roll_max = self.data['Close'].expanding().max()
        drawdown = (self.data['Close'] - roll_max) / roll_max
        
        fig, ax = plt.subplots(figsize=(12, 4))
        
        ax.fill_between(drawdown.index, drawdown, 0, color='r', alpha=0.3)
        ax.plot(drawdown.index, drawdown, color='r', linewidth=1)
        
        ax.set_title('Drawdown')
        ax.set_xlabel('Data')
        ax.set_ylabel('Drawdown (%)')
        ax.grid(True, alpha=0.3)
        
        return fig
        
    def plot_dashboard(self, window_ma: Optional[List[int]] = [20, 50]) -> plt.Figure:
        """
        Gera um dashboard completo com principais gráficos.
        
        Parameters
        ----------
        window_ma : List[int], opcional
            Lista com períodos para médias móveis
            
        Returns
        -------
        plt.Figure
            Figura com o dashboard
        """
        fig = plt.figure(figsize=(15, 12))
        gs = fig.add_gridspec(3, 2)
        
        # Preços e Médias Móveis
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(self.data.index, self.data['Close'], label='Preço', linewidth=1)
        if window_ma:
            for window in window_ma:
                ma = self.data['Close'].rolling(window=window).mean()
                ax1.plot(self.data.index, ma,
                        label=f'MA({window})',
                        linewidth=1, alpha=0.8)
        ax1.set_title('Preço e Médias Móveis')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Volume
        ax2 = fig.add_subplot(gs[1, 0])
        cores = np.where(self.data['Close'] > self.data['Open'], 'g', 'r')
        ax2.bar(self.data.index, self.data['Volume'], color=cores, alpha=0.5)
        ax2.set_title('Volume')
        ax2.grid(True, alpha=0.3)
        
        # Retornos
        ax3 = fig.add_subplot(gs[1, 1])
        returns = np.log(self.data['Close'] / self.data['Close'].shift(1))
        ax3.plot(returns.index, returns, linewidth=1, alpha=0.7)
        ax3.set_title('Log-Retornos')
        ax3.grid(True, alpha=0.3)
        
        # Volatilidade
        ax4 = fig.add_subplot(gs[2, 0])
        vol = returns.rolling(window=21).std() * np.sqrt(252)
        ax4.plot(vol.index, vol, linewidth=1)
        ax4.set_title('Volatilidade (21 dias)')
        ax4.grid(True, alpha=0.3)
        
        # Drawdown
        ax5 = fig.add_subplot(gs[2, 1])
        roll_max = self.data['Close'].expanding().max()
        drawdown = (self.data['Close'] - roll_max) / roll_max
        ax5.fill_between(drawdown.index, drawdown, 0, color='r', alpha=0.3)
        ax5.plot(drawdown.index, drawdown, color='r', linewidth=1)
        ax5.set_title('Drawdown')
        ax5.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
