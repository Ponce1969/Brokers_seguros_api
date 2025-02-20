"""
Vista para la gestión de corredores
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
)
from PyQt6.QtCore import Qt
import logging
from ..viewmodels.corredor_viewmodel import CorredorViewModel
from .dialogo_corredor import DialogoCorredor

# Configurar logging
logger = logging.getLogger(__name__)

class VistaCorredores(QWidget):
    """Vista principal para la gestión de corredores"""

    def __init__(self, viewmodel: CorredorViewModel, es_admin: bool = False):
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
        titulo = QLabel("Gestión de Corredores")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        # Barra de herramientas
        toolbar = QHBoxLayout()
        
        # Búsqueda
        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText("Buscar corredor...")
        self.busqueda.textChanged.connect(self.filtrar_corredores)
        toolbar.addWidget(self.busqueda)

        # Botón nuevo corredor (solo visible para administradores)
        self.btn_nuevo = QPushButton("Nuevo Corredor")
        self.btn_nuevo.clicked.connect(self.mostrar_dialogo_nuevo)
        self.btn_nuevo.setVisible(self.es_admin)
        toolbar.addWidget(self.btn_nuevo)

        layout.addLayout(toolbar)

        # Tabla de corredores
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)  # Agregamos columna para número
        self.tabla.setHorizontalHeaderLabels([
            "Número", "Email", "Nombre", "Teléfono", "Dirección", "Estado", "Acciones"
        ])
        
        # Configurar la tabla
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Número
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Acciones
        self.tabla.setColumnWidth(0, 70)  # Ancho para número
        self.tabla.setColumnWidth(6, 100)  # Ancho para acciones
        
        layout.addWidget(self.tabla)

    def conectar_senales(self):
        """Conecta las señales del ViewModel"""
        self.viewmodel.corredores_actualizados.connect(self.actualizar_tabla)
        self.viewmodel.error_ocurrido.connect(self.mostrar_error)

    def actualizar_tabla(self, corredores):
        """Actualiza la tabla con la lista de corredores"""
        self.tabla.setRowCount(len(corredores))
        for i, corredor in enumerate(corredores):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(corredor.numero)))
            self.tabla.setItem(i, 1, QTableWidgetItem(corredor.email))
            self.tabla.setItem(i, 2, QTableWidgetItem(corredor.nombre))
            self.tabla.setItem(i, 3, QTableWidgetItem(corredor.telefono or ""))
            self.tabla.setItem(i, 4, QTableWidgetItem(corredor.direccion or ""))
            self.tabla.setItem(i, 5, QTableWidgetItem("Activo" if corredor.activo else "Inactivo"))
            
            # Botones de acción (solo visibles para administradores)
            if self.es_admin:
                widget_acciones = QWidget()
                layout_acciones = QHBoxLayout(widget_acciones)
                layout_acciones.setContentsMargins(0, 0, 0, 0)
                
                btn_editar = QPushButton("✏️")
                btn_editar.setFixedWidth(30)
                btn_editar.clicked.connect(lambda checked, id=corredor.id: self.mostrar_dialogo_editar(id))
                
                btn_eliminar = QPushButton("🗑️")
                btn_eliminar.setFixedWidth(30)
                btn_eliminar.clicked.connect(lambda checked, id=corredor.id: self.confirmar_eliminar(id))
                
                layout_acciones.addWidget(btn_editar)
                layout_acciones.addWidget(btn_eliminar)
                
                self.tabla.setCellWidget(i, 6, widget_acciones)

    def filtrar_corredores(self):
        """Filtra la tabla según el texto de búsqueda"""
        texto = self.busqueda.text()
        corredores_filtrados = self.viewmodel.filtrar_corredores(texto)
        self.actualizar_tabla(corredores_filtrados)

    def mostrar_dialogo_nuevo(self):
        """Muestra el diálogo para crear un nuevo corredor"""
        if not self.es_admin:
            return
            
        dialogo = DialogoCorredor(self)
        if dialogo.exec():
            datos = dialogo.obtener_datos()
            # TODO: Implementar creación de corredor
            logger.info("Datos del nuevo corredor:", datos)

    def mostrar_dialogo_editar(self, id: str):
        """Muestra el diálogo para editar un corredor"""
        if not self.es_admin:
            return
            
        corredor = self.viewmodel.buscar_corredor(id)
        if corredor:
            dialogo = DialogoCorredor(self, corredor)
            if dialogo.exec():
                datos = dialogo.obtener_datos()
                # TODO: Implementar actualización de corredor
                logger.info(f"Datos actualizados del corredor {id}:", datos)

    def confirmar_eliminar(self, id: str):
        """Muestra diálogo de confirmación para eliminar un corredor"""
        if not self.es_admin:
            return
            
        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar este corredor?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            # TODO: Implementar eliminación de corredor
            logger.info(f"Eliminando corredor {id}")

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, "Error", mensaje)
