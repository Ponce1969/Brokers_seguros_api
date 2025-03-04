"""
Utilidad para aplicar efectos visuales avanzados a widgets de PyQt6

Proporciona funciones para crear sombras, efectos de elevación y otros
efectos visuales no disponibles directamente en QSS.
"""

from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

def apply_shadow(widget, radius=10, offset=3, color=None):
    """
    Aplica un efecto de sombra a cualquier widget de PyQt6
    
    Args:
        widget: Widget de PyQt6 al que aplicar la sombra
        radius: Radio de difusión de la sombra (8-12px recomendado)
        offset: Desplazamiento de la sombra (2-4px ideal)
        color: Color de la sombra (QColor con alpha ~60)
    """
    try:
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(radius)
        shadow.setXOffset(offset)
        shadow.setYOffset(offset)
        
        # Color por defecto: negro semitransparente
        if color is None:
            color = QColor(0, 0, 0, 60)
        shadow.setColor(color)
        
        widget.setGraphicsEffect(shadow)
        return True
    except Exception as e:
        logger.error(f"Error al aplicar sombra: {e}")
        return False

def apply_input_shadow(widget):
    """
    Aplica una sombra sutil optimizada para campos de entrada
    
    Args:
        widget: Campo de entrada (QLineEdit, QTextEdit, etc.)
    """
    return apply_shadow(widget, radius=8, offset=2, color=QColor(0, 0, 0, 40))

def apply_button_shadow(widget):
    """
    Aplica una sombra pronunciada optimizada para botones principales
    
    Args:
        widget: Botón (QPushButton)
    """
    return apply_shadow(widget, radius=10, offset=3, color=QColor(0, 0, 0, 60))

def apply_card_shadow(widget):
    """
    Aplica una sombra amplia pero suave para paneles y contenedores
    
    Args:
        widget: Contenedor (QWidget, QFrame, etc.)
    """
    return apply_shadow(widget, radius=15, offset=4, color=QColor(0, 0, 0, 50))
