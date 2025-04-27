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
    QScrollArea,
    QSizePolicy,
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
            # Aplicar la hoja de estilos específicas para controlar el tamaño
            self.setStyleSheet("""
            /* Estilos específicos para la vista de corredores */
            QTableWidget {
                max-width: 1200px; /* Limitar expansión horizontal */
            }
            QTableWidget QHeaderView::section {
                padding: 5px;
                background-color: #e8eaed;
                border: 1px solid #cccccc;
                color: #202124;
            }
            /* Asegurar que los elementos dentro de la tabla no expandan la ventana */
            QTableWidget::item {
                max-width: 250px;
                margin: 0;
                padding: 2px;
            }
            """)
            
            # Establecer política de tamaño para la vista principal más restrictiva
            # para evitar que crezca más allá de lo necesario
            self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
            
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
        self.tabla.setColumnCount(8)  # Incluir documento como columna adicional
        self.tabla.setHorizontalHeaderLabels(
            ["Número", "Nombre", "Email", "Teléfono", "Dirección", "Documento", "Estado", "Acciones"]
        )
        
        # Establecer tamaño máximo para la tabla para evitar expansiones excesivas
        self.tabla.setMaximumWidth(1200)
        
        # Establecer política de tamaño para la tabla con expansión controlada
        self.tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Configurar propiedades visuales de la tabla
        header = self.tabla.horizontalHeader()
        
        # Unificar los modos de redimensionamiento para evitar recálculos constantes
        # Usar Fixed para columnas críticas y Stretch para el resto para mejor distribución
        for i in range(self.tabla.columnCount()):
            if i in [0, 6]:  # Número y Acciones - modo fijo
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            else:  # Resto de columnas - modo stretch para mejor distribución
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        # Establecer anchos iniciales de columnas
        self.tabla.setColumnWidth(0, 70)   # Ancho para número
        self.tabla.setColumnWidth(7, 100)  # Ancho para acciones
        self.tabla.setColumnWidth(1, 150)  # Ancho para nombre
        self.tabla.setColumnWidth(2, 180)  # Ancho para email
        self.tabla.setColumnWidth(3, 120)  # Ancho para teléfono
        self.tabla.setColumnWidth(4, 200)  # Ancho para dirección
        self.tabla.setColumnWidth(5, 120)  # Ancho para documento
        self.tabla.setColumnWidth(6, 80)   # Ancho para estado
        
        # Limitar tamaños de secciones
        header.setMinimumSectionSize(70)
        header.setMaximumSectionSize(250)  # Evitar que las columnas se expandan demasiado
        
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setGridStyle(Qt.PenStyle.DotLine)
        self.tabla.setShowGrid(True)
        
        # Agregar la tabla directamente al layout (QTableWidget ya tiene scrolling incorporado)
        # y establecer política de tamaño adecuada para evitar expansiones innecesarias
        self.tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Agregar la tabla directamente al layout principal
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
                        QTableWidgetItem(corredor.documento or ""),  # Nuevo campo documento
                        QTableWidgetItem("Activo" if corredor.activo else "Inactivo"),
                    ]

                    for col, item in enumerate(items):
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        if col == 0:  # Número
                            item.setTextAlignment(
                                Qt.AlignmentFlag.AlignRight
                                | Qt.AlignmentFlag.AlignVCenter
                            )
                        # Limitar el contenido del texto para evitar expansiones
                        text = item.text()
                        if len(text) > 40 and col not in [0, 5]:
                            item.setToolTip(text)  # Mostrar texto completo en tooltip
                            item.setText(text[:37] + "...")
                        self.tabla.setItem(i, col, item)

                    if self.es_admin:
                        self._agregar_botones_accion(i, corredor)
                except AttributeError as e:
                    logger.error(f"Error al procesar corredor: {e}")
                    continue

            # No hacer un resizeColumnsToContents() completo que podría cambiar el tamaño
            # En su lugar, asegurarse que las columnas respeten los límites establecidos
            for i in range(self.tabla.columnCount()):
                if i not in [0, 6] and self.tabla.columnWidth(i) > 250:
                    self.tabla.setColumnWidth(i, 250)  # Limitar a un máximo de 250px
        except Exception as e:
            logger.error(f"Error al actualizar la tabla: {e}")
            self.mostrar_error("Error al actualizar la tabla")

    def _agregar_botones_accion(self, i: int, corredor):
        """Agrega botones de acción para cada corredor en la tabla"""
        widget_acciones = QWidget()
        
        # Usamos QHBoxLayout para alineación perfecta (según memoria)
        layout_acciones = QHBoxLayout(widget_acciones)
        layout_acciones.setContentsMargins(0, 0, 0, 0)  # Eliminar todos los márgenes
        layout_acciones.setSpacing(5)  # Espaciado óptimo entre botones (según memoria)
        layout_acciones.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Alineación central (según memoria)
        
        # Ya tenemos las constantes COLOR_PRIMARY y COLOR_DANGER definidas arriba
        # que se usarán para los iconos de editar y eliminar

        # Botón de editar usando propiedades para identificar en QSS
        btn_editar = QPushButton()
        btn_editar.setObjectName("btn_editar")
        # Usar IconHelper para obtener el SVG correcto
        btn_editar.setIcon(IconHelper.get_icon("edit", COLOR_PRIMARY))
        btn_editar.setIconSize(QSize(16, 16))  # Tamaño óptimo según memorias
        btn_editar.setFixedSize(28, 28)  # Tamaño óptimo según memorias
        btn_editar.setToolTip("Editar corredor")
        btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
        # Marcar como botón de acción en tabla para estilos CSS
        btn_editar.setProperty("tableAction", "true")
        btn_editar.setProperty("actionType", "edit")

        btn_editar.clicked.connect(
            lambda checked=False, id=corredor.id: self.mostrar_dialogo_editar(id)
        )

        # Botón de eliminar usando propiedades para identificar en QSS
        btn_eliminar = QPushButton()
        btn_eliminar.setObjectName("btn_eliminar")
        # Usar IconHelper para obtener el SVG correcto
        btn_eliminar.setIcon(IconHelper.get_icon("delete", COLOR_DANGER))
        btn_eliminar.setIconSize(QSize(16, 16))  # Tamaño óptimo según memorias
        btn_eliminar.setFixedSize(28, 28)  # Tamaño óptimo según memorias
        btn_eliminar.setToolTip("Eliminar corredor")
        btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        # Marcar como botón de acción en tabla para estilos CSS
        btn_eliminar.setProperty("tableAction", "true")
        btn_eliminar.setProperty("actionType", "delete")

        btn_eliminar.clicked.connect(
            lambda checked=False, id=corredor.id: self.confirmar_eliminar(id)
        )

        # Agregar botones al layout
        layout_acciones.addWidget(btn_editar)
        layout_acciones.addWidget(btn_eliminar)

        # Establecer el widget en la celda con alineación central
        self.tabla.setCellWidget(i, 7, widget_acciones)

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
            try:
                dialogo = DialogoCorredor(self, corredor)
                # Conectar la señal datos_guardados a un lambda que actualice el corredor
                dialogo.datos_guardados.connect(
                    lambda datos: self.viewmodel.actualizar_corredor(id, datos)
                )
                dialogo.exec()
            except Exception as e:
                logger.error(f"❌ Error al mostrar diálogo de edición: {e}")
                self.mostrar_error("Error al abrir el formulario de edición de corredor")

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
        
    def resizeEvent(self, event):
        """Controla el comportamiento cuando se cambia el tamaño de la ventana"""
        super().resizeEvent(event)
        # Ajustar tamaños de columnas de forma proporcional cuando el ancho cambia
        table_width = self.tabla.width() - 170  # Restar ancho de columnas fijas (número y acciones)
        for i in range(1, 6):  # Columnas ajustables (excluir número y acciones)
            self.tabla.setColumnWidth(i, int(table_width / 5))  # Distribuir equitativamente
        
        # Solo ejecutar este código si la tabla ya está inicializada
        if hasattr(self, 'tabla'):
            # Obtener el ancho disponible
            tabla_width = self.tabla.width()
            
            # Mantener anchos fijos para columnas críticas
            self.tabla.setColumnWidth(0, 70)  # Número
            self.tabla.setColumnWidth(6, 100)  # Acciones
            
            # Ancho disponible para columnas restantes
            remaining_width = tabla_width - 170  # 70 + 100
            
            # Asegurarse de que todas las columnas tengan un ancho razonable
            col_widths = [150, 180, 120, 200, 80]  # Anchos deseados para columnas 1-5
            total_desired = sum(col_widths)
            
            # Si el espacio disponible es menor que el deseado, ajustar proporcionalmente
            if remaining_width < total_desired and remaining_width > 0:
                scale_factor = remaining_width / total_desired
                col_widths = [max(int(w * scale_factor), 70) for w in col_widths]
            
            # Aplicar anchos calculados a las columnas dinámicas
            for i, width in enumerate(col_widths, 1):
                self.tabla.setColumnWidth(i, width)
