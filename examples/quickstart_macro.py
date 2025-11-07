"""
Exemplo rápido de uso da funcionalidade de dados macroeconômicos com visualizações e relatório.
"""

from datetime import datetime
import pandas as pd

from src.core.entities.macro_series import MacroSeries
from src.extractor.macro_extractor import MacroExtractor
from src.reports.report_macro import MacroReport

def main():
    print("\n=== Quickstart: Dados Macroeconômicos ===")

    # 1. Extração de dados macroeconômicos
    print("\n1. Extraindo dados macroeconômicos...")
    
    extractor = MacroExtractor()
    indicators = extractor.list_available_indicators()
    print(f"Indicadores disponíveis: {len(indicators)}")

    for name, code in list(indicators.items())[:5]:
        print(f"- {name}: {code}")

    selected_indicators = [
        "GDP growth (annual %)",
        "Inflation, GDP deflator (annual %)",
        "Exports of goods and services (% of GDP)",
        "Imports of goods and services (% of GDP)"
    ]
    countries = ["ESP", "USA"]  # Corrigido: EUU para USA
    macro = MacroSeries(
        name="Séries Macroeconômicas Exemplo",
        indicators=selected_indicators,
        countries=countries,
        start_date="2000-01-01",
        end_date=datetime.now().strftime("%Y-%m-%d")
    )

    print("\nEstrutura do DataFrame:")
    print("Colunas:", macro.data.columns)
    print("Index:", macro.data.index)
    print("\nAmostra dos dados:")
    print(macro.data.head())

    print("\n3. Gerando relatório macroeconômico...")
    report = MacroReport(macro_series=macro)
    report.generate()

if __name__ == "__main__":
    main()
