"""
Vista para la gestión de corredores
"""

import logging
import os
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
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
from PyQt6.QtGui import QIcon

from ..viewmodels.corredor_viewmodel import CorredorViewModel
from ..utils import IconHelper, theme_manager
from .dialogo_corredor import DialogoCorredor

# Configurar logging
logger = logging.getLogger(__name__)

# Constantes de colores - obtenidos del ThemeManager
COLOR_PRIMARY = theme_manager.get_theme_colors().get("--primary-color")
COLOR_DANGER = theme_manager.get_theme_colors().get("--danger-color")


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
        """Carga los estilos usando el ThemeManager"""
        try:
            # Aplicar la hoja de estilos procesada a este widget
            self.setStyleSheet(theme_manager.processed_stylesheet)
            logger.info("✅ Estilos aplicados al widget de corredores")
        except Exception as e:
            logger.error(f"❌ Error al aplicar los estilos: {e}")

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
        # Usar el icono de añadir con el color principal definido en QSS
        self.btn_nuevo.setIcon(IconHelper.get_icon("add", COLOR_PRIMARY))
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
            
            # Establecer altura de fila a 32px para mejorar centrado de botones
            for i in range(len(corredores)):
                self.tabla.setRowHeight(i, 32)
                
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
        
        # Usamos QHBoxLayout en lugar de QGridLayout
        layout_acciones = QHBoxLayout(widget_acciones)
        layout_acciones.setContentsMargins(0, 0, 0, 0)  # Márgenes ajustados
        layout_acciones.setSpacing(5)  # Espaciado uniforme entre botones
        layout_acciones.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar botones
        
        # Colores para los botones desde theme_manager
        color_edit = theme_manager.get_theme_colors().get("--primary-color")
        color_delete = theme_manager.get_theme_colors().get("--danger-color")

        # Botón de editar con color pero manteniendo el centrado
        btn_editar = QPushButton()
        btn_editar.setIcon(IconHelper.get_icon("edit", color_edit, size=16))  # Especificamos tamaño de icono
        btn_editar.setIconSize(QSize(16, 16))  # Tamaño optimizado para centrado
        btn_editar.setToolTip("Editar corredor")
        btn_editar.setFixedSize(28, 28)  # Tamaño cuadrado para centrado perfecto
        btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_editar.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f8ff;
                border: 1px solid {color_edit};
                border-radius: 5px;
                text-align: center;
                padding: 0px;
                qproperty-iconSize: 16px;
            }}
            QPushButton:hover {{
                background-color: #e6f2ff;
                border-color: #005bb5;
            }}
        """)

        btn_editar.clicked.connect(
            lambda checked=False, id=corredor.id: self.mostrar_dialogo_editar(id)
        )

        # Botón de eliminar con color pero manteniendo el centrado
        btn_eliminar = QPushButton()
        btn_eliminar.setIcon(IconHelper.get_icon("delete", color_delete, size=16))  # Especificamos tamaño de icono
        btn_eliminar.setIconSize(QSize(16, 16))  # Tamaño uniforme con el de editar
        btn_eliminar.setToolTip("Eliminar corredor")
        btn_eliminar.setFixedSize(28, 28)
        btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eliminar.setStyleSheet(f"""
            QPushButton {{
                background-color: #fff5f5;
                border: 1px solid {color_delete};
                border-radius: 5px;
                text-align: center;
                padding: 0px;
                qproperty-iconSize: 16px;
            }}
            QPushButton:hover {{
                background-color: #ffe6e6;
                border-color: #c82333;
            }}
        """)

        btn_eliminar.clicked.connect(
            lambda checked=False, id=corredor.id: self.confirmar_eliminar(id)
        )

        # Agregar botones al layout
        layout_acciones.addWidget(btn_editar)
        layout_acciones.addWidget(btn_eliminar)

        # Establecer el widget en la celda con alineación central
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
