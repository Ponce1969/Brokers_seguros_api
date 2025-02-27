"""
Modelo de datos para la tabla de corredores
"""

from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from typing import Any, Optional
import logging
from ..models.corredor import Corredor

# Configurar logging
logger = logging.getLogger(__name__)


class CorredorItemModel(QAbstractTableModel):
    """Modelo de datos para manejar corredores en widgets Qt"""

    # Definir las columnas del modelo
    COLUMNS = [
        "numero",
        "nombres",
        "apellidos",
        "documento",
        "direccion",
        "localidad",
        "telefonos",
        "movil",
        "mail",
        "observaciones",
        "matricula",
        "especializacion",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []

    def rowCount(self, parent=QModelIndex()) -> int:
        """Retorna el número de filas en el modelo"""
        return len(self._data)

    def columnCount(self, parent=QModelIndex()) -> int:
        """Retorna el número de columnas en el modelo"""
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> Any:
        """Retorna los datos para el índice y rol especificados"""
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            corredor = self._data[index.row()]
            column_name = self.COLUMNS[index.column()]
            return getattr(corredor, column_name, "")

        return None

    def setData(
        self, index: QModelIndex, value: Any, role=Qt.ItemDataRole.EditRole
    ) -> bool:
        """Establece los datos en el índice especificado"""
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        corredor = self._data[index.row()]
        column_name = self.COLUMNS[index.column()]

        try:
            setattr(corredor, column_name, value)
            self.dataChanged.emit(index, index, [role])
            return True
        except Exception:
            return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Retorna los flags para el índice especificado"""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
        )

    def _crear_corredor_default(self) -> Corredor:
        """Crea un nuevo corredor con valores por defecto para todos los campos requeridos.

        Este método se utiliza al insertar una nueva fila en el modelo, asegurando que el
        objeto Corredor se inicialice correctamente con valores temporales o vacíos.

        Returns:
            Corredor: Un nuevo objeto Corredor con valores por defecto:
                - id: vacío (se generará al guardar)
                - numero: 0 (se generará al guardar)
                - nombres: vacío (se llenará en el diálogo)
                - apellidos: vacío (se llenará en el diálogo)
                - documento: vacío (se llenará en el diálogo)
                - mail: vacío (se llenará en el diálogo)
                - matricula: vacío (se llenará en el diálogo)
                - activo: True (valor por defecto)
        """
        return Corredor(
            id="",  # Se generará al guardar
            numero=0,  # Se generará al guardar
            nombres="",
            apellidos="",
            documento="",
            mail="",
            matricula="",
            activo=True
        )

    def insertRow(self, row: int, parent=QModelIndex()) -> bool:
        """Inserta una nueva fila en el modelo"""
        self.beginInsertRows(parent, row, row)
        self._data.insert(row, self._crear_corredor_default())
        self.endInsertRows()
        return True

    def removeRow(self, row: int, parent=QModelIndex()) -> bool:
        """Elimina una fila del modelo"""
        self.beginRemoveRows(parent, row, row)
        del self._data[row]
        self.endRemoveRows()
        return True

    def addCorredor(self, corredor: Corredor) -> bool:
        """Agrega un corredor al modelo

        Args:
            corredor: El corredor a agregar

        Returns:
            bool: True si se agregó correctamente, False en caso contrario
        """
        try:
            logger.info(f"Agregando corredor al modelo: {corredor.__dict__}")
            row = len(self._data)
            self.beginInsertRows(QModelIndex(), row, row)
            self._data.append(corredor)
            self.endInsertRows()
            # Emitir dataChanged para toda la fila
            self.dataChanged.emit(
                self.index(row, 0),
                self.index(row, len(self.COLUMNS) - 1),
                [Qt.ItemDataRole.DisplayRole]
            )
            logger.info(f"Corredor agregado exitosamente. Total corredores: {len(self._data)}")
            return True
        except Exception as e:
            logger.error(f"Error al agregar corredor: {e}")
            return False

    def getCorredor(self, row: int) -> Optional[Corredor]:
        """Obtiene el corredor en la fila especificada"""
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def clear(self):
        """Limpia todos los datos del modelo"""
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()
