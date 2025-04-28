import logging
from typing import List, Optional

from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from ..models.cliente import Cliente

# Configurar logging
logger = logging.getLogger(__name__)


class ClienteItemModel(QAbstractTableModel):
    """Modelo de datos para la vista de tabla de clientes"""

    # Definir las columnas del modelo
    COLUMNS = [
        "Nu00famero",     # numero_cliente
        "Nombre",      # nombres + apellidos
        "Documento",   # numero_documento
        "Telu00e9fono",    # telefonos o movil
        "Email",       # mail
        "Direcciu00f3n",   # direccion
        "Pu00f3lizas",     # polizas_count
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clientes: List[Cliente] = []
        
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.clientes)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        """Devuelve los datos para el rol especificado"""
        if not index.isValid() or not (0 <= index.row() < len(self.clientes)):
            return None

        cliente = self.clientes[index.row()]
        column = index.column()

        # Rol de visualizaciu00f3n (texto mostrado)
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:       # Nu00famero
                return str(cliente.numero_cliente)
            elif column == 1:     # Nombre completo
                return cliente.nombre_completo
            elif column == 2:     # Documento
                return cliente.numero_documento
            elif column == 3:     # Telu00e9fono
                return cliente.movil or cliente.telefonos
            elif column == 4:     # Email
                return cliente.mail
            elif column == 5:     # Direcciu00f3n
                return cliente.direccion
            elif column == 6:     # Pu00f3lizas
                return str(cliente.polizas_count)
            return ""
        
        # Rol de alineaciu00f3n
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            # Alinear nu00fameros a la derecha, texto a la izquierda
            if column in [0, 6]:  # nu00famero_cliente, polizas_count
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Rol personalizado para obtener el objeto completo
        elif role == Qt.ItemDataRole.UserRole:
            return cliente
        
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Devuelve los datos de encabezado"""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self.COLUMNS):
                return self.COLUMNS[section]
        return None

    def updateClientes(self, clientes: List[Cliente]):
        """Actualiza la lista de clientes en el modelo"""
        self.beginResetModel()
        self.clientes = clientes
        # Filter out clients with numero_cliente = 0 if it's a placeholder
        self.clientes = [c for c in clientes if c.numero_cliente != 0 or c.id]
        self.endResetModel()
        logger.info(f"Modelo actualizado con {len(self.clientes)} clientes")

    def addCliente(self, cliente: Cliente):
        """Agrega un cliente al modelo"""
        self.beginInsertRows(QModelIndex(), len(self.clientes), len(self.clientes))
        self.clientes.append(cliente)
        self.endInsertRows()
        logger.info(f"Cliente {cliente.nombre_completo} agregado al modelo")

    def updateCliente(self, cliente_actualizado: Cliente):
        """Actualiza un cliente existente en el modelo"""
        for i, cliente in enumerate(self.clientes):
            if cliente.id == cliente_actualizado.id:
                self.clientes[i] = cliente_actualizado
                # Notificar cambio en la fila completa
                self.dataChanged.emit(
                    self.index(i, 0),
                    self.index(i, self.columnCount() - 1)
                )
                logger.info(f"Cliente {cliente_actualizado.nombre_completo} actualizado en el modelo")
                return
        
        # Si no se encontru00f3, agregar como nuevo
        logger.warning(f"Cliente {cliente_actualizado.id} no encontrado para actualizar, agregando como nuevo")
        self.addCliente(cliente_actualizado)

    def removeCliente(self, cliente_id: str):
        """Elimina un cliente del modelo"""
        for i, cliente in enumerate(self.clientes):
            if cliente.id == cliente_id:
                self.beginRemoveRows(QModelIndex(), i, i)
                del self.clientes[i]
                self.endRemoveRows()
                logger.info(f"Cliente {cliente_id} eliminado del modelo")
                return
        
        logger.warning(f"Cliente {cliente_id} no encontrado para eliminar")
        
    def _crear_cliente_default(self) -> Cliente:
        """Crea un cliente con valores por defecto para agregar al modelo"""
        return Cliente(
            id="",
            numero_cliente=0,
            nombres="",
            apellidos="",
            tipo_documento_id=0,
            numero_documento="",
            direccion="",
            telefonos="",
            movil="",
            mail="",
            localidad=""
        )
