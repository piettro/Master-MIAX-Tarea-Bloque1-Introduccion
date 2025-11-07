"""
Monte Carlo Simulation Framework

This module implements a flexible Monte Carlo simulation framework using
multiple design patterns to ensure extensibility and maintainability.

Design Patterns:
    - Template Method: Standardized simulation workflow
    - Factory Method: Simulation component creation
    - Observer: Simulation monitoring and results collection
    - Chain of Responsibility: Simulation pipeline

Key Features:
    - Configurable simulation parameters
    - Statistical analysis tools
    - Result visualization
    - Risk metrics calculation

Technical Components:
    - Portfolio Analysis: Performance metrics
    - Risk Assessment: VaR and other metrics
    - Results Management: Data organization
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
import numpy as np
import pandas as pd
from src.core.entities.portfolio import Portfolio

class MonteCarloBase(ABC):
    """
    Abstract base class for portfolio Monte Carlo simulations.
    
    This class implements multiple design patterns to provide a flexible
    and extensible framework for Monte Carlo simulations.
    
    Design Pattern Implementation:
        - Template Method: Simulation workflow
        - Observer: Results monitoring
        
    Key Features:
        - Configurable simulation parameters
        - Risk metric calculations
        - Result management
        
    Technical Components:
        - Portfolio analysis
        - Return generation
        - Statistical analysis
        - Risk assessment
    """

    def __init__(
        self,
        portfolio: Portfolio,
        n_simulations: int = 1000,
        risk_free_rate: float = 0.0,
        alpha: float = 0.05,
        seed: Optional[int] = None,
    ):
        """
        Initialize Monte Carlo simulation parameters.
        
        Parameters
        ----------
        portfolio : Portfolio
            Target portfolio for simulation
        n_simulations : int, default=1000
            Number of Monte Carlo simulations
        risk_free_rate : float, default=0.0
            Risk-free rate for performance metrics
        alpha : float, default=0.05
            Significance level for risk metrics
        seed : int, optional
            Random seed for reproducibility
            
        Design Notes
        -----------
        - Implements Observer for results
        - Supports Chain of Responsibility
        
        Attributes Initialized
        --------------------
        - portfolio: Target portfolio
        - returns_df: Historical returns
        - n_simulations: Simulation count
        - risk_free_rate: Risk-free rate
        - alpha: Significance level
        - results: Simulation results
        - simulations: Detailed paths
        """
        self.portfolio = portfolio
        self.n_simulations = n_simulations
        self.risk_free_rate = risk_free_rate
        self.alpha = alpha

        self.initial_capital = portfolio.total_value_initial()
        self.results: Optional[pd.DataFrame] = None
        self.simulations: Optional[pd.DataFrame] = None
        self.returns_df = self.portfolio.series.get_returns()
        self.historical_returns = self.portfolio.series.get_returns()
        self.assets = self.historical_returns.columns
        self.weights = np.array(list(self.portfolio.weights().values()))
        self.simulations: pd.DataFrame = pd.DataFrame(columns=["Return", "Value", "Simulation"])    

        # Set random seed if provided
        if seed is not None:
            np.random.seed(seed)

        if n_simulations <= 0:
            raise ValueError(f"Number of simulations must be positive, got {n_simulations}")
            
        if not 0 <= alpha <= 1:
            raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")
            
        if risk_free_rate < -1:
            raise ValueError(f"Risk-free rate cannot be less than -100%, got {risk_free_rate}")

    @abstractmethod
    def run(self) -> Any:
        """
        Execute the Monte Carlo simulation process.
        
        This abstract method defines the Template Method pattern
        for implementing specific simulation strategies.
        
        Design Pattern Implementation:
            - Template Method: Simulation workflow
            - Observer: Progress monitoring
            - Chain of Responsibility: Processing pipeline
            
        Expected Implementation:
            1. Parameter validation
            2. Return generation
            3. Path simulation
            4. Results collection
            5. Metrics calculation
            
        Returns
        -------
        Any
            Simulation results in implementation-specific format
            
        Notes
        -----
        - Must be implemented by concrete classes
        - Must handle all simulation parameters
        - Should provide comprehensive results
        """
        pass

    def generate_weights(self) -> np.ndarray:
        """Generate a vector of portfolio weights that sum to 1.

        Returns:
            np.ndarray: Array of weights (length = number of assets).
        """
        
        w = np.abs(np.random.randn(self.assets.shape[0]))
        weights = w / np.sum(w)

        return weights

    def generate_simulated_returns(self, n_periods: int) -> np.ndarray:
        """Generate multivariate simulated log returns.

        Args:
            n_periods (int): Number of periods to simulate.

        Returns:
            np.ndarray: Matrix of simulated returns.
        """
        means = self.historical_returns.mean()
        cov = self.historical_returns.cov()

        simulated_log_returns = np.random.multivariate_normal(mean=means, cov=cov, size=n_periods)
        return np.exp(simulated_log_returns) - 1

    def get_weights(self) -> pd.DataFrame:
        """Get the current portfolio weights as a DataFrame.
        
        Returns:
            pd.DataFrame: DataFrame containing:
                - symbol: Asset symbols/names
                - weight: Portfolio weights for each asset
        """
        return pd.DataFrame({
            'symbol': self.assets,
            'weight': self.weights
        })
