"""
Repositorio para gestionar usuarios a través de la API
"""

from typing import List, Optional
from datetime import datetime
import logging
from frontend.gui.repositories.base_repository import RepositorioBase
from frontend.gui.models.usuario import Usuario
from frontend.gui.services.api_service import ServicioAPI
from frontend.gui.core.excepciones import ErrorAPI

logger = logging.getLogger(__name__)


class RepositorioUsuario(RepositorioBase[Usuario]):
    """
    Implementación del repositorio de usuarios que se comunica con la API
    """

    def __init__(self, servicio_api: ServicioAPI):
        self.servicio_api = servicio_api

    def _adaptar_usuario_api(self, datos_api: dict) -> dict:
        """Adapta los datos de la API al formato esperado por el modelo Usuario"""
        try:
            # Convertir strings de fecha a objetos datetime si existen
            campos_fecha = [
                "fecha_creacion",
                "fecha_modificacion",
                "fecha_alta",
                "fecha_baja",
            ]
            for campo in campos_fecha:
                valor = datos_api.get(campo)
                if valor and isinstance(valor, str):
                    datos_api[campo] = datetime.fromisoformat(
                        valor.replace("Z", "+00:00")
                    )

            return {
                "id": datos_api.get("id"),
                "username": datos_api.get("username", ""),
                "email": datos_api.get("email", ""),
                "nombres": datos_api.get("nombres", ""),
                "apellidos": datos_api.get("apellidos", ""),
                "is_active": datos_api.get("is_active", True),
                "is_superuser": datos_api.get("is_superuser", False),
                "role": datos_api.get("role", "corredor"),
                "corredor_numero": datos_api.get("corredor_numero"),
                "comision_porcentaje": datos_api.get("comision_porcentaje", 0.0),
                "telefono": datos_api.get("telefono"),
                "movil": datos_api.get("movil"),
                "documento": datos_api.get("documento"),
                "direccion": datos_api.get("direccion"),
                "localidad": datos_api.get("localidad"),
                "fecha_alta": datos_api.get("fecha_alta"),
                "fecha_baja": datos_api.get("fecha_baja"),
                "matricula": datos_api.get("matricula"),
                "especializacion": datos_api.get("especializacion"),
                "fecha_creacion": datos_api.get("fecha_creacion"),
                "fecha_modificacion": datos_api.get("fecha_modificacion"),
            }
        except Exception as e:
            logger.error(f"Error al adaptar datos de usuario: {str(e)}")
            raise ErrorAPI(f"Error al procesar datos del usuario: {str(e)}")

    def _preparar_datos_api(
        self, usuario: Usuario, password: Optional[str] = None
    ) -> dict:
        """Prepara los datos del usuario para enviar a la API"""
        datos = {
            "username": usuario.username,
            "email": usuario.email,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "is_active": usuario.is_active,
            "is_superuser": usuario.is_superuser,
            "role": usuario.role,
            "corredor_numero": usuario.corredor_numero,
            "comision_porcentaje": usuario.comision_porcentaje,
            "telefono": usuario.telefono,
            "movil": usuario.movil,
            "documento": usuario.documento,
            "direccion": usuario.direccion,
            "localidad": usuario.localidad,
            "fecha_alta": (
                usuario.fecha_alta.isoformat() if usuario.fecha_alta else None
            ),
            "fecha_baja": (
                usuario.fecha_baja.isoformat() if usuario.fecha_baja else None
            ),
            "matricula": usuario.matricula,
            "especializacion": usuario.especializacion,
        }

        # Agregar contraseña solo si se proporciona (para nuevos usuarios)
        if password:
            datos["password"] = password

        # Agregar ID solo si existe (para actualizaciones)
        if usuario.id:
            datos["id"] = usuario.id

        return datos

    def _formatear_documento(self, tipo: str, numero: str) -> str:
        """Formatea el documento para que quepa en el límite de 20 caracteres"""
        # Mapeo de tipos de documento a abreviaturas
        abreviaturas = {
            "Cédula de Identidad": "CI",
            "DNI": "DNI",
            "RUT": "RUT",
            "CUIT": "CUIT",
            "Pasaporte": "PAS",
            "Otro": "OTR",
        }

        # Usar la abreviatura o el tipo original si no está en el mapeo
        prefijo = abreviaturas.get(tipo, tipo[:3].upper())
        # Formatear como "TIPO:NUMERO"
        return f"{prefijo}:{numero}"

    async def obtener_todos(self) -> List[Usuario]:
        """Obtiene todos los usuarios desde la API"""
        try:
            respuesta = await self.servicio_api.get("usuarios/")
            usuarios = [
                Usuario(**self._adaptar_usuario_api(usuario)) for usuario in respuesta
            ]
            logger.info(f"Obtenidos {len(usuarios)} usuarios")
            return usuarios
        except Exception as e:
            logger.error(f"Error al obtener usuarios: {str(e)}")
            raise

    async def obtener_por_id(self, id: int) -> Optional[Usuario]:
        """Obtiene un usuario específico por su ID"""
        try:
            respuesta = await self.servicio_api.get(f"usuarios/{id}")
            if respuesta:
                usuario = Usuario(**self._adaptar_usuario_api(respuesta))
                logger.info(f"Usuario obtenido: {usuario.username}")
                return usuario
            return None
        except Exception as e:
            logger.error(f"Error al obtener usuario {id}: {str(e)}")
            raise

    async def crear(self, usuario: Usuario, password: Optional[str] = None) -> Usuario:
        """Crea un nuevo usuario"""
        try:
            datos = self._preparar_datos_api(usuario, password)
            logger.debug(f"Datos preparados para crear usuario: {datos}")
            respuesta = await self.servicio_api.post("usuarios/", datos)
            usuario_creado = Usuario(**self._adaptar_usuario_api(respuesta))
            logger.info(f"Usuario creado: {usuario_creado.username}")
            return usuario_creado
        except Exception as e:
            logger.error(f"Error al crear usuario: {str(e)}")
            raise

    async def actualizar(self, usuario: Usuario) -> Usuario:
        """Actualiza un usuario existente"""
        try:
            datos = self._preparar_datos_api(usuario)
            respuesta = await self.servicio_api.put(f"usuarios/{usuario.id}", datos)
            usuario_actualizado = Usuario(**self._adaptar_usuario_api(respuesta))
            logger.info(f"Usuario actualizado: {usuario_actualizado.username}")
            return usuario_actualizado
        except Exception as e:
            logger.error(f"Error al actualizar usuario {usuario.id}: {str(e)}")
            raise

    async def eliminar(self, id: int) -> bool:
        """Elimina un usuario por su ID"""
        try:
            resultado = await self.servicio_api.delete(f"usuarios/{id}")
            if resultado:
                logger.info(f"Usuario {id} eliminado")
            return resultado
        except Exception as e:
            logger.error(f"Error al eliminar usuario {id}: {str(e)}")
            raise

    async def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """Método adicional para buscar usuario por email"""
        try:
            respuesta = await self.servicio_api.get(f"usuarios/email/{email}")
            if respuesta:
                usuario = Usuario(**self._adaptar_usuario_api(respuesta))
                logger.info(f"Usuario encontrado por email: {email}")
                return usuario
            return None
        except Exception as e:
            logger.error(f"Error al buscar usuario por email {email}: {str(e)}")
            raise
