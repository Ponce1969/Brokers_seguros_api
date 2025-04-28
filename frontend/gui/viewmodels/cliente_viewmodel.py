"""ViewModel para la gestión de clientes usando QNetworkAccessManager"""

from typing import List, Optional
from datetime import date
import logging

from PyQt6.QtCore import QObject, pyqtSignal

from ..models.cliente import Cliente
from .cliente_itemmodel import ClienteItemModel
from .cliente.cliente_network_handler import ClienteNetworkHandler

# Configurar logging
logger = logging.getLogger(__name__)


class ClienteViewModel(QObject):
    """ViewModel para manejar la lógica de negocio relacionada con clientes"""

    # Definir señales
    cliente_actualizado = pyqtSignal(Cliente)
    clientes_actualizados = pyqtSignal(list)
    error_ocurrido = pyqtSignal(str)

    def __init__(self, network_manager=None):
        """
        Inicializa el ViewModel de clientes
        
        Args:
            network_manager: Instancia del NetworkManager (opcional)
        """
        super().__init__()
        self.clientes: List[Cliente] = []
        self.cliente_actual: Optional[Cliente] = None
        self.item_model = ClienteItemModel()
        
        # Variable para rastrear la operación actual
        self._current_operation = None
        
        # Inicializar NetworkManager con manejo robusto de errores
        try:
            if network_manager is not None:
                self.api = network_manager
                logger.info("Usando NetworkManager proporcionado")
            else:
                from ..core.di_container import contenedor
                from ..services.network_manager import NetworkManager
                self.api = contenedor.resolver(NetworkManager)
                logger.info("NetworkManager obtenido del contenedor")
                
            # Verificación de validez del API
            if self.api is None:
                logger.error("NetworkManager no válido o no disponible")
                raise ValueError("NetworkManager no disponible")
                
            # Conectar señales del NetworkManager
            self.api.response_received.connect(self._handle_response)
            self.api.error_occurred.connect(self._handle_error)
            logger.info("Señales del NetworkManager conectadas exitosamente")
                
        except Exception as e:
            logger.error(f"Error al inicializar NetworkManager: {e}")
            self.api = None
        
        # Inicializar manejador de red para clientes con manejo más robusto
        try:
            self.cliente_handler = ClienteNetworkHandler(self.api)
            logger.info("ClienteNetworkHandler inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar ClienteNetworkHandler: {e}")
            # Crearlo de todos modos para evitar errores de atributo, pero marcar como no funcional
            self.cliente_handler = ClienteNetworkHandler(None)
            self._api_disponible = False
        else:
            self._api_disponible = (self.api is not None)

    def _handle_error(self, error_msg: str):
        """Maneja los errores del NetworkManager"""
        logger.error(f"Error en la operación {self._current_operation}: {error_msg}")
        self.error_ocurrido.emit(error_msg)

    def _handle_response(self, response):
        """Maneja las respuestas del servidor según la operación actual"""
        # Si no hay operación actual, ignorar la respuesta (puede ser de otra inicialización)
        if self._current_operation is None:
            logger.debug("Respuesta recibida sin operación activa, ignorando")
            return
            
        try:
            # Verificar si es una respuesta válida
            if response is None:
                logger.error("Respuesta nula recibida")
                self.error_ocurrido.emit("El servidor no devolvio datos válidos")
                return
                
            # Log detallado para ayudar en la depuración
            logger.debug(f"Respuesta recibida para operación '{self._current_operation}': {type(response)}")
                
            if self._current_operation == "cargar":
                if isinstance(response, list):
                    self._procesar_lista_clientes(response)
                elif isinstance(response, dict) and 'results' in response:
                    # Manejar respuesta paginada donde los resultados están en 'results'
                    self._procesar_lista_clientes(response['results'])
                else:
                    logger.error(f"Respuesta inesperada al cargar clientes: {type(response)}")
                    self.error_ocurrido.emit("Formato de respuesta inválido")
            elif self._current_operation == "crear":
                if isinstance(response, dict):
                    self._procesar_cliente_creado(response)
                else:
                    logger.error(f"Respuesta inválida al crear cliente: {type(response)}")
                    self.error_ocurrido.emit("Respuesta inválida al crear cliente")
            elif self._current_operation == "actualizar":
                if isinstance(response, dict):
                    self._procesar_cliente_actualizado(response)
                else:
                    logger.error(f"Respuesta inválida al actualizar cliente: {type(response)}")
                    self.error_ocurrido.emit("Respuesta inválida al actualizar cliente")
            elif self._current_operation == "eliminar":
                # La respuesta puede ser vacía (204 No Content)
                self._procesar_cliente_eliminado()
            elif self._current_operation == "obtener":
                if isinstance(response, dict):
                    cliente = Cliente.from_dict(response)
                    self.cliente_actual = cliente
                    self.cliente_actualizado.emit(cliente)
                else:
                    logger.error(f"Respuesta inválida al obtener cliente: {type(response)}")
                    self.error_ocurrido.emit("Respuesta inválida al obtener cliente")
            else:
                logger.warning(f"Operación no reconocida: {self._current_operation}")
        except Exception as e:
            import traceback
            logger.error(f"Error procesando respuesta: {e}")
            logger.debug(traceback.format_exc())
            self.error_ocurrido.emit(f"Error al procesar datos: {str(e)}")
        finally:
            self._current_operation = None

    def _procesar_lista_clientes(self, response: List[dict]) -> None:
        """Procesa la lista de clientes recibida del servidor"""
        try:
            self.clientes = []
            clientes_validos = 0
            clientes_filtrados = 0
            
            for cliente_data in response:
                try:
                    # Criterio para distinguir clientes de corredores
                    es_cliente_valido = True
                    
                    # Imprimir datos del registro para diagnóstico
                    logger.debug(f"Procesando registro: {cliente_data}")
                    
                    # 1. Verificamos si tiene al menos un identificador
                    if 'id' not in cliente_data or not cliente_data.get('id'):
                        # Si no tiene ID, no podemos procesarlo correctamente
                        es_cliente_valido = False
                        logger.debug(f"Registro filtrado por falta de id: {cliente_data}")
                        
                    # 2. IMPORTANTE: Detectar corredores usando mu00faltiples indicadores
                    # Por cada indicador de corredor, registrar el motivo específico
                    
                    # 2.1 Verificar por campos específicos de corredores
                    if 'numero_corredor' in cliente_data:
                        es_cliente_valido = False
                        logger.debug(f"Registro {cliente_data.get('id')} filtrado: tiene campo 'numero_corredor'")
                        
                    if 'comision' in cliente_data:
                        es_cliente_valido = False
                        logger.debug(f"Registro {cliente_data.get('id')} filtrado: tiene campo 'comision'")
                        
                    # 2.2 Verificar por tipo de entidad si existe en la respuesta
                    if 'tipo_entidad' in cliente_data and cliente_data.get('tipo_entidad') == 'corredor':
                        es_cliente_valido = False
                        logger.debug(f"Registro {cliente_data.get('id')} filtrado: tipo_entidad = 'corredor'")
                        
                    # 2.3 Un corredor no debería tener estos campos específicos del cliente
                    claves_cliente = ['tipo_documento_id', 'fecha_nacimiento']
                    if all(clave not in cliente_data for clave in claves_cliente):
                        es_cliente_valido = False
                        logger.debug(f"Registro {cliente_data.get('id')} filtrado: no tiene campos clave de cliente")
                    
                    # 3. Los clientes deben tener un campo tipo_documento_id
                    if not es_cliente_valido:
                        # Ya está marcado como inválido, no seguir comprobando
                        pass
                    elif 'tipo_documento_id' not in cliente_data or not cliente_data.get('tipo_documento_id'):
                        # Si es cliente, debe tener tipo_documento_id
                        cliente_data['tipo_documento_id'] = 1  # Valor predeterminado (CI)
                        logger.debug(f"Asignando tipo_documento_id predeterminado al cliente: {cliente_data.get('id')}")
                    
                    # Verificar que tenga al menos datos mínimos para mostrar
                    # Intentamos autocompletar datos faltantes cuando sea posible
                    if 'nombres' not in cliente_data or not cliente_data.get('nombres'):
                        if 'nombre' in cliente_data and cliente_data.get('nombre'):
                            # Puede que esté usando el campo 'nombre' completo (frontend vs backend)
                            nombres_partes = cliente_data['nombre'].split(' ', 1)
                            cliente_data['nombres'] = nombres_partes[0]
                            if len(nombres_partes) > 1:
                                cliente_data['apellidos'] = nombres_partes[1]
                        else:
                            cliente_data['nombres'] = "Sin nombre"
                    
                    if 'apellidos' not in cliente_data or not cliente_data.get('apellidos'):
                        cliente_data['apellidos'] = ""
                    
                    if 'mail' not in cliente_data or not cliente_data.get('mail'):
                        if 'email' in cliente_data:
                            cliente_data['mail'] = cliente_data['email']
                        else:
                            cliente_data['mail'] = ""
                    
                    if 'numero_documento' not in cliente_data or not cliente_data.get('numero_documento'):
                        if 'documento' in cliente_data:
                            cliente_data['numero_documento'] = cliente_data['documento']
                        else:
                            cliente_data['numero_documento'] = "Sin documento"
                    
                    # Sólo filtrar si no tiene id (mínimo necesario)
                    if es_cliente_valido:
                        cliente = Cliente.from_dict(cliente_data)
                        self.clientes.append(cliente)
                        clientes_validos += 1
                    else:
                        clientes_filtrados += 1
                except Exception as e:
                    logger.error(f"Error procesando cliente {cliente_data.get('id')}: {e}")
            
            # Verificar si tenemos clientes válidos
            if not self.clientes:
                logger.warning("No se encontraron clientes válidos después del filtrado")
                # Asegurar que no hay datos antiguos en la vista
                self.item_model.updateClientes([])
                self.clientes_actualizados.emit([])
            else:
                # Actualizar el modelo de datos para la vista
                self.item_model.updateClientes(self.clientes)
                
                # Notificar que se actualizaron los clientes
                self.clientes_actualizados.emit(self.clientes)
            
            logger.info(f"{clientes_validos} clientes cargados exitosamente. {clientes_filtrados} registros filtrados.")
            # Mostrar IDs de los clientes que pasaron el filtro para depuración
            if self.clientes:
                ids_clientes = [cliente.id for cliente in self.clientes]
                logger.debug(f"IDs de clientes válidos: {ids_clientes}")
            logger.debug(f"Datos completos recibidos: {response}")
        except Exception as e:
            logger.error(f"Error procesando lista de clientes: {e}")
            self.error_ocurrido.emit(f"Error al procesar clientes: {str(e)}")

    def cargar_clientes(self):
        """Carga la lista de clientes desde el servidor"""
        # Verificar disponibilidad de API antes de intentar operaciones de red
        if not getattr(self, '_api_disponible', False):
            logger.warning("No se pueden cargar clientes: API no disponible")
            self.error_ocurrido.emit("Servidor no disponible. Compruebe su conexión.")
            return
            
        try:
            # IMPORTANTE: Limpiar cualquier operación en progreso para evitar elimaciones automáticas
            self._current_operation = None
            
            # Limpiar lista de clientes antes de cargar nueva
            self.clientes = []
            self.item_model.updateClientes([])
            
            logger.info("Cargando clientes...")
            self._current_operation = "cargar"
            self.cliente_handler.listar_clientes()
            logger.debug("Solicitando datos al endpoint de clientes")
        except Exception as e:
            logger.error(f"Error al cargar clientes: {e}")
            self.error_ocurrido.emit(str(e))
            self._current_operation = None
    
    def cargar_clientes_por_corredor(self, corredor_id: int):
        """Carga la lista de clientes asociados a un corredor"""
        try:
            logger.info(f"Cargando clientes del corredor {corredor_id}...")
            self._current_operation = "cargar"
            self.cliente_handler.listar_clientes_por_corredor(corredor_id)
        except Exception as e:
            logger.error(f"Error al cargar clientes del corredor: {e}")
            self.error_ocurrido.emit(str(e))
            self._current_operation = None

    def crear_cliente(self, datos: dict):
        """
        Crea un nuevo cliente con los campos requeridos
        
        Args:
            datos: Diccionario con los datos del cliente
        """
        try:
            logger.info(f"Creando cliente: {datos.get('nombres')} {datos.get('apellidos')}")
            
            # Validar datos requeridos
            valido, mensaje = self.cliente_handler.validar_datos_cliente(datos)
            if not valido:
                raise ValueError(mensaje)
            
            # Asignar operación actual
            self._current_operation = "crear"
            
            # Enviar solicitud al servidor
            self.cliente_handler.crear_cliente(datos)
        except Exception as e:
            logger.error(f"Error al crear cliente: {e}")
            self.error_ocurrido.emit(str(e))
            self._current_operation = None

    def _procesar_cliente_creado(self, response: dict) -> None:
        """Procesa la respuesta después de crear un cliente"""
        try:
            # Crear un cliente desde la respuesta del backend
            cliente = Cliente.from_dict(response)
            
            # Agregar el nuevo cliente a la lista
            self.clientes.append(cliente)
            
            # Actualizar el modelo completo con la lista actual
            self.item_model.updateClientes(self.clientes)
            
            # Notificar que se actualizó el cliente
            self.cliente_actualizado.emit(cliente)
            
            # Notificar que se actualizó la lista completa
            self.clientes_actualizados.emit(self.clientes)
            
            logger.info(f"Cliente {cliente.nombre_completo} creado exitosamente")
        except Exception as e:
            logger.error(f"Error procesando cliente creado: {e}")
            self.error_ocurrido.emit(str(e))

    def actualizar_cliente(self, id: str, datos: dict):
        """
        Actualiza un cliente existente con los campos actualizados
        
        Args:
            id: ID del cliente a actualizar
            datos: Diccionario con los datos a actualizar
        """
        try:
            # Verificar disponibilidad de API
            if not getattr(self, '_api_disponible', False):
                raise ValueError("Servidor no disponible. Compruebe su conexión.")
            
            # Validar que el ID tenga formato UUID
            import re
            uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
            if not uuid_pattern.match(str(id)):
                mensaje = f"ID {id} no tiene formato UUID válido. No se puede actualizar."
                logger.error(mensaje)
                raise ValueError(mensaje)
                
            logger.info(f"Actualizando cliente con ID {id}...")
            
            # Validar que hay campos para actualizar
            if not datos:
                raise ValueError("No hay datos para actualizar")
            
            # Asignar operación actual y enviar al servidor
            self._current_operation = "actualizar"
            self.cliente_handler.actualizar_cliente(id, datos)
            
        except Exception as e:
            logger.error(f"Error al actualizar cliente: {e}")
            self.error_ocurrido.emit(str(e))
            self._current_operation = None
            
    def _procesar_cliente_actualizado(self, response: dict) -> None:
        """Procesa la respuesta después de actualizar un cliente"""
        try:
            cliente = Cliente.from_dict(response)
            
            # Actualizar el cliente en la lista local
            for i, c in enumerate(self.clientes):
                if c.id == cliente.id:
                    self.clientes[i] = cliente
                    break
            else:
                # Si no se encuentra, agregarlo a la lista
                self.clientes.append(cliente)
            
            # Actualizar el modelo
            self.item_model.updateClientes(self.clientes)
            
            # Notificar que se actualizó el cliente
            self.cliente_actualizado.emit(cliente)
            
            # Notificar que se actualizó la lista completa
            self.clientes_actualizados.emit(self.clientes)
            
            logger.info(f"Cliente {cliente.nombre_completo} actualizado exitosamente")
        except Exception as e:
            logger.error(f"Error procesando cliente actualizado: {e}")
            self.error_ocurrido.emit(str(e))
            
    def eliminar_cliente(self, id: str):
        """
        Elimina un cliente
        
        Args:
            id: ID del cliente a eliminar
        """
        # Verificar que el ID exista antes de intentar eliminar
        if not id:
            self.error_ocurrido.emit("No se puede eliminar: Cliente no válido o sin ID")
            return
        
        # Verificar disponibilidad de API
        if not getattr(self, '_api_disponible', False):
            self.error_ocurrido.emit("Servidor no disponible. Compruebe su conexión.")
            return
            
        try:
            # Validar que el ID tenga formato UUID
            import re
            uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
            if not uuid_pattern.match(str(id)):
                mensaje = f"ID {id} no tiene formato UUID válido. No se puede eliminar."
                logger.error(mensaje)
                raise ValueError(mensaje)
                
            logger.info(f"Eliminando cliente con ID {id}...")
            
            # Guardar ID del cliente a eliminar para procesarlo luego
            self._cliente_a_eliminar = id
            
            # Asignar operación e iniciar eliminación
            self._current_operation = "eliminar"
            self.cliente_handler.eliminar_cliente(id)
            
        except Exception as e:
            logger.error(f"Error al eliminar cliente: {e}")
            self.error_ocurrido.emit(str(e))
            self._current_operation = None
    
    def _procesar_cliente_eliminado(self) -> None:
        """Procesa la respuesta después de eliminar un cliente"""
        try:
            if hasattr(self, '_cliente_a_eliminar'):
                # Eliminar el cliente de la lista local
                self.clientes = [c for c in self.clientes if c.id != self._cliente_a_eliminar]
                
                # Actualizar el modelo
                self.item_model.updateClientes(self.clientes)
                
                # Notificar que se actualizó la lista
                self.clientes_actualizados.emit(self.clientes)
                
                logger.info(f"Cliente eliminado exitosamente")
                
                # Eliminar el atributo temporal
                delattr(self, '_cliente_a_eliminar')
        except Exception as e:
            logger.error(f"Error procesando eliminación de cliente: {e}")
            self.error_ocurrido.emit(str(e))

    def buscar_cliente(self, id: str) -> Optional[Cliente]:
        """
        Busca un cliente por su ID en la lista de clientes cargados
        
        Args:
            id: ID del cliente a buscar
            
        Returns:
            Cliente o None si no se encuentra
        """
        for cliente in self.clientes:
            if cliente.id == id:
                return cliente
        return None

    def filtrar_clientes(self, texto: str) -> List[Cliente]:
        """
        Filtra la lista de clientes por texto
        
        Args:
            texto: Texto a buscar
            
        Returns:
            List[Cliente]: Lista de clientes que coinciden
        """
        if not texto:
            return self.clientes
            
        texto = texto.lower()
        return [c for c in self.clientes if (
            texto in c.nombre_completo.lower() or
            texto in c.numero_documento.lower() or
            texto in (c.mail or "").lower() or
            texto in (c.telefonos or "").lower() or
            texto in (c.movil or "").lower() or
            texto in (c.direccion or "").lower()
        )]
