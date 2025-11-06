import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, date, timedelta

from src.extractor.extractor_base import BaseExtractor
from src.extractor.sources.prices.extractor_yahoo import YahooExtractor
from src.extractor.sources.prices.extractor_eodhd import EODHDExtractor
from src.extractor.sources.prices.extractor_fmp import FMPExtractor
from src.extractor.sources.prices.extractor_alphavantage import AlphaVantageExtractor

class TestBaseExtractor(unittest.TestCase):
    """Testes para a classe base BaseExtractor"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.extractor = BaseExtractor()
    
    def test_directory_structure(self):
        """Testa se os diretórios são criados corretamente"""
        self.assertTrue(self.extractor.raw_data_dir.exists())
        self.assertTrue(self.extractor.processed_data_dir.exists())
        
    def test_abstract_methods(self):
        """Testa se os métodos abstratos estão definidos"""
        with self.assertRaises(TypeError):
            self.extractor.get_historical_prices(
                symbol="AAPL",
                start_date=datetime.now(),
                end_date=datetime.now()
            )
            
        with self.assertRaises(TypeError):
            self.extractor.format_historical_prices({})

class TestYahooExtractor(unittest.TestCase):
    """Testes para o extrator do Yahoo Finance"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.extractor = YahooExtractor()
        self.symbol = "AAPL"
        self.start_date = date.today() - timedelta(days=30)
        self.end_date = date.today()
        
    @patch('yfinance.download')
    def test_get_historical_prices(self, mock_download):
        """Testa a obtenção de preços históricos"""
        # Cria um DataFrame de exemplo
        mock_data = pd.DataFrame({
            'Open': [100, 101],
            'High': [102, 103],
            'Low': [98, 99],
            'Close': [101, 102],
            'Volume': [1000, 1100]
        }, index=[self.start_date, self.end_date])
        
        mock_download.return_value = mock_data
        
        result = self.extractor.get_historical_prices(
            self.symbol,
            self.start_date,
            self.end_date
        )
        
        # Verifica se o método download foi chamado com os parâmetros corretos
        mock_download.assert_called_once()
        
        # Verifica o formato dos dados retornados
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(all(col in result.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']))
        
    def test_invalid_symbol(self):
        """Testa o comportamento com símbolo inválido"""
        with self.assertRaises(Exception):
            self.extractor.get_historical_prices(
                "INVALID_SYMBOL",
                self.start_date,
                self.end_date
            )
            
class TestEODHDExtractor(unittest.TestCase):
    """Testes para o extrator do EODHD"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.extractor = EODHDExtractor()
        self.symbol = "AAPL"
        self.start_date = date.today() - timedelta(days=30)
        self.end_date = date.today()
        
    @patch('requests.get')
    def test_get_historical_prices(self, mock_get):
        """Testa a obtenção de preços históricos"""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': [
                {
                    'date': '2023-01-01',
                    'open': 100,
                    'high': 102,
                    'low': 98,
                    'close': 101,
                    'volume': 1000
                }
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.extractor.get_historical_prices(
            self.symbol,
            self.start_date,
            self.end_date
        )
        
        # Verifica se a requisição foi feita corretamente
        mock_get.assert_called_once()
        
        # Verifica o formato dos dados
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        
    def test_api_error_handling(self):
        """Testa o tratamento de erros da API"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            with self.assertRaises(Exception):
                self.extractor.get_historical_prices(
                    self.symbol,
                    self.start_date,
                    self.end_date
                )

class TestFMPExtractor(unittest.TestCase):
    """Testes para o extrator do Financial Modeling Prep"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.extractor = FMPExtractor()
        self.symbol = "AAPL"
        self.start_date = date.today() - timedelta(days=30)
        self.end_date = date.today()
        
    @patch('requests.get')
    def test_get_historical_prices(self, mock_get):
        """Testa a obtenção de preços históricos"""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                'date': '2023-01-01',
                'open': 100,
                'high': 102,
                'low': 98,
                'close': 101,
                'volume': 1000
            }
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.extractor.get_historical_prices(
            self.symbol,
            self.start_date,
            self.end_date
        )
        
        # Verifica se a requisição foi feita corretamente
        mock_get.assert_called_once()
        
        # Verifica o formato dos dados
        self.assertIsInstance(result, list)
        
class TestAlphaVantageExtractor(unittest.TestCase):
    """Testes para o extrator do Alpha Vantage"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.extractor = AlphaVantageExtractor()
        self.symbol = "AAPL"
        self.start_date = date.today() - timedelta(days=30)
        self.end_date = date.today()
        
    @patch('requests.get')
    def test_get_historical_prices(self, mock_get):
        """Testa a obtenção de preços históricos"""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'Time Series (Daily)': {
                '2023-01-01': {
                    '1. open': '100',
                    '2. high': '102',
                    '3. low': '98',
                    '4. close': '101',
                    '5. volume': '1000'
                }
            }
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.extractor.get_historical_prices(
            self.symbol,
            self.start_date,
            self.end_date
        )
        
        # Verifica se a requisição foi feita corretamente
        mock_get.assert_called_once()
        
        # Verifica o formato dos dados
        self.assertIsInstance(result, dict)
        self.assertIn('Time Series (Daily)', result)

class TestDataFormatting(unittest.TestCase):
    """Testes para a formatação de dados de diferentes fontes"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.yahoo_extractor = YahooExtractor()
        self.eodhd_extractor = EODHDExtractor()
        self.fmp_extractor = FMPExtractor()
        self.alpha_extractor = AlphaVantageExtractor()
        
    def test_yahoo_format(self):
        """Testa a formatação dos dados do Yahoo"""
        raw_data = pd.DataFrame({
            'Open': [100],
            'High': [102],
            'Low': [98],
            'Close': [101],
            'Volume': [1000]
        })
        
        formatted_data = self.yahoo_extractor.format_historical_prices(raw_data)
        self._verify_standard_format(formatted_data)
        
    def test_eodhd_format(self):
        """Testa a formatação dos dados do EODHD"""
        raw_data = {
            'data': [
                {
                    'date': '2023-01-01',
                    'open': 100,
                    'high': 102,
                    'low': 98,
                    'close': 101,
                    'volume': 1000
                }
            ]
        }
        
        formatted_data = self.eodhd_extractor.format_historical_prices(raw_data)
        self._verify_standard_format(formatted_data)
        
    def _verify_standard_format(self, data):
        """Verifica se os dados estão no formato padrão esperado"""
        expected_columns = ['open', 'high', 'low', 'close', 'volume']
        self.assertIsInstance(data, pd.DataFrame)
        self.assertTrue(all(col.lower() in map(str.lower, data.columns) 
                          for col in expected_columns))
        
if __name__ == '__main__':
    unittest.main()
