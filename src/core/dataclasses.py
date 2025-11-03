import math
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import List, Union, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .loader import get_historical_data, get_macro_data

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class TimeSeries:
    name: str
    data: pd.DataFrame = field(default_factory=pd.DataFrame)
    start_date: date = field(default_factory=lambda: date.today() - timedelta(days=30))
    end_date: date = field(default_factory=date.today)

    def clean_data(self) -> None:
        """Basic cleaning: ensure Date index, parse dates, drop duplicates and sort."""
        if self.data is None or self.data.empty:
            return

        # If index is a column called Date, set it
        if "Date" in self.data.columns:
            try:
                self.data["Date"] = pd.to_datetime(self.data["Date"])
                self.data = self.data.set_index("Date")
            except Exception:
                pass

        # Ensure datetime index
        if not isinstance(self.data.index, pd.DatetimeIndex):
            try:
                self.data.index = pd.to_datetime(self.data.index)
            except Exception:
                # give up gracefully
                return

        self.data = self.data.sort_index()
        self.data = self.data[~self.data.index.duplicated(keep="first")]
        # Forward fill then backfill for small gaps
        self.data = self.data.ffill().bfill()

    def compute_basic_stats(self) -> None:
        """Compute basic returns-based stats and attach as attributes.

        Attributes added: returns, mean_return, std_return, last_prices
        """
        if self.data is None or self.data.empty:
            self.returns = pd.DataFrame()
            self.mean_return = None
            self.std_return = None
            self.last_prices = None
            return

        close = self._extract_close()
        if close is None or close.empty:
            self.returns = pd.DataFrame()
            self.mean_return = None
            self.std_return = None
            self.last_prices = None
            return

        # log returns
        self.returns = np.log(close / close.shift(1)).dropna()
        self.mean_return = self.returns.mean()
        self.std_return = self.returns.std()
        self.last_prices = close.iloc[-1]

    def _extract_close(self) -> Optional[pd.DataFrame]:
        if self.data is None or self.data.empty:
            return pd.DataFrame()

        cols = self.data.columns
        # MultiIndex with Price level containing 'Close'
        if isinstance(cols, pd.MultiIndex):
            if "Close" in cols.get_level_values(0):
                return self.data["Close"].copy()
            # maybe single-level with tickers only
        # If 'Close' column exists
        if "Close" in cols:
            return self.data["Close"].copy()
        # otherwise, if columns look like tickers return them
        return self.data.copy()


@dataclass
class PricesSeries(TimeSeries):
    tickers: Union[str, List[str]] = field(default_factory=list)
    source: str = "yfinance"

    def __post_init__(self):
        if isinstance(self.tickers, str):
            self.tickers = self.tickers.replace(",", " ").split()
        elif isinstance(self.tickers, (set, tuple)):
            self.tickers = list(self.tickers)

        # Fetch data using shared loader
        self.data = get_historical_data(tickers=self.tickers, source=self.source, start_date=self.start_date, end_date=self.end_date)

        # Clean and compute stats automatically
        self.clean_data()
        self.compute_basic_stats()

    def generate_stats(self) -> pd.DataFrame:
        """Return a small DataFrame with mean and std for each series."""
        if getattr(self, "returns", None) is None or self.returns.empty:
            self.compute_basic_stats()
        df = pd.DataFrame({"mean": self.mean_return, "std": self.std_return})
        return df


@dataclass
class MacroSeries(TimeSeries):
    indicators: Union[str, List[str]] = field(default_factory=list)
    source: str = "fred"

    def __post_init__(self):
        if isinstance(self.indicators, str):
            self.indicators = self.indicators.replace(",", " ").split()
        elif isinstance(self.indicators, (set, tuple)):
            self.indicators = list(self.indicators)

        self.data = get_macro_data(indicators=self.indicators, source=self.source, start_date=self.start_date, end_date=self.end_date)
        self.clean_data()
        self.compute_basic_stats()


@dataclass
class Portfolio:
    name: str
    tickers: Union[str, List[str]] = field(default_factory=list)
    weights: Union[float, List[float]] = field(default_factory=list)
    prices_series: PricesSeries = field(init=False)

    def __post_init__(self):
        if isinstance(self.tickers, str):
            self.tickers = self.tickers.replace(",", " ").split()
        elif isinstance(self.tickers, (set, tuple)):
            self.tickers = list(self.tickers)

        if isinstance(self.weights, float) or isinstance(self.weights, int):
            self.weights = [float(self.weights)] * len(self.tickers)
        elif isinstance(self.weights, (set, tuple)):
            self.weights = list(self.weights)

        # normalize weights if provided
        if self.weights and len(self.weights) == len(self.tickers):
            s = sum(self.weights)
            if s != 0:
                self.weights = [w / s for w in self.weights]

        # create prices series
        self.prices_series = PricesSeries(tickers=self.tickers)

    def monte_carlo(self, n_sims: int = 500, horizon: int = 252, seed: Optional[int] = None, individual: bool = False):
        """Run a simple Monte Carlo simulation.

        If individual=True returns simulations per asset, otherwise returns portfolio-level simulations.
        """
        if seed is not None:
            np.random.seed(seed)

        ps = self.prices_series
        returns = getattr(ps, "returns", None)
        if returns is None or returns.empty:
            ps.compute_basic_stats()
            returns = ps.returns

        mu = returns.mean().values
        sigma = returns.cov().values

        # starting prices
        start_prices = ps.last_prices
        if start_prices is None:
            raise ValueError("No starting prices available for simulation")

        n_assets = len(start_prices.columns) if isinstance(start_prices, pd.DataFrame) else (1 if hasattr(start_prices, '__len__') else 1)

        dt = 1

        sims = None
        if individual:
            # simulate each asset separately using multivariate normal draws
            sims = np.zeros((n_sims, horizon + 1, len(start_prices)))
            for i in range(n_sims):
                prices = np.array(start_prices)
                sims[i, 0, :] = prices
                for t in range(1, horizon + 1):
                    rnd = np.random.multivariate_normal(mu, sigma)
                    prices = prices * np.exp(rnd)
                    sims[i, t, :] = prices
            return sims
        else:
            # portfolio-level simulation
            w = np.array(self.weights) if self.weights else np.repeat(1.0 / len(self.tickers), len(self.tickers))
            sims = np.zeros((n_sims, horizon + 1))
            for i in range(n_sims):
                prices = np.array(start_prices)
                sims[i, 0] = np.dot(prices, w)
                for t in range(1, horizon + 1):
                    rnd = np.random.multivariate_normal(mu, sigma)
                    prices = prices * np.exp(rnd)
                    sims[i, t] = np.dot(prices, w)
            return sims

    def plot_monte_carlo(self, sims: np.ndarray, filename: Optional[Union[str, Path]] = None) -> Path:
        """Plot Monte Carlo results and save to OUTPUT_DIR; returns path to file."""
        fn = filename or (OUTPUT_DIR / f"mc_{self.name}.png")
        plt.figure(figsize=(10, 6))
        # plot a subset of simulations to avoid overplotting
        n_plot = min(50, sims.shape[0])
        for i in range(n_plot):
            plt.plot(sims[i, :], color="gray", alpha=0.3)
        # plot mean
        mean_path = sims.mean(axis=0)
        plt.plot(mean_path, color="red", lw=2, label="Mean")
        plt.title(f"Monte Carlo simulations - {self.name}")
        plt.xlabel("Time")
        plt.ylabel("Portfolio value")
        plt.legend()
        plt.grid(True)
        Path(fn).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(fn, bbox_inches="tight")
        plt.close()
        return Path(fn)

    def report(self, include_plots: bool = True) -> str:
        """Generate a simple markdown report for the portfolio and return the markdown string.

        The report is also written to `data/output/portfolio_{name}.md`.
        """
        ps = self.prices_series
        md_lines = [f"# Portfolio report: {self.name}", ""]
        md_lines.append("## Composition")
        for t, w in zip(self.tickers, self.weights):
            md_lines.append(f"- {t}: {w:.2%}")
        md_lines.append("")

        # basic stats
        stats = ps.generate_stats()
        md_lines.append("## Basic stats (returns)")
        if not stats.empty:
            md_lines.append(stats.to_markdown())
        else:
            md_lines.append("No return statistics available.")
        md_lines.append("")

        # Monte Carlo quick run (small)
        try:
            sims = self.monte_carlo(n_sims=200, horizon=252, seed=42)
            mc_path = self.plot_monte_carlo(sims)
            if include_plots:
                md_lines.append("## Monte Carlo")
                md_lines.append(f"![Monte Carlo]({mc_path.as_posix()})")
                md_lines.append("")
                # quantiles
                final_vals = sims[:, -1]
                q = np.percentile(final_vals, [5, 25, 50, 75, 95])
                md_lines.append("### Monte Carlo final value percentiles")
                md_lines.append(f"- 5%: {q[0]:.2f}")
                md_lines.append(f"- 25%: {q[1]:.2f}")
                md_lines.append(f"- 50%: {q[2]:.2f}")
                md_lines.append(f"- 75%: {q[3]:.2f}")
                md_lines.append(f"- 95%: {q[4]:.2f}")
        except Exception as e:
            md_lines.append(f"Monte Carlo failed: {e}")

        out_md = "\n".join(md_lines)
        out_file = OUTPUT_DIR / f"portfolio_{self.name}.md"
        out_file.write_text(out_md)
        return out_md

    def plots_report(self) -> List[Path]:
        """Generate and return list of paths to saved plots for the portfolio."""
        sims = self.monte_carlo(n_sims=200, horizon=252, seed=1)
        p = self.plot_monte_carlo(sims)
        return [p]
