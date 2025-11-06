import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

class CalculadorMonteCarlo:
    """
    Classe responsável pelos cálculos estatísticos das simulações Monte Carlo.
    Trabalha com o formato expandido do DataFrame de simulações.
    """
    
    def __init__(self, simulacoes: pd.DataFrame):
        """
        Parâmetros
        ----------
        simulacoes : pd.DataFrame
            DataFrame expandido com os resultados das simulações Monte Carlo.
        """
        if simulacoes is None or simulacoes.empty:
            raise ValueError("DataFrame de simulações não pode ser vazio")
            
        self.simulacoes = simulacoes
        
    def calcular_estatisticas_basicas(self) -> Dict[str, float]:
        """
        Calcula estatísticas básicas das simulações.
        
        Retorna
        -------
        Dict[str, float]
            Dicionário com estatísticas básicas (média, mediana, desvio padrão, etc.)
        """
        retornos = self.simulacoes.groupby('Simulação')['Retorno'].mean()
        
        return {
            'retorno_medio': retornos.mean(),
            'retorno_mediano': retornos.median(),
            'desvio_padrao': retornos.std(),
            'retorno_minimo': retornos.min(),
            'retorno_maximo': retornos.max()
        }
        
    def calcular_var_cvar(self, nivel_confianca: float = 0.95) -> Dict[str, float]:
        """
        Calcula o Value at Risk (VaR) e Conditional Value at Risk (CVaR)
        
        Parâmetros
        ----------
        nivel_confianca : float
            Nível de confiança para o cálculo (ex: 0.95 para 95%)
            
        Retorna
        -------
        Dict[str, float]
            Dicionário com VaR e CVaR calculados
        """
        retornos = self.simulacoes.groupby('Simulação')['Retorno'].mean()
        percentil = 100 * (1 - nivel_confianca)
        var = np.percentile(retornos, percentil)
        cvar = retornos[retornos <= var].mean()
        
        return {
            'var': var,
            'cvar': cvar
        }
        
    def calcular_estatisticas_carteira(self) -> pd.DataFrame:
        """
        Calcula estatísticas por ativo na carteira.
        
        Retorna
        -------
        pd.DataFrame
            DataFrame com estatísticas por ativo
        """
        stats = []
        for ativo in self.simulacoes['Ativo'].unique():
            dados_ativo = self.simulacoes[self.simulacoes['Ativo'] == ativo]
            
            peso_medio = dados_ativo['Peso'].mean()
            retorno_medio = dados_ativo['Retorno'].mean()
            vol = dados_ativo['Retorno'].std()
            
            stats.append({
                'Ativo': ativo,
                'Peso Médio': peso_medio,
                'Retorno Médio': retorno_medio,
                'Volatilidade': vol,
                'Sharpe': retorno_medio / vol if vol > 0 else 0
            })
            
        return pd.DataFrame(stats)
        
    def calcular_correlacoes(self) -> pd.DataFrame:
        """
        Calcula a matriz de correlação entre os retornos dos ativos.
        
        Retorna
        -------
        pd.DataFrame
            Matriz de correlação dos retornos
        """
        # Pivota o DataFrame para ter ativos nas colunas
        retornos_pivot = self.simulacoes.pivot_table(
            index=['Data', 'Simulação'],
            columns='Ativo',
            values='Retorno'
        )
        
        return retornos_pivot.corr()
        
    def calcular_drawdowns(self) -> Dict[str, float]:
        """
        Calcula estatísticas de drawdown da carteira.
        
        Retorna
        -------
        Dict[str, float]
            Dicionário com métricas de drawdown
        """
        valores = self.simulacoes.groupby(['Data', 'Simulação'])['Valor Total'].first().unstack()
        
        # Calcula drawdowns para cada simulação
        running_max = valores.expanding().max()
        drawdowns = (valores - running_max) / running_max
        
        return {
            'max_drawdown': drawdowns.min().min(),
            'avg_drawdown': drawdowns.mean().mean(),
            'drawdown_std': drawdowns.std().mean()
        }