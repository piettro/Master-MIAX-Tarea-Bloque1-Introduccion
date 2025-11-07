# 🎨 Diagramas de la Arquitectura

## 📊 Diagrama de Clases Principal (Mermaid)

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
        A[Ejemplos y CLI]
    end
    
    subgraph "Service Layer"
        B[Servicio de Informes]
        C[Servicio de Visualización]
    end
    
    subgraph "Domain Layer"
        D[Entidades de Análisis]
        E[Entidades Centrales]
    end
    
    subgraph "Infrastructure Layer"
        F[Extractores de Datos]
        G[APIs Externas]
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

## 🔄 Diagrama de Flujo de Datos

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Report
    participant Analysis
    participant Core
    participant Extractor
    participant API
    
    User->>CLI: Solicitud de Análisis
    CLI->>Report: Generar Informe
    Report->>Analysis: Ejecutar Simulación
    Analysis->>Core: Obtener Datos de Cartera
    Core->>Extractor: Buscar Datos de Precios
    Extractor->>API: Llamada API
    API-->>Extractor: Datos en Bruto
    Extractor-->>Core: Datos Estandarizados
    Core-->>Analysis: Objeto Portfolio
    Analysis-->>Report: Resultados
    Report-->>CLI: Informe Formateado
    CLI-->>User: Mostrar Resultados
```

## 🎯 Patrones de Diseño por Módulo

```mermaid
graph TD
    subgraph "Strategy Pattern"
        S1[Extractores]
        S2[Métodos de Análisis]
        S3[Tipos de Visualización]
    end
    
    subgraph "Template Method"
        T1[Generación de Informes]
        T2[Flujo de Análisis]
        T3[Procesamiento de Datos]
    end
    
    subgraph "Observer Pattern"
        O1[Actualizaciones de Estadísticas]
        O2[Cambios de Datos]
        O3[Monitoreo de Progreso]
    end
    
    subgraph "Factory Method"
        F1[Creación de Extractores]
        F2[Instanciación de Entidades]
        F3[Generación de Gráficos]
    end
```

## 📊 Dependencias Entre Capas

```mermaid
graph BT
    Infrastructure[🔌 Capa de Infraestructura]
    Domain[💾 Capa de Dominio]
    Service[📊 Capa de Servicio]
    Application[🎯 Capa de Aplicación]
    
    Domain --> Infrastructure
    Service --> Domain
    Application --> Service
    
    Infrastructure -.-> Domain
    Domain -.-> Service
    Service -.-> Application
```