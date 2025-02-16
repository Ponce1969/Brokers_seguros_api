"""
ViewModel específico para la gestión de usuarios/corredores
"""
from typing import Optional, List, Dict, Any
from datetime import date
import asyncio
from PyQt6.QtCore import pyqtSignal, QTimer
import logging
from frontend.gui.models.usuario import Usuario
from frontend.gui.repositories.usuario_repository import RepositorioUsuario
from frontend.gui.viewmodels.base_viewmodel import ViewModelBase
from frontend.gui.core.excepciones import ErrorValidacion, ErrorAPI

logger = logging.getLogger(__name__)

class UsuarioViewModel(ViewModelBase[Usuario]):
    """
    ViewModel para gestionar la lógica de presentación de usuarios/corredores
    """
    # Señales específicas para usuarios
    usuario_creado = pyqtSignal(Usuario)
    usuario_actualizado = pyqtSignal(Usuario)
    usuario_eliminado = pyqtSignal(int)

    def __init__(self, repositorio: RepositorioUsuario):
        super().__init__(repositorio)
        self._repositorio: RepositorioUsuario = repositorio
        self._filtro_busqueda: str = ""
        self._token: Optional[str] = None
        self._timer_filtro = QTimer()
        self._timer_filtro.setSingleShot(True)
        self._timer_filtro.timeout.connect(self._aplicar_filtro_debounced)
        self._items_completos: List[Usuario] = []
        self._loop = asyncio.get_event_loop()

    async def _validar_datos_usuario(self, datos: Dict[str, Any]) -> None:
        """Valida los datos del usuario antes de crear o actualizar"""
        errores = []
        
        # Mapeo de nombres de campos para mensajes en español
        nombres_campos = {
            'username': 'nombre de usuario',
            'email': 'correo electrónico',
            'nombres': 'nombres',
            'apellidos': 'apellidos',
            'documento': 'documento',
            'direccion': 'dirección',
            'localidad': 'localidad',
            'telefono': 'teléfono',
            'movil': 'móvil'
        }

        # Validar campos requeridos
        campos_requeridos = [
            'username', 'email', 'nombres', 'apellidos', 
            'documento', 'direccion', 'localidad', 
            'telefono', 'movil'
        ]
        for campo in campos_requeridos:
            if not datos.get(campo):
                errores.append(f"El campo {nombres_campos[campo]} es obligatorio")
            elif campo == 'email' and '@' not in datos[campo]:
                errores.append("El correo electrónico debe tener un formato válido")

        # Validar comisión
        comision = datos.get('comision_porcentaje', 0)
        if not isinstance(comision, (int, float)):
            errores.append("La comisión debe ser un valor numérico")
        elif comision < 0 or comision > 100:
            errores.append("La comisión debe estar entre 0 y 100 por ciento")

        email_lower = datos['email'].lower()
        
        try:
            # Verificar usuarios existentes
            usuarios = await self._repositorio.servicio_api.get("usuarios/")
            if usuarios:
                logger.info(f"Usuarios encontrados: {len(usuarios)}")
                if any(u.get('email', '').lower() == email_lower for u in usuarios):
                    errores.append(
                        f"Ya existe un usuario registrado con el correo electrónico {datos['email']}. "
                        "Por favor, utilice otro correo electrónico."
                    )

            # Verificar corredores existentes
            corredores = await self._repositorio.servicio_api.get("corredores/")
            if corredores:
                logger.info(f"Corredores encontrados: {len(corredores)}")
                
                # Verificar email en corredores
                if any(c.get('mail', '').lower() == email_lower for c in corredores):
                    errores.append(
                        f"Ya existe un corredor registrado con el correo electrónico {datos['email']}. "
                        "Por favor, utilice otro correo electrónico."
                    )

                # Verificar documento en corredores
                if any(c.get('documento') == datos['documento'] for c in corredores):
                    errores.append(
                        f"Ya existe un corredor registrado con el documento {datos['documento']}. "
                        "Por favor, verifique el número de documento."
                    )

        except Exception as e:
            logger.error(f"Error al verificar datos existentes: {str(e)}")
            logger.error(f"Detalles del error: {e.__class__.__name__}: {str(e)}")

        if errores:
            raise ErrorValidacion("\n".join(errores))

    def _limpiar_datos(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Limpia y normaliza los datos de entrada"""
        datos_limpios = datos.copy()
        
        # Convertir email a minúsculas y eliminar espacios
        if 'email' in datos_limpios:
            datos_limpios['email'] = datos_limpios['email'].lower().strip()
        
        # Limpiar espacios en blanco de los campos de texto
        campos_texto = [
            'username', 'nombres', 'apellidos', 'direccion', 
            'localidad', 'telefono', 'movil', 'documento',
            'matricula', 'especializacion'
        ]
        for campo in campos_texto:
            if campo in datos_limpios:
                datos_limpios[campo] = datos_limpios[campo].strip()
        
        return datos_limpios

    def _preparar_datos_corredor(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara los datos para crear un corredor"""
        datos_limpios = self._limpiar_datos(datos)
        
        return {
            "nombres": datos_limpios['nombres'],
            "apellidos": datos_limpios['apellidos'],
            "documento": datos_limpios['documento'],
            "direccion": datos_limpios['direccion'],
            "localidad": datos_limpios['localidad'],
            "telefonos": datos_limpios.get('telefono', ""),
            "movil": datos_limpios.get('movil', datos_limpios.get('telefono', "")),
            "mail": datos_limpios['email'],
            "fecha_alta": datos_limpios.get('fecha_alta', date.today().isoformat()),
            "fecha_baja": datos_limpios.get('fecha_baja'),
            "observaciones": datos_limpios.get('observaciones', "Corredor creado desde la interfaz de usuario"),
            "matricula": datos_limpios.get('matricula'),
            "especializacion": datos_limpios.get('especializacion')
        }

    async def _limpiar_corredor(self, corredor: dict) -> None:
        """Intenta eliminar un corredor creado en caso de error"""
        if corredor and 'numero' in corredor:
            try:
                await self._repositorio.servicio_api.delete(f"corredores/{corredor['numero']}")
                logger.info(f"Corredor {corredor['numero']} eliminado después de fallo en creación de usuario")
            except Exception as cleanup_error:
                logger.error(f"Error al limpiar corredor: {str(cleanup_error)}")

    async def crear_usuario(self, **datos) -> None:
        """
        Crea un nuevo usuario/corredor
        """
        corredor = None
        try:
            # Limpiar datos de entrada
            datos = self._limpiar_datos(datos)
            logger.info(f"Datos limpios para crear corredor/usuario: {datos}")
            
            # Ejecutar validación asíncrona
            logger.info("Iniciando validación de datos...")
            await self._validar_datos_usuario(datos)
            logger.info("Validación de datos completada exitosamente")
            
            logger.info(f"Iniciando creación de corredor/usuario con email: {datos['email']}")
            logger.info("Datos del corredor a crear:")
            logger.info(f"- Email: {datos['email']}")
            logger.info(f"- Documento: {datos['documento']}")
            logger.info(f"- Nombre completo: {datos['nombres']} {datos['apellidos']}")
            
            # Extraer la contraseña de los datos antes de crear el usuario
            password = datos.pop('password', None)
            if not password:
                raise ErrorValidacion("La contraseña es requerida para nuevos usuarios")

            # 1. Primero crear el corredor
            datos_corredor = self._preparar_datos_corredor(datos)
            logger.info(f"Creando corredor con datos: {datos_corredor}")
            
            try:
                logger.info("Intentando crear corredor en la base de datos...")
                corredor = await self._repositorio.crear_corredor(datos_corredor)
                logger.info(f"Corredor creado exitosamente: {corredor}")
                logger.info(f"Número de corredor asignado: {corredor.get('numero', 'No asignado')}")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error al crear corredor: {error_msg}")
                logger.error(f"Tipo de error: {type(e).__name__}")
                
                if "duplicate key value violates unique constraint" in error_msg:
                    if "corredores_mail_key" in error_msg:
                        raise ErrorValidacion(
                            f"Ya existe un corredor con el email {datos['email']}. "
                            "Por favor, utilice un email diferente."
                        )
                    elif "corredores_documento_key" in error_msg:
                        raise ErrorValidacion(
                            f"Ya existe un corredor con el documento {datos['documento']}. "
                            "Por favor, verifique el número de documento."
                        )
                    else:
                        raise ErrorValidacion(
                            "Error al crear el corredor: Ya existe un registro con los mismos datos. "
                            "Por favor, verifique la información ingresada."
                        )
                
                raise ErrorValidacion(
                    f"Error al crear el corredor: {error_msg}. "
                    "Por favor, contacte al soporte técnico si el problema persiste."
                )
            
            # Verificar que el corredor se creó correctamente
            if not corredor:
                raise ErrorValidacion("No se pudo crear el corredor")
            
            # Obtener el número de corredor asignado por el backend
            if 'numero' not in corredor:
                raise ErrorValidacion("El servidor no devolvió el número de corredor")
            
            # Asignar el número de corredor a los datos del usuario
            datos['corredor_numero'] = corredor['numero']
            logger.info(f"Número de corredor asignado: {corredor['numero']}")
            
            # 2. Luego crear el usuario asociado
            nuevo_usuario = Usuario(**datos)
            usuario_creado = await self._repositorio.crear(nuevo_usuario, password=password)
            
            self._items_completos.append(usuario_creado)
            self._aplicar_filtro_debounced()
            self.usuario_creado.emit(usuario_creado)
            logger.info(f"Usuario y corredor creados: {usuario_creado.email}")

        except ErrorAPI as e:
            logger.error(f"Error en el proceso de creación: {str(e)}")
            await self._limpiar_corredor(corredor)
            
            error_msg = str(e)
            if "ForeignKeyViolationError" in error_msg:
                raise ErrorValidacion(
                    "Error al crear el usuario: Hubo un problema al vincular el usuario con el corredor. "
                    "Por favor, intente nuevamente o contacte al soporte técnico."
                )
            elif "duplicate key value violates unique constraint" in error_msg:
                if "usuarios_email_key" in error_msg:
                    raise ErrorValidacion(
                        f"Ya existe un usuario con el email {datos['email']}. "
                        "Por favor, utilice un email diferente."
                    )
                elif "usuarios_username_key" in error_msg:
                    raise ErrorValidacion(
                        f"Ya existe un usuario con el nombre de usuario {datos['username']}. "
                        "Por favor, elija otro nombre de usuario."
                    )
            raise ErrorValidacion(f"Error al crear el usuario: {error_msg}")

        except Exception as e:
            logger.error(f"Error inesperado en el proceso de creación: {str(e)}")
            await self._limpiar_corredor(corredor)
            raise ErrorValidacion(
                "Error inesperado al crear el usuario. "
                "Por favor, verifique los datos e intente nuevamente. "
                "Si el problema persiste, contacte al soporte técnico."
            )

    async def actualizar_usuario(self, id: int, **datos) -> None:
        """
        Actualiza un usuario/corredor existente
        """
        try:
            datos['id'] = id
            await self._validar_datos_usuario(datos)
            
            # Remover la contraseña de los datos de actualización
            datos.pop('password', None)
            
            usuario = Usuario(**datos)
            usuario_actualizado = await self._repositorio.actualizar(usuario)
            
            # Actualizar en ambas listas
            self._actualizar_item_en_lista(usuario_actualizado, self._items_completos)
            self._aplicar_filtro_debounced()
            self.usuario_actualizado.emit(usuario_actualizado)
            logger.info(f"Usuario actualizado: {usuario_actualizado.email}")
        except Exception as e:
            mensaje_error = f"Error al actualizar usuario: {str(e)}"
            logger.error(mensaje_error)
            self._establecer_error(mensaje_error)
            raise

    async def eliminar_usuario(self, id: int) -> None:
        """
        Elimina un usuario/corredor
        """
        try:
            resultado = await self._repositorio.eliminar(id)
            if resultado:
                # Eliminar de ambas listas
                self._items_completos = [u for u in self._items_completos if u.id != id]
                self._aplicar_filtro_debounced()
                self.usuario_eliminado.emit(id)
                logger.info(f"Usuario eliminado: ID {id}")
        except Exception as e:
            mensaje_error = f"Error al eliminar usuario: {str(e)}"
            logger.error(mensaje_error)
            self._establecer_error(mensaje_error)
            raise

    @property
    def filtro_busqueda(self) -> str:
        """Obtiene el filtro de búsqueda actual"""
        return self._filtro_busqueda

    @filtro_busqueda.setter
    def filtro_busqueda(self, valor: str) -> None:
        """Establece el filtro de búsqueda y programa la actualización"""
        self._filtro_busqueda = valor
        self._timer_filtro.start(300)  # 300ms debounce

    def _aplicar_filtro_debounced(self) -> None:
        """Aplica el filtro después del debounce"""
        if not self._filtro_busqueda:
            self._items = self._items_completos.copy()
        else:
            filtro = self._filtro_busqueda.lower()
            self._items = [
                usuario for usuario in self._items_completos
                if filtro in usuario.nombre_completo.lower() or
                   filtro in usuario.email.lower() or
                   (usuario.corredor_numero and 
                    str(usuario.corredor_numero).startswith(filtro))
            ]
        self.datos_actualizados.emit()

    async def cargar_datos(self) -> None:
        """Carga todos los items desde el repositorio"""
        try:
            self._establecer_cargando(True)
            self._items_completos = await self._repositorio.obtener_todos()
            self._items = self._items_completos.copy()
            self._limpiar_error()
            self.datos_actualizados.emit()
            logger.info(f"Datos cargados: {len(self._items)} usuarios")
        except Exception as e:
            mensaje_error = f"Error al cargar usuarios: {str(e)}"
            logger.error(mensaje_error)
            self._establecer_error(mensaje_error)
        finally:
            self._establecer_cargando(False)

    def set_token(self, token: str) -> None:
        """Establece el token de autenticación"""
        self._token = token
