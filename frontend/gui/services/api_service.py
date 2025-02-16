"""
Servicio para manejar las comunicaciones con la API REST
"""
import aiohttp
import logging
import json
from typing import Any, Dict, Optional
from frontend.gui.core.excepciones import ErrorAPI

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServicioAPI:
    """
    Clase para manejar todas las comunicaciones con la API REST
    """
    def __init__(self, url_base: str):
        self.url_base = url_base.rstrip('/')  # Remover slash final si existe
        self._token: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def headers(self) -> Dict[str, str]:
        """Construye los headers para las peticiones"""
        headers = {'Content-Type': 'application/json'}
        if self._token:
            headers['Authorization'] = f'Bearer {self._token}'
        return headers

    def establecer_token(self, token: str) -> None:
        """Establece el token de autenticación"""
        self._token = token
        logger.info("Token de autenticación establecido")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtiene o crea una sesión de aiohttp"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _manejar_respuesta(self, response: aiohttp.ClientResponse, operacion: str) -> Any:
        """Maneja la respuesta de la API y registra información relevante"""
        try:
            logger.info(f"=== Manejando respuesta de {operacion} ===")
            logger.info(f"Código de estado: {response.status}")
            logger.info(f"Headers de respuesta: {dict(response.headers)}")
            
            content_type = response.headers.get('Content-Type', 'No especificado')
            logger.info(f"Content-Type: {content_type}")

            if response.status >= 400:
                logger.error(f"=== Error en respuesta de {operacion} ===")
                texto = await response.text()
                logger.error(f"Respuesta texto: {texto}")
                
                try:
                    detalle = await response.json()
                    logger.error(f"Respuesta JSON: {json.dumps(detalle, indent=2, ensure_ascii=False)}")
                    mensaje_error = f"Error HTTP en {operacion}: {response.status} - {json.dumps(detalle, indent=2)}"
                except ValueError:
                    logger.error("No se pudo parsear la respuesta como JSON")
                    mensaje_error = f"Error HTTP en {operacion}: {response.status} - {texto}"
                
                raise ErrorAPI(mensaje_error)

            if response.content_length:
                try:
                    datos = await response.json()
                    logger.info("Respuesta recibida (JSON):")
                    logger.info(json.dumps(datos, indent=2, ensure_ascii=False))
                    return datos
                except ValueError as e:
                    logger.error(f"Error al parsear respuesta JSON: {str(e)}")
                    texto = await response.text()
                    logger.error(f"Contenido de respuesta (texto): {texto}")
                    raise ErrorAPI(f"Error al procesar respuesta del servidor en {operacion}")
            
            logger.info("Respuesta sin contenido")
            return None

        except aiohttp.ClientError as e:
            logger.error(f"=== Error de cliente en {operacion} ===")
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Mensaje de error: {str(e)}")
            raise ErrorAPI(f"Error en la comunicación con el servidor: {str(e)}")
        
        except Exception as e:
            logger.error(f"=== Error inesperado en {operacion} ===")
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Mensaje de error: {str(e)}")
            raise ErrorAPI(f"Error inesperado al procesar la respuesta: {str(e)}")

    async def get(self, endpoint: str) -> Any:
        """Realiza una petición GET"""
        url = f"{self.url_base}/{endpoint}"
        self._log_request("GET", url)
        session = await self._get_session()
        async with session.get(url, headers=self.headers) as response:
            return await self._manejar_respuesta(response, f"GET {endpoint}")

    async def post(self, endpoint: str, datos: Dict) -> Any:
        """Realiza una petición POST"""
        url = f"{self.url_base}/{endpoint}"
        try:
            logger.info(f"=== Iniciando petición POST a {endpoint} ===")
            logger.info(f"URL completa: {url}")
            logger.info(f"Headers: {self.headers}")
            logger.info("Datos a enviar (sin contraseña):")
            datos_log = datos.copy()
            if 'password' in datos_log:
                datos_log['password'] = '********'
            logger.info(f"{json.dumps(datos_log, indent=2, ensure_ascii=False)}")

            session = await self._get_session()
            async with session.post(url, headers=self.headers, json=datos) as response:
                logger.info(f"Código de respuesta: {response.status}")
                
                if response.status >= 400:
                    content_type = response.headers.get('Content-Type', '')
                    logger.error(f"Error en la respuesta. Content-Type: {content_type}")
                    
                    texto = await response.text()
                    logger.error(f"Respuesta de error (texto): {texto}")
                    
                    try:
                        json_resp = await response.json()
                        logger.error(f"Respuesta de error (JSON): {json.dumps(json_resp, indent=2)}")
                    except:
                        logger.error("No se pudo parsear la respuesta como JSON")
                
                return await self._manejar_respuesta(response, f"POST {endpoint}")
                
        except aiohttp.ClientError as e:
            logger.error(f"=== Error de cliente HTTP en POST {endpoint} ===")
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Mensaje de error: {str(e)}")
            raise ErrorAPI(f"Error en la comunicación con el servidor: {str(e)}")
        except Exception as e:
            logger.error(f"=== Error inesperado en POST {endpoint} ===")
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Mensaje de error: {str(e)}")
            raise ErrorAPI(f"Error inesperado en la petición: {str(e)}")

    async def put(self, endpoint: str, datos: Dict) -> Any:
        """Realiza una petición PUT"""
        url = f"{self.url_base}/{endpoint}"
        self._log_request("PUT", url, datos)
        session = await self._get_session()
        async with session.put(url, headers=self.headers, json=datos) as response:
            return await self._manejar_respuesta(response, f"PUT {endpoint}")

    async def delete(self, endpoint: str) -> bool:
        """Realiza una petición DELETE"""
        url = f"{self.url_base}/{endpoint}"
        self._log_request("DELETE", url)
        session = await self._get_session()
        async with session.delete(url, headers=self.headers) as response:
            await self._manejar_respuesta(response, f"DELETE {endpoint}")
            return response.status == 204

    async def close(self):
        """Cierra la sesión HTTP"""
        if self._session and not self._session.closed:
            await self._session.close()
