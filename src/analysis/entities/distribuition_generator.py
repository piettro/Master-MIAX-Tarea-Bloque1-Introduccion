"""
Distribution Generator Module for Financial Return Simulations

This module implements various distribution generators for simulating
financial returns using multiple design patterns to ensure flexibility
and extensibility in the simulation process.

Design Patterns:
    - Strategy: Different distribution generation approaches
    - Template Method: Standardized sample generation interface
    - Factory Method: Distribution instance creation
    - Observer: Data monitoring and validation
    - Chain of Responsibility: Distribution selection

Key Components:
    - DistributionBase: Abstract base class defining interface
    - NormalDistribution: Markowitz model implementation
    - LogNormalDistribution: Positive returns simulation
    - EmpiricalDistribution: Bootstrap resampling approach

Features:
    - Multiple distribution types
    - Standardized interface
    - Statistical validation
    - Efficient sampling
    - Historical data support
"""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from src.core.entities.portfolio import Portfolio

class DistributionBase(ABC):
    """
    Abstract base class for generating simulated return distributions.
    
    This class implements the Strategy pattern to define a family of
    distribution generation algorithms that can be interchanged.
    
    Design Pattern Implementation:
        - Strategy: Different distribution generation approaches
        - Template Method: Common interface for all distributions
        - Factory Method: Sample generation methods
        
    Key Features:
        - Abstract interface definition
        - Standardized sample generation
        - Flexible distribution implementation
        - Statistical consistency
    """

    @abstractmethod
    def generate_samples(self, mean: np.ndarray, cov: np.ndarray, n_samples: int) -> np.ndarray:
        """
        Generate random samples from the distribution.
        
        Parameters
        ----------
        mean : np.ndarray
            Mean vector of the distribution
        cov : np.ndarray
            Covariance matrix of the distribution
        n_samples : int
            Number of samples to generate
            
        Returns
        -------
        np.ndarray
            Array of generated samples with shape (n_samples, n_assets)
        """
        pass

class NormalDistribution(DistributionBase):
    """
    Standard multivariate normal distribution (Markowitz model).
    
    This class implements the normal distribution strategy for
    generating simulated returns using the Markowitz framework.
    
    Design Pattern Implementation:
        - Strategy: Normal distribution algorithm
        - Template Method: Sample generation implementation
        
    Key Features:
        - Multivariate normal sampling
        - Markowitz model compatibility
        - Mean-variance optimization
    """

    def generate_samples(self, mean, cov, n_samples):
        """
        Generate samples from multivariate normal distribution.
        
        Parameters
        ----------
        mean : np.ndarray
            Mean vector of returns
        cov : np.ndarray
            Covariance matrix of returns
        n_samples : int
            Number of samples to generate
            
        Returns
        -------
        np.ndarray
            Generated normal samples
        """
        return np.random.multivariate_normal(mean, cov, n_samples)

class LogNormalDistribution(DistributionBase):
    """
    Log-normal distribution for positive returns simulation.
    
    This class implements the log-normal distribution strategy
    ensuring generated returns are always positive.
    
    Design Pattern Implementation:
        - Strategy: Log-normal distribution algorithm
        - Template Method: Sample generation implementation
        
    Key Features:
        - Always positive returns
        - Skewed distribution
        - Real-world return characteristics
    """

    def generate_samples(self, mean, cov, n_samples):
        """
        Generate samples from multivariate log-normal distribution.
        
        Parameters
        ----------
        mean : np.ndarray
            Mean vector of log-returns
        cov : np.ndarray
            Covariance matrix of log-returns
        n_samples : int
            Number of samples to generate
            
        Returns
        -------
        np.ndarray
            Generated log-normal samples
        """
        normal_samples = np.random.multivariate_normal(mean, cov, n_samples)
        return np.exp(normal_samples) - 1

class EmpiricalDistribution(DistributionBase):
    """
    Empirical distribution using historical returns bootstrap.
    
    This class implements the empirical distribution strategy
    based on resampling historical data with replacement.
    
    Design Pattern Implementation:
        - Strategy: Bootstrap resampling algorithm
        - Template Method: Sample generation implementation
        - Observer: Historical data monitoring
        
    Key Features:
        - Non-parametric approach
        - Historical data preservation
        - Bootstrap resampling
        - Empirical characteristics
    """

    def __init__(self, historical_returns: pd.DataFrame):
        """
        Initialize empirical distribution with historical data.
        
        Parameters
        ----------
        historical_returns : pd.DataFrame
            Historical returns data for bootstrap sampling
            Must contain asset returns in columns
            
        Design Notes
        -----------
        - Converts DataFrame to numpy array for efficient sampling
        - Preserves original data structure
        - Enables fast random access
        """
        self.historical_returns = historical_returns.values

    def generate_samples(self, mean, cov, n_samples):
        """
        Generate samples using bootstrap resampling of historical data.
        
        This method implements bootstrap resampling to generate
        new samples while preserving the empirical characteristics
        of the original data.
        
        Parameters
        ----------
        mean : np.ndarray
            Not used in empirical sampling, kept for interface consistency
        cov : np.ndarray
            Not used in empirical sampling, kept for interface consistency
        n_samples : int
            Number of bootstrap samples to generate
            
        Returns
        -------
        np.ndarray
            Generated bootstrap samples
            
        Technical Details
        ----------------
        - Random sampling with replacement
        - Preserves cross-sectional dependencies
        - Maintains empirical distribution properties
        """
        n_periods, n_assets = self.historical_returns.shape
        idx = np.random.choice(n_periods, n_samples, replace=True)
        return self.historical_returns[idx, :]
