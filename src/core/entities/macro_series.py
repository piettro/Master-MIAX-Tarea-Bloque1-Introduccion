"""
Classe para representação e análise de séries temporais macroeconômicas.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Union, Optional
from datetime import datetime
import pandas as pd
import numpy as np

from src.core.entities.time_series import TimeSeries
from src.extractor.macro_extractor import MacroExtractor

@dataclass
class MacroSeries(TimeSeries):
    """
    Container para séries temporais de indicadores macroeconômicos.
    
    Funciona de forma similar ao PriceSeries, mas para dados macro.
    Usa o MacroExtractor para buscar dados e computa estatísticas básicas.
    """
    
    indicators: Union[str, List[str]] = field(default_factory=list)
    countries: Union[str, List[str]] = field(default_factory=lambda: ["ESP", "EUU"])
    stats: Dict[str, Dict[str, float]] = field(default_factory=dict, init=False)
    
    def __post_init__(self) -> None:
        """Inicializa a série temporal e computa estatísticas."""
        # Processa indicadores
        if isinstance(self.indicators, str):
            self.indicators = self.indicators.replace(",", " ").split()
            
        # Processa países
        if isinstance(self.countries, str):
            self.countries = self.countries.replace(",", " ").split()
            
        # Extrai dados
        extractor = MacroExtractor()
        self.data = extractor.extract(
            indicators=self.indicators,
            countries=self.countries,
            start_date=self.start_date,
            end_date=self.end_date,
            source=self.source
        )
        
        # Computa estatísticas
        self._compute_stats()
        
    def _compute_stats(self) -> None:
        """
        Computa estatísticas básicas para cada indicador.
        - Média
        - Desvio padrão
        - Valor mínimo e máximo
        - Variação percentual total
        """
        if self.data.empty:
            self.stats = {}
            return
            
        self.stats = {}
        
        # Para cada indicador
        for indicator in self.data.columns.get_level_values(0).unique():
            indicator_data = self.data[indicator]
            
            # Para cada país
            country_stats = {}
            for country in indicator_data.columns:
                series = indicator_data[country].dropna()
                
                if not series.empty:
                    total_change = (series.iloc[-1] / series.iloc[0] - 1) if len(series) > 1 else 0
                    avg_change = (
                        (series.pct_change().mean() * len(series))
                        if len(series) > 1 else 0
                    )
                    
                    country_stats[country] = {
                        "mean": float(series.mean()),
                        "std": float(series.std()),
                        "min": float(series.min()),
                        "max": float(series.max()),
                        "total_change": float(total_change),
                        "avg_annual_change": float(avg_change)
                    }
                    
            self.stats[indicator] = country_stats
    
    def get_latest_values(self) -> pd.DataFrame:
        """
        Retorna os valores mais recentes para cada indicador e país.
        
        Returns
        -------
        pd.DataFrame
            DataFrame com os últimos valores disponíveis
        """
        if self.data.empty:
            return pd.DataFrame()
            
        latest = {}
        for indicator in self.data.columns.get_level_values(0).unique():
            latest[indicator] = self.data[indicator].iloc[-1]
            
        return pd.DataFrame(latest)
    
    def get_changes(
        self,
        periods: Optional[int] = None,
        annualized: bool = True
    ) -> pd.DataFrame:
        """
        Calcula variações dos indicadores.
        
        Parameters
        ----------
        periods : int, opcional
            Número de períodos para calcular variação
            Se None, usa todo o período disponível
        annualized : bool
            Se True, anualiza as variações
            
        Returns
        -------
        pd.DataFrame
            DataFrame com as variações calculadas
        """
        if self.data.empty:
            return pd.DataFrame()
            
        changes = {}
        for indicator in self.data.columns.get_level_values(0).unique():
            indicator_data = self.data[indicator]
            
            if periods:
                start_values = indicator_data.iloc[-periods-1]
                end_values = indicator_data.iloc[-1]
            else:
                start_values = indicator_data.iloc[0]
                end_values = indicator_data.iloc[-1]
                
            total_change = (end_values / start_values - 1)
            
            if annualized and periods:
                changes[indicator] = (1 + total_change) ** (1 / (periods/12)) - 1
            else:
                changes[indicator] = total_change
                
        return pd.DataFrame(changes)
    
    def get_correlations(self) -> Dict[str, pd.DataFrame]:
        """
        Calcula matriz de correlação entre países para cada indicador.
        
        Returns
        -------
        dict
            Dicionário com matriz de correlação por indicador
        """
        if self.data.empty:
            return {}
            
        correlations = {}
        for indicator in self.data.columns.get_level_values(0).unique():
            correlations[indicator] = self.data[indicator].corr()
            
        return correlations
    
    def describe(self) -> None:
        """Imprime estatísticas descritivas dos dados."""
        print(f"=== Estatísticas para {self.name} ===")
        
        for indicator, country_stats in self.stats.items():
            print(f"\nIndicador: {indicator}")
            for country, stats in country_stats.items():
                print(f"\n{country}:")
                for stat, value in stats.items():
                    if "change" in stat:
                        print(f"  {stat}: {value:.2%}")
                    else:
                        print(f"  {stat}: {value:.4f}")