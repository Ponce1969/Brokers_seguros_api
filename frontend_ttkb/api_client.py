"""
Cliente API para comunicación con el backend

Este cliente está diseñado para ser simple, directo y alineado
con los endpoints del backend. Utiliza la biblioteca requests
para realizar peticiones HTTP.
"""

import requests
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from urllib.parse import urljoin
import sys
sys.path.append('/home/gonzapython/CascadeProjects/Brokerseguros')
from frontend_ttkb import config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIClient:
    """
    Cliente API simple para comunicarse con el backend.
    
    Esta clase proporciona métodos para interactuar con el backend
    de forma directa y sencilla, sin abstracciones innecesarias.
    """
    
    def __init__(self):
        """
        Inicializa el cliente API con la URL base configurada.
        """
        self.base_url = config.API_URL
        self.token = None
        self.token_type = None
        self.session = requests.Session()
        logger.info(f"Cliente API inicializado con URL base: {self.base_url}")
    
    def set_token(self, token: str, token_type: str = "bearer") -> None:
        """
        Establece el token de autenticación para las peticiones.
        
        Args:
            token: El token JWT para autenticación.
            token_type: El tipo de token (por defecto 'bearer').
        """
        self.token = token
        self.token_type = token_type
        # Configurar el token en los headers para todas las peticiones futuras
        self.session.headers.update({"Authorization": f"{token_type.capitalize()} {token}"})
        logger.info("Token de autenticación establecido")
    
    def clear_token(self) -> None:
        """
        Elimina el token de autenticación.
        """
        self.token = None
        self.token_type = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        logger.info("Token de autenticación eliminado")
    
    def _get_full_url(self, endpoint: str) -> str:
        """
        Construye la URL completa para un endpoint.
        
        Args:
            endpoint: El endpoint relativo (sin la URL base).
            
        Returns:
            La URL completa para el endpoint.
        """
        # Asegurarse de que el endpoint no comience con '/'
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return urljoin(self.base_url, endpoint)
    
    def _handle_response(self, response: requests.Response) -> Tuple[bool, Any]:
        """
        Procesa la respuesta de la API y maneja posibles errores.
        
        Args:
            response: La respuesta HTTP recibida.
            
        Returns:
            Una tupla (exito, datos), donde exito es un booleano que indica
            si la petición fue exitosa, y datos contiene los datos de la respuesta
            o un mensaje de error.
        """
        try:
            # Verificar si la petición fue exitosa (código 2xx)
            if response.ok:
                # Intentar parsear la respuesta como JSON
                try:
                    data = response.json()
                    return True, data
                except ValueError:
                    # Si no es JSON, devolver el texto de la respuesta
                    return True, response.text
            else:
                # Manejar errores comunes
                if response.status_code == 401:
                    logger.error(f"Error de autenticación: {response.text}")
                    return False, config.MSG_ERROR_AUTENTICACION
                elif response.status_code == 403:
                    logger.error(f"Error de permisos: {response.text}")
                    return False, config.MSG_ERROR_PERMISOS
                elif response.status_code == 404:
                    logger.error(f"Recurso no encontrado: {response.text}")
                    return False, f"El recurso solicitado no existe: {response.url}"
                else:
                    # Intentar obtener detalles del error desde JSON
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", str(error_data))
                    except ValueError:
                        error_msg = response.text or f"Error {response.status_code}"
                    
                    logger.error(f"Error en petición ({response.status_code}): {error_msg}")
                    return False, error_msg
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {str(e)}")
            return False, config.MSG_ERROR_CONEXION
    
    def login(self, username: str, password: str) -> dict:
        """
        Realiza la autenticación con el backend.
        
        Args:
            username: El correo electrónico del usuario.
            password: La contraseña del usuario.
            
        Returns:
            Un diccionario con el token de acceso y su tipo si el login fue exitoso.
            
        Raises:
            Exception: Si hay algún error en la autenticación.
        """
        try:
            url = self._get_full_url(config.ENDPOINT_LOGIN)
            logger.info(f"Intentando login para usuario: {username}")
            
            # Datos de la petición de login
            data = {
                "username": username,
                "password": password
            }
            
            # Realizar la petición POST
            response = self.session.post(
                url, 
                data=data,
                timeout=config.HTTP_TIMEOUT
            )
            
            success, result = self._handle_response(response)
            if success:
                # Si el login fue exitoso, extraer el token
                token = result.get("access_token")
                token_type = result.get("token_type", "bearer")
                if token:
                    # No establecemos el token aquí, lo dejamos para que lo haga
                    # el llamador si así lo decide
                    logger.info(f"Login exitoso para {username}")
                    return result
                else:
                    logger.error("Login exitoso pero no se recibió token")
                    raise Exception("Error: No se recibió token de acceso")
            else:
                logger.error(f"Error en login: {result}")
                raise Exception(str(result))
        except Exception as e:
            logger.error(f"Error inesperado en login: {str(e)}")
            raise Exception(f"Error de autenticación: {str(e)}")
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Esta función ya no se utiliza ya que no dependemos del endpoint /api/v1/users/me.
        En su lugar, creamos la información del usuario a partir del email durante el login.
        
        Esta función se mantiene por compatibilidad pero siempre devuelve None.
        
        Returns:
            None para indicar que esta funcionalidad no está disponible.
        """
        logger.warning("La función get_current_user() está deprecada. La información del usuario se debe crear durante el login.")
        return None
    
    def get_clientes(self, role: str = None) -> List[dict]:
        """
        Obtiene la lista de clientes del backend.
        
        Args:
            role: El rol del usuario actual ('admin' o 'corredor').
                 Si es admin, se asegura de obtener clientes reales.
                 
        Returns:
            Una lista de diccionarios con los datos de los clientes.
            
        Raises:
            Exception: Si hay algún error en la petición.
        """
        try:
            url = self._get_full_url(config.ENDPOINT_CLIENTES)
            logger.info(f"Obteniendo lista de clientes para rol: {role}")
            
            # SOLUCIÓN AL PROBLEMA DE INCONSISTENCIA:
            # Sabemos que el endpoint se comporta diferente según la autenticación
            if role == 'admin':
                # Para administradores, necesitamos asegurar que obtenemos clientes reales
                # La solución es añadir un parámetro especial para indicarle al backend
                # que queremos los clientes reales, no los corredores
                url = f"{url}?real_clients=true"
                logger.info("Usuario administrador: solicitando clientes reales")
            
            response = self.session.get(
                url,
                timeout=config.HTTP_TIMEOUT
            )
            
            success, result = self._handle_response(response)
            if success:
                # Validar que el resultado es una lista
                if isinstance(result, list):
                    # Filtrar para asegurarnos de tener solo clientes reales
                    # Este es un paso adicional para manejar la inconsistencia
                    filtered_clients = []
                    for client in result:
                        # Verificar si parece un corredor (tiene campos específicos)
                        if role == 'admin' and client.get('is_superuser') is not None:
                            # Esto parece un corredor, no un cliente real
                            logger.debug(f"Filtrando corredor: {client.get('email')}")
                            continue
                        filtered_clients.append(client)
                    
                    logger.info(f"Se obtuvieron {len(filtered_clients)} clientes reales")
                    return filtered_clients
                else:
                    logger.warning("La respuesta no es una lista de clientes")
                    if isinstance(result, dict) and 'items' in result:
                        # Algunos APIs devuelven {items: [...], total: X}
                        return result['items']
                    elif isinstance(result, dict):
                        # Si es un único objeto, lo devolvemos como lista de un elemento
                        return [result]
                    # Si no podemos convertirlo, devolver lista vacía
                    logger.error("No se pudo convertir la respuesta a lista de clientes")
                    return []
            else:
                logger.error(f"Error al obtener clientes: {result}")
                raise Exception(str(result))
        except Exception as e:
            logger.error(f"Error inesperado al obtener clientes: {str(e)}")
            raise Exception(f"Error al obtener clientes: {str(e)}")
            
    def get_cliente(self, cliente_id: str) -> dict:
        """
        Obtiene los datos de un cliente específico.
        
        Args:
            cliente_id: El ID del cliente a obtener.
            
        Returns:
            Un diccionario con la información del cliente.
            
        Raises:
            Exception: Si hay algún error en la petición.
        """
        try:
            url = self._get_full_url(f"{config.ENDPOINT_CLIENTES}/{cliente_id}")
            logger.info(f"Obteniendo datos del cliente con ID: {cliente_id}")
            
            response = self.session.get(
                url,
                timeout=config.HTTP_TIMEOUT
            )
            
            success, result = self._handle_response(response)
            if success and isinstance(result, dict):
                logger.info(f"Datos del cliente obtenidos: {result.get('email', 'Sin email')}")
                return result
            else:
                logger.error(f"Error al obtener datos del cliente: {result}")
                raise Exception(str(result))
        except Exception as e:
            logger.error(f"Error inesperado al obtener datos del cliente: {str(e)}")
            raise Exception(f"Error al obtener datos del cliente: {str(e)}")
    
    def get_corredores(self) -> List[dict]:
        """
        Obtiene la lista de corredores del backend.
        
        Returns:
            Una lista de diccionarios con los datos de los corredores.
            
        Raises:
            Exception: Si hay algún error en la petición.
        """
        try:
            url = self._get_full_url(config.ENDPOINT_CORREDORES)
            logger.info("Obteniendo lista de corredores")
            
            response = self.session.get(
                url,
                timeout=config.HTTP_TIMEOUT
            )
            
            success, result = self._handle_response(response)
            if success:
                if isinstance(result, list):
                    logger.info(f"Se obtuvieron {len(result)} corredores")
                    return result
                else:
                    logger.warning("La respuesta no es una lista de corredores")
                    if isinstance(result, dict) and 'items' in result:
                        return result['items']
                    elif isinstance(result, dict):
                        return [result]
                    return []
            else:
                logger.error(f"Error al obtener corredores: {result}")
                raise Exception(str(result))
        except Exception as e:
            logger.error(f"Error inesperado al obtener corredores: {str(e)}")
            raise Exception(f"Error al obtener corredores: {str(e)}")
    
    def get_corredor(self, corredor_id: str) -> dict:
        """
        Obtiene los datos de un corredor específico.
        
        Args:
            corredor_id: El ID del corredor a obtener.
            
        Returns:
            Un diccionario con la información del corredor.
            
        Raises:
            Exception: Si hay algún error en la petición.
        """
        try:
            url = self._get_full_url(f"{config.ENDPOINT_CORREDORES}/{corredor_id}")
            logger.info(f"Obteniendo datos del corredor con ID: {corredor_id}")
            
            response = self.session.get(
                url,
                timeout=config.HTTP_TIMEOUT
            )
            
            success, result = self._handle_response(response)
            if success and isinstance(result, dict):
                logger.info(f"Datos del corredor obtenidos: {result.get('email', 'Sin email')}")
                return result
            else:
                logger.error(f"Error al obtener datos del corredor: {result}")
                raise Exception(str(result))
        except Exception as e:
            logger.error(f"Error inesperado al obtener datos del corredor: {str(e)}")
            raise Exception(f"Error al obtener datos del corredor: {str(e)}")
            
    def get_movimientos(self) -> List[dict]:
        """
        Obtiene la lista de movimientos del backend.
        
        Returns:
            Una lista de diccionarios con los datos de los movimientos.
            
        Raises:
            Exception: Si hay algún error en la petición.
        """
        try:
            url = self._get_full_url(config.ENDPOINT_MOVIMIENTOS)
            logger.info("Obteniendo lista de movimientos")
            
            response = self.session.get(
                url,
                timeout=config.HTTP_TIMEOUT
            )
            
            success, result = self._handle_response(response)
            if success:
                if isinstance(result, list):
                    logger.info(f"Se obtuvieron {len(result)} movimientos")
                    return result
                else:
                    logger.warning("La respuesta no es una lista de movimientos")
                    if isinstance(result, dict) and 'items' in result:
                        return result['items']
                    elif isinstance(result, dict):
                        return [result]
                    return []
            else:
                logger.error(f"Error al obtener movimientos: {result}")
                raise Exception(str(result))
        except Exception as e:
            logger.error(f"Error inesperado al obtener movimientos: {str(e)}")
            raise Exception(f"Error al obtener movimientos: {str(e)}")
