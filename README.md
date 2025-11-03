# 📊 Tarea 1 - MIAX

Ferramenta modular para **obtenção, padronização e análise de dados financeiros** (ações, índices, carteiras e simulações de Monte Carlo).

Este projeto faz parte de uma tarefa do programa Master e tem como objetivo praticar **boas práticas de arquitetura, abstração e padronização de código** para projetos escaláveis.

---

## 🧱 Estrutura do Projeto

tarea_bloque_1_introduccion/
├── src/
│   ├── __init__.py
│   │
│   ├── core/                     # Núcleo lógico do projeto (modelos e cálculos)
│   │   ├── __init__.py
│   │   ├── dataclasses.py        # Classes: PriceSeries, Portfolio
│   │   ├── montecarlo.py         # Simulação de Monte Carlo
│   │   ├── statistics.py         # Funções estatísticas gerais (média, desvio, etc.)
│   │   ├── transformer.py        # Limpeza e padronização dos dados
│   │   └── loader.py             # Salvamento de dados processados (parte do ETL)
│   │
│   ├── extractor/                # Módulo de extração (ETL: Extract)
│   │   ├── __init__.py
│   │   ├── api_extractor.py      # Classe central de extração (coordena fontes)
│   │   └── sources/              # Módulos específicos por fonte
│   │       ├── __init__.py
│   │       ├── yahoo.py
│   │       ├── alphavantage.py
│   │       ├── fmp.py
│   │       └── eodhd.py
│   │
│   ├── portfolios/               # Lógica de carteiras e agregações
│   │   ├── __init__.py
│   │   ├── portfolio_builder.py  # Criação de carteiras a partir de séries de preços
│   │   ├── optimization.py       # (futuro) otimização de pesos e métricas
│   │   └── risk.py               # Cálculos de volatilidade, covariância, etc.
│   │
│   ├── reports/                  # Geração de relatórios e visualizações
│   │   ├── __init__.py
│   │   ├── report_generator.py   # .report() e exportação Markdown
│   │   ├── plots.py              # .plots_report() e geração de gráficos
│   │   └── templates/            # (opcional) templates Markdown/HTML
│   │
│   ├── interfaces/               # Interações com o usuário
│   │   ├── __init__.py
│   │   ├── cli.py                # Interface via linha de comando
│   │   └── api_interface.py      # (futuro) interface REST se for expandido
│   │
│   └── utils/                    # Funções auxiliares genéricas
│       ├── __init__.py
│       ├── io.py                 # Leitura/escrita de dados e controle de diretórios
│       ├── config.py             # Configurações globais e leitura de .env
│       ├── logging_config.py     # Setup de logs
│       └── exceptions.py         # Definições de erros personalizados
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── output/
│
├── tests/
│   ├── test_extractor.py
│   ├── test_transformer.py
│   ├── test_portfolio.py
│   └── test_montecarlo.py
│
├── examples/
│   ├── quickstart.py
│   └── montecarlo_demo.py
│
├── .venv/
├── .gitignore
├── .env
├── .dockerignore
├── LICENSE
├── requirements.txt
├── setup.cfg
├── Dockerfile
└── README.md

---

## 🚀 Funcionalidades Principais

- Extração de dados históricos de **múltiplas APIs** (ex: Yahoo Finance, Alpha Vantage)
- Padronização do formato de dados independente da origem
- Criação de **DataClasses** para séries temporais e carteiras
- Estatísticas automáticas (média, desvio padrão)
- **Simulação de Monte Carlo** da evolução de ativos ou carteiras
- Geração de **relatórios formatados em Markdown**
- Criação automática de gráficos e visualizações (.plots_report)
- Projeto pronto para rodar em **Docker** 🐳

---

## ⚙️ Instalação

### 🔹 Opção 1: Local

```bash
git clone https://github.com/SEU-USUARIO/portfolio-toolkit.git
cd portfolio-toolkit
pip install -r requirements.txt
