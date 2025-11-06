import unittest
from unittest.mock import Mock, patch
import numpy as np
import pandas as pd
from datetime import date, timedelta

from src.analysis.entities.monte_carlo_base import MonteCarloBase
from src.analysis.entities.monte_carlo_portfolios import MonteCarloPortfolio
from src.analysis.entities.monte_carlo_returns import MonteCarloRetorno
from src.analysis.entities.monte_carlo_combined import MonteCarloCombinado
from src.core.entities.portfolio import Portfolio
from src.analysis.entities.distribuition_generator import DistribuicaoNormal

class TestMonteCarloBase(unittest.TestCase):
    """Testes para a classe base MonteCarloBase"""
    
    def setUp(self):
        """Setup para cada teste"""
        # Cria um mock do Portfolio
        self.mock_portfolio = Mock(spec=Portfolio)
        self.mock_portfolio.series.get_returns.return_value = pd.DataFrame({
            'AAPL': [0.01, -0.02, 0.03],
            'MSFT': [0.02, -0.01, 0.01]
        })
        
        # Parâmetros padrão
        self.n_simulacoes = 100
        self.taxa_livre_risco = 0.03
        self.seed = 42
        
    def test_initialization(self):
        """Testa a inicialização correta da classe base"""
        class ConcreteMonteCarlo(MonteCarloBase):
            def run(self):
                pass
        
        mc = ConcreteMonteCarlo(
            portfolio=self.mock_portfolio,
            n_simulacoes=self.n_simulacoes,
            taxa_livre_risco=self.taxa_livre_risco,
            seed=self.seed
        )
        
        self.assertEqual(mc.n_simulacoes, self.n_simulacoes)
        self.assertEqual(mc.taxa_livre_risco, self.taxa_livre_risco)
        self.assertIsInstance(mc.distribution, DistribuicaoNormal)
        
    def test_seed_reproducibility(self):
        """Testa se a semente aleatória garante reprodutibilidade"""
        class ConcreteMonteCarlo(MonteCarloBase):
            def run(self):
                return np.random.rand(10)
        
        mc1 = ConcreteMonteCarlo(
            portfolio=self.mock_portfolio,
            seed=42
        )
        mc2 = ConcreteMonteCarlo(
            portfolio=self.mock_portfolio,
            seed=42
        )
        
        np.testing.assert_array_equal(mc1.run(), mc2.run())

class TestMonteCarloPortfolio(unittest.TestCase):
    """Testes para MonteCarloPortfolio"""
    
    def setUp(self):
        """Setup para cada teste"""
        # Cria dados de teste
        self.returns_data = pd.DataFrame({
            'AAPL': [0.01, -0.02, 0.03],
            'MSFT': [0.02, -0.01, 0.01]
        })
        
        # Mock do Portfolio
        self.mock_portfolio = Mock(spec=Portfolio)
        self.mock_portfolio.series.get_returns.return_value = self.returns_data
        self.mock_portfolio.weights.return_value = {'AAPL': 0.6, 'MSFT': 0.4}
        
        # Instância de MonteCarloPortfolio
        self.mc_portfolio = MonteCarloPortfolio(
            portfolio=self.mock_portfolio,
            n_simulacoes=100,
            taxa_livre_risco=0.03,
            capital_inicial=10000.0,
            seed=42
        )
        
    def test_peso_soma_um(self):
        """Testa se os pesos gerados somam 1"""
        pesos = self.mc_portfolio._gerar_pesos()
        self.assertAlmostEqual(np.sum(pesos), 1.0)
        
    def test_run_structure(self):
        """Testa a estrutura do DataFrame retornado pelo run"""
        result = self.mc_portfolio.run()
        
        # Verifica as colunas
        expected_columns = ['Ativo', 'Data', 'Peso', 'Valor', 'Valor Total', 'Retorno', 'Simulação']
        self.assertTrue(all(col in result.columns for col in expected_columns))
        
        # Verifica número de simulações
        self.assertEqual(len(result['Simulação'].unique()), self.mc_portfolio.n_simulacoes)
        
        # Verifica ativos
        self.assertTrue(all(ativo in result['Ativo'].unique() for ativo in ['AAPL', 'MSFT']))
        
    def test_valor_inicial(self):
        """Testa se o valor inicial está correto"""
        result = self.mc_portfolio.run()
        primeiro_dia = result[result['Data'] == result['Data'].min()]
        valor_total_inicial = primeiro_dia.groupby('Simulação')['Valor'].sum()
        
        # Verifica se cada simulação começa com o capital inicial
        self.assertTrue(all(abs(valor - self.mc_portfolio.capital_inicial) < 0.01 
                          for valor in valor_total_inicial))
        
class TestMonteCarloRetorno(unittest.TestCase):
    """Testes para MonteCarloRetorno"""
    
    def setUp(self):
        """Setup para cada teste"""
        # Cria dados de teste
        self.returns_data = pd.DataFrame({
            'AAPL': [0.01, -0.02, 0.03],
            'MSFT': [0.02, -0.01, 0.01]
        })
        
        # Mock do Portfolio
        self.mock_portfolio = Mock(spec=Portfolio)
        self.mock_portfolio.series.get_returns.return_value = self.returns_data
        self.mock_portfolio.weights.return_value = {'AAPL': 0.6, 'MSFT': 0.4}
        
        # Instância de MonteCarloRetorno
        self.mc_retorno = MonteCarloRetorno(
            portfolio=self.mock_portfolio,
            n_simulacoes=100,
            taxa_livre_risco=0.03,
            capital_inicial=10000.0,
            seed=42
        )
        
    def test_pesos_fixos(self):
        """Testa se os pesos permanecem fixos em todas as simulações"""
        result = self.mc_retorno.run()
        
        # Verifica se os pesos são constantes para cada ativo
        for ativo in ['AAPL', 'MSFT']:
            pesos = result[result['Ativo'] == ativo]['Peso'].unique()
            self.assertEqual(len(pesos), 1)
            
    def test_retornos_correlacao(self):
        """Testa se os retornos simulados mantêm correlação similar aos dados históricos"""
        result = self.mc_retorno.run()
        
        # Calcula correlação histórica
        corr_historica = self.returns_data.corr().iloc[0,1]
        
        # Calcula correlação média das simulações
        corr_simulada = []
        for sim in result['Simulação'].unique():
            sim_data = result[result['Simulação'] == sim].pivot(
                index='Data', columns='Ativo', values='Retorno'
            )
            corr_simulada.append(sim_data.corr().iloc[0,1])
        
        corr_media_simulada = np.mean(corr_simulada)
        
        # Verifica se a correlação média está próxima da histórica
        self.assertTrue(abs(corr_historica - corr_media_simulada) < 0.3)
        
    def test_log_returns_distribution(self):
        """Testa se os retornos seguem distribuição log-normal"""
        result = self.mc_retorno.run()
        
        # Pega os retornos de um ativo
        retornos = result[result['Ativo'] == 'AAPL']['Retorno']
        
        # Testa características da distribuição log-normal
        self.assertTrue(np.all(retornos > -1))  # Retornos maiores que -100%
        self.assertTrue(abs(np.mean(np.log(retornos + 1))) < 1)  # Média razoável
        
class TestCombinedFeatures(unittest.TestCase):
    """Testes para características comuns e integração"""
    
    def setUp(self):
        """Setup para cada teste"""
        # Cria portfolio real para testes de integração
        self.portfolio = Portfolio(
            name="Test Portfolio",
            holdings=['AAPL', 'MSFT'],
            quantity=[10, 15],
            start_date=date.today() - timedelta(days=365),
            end_date=date.today(),
            source="yfinance"
        )
        
    def test_metricas_simulacoes(self):
        """Testa o cálculo de métricas das simulações"""
        for MCClass in [MonteCarloPortfolio, MonteCarloRetorno]:
            mc = MCClass(
                portfolio=self.portfolio,
                n_simulacoes=50,
                seed=42
            )
            
            mc.run()
            
            # Verifica estrutura das métricas
            self.assertTrue(hasattr(mc, 'metricas_simulacoes'))
            self.assertIsInstance(mc.metricas_simulacoes, pd.DataFrame)
            
            # Verifica cálculos
            metricas = mc.metricas_simulacoes
            self.assertTrue(all(metricas['Valor Total'] > 0))
            self.assertTrue(all(metricas['Retorno']['std'] > 0))
            
    def test_reproducibility_full(self):
        """Testa reprodutibilidade completa das simulações"""
        for MCClass in [MonteCarloPortfolio, MonteCarloRetorno]:
            mc1 = MCClass(portfolio=self.portfolio, seed=42)
            mc2 = MCClass(portfolio=self.portfolio, seed=42)
            
            result1 = mc1.run()
            result2 = mc2.run()
            
            pd.testing.assert_frame_equal(result1, result2)
            
    def test_error_handling(self):
        """Testa tratamento de erros"""
        # Teste com portfolio inválido
        with self.assertRaises(Exception):
            MonteCarloPortfolio(portfolio=None)
            
        # Teste com número negativo de simulações
        with self.assertRaises(ValueError):
            MonteCarloPortfolio(portfolio=self.portfolio, n_simulacoes=-1)
            
if __name__ == '__main__':
    unittest.main()