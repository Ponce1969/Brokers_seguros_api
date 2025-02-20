"""
Vista para la gestión de movimientos de vigencia
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QComboBox,
)
from PyQt6.QtCore import Qt
import logging
from datetime import date
from ..viewmodels.movimiento_vigencia_viewmodel import MovimientoVigenciaViewModel

# Configurar logging
logger = logging.getLogger(__name__)

class VistaMovimientosVigencia(QWidget):
    """Vista principal para la gestión de movimientos de vigencia"""

    def __init__(self, viewmodel: MovimientoVigenciaViewModel, es_admin: bool = False):
        super().__init__()
        self.viewmodel = viewmodel
        self.es_admin = es_admin
        self.init_ui()
        self.conectar_senales()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Título
        titulo = QLabel("Gestión de Movimientos de Vigencia")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        # Barra de herramientas superior
        toolbar_superior = QHBoxLayout()
        
        # Filtro de estado
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Todos", "Vigentes", "Por Vencer", "Vencidos"])
        self.combo_estado.currentTextChanged.connect(self.filtrar_movimientos)
        toolbar_superior.addWidget(QLabel("Estado:"))
        toolbar_superior.addWidget(self.combo_estado)
        
        toolbar_superior.addStretch()
        
        # Búsqueda
        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText("Buscar movimiento...")
        self.busqueda.textChanged.connect(self.filtrar_movimientos)
        toolbar_superior.addWidget(self.busqueda)

        # Botón nuevo movimiento
        self.btn_nuevo = QPushButton("Nuevo Movimiento")
        self.btn_nuevo.clicked.connect(self.mostrar_dialogo_nuevo)
        toolbar_superior.addWidget(self.btn_nuevo)

        layout.addLayout(toolbar_superior)

        # Tabla de movimientos
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(10)
        self.tabla.setHorizontalHeaderLabels([
            "N° Póliza",
            "Cliente",
            "Corredor",
            "Tipo Seguro",
            "Fecha Inicio",
            "Fecha Venc.",
            "Prima",
            "Estado",
            "Días Rest.",
            "Acciones"
        ])
        
        # Configurar la tabla
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)  # Acciones
        self.tabla.setColumnWidth(9, 100)
        
        layout.addWidget(self.tabla)

        # Barra de estado
        barra_estado = QHBoxLayout()
        
        # Totales
        self.lbl_total = QLabel("Total: 0 movimientos")
        barra_estado.addWidget(self.lbl_total)
        
        barra_estado.addStretch()
        
        # Por vencer
        self.lbl_por_vencer = QLabel("Por vencer: 0")
        self.lbl_por_vencer.setStyleSheet("color: #ffc107;")  # Amarillo warning
        barra_estado.addWidget(self.lbl_por_vencer)
        
        # Vencidos
        self.lbl_vencidos = QLabel("Vencidos: 0")
        self.lbl_vencidos.setStyleSheet("color: #dc3545;")  # Rojo danger
        barra_estado.addWidget(self.lbl_vencidos)
        
        layout.addLayout(barra_estado)

    def conectar_senales(self):
        """Conecta las señales del ViewModel"""
        self.viewmodel.movimientos_actualizados.connect(self.actualizar_tabla)
        self.viewmodel.error_ocurrido.connect(self.mostrar_error)

    def actualizar_tabla(self, movimientos):
        """Actualiza la tabla con la lista de movimientos"""
        self.tabla.setRowCount(len(movimientos))
        
        hoy = date.today()
        vigentes = 0
        por_vencer = 0
        vencidos = 0
        
        for i, mov in enumerate(movimientos):
            self.tabla.setItem(i, 0, QTableWidgetItem(mov.numero_poliza))
            self.tabla.setItem(i, 1, QTableWidgetItem(mov.cliente_nombre))
            self.tabla.setItem(i, 2, QTableWidgetItem(mov.corredor_nombre))
            self.tabla.setItem(i, 3, QTableWidgetItem(mov.tipo_seguro_nombre))
            self.tabla.setItem(i, 4, QTableWidgetItem(mov.fecha_inicio.strftime("%d/%m/%Y")))
            self.tabla.setItem(i, 5, QTableWidgetItem(mov.fecha_vencimiento.strftime("%d/%m/%Y")))
            self.tabla.setItem(i, 6, QTableWidgetItem(f"{mov.prima:,.2f}"))
            self.tabla.setItem(i, 7, QTableWidgetItem(mov.estado_display))
            
            # Calcular días restantes
            dias_rest = (mov.fecha_vencimiento - hoy).days
            item_dias = QTableWidgetItem(str(dias_rest))
            if dias_rest < 0:
                item_dias.setForeground(Qt.GlobalColor.red)
                vencidos += 1
            elif dias_rest <= 30:
                item_dias.setForeground(Qt.GlobalColor.darkYellow)
                por_vencer += 1
            else:
                vigentes += 1
            self.tabla.setItem(i, 8, item_dias)
            
            # Botones de acción
            if self.es_admin:
                widget_acciones = QWidget()
                layout_acciones = QHBoxLayout(widget_acciones)
                layout_acciones.setContentsMargins(0, 0, 0, 0)
                
                btn_editar = QPushButton("✏️")
                btn_editar.setFixedWidth(30)
                btn_editar.clicked.connect(lambda checked, id=mov.id: self.mostrar_dialogo_editar(id))
                
                layout_acciones.addWidget(btn_editar)
                
                self.tabla.setCellWidget(i, 9, widget_acciones)

        # Actualizar estadísticas
        self.lbl_total.setText(f"Total: {len(movimientos)} movimientos")
        self.lbl_por_vencer.setText(f"Por vencer: {por_vencer}")
        self.lbl_vencidos.setText(f"Vencidos: {vencidos}")

    def filtrar_movimientos(self):
        """Filtra la tabla según el texto de búsqueda y estado seleccionado"""
        texto = self.busqueda.text()
        estado = self.combo_estado.currentText()
        
        # Primero filtrar por texto
        movimientos = self.viewmodel.filtrar_movimientos(texto)
        
        # Luego filtrar por estado
        if estado == "Vigentes":
            movimientos = self.viewmodel.get_movimientos_vigentes()
        elif estado == "Por Vencer":
            movimientos = self.viewmodel.get_movimientos_por_vencer()
        elif estado == "Vencidos":
            hoy = date.today()
            movimientos = [m for m in movimientos if m.fecha_vencimiento < hoy]
            
        self.actualizar_tabla(movimientos)

    def mostrar_dialogo_nuevo(self):
        """Muestra el diálogo para crear un nuevo movimiento"""
        # TODO: Implementar diálogo de nuevo movimiento
        logger.info("Mostrando diálogo de nuevo movimiento")

    def mostrar_dialogo_editar(self, id: int):
        """Muestra el diálogo para editar un movimiento"""
        # TODO: Implementar diálogo de edición
        logger.info(f"Mostrando diálogo de edición para movimiento {id}")

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, "Error", mensaje)
