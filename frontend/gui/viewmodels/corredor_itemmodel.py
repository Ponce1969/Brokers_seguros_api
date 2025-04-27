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

    # Definir las columnas del modelo y sus títulos
    COLUMNS = [
        # No mostramos el ID técnico al usuario, solo se usa internamente
        ("numero", "Número"),  # Identificador de negocio visible para el usuario
        ("nombre", "Nombre"),
        ("email", "Email"),
        ("telefono", "Teléfono"),
        ("direccion", "Dirección"),
        ("documento", "Documento"),  # Documento de identidad
        ("tipo", "Tipo"),  # Tipo de corredor
        ("fecha_registro", "Fecha Registro"),
        ("activo", "Estado"),
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

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole) -> Any:
        """Retorna los datos del encabezado"""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.COLUMNS[section][1]
        return None

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> Any:
        """Retorna los datos para el índice y rol especificados"""
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            corredor = self._data[index.row()]
            column_name = self.COLUMNS[index.column()][0]
            
            if column_name == "activo":
                return "Activo" if getattr(corredor, column_name, True) else "Inactivo"
            
            return str(getattr(corredor, column_name, ""))

        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Retorna los flags para el índice especificado"""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def _crear_corredor_default(self) -> Corredor:
        """Crea un nuevo corredor con valores por defecto"""
        return Corredor(
            id=0,  # Clave primaria técnica (no visible para el usuario)
            numero=0,  # Identificador de negocio visible para el usuario
            email="",  # Email
            nombre="",  # Nombre completo del corredor
            telefono="",  # Teléfono
            direccion="",  # Dirección
            documento="",  # Documento de identidad
            tipo="corredor",  # Tipo de corredor
            fecha_registro=None,
            activo=True  # Estado activo/inactivo
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
        """Agrega un corredor al modelo"""
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

    def updateCorredores(self, corredores: list[Corredor]):
        """Actualiza la lista completa de corredores"""
        self.beginResetModel()
        self._data = corredores
        self.endResetModel()
