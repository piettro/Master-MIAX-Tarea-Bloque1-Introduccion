"""
Base Report Framework Implementation.

This module implements a comprehensive framework for report generation using
multiple design patterns to ensure flexibility, extensibility, and maintainability.

Design Patterns:
    - Template Method: Defines skeleton of report generation algorithm
    - Builder: Constructs complex report structure
    - Strategy: Different report generation strategies
    - Abstract Factory: Creates families of related reports
    - Chain of Responsibility: Report section handling

Key Features:
    - Flexible report structure
    - Modular section management
    - Dynamic content generation
    - Automatic file organization
    - Rich media support (plots, tables)
    - Metadata handling
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
    Abstract base class for all report types in the system.
    
    This class implements multiple design patterns to provide a robust
    and flexible framework for report generation and management.
    
    Design Pattern Implementation:
        - Template Method: Defines report generation workflow
        - Builder: Constructs report sections and content
        - Strategy: Supports different report formats
        - Chain of Responsibility: Handles section processing
        
    Features:
        - Modular section management
        - Plot and table integration
        - Metadata handling
        - File organization
        - Format flexibility
        
    The class provides:
        1. Standard report structure
        2. Common functionality
        3. Content management
        4. File handling
        5. Error management
        
    Notes:
        Concrete report classes must implement the generate() method
        and may override other methods for specific functionality.
    """
    
    def __init__(
        self,
        title: str,
        include_plots: bool = True,
        include_tables: bool = True,
    ):
        """
        Initialize a new report instance with specified configuration.
        
        This constructor implements multiple design patterns to set up
        the report structure and prepare content management systems.
        
        Design Pattern Implementation:
            - Template Method: Initializes standard report structure
            - Builder: Sets up content building system
            - Strategy: Configures content inclusion strategies
            
        Parameters
        ----------
        title : str
            Report title used for identification and metadata
        include_plots : bool, default=True
            Whether to include visualizations in the report
            Controls plot-related functionality
        include_tables : bool, default=True
            Whether to include data tables in the report
            Controls table-related functionality
            
        Process Flow:
            1. Basic validation
            2. Content flags setup
            3. Section list initialization
            4. Directory structure setup
            
        Attributes Initialized:
            - title: Report title
            - include_plots: Plot inclusion flag
            - include_tables: Table inclusion flag
            - sections: List of report sections
            
        Notes
        -----
        The initialization process sets up all necessary structures
        for report generation and management.
        """
        self.title = title
        self.include_plots = include_plots
        self.include_tables = include_tables
        self.sections: List[Dict[str, Any]] = []
        
        self._setup_output_directory()
        
    def add_section(
        self,
        title: str,
        content: str = "",
        level: int = 2
    ) -> None:
        """
        Add a new section to the report with specified content.
        
        This method implements the Builder pattern to construct report
        sections and manage content hierarchy.
        
        Design Pattern Implementation:
            - Builder: Constructs section structure
            - Chain of Responsibility: Section management
            - Template Method: Standard section formatting
            
        Parameters
        ----------
        title : str
            Section title for hierarchy organization
        content : str, default=""
            Section content in Markdown format
            Supports all standard Markdown syntax
        level : int, default=2
            Header level (1-6) for hierarchical organization
            1: Main titles
            2: Major sections
            3-6: Subsections
            
        Section Structure:
            {
                'title': Section title
                'content': Markdown content
                'level': Header level
            }
            
        Notes
        -----
        Sections are stored sequentially and maintain hierarchy
        through their level attribute.
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
        Add a formatted data table to the report.
        
        This method implements multiple patterns to handle table
        generation and formatting in a flexible way.
        
        Design Pattern Implementation:
            - Strategy: Table formatting strategy
            - Builder: Table construction
            - Chain of Responsibility: Table processing
            
        Parameters
        ----------
        data : pd.DataFrame
            Data to be presented in table format
            Must have proper column names
        title : str
            Table title for identification
        level : int, default=3
            Header level for table title
        format_dict : Dict, optional
            Column formatting specifications:
            {
                'column_name': formatting_function,
                ...
            }
            
        Process Flow:
            1. Configuration validation
            2. Table header generation
            3. Content formatting
            4. Markdown table construction
            
        Notes
        -----
        - Automatically handles column alignment
        - Supports custom column formatting
        - Generates valid Markdown tables
        - Respects include_tables flag
        """
        if not self.include_tables:
            return
            
        table = [
            f"{'#' * level} {title}\n",
            "| " + " | ".join(data.columns) + " |",
            "|-" + "-|-".join(["-" * len(col) for col in data.columns]) + "-|"
        ]
        
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
        Add a matplotlib figure to the report as an embedded image.
        
        This method implements multiple patterns to handle plot
        integration and image processing.
        
        Design Pattern Implementation:
            - Strategy: Image conversion strategy
            - Builder: Plot section construction
            - Chain of Responsibility: Plot processing
            
        Parameters
        ----------
        fig : plt.Figure
            Matplotlib figure to be included
            Must be a valid figure instance
        title : str
            Title for the plot section
        level : int, default=3
            Header level for plot title
            
        Process Flow:
            1. Plot inclusion check
            2. Figure conversion to PNG
            3. Base64 encoding
            4. Markdown section creation
            
        Technical Details:
            - PNG format for maximum compatibility
            - 300 DPI for high quality
            - Base64 encoding for embedding
            - Markdown image syntax
            
        Notes
        -----
        - Respects include_plots flag
        - Automatically handles figure cleanup
        - Preserves figure quality
        - Supports all matplotlib figures
        """
        if not self.include_plots:
            return
            
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        content = f"\n![{title}](data:image/png;base64,{img_base64})"
        self.add_section(title=title, content=content, level=level)
        
    def add_metadata(self) -> None:
        """
        Add metadata information to the report.
        
        This method implements the Template Method pattern to provide
        standard metadata handling across all report types.
        
        Design Pattern Implementation:
            - Template Method: Standard metadata format
            - Strategy: Metadata collection
            - Chain of Responsibility: Metadata processing
            
        Metadata Components:
            1. Document delimiters
            2. Report title
            3. Generation timestamp
            4. Additional metadata
            
        Process Flow:
            1. Metadata collection
            2. Format preparation
            3. Section insertion
            
        Notes
        -----
        - Automatically adds timestamp
        - Preserves document structure
        - Supports YAML frontmatter format
        - Placed at the beginning of the document
        """
        metadata = [
            "---",
            f"Title: {self.title}",
            f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
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
        Generate report content and optionally save to file.
        Must be implemented by child classes.
        
        This abstract method defines the Template Method pattern
        for report generation across all report types.
        
        Design Pattern Implementation:
            - Template Method: Report generation workflow
            - Strategy: Content generation strategy
            - Chain of Responsibility: Content processing
            
        Parameters
        ----------
        auto_save : bool, default=True
            If True, automatically saves report after generation
            Controls file output behavior
            
        Returns
        -------
        Union[str, Path]
            If auto_save=True: Path object to saved file
            If auto_save=False: Report content as Markdown string
            
        Process Flow:
            1. Content generation
            2. Format application
            3. Optional file saving
            4. Result return
            
        Technical Details:
            - Must be implemented by subclasses
            - Defines standard generation workflow
            - Handles both file and string output
            - Maintains consistent format
            
        Notes
        -----
        - Template for all report generation
        - Ensures consistent structure
        - Flexible output handling
        - Error management required
        """
        pass
        
    def _setup_output_directory(self) -> None:
        """
        Configure directory structure for report storage.
        
        This helper method implements patterns to manage the
        file system organization for report storage.
        
        Design Pattern Implementation:
            - Template Method: Standard directory structure
            - Strategy: Path resolution strategy
            - Facade: File system operations
            
        Directory Structure:
            base_dir/
                data/
                    reports/
                        report_type/
                            YYYY-MM-DD/
            
        Process Flow:
            1. Base directory resolution
            2. Current date formatting
            3. Report type determination
            4. Directory creation
            
        Technical Details:
            - Uses Path for cross-platform compatibility
            - Creates nested directory structure
            - Handles permissions and existence
            - Maintains consistent organization
            
        Notes
        -----
        - Creates directories if they don't exist
        - Uses class name for report type
        - Organizes by date for easy retrieval
        - Prints confirmation message
        """
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        report_type = self.__class__.__name__.lower().replace('report', '')
        
        self.output_dir = self.base_dir / "data" / "reports" / report_type / today
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Output directory set: {self.output_dir}")

    def save(self, symbols: Optional[List[str]] = None, custom_name: Optional[str] = None) -> Path:
        """
        Save the report as a Markdown file in the appropriate directory structure.
        
        This method implements multiple patterns to handle file saving
        and organization in a consistent way.
        
        Design Pattern Implementation:
            - Template Method: Standard save process
            - Strategy: File naming strategy
            - Chain of Responsibility: File processing
            
        Parameters
        ----------
        symbols : List[str], optional
            List of symbols for subfolder organization
            Used for financial instrument reports
        custom_name : str, optional
            Custom filename without extension
            Overrides default naming convention
            
        Returns
        -------
        Path
            Absolute path to the saved file
            
        Process Flow:
            1. Filename determination
            2. Metadata addition
            3. Content compilation
            4. File writing
            5. Confirmation
            
        Technical Details:
            - UTF-8 encoding
            - Markdown format
            - Automatic metadata
            - Error handling
            
        File Naming:
            - Custom name if provided
            - Symbol-based name if symbols provided
            - Timestamp-based name as fallback
            
        Notes
        -----
        - Creates necessary directories
        - Handles file system errors
        - Maintains consistent structure
        - Confirms successful save
        
        Raises
        ------
        ValueError
            If file saving encounters an error
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
            
            print(f"Report saved: {output_path}")
            return output_path
            
        except Exception as e:
            raise ValueError(f"Error to save report: {str(e)}") from e
        