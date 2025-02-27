"""
Vista para la gestión de corredores
"""

import logging
import os
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..viewmodels.corredor_viewmodel import CorredorViewModel
from .dialogo_corredor import DialogoCorredor

# Configurar logging
logger = logging.getLogger(__name__)


class VistaCorredores(QWidget):
    """Vista principal para la gestión de corredores"""

    def __init__(self, viewmodel: CorredorViewModel = None, es_admin: bool = False):
        super().__init__()
        # Si no se proporciona un viewmodel, crear uno nuevo
        self.viewmodel = viewmodel if viewmodel is not None else CorredorViewModel()
        self.es_admin = es_admin

        # Cargar la hoja de estilos
        self.cargar_estilos()

        self.init_ui()
        self.conectar_senales()

        # Cargar corredores iniciales
        self.viewmodel.cargar_corredores()

    def cargar_estilos(self):
        """Carga los estilos desde el archivo .qss"""
        try:
            # Ruta relativa al archivo styles.qss
            styles_path = os.path.join(
                os.path.dirname(__file__), "../resources/styles.qss"
            )

            if os.path.exists(styles_path):
                with open(styles_path, "r") as file:
                    self.setStyleSheet(file.read())
                logger.info("✅ Estilos cargados correctamente")
            else:
                logger.warning("⚠️ Archivo de estilos no encontrado: %s", styles_path)
        except Exception as e:
            logger.error(f"❌ Error al cargar los estilos: {e}")

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
        self.btn_nuevo.clicked.connect(self.handle_nuevo_corredor)
        self.btn_nuevo.setVisible(self.es_admin)
        toolbar.addWidget(self.btn_nuevo)

        layout.addLayout(toolbar)

        # Tabla de corredores
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)  # Aumentado para incluir más campos
        self.tabla.setHorizontalHeaderLabels(
            ["Número", "Nombre", "Email", "Teléfono", "Dirección", "Estado", "Acciones"]
        )
        
        # Configurar propiedades visuales de la tabla
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Número
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Acciones
        self.tabla.setColumnWidth(0, 70)  # Ancho para número
        self.tabla.setColumnWidth(6, 100)  # Ancho para acciones
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setGridStyle(Qt.PenStyle.DotLine)
        self.tabla.setShowGrid(True)

        layout.addWidget(self.tabla)

    def conectar_senales(self):
        """Conecta las señales del ViewModel"""
        self.viewmodel.corredores_actualizados.connect(self.actualizar_tabla)
        self.viewmodel.error_ocurrido.connect(self.mostrar_error)

    def actualizar_tabla(self, corredores):
        """Actualiza la tabla con la lista de corredores"""
        try:
            self.tabla.setRowCount(len(corredores))
            for i, corredor in enumerate(corredores):
                try:
                    items = [
                        QTableWidgetItem(str(corredor.numero)),
                        QTableWidgetItem(corredor.nombre),
                        QTableWidgetItem(corredor.email),
                        QTableWidgetItem(corredor.telefono or ""),
                        QTableWidgetItem(corredor.direccion or ""),
                        QTableWidgetItem("Activo" if corredor.activo else "Inactivo"),
                    ]

                    for col, item in enumerate(items):
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        if col == 0:  # Número
                            item.setTextAlignment(
                                Qt.AlignmentFlag.AlignRight
                                | Qt.AlignmentFlag.AlignVCenter
                            )
                        self.tabla.setItem(i, col, item)

                    if self.es_admin:
                        self._agregar_botones_accion(i, corredor)
                except AttributeError as e:
                    logger.error(f"Error al procesar corredor: {e}")
                    continue

            self.tabla.resizeColumnsToContents()
        except Exception as e:
            logger.error(f"Error al actualizar la tabla: {e}")
            self.mostrar_error("Error al actualizar la tabla")

    def _agregar_botones_accion(self, i: int, corredor):
        """Agrega botones de acción para cada corredor en la tabla"""
        widget_acciones = QWidget()
        layout_acciones = QHBoxLayout(widget_acciones)
        layout_acciones.setContentsMargins(0, 0, 0, 0)

        btn_editar = QPushButton("✏️")
        btn_editar.setFixedWidth(30)
        btn_editar.clicked.connect(
            lambda checked, id=corredor.id: self.mostrar_dialogo_editar(id)
        )

        btn_eliminar = QPushButton("🗑️")
        btn_eliminar.setFixedWidth(30)
        btn_eliminar.clicked.connect(
            lambda checked, id=corredor.id: self.confirmar_eliminar(id)
        )

        layout_acciones.addWidget(btn_editar)
        layout_acciones.addWidget(btn_eliminar)

        self.tabla.setCellWidget(i, 6, widget_acciones)

    def filtrar_corredores(self):
        """Filtra la tabla según el texto de búsqueda"""
        texto = self.busqueda.text().strip().lower()
        if texto:
            corredores_filtrados = self.viewmodel.filtrar_corredores(texto)
        else:
            corredores_filtrados = self.viewmodel.corredores
        self.actualizar_tabla(corredores_filtrados)

    def handle_nuevo_corredor(self):
        """Maneja el evento del botón nuevo corredor"""
        if not self.es_admin:
            return

        try:
            dialogo = DialogoCorredor(parent=self, model=self.viewmodel.item_model)
            dialogo.datos_guardados.connect(self._crear_corredor_slot)
            dialogo.exec()
        except Exception as e:
            logger.error(f"❌ Error al mostrar diálogo: {e}")
            self.mostrar_error("Error al abrir el formulario de nuevo corredor")

    @pyqtSlot(dict)
    def _crear_corredor_slot(self, datos):
        """Slot que maneja la señal datos_guardados y crea el corredor"""
        try:
            self.viewmodel.crear_corredor(datos)
        except Exception as e:
            self.mostrar_error(f"Error al crear el corredor: {str(e)}")

    def mostrar_dialogo_editar(self, id: int):
        """Muestra el diálogo para editar un corredor"""
        if not self.es_admin:
            return

        corredor = self.viewmodel.buscar_corredor(id)
        if corredor:
            dialogo = DialogoCorredor(self, corredor)
            if dialogo.exec():
                datos = dialogo.obtener_datos()
                self.viewmodel.actualizar_corredor(id, datos)

    def confirmar_eliminar(self, id: int):
        """Muestra diálogo de confirmación para eliminar un corredor"""
        if not self.es_admin:
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar este corredor?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            self.viewmodel.eliminar_corredor(id)

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, "Error", mensaje)
