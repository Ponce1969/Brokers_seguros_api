import logging
from datetime import date
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class CorredorNetworkHandler:
    def __init__(self, api):
        self.api = api
        self._current_operation = None
    
    def crear_corredor(self, datos: dict):
        """
        Crea un nuevo corredor
        
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
        
        # Obtener los datos actuales del corredor para referencias
        logger.info(f"📝 Obteniendo modelo actual para corredor {id} antes de actualizar")
        try:
            # Hacer GET para obtener el modelo actual
            corredor_actual = self.api.get(f"api/v1/corredores/{id}")
            logger.debug(f"📗 Modelo actual del corredor: {corredor_actual}")
        except Exception as e:
            logger.error(f"❌ Error al obtener el modelo actual: {e}")
            corredor_actual = {}
            
        logger.debug(f"[DIAGNÓSTICO] Datos recibidos del frontend: {datos}")
        
        # IMPORTANTE: Validación de datos requeridos
        campos_requeridos_frontend = {
            'nombre': 'Nombre completo',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'documento': 'Documento'
        }
        
        # Verificar si faltan campos requeridos en el frontend
        campos_faltantes = []
        for campo, descripcion in campos_requeridos_frontend.items():
            if campo not in datos or not datos[campo]:
                campos_faltantes.append(descripcion)
        
        # Si faltan campos, mostrar un mensaje de error claro
        if campos_faltantes:
            mensaje_error = f"Faltan campos requeridos: {', '.join(campos_faltantes)}"
            logger.error(f"🔴 {mensaje_error}")
            # Lanzar una excepción que será capturada por el manejador de errores
            raise ValueError(mensaje_error)
        
        # No es necesaria una transformación ya que el frontend ya está usando
        # los mismos nombres de campos que el backend
        datos_backend = datos.copy()
        
        # Manejar estado activo/inactivo
        if 'activo' in datos:
            if datos['activo'] is False:
                datos_backend['fecha_baja'] = date.today().isoformat()
            else:
                datos_backend['fecha_baja'] = None
        
        # Verificar que todos los campos requeridos por el backend estén presentes
        campos_requeridos_backend = ['nombre', 'email', 'telefono', 'direccion', 'documento']
        campos_faltantes_backend = []
        
        for campo in campos_requeridos_backend:
            if campo not in datos_backend or not datos_backend[campo]:
                campos_faltantes_backend.append(campo)
        
        if campos_faltantes_backend:
            mensaje_error = f"Faltan campos requeridos por el backend: {', '.join(campos_faltantes_backend)}"
            logger.error(f"🔴 {mensaje_error}")
            raise ValueError(mensaje_error)
            
        # Logging detallado para depuración
        logger.debug(f"[DIAGNÓSTICO] Datos transformados para backend: {datos_backend}")
        
        try:
            # Enviar la petición al servidor con el formato CorredorUpdate
            response = self.api.put(url, datos_backend)
            logger.info(f"🟢 Corredor actualizado correctamente: {id}")
            return response
        except Exception as e:
            logger.error(f"🔴 Error al actualizar corredor {id}: {str(e)}")
            # Intentar obtener más detalles del error
            error_detail = str(e)
            if hasattr(e, 'response') and e.response:
                try:
                    error_detail = e.response.json()
                    logger.error(f"🔴 Detalles del error: {error_detail}")
                except:
                    pass
            raise ValueError(f"Error al actualizar corredor: {error_detail}")

    
    def eliminar_corredor(self, id: int):
        """
        Elimina un corredor
        
        Args:
            id: ID del corredor a eliminar
        """
        self._current_operation = "eliminar"
        logger.debug(f"Eliminando corredor {id}")
        self.api.delete(f"api/v1/corredores/{id}/")
