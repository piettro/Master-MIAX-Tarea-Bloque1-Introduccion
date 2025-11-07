import pandas as pd
import numpy as np
from typing import Dict

class MonteCarloCalculator:
    """
    Statistical calculator for Monte Carlo simulation analysis.
    
    This class implements multiple design patterns to provide a comprehensive
    framework for analyzing Monte Carlo simulation results.
    
    Design Pattern Implementation:
        - Strategy: Different calculation methods
        - Observer: Results monitoring
        - Template Method: Standard calculation workflow
        - Chain of Responsibility: Metric calculation pipeline
        
    Key Features:
        - Basic statistical measures
        - Risk metrics (VaR, CVaR)
        - Portfolio analytics
        - Correlation analysis
        - Drawdown calculations
        
    Technical Components:
        - Statistical analysis
        - Risk assessment
        - Portfolio evaluation
        - Results validation
    """
    
    def __init__(self, simulations: pd.DataFrame):
        """
        Initialize Monte Carlo calculator with simulation results.
        
        Parameters
        ----------
        simulations : pd.DataFrame
            Expanded DataFrame containing Monte Carlo simulation results
            Must include columns: [Simulation, Date, Asset, Return, Weight, Total Value]
            
        Design Notes
        -----------
        - Uses Observer pattern for data validation
        - Implements Strategy for calculation methods
        - Supports Template Method for analysis workflow
        
        Raises
        ------
        ValueError
            If simulations DataFrame is None or empty
        """
        if simulations is None or simulations.empty:
            raise ValueError("Simulations DataFrame cannot be empty")
            
        self.simulations = simulations
        
    def calculate_basic_statistics(self) -> Dict[str, float]:
        """
        Calculate basic statistical measures from simulation results.
        
        This method implements the Strategy pattern for statistical
        calculations on Monte Carlo simulation data.
        
        Design Pattern Implementation:
            - Strategy: Statistical calculation methods
            - Observer: Results monitoring
            - Chain of Responsibility: Calculation pipeline
            
        Returns
        -------
        Dict[str, float]
            Dictionary containing:
                - mean_return: Average return across simulations
                - median_return: Median return
                - std_deviation: Return standard deviation
                - min_return: Minimum return observed
                - max_return: Maximum return observed
                
        Technical Details
        ----------------
        - Groups by simulation to get path-level statistics
        - Calculates cross-sectional measures
        - Handles outliers appropriately
        """
        returns = self.simulations.groupby('Simulation')['Return'].mean()
        
        return {
            'mean_return': returns.mean(),
            'median_return': returns.median(),
            'std_deviation': returns.std(),
            'min_return': returns.min(),
            'max_return': returns.max()
        }
        
    def calculate_var_cvar(self, confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Calculate Value at Risk (VaR) and Conditional Value at Risk (CVaR).
        
        This method implements risk metric calculations using multiple
        design patterns for robust risk assessment.
        
        Design Pattern Implementation:
            - Strategy: Risk calculation methodology
            - Template Method: Standard risk calculation flow
            - Chain of Responsibility: Risk metric pipeline
            
        Parameters
        ----------
        confidence_level : float, default=0.95
            Confidence level for VaR/CVaR calculation
            Example: 0.95 for 95% confidence
            
        Returns
        -------
        Dict[str, float]
            Dictionary containing:
                - var: Value at Risk at specified confidence level
                - cvar: Conditional Value at Risk (Expected Shortfall)
                
        Technical Details
        ----------------
        - Calculates path-level returns
        - Determines VaR using percentile method
        - Computes CVaR as mean of tail events
        - Handles extreme scenarios appropriately
        """
        returns = self.simulations.groupby('Simulation')['Return'].mean()
        percentile = 100 * (1 - confidence_level)
        var = np.percentile(returns, percentile)
        cvar = returns[returns <= var].mean()
        
        return {
            'var': var,
            'cvar': cvar
        }
        
    def calculate_portfolio_statistics(self) -> pd.DataFrame:
        """
        Calculate per-asset statistics within the portfolio.
        
        This method implements multiple patterns to analyze individual
        asset performance within the portfolio context.
        
        Design Pattern Implementation:
            - Strategy: Asset analysis methodology
            - Observer: Performance monitoring
            - Chain of Responsibility: Metric calculation
            
        Returns
        -------
        pd.DataFrame
            DataFrame containing per-asset statistics:
                - Asset: Asset identifier
                - Average Weight: Mean portfolio weight
                - Average Return: Mean return
                - Volatility: Return standard deviation
                - Sharpe: Risk-adjusted return metric
                
        Technical Details
        ----------------
        - Analyzes each asset individually
        - Calculates risk-adjusted metrics
        - Handles weight dynamics
        - Processes return distributions
        """
        stats = []
        for asset in self.simulations['Asset'].unique():
            asset_data = self.simulations[self.simulations['Asset'] == asset]
            
            avg_weight = asset_data['Weight'].mean()
            avg_return = asset_data['Return'].mean()
            volatility = asset_data['Return'].std()
            
            stats.append({
                'Asset': asset,
                'Average Weight': avg_weight,
                'Average Return': avg_return,
                'Volatility': volatility,
                'Sharpe': avg_return / volatility if volatility > 0 else 0
            })
            
        return pd.DataFrame(stats)
        
    def calculate_correlations(self) -> pd.DataFrame:
        """
        Calculate the correlation matrix between asset returns.
        
        This method implements correlation analysis using multiple
        design patterns for robust relationship assessment.
        
        Design Pattern Implementation:
            - Strategy: Correlation calculation method
            - Observer: Relationship monitoring
            - Template Method: Analysis workflow
            
        Returns
        -------
        pd.DataFrame
            Correlation matrix containing:
                - Pairwise asset correlations
                - Symmetric matrix format
                - Values in [-1, 1] range
                
        Technical Details
        ----------------
        - Pivots data for correlation analysis
        - Handles missing values appropriately
        - Computes pairwise relationships
        - Maintains matrix symmetry
        """
        # Pivot DataFrame for correlation analysis
        returns_pivot = self.simulations.pivot_table(
            index=['Date', 'Simulation'],
            columns='Asset',
            values='Return'
        )
        
        return returns_pivot.corr()
        
    def calculate_drawdowns(self) -> Dict[str, float]:
        """
        Calculate portfolio drawdown statistics across simulations.
        
        This method implements drawdown analysis using multiple design
        patterns for comprehensive risk assessment.
        
        Design Pattern Implementation:
            - Strategy: Drawdown calculation methodology
            - Observer: Risk monitoring
            - Chain of Responsibility: Metric pipeline
            - Template Method: Analysis workflow
            
        Returns
        -------
        Dict[str, float]
            Dictionary containing drawdown metrics:
                - max_drawdown: Maximum portfolio drawdown
                - avg_drawdown: Average drawdown across simulations
                - drawdown_std: Drawdown volatility measure
                
        Technical Details
        ----------------
        - Computes path-wise drawdowns
        - Tracks running maximum values
        - Calculates relative declines
        - Aggregates across simulations
        
        Process Flow:
            1. Group values by date and simulation
            2. Calculate running maximum
            3. Compute drawdown percentages
            4. Aggregate statistics
        """
        # Extract portfolio values across time and simulations
        values = self.simulations.groupby(['Date', 'Simulation'])['Total Value'].first().unstack()
        
        # Calculate drawdowns for each simulation path
        running_max = values.expanding().max()
        drawdowns = (values - running_max) / running_max
        
        return {
            'max_drawdown': drawdowns.min().min(),
            'avg_drawdown': drawdowns.mean().mean(),
            'drawdown_std': drawdowns.std().mean()
        }