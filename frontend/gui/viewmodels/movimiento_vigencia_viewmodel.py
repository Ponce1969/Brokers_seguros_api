"""
ViewModel para la gestión de movimientos de vigencia
"""

from typing import List, Optional
from datetime import date
import logging
from PyQt6.QtCore import QObject, pyqtSignal

from ..models.movimiento_vigencia import MovimientoVigencia
from ..core.excepciones import ErrorAPI

# Configurar logging
logger = logging.getLogger(__name__)

class MovimientoVigenciaViewModel(QObject):
    """
    ViewModel para manejar la lógica de negocio relacionada con movimientos de vigencia
    """
    
    # Señales
    movimiento_actualizado = pyqtSignal(MovimientoVigencia)
    movimientos_actualizados = pyqtSignal(list)
    error_ocurrido = pyqtSignal(str)
    
    def __init__(self):
        """Inicializa el ViewModel de movimientos de vigencia"""
        super().__init__()
        self.movimientos: List[MovimientoVigencia] = []
        self.movimiento_actual: Optional[MovimientoVigencia] = None

    async def cargar_movimientos(self, corredor_id: Optional[int] = None) -> None:
        """
        Carga la lista de movimientos desde el servidor
        
        Args:
            corredor_id: ID del corredor para filtrar movimientos (opcional)
        """
        try:
            logger.info("📥 Cargando lista de movimientos...")
            # TODO: Implementar llamada a la API
            # endpoint = f"api/v1/movimientos_vigencia"
            # if corredor_id:
            #     endpoint += f"?corredor_id={corredor_id}"
            # self.movimientos = await self.api.get(endpoint)
            # self.movimientos_actualizados.emit(self.movimientos)
            logger.info(f"✅ {len(self.movimientos)} movimientos cargados")
        except ErrorAPI as e:
            mensaje = f"Error al cargar movimientos: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        except Exception as e:
            mensaje = f"Error inesperado al cargar movimientos: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)

    async def crear_movimiento(self, datos: dict) -> Optional[MovimientoVigencia]:
        """
        Crea un nuevo movimiento de vigencia
        
        Args:
            datos: Diccionario con los datos del movimiento
            
        Returns:
            MovimientoVigencia: El movimiento creado o None si hubo error
        """
        try:
            logger.info("📝 Creando nuevo movimiento...")
            # TODO: Implementar llamada a la API
            # movimiento = await self.api.post("api/v1/movimientos_vigencia", datos)
            # self.movimientos.append(movimiento)
            # self.movimiento_actualizado.emit(movimiento)
            # return movimiento
            logger.info("✅ Movimiento creado exitosamente")
        except ErrorAPI as e:
            mensaje = f"Error al crear movimiento: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        except Exception as e:
            mensaje = f"Error inesperado al crear movimiento: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        return None

    async def actualizar_movimiento(self, id: int, datos: dict) -> Optional[MovimientoVigencia]:
        """
        Actualiza un movimiento existente
        
        Args:
            id: ID del movimiento a actualizar
            datos: Diccionario con los datos actualizados
            
        Returns:
            MovimientoVigencia: El movimiento actualizado o None si hubo error
        """
        try:
            logger.info(f"📝 Actualizando movimiento {id}...")
            # TODO: Implementar llamada a la API
            # movimiento = await self.api.put(f"api/v1/movimientos_vigencia/{id}", datos)
            # self.movimiento_actualizado.emit(movimiento)
            # return movimiento
            logger.info("✅ Movimiento actualizado exitosamente")
        except ErrorAPI as e:
            mensaje = f"Error al actualizar movimiento: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        except Exception as e:
            mensaje = f"Error inesperado al actualizar movimiento: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        return None

    def buscar_movimiento(self, id: int) -> Optional[MovimientoVigencia]:
        """
        Busca un movimiento por su ID
        
        Args:
            id: ID del movimiento a buscar
            
        Returns:
            MovimientoVigencia: El movimiento encontrado o None
        """
        return next((m for m in self.movimientos if m.id == id), None)

    def filtrar_movimientos(self, texto: str) -> List[MovimientoVigencia]:
        """
        Filtra la lista de movimientos por texto
        
        Args:
            texto: Texto a buscar
            
        Returns:
            List[MovimientoVigencia]: Lista de movimientos que coinciden
        """
        texto = texto.lower()
        return [
            m for m in self.movimientos
            if texto in m.numero_poliza.lower() or 
               texto in (m.cliente_nombre or '').lower() or
               texto in (m.corredor_nombre or '').lower() or
               texto in (m.tipo_seguro_nombre or '').lower()
        ]

    def get_movimientos_vigentes(self) -> List[MovimientoVigencia]:
        """
        Obtiene la lista de movimientos vigentes
        
        Returns:
            List[MovimientoVigencia]: Lista de movimientos vigentes
        """
        return [m for m in self.movimientos if m.vigente]

    def get_movimientos_por_vencer(self, dias: int = 30) -> List[MovimientoVigencia]:
        """
        Obtiene la lista de movimientos próximos a vencer
        
        Args:
            dias: Número de días para considerar próximo a vencer
            
        Returns:
            List[MovimientoVigencia]: Lista de movimientos próximos a vencer
        """
        hoy = date.today()
        return [
            m for m in self.movimientos 
            if m.vigente and (m.fecha_vencimiento - hoy).days <= dias
        ]
