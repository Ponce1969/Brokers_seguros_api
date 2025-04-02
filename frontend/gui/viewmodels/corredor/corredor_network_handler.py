"""
Manejador de red para operaciones relacionadas con corredores

Se encarga de todas las operaciones de red y manejo de respuestas HTTP
para el modelo de corredores.
"""

import logging
from typing import Callable, Dict, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class CorredorNetworkHandler(QObject):
    """
    Clase para manejar las operaciones de red relacionadas con corredores
    
    Se encarga de realizar peticiones HTTP y procesar las respuestas de la API
    para las operaciones CRUD de corredores.
    """
    
    # Seu00f1ales para comunicar resultados
    error_ocurrido = pyqtSignal(str)
    respuesta_recibida = pyqtSignal(object, str)
    
    def __init__(self, network_manager=None):
        """
        Inicializa el manejador de red
        
        Args:
            network_manager: Instancia del NetworkManager (opcional)
        """
        super().__init__()
        
        # Inicializar NetworkManager
        from ...core.di_container import contenedor
        from ...services.network_manager import NetworkManager
        self.api = network_manager if network_manager is not None else contenedor.resolver(NetworkManager)
        
        # Conectar seu00f1ales del NetworkManager
        self.api.response_received.connect(self._handle_response)
        self.api.error_occurred.connect(self._handle_error)
        
        # Variable para rastrear la operaciu00f3n actual
        self._current_operation = None
        self._callback_map: Dict[str, Callable] = {}
    
    def _handle_error(self, error_msg: str):
        """
        Maneja los errores del NetworkManager
        
        Args:
            error_msg: Mensaje de error
        """
        logger.error(f"Error en la operaciu00f3n {self._current_operation}: {error_msg}")
        self.error_ocurrido.emit(error_msg)
    
    def _handle_response(self, response):
        """
        Maneja las respuestas del servidor
        
        Verifica el tipo de respuesta y emite la seu00f1al correspondiente
        
        Args:
            response: Respuesta del servidor
        """
        operation = self._current_operation
        try:
            # Verificar si es una respuesta vu00e1lida segu00fan el tipo de operaciu00f3n
            self._validate_response(response, operation)
            
            # Emitir seu00f1al con la respuesta y la operaciu00f3n que la originu00f3
            self.respuesta_recibida.emit(response, operation)
            
        except Exception as e:
            logger.error(f"Error procesando respuesta: {e}")
            self.error_ocurrido.emit(str(e))
        finally:
            self._current_operation = None
    
    def _validate_response(self, response, operation):
        """
        Valida que la respuesta tenga el formato esperado segu00fan la operaciu00f3n
        
        Args:
            response: Respuesta a validar
            operation: Tipo de operaciu00f3n realizada
            
        Raises:
            ValueError: Si la respuesta no tiene el formato esperado
        """
        if operation == "cargar":
            if not isinstance(response, list):
                raise ValueError("Formato de respuesta invu00e1lido al cargar corredores")
        elif operation in ["crear", "actualizar"]:
            if not isinstance(response, dict):
                raise ValueError(f"Respuesta invu00e1lida al {operation} corredor")
    
    def cargar_corredores(self):
        """
        Carga la lista de corredores desde el servidor
        """
        self._current_operation = "cargar"
        logger.debug("Cargando lista de corredores...")
        self.api.get("api/v1/corredores/")
    
    def crear_corredor(self, datos: dict):
        """
        Crea un nuevo corredor en el servidor
        
        Args:
            datos: Diccionario con los datos del corredor
        """
        self._current_operation = "crear"
        logger.debug(f"Creando corredor: {datos}")
        self.api.post("api/v1/corredores/", datos)
    
    def actualizar_corredor(self, id: int, datos: dict):
        """
        Actualiza un corredor existente
        
        Args:
            id: ID del corredor a actualizar
            datos: Diccionario con los datos a actualizar (formato frontend)
        """
        self._current_operation = "actualizar"
        # URL sin barra final para evitar redirecciones 307
        url = f"api/v1/corredores/{id}"
        
        # Obtener los datos actuales del corredor para referencias y valores por defecto
        logger.info(f"📝 Obteniendo modelo actual para corredor {id} antes de actualizar")
        try:
            # Hacer GET para obtener el modelo actual
            corredor_actual = self.api.get(f"api/v1/corredores/{id}")
            logger.debug(f"📗 Modelo actual del corredor: {corredor_actual}")
        except Exception as e:
            logger.error(f"❌ Error al obtener el modelo actual: {e}")
            corredor_actual = {}
            
        logger.debug(f"[DIAGNÓSTICO] Datos recibidos del frontend: {datos}")
        
        # IMPORTANTE: Transformación de datos frontend→backend
        # El frontend usa: nombre, email, telefono
        # El backend espera: nombres, apellidos, mail, telefonos (modelo CorredorUpdate)
        
        # Crear un diccionario para el backend (modelo CorredorUpdate)
        datos_backend = {}
        
        # Mapear nombre → nombres/apellidos (dividir el nombre completo)
        if 'nombre' in datos:
            partes_nombre = datos['nombre'].split(' ', 1)  # Dividir en 2 partes máximo
            if len(partes_nombre) >= 2:
                datos_backend['nombres'] = partes_nombre[0]
                datos_backend['apellidos'] = partes_nombre[1]
            else:
                # Si solo hay una parte, la consideramos apellido (campo requerido)
                datos_backend['nombres'] = ''
                datos_backend['apellidos'] = partes_nombre[0]
                
        # Mapear email → mail
        if 'email' in datos:
            datos_backend['mail'] = datos['email']
            
        # Mapear telefono → telefonos
        if 'telefono' in datos:
            datos_backend['telefonos'] = datos['telefono']
            
        # Copiar dirección directamente (mismo nombre de campo)
        if 'direccion' in datos:
            datos_backend['direccion'] = datos['direccion']
            
        # Mapear localidad (requerido por el backend)
        if 'localidad' in datos:
            datos_backend['localidad'] = datos['localidad']
        else:
            # Verificar si podemos obtenerlo del objeto original
            logger.debug(f"ℹ️ Falta campo localidad. Usando valor por defecto.")
            datos_backend['localidad'] = "Montevideo"  # Valor por defecto
            
        # Documento es requerido por el backend - MANDATORIO
        if 'documento' in datos:
            datos_backend['documento'] = datos['documento']
        elif corredor_actual and 'documento' in corredor_actual:
            # Usar el valor del modelo actual
            logger.debug(f"ℹ️ Tomando valor de documento del modelo actual: {corredor_actual['documento']}")
            datos_backend['documento'] = corredor_actual['documento']
        else:
            # Valor por defecto para documento (REQUERIDO por el API)
            logger.debug(f"ℹ️ Falta campo documento. Usando valor por defecto.")
            # Debemos proporcionar un valor ya que el backend no acepta actualizaciones sin este campo
            datos_backend['documento'] = "00000000"  # Valor provisional que cumple con las validaciones
            
        # Campos opcionales
        for campo in ['movil', 'observaciones', 'matricula', 'especializacion']:
            if campo in datos:
                datos_backend[campo] = datos[campo]
            
        # Convertir booleano 'activo' a fecha_baja
        if 'activo' in datos and datos['activo'] is False:
            from datetime import date
            datos_backend['fecha_baja'] = date.today().isoformat()
        elif 'activo' in datos and datos['activo'] is True:
            datos_backend['fecha_baja'] = None
            
        # Validación de tipos de datos (mantenemos la validación existente)
        for campo, valor in datos_backend.items():
            # Validar strings vacíos
            if isinstance(valor, str) and valor.strip() == '':
                datos_backend[campo] = None
                continue
                
            # Convertir números si están como strings
            if campo in ['numero'] and isinstance(valor, str):
                if valor.strip().isdigit():
                    datos_backend[campo] = int(valor.strip())
                    
            # Validar booleanos expresados como string
            if campo in ['activo'] and isinstance(valor, str):
                valor_lower = valor.lower().strip()
                if valor_lower in ['true', 'verdadero', 'si', 'sí', 'yes', '1']:
                    datos_backend[campo] = True
                elif valor_lower in ['false', 'falso', 'no', '0']:
                    datos_backend[campo] = False
        
        # Logging detallado para depuración
        logger.debug(f"[DIAGNÓSTICO] Datos transformados para backend: {datos_backend}")
        
        # Enviar la petición al servidor con el formato CorredorUpdate
        self.api.put(url, datos_backend)
    
    def eliminar_corredor(self, id: int):
        """
        Elimina un corredor
        
        Args:
            id: ID del corredor a eliminar
        """
        self._current_operation = "eliminar"
        logger.debug(f"Eliminando corredor {id}")
        self.api.delete(f"api/v1/corredores/{id}/")
