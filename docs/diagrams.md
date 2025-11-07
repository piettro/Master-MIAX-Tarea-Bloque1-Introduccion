# 🎨 Diagramas da Arquitetura

## 📊 Diagrama de Classes Principal (Mermaid)

```mermaid
graph TB
    subgraph "🎯 User Interface"
        CLI[CLI Interface]
        EX[Examples]
    end
    
    subgraph "📝 Reports Layer"
        RB[ReportBase]
        RM[ReportMacro]
        RP[ReportPortfolio]
        RMC[ReportMonteCarlo]
        RPS[ReportPriceSeries]
    end
    
    subgraph "📊 Visualization Layer"
        PM[PlotMacro]
        PMC[PlotMonteCarlo]
        PP[PlotPortfolio]
        PPS[PlotPriceSeries]
    end
    
    subgraph "🧠 Analysis Layer"
        MCB[MonteCarloBase]
        MCR[MonteCarloReturns]
        MCP[MonteCarloPortfolios]
        MCC[MonteCarloCombined]
        MCM[MonteCarloMetrics]
    end
    
    subgraph "💾 Core Entities"
        TS[TimeSeries]
        PS[PriceSeries]
        PF[Portfolio]
        MS[MacroSeries]
    end
    
    subgraph "🔌 Extraction Layer"
        PE[PricesExtractor]
        ME[MacroExtractor]
        
        subgraph "Price Sources"
            YE[YahooExtractor]
            AE[AlphaVantageExtractor]
            FE[FMPExtractor]
            EE[EODHDExtractor]
        end
        
        subgraph "Macro Sources"
            WE[WorldBankExtractor]
        end
    end
    
    subgraph "🌐 External APIs"
        YF[Yahoo Finance]
        AV[Alpha Vantage]
        FM[Financial Modeling Prep]
        ED[EOD Historical Data]
        WB[World Bank]
    end
    
    %% Connections
    CLI --> RB
    EX --> RB
    RB --> TS
    RM --> MS
    RP --> PF
    RMC --> MCB
    RPS --> PS
    
    RB --> PM
    RB --> PMC
    RB --> PP
    RB --> PPS
    
    MCB --> MCR
    MCB --> MCP
    MCB --> MCC
    MCB --> MCM
    
    TS --> PS
    TS --> MS
    PS --> PF
    
    PS --> PE
    MS --> ME
    PF --> PE
    
    PE --> YE
    PE --> AE
    PE --> FE
    PE --> EE
    
    ME --> WE
    
    YE --> YF
    AE --> AV
    FE --> FM
    EE --> ED
    WE --> WB
    
    %% Styling
    classDef userInterface fill:#e1f5fe
    classDef reports fill:#f3e5f5
    classDef visualization fill:#e8f5e8
    classDef analysis fill:#fff3e0
    classDef core fill:#fce4ec
    classDef extraction fill:#f1f8e9
    classDef external fill:#ffebee
    
    class CLI,EX userInterface
    class RB,RM,RP,RMC,RPS reports
    class PM,PMC,PP,PPS visualization
    class MCB,MCR,MCP,MCC,MCM analysis
    class TS,PS,PF,MS core
    class PE,ME,YE,AE,FE,EE,WE extraction
    class YF,AV,FM,ED,WB external
```

## 🏗️ Diagrama de Componentes

```mermaid
graph LR
    subgraph "Application Layer"
        A[Examples & CLI]
    end
    
    subgraph "Service Layer"
        B[Reports Service]
        C[Visualization Service]
    end
    
    subgraph "Domain Layer"
        D[Analysis Entities]
        E[Core Entities]
    end
    
    subgraph "Infrastructure Layer"
        F[Data Extractors]
        G[External APIs]
    end
    
    A --> B
    A --> C
    B --> D
    B --> E
    C --> D
    C --> E
    D --> E
    E --> F
    F --> G
```

## 🔄 Diagrama de Fluxo de Dados

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Report
    participant Analysis
    participant Core
    participant Extractor
    participant API
    
    User->>CLI: Request Analysis
    CLI->>Report: Generate Report
    Report->>Analysis: Run Simulation
    Analysis->>Core: Get Portfolio Data
    Core->>Extractor: Fetch Price Data
    Extractor->>API: API Call
    API-->>Extractor: Raw Data
    Extractor-->>Core: Standardized Data
    Core-->>Analysis: Portfolio Object
    Analysis-->>Report: Results
    Report-->>CLI: Formatted Report
    CLI-->>User: Display Results
```

## 🎯 Padrões de Design por Módulo

```mermaid
graph TD
    subgraph "Strategy Pattern"
        S1[Extractors]
        S2[Analysis Methods]
        S3[Visualization Types]
    end
    
    subgraph "Template Method"
        T1[Report Generation]
        T2[Analysis Workflow]
        T3[Data Processing]
    end
    
    subgraph "Observer Pattern"
        O1[Statistics Updates]
        O2[Data Changes]
        O3[Progress Monitoring]
    end
    
    subgraph "Factory Method"
        F1[Extractor Creation]
        F2[Entity Instantiation]
        F3[Plot Generation]
    end
```

## 📊 Dependências Entre Camadas

```mermaid
graph BT
    Infrastructure[🔌 Infrastructure Layer]
    Domain[💾 Domain Layer]
    Service[📊 Service Layer]
    Application[🎯 Application Layer]
    
    Domain --> Infrastructure
    Service --> Domain
    Application --> Service
    
    Infrastructure -.-> Domain
    Domain -.-> Service
    Service -.-> Application
```