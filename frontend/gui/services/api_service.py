"""
Servicio para manejar las comunicaciones con la API REST
"""

import aiohttp
import logging
import json
import asyncio
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.excepciones import ErrorAPI

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServicioAPI:
    """
    Clase para manejar todas las comunicaciones con la API REST
    """

    def __init__(
        self, 
        url_base: str, 
        timeout: int = 30,
        cache_duration: int = 5,
        session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Inicializa el servicio API
        
        Args:
            url_base: URL base para todas las peticiones
            timeout: Tiempo máximo de espera para peticiones en segundos
            cache_duration: Duración del caché en minutos
            session: Sesión aiohttp opcional para reutilizar
        """
        self.url_base = url_base.rstrip("/")  # Remover slash final si existe
        self._token: Optional[str] = None
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        
        # La sesión se creará cuando se necesite
        self._session = None
        
        # Configuración de caché
        self.cache = {}
        self.cache_duration = timedelta(minutes=cache_duration)
        
        # Métricas
        self.metricas = {
            "total_requests": 0,
            "errores": 0,
            "tiempo_promedio": 0
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Obtiene una sesión HTTP, creándola si es necesario
        
        Returns:
            aiohttp.ClientSession: Sesión HTTP activa
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    def get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Construye los headers para las peticiones
        
        Args:
            custom_headers: Headers adicionales a incluir
            
        Returns:
            Dict[str, str]: Headers combinados
        """
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def establecer_token(self, token: str) -> None:
        """Establece el token de autenticación"""
        self._token = token
        logger.info("🔑 Token de autenticación establecido")

    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Obtiene datos del caché si están disponibles y válidos"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.cache_duration:
                logger.debug(f"📦 Datos recuperados del caché para: {key}")
                return data
        return None

    async def _validar_respuesta(self, data: Dict) -> bool:
        """Valida la estructura básica de la respuesta"""
        if not isinstance(data, dict):
            return False
        return True  # Simplificamos la validación ya que la estructura puede variar

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def request(
        self, 
        metodo: str, 
        endpoint: str, 
        datos: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Método general para manejar requests HTTP con reintentos automáticos
        """
        url = f"{self.url_base}/{endpoint}"
        inicio = datetime.now()
        self.metricas["total_requests"] += 1

        try:
            session = await self._get_session()
            request_headers = self.get_headers(headers)
            
            # Si los datos son un string y el content-type es form-urlencoded,
            # enviamos los datos como texto
            if isinstance(datos, str) and headers and \
               headers.get("Content-Type") == "application/x-www-form-urlencoded":
                kwargs = {"data": datos}
            else:
                kwargs = {"json": datos} if datos is not None else {}

            async with session.request(
                metodo, 
                url, 
                headers=request_headers,
                **kwargs
            ) as response:
                resultado = await self._manejar_respuesta(response, f"{metodo} {endpoint}")
                
                # Actualizar métricas
                tiempo = (datetime.now() - inicio).total_seconds()
                self.metricas["tiempo_promedio"] = (
                    (self.metricas["tiempo_promedio"] * (self.metricas["total_requests"] - 1) + tiempo)
                    / self.metricas["total_requests"]
                )
                
                return resultado

        except aiohttp.ClientError as e:
            self.metricas["errores"] += 1
            logger.error(f"❌ Error de conexión en {metodo} {endpoint}: {str(e)}")
            raise ErrorAPI(f"Error en la comunicación con la API: {str(e)}")

        except Exception as e:
            self.metricas["errores"] += 1
            logger.error(f"❌ Error inesperado en {metodo} {endpoint}: {str(e)}")
            raise ErrorAPI(f"Error inesperado al procesar la solicitud: {str(e)}")

    async def _manejar_respuesta(self, response: aiohttp.ClientResponse, operacion: str) -> Any:
        """Maneja la respuesta de la API y errores"""
        logger.info(f"📡 {operacion} - Código de estado: {response.status}")

        try:
            if response.status >= 400:
                error_text = await response.text()
                logger.error(f"❌ Error en {operacion}: {error_text}")

                try:
                    error_json = await response.json()
                    raise ErrorAPI(f"Error en {operacion}: {json.dumps(error_json, indent=2)}")
                except ValueError:
                    raise ErrorAPI(f"Error en {operacion}: {error_text}")

            if response.content_length and response.content_length > 0:
                data = await response.json()
                return data

            return None  # Devuelve None si no hay contenido en la respuesta

        except aiohttp.ClientResponseError as e:
            logger.error(f"❌ Error HTTP en {operacion}: {e.status} - {e.message}")
            raise ErrorAPI(f"Error HTTP en {operacion}: {e.status} - {e.message}")

        except json.JSONDecodeError:
            error_text = await response.text()
            logger.error(f"❌ No se pudo parsear la respuesta en {operacion}: {error_text}")
            raise ErrorAPI(f"Respuesta no válida en {operacion}")

    async def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> Any:
        """Realiza una petición GET con soporte de caché"""
        cache_key = f"GET:{endpoint}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        result = await self.request("GET", endpoint, headers=headers)
        if result is not None:
            self.cache[cache_key] = (result, datetime.now())
        return result

    async def post(
        self, 
        endpoint: str, 
        datos: Any = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        return await self.request("POST", endpoint, datos, headers)

    async def put(
        self, 
        endpoint: str, 
        datos: Any = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        return await self.request("PUT", endpoint, datos, headers)

    async def delete(
        self, 
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        response = await self.request("DELETE", endpoint, headers=headers)
        return response is None  # DELETE no devuelve contenido

    async def close(self):
        """Cierra la sesión HTTP"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("🔌 Sesión HTTP cerrada correctamente")

    def get_metricas(self) -> Dict:
        """Retorna las métricas actuales del servicio"""
        return {
            "total_requests": self.metricas["total_requests"],
            "errores": self.metricas["errores"],
            "tasa_error": (
                self.metricas["errores"] / self.metricas["total_requests"]
                if self.metricas["total_requests"] > 0
                else 0
            ),
            "tiempo_promedio": round(self.metricas["tiempo_promedio"], 3)
        }
