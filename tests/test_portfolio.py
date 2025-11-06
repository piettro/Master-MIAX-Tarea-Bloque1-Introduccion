import unittest
from unittest.mock import patch, Mock
import pandas as pd
import numpy as np
from datetime import date, timedelta
from src.core.entities.portfolio import Portfolio
from src.core.entities.price_series import PriceSeries

class TestPortfolio(unittest.TestCase):
    """Testes para a classe Portfolio"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.start_date = date.today() - timedelta(days=30)
        self.end_date = date.today()
        
        # Mock de preços para testes
        self.mock_prices = pd.DataFrame({
            'AAPL': [150.0, 152.0, 151.0],
            'MSFT': [300.0, 305.0, 302.0]
        })
        
    def test_portfolio_initialization_single(self):
        """Testa inicialização com um único ativo"""
        portfolio = Portfolio(
            name="Test Single",
            holdings="AAPL",
            quantity=10,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        self.assertEqual(portfolio.name, "Test Single")
        self.assertEqual(len(portfolio.positions), 1)
        self.assertEqual(portfolio.positions["AAPL"], 10.0)
        
    def test_portfolio_initialization_multiple(self):
        """Testa inicialização com múltiplos ativos"""
        portfolio = Portfolio(
            name="Test Multiple",
            holdings=["AAPL", "MSFT"],
            quantity=[10, 15],
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        self.assertEqual(len(portfolio.positions), 2)
        self.assertEqual(portfolio.positions["AAPL"], 10.0)
        self.assertEqual(portfolio.positions["MSFT"], 15.0)
        
    def test_portfolio_validation(self):
        """Testa validações na inicialização"""
        # Testa quantidades diferentes do número de ativos
        with self.assertRaises(ValueError):
            Portfolio(
                name="Test Invalid",
                holdings=["AAPL", "MSFT"],
                quantity=[10]  # Deveria ter 2 quantidades
            )
            
    def test_weights_calculation(self):
        """Testa cálculo de pesos da carteira"""
        portfolio = Portfolio(
            name="Test Weights",
            holdings=["AAPL", "MSFT"],
            quantity=[10, 10]  # Quantidades iguais
        )
        
        weights = portfolio.weights()
        
        # Verifica se os pesos somam 1
        self.assertAlmostEqual(sum(weights.values()), 1.0)
        
        # Verifica se os pesos são iguais (50% cada)
        self.assertAlmostEqual(weights["AAPL"], 0.5)
        self.assertAlmostEqual(weights["MSFT"], 0.5)
        
    def test_weights_zero_position(self):
        """Testa cálculo de pesos com posição zero"""
        portfolio = Portfolio(
            name="Test Zero",
            holdings=["AAPL", "MSFT"],
            quantity=[0, 0]
        )
        
        weights = portfolio.weights()
        
        # Verifica se todos os pesos são zero
        self.assertTrue(all(w == 0.0 for w in weights.values()))
        
    @patch('src.core.entities.price_series.PriceSeries')
    def test_total_value_calculation(self, MockPriceSeries):
        """Testa cálculo do valor total da carteira"""
        # Configura o mock
        mock_series = Mock()
        mock_series.get_market_value.return_value = pd.Series({
            'AAPL': 150.0,
            'MSFT': 300.0
        })
        MockPriceSeries.return_value = mock_series
        
        portfolio = Portfolio(
            name="Test Value",
            holdings=["AAPL", "MSFT"],
            quantity=[10, 5]
        )
        
        # Valor esperado: (10 * 150) + (5 * 300) = 3000
        self.assertEqual(portfolio.total_value(), 3000.0)
        
    @patch('src.core.entities.price_series.PriceSeries')
    def test_returns_calculation(self, MockPriceSeries):
        """Testa cálculo dos retornos da carteira"""
        # Configura o mock
        mock_series = Mock()
        mock_series.get_returns.return_value = pd.DataFrame({
            'AAPL': [0.01, -0.02, 0.03],
            'MSFT': [0.02, -0.01, 0.01]
        })
        MockPriceSeries.return_value = mock_series
        
        portfolio = Portfolio(
            name="Test Returns",
            holdings=["AAPL", "MSFT"],
            quantity=[10, 5]
        )
        
        returns = portfolio.returns()
        
        self.assertIsInstance(returns, pd.DataFrame)
        self.assertEqual(len(returns.columns), 2)
        self.assertEqual(len(returns), 3)
        
    def test_total_value_per_holding(self):
        """Testa cálculo do valor por ativo"""
        with patch('src.core.entities.price_series.PriceSeries') as MockPriceSeries:
            # Configura o mock
            mock_series = Mock()
            mock_series.get_market_value.return_value = pd.Series({
                'AAPL': 150.0,
                'MSFT': 300.0
            })
            MockPriceSeries.return_value = mock_series
            
            portfolio = Portfolio(
                name="Test Holdings",
                holdings=["AAPL", "MSFT"],
                quantity=[10, 5]
            )
            
            values = portfolio.total_value_per_holding()
            
            # Verifica valores por ativo
            self.assertEqual(values['AAPL'], 1500.0)  # 10 * 150
            self.assertEqual(values['MSFT'], 1500.0)  # 5 * 300
            
    def test_portfolio_representation(self):
        """Testa a representação string do portfolio"""
        with patch('src.core.entities.price_series.PriceSeries') as MockPriceSeries:
            # Configura o mock
            mock_series = Mock()
            mock_series.get_market_value.return_value = pd.Series({
                'AAPL': 150.0,
                'MSFT': 300.0
            })
            MockPriceSeries.return_value = mock_series
            
            portfolio = Portfolio(
                name="Test Portfolio",
                holdings=["AAPL", "MSFT"],
                quantity=[10, 5]
            )
            
            repr_str = repr(portfolio)
            
            # Verifica se a representação contém informações importantes
            self.assertIn("Test Portfolio", repr_str)
            self.assertIn("2", repr_str)  # Número de posições
            self.assertIn("3000.00", repr_str)  # Valor total
            
    def test_date_validation(self):
        """Testa validação de datas"""
        # Testa data final anterior à inicial
        with self.assertRaises(Exception):
            Portfolio(
                name="Test Dates",
                holdings=["AAPL"],
                quantity=[10],
                start_date=date.today(),
                end_date=date.today() - timedelta(days=1)
            )
            
    def test_source_validation(self):
        """Testa diferentes fontes de dados"""
        valid_sources = ['yfinance', 'alpha_vantage', 'fmp']
        
        for source in valid_sources:
            portfolio = Portfolio(
                name=f"Test {source}",
                holdings=["AAPL"],
                quantity=[10],
                source=source
            )
            self.assertEqual(portfolio.source, source)
            
class TestPortfolioIntegration(unittest.TestCase):
    """Testes de integração para Portfolio"""
    
    def setUp(self):
        """Setup para testes de integração"""
        self.portfolio = Portfolio(
            name="Integration Test",
            holdings=["AAPL", "MSFT"],
            quantity=[10, 15],
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )
        
    def test_full_workflow(self):
        """Testa fluxo completo de uso do Portfolio"""
        # 1. Verifica pesos
        weights = self.portfolio.weights()
        self.assertAlmostEqual(sum(weights.values()), 1.0)
        
        # 2. Obtém retornos
        returns = self.portfolio.returns()
        self.assertIsInstance(returns, pd.DataFrame)
        
        # 3. Calcula valor total
        total_value = self.portfolio.total_value()
        self.assertIsInstance(total_value, float)
        self.assertGreater(total_value, 0)
        
        # 4. Verifica valores por ativo
        values_per_holding = self.portfolio.total_value_per_holding()
        self.assertEqual(len(values_per_holding), 2)
        
if __name__ == '__main__':
    unittest.main()
