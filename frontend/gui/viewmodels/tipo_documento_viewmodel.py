"""ViewModel para la gestión de tipos de documentos"""

from typing import List, Optional, Dict, Any
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import datetime

from ..models.tipo_documento import TipoDocumento
from ..services.network_manager import NetworkManager

# Configurar logging
logger = logging.getLogger(__name__)


class TipoDocumentoViewModel(QObject):
    """
    ViewModel para manejar la lógica de negocio relacionada con tipos de documentos
    """

    # Señales
    tipos_actualizados = pyqtSignal(list)  # Lista de tipos de documentos actualizada
    tipo_creado = pyqtSignal(TipoDocumento)  # Nuevo tipo creado
    tipo_actualizado = pyqtSignal(TipoDocumento)  # Tipo actualizado
    error_ocurrido = pyqtSignal(str)  # Error en operación

    def __init__(self, network_manager=None):
        """
        Inicializa el ViewModel de tipos de documentos
        
        Args:
            network_manager: Instancia del NetworkManager (opcional)
        """
        super().__init__()
        self.tipos_documento: List[TipoDocumento] = []
        self.tipos_por_id: Dict[int, TipoDocumento] = {}  # Cache por ID
        self.tipos_por_codigo: Dict[str, TipoDocumento] = {}  # Cache por código
        
        # Inicializar NetworkManager
        if network_manager is None:
            try:
                from ..core.di_container import contenedor
                self.api = contenedor.resolver(NetworkManager)
            except:
                self.api = NetworkManager()
        else:
            self.api = network_manager
            
        # Conectar seu00f1ales del NetworkManager
        self.api.response_received.connect(self._handle_response)
        self.api.error_occurred.connect(self._handle_error)
        
        # Variable para rastrear la operaciu00f3n actual
        self._current_operation = None
        
        # Indicador de si los tipos ya fueron cargados
        self._tipos_cargados = False

    def _handle_response(self, data: Any):
        """Maneja las respuestas del servidor"""
        operation = self._current_operation
        logger.debug(f"Respuesta recibida para operación: {operation}")
        
        try:
            if operation == "get_tipos":
                self._procesar_tipos_documento(data)
            elif operation == "create_tipo":
                self._procesar_tipo_creado(data)
            elif operation == "update_tipo":
                self._procesar_tipo_actualizado(data)
            else:
                logger.warning(f"Operación no manejada: {operation}")
        except Exception as e:
            logger.error(f"Error procesando respuesta para {operation}: {e}")
            self.error_ocurrido.emit(f"Error procesando respuesta: {str(e)}")
        finally:
            self._current_operation = None

    def _handle_error(self, error_msg: str):
        """Maneja los errores de red"""
        operation = self._current_operation
        logger.error(f"Error en operación {operation}: {error_msg}")
        
        # Emitir señal de error
        self.error_ocurrido.emit(f"Error en operación {operation}: {error_msg}")
        
        # Resetear operación actual
        self._current_operation = None

    def _procesar_tipos_documento(self, data):
        """Procesa la lista de tipos de documento recibida del servidor"""
        if not isinstance(data, list):
            logger.error(f"Datos inesperados al cargar tipos de documento: {type(data)}")
            return
            
        logger.info(f"Procesando {len(data)} tipos de documento")
        
        # Limpiar listas y cachés existentes
        self.tipos_documento.clear()
        self.tipos_por_id.clear()
        self.tipos_por_codigo.clear()
        
        # Procesar cada tipo
        for tipo_data in data:
            try:
                tipo = TipoDocumento.from_dict(tipo_data)
                self.tipos_documento.append(tipo)
                self.tipos_por_id[tipo.id] = tipo
                self.tipos_por_codigo[tipo.codigo] = tipo
            except Exception as e:
                logger.error(f"Error procesando tipo de documento: {e}")
        
        # Marcar como cargados
        self._tipos_cargados = True
        
        # Notificar actualización
        logger.info(f"Emitiendo señal con {len(self.tipos_documento)} tipos de documento")
        self.tipos_actualizados.emit(self.tipos_documento)

    def _procesar_tipo_creado(self, data):
        """Procesa un nuevo tipo de documento creado"""
        if not isinstance(data, dict):
            logger.error(f"Datos inesperados al crear tipo de documento: {type(data)}")
            return
            
        try:
            nuevo_tipo = TipoDocumento.from_dict(data)
            
            # Actualizar cachés
            self.tipos_documento.append(nuevo_tipo)
            self.tipos_por_id[nuevo_tipo.id] = nuevo_tipo
            self.tipos_por_codigo[nuevo_tipo.codigo] = nuevo_tipo
            
            # Notificar creación
            self.tipo_creado.emit(nuevo_tipo)
            self.tipos_actualizados.emit(self.tipos_documento)
            
            logger.info(f"Tipo de documento creado: {nuevo_tipo.nombre} (ID: {nuevo_tipo.id})")
        except Exception as e:
            logger.error(f"Error procesando tipo de documento creado: {e}")

    def _procesar_tipo_actualizado(self, data):
        """Procesa un tipo de documento actualizado"""
        if not isinstance(data, dict):
            logger.error(f"Datos inesperados al actualizar tipo de documento: {type(data)}")
            return
            
        try:
            tipo_actualizado = TipoDocumento.from_dict(data)
            
            # Buscar y actualizar en la lista y cachés
            for i, tipo in enumerate(self.tipos_documento):
                if tipo.id == tipo_actualizado.id:
                    self.tipos_documento[i] = tipo_actualizado
                    break
            
            self.tipos_por_id[tipo_actualizado.id] = tipo_actualizado
            self.tipos_por_codigo[tipo_actualizado.codigo] = tipo_actualizado
            
            # Notificar actualización
            self.tipo_actualizado.emit(tipo_actualizado)
            self.tipos_actualizados.emit(self.tipos_documento)
            
            logger.info(f"Tipo de documento actualizado: {tipo_actualizado.nombre} (ID: {tipo_actualizado.id})")
        except Exception as e:
            logger.error(f"Error procesando tipo de documento actualizado: {e}")

    # --- Métodos Públicos --- #

    def cargar_tipos_documento(self, forzar=False):
        """Carga todos los tipos de documento desde el servidor"""
        if self._tipos_cargados and not forzar:
            logger.info("Tipos de documento ya cargados, emitiendo desde caché")
            self.tipos_actualizados.emit(self.tipos_documento)
            return
            
        logger.info("Solicitando lista de tipos de documento")
        self._current_operation = "get_tipos"
        self.api.get("api/v1/tipos-documento/")

    def crear_tipo_documento(self, nombre: str, codigo: str, descripcion: str = "", es_default: bool = False):
        """Crea un nuevo tipo de documento"""
        logger.info(f"Creando tipo de documento: {nombre} ({codigo})")
        
        datos = {
            "nombre": nombre,
            "codigo": codigo,
            "descripcion": descripcion,
            "es_default": es_default,
            "esta_activo": True
        }
        
        self._current_operation = "create_tipo"
        self.api.post("api/v1/tipos-documento/", datos)

    def actualizar_tipo_documento(self, id: int, datos: dict):
        """Actualiza un tipo de documento existente"""
        logger.info(f"Actualizando tipo de documento ID: {id}")
        
        self._current_operation = "update_tipo"
        self.api.put(f"api/v1/tipos-documento/{id}", datos)

    def obtener_tipo_por_id(self, id: int) -> Optional[TipoDocumento]:
        """Obtiene un tipo de documento por su ID"""
        return self.tipos_por_id.get(id)

    def obtener_tipo_por_codigo(self, codigo: str) -> Optional[TipoDocumento]:
        """Obtiene un tipo de documento por su código"""
        return self.tipos_por_codigo.get(codigo)

    def existe_tipo_con_codigo(self, codigo: str) -> bool:
        """Verifica si existe un tipo de documento con el código especificado"""
        return codigo in self.tipos_por_codigo

    def obtener_tipos_activos(self) -> List[TipoDocumento]:
        """Obtiene solo los tipos de documento activos"""
        return [tipo for tipo in self.tipos_documento if tipo.esta_activo]

    def obtener_tipo_default(self) -> Optional[TipoDocumento]:
        """Obtiene el tipo de documento marcado como predeterminado"""
        for tipo in self.tipos_documento:
            if tipo.es_default and tipo.esta_activo:
                return tipo
        
        # Si no hay predeterminado, retornar el primero activo o None
        activos = self.obtener_tipos_activos()
        return activos[0] if activos else None
