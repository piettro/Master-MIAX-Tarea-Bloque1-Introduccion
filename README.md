# 📊 Análisis Financiero y Simulación Monte Carlo

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Herramienta modular para la **obtención, estandarización y análisis de datos financieros** (acciones, índices, carteras y simulaciones de Monte Carlo).

Este proyecto forma parte del Máster en Inteligencia Artificial y Finanzas Cuantitativas (MIAX), con el objetivo de implementar **buenas prácticas de arquitectura, abstracción y estandarización de código** para proyectos escalables.

---

## 🧱 Estructura del Proyecto

```
├── data/                  # Datos de entrada y salida
│   ├── raw/              # Datos sin procesar
│   ├── processed/        # Datos procesados
│   ├── output/           # Resultados generados
│   └── reports/          # Informes y visualizaciones
│
├── examples/             # Ejemplos de uso
│   ├── quickstart_price_series.py
│   ├── quickstart_monte_carlo.py
│   └── quickstart_macro.py
│
├── src/                  # Código fuente
│   ├── analysis/         # Módulos de análisis
│   │   └── entities/     # Entidades de análisis Monte Carlo
│   │
│   ├── core/            # Entidades principales
│   │   └── entities/    # Series temporales y carteras
│   │
│   ├── extractor/       # Extractores de datos
│   │   └── sources/     # Fuentes de datos (Yahoo, Alpha Vantage, etc.)
│   │
│   ├── plots/           # Visualizaciones
│   │
│   └── reports/         # Generación de informes
│
└── tests/               # Tests unitarios
```

### 🔧 Patrones de Diseño Implementados

- **Strategy Pattern**: Extractores de datos y análisis
- **Template Method**: Generación de informes
- **Observer Pattern**: Monitoreo de simulaciones
- **Chain of Responsibility**: Procesamiento de métricas
- **Factory Method**: Creación de extractores
- **Builder Pattern**: Construcción de simulaciones
- **Bridge Pattern**: Abstracción de visualizaciones

---

## 🚀 Características Principales

### 📈 Análisis de Series de Precios
- Extracción de datos históricos de **múltiples APIs**:
  - Yahoo Finance
  - Alpha Vantage
  - Financial Modeling Prep
  - EOD Historical Data
- Estandarización automática de datos
- Cálculo de métricas financieras
- Visualizaciones interactivas

### 💹 Simulación Monte Carlo
- Simulación de evolución de activos
- Análisis de carteras de inversión
- Generación de escenarios múltiples
- Métricas de riesgo y rendimiento:
  - VaR (Value at Risk)
  - CVaR (Conditional VaR)
  - Drawdown análisis
  - Estadísticas de retorno

### 📊 Análisis Macroeconómico
- Integración con datos del Banco Mundial
- Análisis de indicadores económicos
- Series temporales macroeconómicas
- Correlaciones entre indicadores

### 📋 Informes y Visualización
- Generación automática de informes en Markdown
- Gráficos interactivos y estáticos
- Análisis detallado de resultados
- Exportación de datos procesados

### 🔄 Infraestructura
- Arquitectura modular y escalable
- Implementación de patrones de diseño
- Tests unitarios completos
- Contenedorización con Docker 🐳

---

## ⚙️ Instalação

### 🔹 Opção 1: Local

```bash
git clone https://github.com/piettro/Master-MIAX-Tarea-Bloque1-Introduccion.git
cd portfolio-toolkit
pip install -r requirements.txt
