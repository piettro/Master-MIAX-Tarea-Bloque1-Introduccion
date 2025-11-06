"""
Testes unitários para a funcionalidade de dados macroeconômicos.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.core.entities.macro_series import MacroSeries
from src.extractor.macro_extractor import MacroExtractor
from src.reports.plot_macro import VisualizadorMacroSeries

class TestMacroSeries(unittest.TestCase):
    """Testes para a classe MacroSeries."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.indicators = [
            "GDP growth (annual %)",
            "Inflation, GDP deflator (annual %)"
        ]
        self.countries = ["ESP", "EUU"]
        
        # Cria dados de exemplo
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        data = {}
        for country in self.countries:
            for indicator in self.indicators:
                # Gera dados sintéticos
                if "GDP" in indicator:
                    values = np.random.normal(2.5, 1.0, len(dates))  # GDP em torno de 2.5%
                else:
                    values = np.random.normal(3.0, 0.5, len(dates))  # Inflação em torno de 3%
                data[(country, indicator)] = pd.Series(values, index=dates)
        
        self.mock_data = pd.DataFrame(data)
        
        # Mock do extrator
        self.mock_extractor = MagicMock()
        self.mock_extractor.extract.return_value = self.mock_data
        
        # Cria instância com dados mockados
        with patch('src.core.entities.macro_series.MacroExtractor') as mock:
            mock.return_value = self.mock_extractor
            self.macro = MacroSeries(
                indicators=self.indicators,
                countries=self.countries,
                start_date="2020-01-01",
                end_date="2022-12-31"
            )
    
    def test_init_validation(self):
        """Testa validações do construtor."""
        # Testa indicadores vazios
        with self.assertRaises(ValueError):
            MacroSeries(indicators=[], countries=self.countries)
        
        # Testa países vazios
        with self.assertRaises(ValueError):
            MacroSeries(indicators=self.indicators, countries=[])
        
        # Testa data final menor que inicial
        with self.assertRaises(ValueError):
            MacroSeries(
                indicators=self.indicators,
                countries=self.countries,
                start_date="2022-01-01",
                end_date="2021-01-01"
            )
    
    def test_data_loading(self):
        """Testa carregamento de dados."""
        # Verifica se os dados foram carregados corretamente
        self.assertIsInstance(self.macro.data, pd.DataFrame)
        self.assertEqual(len(self.macro.data.columns), len(self.indicators) * len(self.countries))
        
        # Verifica estrutura do MultiIndex
        self.assertEqual(self.macro.data.columns.names, ['Country', 'Indicator'])
        
        # Verifica países e indicadores
        countries = self.macro.data.columns.get_level_values('Country').unique()
        indicators = self.macro.data.columns.get_level_values('Indicator').unique()
        self.assertListEqual(list(countries), self.countries)
        self.assertListEqual(list(indicators), self.indicators)
    
    def test_get_latest_values(self):
        """Testa obtenção dos valores mais recentes."""
        latest = self.macro.get_latest_values()
        
        # Verifica estrutura
        self.assertIsInstance(latest, pd.Series)
        self.assertEqual(len(latest), len(self.indicators) * len(self.countries))
        
        # Verifica se são os últimos valores
        for col in self.macro.data.columns:
            self.assertEqual(latest[col], self.macro.data[col].iloc[-1])
    
    def test_get_changes(self):
        """Testa cálculo de variações."""
        periods = 12
        changes = self.macro.get_changes(periods=periods)
        
        # Verifica estrutura
        self.assertIsInstance(changes, pd.Series)
        self.assertEqual(len(changes), len(self.indicators) * len(self.countries))
        
        # Verifica cálculo
        for col in self.macro.data.columns:
            expected = (self.macro.data[col].iloc[-1] / 
                       self.macro.data[col].iloc[-periods-1] - 1)
            self.assertAlmostEqual(changes[col], expected)
    
    def test_get_correlations(self):
        """Testa cálculo de correlações."""
        correlations = self.macro.get_correlations()
        
        # Verifica estrutura
        self.assertIsInstance(correlations, dict)
        self.assertEqual(len(correlations), len(self.indicators))
        
        # Verifica cada matriz de correlação
        for indicator in self.indicators:
            corr_matrix = correlations[indicator]
            self.assertIsInstance(corr_matrix, pd.DataFrame)
            self.assertEqual(len(corr_matrix), len(self.countries))
            self.assertEqual(len(corr_matrix.columns), len(self.countries))
    
    def test_describe(self):
        """Testa geração de estatísticas descritivas."""
        stats = self.macro.describe()
        
        # Verifica estrutura
        self.assertIsInstance(stats, dict)
        self.assertEqual(len(stats), len(self.indicators))
        
        # Verifica estatísticas para cada indicador
        for indicator in self.indicators:
            desc = stats[indicator]
            self.assertIsInstance(desc, pd.DataFrame)
            self.assertEqual(len(desc.columns), len(self.countries))
            
            # Verifica métricas padrão
            expected_metrics = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
            self.assertListEqual(list(desc.index), expected_metrics)


class TestVisualizadorMacroSeries(unittest.TestCase):
    """Testes para a classe VisualizadorMacroSeries."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        # Cria dados de exemplo
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        self.indicator = "GDP growth (annual %)"
        values = np.random.normal(2.5, 1.0, len(dates))
        self.data = pd.DataFrame({self.indicator: values}, index=dates)
        self.viz = VisualizadorMacroSeries(self.data)
    
    def test_init_validation(self):
        """Testa validações do construtor."""
        # Testa DataFrame vazio
        with self.assertRaises(ValueError):
            VisualizadorMacroSeries(pd.DataFrame())
        
        # Testa None
        with self.assertRaises(ValueError):
            VisualizadorMacroSeries(None)
    
    def test_plot_serie_temporal(self):
        """Testa geração do gráfico de série temporal."""
        fig = self.viz.plot_serie_temporal(self.indicator)
        self.assertIsNotNone(fig)
        
        # Testa com médias móveis
        fig = self.viz.plot_serie_temporal(self.indicator, window_ma=[3, 6])
        self.assertIsNotNone(fig)
        
        # Testa indicador inválido
        with self.assertRaises(ValueError):
            self.viz.plot_serie_temporal("indicador_invalido")
    
    def test_plot_variacao_anual(self):
        """Testa geração do gráfico de variação anual."""
        fig = self.viz.plot_variacao_anual(self.indicator)
        self.assertIsNotNone(fig)
        
        # Testa indicador inválido
        with self.assertRaises(ValueError):
            self.viz.plot_variacao_anual("indicador_invalido")
    
    def test_plot_sazonalidade(self):
        """Testa geração do gráfico de sazonalidade."""
        fig = self.viz.plot_sazonalidade(self.indicator)
        self.assertIsNotNone(fig)
        
        # Testa indicador inválido
        with self.assertRaises(ValueError):
            self.viz.plot_sazonalidade("indicador_invalido")
    
    def test_plot_dashboard_macro(self):
        """Testa geração do dashboard."""
        fig = self.viz.plot_dashboard_macro(self.indicator)
        self.assertIsNotNone(fig)
        
        # Testa indicador inválido
        with self.assertRaises(ValueError):
            self.viz.plot_dashboard_macro("indicador_invalido")


if __name__ == '__main__':
    unittest.main()
