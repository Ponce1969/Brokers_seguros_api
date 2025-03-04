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
from ..utils import IconHelper, apply_shadow, apply_button_shadow, apply_card_shadow
from .dialogo_corredor import DialogoCorredor

# Configurar logging
logger = logging.getLogger(__name__)

# Constantes de colores - obtenidos del ThemeManager
COLOR_PRIMARY = "#1a73e8"  # Azul principal
COLOR_DANGER = "#d93025"   # Rojo para acciones de eliminación


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
            # No se requiere estilo específico aquí, ya se aplica a nivel de aplicación
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
        # Aplicar estilo para asegurar que el texto sea visible (oscuro sobre fondo claro)
        self.btn_nuevo.setStyleSheet("QPushButton { color: #202124; }")
        self.btn_nuevo.clicked.connect(self.handle_nuevo_corredor)
        self.btn_nuevo.setVisible(self.es_admin)
        # Aplicar efecto de sombra al botón principal
        apply_button_shadow(self.btn_nuevo)
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
        
        # Asegurar que el texto del encabezado sea visible con fondo claro
        header.setStyleSheet("QHeaderView::section { color: #202124; background-color: #e8eaed; }")

        layout.addWidget(self.tabla)

    def conectar_senales(self):
        """Conecta las señales del ViewModel"""
        self.viewmodel.corredores_actualizados.connect(self.actualizar_tabla)
        self.viewmodel.error_ocurrido.connect(self.mostrar_error)

    def actualizar_tabla(self, corredores):
        """Actualiza la tabla con la lista de corredores"""
        try:
            self.tabla.setRowCount(len(corredores))
            
            # Establecer altura de fila a 38px para acomodar mejor los botones
            for i in range(len(corredores)):
                self.tabla.setRowHeight(i, 38)
                
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
        layout_acciones.setContentsMargins(0, 2, 0, 2)  # Márgenes verticales para centrado óptimo
        layout_acciones.setSpacing(8)  # Mayor espaciado entre botones para mejor visibilidad
        layout_acciones.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar botones
        
        # Colores fijos para los botones
        color_edit = "#1a73e8"  # Azul principal
        color_delete = "#d93025"  # Rojo para acciones de eliminación

        # Botón de editar usando propiedades para identificar en QSS
        btn_editar = QPushButton()
        btn_editar.setObjectName("btn_editar")
        # Usar directamente el icono PNG en lugar de SVG
        btn_editar.setIcon(QIcon("/home/gonzapython/CascadeProjects/Brokerseguros/frontend/gui/resources/icons/editar.png"))
        btn_editar.setIconSize(QSize(20, 20))
        btn_editar.setToolTip("Editar corredor")
        # Eliminar restricciu00f3n de tamau00f1o fijo para que ocupe todo el espacio disponible
        btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
        # Aplicamos propiedades para identificar en QSS
        btn_editar.setProperty("actionType", "edit")

        btn_editar.clicked.connect(
            lambda checked=False, id=corredor.id: self.mostrar_dialogo_editar(id)
        )

        # Botón de eliminar usando propiedades para identificar en QSS
        btn_eliminar = QPushButton()
        btn_eliminar.setObjectName("btn_eliminar")
        # Usar directamente el icono PNG en lugar de SVG
        btn_eliminar.setIcon(QIcon("/home/gonzapython/CascadeProjects/Brokerseguros/frontend/gui/resources/icons/eliminar.png"))
        btn_eliminar.setIconSize(QSize(20, 20))
        btn_eliminar.setToolTip("Eliminar corredor")
        # Eliminar restricciu00f3n de tamau00f1o fijo para que ocupe todo el espacio disponible
        btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        # Aplicamos propiedades para identificar en QSS
        btn_eliminar.setProperty("actionType", "delete")

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
