"""
Gestor de temas y estilos para la aplicación.

Este módulo proporciona funcionalidades para cargar y aplicar estilos,
procesar variables CSS y cambiar entre diferentes temas.
"""

import os
import re
import logging
from enum import Enum, auto
from typing import Dict, Optional
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class Theme(Enum):
    """Enumeración de temas disponibles"""
    LIGHT = auto()
    DARK = auto()  # Para uso futuro

class ThemeManager:
    """
    Gestiona los temas y estilos de la aplicación.
    
    Esta clase se encarga de cargar, procesar y aplicar hojas de estilo QSS,
    incluyendo el procesamiento de variables CSS que no son nativamente
    soportadas por PyQt6.
    """
    
    # Definición de colores para el tema claro
    LIGHT_THEME_COLORS = {
        "--primary-color": "#007bff",
        "--hover-color": "#0056b3",
        "--pressed-color": "#004085",
        "--disabled-color": "#6c757d",
        "--danger-color": "#dc3545",
        "--danger-hover": "#bd2130",
        "--background": "#f0f0f0",
        "--text-color": "#333",
        "--nav-title-bg": "#f8f9fa",
        "--border-color": "#ddd",
        "--grid-color": "#eee",
    }
    
    # Definición de colores para el tema oscuro (para implementación futura)
    DARK_THEME_COLORS = {
        "--primary-color": "#0d6efd",
        "--hover-color": "#0b5ed7",
        "--pressed-color": "#0a58ca",
        "--disabled-color": "#6c757d",
        "--danger-color": "#dc3545",
        "--danger-hover": "#bb2d3b",
        "--background": "#212529",
        "--text-color": "#f8f9fa",
        "--nav-title-bg": "#343a40",
        "--border-color": "#495057",
        "--grid-color": "#343a40",
    }
    
    def __init__(self, styles_path: Optional[str] = None):
        """Inicializa el gestor de temas con el tema predeterminado (claro)
        
        Args:
            styles_path: Ruta opcional al archivo .qss. Si es None, se usa la ruta por defecto.
        """
        self.current_theme = Theme.LIGHT
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.styles_path = styles_path or os.path.join(self.base_path, "resources", "styles.qss")
        self.processed_stylesheet = ""
        self.theme_changed_callback = None  # Callback opcional para notificar cambios de tema
        
        # Cargar el estilo en la inicialización
        self.load_stylesheet()
    
    def get_theme_colors(self, theme: Theme = None) -> Dict[str, str]:
        """
        Obtiene el diccionario de colores para el tema especificado.
        
        Args:
            theme: Tema del cual obtener los colores. Si es None, se usa el tema actual.
            
        Returns:
            Diccionario con las variables CSS y sus valores correspondientes.
        """
        theme = theme or self.current_theme
        
        if theme == Theme.LIGHT:
            return self.LIGHT_THEME_COLORS
        elif theme == Theme.DARK:
            return self.DARK_THEME_COLORS
        else:
            logger.warning(f"Tema {theme} no reconocido, usando tema claro por defecto")
            return self.LIGHT_THEME_COLORS
    
    def load_stylesheet(self, theme: Theme = None) -> str:
        """
        Genera una hoja de estilos base usando los colores del tema actual.
        
        Args:
            theme: Tema a aplicar. Si es None, se usa el tema actual.
            
        Returns:
            Hoja de estilos base como cadena de texto.
        """
        if theme:
            self.current_theme = theme
            
        try:
            colors = self.get_theme_colors()
            
            # Crear un stylesheet base con los estilos comunes
            base_stylesheet = f"""
            /* Estilos globales */
            QWidget {{
                background-color: {colors.get('--background')};
                color: {colors.get('--text-color')};
            }}
            
            /* Botones normales */
            QPushButton {{
                background-color: {colors.get('--primary-color')};
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                text-align: left;
                font-size: 12px;
                margin-bottom: 5px;
            }}
            
            QPushButton:hover {{
                background-color: {colors.get('--hover-color')};
            }}
            
            QPushButton:pressed {{
                background-color: {colors.get('--pressed-color')};
            }}
            
            QPushButton:disabled {{
                background-color: {colors.get('--disabled-color')};
            }}
            
            /* Etiquetas */
            QLabel {{
                color: {colors.get('--text-color')};
                font-size: 14px;
            }}
            
            QLabel#titulo_nav {{
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background-color: {colors.get('--nav-title-bg')};
                border-radius: 5px;
                margin-bottom: 10px;
            }}
            
            /* Campos de texto */
            QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit {{
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
                border: 1px solid {colors.get('--primary-color')};
            }}
            
            /* Tablas */
            QTableWidget {{
                border: 1px solid {colors.get('--border-color')};
                background-color: white;
                alternate-background-color: #f9f9f9;
                selection-background-color: {colors.get('--primary-color')};
                selection-color: white;
            }}
            
            QTableWidget::item {{
                padding: 5px;
                border-bottom: 1px solid {colors.get('--grid-color')}; 
            }}
            
            QTableWidget::item:selected {{
                background-color: {colors.get('--primary-color')};
                color: white;
            }}
            
            /* Cabeceras de tabla */
            QHeaderView::section {{
                background-color: {colors.get('--nav-title-bg')};
                padding: 5px;
                border: 1px solid {colors.get('--border-color')};
                font-weight: bold;
            }}
            """
            
            self.processed_stylesheet = base_stylesheet
            logger.info(f"✅ Estilos generados correctamente para tema: {self.current_theme.name}")
            return base_stylesheet
            
        except Exception as e:
            logger.error(f"❌ Error al generar estilos: {e}")
            return ""
    
    def apply_stylesheet(self, app: Optional[QApplication] = None) -> None:
        """
        Aplica la hoja de estilos base a la aplicación.
        
        Args:
            app: Instancia de QApplication a la que aplicar los estilos.
                Si es None, se usa QApplication.instance().
        """
        try:
            target_app = app or QApplication.instance()
            if target_app:
                if not self.processed_stylesheet:
                    self.load_stylesheet()
                
                # Configurar paleta de colores para mejorar la apariencia general
                colors = self.get_theme_colors()
                
                # Generar una paleta coherente con el tema
                from PyQt6.QtGui import QPalette, QColor
                palette = QPalette()
                
                # Configurar colores comunes
                palette.setColor(QPalette.ColorRole.Window, QColor(colors.get('--background')))
                palette.setColor(QPalette.ColorRole.WindowText, QColor(colors.get('--text-color')))
                palette.setColor(QPalette.ColorRole.Base, QColor('white'))
                palette.setColor(QPalette.ColorRole.AlternateBase, QColor('#f9f9f9'))
                palette.setColor(QPalette.ColorRole.ToolTipBase, QColor('white'))
                palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors.get('--text-color')))
                palette.setColor(QPalette.ColorRole.Text, QColor(colors.get('--text-color')))
                palette.setColor(QPalette.ColorRole.Button, QColor(colors.get('--primary-color')))
                palette.setColor(QPalette.ColorRole.ButtonText, QColor('white'))
                palette.setColor(QPalette.ColorRole.Highlight, QColor(colors.get('--primary-color')))
                palette.setColor(QPalette.ColorRole.HighlightedText, QColor('white'))
                
                # Aplicar la paleta
                target_app.setPalette(palette)
                
                # Aplicar la hoja de estilos
                target_app.setStyleSheet(self.processed_stylesheet)
                logger.info(f"✅ Estilos y paleta aplicados correctamente a la aplicación")
            else:
                logger.warning("⚠️ No se pudo aplicar el estilo: QApplication no disponible")
        except Exception as e:
            logger.error(f"❌ Error al aplicar estilos: {e}")
    
    def set_theme_changed_callback(self, callback) -> None:
        """
        Registra una función para ser llamada cuando cambia el tema.
        
        Args:
            callback: Función a llamar cuando cambie el tema. Recibirá el tema como argumento.
        """
        self.theme_changed_callback = callback
        
    def reload_styles(self, app: Optional[QApplication] = None) -> None:
        """
        Recarga los estilos sin cambiar el tema actual.
        
        Útil cuando se modifica el archivo .qss manualmente y se quieren aplicar
        los cambios sin reiniciar la aplicación.
        
        Args:
            app: Instancia de QApplication a la que aplicar los estilos.
                Si es None, se usa QApplication.instance().
        """
        self.load_stylesheet()
        self.apply_stylesheet(app)
        logger.info("🔄 Estilos recargados correctamente")
        
    def change_theme(self, theme: Theme, app: Optional[QApplication] = None) -> None:
        """
        Cambia el tema actual y aplica los nuevos estilos.
        
        Args:
            theme: Nuevo tema a aplicar.
            app: Instancia de QApplication a la que aplicar los estilos.
                Si es None, se usa QApplication.instance().
        """
        if theme != self.current_theme:
            self.current_theme = theme
            self.load_stylesheet()
            self.apply_stylesheet(app)
            
            # Notificar a otros componentes del cambio de tema si hay un callback registrado
            if self.theme_changed_callback:
                self.theme_changed_callback(theme)
                
            logger.info(f"✅ Tema cambiado a: {theme.name}")

# Instancia global del gestor de temas para usar en toda la aplicación
theme_manager = ThemeManager()
