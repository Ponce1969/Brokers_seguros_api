"""Gestión de temas (claro/oscuro) para la aplicación"""

import logging
from enum import Enum
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class Theme(Enum):
    """Enumeración para los temas disponibles"""
    LIGHT = "light"
    DARK = "dark"

class ThemeManager:
    """Gestor de temas para la aplicación"""
    
    # Colores del tema claro
    LIGHT_THEME = {
        "primary": "#1a73e8",       # Azul primario
        "primary_dark": "#1967d2", # Azul primario oscuro
        "primary_light": "#90c2ff", # Azul primario claro
        "text": "#202124",         # Texto principal
        "text_secondary": "#5f6368", # Texto secundario
        "background": "#f8f9fc",    # Fondo principal
        "background_alt": "#f1f3f4", # Fondo alternativo
        "surface": "#ffffff",      # Superficie (tarjetas, elementos)
        "border": "#dadce0",       # Bordes estándar
        "error": "#d93025",        # Color de error
        "warning": "#f29900",      # Color de advertencia
        "success": "#188038",      # Color de éxito
    }
    
    # Colores del tema oscuro
    DARK_THEME = {
        "primary": "#8ab4f8",       # Azul primario (más claro para modo oscuro)
        "primary_dark": "#669df6", # Azul primario oscuro 
        "primary_light": "#aecbfa", # Azul primario claro
        "text": "#e8eaed",         # Texto principal
        "text_secondary": "#9aa0a6", # Texto secundario
        "background": "#202124",    # Fondo principal
        "background_alt": "#303134", # Fondo alternativo
        "surface": "#292a2d",      # Superficie (tarjetas, elementos)
        "border": "#5f6368",       # Bordes estándar
        "error": "#f28b82",        # Color de error
        "warning": "#fdd663",      # Color de advertencia
        "success": "#81c995",      # Color de éxito
    }
    
    @classmethod
    def apply_theme(cls, app: QApplication, theme: Theme = Theme.LIGHT):
        """Aplica un tema específico a la aplicación
        
        Args:
            app: Instancia de QApplication
            theme: Tema a aplicar (LIGHT o DARK)
        """
        import os
        
        # Asegurarse de que estamos usando el estilo Fusion
        app.setStyle("Fusion")
        
        # Seleccionar los colores según el tema
        colors = cls.LIGHT_THEME if theme == Theme.LIGHT else cls.DARK_THEME
        
        # Crear una nueva paleta
        palette = QPalette()
        
        # Configurar colores comunes
        palette.setColor(QPalette.ColorRole.Window, QColor(colors["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["text"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors["surface"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["background_alt"]))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors["surface"]))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors["text"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors["text"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors["primary"]))
        # En tema oscuro, el texto de los botones debe ser blanco o claro
        # En tema claro, el texto de los botones puede ser oscuro o blanco dependiendo del fondo
        if theme == Theme.DARK:
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
        else:
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["surface"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["surface"]))
        
        # Roles adicionales para tema oscuro
        if theme == Theme.DARK:
            palette.setColor(QPalette.ColorRole.Link, QColor(colors["primary_light"]))
            palette.setColor(QPalette.ColorRole.LinkVisited, QColor(colors["primary"]))
            
            # Colores para widgets deshabilitados
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, 
                            QColor(colors["text_secondary"]))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, 
                            QColor(colors["text_secondary"]))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, 
                            QColor(colors["text_secondary"]))
        else:
            # Colores para widgets deshabilitados en tema claro
            disabled_color = "#9aa0a6"  # Gris medio
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, 
                            QColor(disabled_color))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, 
                            QColor(disabled_color))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, 
                            QColor(disabled_color))
        
        # Aplicar la paleta
        app.setPalette(palette)
        
        # Guardar el tema actual como propiedad de la aplicación para referencia futura
        app.setProperty("theme", theme.value)
        
        # Cargar y aplicar archivo QSS según el tema
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        qss_file = "styles_light.qss" if theme == Theme.LIGHT else "styles_dark.qss"
        styles_path = os.path.join(base_path, "resources", qss_file)
        
        # Asegurarse de usar únicamente los archivos de tema específicos
        # (Se eliminó el código que permitía usar styles.qss como respaldo)
        
        if os.path.exists(styles_path):
            try:
                with open(styles_path, 'r', encoding='utf-8') as file:
                    app.setStyleSheet(file.read())
                logger.info(f"Estilos QSS aplicados desde {styles_path}")
            except Exception as e:
                logger.error(f"Error al cargar archivo QSS: {e}")
        else:
            logger.warning(f"No se encontró archivo de estilos QSS en {styles_path}")
        
        logger.info(f"Tema {theme.value} aplicado correctamente")
        
    @classmethod
    def toggle_theme(cls, app: QApplication):
        """Alterna entre temas claro y oscuro
        
        Args:
            app: Instancia de QApplication
        """
        current_theme = app.property("theme")
        
        if not current_theme or current_theme == Theme.DARK.value:
            cls.apply_theme(app, Theme.LIGHT)
        else:
            cls.apply_theme(app, Theme.DARK)
    
    @classmethod
    def get_current_theme(cls, app: QApplication) -> Theme:
        """Obtiene el tema actual de la aplicación
        
        Args:
            app: Instancia de QApplication
            
        Returns:
            El tema actual (Theme.LIGHT o Theme.DARK)
        """
        current_theme = app.property("theme")
        
        if not current_theme or current_theme == Theme.LIGHT.value:
            return Theme.LIGHT
        return Theme.DARK
