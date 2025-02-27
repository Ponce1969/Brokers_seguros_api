"""
ViewModel para la gestión de corredores usando QNetworkAccessManager
"""

from typing import List, Optional
import logging
from PyQt6.QtCore import QObject, pyqtSignal

from ..models.corredor import Corredor
from ..core.excepciones import ErrorAPI
from .corredor_itemmodel import CorredorItemModel
from ..services.network_manager import NetworkManager

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
        self.item_model = CorredorItemModel()
        
        # Inicializar NetworkManager
        self.api = NetworkManager("http://localhost:8000")
        self.api.response_received.connect(self._handle_response)
        self.api.error_occurred.connect(self._handle_error)
        
        # Variable para rastrear la operación actual
        self._current_operation = None

    def _handle_error(self, error_msg: str):
        """Maneja los errores del NetworkManager"""
        logger.error(f"Error en la operación {self._current_operation}: {error_msg}")
        self.error_ocurrido.emit(error_msg)

    def _handle_response(self, response):
        """Maneja las respuestas del servidor según la operación actual"""
        try:
            if self._current_operation == "cargar":
                if isinstance(response, list):
                    self._procesar_lista_corredores(response)
                else:
                    logger.error("Respuesta inesperada al cargar corredores")
                    self.error_ocurrido.emit("Formato de respuesta inválido")
            elif self._current_operation == "crear":
                if isinstance(response, dict):
                    self._procesar_corredor_creado(response)
                else:
                    self.error_ocurrido.emit("Respuesta inválida al crear corredor")
            elif self._current_operation == "actualizar":
                if isinstance(response, dict):
                    self._procesar_corredor_actualizado(response)
                else:
                    self.error_ocurrido.emit("Respuesta inválida al actualizar corredor")
            elif self._current_operation == "eliminar":
                self._procesar_corredor_eliminado()
        except Exception as e:
            logger.error(f"Error procesando respuesta: {e}")
            self.error_ocurrido.emit(str(e))
        finally:
            self._current_operation = None

    def _procesar_lista_corredores(self, response: List[dict]) -> None:
        """Procesa la lista de corredores recibida del servidor"""
        try:
            self.corredores = []
            for corredor_data in response:
                try:
                    corredor = Corredor.from_dict(corredor_data)
                    self.corredores.append(corredor)
                except Exception as e:
                    logger.error(f"Error al procesar corredor: {e}")
            
            self.corredores_actualizados.emit(self.corredores)
            logger.info(f"✅ {len(self.corredores)} corredores cargados")
        except Exception as e:
            logger.error(f"Error procesando lista de corredores: {e}")
            self.error_ocurrido.emit(f"Error al procesar los datos: {str(e)}")

    def cargar_corredores(self) -> None:
        """Carga la lista de corredores desde el servidor"""
        try:
            logger.info("📥 Cargando lista de corredores...")
            self._current_operation = "cargar"
            self.api.get("api/v1/corredores")
        except Exception as e:
            logger.error(f"Error al iniciar carga de corredores: {e}")
            self.error_ocurrido.emit(str(e))

    def crear_corredor(self, datos: dict) -> None:
        """
        Crea un nuevo corredor

        Args:
            datos: Diccionario con los datos del corredor
        """
        try:
            # Validar datos requeridos
            campos_requeridos = ["numero", "nombres", "apellidos", "mail"]
            for campo in campos_requeridos:
                if not datos.get(campo):
                    raise ValueError(f"El campo {campo} es requerido")

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

            self._current_operation = "crear"
            self.api.post("api/v1/corredores", datos_api)

        except Exception as e:
            mensaje = f"Error al crear corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)

    def _procesar_corredor_creado(self, response: dict) -> None:
        """Procesa la respuesta después de crear un corredor"""
        try:
            corredor = Corredor.from_dict(response)
            self.corredores.append(corredor)
            self.item_model.addCorredor(corredor)
            self.corredor_actualizado.emit(corredor)
            self.corredores_actualizados.emit(self.corredores)
            mensaje_exito = f"Corredor {corredor.numero} creado exitosamente"
            self.error_ocurrido.emit(mensaje_exito)
        except Exception as e:
            logger.error(f"Error procesando corredor creado: {e}")
            self.error_ocurrido.emit(str(e))

    def actualizar_corredor(self, id: int, datos: dict) -> None:
        """
        Actualiza un corredor existente

        Args:
            id: ID del corredor a actualizar
            datos: Diccionario con los datos a actualizar
        """
        try:
            logger.info(f"📝 Actualizando corredor {id}...")
            self._current_operation = "actualizar"
            self.api.put(f"api/v1/corredores/{id}", datos)
        except Exception as e:
            mensaje = f"Error al actualizar corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)

    def _procesar_corredor_actualizado(self, response: dict) -> None:
        """Procesa la respuesta después de actualizar un corredor"""
        try:
            corredor = Corredor.from_dict(response)
            # Actualizar la lista local
            for i, c in enumerate(self.corredores):
                if c.id == corredor.id:
                    self.corredores[i] = corredor
                    break
            self.corredor_actualizado.emit(corredor)
            self.corredores_actualizados.emit(self.corredores)
            logger.info("✅ Corredor actualizado exitosamente")
        except Exception as e:
            logger.error(f"Error procesando corredor actualizado: {e}")
            self.error_ocurrido.emit(str(e))

    def eliminar_corredor(self, id: int) -> None:
        """
        Elimina un corredor

        Args:
            id: ID del corredor a eliminar
        """
        try:
            logger.info(f"🗑️ Eliminando corredor {id}...")
            self._current_operation = "eliminar"
            self._corredor_a_eliminar = id
            self.api.delete(f"api/v1/corredores/{id}")
        except Exception as e:
            mensaje = f"Error al eliminar corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)

    def _procesar_corredor_eliminado(self) -> None:
        """Procesa la respuesta después de eliminar un corredor"""
        try:
            if hasattr(self, '_corredor_a_eliminar'):
                self.corredores = [c for c in self.corredores if c.id != self._corredor_a_eliminar]
                self.corredores_actualizados.emit(self.corredores)
                logger.info("✅ Corredor eliminado exitosamente")
                delattr(self, '_corredor_a_eliminar')
        except Exception as e:
            logger.error(f"Error procesando eliminación de corredor: {e}")
            self.error_ocurrido.emit(str(e))

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
