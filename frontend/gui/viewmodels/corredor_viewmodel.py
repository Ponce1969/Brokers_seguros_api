"""
ViewModel para la gestión de corredores
"""

from typing import List, Optional
from datetime import datetime
import logging
from PyQt6.QtCore import QObject, pyqtSignal

from ..models.corredor import Corredor
from ..core.excepciones import ErrorAPI

# Configurar logging
logger = logging.getLogger(__name__)

class CorredorViewModel(QObject):
    """
    ViewModel para manejar la lógica de negocio relacionada con corredores
    """
    
    # Señales
    corredor_actualizado = pyqtSignal(Corredor)
    corredores_actualizados = pyqtSignal(list)
    error_ocurrido = pyqtSignal(str)
    
    def __init__(self):
        """Inicializa el ViewModel de corredores"""
        super().__init__()
        self.corredores: List[Corredor] = []
        self.corredor_actual: Optional[Corredor] = None

    async def cargar_corredores(self) -> None:
        """
        Carga la lista de corredores desde el servidor
        """
        try:
            logger.info("📥 Cargando lista de corredores...")
            # TODO: Implementar llamada a la API
            # self.corredores = await self.api.get("api/v1/corredores")
            # self.corredores_actualizados.emit(self.corredores)
            logger.info(f"✅ {len(self.corredores)} corredores cargados")
        except ErrorAPI as e:
            mensaje = f"Error al cargar corredores: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        except Exception as e:
            mensaje = f"Error inesperado al cargar corredores: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)

    async def crear_corredor(self, datos: dict) -> Optional[Corredor]:
        """
        Crea un nuevo corredor
        
        Args:
            datos: Diccionario con los datos del corredor
            
        Returns:
            Corredor: El corredor creado o None si hubo error
        """
        try:
            logger.info("📝 Creando nuevo corredor...")
            # TODO: Implementar llamada a la API
            # corredor = await self.api.post("api/v1/corredores", datos)
            # self.corredores.append(corredor)
            # self.corredor_actualizado.emit(corredor)
            # return corredor
            logger.info("✅ Corredor creado exitosamente")
        except ErrorAPI as e:
            mensaje = f"Error al crear corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        except Exception as e:
            mensaje = f"Error inesperado al crear corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        return None

    async def actualizar_corredor(self, id: str, datos: dict) -> Optional[Corredor]:
        """
        Actualiza un corredor existente
        
        Args:
            id: ID del corredor a actualizar
            datos: Diccionario con los datos actualizados
            
        Returns:
            Corredor: El corredor actualizado o None si hubo error
        """
        try:
            logger.info(f"📝 Actualizando corredor {id}...")
            # TODO: Implementar llamada a la API
            # corredor = await self.api.put(f"api/v1/corredores/{id}", datos)
            # self.corredor_actualizado.emit(corredor)
            # return corredor
            logger.info("✅ Corredor actualizado exitosamente")
        except ErrorAPI as e:
            mensaje = f"Error al actualizar corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        except Exception as e:
            mensaje = f"Error inesperado al actualizar corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        return None

    async def eliminar_corredor(self, id: str) -> bool:
        """
        Elimina un corredor
        
        Args:
            id: ID del corredor a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            logger.info(f"🗑️ Eliminando corredor {id}...")
            # TODO: Implementar llamada a la API
            # await self.api.delete(f"api/v1/corredores/{id}")
            # self.corredores = [c for c in self.corredores if c.id != id]
            # self.corredores_actualizados.emit(self.corredores)
            logger.info("✅ Corredor eliminado exitosamente")
            return True
        except ErrorAPI as e:
            mensaje = f"Error al eliminar corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        except Exception as e:
            mensaje = f"Error inesperado al eliminar corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        return False

    def buscar_corredor(self, id: str) -> Optional[Corredor]:
        """
        Busca un corredor por su ID
        
        Args:
            id: ID del corredor a buscar
            
        Returns:
            Corredor: El corredor encontrado o None
        """
        return next((c for c in self.corredores if c.id == id), None)

    def filtrar_corredores(self, texto: str) -> List[Corredor]:
        """
        Filtra la lista de corredores por texto
        
        Args:
            texto: Texto a buscar
            
        Returns:
            List[Corredor]: Lista de corredores que coinciden
        """
        texto = texto.lower()
        return [
            c for c in self.corredores
            if texto in c.nombre.lower() or 
               texto in c.email.lower() or 
               texto in c.rut.lower()
        ]
