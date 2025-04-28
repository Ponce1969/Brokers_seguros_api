import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ClienteNetworkHandler:
    def __init__(self, api):
        self.api = api
        self._current_operation = None
        
        # Verificar si la API está disponible
        if self.api is None:
            logger.error("API no disponible en ClienteNetworkHandler")

    
    def crear_cliente(self, datos: dict):
        """
        Crea un nuevo cliente con los datos proporcionados, transformando
        los campos según el esquema esperado por el backend
        
        Args:
            datos: Diccionario con los datos del cliente
        """
        self._current_operation = "crear"
        logger.debug(f"Creando cliente: {datos}")
        
        if self.api is not None:
            # Transformar los datos de cliente para el backend
            # Según MEMORY: el backend espera nombres, apellidos, mail, telefonos, movil, localidad
            datos_transformados = datos.copy()
            
            # Asegurar que los campos obligatorios tengan valores válidos
            datos_transformados['tipo_documento_id'] = int(datos_transformados.get('tipo_documento_id', 1))
            datos_transformados['creado_por_id'] = int(datos_transformados.get('creado_por_id', 1))
            datos_transformados['modificado_por_id'] = int(datos_transformados.get('modificado_por_id', 1))
            
            # Asegurar que existe campo localidad (requerido por el backend)
            if 'localidad' not in datos_transformados or not datos_transformados['localidad']:
                datos_transformados['localidad'] = "Montevideo"  # Valor por defecto
                
            logger.info(f"Enviando datos de cliente transformados: {datos_transformados}")
            # Corregido: usar datos como argumento posicional, no como keyword 'payload'
            self.api.post("api/v1/clientes/", datos_transformados)
        else:
            logger.error("No se puede crear cliente: API no disponible")
    
    def actualizar_cliente(self, id: str, datos: dict):
        """
        Actualiza un cliente existente
        
        Args:
            id: ID del cliente a actualizar (UUID como cadena)
            datos: Diccionario con los datos a actualizar (formato frontend)
        """
        self._current_operation = "actualizar"
        # Asegurar que el ID siempre sea tratado como cadena (UUID)
        id_str = str(id).strip()
        logger.debug(f"Actualizando cliente con ID (UUID): {id_str}")
        
        if self.api is not None:
            # Transformar los datos similar a crear_cliente
            datos_transformados = datos.copy()
            
            # Asegurar tipos correctos para IDs
            if 'tipo_documento_id' in datos_transformados:
                datos_transformados['tipo_documento_id'] = int(datos_transformados.get('tipo_documento_id', 1))
            if 'modificado_por_id' in datos_transformados:
                datos_transformados['modificado_por_id'] = int(datos_transformados.get('modificado_por_id', 1))
            
            # Asegurar que existe campo localidad
            if 'localidad' not in datos_transformados or not datos_transformados['localidad']:
                datos_transformados['localidad'] = "Montevideo"
                
            logger.info(f"Enviando datos actualizados: {datos_transformados}")
            # Corregido: usar datos como argumento posicional, no como keyword 'payload'
            self.api.put(f"api/v1/clientes/{id_str}", datos_transformados)
        else:
            logger.error("No se puede actualizar cliente: API no disponible")
    
    def eliminar_cliente(self, id: str):
        """
        Elimina un cliente
        
        Args:
            id: ID del cliente a eliminar (UUID como cadena)
        """
        try:
            self._current_operation = "eliminar"
            # Asegurar que el ID siempre sea tratado como cadena (UUID)
            id_str = str(id).strip()
            logger.debug(f"Eliminando cliente con ID (UUID): {id_str}")
            
            if self.api is not None:
                self.api.delete(f"api/v1/clientes/{id_str}")
            else:
                logger.error("No se puede eliminar cliente: API no disponible")
        except Exception as e:
            logger.error(f"Error al eliminar cliente {id_str}: {e}")
            mensaje = f"Error al eliminar cliente: {str(e)}"
            logger.error(f"❌ {mensaje}")
            raise ValueError(mensaje)
    
    def obtener_cliente(self, id: str):
        """
        Obtiene un cliente por su ID
        
        Args:
            id: ID del cliente (UUID como cadena)
        """
        self._current_operation = "obtener"
        # Asegurar que el ID siempre sea tratado como cadena (UUID)
        id_str = str(id).strip()
        logger.debug(f"Obteniendo cliente con ID (UUID): {id_str}")
        if self.api is not None:
            self.api.get(f"api/v1/clientes/{id_str}")
        else:
            logger.error("No se puede obtener cliente: API no disponible")
    
    def listar_clientes(self):
        """Carga la lista completa de clientes"""
        self._current_operation = "cargar"  # Cambiado de 'listar' a 'cargar' para coincidir con ClienteViewModel
        logger.debug("Cargando lista de clientes")
        if self.api is not None:
            self.api.get("api/v1/clientes/")
        else:
            logger.error("No se puede cargar clientes: API no disponible")
    
    def listar_clientes_por_corredor(self, corredor_id: int):
        """
        Carga los clientes asociados a un corredor
        
        Args:
            corredor_id: ID del corredor
        """
        self._current_operation = "listar"
        logger.debug(f"Cargando clientes del corredor {corredor_id}")
        logger.warning("ATENCIÓN: Se está utilizando el endpoint de clientes por corredor en lugar del endpoint general de clientes")
        if self.api is not None:
            self.api.get(f"api/v1/corredores/{corredor_id}/clientes/")
        else:
            logger.error("No se puede listar clientes por corredor: API no disponible")
    
    def validar_datos_cliente(self, datos: dict) -> tuple[bool, str]:
        """
        Valida los datos del cliente antes de enviarlos al servidor
        
        Args:
            datos: Diccionario con los datos del cliente
            
        Returns:
            tuple: (válido, mensaje de error)
        """
        # Campos obligatorios según el esquema del backend
        campos_requeridos = [
            "nombres", "apellidos", "tipo_documento_id", 
            "numero_documento", "direccion"
        ]
        
        # Validación de campos requeridos
        for campo in campos_requeridos:
            if campo not in datos or not datos.get(campo):
                return False, f"El campo {campo} es requerido"
        
        # Validación más estricta para IDs (deben ser números positivos)
        campos_id = ["tipo_documento_id", "creado_por_id", "modificado_por_id"]
        for campo in campos_id:
            if campo in datos:
                try:
                    valor = int(datos[campo])
                    if valor <= 0:
                        return False, f"El {campo} debe ser un número positivo"
                except (ValueError, TypeError):
                    return False, f"El {campo} debe ser un número válido"
        
        # Validación para asegurar que al menos uno de los teléfonos esté presente
        if (("telefonos" not in datos or not datos.get("telefonos")) and
            ("movil" not in datos or not datos.get("movil"))):
            return False, "Debe proporcionar al menos un número de teléfono (fijo o móvil)"
        
        # Validación del correo electrónico (campo mail, no email según memoria)
        if "mail" in datos and datos["mail"]:
            if "@" not in datos["mail"] or "." not in datos["mail"]:
                return False, "El correo electrónico debe tener un formato válido (ejemplo@dominio.com)"
        
        # Si todas las validaciones pasan
        return True, ""
