"""
Classe para visualização de séries temporais macroeconômicas.
Implementa diversos gráficos para análise de indicadores macro.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Union
from pathlib import Path
from statsmodels.tsa.seasonal import seasonal_decompose

class VisualizadorMacroSeries:
    """
    Classe responsável pela geração de gráficos para análise de séries temporais
    de indicadores macroeconômicos.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Inicializa o visualizador com os dados da série temporal.
        
        Parameters
        ----------
        data : pd.DataFrame
            DataFrame com os dados das séries temporais.
            Deve conter pelo menos as colunas: 'Date' e valores dos indicadores
        """
        if data is None or data.empty:
            raise ValueError("DataFrame não pode ser vazio")
            
        self.data = data.copy()
        
        # Converte PeriodIndex para DatetimeIndex se necessário
        if isinstance(self.data.index, pd.PeriodIndex):
            self.data.index = self.data.index.to_timestamp()
        elif not isinstance(self.data.index, pd.DatetimeIndex):
            try:
                self.data.index = pd.to_datetime(self.data.index)
            except Exception as e:
                raise ValueError(f"Não foi possível converter o índice para datetime: {e}")
        
    def plot_serie_temporal(self) -> plt.Figure:
        """
        Gera gráfico de série temporal para todos os países.
        
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot para cada país
        for country in self.data.columns:
            # Série temporal
            ax.plot(self.data.index, self.data[country], label=country, linewidth=1)
                
        ax.set_title('Evolução da Série Temporal')
        ax.set_xlabel('Data')
        ax.set_ylabel('Valor')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return fig
        
    def plot_variacao_anual(self) -> plt.Figure:
        """
        Gera gráfico de variação anual para todos os países.
        
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Para cada país, plota a variação anual
        for country in self.data.columns:
            # Calcula variação em relação ao ano anterior
            var_anual = self.data[country].pct_change(periods=1) * 100
            var_anual = var_anual.dropna()
            
            if not var_anual.empty:
                # Plot linha com markers
                ax.plot(var_anual.index.astype(str), var_anual, 
                       marker='o', label=country, alpha=0.7)
        
        # Adiciona linha horizontal no zero
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        # Formata o gráfico
        ax.set_title('Variação Anual')
        ax.set_xlabel('Ano')
        ax.set_ylabel('Variação (%)')
        
        # Rotaciona labels do eixo x para melhor visualização
        plt.xticks(rotation=45)
        
        # Adiciona valores em cima das barras
        for i, v in enumerate(var_anual):
            ax.text(i, v + (0.5 if v >= 0 else -2), 
                   f'{v:.1f}%', 
                   ha='center', 
                   va='bottom' if v >= 0 else 'top')
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()  # Ajusta o layout para evitar cortes
        
        return fig
        
    def plot_correlacao_temporal(self, indicadores: List[str], 
                               window: int = 12) -> plt.Figure:
        """
        Gera gráfico de correlação móvel entre indicadores.
        
        Parameters
        ----------
        indicadores : List[str]
            Lista com nomes das colunas dos indicadores a serem correlacionados
        window : int
            Janela para cálculo da correlação móvel
            
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        if len(indicadores) != 2:
            raise ValueError("Deve fornecer exatamente 2 indicadores")
            
        for ind in indicadores:
            if ind not in self.data.columns:
                raise ValueError(f"Indicador {ind} não encontrado nos dados")
                
        # Calcula correlação móvel
        corr = self.data[indicadores[0]].rolling(window).corr(self.data[indicadores[1]])
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(self.data.index, corr, linewidth=1)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        ax.set_title(f'Correlação Móvel ({window} períodos)\n{indicadores[0]} vs {indicadores[1]}')
        ax.set_xlabel('Data')
        ax.set_ylabel('Correlação')
        ax.grid(True, alpha=0.3)
        
        return fig
        
    def plot_scatter_indicadores(self, x: str, y: str) -> plt.Figure:
        """
        Gera gráfico de dispersão entre dois indicadores.
        
        Parameters
        ----------
        x : str
            Nome da coluna do indicador para o eixo x
        y : str
            Nome da coluna do indicador para o eixo y
            
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """
        if x not in self.data.columns or y not in self.data.columns:
            raise ValueError("Indicadores não encontrados nos dados")
            
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Scatter plot com linha de tendência
        sns.regplot(data=self.data, x=x, y=y, ax=ax,
                   scatter_kws={'alpha':0.5}, line_kws={'color': 'red'})
        
        ax.set_title(f'Relação entre {x} e {y}')
        ax.grid(True, alpha=0.3)
        
        return fig
        
    def plot_decomposicao(self, indicador: str) -> plt.Figure:
        """
        Gera gráfico de decomposição da série temporal.
        
        Parameters
        ----------
        indicador : str
            Nome da coluna do indicador a ser decomposto
            
        Returns
        -------
        plt.Figure
            Figura com o gráfico gerado
        """        
        if indicador not in self.data.columns:
            raise ValueError(f"Indicador {indicador} não encontrado nos dados")
            
        # Realiza decomposição
        decomposicao = seasonal_decompose(self.data[indicador], period=12)
        
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 10))
        
        # Série original
        ax1.plot(self.data.index, decomposicao.observed)
        ax1.set_title('Série Original')
        ax1.grid(True, alpha=0.3)
        
        # Tendência
        ax2.plot(self.data.index, decomposicao.trend)
        ax2.set_title('Tendência')
        ax2.grid(True, alpha=0.3)
        
        # Sazonalidade
        ax3.plot(self.data.index, decomposicao.seasonal)
        ax3.set_title('Sazonalidade')
        ax3.grid(True, alpha=0.3)
        
        # Resíduos
        ax4.plot(self.data.index, decomposicao.resid)
        ax4.set_title('Resíduos')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
        
    def plot_dashboard_macro(self, indicador: str) -> plt.Figure:
        """
        Gera um dashboard completo para análise do indicador.
        
        Parameters
        ----------
        indicador : str
            Nome da coluna do indicador a ser analisado
            
        Returns
        -------
        plt.Figure
            Figura com o dashboard
        """
        if indicador not in self.data.columns:
            raise ValueError(f"Indicador {indicador} não encontrado nos dados")
            
        fig = plt.figure(figsize=(15, 12))
        gs = fig.add_gridspec(3, 2)
        
        # Série temporal
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(self.data.index, self.data[indicador], label='Valor', linewidth=1)
        ax1.set_title(f'Evolução do {indicador}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Variação anual
        ax2 = fig.add_subplot(gs[1, 0])
        var_anual = self.data[indicador].pct_change(periods=12) * 100
        cores = np.where(var_anual >= 0, 'g', 'r')
        ax2.bar(self.data.index, var_anual, color=cores, alpha=0.5)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_title('Variação Anual')
        ax2.grid(True, alpha=0.3)
        
        # Histograma
        ax3 = fig.add_subplot(gs[1, 1])
        sns.histplot(data=self.data[indicador], ax=ax3, bins=30, 
                    stat='density', alpha=0.6)
        sns.kdeplot(data=self.data[indicador], ax=ax3, color='red', linewidth=2)
        ax3.set_title('Distribuição dos Valores')
        ax3.grid(True, alpha=0.3)
        
        # Sazonalidade
        ax4 = fig.add_subplot(gs[2, 0])
        self.data['Mês'] = self.data.index.month
        medias_mensais = self.data.groupby('Mês')[indicador].mean()
        
        # Preenche meses faltantes com NaN
        todos_meses = pd.Series(index=range(1, 13), dtype=float)
        medias_mensais = medias_mensais.reindex(todos_meses.index)
        
        # Plota apenas meses com dados
        meses_com_dados = medias_mensais.dropna().index
        valores_com_dados = medias_mensais.dropna().values
        
        if len(meses_com_dados) > 0:
            ax4.plot(meses_com_dados, valores_com_dados, marker='o')
        ax4.set_title('Padrão Sazonal')
        ax4.set_xticks(range(1, 13))
        ax4.grid(True, alpha=0.3)
        self.data.drop('Mês', axis=1, inplace=True)
        
        # Box plot mensal
        ax5 = fig.add_subplot(gs[2, 1])
        self.data['Mês'] = self.data.index.month
        
        # Verifica se há dados suficientes para o boxplot
        meses_unicos = self.data['Mês'].unique()
        if len(meses_unicos) > 1:  # Precisa de pelo menos 2 meses diferentes
            sns.boxplot(data=self.data, x='Mês', y=indicador, ax=ax5)
        else:
            ax5.text(0.5, 0.5, 'Dados insuficientes para boxplot',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax5.transAxes)
        ax5.set_title('Distribuição Mensal')
        ax5.grid(True, alpha=0.3)
        self.data.drop('Mês', axis=1, inplace=True)
        
        plt.tight_layout()
        return fig
