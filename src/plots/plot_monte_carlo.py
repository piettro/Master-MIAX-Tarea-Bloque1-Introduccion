import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Optional, List, Tuple, Dict
from src.analysis.entities.monte_carlo_metrics import CalculadorMonteCarlo


class   VisualizadorMonteCarlo:
    """
    Classe responsável por visualizar os resultados das simulações de Monte Carlo.
    Compatível com MonteCarloPortfolio, MonteCarloRetorno e MonteCarloCombinado.
    Trabalha com o formato expandido do DataFrame de simulações que contém:
    - Ativo: nome do ativo
    - Data: data da simulação
    - Peso: peso do ativo na carteira
    - Valor: valor do ativo
    - Valor Total: soma total da carteira
    - Retorno: retorno do ativo
    - Simulação: número da simulação
    """

    def __init__(self, simulacoes: pd.DataFrame):
        """
        Parâmetros
        ----------
        simulacoes : pd.DataFrame
            DataFrame expandido com os resultados das simulações Monte Carlo.

        Observa-se que o DataFrame esperado deve conter pelo menos as colunas:
        ['Data', 'Simulação', 'Ativo', 'Peso', 'Valor', 'Valor Total', 'Retorno']
        """
        if simulacoes is None or simulacoes.empty:
            raise ValueError("DataFrame de simulações não pode ser vazio")

        required = ['Data', 'Simulação', 'Ativo', 'Peso', 'Valor', 'Valor Total', 'Retorno']
        missing = [c for c in required if c not in simulacoes.columns]
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes no DataFrame de simulações: {missing}")

        self.simulacoes = simulacoes.copy()
        self.calculador = CalculadorMonteCarlo(simulacoes)
    def plot_evolucao_valor(self, title: str = "Evolução do Valor da Carteira") -> plt.Figure:
        """
        Plota a evolução do valor total da carteira para todas as simulações.
        
        Parâmetros
        ----------
        title : str, opcional
            Título do gráfico
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.set_style("whitegrid")

        # Agrupa por Data e Simulação para obter o valor total da carteira
        valores_por_sim = self.simulacoes.groupby(['Data', 'Simulação'])['Valor Total'].first().unstack()

        # Plota todas as simulações
        for sim in valores_por_sim.columns:
            ax.plot(valores_por_sim.index, valores_por_sim[sim], alpha=0.08, color='blue')

        # Plota a média
        media = valores_por_sim.mean(axis=1)
        ax.plot(valores_por_sim.index, media, color='red', linewidth=2, label='Média')

        ax.set_title(title)
        ax.set_xlabel('Data')
        ax.set_ylabel('Valor Total da Carteira')
        ax.legend()
        fig.tight_layout()
        return fig

    def plot_distribuicao_retornos(self, title: str = "Distribuição dos Retornos") -> plt.Figure:
        """
        Plota a distribuição dos retornos da carteira para todas as simulações.
        
        Parâmetros
        ----------
        title : str, opcional
            Título do gráfico
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.set_style("whitegrid")

        # Calcula os retornos por simulação
        retornos = self.simulacoes.groupby('Simulação')['Retorno'].mean()

        # Plota o histograma
        sns.histplot(data=retornos, bins=30, kde=True, ax=ax)
        ax.axvline(retornos.mean(), color='red', linestyle='--', label=f'Média: {retornos.mean():.2%}')
        ax.set_title(title)
        ax.set_xlabel('Retorno')
        ax.set_ylabel('Frequência')
        ax.legend()
        fig.tight_layout()
        return fig

    def plot_evolucao_pesos(self, title: str = "Evolução dos Pesos dos Ativos") -> plt.Figure:
        """
        Plota a evolução dos pesos dos ativos na carteira ao longo do tempo.
        
        Parâmetros
        ----------
        title : str, opcional
            Título do gráfico
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.set_style("whitegrid")

        # Calcula a média dos pesos por data e ativo
        pesos_medios = self.simulacoes.groupby(['Data', 'Ativo'])['Peso'].mean().unstack()

        # Plota as áreas empilhadas usando o axis retornado
        pesos_medios.plot(kind='area', stacked=True, ax=ax)

        ax.set_title(title)
        ax.set_xlabel('Data')
        ax.set_ylabel('Peso na Carteira')
        ax.legend(title='Ativos', bbox_to_anchor=(1.05, 1), loc='upper left')
        fig.tight_layout()
        return fig

    def plot_metricas(self) -> plt.Figure:
        """
        Plota um resumo das principais métricas em um dashboard.
        """
        stats_basicas = self.calculador.calcular_estatisticas_basicas()
        var_cvar = self.calculador.calcular_var_cvar()
        drawdowns = self.calculador.calcular_drawdowns()

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Dashboard de Métricas', fontsize=16)

        # Retornos e Volatilidade
        stats_df = pd.DataFrame({'Valor': [stats_basicas['retorno_medio'], stats_basicas['desvio_padrao'], var_cvar['var'], var_cvar['cvar']]},
                                index=['Retorno Médio', 'Volatilidade', 'VaR 95%', 'CVaR 95%'])
        sns.barplot(data=stats_df, y=stats_df.index, x='Valor', ax=axes[0,0])
        axes[0,0].set_title('Métricas de Risco-Retorno')

        # Estatísticas por Ativo
        stats_ativos = self.calculador.calcular_estatisticas_carteira()
        sns.scatterplot(data=stats_ativos, x='Volatilidade', y='Retorno Médio', size='Peso Médio', ax=axes[0,1])
        axes[0,1].set_title('Risco-Retorno por Ativo')

        # Correlações
        corr = self.calculador.calcular_correlacoes()
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=axes[1,0])
        axes[1,0].set_title('Correlações entre Ativos')

        # Drawdowns
        vals = pd.Series(drawdowns)
        sns.barplot(x=vals.index, y=vals.values, ax=axes[1,1])
        axes[1,1].set_title('Métricas de Drawdown')
        axes[1,1].tick_params(axis='x', rotation=45)

        fig.tight_layout()
        return fig

    def plot_fronteira_eficiente(self) -> plt.Figure:
        """
        Mostra o gráfico de risco vs retorno, colorido pelo índice de Sharpe.
        Usado com MonteCarloPortfolio ou MonteCarloCombinado.
        """
        df = getattr(self, 'resultados', None)
        if df is None:
            raise ValueError("Nenhum DataFrame de resultados disponível para plotar a fronteira eficiente")

        if "Sharpe" not in df.columns:
            raise ValueError("O DataFrame precisa conter a coluna 'Sharpe'.")

        fig, ax = plt.subplots(figsize=(10, 6))
        scatter = ax.scatter(
            df["Risco_Médio"] if "Risco_Médio" in df.columns else df["Risco"],
            df["Retorno_Médio"] if "Retorno_Médio" in df.columns else df["Retorno"],
            c=df["Sharpe"],
            cmap="viridis",
            alpha=0.7,
            s=50
        )
        fig.colorbar(scatter, ax=ax, label="Índice de Sharpe")
        ax.set_title("Fronteira Eficiente Simulada (Monte Carlo)")
        ax.set_xlabel("Risco (Desvio Padrão)")
        ax.set_ylabel("Retorno Esperado")
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    def plot_distribuicao_retorno(self) -> plt.Figure:
        """
        Exibe o histograma dos retornos simulados (MonteCarloRetorno).
        """
        resultados = getattr(self, 'resultados', None)
        if isinstance(resultados, dict):
            retornos = resultados.get("retornos", None)
        elif isinstance(resultados, pd.Series):
            retornos = resultados
        else:
            raise ValueError("Resultados inválidos para plotar distribuição de retornos.")

        if retornos is None:
            raise ValueError("Nenhuma série de retornos encontrada para plotagem.")

        fig, ax = plt.subplots(figsize=(9, 5))
        sns.histplot(retornos, bins=50, kde=True, color="steelblue", ax=ax)
        ax.set_title("Distribuição dos Retornos Simulados")
        ax.set_xlabel("Retorno Simulado")
        ax.set_ylabel("Frequência")
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    def plot_mapa_sharpe(self) -> plt.Figure:
        """
        Mostra um mapa de calor de Sharpe x risco x retorno (MonteCarloCombinado).
        """
        df = getattr(self, 'resultados', None)
        if df is None or not all(col in df.columns for col in ["Risco_Médio", "Retorno_Médio", "Sharpe"]):
            raise ValueError("O DataFrame deve conter colunas 'Risco_Médio', 'Retorno_Médio' e 'Sharpe'.")

        fig, ax = plt.subplots(figsize=(8, 6))
        scatter = ax.scatter(df["Risco_Médio"], df["Retorno_Médio"], c=df["Sharpe"], cmap="plasma", s=40, alpha=0.8)
        fig.colorbar(scatter, ax=ax, label="Índice de Sharpe")
        ax.set_title("Mapa de Sharpe — Monte Carlo Combinado")
        ax.set_xlabel("Risco (Desvio Padrão)")
        ax.set_ylabel("Retorno Esperado")
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    def plot_boxplot_metricas(self) -> plt.Figure:
        """
        Exibe boxplots para Sharpe, Sortino, VaR e CVaR (MonteCarloCombinado).
        """
        df = getattr(self, 'resultados', None)
        if df is None:
            raise ValueError("Nenhum DataFrame de resultados disponível para plotagem de boxplots")

        metricas = ["Sharpe", "Sortino", "VaR", "CVaR"]
        metricas_presentes = [m for m in metricas if m in df.columns]
        if not metricas_presentes:
            raise ValueError("Nenhuma métrica de risco ajustado encontrada para plotagem.")

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=df[metricas_presentes], palette="Set2", ax=ax)
        ax.set_title("Distribuição das Métricas de Risco Ajustado")
        ax.set_ylabel("Valor")
        ax.grid(True, linestyle="--", alpha=0.3)
        return fig

    def plot_correlation_matrix(self, retornos_ativos: pd.DataFrame) -> plt.Figure:
        """
        Exibe a matriz de correlação dos retornos dos ativos.
        
        Parâmetros
        ----------
        retornos_ativos : pd.DataFrame
            DataFrame contendo os retornos diários dos ativos.
        """
        corr = retornos_ativos.corr()

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', square=True, cbar_kws={"shrink": .8}, ax=ax)
        ax.set_title("Matriz de Correlação dos Retornos dos Ativos")
        return fig

    def plot_simulation(self, sims: np.ndarray) -> plt.Figure:
        """
        Plota as simulações de Monte Carlo ao longo do tempo.
        
        Parâmetros
        ----------
        sims : np.ndarray
            Matriz de simulações (linhas = dias, colunas = simulações).
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        # Se sims for 2D (dias x simulações), plotar cada simulação
        if sims.ndim == 2:
            ax.plot(sims, color="lightgray", alpha=0.3)
        else:
            ax.plot(sims, color="lightgray", alpha=0.7)

        ax.set_title("Simulações de Monte Carlo ao Longo do Tempo")
        ax.set_xlabel("Dias")
        ax.set_ylabel("Valor da Carteira")
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    def plot_final_distribution(self, sims: np.ndarray) -> plt.Figure:
        """
        Plota a distribuição dos valores finais das simulações.
        
        Parâmetros
        ----------
        sims : np.ndarray
            Matriz de simulações (linhas = dias, colunas = simulações).
        """
        final_values = sims[-1, :]

        fig, ax = plt.subplots(figsize=(9, 5))
        sns.histplot(final_values, bins=50, kde=True, color="coral", ax=ax)
        ax.set_title("Distribuição dos Valores Finais das Simulações")
        ax.set_xlabel("Valor Final da Carteira")
        ax.set_ylabel("Frequência")
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    def plot_var_cvar(self, sims: np.ndarray, alpha: float = 0.05) -> plt.Figure:
        """
        Plota o VaR e CVaR das simulações.
        
        Parâmetros
        ----------
        sims : np.ndarray
            Matriz de simulações (linhas = dias, colunas = simulações).
        alpha : float
            Nível de confiança para VaR e CVaR.
        """
        final_values = sims[-1, :]
        # proteção contra divisão por zero: se sims[0, :] tiver zeros, use primeira coluna não-nula
        start_val = sims[0, :].copy()
        start_val[start_val == 0] = np.nan
        returns = final_values / start_val - 1
        returns = returns[~np.isnan(returns)]

        var = np.percentile(returns, 100 * alpha)
        cvar = returns[returns <= var].mean()

        fig, ax = plt.subplots(figsize=(9, 5))
        sns.histplot(returns, bins=50, kde=True, color="seagreen", ax=ax)
        ax.axvline(var, color="red", linestyle="--", label=f"VaR ({alpha*100:.1f}%) = {var:.2%}")
        ax.axvline(cvar, color="blue", linestyle="--", label=f"CVaR ({alpha*100:.1f}%) = {cvar:.2%}")
        ax.set_title("Distribuição dos Retornos Finais com VaR e CVaR")
        ax.set_xlabel("Retorno Final da Carteira")
        ax.set_ylabel("Frequência")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    def plot_corr_assets(self, retornos_ativos: pd.DataFrame) -> plt.Figure:
        """
        Plota a matriz de correlação dos ativos.
        
        Parâmetros
        ----------
        retornos_ativos : pd.DataFrame
            DataFrame contendo os retornos diários dos ativos.
        """
        corr = retornos_ativos.corr()

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', square=True, cbar_kws={"shrink": .8}, ax=ax)
        ax.set_title("Matriz de Correlação dos Ativos")
        return fig
