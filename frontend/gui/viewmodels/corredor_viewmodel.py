"""
ViewModel específico para la gestión de corredores
"""

from typing import Optional, List
from datetime import date
import asyncio
from PyQt6.QtCore import pyqtSignal, QTimer
import logging
from frontend.gui.models.corredor import Corredor
from frontend.gui.repositories.corredor_repository import RepositorioCorredor
from frontend.gui.viewmodels.base_viewmodel import ViewModelBase
from frontend.gui.core.excepciones import ErrorValidacion, ErrorAPI

logger = logging.getLogger(__name__)


class CorredorViewModel(ViewModelBase[Corredor]):
    """
    ViewModel para gestionar la lógica de presentación de corredores
    """

    # Señales específicas para corredores
    corredor_creado = pyqtSignal(Corredor)
    corredor_actualizado = pyqtSignal(Corredor)
    corredor_eliminado = pyqtSignal(int)

    def __init__(self, repositorio: RepositorioCorredor):
        super().__init__(repositorio)
        self._repositorio: RepositorioCorredor = repositorio
        self._filtro_busqueda: str = ""
        self._timer_filtro = QTimer()
        self._timer_filtro.setSingleShot(True)
        self._timer_filtro.timeout.connect(self._aplicar_filtro_debounced)
        self._items_completos: List[Corredor] = []
        self._loop = asyncio.get_event_loop()

    async def _validar_datos_corredor(self, datos: dict) -> None:
        """Valida los datos del corredor antes de crear o actualizar"""
        errores = []

        # Mapeo de nombres de campos para mensajes en español
        nombres_campos = {
            "numero": "número",
            "nombres": "nombres",
            "apellidos": "apellidos",
            "documento": "documento",
            "direccion": "dirección",
            "localidad": "localidad",
            "mail": "correo electrónico",
        }

        # Validar campos requeridos
        campos_requeridos = [
            "numero",
            "nombres",
            "apellidos",
            "documento",
            "direccion",
            "localidad",
            "mail",
        ]

        # Validar número de corredor
        if "numero" in datos:
            try:
                numero = int(datos["numero"])
                if numero < 1000 or numero > 9999:
                    errores.append("El número de corredor debe estar entre 1000 y 9999")
            except (ValueError, TypeError):
                errores.append("El número de corredor debe ser un número entero")
        for campo in campos_requeridos:
            if not datos.get(campo):
                errores.append(f"El campo {nombres_campos[campo]} es obligatorio")
            elif campo == "mail" and "@" not in datos[campo]:
                errores.append("El correo electrónico debe tener un formato válido")

        # Verificar si ya existe un corredor con el mismo email o documento
        try:
            corredores = await self._repositorio.obtener_todos()
            if corredores:
                for corredor in corredores:
                    # No validar contra sí mismo en caso de actualización
                    if "numero" in datos and corredor.numero == datos["numero"]:
                        continue
                        
                    if corredor.mail.lower() == datos["mail"].lower():
                        errores.append(
                            f"Ya existe un corredor con el correo electrónico {datos['mail']}"
                        )
                    if corredor.documento == datos["documento"]:
                        errores.append(
                            f"Ya existe un corredor con el documento {datos['documento']}"
                        )
                    if corredor.numero == datos.get("numero"):
                        errores.append(
                            f"Ya existe un corredor con el número {datos['numero']}"
                        )
        except Exception as e:
            logger.error(f"Error al verificar datos existentes: {str(e)}")

        if errores:
            raise ErrorValidacion("\n".join(errores))

    async def crear_corredor(self, **datos) -> None:
        """
        Crea un nuevo corredor
        """
        try:
            # Validar datos
            await self._validar_datos_corredor(datos)

            # Asegurar que la fecha de alta esté presente
            if "fecha_alta" not in datos:
                datos["fecha_alta"] = date.today()

            # Crear el corredor
            nuevo_corredor = Corredor(**datos)
            corredor_creado = await self._repositorio.crear(nuevo_corredor)

            # Actualizar las listas
            self._items_completos.append(corredor_creado)
            self._aplicar_filtro_debounced()
            self.corredor_creado.emit(corredor_creado)
            logger.info(f"Corredor creado: {corredor_creado.nombre_completo}")

        except Exception as e:
            logger.error(f"Error al crear corredor: {str(e)}")
            raise

    async def actualizar_corredor(self, numero: int, **datos) -> None:
        """
        Actualiza un corredor existente
        """
        try:
            datos["numero"] = numero
            await self._validar_datos_corredor(datos)

            corredor = Corredor(**datos)
            corredor_actualizado = await self._repositorio.actualizar(corredor)

            # Actualizar en ambas listas
            self._actualizar_item_en_lista(corredor_actualizado, self._items_completos)
            self._aplicar_filtro_debounced()
            self.corredor_actualizado.emit(corredor_actualizado)
            logger.info(f"Corredor actualizado: {corredor_actualizado.nombre_completo}")
        except Exception as e:
            logger.error(f"Error al actualizar corredor: {str(e)}")
            raise

    async def eliminar_corredor(self, numero: int) -> None:
        """
        Elimina un corredor
        """
        try:
            resultado = await self._repositorio.eliminar(numero)
            if resultado:
                # Eliminar de ambas listas
                self._items_completos = [
                    c for c in self._items_completos if c.numero != numero
                ]
                self._aplicar_filtro_debounced()
                self.corredor_eliminado.emit(numero)
                logger.info(f"Corredor eliminado: número {numero}")
        except Exception as e:
            logger.error(f"Error al eliminar corredor: {str(e)}")
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
                corredor
                for corredor in self._items_completos
                if filtro in corredor.nombre_completo.lower()
                or filtro in corredor.mail.lower()
                or (corredor.documento and filtro in corredor.documento.lower())
                or (corredor.numero and str(corredor.numero).startswith(filtro))
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
            logger.info(f"Datos cargados: {len(self._items)} corredores")
        except Exception as e:
            mensaje_error = f"Error al cargar corredores: {str(e)}"
            logger.error(mensaje_error)
            self._establecer_error(mensaje_error)
        finally:
            self._establecer_cargando(False)
