"""
Repositorio para gestionar corredores a través de la API
"""

from typing import List, Optional
from datetime import datetime, date
import logging
from frontend.gui.repositories.base_repository import RepositorioBase
from frontend.gui.models.corredor import Corredor
from frontend.gui.services.api_service import ServicioAPI
from frontend.gui.core.excepciones import ErrorAPI

logger = logging.getLogger(__name__)


class RepositorioCorredor(RepositorioBase[Corredor]):
    """Implementación del repositorio de corredores"""

    def __init__(self, servicio_api: ServicioAPI):
        self.servicio_api = servicio_api

    def _adaptar_corredor_api(self, datos_api: dict) -> dict:
        """Adapta los datos de la API al formato del modelo"""
        try:
            # Convertir fechas si existen
            if "fecha_alta" in datos_api and datos_api["fecha_alta"]:
                datos_api["fecha_alta"] = datetime.strptime(
                    datos_api["fecha_alta"], "%Y-%m-%d"
                ).date()
            if "fecha_baja" in datos_api and datos_api["fecha_baja"]:
                datos_api["fecha_baja"] = datetime.strptime(
                    datos_api["fecha_baja"], "%Y-%m-%d"
                ).date()

            # Mapear campos de usuario
            datos_api["username"] = datos_api.get("username")
            datos_api["role"] = datos_api.get("role", "corredor")
            datos_api["is_active"] = datos_api.get("is_active", True)
            datos_api["comision_porcentaje"] = datos_api.get("comision_porcentaje", 0.0)

            return datos_api
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
        """Obtiene un corredor específico por su ID (número)"""
        return await self.obtener_por_numero(id)

    async def obtener_por_numero(self, numero: int) -> Optional[Corredor]:
        """Obtiene un corredor específico por su número"""
        try:
            respuesta = await self.servicio_api.get(f"corredores/{numero}")
            if respuesta:
                corredor = Corredor(**self._adaptar_corredor_api(respuesta))
                logger.info(f"Corredor obtenido: {corredor.numero}")
                return corredor
            return None
        except Exception as e:
            logger.error(f"Error al obtener corredor {numero}: {str(e)}")
            raise

    async def crear(self, corredor: Corredor, es_admin: bool = False) -> Corredor:
        """Crea un nuevo corredor"""
        try:
            datos = corredor.to_dict()
            # Asegurar que la fecha de alta sea hoy si no se proporciona
            if not datos.get("fecha_alta"):
                datos["fecha_alta"] = date.today().isoformat()

            # Determinar el endpoint basado en si es admin inicial
            endpoint = "corredores/admin" if es_admin else "corredores/"
            respuesta = await self.servicio_api.post(endpoint, datos)
            corredor_creado = Corredor(**self._adaptar_corredor_api(respuesta))
            logger.info(f"Corredor creado: {corredor_creado.numero}")
            return corredor_creado
        except Exception as e:
            logger.error(f"Error al crear corredor: {str(e)}")
            raise

    async def actualizar(self, corredor: Corredor) -> Corredor:
        """Actualiza un corredor existente"""
        try:
            datos = corredor.to_dict()
            respuesta = await self.servicio_api.put(
                f"corredores/{corredor.numero}", datos
            )
            corredor_actualizado = Corredor(**self._adaptar_corredor_api(respuesta))
            logger.info(f"Corredor actualizado: {corredor_actualizado.numero}")
            return corredor_actualizado
        except Exception as e:
            logger.error(f"Error al actualizar corredor {corredor.numero}: {str(e)}")
            raise

    async def eliminar(self, numero: int) -> bool:
        """Elimina un corredor por su número"""
        try:
            resultado = await self.servicio_api.delete(f"corredores/{numero}")
            if resultado:
                logger.info(f"Corredor {numero} eliminado")
            return resultado
        except Exception as e:
            logger.error(f"Error al eliminar corredor {numero}: {str(e)}")
            raise

    async def buscar_por_documento(self, documento: str) -> Optional[Corredor]:
        """Busca un corredor por su documento"""
        try:
            corredores = await self.obtener_todos()
            for corredor in corredores:
                if corredor.documento == documento:
                    logger.info(f"Corredor encontrado por documento: {documento}")
                    return corredor
            logger.info(f"No se encontró corredor con documento: {documento}")
            return None
        except Exception as e:
            logger.error(
                f"Error al buscar corredor por documento {documento}: {str(e)}"
            )
            raise

    async def buscar_por_email(self, email: str) -> Optional[Corredor]:
        """Busca un corredor por su email"""
        try:
            corredores = await self.obtener_todos()
            for corredor in corredores:
                if corredor.mail == email:
                    logger.info(f"Corredor encontrado por email: {email}")
                    return corredor
            logger.info(f"No se encontró corredor con email: {email}")
            return None
        except Exception as e:
            logger.error(f"Error al buscar corredor por email {email}: {str(e)}")
            raise
