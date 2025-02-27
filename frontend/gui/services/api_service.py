"""
Servicio para manejar las comunicaciones con la API REST
"""

import aiohttp
import asyncio
import logging
import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.excepciones import ErrorAPI

# Configurar logging
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
        session: Optional[aiohttp.ClientSession] = None,
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
        self.metricas = {"total_requests": 0, "errores": 0, "tiempo_promedio": 0}

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Obtiene una sesión HTTP, creándola si es necesario

        Returns:
            aiohttp.ClientSession: Sesión HTTP activa
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    def get_headers(
        self, custom_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
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
        logger.info(" Token de autenticación establecido")

    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Obtiene datos del caché si están disponibles y válidos"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.cache_duration:
                return data
        return None

    async def _validar_respuesta(self, data: Any) -> bool:
        """
        Valida la estructura básica de la respuesta.
        Acepta tanto diccionarios como listas como respuestas válidas.
        """
        # Aceptamos tanto listas como diccionarios como respuestas válidas
        if not isinstance(data, (dict, list)):
            logger.warning(f"Tipo de respuesta inesperado: {type(data)}")
            return False
            
        # Si es una lista, verificamos que no esté vacía
        if isinstance(data, list) and not data:
            logger.warning("La lista de respuesta está vacía")
            return True  # Una lista vacía sigue siendo válida, solo la registramos
            
        # Si es un diccionario, podríamos hacer validaciones adicionales aquí
        # Por ahora, consideramos cualquier diccionario como válido
            
        return True

    async def _manejar_respuesta(
        self, response: aiohttp.ClientResponse, operacion: str
    ) -> Any:
        """
        Procesa la respuesta HTTP y maneja diferentes escenarios de error

        Args:
            response: Respuesta HTTP recibida
            operacion: Descripción de la operación para mensajes de error

        Returns:
            Any: Datos procesados de la respuesta

        Raises:
            ErrorAPI: Si hay un error en la respuesta
        """
        if response.status == 204:  # No Content
            return None

        try:
            # Intentar cargar el contenido como JSON
            data = await response.json()

            # Verificar si hay errores en la respuesta
            if 400 <= response.status < 600:
                # Manejar diferente si la respuesta es un diccionario o una lista
                if isinstance(data, dict):
                    mensaje_error = data.get(
                        "error",
                        data.get("mensaje", f"Error {response.status} en {operacion}"),
                    )
                else:
                    mensaje_error = f"Error {response.status} en {operacion}"
                
                logger.error(f"Error {response.status} en {operacion}: {mensaje_error}")
                raise ErrorAPI(f"Error del servidor: {mensaje_error}")

            # Validar la estructura de la respuesta si todo está bien
            if not await self._validar_respuesta(data):
                logger.warning(f"Estructura de respuesta inválida en {operacion}")
                raise ErrorAPI(f"Estructura de respuesta inválida en {operacion}")

            return data

        except json.JSONDecodeError:
            # Si la respuesta no es JSON válido
            contenido = await response.text()
            logger.error(
                f"Respuesta no es JSON válido en {operacion}: {contenido[:200]}..."
            )
            raise ErrorAPI(f"Respuesta no válida del servidor en {operacion}")

        except aiohttp.ClientResponseError as e:
            logger.error(f"Error de respuesta HTTP en {operacion}: {str(e)}")
            raise ErrorAPI(f"Error en la comunicación con el servidor: {str(e)}")

        except Exception as e:
            logger.error(f"Error inesperado en {operacion}: {str(e)}")
            logger.exception("Detalles del error inesperado:")
            raise ErrorAPI(f"Error inesperado al procesar la solicitud: {str(e)}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def request(
        self,
        metodo: str,
        endpoint: str,
        datos: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Método general para manejar requests HTTP con reintentos automáticos y control de timeout.
        """
        url = f"{self.url_base}/{endpoint}"
        inicio = datetime.now()
        self.metricas["total_requests"] += 1

        try:
            session = await self._get_session()
            request_headers = self.get_headers(headers)

            # Construcción de los argumentos de la petición
            if (
                isinstance(datos, str)
                and headers
                and headers.get("Content-Type") == "application/x-www-form-urlencoded"
            ):
                kwargs = {"data": datos}
            else:
                kwargs = {"json": datos} if datos is not None else {}

            # Creamos una función para la petición sin timeout interno
            async def do_request():
                async with session.request(
                    metodo, url, headers=request_headers, timeout=None, **kwargs
                ) as response:
                    # Cuando usamos 'async with', la respuesta se cierra automáticamente al salir del contexto
                    # Procesamos la respuesta dentro del contexto para asegurar que está abierta
                    resultado = await self._manejar_respuesta(response, f"{metodo} {endpoint}")
                    return resultado

            # Usamos asyncio.wait_for para controlar el timeout
            timeout_seconds = self.timeout if isinstance(self.timeout, (int, float)) else 30
            resultado = await asyncio.wait_for(do_request(), timeout=timeout_seconds)

            # Actualizar métricas
            tiempo = (datetime.now() - inicio).total_seconds()
            self.metricas["tiempo_promedio"] = (
                (
                    self.metricas["tiempo_promedio"]
                    * (self.metricas["total_requests"] - 1)
                )
                + tiempo
            ) / self.metricas["total_requests"]

            if tiempo > 1.0:  # Solo logear tiempos lentos
                logger.warning(f"Request {metodo} {endpoint} tomó {tiempo:.2f} segundos")
            return resultado
        except asyncio.TimeoutError:
            self.metricas["errores"] += 1
            logger.error(f"Timeout alcanzado en {metodo} {endpoint}")
            raise ErrorAPI(f"Timeout alcanzado en {metodo} {endpoint}")

        except aiohttp.ClientError as e:
            self.metricas["errores"] += 1
            logger.error(f"Error de conexión en {metodo} {endpoint}: {str(e)}")
            logger.exception("Detalles del error de conexión:")
            raise ErrorAPI(f"Error en la comunicación con la API: {str(e)}")

        except Exception as e:
            self.metricas["errores"] += 1
            logger.error(f"Error inesperado en {metodo} {endpoint}: {str(e)}")
            logger.exception("Detalles del error inesperado:")
            raise ErrorAPI(f"Error inesperado al procesar la solicitud: {str(e)}")

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
        self, endpoint: str, datos: Any = None, headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """Realiza una petición POST"""
        return await self.request("POST", endpoint, datos, headers)

    async def put(
        self, endpoint: str, datos: Any = None, headers: Optional[Dict[str, str]] = None
    ) -> Any:
        return await self.request("PUT", endpoint, datos, headers)

    async def delete(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None
    ) -> bool:
        response = await self.request("DELETE", endpoint, headers=headers)
        return response is None  # DELETE no devuelve contenido

    async def close(self):
        """Cierra la sesión HTTP"""
        if self._session and not self._session.closed:
            await self._session.close()

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
            "tiempo_promedio": round(self.metricas["tiempo_promedio"], 3),
        }
