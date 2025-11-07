"""
Relatório especializado para análise de séries macroeconômicas.
Gera relatórios completos com visualizações e análises de indicadores.
"""

from pathlib import Path
from typing import Any, Optional, List, Union

from src.core.entities.macro_series import MacroSeries
from src.reports.report_base import BaseReport
from src.plots.plot_macro import VisualizadorMacroSeries
import pandas as pd

class MacroReport(BaseReport):
    def __init__(
        self,
        macro_series: MacroSeries,  
        titulo: str = "Relatório de Análise Macroeconômica",
        include_plots: bool = True,
        include_tables: bool = True
    ):
        super().__init__(
            titulo=titulo,
            include_plots=include_plots,
            include_tables=include_tables
        )

        self.macro_series = macro_series
        self.data = macro_series.data

        if not isinstance(self.data.columns, pd.MultiIndex) or \
           self.data.columns.names != ['Country', 'Indicator']:
            raise ValueError("DataFrame esperado com MultiIndex nas colunas: ['Country', 'Indicator']")
        
        self.countries = self.data.columns.get_level_values('Country').unique().tolist()
        self.indicators = self.data.columns.get_level_values('Indicator').unique().tolist()
        self.visualizadores = {}

    def _prepare_indicator_data(self, indicator: str) -> pd.DataFrame:
        """
        Prepara DataFrame para um indicador, incluindo todos os países.
        """
        try:
            # Seleciona todos os países para o indicador
            df = self.data.xs(indicator, level='Indicator', axis=1)
            
            # Remove valores nulos
            df = df.dropna(how='all')
            
            if df.empty:
                raise ValueError(f"Sem dados válidos para o indicador {indicator}")
            
            # Converte índice para período anual
            df.index = pd.PeriodIndex(df.index, freq='Y')
            
            return df
            
        except Exception as e:
            raise ValueError(f"Erro ao preparar dados para {indicator}: {str(e)}")

    def _add_info_section(self, indicator: str) -> None:
        df = self._prepare_indicator_data(indicator)
        
        # Ordena o índice
        df = df.sort_index()
        
        # Pega os anos inicial e final
        start = str(df.index.min())
        end = str(df.index.max())
        
        # Informações por país
        info_paises = []
        for country in df.columns:
            series = df[country].dropna()
            if not series.empty:
                inicial = series.iloc[0]
                final = series.iloc[-1]
                if pd.notna(inicial) and pd.notna(final) and inicial != 0:
                    variacao = f"{(final/inicial - 1)*100:.2f}%"
                else:
                    variacao = "N/A"
                info_paises.append(f"- **{country}**: {variacao}")
        
        self.add_section(
            f"Informações do Indicador: {indicator}",
            f"### Período de Análise\n"
            f"- De: {start}\n"
            f"- Até: {end}\n\n"
            f"### Variação Total por País\n" +
            "\n".join(info_paises),
            level=2
        )

    def _add_statistical_analysis(self, indicator: str) -> None:
        df = self._prepare_indicator_data(indicator)
        # Calcula estatísticas para cada país
        stats_list = []
        for country in df.columns:
            stats = df[country].describe()
            stats.name = country
            stats_list.append(stats)
        
        stats_df = pd.concat(stats_list, axis=1)
        stats_df = stats_df.reset_index(names='Stats')
        
        self.add_table(
            stats_df,
            f"Estatísticas Descritivas: {indicator}",
            level=3,
            format_dict={col: (lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x) for col in stats_df.columns}
        )

    def _add_variation_analysis(self, indicator: str) -> None:
        df = self._prepare_indicator_data(indicator)
        # Calcula variação para cada país
        variations_list = []
        for country in df.columns:
            var = df[country].pct_change(periods=1).dropna()
            if not var.empty:
                stats = var.describe()
                stats.name = country
                variations_list.append(stats)
            
        if variations_list:
            variations_df = pd.concat(variations_list, axis=1)
            variations_df = variations_df.reset_index(names='Stats')
            self.add_table(
                variations_df,
                f"Variação Percentual Anual: {indicator}",
                level=3,
                format_dict={col: (lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x) for col in variations_df.columns}
            )
        else:
            self.add_section(
                f"Variação Percentual Anual: {indicator}",
                "Não há dados suficientes para calcular as variações anuais.",
                level=3
            )

    def _add_visualizations(self, indicator: str) -> None:
        df = self._prepare_indicator_data(indicator)
        viz = VisualizadorMacroSeries(df)

        if self.include_plots:
            # Gráfico de série temporal com todos os países
            fig1 = viz.plot_serie_temporal()
            self.add_plot(fig1, f"Série Temporal - {indicator}", level=3)

            # Gráfico de variação anual com todos os países
            try:
                fig2 = viz.plot_variacao_anual()
                self.add_plot(fig2, f"Variação Anual - {indicator}", level=3)
            except Exception as e:
                self.add_section(
                    f"Aviso - Variação Anual {indicator}",
                    f"Não foi possível gerar o gráfico de variação anual: {str(e)}",
                    level=3
                )

            # Para decomposição e sazonalidade, ainda fazemos por país pois são análises específicas
            for country in df.columns:
                country_df = pd.DataFrame({country: df[country]})
                country_viz = VisualizadorMacroSeries(country_df)

                fig3 = country_viz.plot_decomposicao(indicador=country)
                self.add_plot(fig3, f"Decomposição: {indicator} - {country}", level=3)

    def _add_correlation_analysis(self, indicator: str) -> None:
        """
        Realiza análise de correlação entre países para um indicador.
        """
        try:
            # Extrai dados para o indicador específico
            df_corr = self.data.xs(indicator, level='Indicator', axis=1)
            
            # Remove valores nulos antes do cálculo de correlação
            df_corr = df_corr.dropna()
            
            if df_corr.empty:
                raise ValueError(f"Sem dados válidos para correlação do indicador {indicator}")
                
            # Calcula correlação
            corr = df_corr.corr().round(3)  # Arredonda para 3 casas decimais
            
            # Adiciona tabela de correlação
            self.add_table(
                corr,
                f"Matriz de Correlação entre Países ({indicator})",
                level=3,
                format_dict={col: lambda x: f"{x:.3f}" for col in corr.columns}
            )
            
            # Adiciona visualização
            if self.include_plots:
                import seaborn as sns
                import matplotlib.pyplot as plt
                
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(
                    corr, 
                    annot=True, 
                    cmap='coolwarm',
                    center=0,
                    fmt='.3f',
                    ax=ax
                )
                ax.set_title(f"Heatmap de Correlação: {indicator}")
                plt.tight_layout()
                self.add_plot(fig, f"Heatmap de Correlação: {indicator}", level=3)
                
        except Exception as e:
            self.add_section(
                f"Erro na Análise de Correlação ({indicator})",
                f"Não foi possível gerar a análise de correlação: {str(e)}",
                level=3
            )

    def generate(self, auto_save: bool = True) -> Union[str, Path]:
        """
        Gera o conteúdo do relatório macroeconômico e opcionalmente salva em arquivo.
        
        Parameters
        ----------
        auto_save : bool, opcional
            Se True, salva automaticamente o relatório após gerar (default: True)
            
        Returns
        -------
        Union[str, Path]
            Se auto_save=True: Path do arquivo salvo
            Se auto_save=False: Conteúdo do relatório em formato Markdown
        """
        # Limpa seções anteriores
        self.sections = []
        
        relatorios_gerados = []
        for indicator in self.indicators:
            try:
                self._add_info_section(indicator)
                self._add_statistical_analysis(indicator)
                self._add_variation_analysis(indicator)
                self._add_visualizations(indicator)
                self._add_correlation_analysis(indicator)
                relatorios_gerados.append(indicator)
            except Exception as e:
                self.add_section(
                    f"Erro ao processar {indicator}",
                    f"Detalhes: {str(e)}",
                    level=3
                )
            self.add_section("---", "", level=1)

        if auto_save:
            return self.save(custom_name=self.macro_series.name)

        full_report = []
        for section in self.sections:
            if section['level'] > 0:
                full_report.append(f"{'#' * section['level']} {section['title']}")
            if section['content']:
                full_report.append(section['content'])
            full_report.append("")
            
        return "\n".join(full_report)