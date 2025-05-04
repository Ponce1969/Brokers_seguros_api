import logging
import re
from typing import Dict, Optional, List
from frontend.gui.utils.id_validator import is_uuid

logger = logging.getLogger(__name__)

# Constantes centralizadas para validación de clientes
CAMPOS_OBLIGATORIOS = [
    "nombres", "apellidos", "tipo_documento_id", "numero_documento",
    "fecha_nacimiento", "direccion", "localidad", "telefonos", "movil", "mail"
]
CAMPOS_OPCIONALES = ["observaciones", "creado_por_id", "modificado_por_id"]
CAMPOS_BACKEND = CAMPOS_OBLIGATORIOS + CAMPOS_OPCIONALES

class ClienteNetworkHandler:
    def __init__(self, api):
        self.api = api
        self._current_operation = None
        
        # Verificar si la API está disponible
        if self.api is None:
            logger.error("API no disponible en ClienteNetworkHandler")
            
    # Métodos privados para validaciones comunes
    def _validar_api(self):
        """Valida que la API esté disponible"""
        if self.api is None:
            error_msg = f"API no disponible durante operación '{self._current_operation}'"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
    def _validar_id_cliente(self, id: str):
        """
        Valida que el ID del cliente sea un UUID válido.

        NOTA PROFESIONAL:
        -------------------------------------------
        El backend SOLO acepta UUIDs (v4) como identificador de cliente.
        No se permite ningún otro formato (ni numérico ni string arbitrario).
        Si el backend cambia este contrato, actualizar aquí y en los tests.
        -------------------------------------------
        """
        if not is_uuid(id):
            error_msg = f"ID de cliente no válido: {id} (el backend SOLO acepta UUIDs)"
            logger.warning(error_msg)
            raise ValueError(error_msg)
            
    def _validar_campos_obligatorios_cliente(self, datos: dict):
        """
        Valida que el payload contenga todos los campos obligatorios
        requeridos por el backend.
        
        Args:
            datos: Diccionario con los datos del cliente (formato backend)
            
        Raises:
            ValueError: Si faltan campos obligatorios o tienen valores inválidos
        """
        # Lista de campos obligatorios según la documentación del backend
        # Nota: corredor_id no es obligatorio porque se puede determinar automáticamente
        # a partir del creado_por_id en el backend
        CAMPOS_OBLIGATORIOS = [
            'nombres', 'apellidos', 'tipo_documento_id', 'numero_documento',
            'fecha_nacimiento', 'direccion', 'localidad', 'telefonos', 'movil', 'mail'
        ]
        # Solo estos campos son obligatorios, el resto (como 'observaciones') es opcional
        campos_faltantes = []
        for campo in CAMPOS_OBLIGATORIOS:
            if campo not in datos or datos[campo] is None or str(datos[campo]).strip() == "":
                campos_faltantes.append(campo)
        if campos_faltantes:
            error_msg = f"Faltan campos obligatorios para el cliente: {', '.join(campos_faltantes)}"
            logger.warning(error_msg)
            raise ValueError(error_msg)
            
        # Validar formato y valores específicos
        if 'tipo_documento_id' in datos and not isinstance(datos['tipo_documento_id'], int):
            error_msg = f"El tipo de documento debe ser un número entero, no: {datos['tipo_documento_id']}"
            logger.warning(error_msg)
            raise ValueError(error_msg)
            
        # Verificar que la fecha de nacimiento tenga el formato correcto (yyyy-mm-dd)
        if 'fecha_nacimiento' in datos and datos['fecha_nacimiento']:
            fecha = str(datos['fecha_nacimiento'])
            if not (len(fecha) == 10 and fecha[4] == '-' and fecha[7] == '-'):
                error_msg = f"Formato de fecha de nacimiento inválido. Debe ser YYYY-MM-DD, no: {fecha}"
                logger.warning(error_msg)
                raise ValueError(error_msg)
            
    def _crear_payload_cliente(self, datos: dict) -> dict:
        """
        Crea un payload estricto y profesional para la creación de clientes,
        alineado 1:1 con el modelo ClienteCreate del backend.
        """
        logger.debug(f"Datos recibidos para crear cliente: {datos}")
        payload = {}
        errores = []
        for campo in CAMPOS_BACKEND:
            valor = datos.get(campo)
            if campo in ["tipo_documento_id", "creado_por_id", "modificado_por_id"]:
                if campo in CAMPOS_OBLIGATORIOS and (valor is None or str(valor).strip() == ""):
                    errores.append(f"El campo '{campo}' es obligatorio y debe ser un entero válido.")
                    continue
                if valor is not None and str(valor).strip() != "":
                    try:
                        payload[campo] = int(valor)
                    except (TypeError, ValueError):
                        errores.append(f"El campo '{campo}' debe ser un entero válido.")
            elif campo == "fecha_nacimiento":
                if campo in CAMPOS_OBLIGATORIOS:
                    if not valor or not isinstance(valor, str) or not valor.strip():
                        errores.append("El campo 'fecha_nacimiento' es obligatorio y no puede estar vacío.")
                    else:
                        try:
                            from datetime import datetime
                            datetime.strptime(valor.strip(), "%Y-%m-%d")
                            payload[campo] = valor.strip()
                        except Exception as e:
                            errores.append(f"El campo 'fecha_nacimiento' debe tener formato YYYY-MM-DD y ser una fecha válida. Error: {e}")
                elif valor:
                    try:
                        from datetime import datetime
                        datetime.strptime(str(valor).strip(), "%Y-%m-%d")
                        payload[campo] = str(valor).strip()
                    except Exception as e:
                        errores.append(f"El campo 'fecha_nacimiento' debe tener formato YYYY-MM-DD y ser una fecha válida. Error: {e}")
            elif campo == "mail":
                if campo in CAMPOS_OBLIGATORIOS:
                    if not valor or not isinstance(valor, str) or not valor.strip():
                        errores.append("El campo 'mail' es obligatorio y no puede estar vacío.")
                    elif "@" not in valor or "." not in valor.split("@")[-1]:
                        errores.append("El campo 'mail' debe ser un email válido (debe contener '@' y dominio).")
                    else:
                        payload[campo] = valor.strip()
                elif valor:
                    payload[campo] = str(valor).strip()
            elif campo in CAMPOS_OBLIGATORIOS:
                if valor is None or str(valor).strip() == "":
                    errores.append(f"El campo '{campo}' es obligatorio y no puede estar vacío.")
                else:
                    payload[campo] = str(valor).strip()
            else:  # Opcional
                if valor is not None:
                    payload[campo] = str(valor).strip()

        if errores:
            logger.error("Errores en los datos del cliente: " + '; '.join(errores))
            raise ValueError('; '.join(errores))

        logger.info(f"Payload para crear cliente armado correctamente: {payload}")
        return payload


    
    def crear_cliente(self, datos: dict):
        """
        Crea un nuevo cliente en el backend
        
        Args:
            datos: Diccionario con los datos del cliente
        """
        self._current_operation = "crear"
        logger.debug("Creando cliente")
        
        try:
            # Validar que la API esté disponible
            self._validar_api()
            
            # Log con los datos recibidos para depuración
            logger.debug(f"Datos recibidos para crear cliente: {datos}")
            
            # Verificar si tenemos un corredor_id
            if 'corredor_id' not in datos or datos['corredor_id'] is None:
                logger.warning("No se proporcionó corredor_id para la asociación del cliente")
                # Nota: seguimos adelante porque el backend intentará asociarlo automáticamente
                # basado en el usuario actual (creado_por_id)
            
            # Crear payload con datos serializables y campos requeridos
            payload = self._crear_payload_cliente(datos)
            
            # Log de los campos después de la transformación para depuración
            logger.debug(f"Payload después de transformación: {payload}")
            
            # Validar campos obligatorios antes de enviar
            self._validar_campos_obligatorios_cliente(payload)
                
            # Enviar solicitud al servidor
            logger.info(f"Enviando solicitud para crear cliente: {payload}")
            result = self.api.post("api/v1/clientes/", payload)
            return result
        except ValueError as e:
            # Error de validación
            mensaje = f"Error de validación al crear cliente: {str(e)}"
            logger.error(mensaje)
            raise ValueError(mensaje)
        except Exception as e:
            raise ValueError(str(e))
                
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def actualizar_cliente(self, id: str, datos: dict):
        """
        Actualiza un cliente existente
        
        Args:
            id: ID del cliente a actualizar
            datos: Diccionario con los datos del cliente
        """
        self._current_operation = "actualizar"
        logger.debug(f"Actualizando cliente ID: {id}")
        
        try:
            # Validaciones
            self._validar_api()
            self._validar_id_cliente(id)
                
            # Crear payload con datos serializables y campos requeridos
            payload = self._crear_payload_cliente(datos)
            
            # Validar campos obligatorios antes de enviar
            self._validar_campos_obligatorios_cliente(payload)
            
            # Enviar solicitud al servidor
            logger.info(f"Enviando solicitud para actualizar cliente {id}")
            self.api.put(f"api/v1/clientes/{id}/", payload)
        except ValueError as e:
            # Error de validación
            mensaje = f"Error de validación al actualizar cliente: {str(e)}"
            logger.error(mensaje)
            raise ValueError(mensaje)
        except Exception as e:
            mensaje = f"Error al actualizar cliente: {str(e)}"
            logger.error(mensaje)
            raise ValueError(mensaje)
    
    def _buscar_id_numerico_cliente(self, uuid: str) -> int:
        """
        Busca el ID numérico correspondiente a un UUID de cliente.
        Esta es una solución temporal para manejar la inconsistencia del backend.
        
        Args:
            uuid: UUID del cliente como string
            
        Returns:
            int: ID numérico del cliente si se encuentra, o None si no se encuentra
            
        Raises:
            ValueError: Si no se encuentra un ID numérico para el UUID proporcionado
        """
        logger.info(f"Buscando ID numérico para cliente con UUID: {uuid}")
        
        # Para encontrar el ID numérico, debemos primero obtener la lista completa de clientes
        # y buscar el cliente con el UUID proporcionado
        self._current_operation = "buscar_id_numerico"
        
        try:
            # Solicitar la lista completa de clientes al backend
            # Usamos una solicitud síncrona para esperar la respuesta
            response = self.api.get_sync("api/v1/clientes/")
            
            if response and isinstance(response, list):
                # Buscar en la respuesta el cliente con el UUID dado
                for cliente in response:
                    # Verificar que el UUID coincida
                    if 'id' in cliente and cliente['id'] == uuid:
                        # Buscar un campo que contenga el ID numérico
                        # Las posibilidades son: 'numero_cliente' o algún otro campo
                        if 'numero_cliente' in cliente and cliente['numero_cliente']:
                            logger.info(f"Encontrado ID numérico {cliente['numero_cliente']} para UUID {uuid}")
                            return int(cliente['numero_cliente'])
            
            # Si llegamos aquí, no encontramos el ID numérico
            raise ValueError(f"No se encontró un ID numérico para el cliente con UUID: {uuid}")
        except Exception as e:
            logger.error(f"Error buscando ID numérico para cliente con UUID {uuid}: {e}")
            raise ValueError(f"Error buscando ID numérico: {str(e)}")
            
    def eliminar_cliente(self, id):
        """
        Elimina un cliente existente
        
        Args:
            id: ID del cliente a eliminar (UUID)
        """
        self._current_operation = "eliminar"
        logger.debug(f"Eliminando cliente ID: {id}")
        
        try:
            # Validaciones
            self._validar_api()
            self._validar_id_cliente(id)
            
            # PROBLEMA: El endpoint DELETE del backend espera IDs numéricos, pero
            # los clientes tienen UUIDs. Esta es una inconsistencia del backend.
            # Solución: Intentar primero con el UUID, y si falla, buscar el ID numérico
            try:
                # Primer intento: usar el UUID directamente (por si el backend ya fue actualizado)
                logger.info(f"Intentando eliminar cliente usando UUID: {id}")
                self.api.delete(f"api/v1/clientes/{id}/")
                logger.info(f"Cliente eliminado exitosamente usando UUID")
                return  # Si llegamos aquí, la eliminación fue exitosa
            except Exception as e:
                # Si el error contiene un mensaje sobre parsing de entero, es el problema de inconsistencia
                error_str = str(e)
                if "int_parsing" in error_str or "integer" in error_str.lower():
                    logger.warning(f"Error al eliminar con UUID, intentando con ID numérico: {error_str}")
                    
                    # Segundo intento: buscar el ID numérico correspondiente al UUID
                    try:
                        id_numerico = self._buscar_id_numerico_cliente(id)
                        logger.info(f"Intentando eliminar cliente usando ID numérico: {id_numerico}")
                        self.api.delete(f"api/v1/clientes/{id_numerico}/")
                        logger.info(f"Cliente eliminado exitosamente usando ID numérico")
                        return  # Si llegamos aquí, la eliminación fue exitosa
                    except Exception as e2:
                        raise ValueError(f"Error al eliminar cliente usando ID numérico: {str(e2)}")
                else:
                    # Si el error no está relacionado con el parsing de entero, propagar el error original
                    raise e
        except Exception as e:
            mensaje = f"Error al eliminar cliente: {str(e)}"
            logger.error(mensaje)
            raise ValueError(mensaje)
    
    def obtener_cliente(self, id: str):
        """
        Obtiene un cliente por su ID
        
        Args:
            id: ID del cliente
        """
        self._current_operation = "obtener"
        logger.debug(f"Obteniendo cliente ID: {id}")
        
        try:
            # Validaciones
            self._validar_api()
            self._validar_id_cliente(id)
            
            # Enviar solicitud al servidor
            logger.info(f"Enviando solicitud para obtener cliente {id}")
            self.api.get(f"api/v1/clientes/{id}/")
        except Exception as e:
            mensaje = f"Error al obtener cliente: {str(e)}"
            logger.error(mensaje)
            raise ValueError(mensaje)
    
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
