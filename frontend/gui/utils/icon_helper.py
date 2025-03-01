"""
Utilidad para cargar y gestionar iconos de la aplicación con soporte SVG y colores personalizados
"""

import os
import re
import logging
from PyQt6.QtCore import QSize, Qt, QRectF
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

logger = logging.getLogger(__name__)

class IconHelper:
    """
    Clase de utilidad para cargar iconos desde la carpeta de recursos
    """
    
    ICON_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons")
    
    @staticmethod
    def get_icon(name: str, color: str = None, size: int = 24) -> QIcon:
        """
        Obtiene un icono por su nombre desde la carpeta de recursos
        
        Args:
            name: Nombre del archivo de icono (sin extensión)
            color: Color opcional para aplicar al SVG (formato '#RRGGBB')
            size: Tamaño del icono (por defecto 24px)
            
        Returns:
            QIcon: Icono cargado o un icono por defecto si no se encuentra
        """
        try:
            # Construye la ruta completa del icono
            icon_path = os.path.join(IconHelper.ICON_BASE_DIR, f"{name}.svg")
            
            if not os.path.exists(icon_path):
                logger.warning(f"Ícono no encontrado: {icon_path}")
                return QIcon()
            
            # Si no se especifica un color personalizado, carga el icono directamente
            if not color:
                return QIcon(icon_path)
            
            # Si se especifica un color, carga el SVG y lo colorea
            return IconHelper._load_colored_svg(icon_path, color, size)
            
        except Exception as e:
            logger.error(f"Error al cargar icono '{name}': {e}")
            return QIcon()
    
    @staticmethod
    def _load_colored_svg(path: str, color: str, size: int = 24) -> QIcon:
        """
        Carga un SVG y lo colorea correctamente aplicando color de relleno y borde
        
        Args:
            path: Ruta al archivo SVG
            color: Color en formato '#RRGGBB'
            size: Tamaño en píxeles del icono
            
        Returns:
            QIcon: Icono SVG coloreado
        """
        try:
            # Crear iconos en varios tamaños para mejor escalado
            sizes = [size, int(size * 1.5)]  # Ej: 16px y 24px o 24px y 36px
            icon = QIcon()
            
            for icon_size in sizes:
                # Crear pixmap transparente
                pixmap = QPixmap(icon_size, icon_size)
                pixmap.fill(Qt.GlobalColor.transparent)
                
                # Renderizador del SVG
                renderer = QSvgRenderer(path)
                
                # Obtener tamaño del SVG original
                view_box = renderer.viewBoxF()
                
                # Crear un painter para renderizar el SVG en el pixmap
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                
                # Escalar el SVG para que ocupe todo el espacio del icono
                scale_factor = min(icon_size / view_box.width(), icon_size / view_box.height())
                scaled_view_box = QRectF(
                    (icon_size - view_box.width() * scale_factor) / 2,
                    (icon_size - view_box.height() * scale_factor) / 2,
                    view_box.width() * scale_factor,
                    view_box.height() * scale_factor
                )
                
                # Aplicar color personalizado (si es distinto de negro)
                if color and color.lower() != "#000000" and color != "black":
                    with open(path, "r", encoding="utf-8") as f:
                        xml_data = f.read()
                    
                    # Reemplazar cualquier fill="..." por el nuevo color
                    colored_xml = re.sub(r'fill="[^"]+"', f'fill="{color}"', xml_data)
                    
                    # Renderizar el SVG modificado
                    renderer = QSvgRenderer(bytes(colored_xml, "utf-8"))
                
                # Dibujar el SVG escalado y centrado
                renderer.render(painter, scaled_view_box)
                painter.end()
                
                # Agregar el pixmap al icono
                icon.addPixmap(pixmap)
            
            return icon
            
        except Exception as e:
            logger.error(f"Error al colorear SVG: {e}")
            return QIcon(path)  # Fallback al icono original
