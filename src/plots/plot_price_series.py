"""
Class for visualizing financial asset price time series.
Implements various charts for analyzing asset price behavior.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, List
from pathlib import Path


class PriceSeriesVisualizer:
    """Class responsible for generating charts for financial asset price time series analysis."""

    def __init__(self, data: pd.DataFrame):
        """Initialize the visualizer with time series data.

        Args:
            data (pd.DataFrame): DataFrame containing price time series data.
                Must include columns: 'Date', 'Close', 'Open', 'High', 'Low', 'Volume'.

        Raises:
            ValueError: If the DataFrame is empty or missing required columns.
        """
        if data is None or data.empty:
            raise ValueError("DataFrame cannot be empty.")

        required_columns = ['Close', 'Open', 'High', 'Low', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing columns in DataFrame: {missing_columns}")

        self.data = data.copy()

    def plot_prices(self, window_ma: Optional[List[int]] = None) -> plt.Figure:
        """Generate a price chart with optional moving averages.

        Args:
            window_ma (Optional[List[int]]): List of periods for moving averages.

        Returns:
            plt.Figure: Figure object with the generated chart.
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot closing prices
        ax.plot(self.data.index, self.data['Close'], label='Price', linewidth=1)

        # Add moving averages if provided
        if window_ma:
            for window in window_ma:
                ma = self.data['Close'].rolling(window=window).mean()
                ax.plot(self.data.index, ma,
                        label=f'Moving Average ({window} periods)',
                        linewidth=1, alpha=0.8)

        ax.set_title('Price Evolution and Moving Averages')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig

    def plot_candlestick(self) -> plt.Figure:
        """Generate a candlestick chart.

        Returns:
            plt.Figure: Figure object with the generated chart.
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Convert index to numeric for plotting
        x = np.arange(len(self.data.index))
        width = 0.6  # Candle width

        # Bullish candles (close > open)
        mask_up = self.data['Close'] > self.data['Open']
        ax.bar(x[mask_up],
               self.data[mask_up]['Close'] - self.data[mask_up]['Open'],
               bottom=self.data[mask_up]['Open'],
               width=width, color='g', alpha=0.5)

        # Bearish candles (close <= open)
        mask_down = self.data['Close'] <= self.data['Open']
        ax.bar(x[mask_down],
               self.data[mask_down]['Close'] - self.data[mask_down]['Open'],
               bottom=self.data[mask_down]['Open'],
               width=width, color='r', alpha=0.5)

        # Wicks
        ax.vlines(x, self.data['Low'], self.data['High'],
                  color='black', linewidth=1)

        # Format x-axis to show dates
        ax.set_xticks(x[::max(1, len(x)//10)])
        ax.set_xticklabels(self.data.index[::max(1, len(x)//10)].strftime('%Y-%m-%d'),
                           rotation=45)

        ax.set_title('Candlestick Chart')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.grid(True, alpha=0.3)

        return fig

    def plot_returns(self, return_type: str = 'log') -> plt.Figure:
        """Generate a chart of returns and their distribution.

        Args:
            return_type (str): Type of return to calculate:
                'log' for log returns, 'simple' for simple returns.

        Returns:
            plt.Figure: Figure object with the generated charts.
        """
        if return_type == 'log':
            returns = np.log(self.data['Close'] / self.data['Close'].shift(1))
        else:
            returns = self.data['Close'].pct_change()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[2, 1])

        # Time series of returns
        ax1.plot(returns.index, returns, linewidth=1, alpha=0.7)
        ax1.set_title(f'{"Log-" if return_type == "log" else ""}Daily Returns')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Return')
        ax1.grid(True, alpha=0.3)

        # Return distribution
        sns.histplot(data=returns, ax=ax2, bins=50, stat='density', alpha=0.6)
        sns.kdeplot(data=returns, ax=ax2, color='red', linewidth=2)

        ax2.set_title('Return Distribution')
        ax2.set_xlabel('Return')
        ax2.set_ylabel('Density')

        plt.tight_layout()
        return fig

    def plot_volume(self) -> plt.Figure:
        """Generate a chart of traded volume.

        Returns:
            plt.Figure: Figure object with the generated chart.
        """
        fig, ax = plt.subplots(figsize=(12, 4))

        # Volume bars colored by price change
        colors = np.where(self.data['Close'] > self.data['Open'], 'g', 'r')
        ax.bar(self.data.index, self.data['Volume'], color=colors, alpha=0.5)

        ax.set_title('Trading Volume')
        ax.set_xlabel('Date')
        ax.set_ylabel('Volume')
        ax.grid(True, alpha=0.3)

        return fig

    def plot_volatility(self, window: int = 21) -> plt.Figure:
        """Generate a rolling volatility chart.

        Args:
            window (int): Window size (in days) for volatility calculation.

        Returns:
            plt.Figure: Figure object with the generated chart.
        """
        returns = np.log(self.data['Close'] / self.data['Close'].shift(1))
        vol = returns.rolling(window=window).std() * np.sqrt(252)

        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(vol.index, vol, linewidth=1)

        ax.set_title(f'Rolling Volatility ({window}-Day Window)')
        ax.set_xlabel('Date')
        ax.set_ylabel('Annualized Volatility')
        ax.grid(True, alpha=0.3)

        return fig

    def plot_drawdown(self) -> plt.Figure:
        """Generate a drawdown chart.

        Returns:
            plt.Figure: Figure object with the generated chart.
        """
        roll_max = self.data['Close'].expanding().max()
        drawdown = (self.data['Close'] - roll_max) / roll_max

        fig, ax = plt.subplots(figsize=(12, 4))

        ax.fill_between(drawdown.index, drawdown, 0, color='r', alpha=0.3)
        ax.plot(drawdown.index, drawdown, color='r', linewidth=1)

        ax.set_title('Drawdown')
        ax.set_xlabel('Date')
        ax.set_ylabel('Drawdown (%)')
        ax.grid(True, alpha=0.3)

        return fig

    def plot_dashboard(self, window_ma: Optional[List[int]] = [20, 50]) -> plt.Figure:
        """Generate a complete dashboard with key charts.

        Args:
            window_ma (Optional[List[int]]): List of periods for moving averages.

        Returns:
            plt.Figure: Figure object with the generated dashboard.
        """
        fig = plt.figure(figsize=(15, 12))
        gs = fig.add_gridspec(3, 2)

        # Prices and Moving Averages
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(self.data.index, self.data['Close'], label='Price', linewidth=1)
        if window_ma:
            for window in window_ma:
                ma = self.data['Close'].rolling(window=window).mean()
                ax1.plot(self.data.index, ma, label=f'MA({window})',
                         linewidth=1, alpha=0.8)
        ax1.set_title('Price and Moving Averages')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Volume
        ax2 = fig.add_subplot(gs[1, 0])
        colors = np.where(self.data['Close'] > self.data['Open'], 'g', 'r')
        ax2.bar(self.data.index, self.data['Volume'], color=colors, alpha=0.5)
        ax2.set_title('Volume')
        ax2.grid(True, alpha=0.3)

        # Returns
        ax3 = fig.add_subplot(gs[1, 1])
        returns = np.log(self.data['Close'] / self.data['Close'].shift(1))
        ax3.plot(returns.index, returns, linewidth=1, alpha=0.7)
        ax3.set_title('Log Returns')
        ax3.grid(True, alpha=0.3)

        # Volatility
        ax4 = fig.add_subplot(gs[2, 0])
        vol = returns.rolling(window=21).std() * np.sqrt(252)
        ax4.plot(vol.index, vol, linewidth=1)
        ax4.set_title('Volatility (21 Days)')
        ax4.grid(True, alpha=0.3)

        # Drawdown
        ax5 = fig.add_subplot(gs[2, 1])
        roll_max = self.data['Close'].expanding().max()
        drawdown = (self.data['Close'] - roll_max) / roll_max
        ax5.fill_between(drawdown.index, drawdown, 0, color='r', alpha=0.3)
        ax5.plot(drawdown.index, drawdown, color='r', linewidth=1)
        ax5.set_title('Drawdown')
        ax5.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig
