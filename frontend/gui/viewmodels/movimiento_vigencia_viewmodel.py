"""
ViewModel para la gestión de movimientos de vigencia
"""

from typing import List, Optional
from datetime import date
import logging
from PyQt6.QtCore import QObject, pyqtSignal

from ..models.movimiento_vigencia import MovimientoVigencia
from ..core.excepciones import ErrorAPI
from ..services.network_manager import NetworkManager

# Configurar logging
logger = logging.getLogger(__name__)


class MovimientoVigenciaViewModel(QObject):
    """
    ViewModel para manejar la lógica de negocio relacionada con movimientos de vigencia
    """

    # Señales
    movimiento_actualizado = pyqtSignal(MovimientoVigencia)
    movimientos_actualizados = pyqtSignal(list)
    error_ocurrido = pyqtSignal(str)

    def __init__(self):
        """Inicializa el ViewModel de movimientos de vigencia"""
        super().__init__()
        self.movimientos: List[MovimientoVigencia] = []
        self.movimiento_actual: Optional[MovimientoVigencia] = None
        
        # Inicializar NetworkManager
        self.api = NetworkManager()
        self.api.response_received.connect(self._handle_response)
        self.api.error_occurred.connect(self._handle_error)
        
        # Variable para rastrear la operación actual
        self._current_operation = None
        self._current_params = None

    def _handle_error(self, error_msg: str):
        """Maneja los errores del NetworkManager"""
        logger.error(f"Error en la operación {self._current_operation}: {error_msg}")
        self.error_ocurrido.emit(error_msg)

    def _handle_response(self, response):
        """Maneja las respuestas del servidor según la operación actual"""
        try:
            if self._current_operation == "cargar":
                if isinstance(response, list):
                    self._procesar_lista_movimientos(response)
                else:
                    logger.error("Respuesta inesperada al cargar movimientos")
                    self.error_ocurrido.emit("Formato de respuesta inválido")
            elif self._current_operation == "crear":
                if isinstance(response, dict):
                    self._procesar_movimiento_creado(response)
                else:
                    self.error_ocurrido.emit("Respuesta inválida al crear movimiento")
            elif self._current_operation == "actualizar":
                if isinstance(response, dict):
                    self._procesar_movimiento_actualizado(response)
                else:
                    self.error_ocurrido.emit("Respuesta inválida al actualizar movimiento")
        except Exception as e:
            logger.error(f"Error procesando respuesta: {e}")
            self.error_ocurrido.emit(str(e))
        finally:
            self._current_operation = None
            self._current_params = None

    def cargar_movimientos(self, corredor_id: Optional[int] = None) -> None:
        """
        Carga la lista de movimientos desde el servidor

        Args:
            corredor_id: ID del corredor para filtrar movimientos (opcional)
        """
        try:
            logger.info("📥 Cargando lista de movimientos...")
            self._current_operation = "cargar"
            endpoint = "api/v1/movimientos_vigencia/"
            if corredor_id:
                endpoint += f"?corredor_id={corredor_id}"
            self.api.get(endpoint)
        except Exception as e:
            mensaje = f"Error al cargar movimientos: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)

    def _procesar_lista_movimientos(self, response: List[dict]) -> None:
        """Procesa la lista de movimientos recibida del servidor"""
        try:
            self.movimientos = []
            for movimiento_data in response:
                try:
                    movimiento = MovimientoVigencia.from_dict(movimiento_data)
                    self.movimientos.append(movimiento)
                except Exception as e:
                    logger.error(f"Error al procesar movimiento: {e}")
            
            self.movimientos_actualizados.emit(self.movimientos)
            logger.info(f"✅ {len(self.movimientos)} movimientos cargados")
        except Exception as e:
            logger.error(f"Error procesando lista de movimientos: {e}")
            self.error_ocurrido.emit(f"Error al procesar los datos: {str(e)}")

    def crear_movimiento(self, datos: dict) -> None:
        """
        Crea un nuevo movimiento de vigencia

        Args:
            datos: Diccionario con los datos del movimiento
        """
        try:
            logger.info("📝 Creando nuevo movimiento...")
            self._current_operation = "crear"
            self.api.post("api/v1/movimientos_vigencia/", datos)
        except Exception as e:
            mensaje = f"Error al crear movimiento: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)

    def _procesar_movimiento_creado(self, response: dict) -> None:
        """Procesa la respuesta después de crear un movimiento"""
        try:
            movimiento = MovimientoVigencia.from_dict(response)
            self.movimientos.append(movimiento)
            self.movimiento_actualizado.emit(movimiento)
            self.movimientos_actualizados.emit(self.movimientos)
            logger.info("✅ Movimiento creado exitosamente")
        except Exception as e:
            logger.error(f"Error procesando movimiento creado: {e}")
            self.error_ocurrido.emit(str(e))

    def actualizar_movimiento(self, id: int, datos: dict) -> None:
        """
        Actualiza un movimiento existente

        Args:
            id: ID del movimiento a actualizar
            datos: Diccionario con los datos actualizados
        """
        try:
            logger.info(f"📝 Actualizando movimiento {id}...")
            self._current_operation = "actualizar"
            self.api.put(f"api/v1/movimientos_vigencia/{id}", datos)
        except Exception as e:
            mensaje = f"Error al actualizar movimiento: {str(e)}"
            logger.error(f"❌ {mensaje}")
            self.error_ocurrido.emit(mensaje)

    def _procesar_movimiento_actualizado(self, response: dict) -> None:
        """Procesa la respuesta después de actualizar un movimiento"""
        try:
            movimiento = MovimientoVigencia.from_dict(response)
            # Actualizar la lista local
            for i, m in enumerate(self.movimientos):
                if m.id == movimiento.id:
                    self.movimientos[i] = movimiento
                    break
            self.movimiento_actualizado.emit(movimiento)
            self.movimientos_actualizados.emit(self.movimientos)
            logger.info("✅ Movimiento actualizado exitosamente")
        except Exception as e:
            logger.error(f"Error procesando movimiento actualizado: {e}")
            self.error_ocurrido.emit(str(e))

    def buscar_movimiento(self, id: int) -> Optional[MovimientoVigencia]:
        """
        Busca un movimiento por su ID

        Args:
            id: ID del movimiento a buscar

        Returns:
            MovimientoVigencia: El movimiento encontrado o None
        """
        return next((m for m in self.movimientos if m.id == id), None)

    def filtrar_movimientos(self, texto: str) -> List[MovimientoVigencia]:
        """
        Filtra la lista de movimientos por texto

        Args:
            texto: Texto a buscar

        Returns:
            List[MovimientoVigencia]: Lista de movimientos que coinciden
        """
        texto = texto.lower()
        return [
            m
            for m in self.movimientos
            if texto in m.numero_poliza.lower()
            or texto in (m.cliente_nombre or "").lower()
            or texto in (m.corredor_nombre or "").lower()
            or texto in (m.tipo_seguro_nombre or "").lower()
        ]

    def get_movimientos_vigentes(self) -> List[MovimientoVigencia]:
        """
        Obtiene la lista de movimientos vigentes

        Returns:
            List[MovimientoVigencia]: Lista de movimientos vigentes
        """
        return [m for m in self.movimientos if m.vigente]

    def get_movimientos_por_vencer(self, dias: int = 30) -> List[MovimientoVigencia]:
        """
        Obtiene la lista de movimientos próximos a vencer

        Args:
            dias: Número de días para considerar próximo a vencer

        Returns:
            List[MovimientoVigencia]: Lista de movimientos próximos a vencer
        """
        hoy = date.today()
        return [
            m
            for m in self.movimientos
            if m.vigente and (m.fecha_vencimiento - hoy).days <= dias
        ]
