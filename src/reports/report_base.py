"""
Classe base para todos os relatórios do sistema.
Define a interface comum e funcionalidades básicas que todos os reports devem implementar.
"""

from abc import ABC, abstractmethod
import base64
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import matplotlib.pyplot as plt
import pandas as pd

class BaseReport(ABC):
    """
    Classe base abstrata para relatórios.
    Provê funcionalidades comuns e define a interface que todos os relatórios devem seguir.
    """
    
    def __init__(
        self,
        titulo: str,
        include_plots: bool = True,
        include_tables: bool = True,
    ):
        """
        Inicializa um novo relatório.
        
        Parameters
        ----------
        titulo : str
            Título do relatório
        include_plots : bool
            Se True, inclui visualizações no relatório
        include_tables : bool
            Se True, inclui tabelas de dados no relatório
        """
        self.titulo = titulo
        self.include_plots = include_plots
        self.include_tables = include_tables
        self.sections: List[Dict[str, Any]] = []
        
        # Setup do diretório de saída com estrutura organizada
        self._setup_output_directory()
        
    def add_section(
        self,
        title: str,
        content: str = "",
        level: int = 2
    ) -> None:
        """
        Adiciona uma nova seção ao relatório.
        
        Parameters
        ----------
        title : str
            Título da seção
        content : str
            Conteúdo em formato Markdown
        level : int
            Nível do título (1 a 6)
        """
        self.sections.append({
            'title': title,
            'content': content,
            'level': level
        })
        
    def add_table(
        self,
        data: pd.DataFrame,
        title: str,
        level: int = 3,
        format_dict: Optional[Dict] = None
    ) -> None:
        """
        Adiciona uma tabela ao relatório.
        
        Parameters
        ----------
        data : pd.DataFrame
            Dados para a tabela
        title : str
            Título da tabela
        level : int
            Nível do título
        format_dict : Dict, opcional
            Dicionário com formatos para cada coluna
        """
        if not self.include_tables:
            return
            
        # Criar cabeçalho da tabela
        table = [
            f"{'#' * level} {title}\n",
            "| " + " | ".join(data.columns) + " |",
            "|-" + "-|-".join(["-" * len(col) for col in data.columns]) + "-|"
        ]
        
        # Adicionar linhas
        for _, row in data.iterrows():
            formatted_row = []
            for col in data.columns:
                value = row[col]
                if format_dict and col in format_dict:
                    value = format_dict[col](value)
                formatted_row.append(str(value))
            table.append("| " + " | ".join(formatted_row) + " |")
            
        self.add_section(title="", content="\n".join(table), level=level)
        
    def add_plot(
        self,
        fig: plt.Figure,
        title: str,
        level: int = 3
    ) -> None:
        """
        Adiciona um plot ao relatório.
        
        Parameters
        ----------
        fig : plt.Figure
            Figura do matplotlib
        title : str
            Título do plot
        level : int
            Nível do título
        """
        if not self.include_plots:
            return
            
        # Converter figura para base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        content = f"\n![{title}](data:image/png;base64,{img_base64})"
        self.add_section(title=title, content=content, level=level)
        
    def add_metadata(self) -> None:
        """Adiciona metadados ao relatório."""
        metadata = [
            "---",
            f"Título: {self.titulo}",
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "---\n"
        ]
        self.sections.insert(0, {
            'title': '',
            'content': "\n".join(metadata),
            'level': 0
        })
        
    @abstractmethod
    def generate(self, auto_save: bool = True) -> Union[str, Path]:
        """
        Gera o conteúdo do relatório e opcionalmente salva em arquivo.
        Deve ser implementado pelas classes filhas.
        
        Parameters
        ----------
        auto_save : bool, opcional
            Se True, salva automaticamente o relatório após gerar (default: True)
            
        Returns
        -------
        Union[str, Path]
            Se auto_save=True: Path do arquivo salvo
            Se auto_save=False: Conteúdo do relatório em formato Markdown
        """
        pass
        
    def _setup_output_directory(self) -> None:
        """
        Configura a estrutura de diretórios para salvar os relatórios.
        Estrutura: base_dir/data/reports/tipo_report/YYYY-MM-DD/
        """
        # Diretório base (raiz do projeto)
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        
        # Data atual para organização
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Define o tipo de relatório com base no nome da classe
        report_type = self.__class__.__name__.lower().replace('report', '')
        
        # Criar estrutura de diretórios
        self.output_dir = self.base_dir / "data" / "reports" / report_type / today
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Diretório de saída configurado: {self.output_dir}")

    def save(self, symbols: Optional[List[str]] = None, custom_name: Optional[str] = None) -> Path:
        """
        Salva o relatório em arquivo markdown na estrutura de diretórios apropriada.
        
        Parameters
        ----------
        symbols : List[str], opcional
            Lista de símbolos para organização em subpastas
        custom_name : str, opcional
            Nome customizado para o arquivo (sem extensão)
            
        Returns
        -------
        Path
            Caminho do arquivo salvo
        """
        try:
            if custom_name:
                filename = custom_name
            elif symbols:
                symbol_part = "_".join(sorted(symbols)[:5])
                if len(symbols) > 5:
                    symbol_part += "_etc"
                filename = f"report_{symbol_part}"
            else:
                filename = f"report_{datetime.now().strftime('%H%M%S')}"
            
            self.add_metadata()
            
            full_report = []
            for section in self.sections:
                if section['level'] > 0:
                    full_report.append(f"{'#' * section['level']} {section['title']}")
                if section['content']:
                    full_report.append(section['content'])
                full_report.append("")
            
            output_path = self.output_dir / f"{filename}.md"
            
            output_path.write_text("\n".join(full_report), encoding='utf-8')
            
            print(f"Relatório salvo em: {output_path}")
            return output_path
            
        except Exception as e:
            raise ValueError(f"Erro ao salvar relatório: {str(e)}") from e
        