"""
Utilidad para cargar y gestionar iconos de la aplicación con soporte SVG y colores personalizados

Proporciona funcionalidades para cargar iconos SVG, aplicar colores personalizados,
y optimizar el rendimiento mediante un sistema de caché.
"""

import os
import re
import logging
from typing import Dict, Tuple
from PyQt6.QtCore import QSize, Qt, QRectF
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

logger = logging.getLogger(__name__)

class IconHelper:
    """
    Clase de utilidad para cargar iconos desde la carpeta de recursos con soporte
    para coloreado de SVGs y sistema de caché para mejorar el rendimiento.
    """
    
    ICON_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons")
    
    # Cache para evitar recargar y reprocesar iconos constantemente
    # La clave es (nombre_icono, color, tamaño)
    _icon_cache: Dict[Tuple[str, str, int], QIcon] = {}
    
    # Lista de iconos SVG conocidos por ser problemáticos
    _PROBLEMATIC_SVGS = [
        "login", "user", "users", "calendar", "edit", "delete", "add"
    ]
    
    # Mapeo de iconos SVG problemáticos a sus equivalentes PNG (si existen)
    _PNG_MAPPING = {
        "edit": "editar.png",
        "delete": "eliminar.png",
        "add": "add.png",
        "login": "login.png",
        "user": "user.png",
        "users": "users.png",
        "calendar": "calendar.png",
        "dark_mode": "dark_mode.png",
        "light_mode": "light_mode.png",
        "corredor": "corredor.png",
        "clientes": "clientes.png",
        "movimientos": "movimientos.png"
    }
    
    @classmethod
    def _check_for_png(cls, name: str) -> str:
        """Busca una versión PNG del icono especificado
        
        Args:
            name: Nombre del icono sin extensión
            
        Returns:
            str: Ruta al archivo PNG si existe, o cadena vacía si no existe
        """
        # Verificar si tenemos un mapeo directo para este icono
        if name in cls._PNG_MAPPING:
            png_path = os.path.join(cls.ICON_BASE_DIR, cls._PNG_MAPPING[name])
            if os.path.exists(png_path):
                return png_path
                
        # Probar con varias combinaciones posibles
        posibles_nombres = [
            f"{name}.png",                 # nombre.png
            f"{name.lower()}.png",         # nombre_minúsculas.png
            f"{name}_icon.png",            # nombre_icon.png
            f"icon_{name}.png",            # icon_nombre.png
            f"{name.replace('_', '-')}.png"  # nombre-con-guiones.png (si tenía guiones bajos)
        ]
        
        for nombre_archivo in posibles_nombres:
            png_path = os.path.join(cls.ICON_BASE_DIR, nombre_archivo)
            if os.path.exists(png_path):
                return png_path
            
        return ""
    
    @classmethod
    def get_icon(cls, name: str, color: str = None, size: int = 24) -> QIcon:
        """
        Obtiene un icono por su nombre desde la carpeta de recursos,
        utilizando caché para optimizar el rendimiento.
        
        Args:
            name: Nombre del archivo de icono (sin extensión)
            color: Color opcional para aplicar al SVG (formato '#RRGGBB') - solo aplicable a SVGs
            size: Tamaño del icono (por defecto 24px)
            
        Returns:
            QIcon: Icono cargado o un icono por defecto si no se encuentra
        
        Note:
            Prioriza archivos PNG sobre SVG para todos los iconos
        """
        try:
            # Normalizar el color (convertir None a una cadena vacía para la clave de caché)
            normalized_color = color.lower() if color else ""
            
            # Verificar si el icono ya está en caché
            cache_key = (name, normalized_color, size)
            if cache_key in cls._icon_cache:
                return cls._icon_cache[cache_key]
            
            # Primero buscar si existe versión PNG del icono (prioridad sobre SVG)
            png_path = cls._check_for_png(name)
            if png_path:
                logger.debug(f"Usando archivo PNG para icono: {png_path}")
                icon = QIcon(png_path)
                cls._icon_cache[cache_key] = icon
                return icon
            
            # Si no hay PNG, buscar archivo SVG
            icon_path = os.path.join(cls.ICON_BASE_DIR, f"{name}.svg")
            
            if not os.path.exists(icon_path):
                logger.warning(f"Ícono no encontrado: {icon_path}")
                return QIcon()
            
            # Cargar el icono (con o sin color)
            if not color:
                icon = QIcon(icon_path)
            else:
                icon = cls._load_colored_svg(icon_path, color, size)
            
            # Guardar en caché para futuras solicitudes
            cls._icon_cache[cache_key] = icon
            return icon
            
        except Exception as e:
            logger.error(f"Error al cargar icono '{name}': {e}")
            return QIcon()
    
    @classmethod
    def _load_colored_svg(cls, path: str, color: str, size: int = 24) -> QIcon:
        """
        Carga un SVG y lo colorea correctamente aplicando color de relleno y borde.
        
        Optimizado para un mejor rendimiento usando un enfoque que minimiza la manipulación
        de XML cuando es posible.
        
        Args:
            path: Ruta al archivo SVG
            color: Color en formato '#RRGGBB'
            size: Tamaño en píxeles del icono
            
        Returns:
            QIcon: Icono SVG coloreado
        """
        try:
            # Normalizar el color
            if color:
                normalized_color = color.lower()
                is_default_color = normalized_color == "#000000" or normalized_color == "black"
            else:
                is_default_color = True
            
            # En caso de que sea el color predeterminado, cargar normalmente
            # Pero vamos a seguir el flujo normal para garantizar que todos los SVG
            # se traten de la misma manera
            
            # Crear iconos en varios tamaños para mejor escalado
            sizes = [size, int(size * 1.5)]  # Ej: 16px y 24px o 24px y 36px
            icon = QIcon()
            
            # Procesamos el XML para cambiar el color una sola vez
            try:
                with open(path, "r", encoding="utf-8") as f:
                    xml_data = f.read()
            except Exception as e:
                logger.warning(f"Error al leer el archivo SVG {path}: {e}")
                # Si no podemos leer el archivo, crear un icono de fallback
                pixmap = QPixmap(size, size)
                pixmap.fill(QColor(color))
                return QIcon(pixmap)
            
            # Limpiar el SVG para mayor compatibilidad
            # 1. Asegurar que tenga un viewBox válido
            if "viewBox" not in xml_data and "width" in xml_data and "height" in xml_data:
                # Extraer dimensiones y agregar viewBox si no existe
                width_match = re.search(r'width="([\d\.]+)(?:px)?"', xml_data)
                height_match = re.search(r'height="([\d\.]+)(?:px)?"', xml_data)
                if width_match and height_match:
                    width = width_match.group(1)
                    height = height_match.group(1)
                    # Buscar la etiqueta <svg y agregar viewBox
                    xml_data = re.sub(r'<svg([^>]*)>', 
                                    f'<svg\\1 viewBox="0 0 {width} {height}">', 
                                    xml_data)
                    logger.debug(f"Agregado viewBox='0 0 {width} {height}' a {path}")
            
            # 2. Eliminar atributos problemáticos que puedan causar problemas de renderizado
            problematic_attrs = ['version', 'xmlns:xlink', 'xml:space', 'xmlns:svg']
            for attr in problematic_attrs:
                xml_data = re.sub(f'{attr}="[^"]*"', '', xml_data)
                
            # 3. Asegurar que tenga namespace SVG correcto si no lo tiene
            if 'xmlns="http://www.w3.org/2000/svg"' not in xml_data:
                xml_data = re.sub(r'<svg', '<svg xmlns="http://www.w3.org/2000/svg"', xml_data)
            
            # Corregir el color de stroke si existe
            xml_data = xml_data.replace('stroke="currentColor"', f'stroke="{color}"')
            
            # Reemplazar colores en el XML
            # 1. Sustituir atributos de color explícitos (fill="color")
            colored_xml = re.sub(r'fill="[^"]+"', f'fill="{color}"', xml_data)
            # 2. Añadir fill a elementos sin color explícito (pero no sobreescribir 'none')
            colored_xml = re.sub(r'(<(?:path|rect|circle|ellipse|line|polyline|polygon)[^>]*?)(?!fill=)([^>]*?>)', 
                               f'\\1 fill="{color}"\\2', colored_xml)
            
            # Crear el renderizador con el XML modificado
            svg_renderer = QSvgRenderer(bytes(colored_xml, "utf-8"))
            
            # Verificar que el SVG se cargó correctamente
            if not svg_renderer.isValid():
                # Extraer el nombre del archivo de la ruta para comprobar si es un SVG problemático
                filename = os.path.basename(path)
                basename = os.path.splitext(filename)[0]
                
                # Si es un SVG problemático conocido, usar un warning silencioso para no contaminar el log
                if basename in cls._PROBLEMATIC_SVGS:
                    logger.debug(f"SVG problemático conocido: {basename}, usando respaldo")
                else:
                    logger.warning(f"El SVG no es válido: {path}")
                
                # Intentar crear un SVG mínimo válido con el color especificado
                minimal_svg = f'''
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
                    <rect width="24" height="24" fill="{color}" opacity="0.8" rx="4" ry="4"/>
                </svg>
                '''
                
                svg_renderer = QSvgRenderer(bytes(minimal_svg, "utf-8"))
                
                if not svg_renderer.isValid():
                    # Si aún falla, crear un pixmap de respaldo
                    pixmap = QPixmap(size, size)
                    pixmap.fill(QColor(color))
                    return QIcon(pixmap)
            
            # Obtener tamaño del SVG original
            view_box = svg_renderer.viewBoxF()
            
            # Verificar si el viewBox es válido
            if view_box.width() <= 0 or view_box.height() <= 0:
                # Tratar de extraer las dimensiones directamente del XML
                width_match = re.search(r'width="([\d\.]+)"', colored_xml)
                height_match = re.search(r'height="([\d\.]+)"', colored_xml)
                
                if width_match and height_match:
                    try:
                        width = float(width_match.group(1))
                        height = float(height_match.group(1))
                        view_box = QRectF(0, 0, width, height)
                        logger.info(f"Usando dimensiones del atributo: {width}x{height}")
                    except ValueError:
                        # Si no se puede convertir a float, usar valores predeterminados
                        view_box = QRectF(0, 0, 24, 24)
                        logger.warning(f"Usando dimensiones predeterminadas 24x24 para: {path}")
                else:
                    # Si no hay atributos width/height, usar tamaño predeterminado
                    view_box = QRectF(0, 0, 24, 24)
                    logger.warning(f"Usando dimensiones predeterminadas 24x24 para: {path}")
            
            for icon_size in sizes:
                # Crear pixmap transparente
                pixmap = QPixmap(icon_size, icon_size)
                pixmap.fill(Qt.GlobalColor.transparent)
                
                # Crear un painter para renderizar el SVG en el pixmap
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                
                # Solo necesitamos calcular una vez el factor de escala y el rectángulo de destino
                # para cada tamaño de icono, ya que el viewBox ya está normalizado
                
                # Calcular el rectángulo de destino para el SVG
                # Queremos que el SVG ocupe todo el espacio disponible respetando su relación de aspecto
                
                # El factor de escala debe mantener la relación de aspecto
                scale_factor = min(icon_size / view_box.width(), icon_size / view_box.height())
                
                # Centrar el SVG en el icono
                scaled_width = view_box.width() * scale_factor
                scaled_height = view_box.height() * scale_factor
                
                # Cálculo del offset para centrar correctamente
                offset_x = (icon_size - scaled_width) / 2
                offset_y = (icon_size - scaled_height) / 2
                
                # Construir el rectángulo de destino
                scaled_view_box = QRectF(
                    offset_x,
                    offset_y,
                    scaled_width,
                    scaled_height
                )
                
                # Dibujar el SVG escalado y centrado
                svg_renderer.render(painter, scaled_view_box)
                painter.end()
                
                # Agregar el pixmap al icono
                icon.addPixmap(pixmap)
            
            return icon
            
        except Exception as e:
            logger.error(f"Error al colorear SVG: {e}")
            return QIcon(path)  # Fallback al icono original
