"""
ViewModel para la gestión de corredores
"""

from typing import List, Optional
import logging
from PyQt6.QtCore import QObject, pyqtSignal

from ..models.corredor import Corredor
from ..core.excepciones import ErrorAPI
from .corredor_itemmodel import CorredorItemModel
from ..services.api_service import ServicioAPI
from ..core.di_container import contenedor

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
        self.api: ServicioAPI = contenedor.resolver(ServicioAPI)
        self.item_model = CorredorItemModel()

    async def cargar_corredores(self) -> None:
        """
        Carga la lista de corredores desde el servidor
        """
        try:
            if not self.api:
                raise ValueError("API service no inicializado")

            logger.info("📥 Cargando lista de corredores...")
            response = await self.api.get("api/v1/corredores/")
            if not response:
                logger.warning("⚠️ No se recibieron datos de corredores")
                self.corredores = []
                self.corredores_actualizados.emit(self.corredores)
                return

            # Procesar la respuesta
            if isinstance(response, list):
                self.corredores = []
                for corredor_data in response:
                    try:
                        corredor = Corredor.from_dict(corredor_data)
                        self.corredores.append(corredor)
                    except Exception as e:
                        logger.error(f"Error al crear corredor: {str(e)}")
            else:
                self.corredores = []

            self.corredores_actualizados.emit(self.corredores)
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
            if not self.api:
                raise ErrorAPI("Servicio API no inicializado")

            # Validar datos requeridos
            campos_requeridos = ["numero", "nombres", "apellidos", "mail"]
            for campo in campos_requeridos:
                if not datos.get(campo):
                    raise ErrorAPI(f"El campo {campo} es requerido")

            # Adaptar los datos al formato esperado por la API
            datos_api = {
                "numero": datos.get("numero"),
                "nombres": datos.get("nombres", ""),
                "apellidos": datos.get("apellidos", ""),
                "documento": datos.get("documento", ""),
                "mail": datos.get("mail"),
                "matricula": datos.get("matricula", ""),
                "direccion": datos.get("direccion"),
                "localidad": datos.get("localidad"),
                "telefonos": datos.get("telefonos"),
                "movil": datos.get("movil"),
                "observaciones": datos.get("observaciones"),
                "especializacion": datos.get("especializacion"),
                "fecha_alta": datos.get("fecha_alta"),
                "fecha_baja": datos.get("fecha_baja"),
                "activo": datos.get("activo", True),
            }

            response = await self.api.post("api/v1/corredores", datos_api)

            if not response or not isinstance(response, dict):
                raise ErrorAPI("Respuesta inválida del servidor")

            corredor = Corredor.from_dict(response)
            self.corredores.append(corredor)
            self.item_model.addCorredor(corredor)
            self.corredor_actualizado.emit(corredor)
            self.corredores_actualizados.emit(self.corredores)

            mensaje_exito = f"Corredor {corredor.numero} creado exitosamente"
            self.error_ocurrido.emit(mensaje_exito)
            return corredor

        except ErrorAPI as e:
            mensaje = f"Error al crear corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        except Exception as e:
            mensaje = f"Error inesperado al crear corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            logger.exception("Detalles del error:")
            self.error_ocurrido.emit(mensaje)
        return None

    async def actualizar_corredor(self, id: int, datos: dict) -> Optional[Corredor]:
        """
        Actualiza un corredor existente

        Args:
            id: ID del corredor a actualizar
            datos: Diccionario con los datos a actualizar

        Returns:
            Corredor actualizado o None si ocurrió un error
        """
        try:
            logger.info(f"📝 Actualizando corredor {id}...")
            respuesta = await self.api.put(f"api/v1/corredores/{id}", datos)
            corredor = Corredor.from_dict(respuesta)
            self.corredor_actualizado.emit(corredor)
            logger.info("✅ Corredor actualizado exitosamente")
            return corredor
        except ErrorAPI as e:
            mensaje = f"Error al actualizar corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        except Exception as e:
            mensaje = f"Error inesperado al actualizar corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)
        return None

    async def eliminar_corredor(self, id: int) -> bool:
        """
        Elimina un corredor

        Args:
            id: ID del corredor a eliminar

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            logger.info(f"🗑️ Eliminando corredor {id}...")
            await self.api.delete(f"api/v1/corredores/{id}")
            self.corredores = [c for c in self.corredores if c.id != id]
            self.corredores_actualizados.emit(self.corredores)
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

    def buscar_corredor(self, id: int) -> Optional[Corredor]:
        """
        Busca un corredor por su ID en la lista de corredores cargados

        Args:
            id: ID del corredor a buscar

        Returns:
            Corredor o None si no se encuentra
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
        texto = texto.lower().strip()
        return [
            c
            for c in self.corredores
            if texto in f"{c.nombres} {c.apellidos}".lower()
            or texto in c.mail.lower()
            or texto in c.documento.lower()
            or texto in str(c.numero)
            or (c.telefonos and texto in c.telefonos.lower())
            or (c.movil and texto in c.movil.lower())
            or (c.matricula and texto in c.matricula.lower())
        ]
