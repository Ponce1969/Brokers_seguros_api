"""
ViewModel base que implementa funcionalidad común para todos los ViewModels
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import Generic, TypeVar, List, Optional
import logging
from frontend.gui.repositories.base_repository import RepositorioBase
from frontend.gui.core.excepciones import ErrorAPI, ErrorValidacion

T = TypeVar("T")
logger = logging.getLogger(__name__)


class ViewModelBase(QObject, Generic[T]):
    """
    Clase base para todos los ViewModels que proporciona funcionalidad común
    """

    # Señales para notificar cambios en los datos
    datos_actualizados = pyqtSignal()  # Cuando los datos cambian
    error_ocurrido = pyqtSignal(str)  # Cuando ocurre un error
    cargando = pyqtSignal(bool)  # Cuando se está cargando datos

    def __init__(self, repositorio: RepositorioBase[T]):
        super().__init__()
        self._repositorio = repositorio
        self._items: List[T] = []
        self._esta_cargando = False
        self._error = ""
        self._item_seleccionado: Optional[T] = None

    @property
    def items(self) -> List[T]:
        """Lista de items cargados"""
        return self._items

    @property
    def esta_cargando(self) -> bool:
        """Indica si se están cargando datos"""
        return self._esta_cargando

    @property
    def error(self) -> str:
        """Último error ocurrido"""
        return self._error

    @property
    def item_seleccionado(self) -> Optional[T]:
        """Item actualmente seleccionado"""
        return self._item_seleccionado

    def cargar_datos(self) -> None:
        """Carga todos los items desde el repositorio"""
        try:
            self._establecer_cargando(True)
            self._items = self._repositorio.obtener_todos()
            self._limpiar_error()
            self.datos_actualizados.emit()
            logger.info(f"Datos cargados: {len(self._items)} items")
        except (ErrorAPI, ErrorValidacion) as e:
            mensaje_error = f"Error al cargar datos: {str(e)}"
            logger.error(mensaje_error)
            self._establecer_error(mensaje_error)
        finally:
            self._establecer_cargando(False)

    def seleccionar_item(self, item: Optional[T]) -> None:
        """Selecciona un item"""
        self._item_seleccionado = item
        self.datos_actualizados.emit()
        if item:
            logger.debug(f"Item seleccionado: {str(item)}")
        else:
            logger.debug("Selección limpiada")

    def crear_item(self, item: T) -> None:
        """Crea un nuevo item"""
        try:
            self._establecer_cargando(True)
            item_creado = self._repositorio.crear(item)
            self._items.append(item_creado)
            self._limpiar_error()
            self.datos_actualizados.emit()
            logger.info(f"Item creado: {str(item_creado)}")
        except (ErrorAPI, ErrorValidacion) as e:
            mensaje_error = f"Error al crear item: {str(e)}"
            logger.error(mensaje_error)
            self._establecer_error(mensaje_error)
        finally:
            self._establecer_cargando(False)

    def actualizar_item(self, item: T) -> None:
        """Actualiza un item existente"""
        try:
            self._establecer_cargando(True)
            item_actualizado = self._repositorio.actualizar(item)
            self._actualizar_item_en_lista(item_actualizado, self._items)
            self._limpiar_error()
            self.datos_actualizados.emit()
            logger.info(f"Item actualizado: {str(item_actualizado)}")
        except (ErrorAPI, ErrorValidacion) as e:
            mensaje_error = f"Error al actualizar item: {str(e)}"
            logger.error(mensaje_error)
            self._establecer_error(mensaje_error)
        finally:
            self._establecer_cargando(False)

    def eliminar_item(self, id: int) -> None:
        """Elimina un item por su ID"""
        try:
            self._establecer_cargando(True)
            if self._repositorio.eliminar(id):
                self._items = [
                    item for item in self._items if getattr(item, "id", None) != id
                ]
                self._limpiar_error()
                self.datos_actualizados.emit()
                logger.info(f"Item eliminado: ID {id}")
        except (ErrorAPI, ErrorValidacion) as e:
            mensaje_error = f"Error al eliminar item: {str(e)}"
            logger.error(mensaje_error)
            self._establecer_error(mensaje_error)
        finally:
            self._establecer_cargando(False)

    def _establecer_cargando(self, valor: bool) -> None:
        """Establece el estado de carga y emite la señal correspondiente"""
        if self._esta_cargando != valor:
            self._esta_cargando = valor
            self.cargando.emit(valor)
            logger.debug(f"Estado de carga: {'Cargando' if valor else 'Completado'}")

    def _establecer_error(self, mensaje: str) -> None:
        """Establece el mensaje de error y emite la señal correspondiente"""
        self._error = mensaje
        self.error_ocurrido.emit(mensaje)

    def _limpiar_error(self) -> None:
        """Limpia el mensaje de error actual"""
        if self._error:
            self._error = ""

    def _actualizar_item_en_lista(self, item_actualizado: T, lista: List[T]) -> None:
        """Actualiza un item en la lista especificada"""
        for i, item in enumerate(lista):
            if getattr(item, "id", None) == getattr(item_actualizado, "id", None):
                lista[i] = item_actualizado
                break
