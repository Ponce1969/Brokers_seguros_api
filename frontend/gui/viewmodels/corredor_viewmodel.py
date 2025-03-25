"""
ViewModel para la gestión de corredores usando QNetworkAccessManager
"""

from typing import List, Optional
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import date

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

    def __init__(self, network_manager=None):
        """
        Inicializa el ViewModel de corredores
        
        Args:
            network_manager: Instancia del NetworkManager (opcional)
        """
        super().__init__()
        self.corredores: List[Corredor] = []
        self.corredor_actual: Optional[Corredor] = None
        self.item_model = CorredorItemModel()
        
        # Inicializar NetworkManager
        from ..core.di_container import contenedor
        from ..services.network_manager import NetworkManager
        self.api = network_manager if network_manager is not None else contenedor.resolver(NetworkManager)
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
            
            self.item_model.updateCorredores(self.corredores)
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
            self.api.get("api/v1/corredores/")
        except Exception as e:
            logger.error(f"Error al iniciar carga de corredores: {e}")
            self.error_ocurrido.emit(str(e))

    def crear_corredor(self, datos: dict) -> None:
        """
        Crea un nuevo corredor con los campos simplificados

        Args:
            datos: Diccionario con los datos del corredor
        """
        try:
            # Validar datos requeridos
            campos_requeridos = ["numero", "nombre", "email", "direccion"]
            for campo in campos_requeridos:
                if not datos.get(campo):
                    raise ValueError(f"El campo {campo} es requerido")
                    
            # Validar que el correo tenga formato correcto
            if "@" not in datos.get("email", ""):
                raise ValueError("El correo electrónico debe tener un formato válido")
                
            # Asegurar que la contraseña esté presente para nuevos corredores
            if not datos.get("password"):
                raise ValueError("La contraseña es requerida para nuevos corredores")

            # Adaptar los datos al formato esperado por la API
            datos_api = {
                "numero": int(datos.get("numero")),  # Asegurar que sea entero
                "nombre": datos.get("nombre"),  # Campo único para nombre completo
                "direccion": datos.get("direccion", ""),
                "telefono": datos.get("telefono", ""),  # Teléfono único
                "mail": datos.get("email"),  # Mapear 'email' del frontend a 'mail' para la API
                "password": datos.get("password"),  # Nueva contraseña
                "rol": datos.get("rol", "corredor"),  # Rol (corredor o admin)
                "activo": datos.get("activo", True),  # Estado activo/inactivo
                "fecha_alta": date.today().isoformat()  # Fecha de alta automática
            }

            self._current_operation = "crear"
            self.api.post("api/v1/corredores/", datos_api)

        except Exception as e:
            mensaje = f"Error al crear corredor: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)

    def _procesar_corredor_creado(self, response: dict) -> None:
        """Procesa la respuesta después de crear un corredor"""
        try:
            corredor = Corredor.from_dict(response)
            # Agregamos el corredor a la lista
            self.corredores.append(corredor)
            
            # Actualizamos el modelo completo para asegurar consistencia
            # en lugar de agregar solo el nuevo corredor
            self.item_model.updateCorredores(self.corredores)
            
            # Notificamos que se actualizó el corredor
            self.corredor_actualizado.emit(corredor)
            
            # Notificamos que se actualizó la lista completa
            self.corredores_actualizados.emit(self.corredores)
            
            logger.info(f"✅ Corredor {corredor.numero} creado exitosamente")
        except Exception as e:
            logger.error(f"Error procesando corredor creado: {e}")
            self.error_ocurrido.emit(str(e))

    def actualizar_corredor(self, id: int, datos: dict) -> None:
        """
        Actualiza un corredor existente con los campos simplificados

        Args:
            id: ID del corredor a actualizar
            datos: Diccionario con los datos a actualizar
        """
        try:
            logger.info(f"📝 Actualizando corredor {id}...")
            self._current_operation = "actualizar"
            
            # Validar campos requeridos para actualización
            campos_requeridos = ["numero", "nombre", "email", "direccion"]
            for campo in campos_requeridos:
                if campo in datos and not datos.get(campo):
                    raise ValueError(f"El campo {campo} es requerido")
                    
            # Validar que el correo tenga formato correcto si está presente
            if "email" in datos and "@" not in datos.get("email", ""):
                raise ValueError("El correo electrónico debe tener un formato válido")
            
            # Mapear los nombres de campos del frontend a los campos de la API
            datos_api = {}
            
            # Mapeo de campos frontend -> API
            mapping = {
                "numero": "numero",
                "nombre": "nombre",
                "email": "mail",
                "telefono": "telefono",
                "direccion": "direccion",
                "password": "password",
                "rol": "rol",
                "activo": "activo"
            }
            
            # Construir el diccionario de datos para la API
            for campo_frontend, campo_api in mapping.items():
                if campo_frontend in datos and datos[campo_frontend] is not None:
                    datos_api[campo_api] = datos[campo_frontend]
            
            self.api.put(f"api/v1/corredores/{id}", datos_api)
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
            self.item_model.updateCorredores(self.corredores)
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
                self.item_model.updateCorredores(self.corredores)
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
        corredores_filtrados = [
            c for c in self.corredores
            if texto in str(c.numero).lower()
            or texto in c.nombre.lower()
            or texto in c.email.lower()
            or texto in (c.telefono or "").lower()
            or texto in (c.direccion or "").lower()
        ]
        self.item_model.updateCorredores(corredores_filtrados)
        return corredores_filtrados
