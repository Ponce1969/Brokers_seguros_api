"""
Repositorio para gestionar corredores a través de la API
"""

from typing import List, Optional
from datetime import datetime
import logging
from frontend.gui.repositories.base_repository import RepositorioBase
from frontend.gui.models.corredor import Corredor
from frontend.gui.services.api_service import ServicioAPI
from frontend.gui.core.excepciones import ErrorAPI

logger = logging.getLogger(__name__)


class RepositorioCorredor(RepositorioBase[Corredor]):
    """
    Implementación del repositorio de corredores que se comunica con la API
    """

    def __init__(self, servicio_api: ServicioAPI):
        self.servicio_api = servicio_api

    def _adaptar_corredor_api(self, datos_api: dict) -> dict:
        """Adapta los datos de la API al formato esperado por el modelo Corredor"""
        try:
            # Convertir strings de fecha a objetos datetime si existen
            campos_fecha = ["fecha_alta", "fecha_baja"]
            for campo in campos_fecha:
                valor = datos_api.get(campo)
                if valor and isinstance(valor, str):
                    datos_api[campo] = datetime.fromisoformat(
                        valor.replace("Z", "+00:00")
                    ).date()

            return {
                "numero": datos_api.get("numero"),
                "nombres": datos_api.get("nombres", ""),
                "apellidos": datos_api.get("apellidos", ""),
                "documento": datos_api.get("documento", ""),
                "direccion": datos_api.get("direccion", ""),
                "localidad": datos_api.get("localidad", ""),
                "telefonos": datos_api.get("telefonos"),
                "movil": datos_api.get("movil"),
                "mail": datos_api.get("mail"),
                "observaciones": datos_api.get("observaciones"),
                "matricula": datos_api.get("matricula"),
                "especializacion": datos_api.get("especializacion"),
                "fecha_alta": datos_api.get("fecha_alta"),
                "fecha_baja": datos_api.get("fecha_baja"),
            }
        except Exception as e:
            logger.error(f"Error al adaptar datos de corredor: {str(e)}")
            raise ErrorAPI(f"Error al procesar datos del corredor: {str(e)}")

    async def obtener_todos(self) -> List[Corredor]:
        """Obtiene todos los corredores desde la API"""
        try:
            respuesta = await self.servicio_api.get("corredores/")
            corredores = [
                Corredor(**self._adaptar_corredor_api(corredor))
                for corredor in respuesta
            ]
            logger.info(f"Obtenidos {len(corredores)} corredores")
            return corredores
        except Exception as e:
            logger.error(f"Error al obtener corredores: {str(e)}")
            raise

    async def obtener_por_id(self, id: int) -> Optional[Corredor]:
        """Obtiene un corredor específico por su ID"""
        try:
            respuesta = await self.servicio_api.get(f"corredores/{id}")
            if respuesta:
                corredor = Corredor(**self._adaptar_corredor_api(respuesta))
                logger.info(f"Corredor obtenido: {corredor.numero}")
                return corredor
            return None
        except Exception as e:
            logger.error(f"Error al obtener corredor {id}: {str(e)}")
            raise

    async def crear(self, corredor: Corredor) -> Corredor:
        """Crea un nuevo corredor"""
        try:
            datos = {
                "numero": corredor.numero,
                "nombres": corredor.nombres,
                "apellidos": corredor.apellidos,
                "documento": corredor.documento,
                "direccion": corredor.direccion,
                "localidad": corredor.localidad,
                "telefonos": corredor.telefonos,
                "movil": corredor.movil,
                "mail": corredor.mail,
                "observaciones": corredor.observaciones,
                "matricula": corredor.matricula,
                "especializacion": corredor.especializacion,
                "fecha_alta": corredor.fecha_alta.isoformat() if corredor.fecha_alta else None,
            }

            logger.debug(f"Datos preparados para crear corredor: {datos}")
            respuesta = await self.servicio_api.post("corredores/", datos)
            corredor_creado = Corredor(**self._adaptar_corredor_api(respuesta))
            logger.info(f"Corredor creado: {corredor_creado.numero}")
            return corredor_creado
        except Exception as e:
            logger.error(f"Error al crear corredor: {str(e)}")
            raise

    async def actualizar(self, corredor: Corredor) -> Corredor:
        """Actualiza un corredor existente"""
        try:
            datos = {
                "nombres": corredor.nombres,
                "apellidos": corredor.apellidos,
                "documento": corredor.documento,
                "direccion": corredor.direccion,
                "localidad": corredor.localidad,
                "telefonos": corredor.telefonos,
                "movil": corredor.movil,
                "mail": corredor.mail,
                "observaciones": corredor.observaciones,
                "matricula": corredor.matricula,
                "especializacion": corredor.especializacion,
                "fecha_alta": corredor.fecha_alta.isoformat() if corredor.fecha_alta else None,
                "fecha_baja": corredor.fecha_baja.isoformat() if corredor.fecha_baja else None,
            }

            respuesta = await self.servicio_api.put(f"corredores/{corredor.numero}", datos)
            corredor_actualizado = Corredor(**self._adaptar_corredor_api(respuesta))
            logger.info(f"Corredor actualizado: {corredor_actualizado.numero}")
            return corredor_actualizado
        except Exception as e:
            logger.error(f"Error al actualizar corredor {corredor.numero}: {str(e)}")
            raise

    async def eliminar(self, id: int) -> bool:
        """Elimina un corredor por su ID"""
        try:
            resultado = await self.servicio_api.delete(f"corredores/{id}")
            if resultado:
                logger.info(f"Corredor {id} eliminado")
            return resultado
        except Exception as e:
            logger.error(f"Error al eliminar corredor {id}: {str(e)}")
            raise


# El repositorio se inicializará con el servicio API desde main.py
