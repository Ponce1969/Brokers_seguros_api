"""Vista para la gestion de cliente"""

import logging
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

from ..viewmodels.cliente_viewmodel import ClienteViewModel
from ..services.auth_service import AuthService  # Para obtener info del usuario actual
from ..utils import IconHelper, apply_shadow, apply_button_shadow, apply_card_shadow
from .dialogo_cliente import DialogoCliente

# Configurar logging
logger = logging.getLogger(__name__)

# Constantes de colores - obtenidos del ThemeManager
COLOR_PRIMARY = "#1a73e8"  # Azul principal
COLOR_DANGER = "#d93025"   # Rojo para acciones de eliminación


class VistaClientes(QWidget):
    """Vista principal para la gestión de clientes"""

    def __init__(self, viewmodel: ClienteViewModel = None, es_admin: bool = False):
        super().__init__()
        
        # Si no se proporciona un viewmodel, intentar obtenerlo del contenedor
        if viewmodel is not None:
            self.viewmodel = viewmodel
        else:
            try:
                from ..core.di_container import contenedor
                from ..services.network_manager import NetworkManager
                network_manager = contenedor.resolver(NetworkManager)
                self.viewmodel = ClienteViewModel(network_manager)
                logger.info("ClienteViewModel inicializado correctamente en VistaClientes")
            except Exception as e:
                logger.error(f"Error al resolver ClienteViewModel: {e}")
                # Como último recurso, crear una instancia sin parámetros
                self.viewmodel = ClienteViewModel()
        
        # Obtener servicio de autenticación para info del usuario actual
        try:
            from ..core.di_container import contenedor
            self.auth_service = contenedor.resolver(AuthService)
            logger.info("AuthService resuelto correctamente en VistaClientes")
        except Exception as e:
            logger.error(f"Error al resolver AuthService: {e}")
            self.auth_service = None
                
        self.es_admin = es_admin

        # Cargar la hoja de estilos
        self.cargar_estilos()

        self.init_ui()
        self.conectar_senales()
        
        # Intentar cargar clientes iniciales sólo si hay API disponible
        try:
            if hasattr(self.viewmodel, 'api') and self.viewmodel.api is not None:
                self.viewmodel.cargar_clientes()
                logger.info("Cargando lista de clientes")
            else:
                logger.warning("No se pueden cargar clientes: NetworkManager no disponible")
        except Exception as e:
            logger.error(f"Error al cargar clientes: {e}")

    def cargar_estilos(self):
        """Carga los estilos usando setStyleSheet"""
        try:
            # Aplicar la hoja de estilos específicas para controlar el tamaño
            self.setStyleSheet("""
            /* Estilos específicos para la vista de clientes */
            QTableWidget {
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 2px;
            }
            
            QTableWidget::item {
                padding: 4px;
            }
            
            QLineEdit#busqueda {
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            """)
        except Exception as e:
            logger.error(f"Error al aplicar estilos: {e}")

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Título y buscador
        titulo_layout = QHBoxLayout()

        # Etiqueta de título con icono
        titulo_layout.addWidget(QLabel("Gestión de Clientes"))
        titulo_layout.addStretch()

        # Campo de búsqueda
        self.busqueda_input = QLineEdit()
        self.busqueda_input.setPlaceholderText("Buscar clientes...")
        self.busqueda_input.textChanged.connect(self.filtrar_clientes)
        # Ancho mínimo para que sea visible
        self.busqueda_input.setMinimumWidth(200)
        titulo_layout.addWidget(self.busqueda_input)

        # Botu00f3n de nuevo cliente (solo para administradores)
        if self.es_admin:
            self.btn_nuevo = QPushButton("Nuevo Cliente")
            self.btn_nuevo.setIcon(IconHelper.get_icon("add"))  # Sin extensión .svg
            self.btn_nuevo.clicked.connect(self.handle_nuevo_cliente)
            titulo_layout.addWidget(self.btn_nuevo)

        main_layout.addLayout(titulo_layout)

        # Tabla de clientes
        self.tabla = QTableWidget(0, 7)  # Filas, Columnas
        self.tabla.setHorizontalHeaderLabels(
            ["Número", "Nombre", "Documento", "Teléfono", "Email", "Dirección", "Acciones"]
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)

        # Configurar anchos de columna
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nombre
        self.tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Dirección

        main_layout.addWidget(self.tabla)

    def conectar_senales(self):
        """Conecta las señales del ViewModel"""
        # Conectar señales del viewmodel
        self.viewmodel.clientes_actualizados.connect(self.actualizar_tabla)
        self.viewmodel.error_ocurrido.connect(self.mostrar_error)

    def actualizar_tabla(self, clientes):
        """Actualiza la tabla con la lista de clientes"""
        self.tabla.setRowCount(0)  # Limpiar tabla

        for i, cliente in enumerate(clientes):
            self.tabla.insertRow(i)

            # Crear items para cada columna
            self.tabla.setItem(i, 0, QTableWidgetItem(str(cliente.numero_cliente)))
            self.tabla.setItem(i, 1, QTableWidgetItem(cliente.nombre_completo))
            self.tabla.setItem(i, 2, QTableWidgetItem(cliente.numero_documento))
            self.tabla.setItem(i, 3, QTableWidgetItem(cliente.movil or cliente.telefonos))
            self.tabla.setItem(i, 4, QTableWidgetItem(cliente.mail))
            self.tabla.setItem(i, 5, QTableWidgetItem(cliente.direccion))

            # Agregar botones de acción (editar, eliminar)
            self._agregar_botones_accion(i, cliente)

        # Ajustar tamaño de las filas
        self.tabla.resizeRowsToContents()

    def _agregar_botones_accion(self, i: int, cliente):
        """Agrega botones de acción para cada cliente en la tabla"""
        # Crear un widget para contener los botones
        widget_botones = QWidget()
        layout_botones = QHBoxLayout(widget_botones)
        layout_botones.setContentsMargins(4, 4, 4, 4)
        layout_botones.setSpacing(5)

        # Botón de editar
        btn_editar = QPushButton()
        btn_editar.setIcon(IconHelper.get_icon("edit"))  # Sin extensión .svg
        btn_editar.setToolTip("Editar Cliente")
        btn_editar.setFixedSize(QSize(30, 30))
        btn_editar.clicked.connect(lambda: self.mostrar_dialogo_editar(cliente.id))
        layout_botones.addWidget(btn_editar)

        # Botón de eliminar
        if self.es_admin:
            btn_eliminar = QPushButton()
            btn_eliminar.setIcon(IconHelper.get_icon("delete"))  # Sin extensión .svg
            btn_eliminar.setToolTip("Eliminar Cliente")
            btn_eliminar.setFixedSize(QSize(30, 30))
            btn_eliminar.clicked.connect(lambda: self.confirmar_eliminar(cliente.id))
            layout_botones.addWidget(btn_eliminar)

        # Agregar widget de botones a la tabla
        self.tabla.setCellWidget(i, 6, widget_botones)

    def filtrar_clientes(self):
        """Filtra la tabla según el texto de búsqueda"""
        texto = self.busqueda_input.text().strip()
        clientes_filtrados = self.viewmodel.filtrar_clientes(texto)
        self.actualizar_tabla(clientes_filtrados)

    def handle_nuevo_cliente(self):
        """Maneja el evento del botón nuevo cliente"""
        if not self.es_admin:
            return

        try:
            # Obtener ID del corredor actual
            corredor_id = self._obtener_corredor_id_actual()
            logger.info(f"Creando cliente asociado al corredor ID: {corredor_id}")
            
            # Pasar el ID del corredor al diálogo
            dialogo = DialogoCliente(
                parent=self, 
                model=self.viewmodel.item_model,
                corredor_id=corredor_id
            )
            dialogo.datos_guardados.connect(self._crear_cliente_slot)
            dialogo.exec()
        except Exception as e:
            logger.error(f"Error al mostrar dialogo: {e}")
            self.mostrar_error("Error al abrir el formulario de nuevo cliente")

    @pyqtSlot(dict)
    def _crear_cliente_slot(self, datos):
        """Slot que maneja la señal datos_guardados y crea el cliente"""
        try:
            self.viewmodel.crear_cliente(datos)
        except Exception as e:
            self.mostrar_error(f"Error al crear el cliente: {str(e)}")

    def mostrar_dialogo_editar(self, id: str):
        """Muestra el dialogo para editar un cliente"""
        if not self.es_admin:
            return

        cliente = self.viewmodel.buscar_cliente(id)
        if cliente:
            try:
                # Obtener ID del corredor actual para mantener la asociación
                corredor_id = self._obtener_corredor_id_actual()
                logger.info(f"Editando cliente ID: {id} asociado al corredor ID: {corredor_id}")
                
                dialogo = DialogoCliente(self, cliente, corredor_id=corredor_id)
                # Conectar la señal datos_guardados a un lambda que actualice el cliente
                dialogo.datos_guardados.connect(
                    lambda datos: self.viewmodel.actualizar_cliente(id, datos)
                )
                dialogo.exec()
            except Exception as e:
                logger.error(f"Error al mostrar dialogo de edicion: {e}")
                self.mostrar_error("Error al abrir el formulario de edicion de cliente")

    def confirmar_eliminar(self, id: str):
        """Muestra dialogo de confirmacion para eliminar un cliente"""
        if not self.es_admin:
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminacion",
            "¿Está seguro de que desea eliminar este cliente?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                self.viewmodel.eliminar_cliente(id)
            except Exception as e:
                self.mostrar_error(f"Error al eliminar cliente: {str(e)}")

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, "Error", mensaje)
        
    def _obtener_corredor_id_actual(self) -> int:
        """
        Obtiene el ID del corredor actualmente autenticado
        
        Returns:
            int: ID del corredor actual o None si no se puede determinar
        """
        try:
            # Si no hay servicio de autenticación, no podemos obtener la info
            if not self.auth_service:
                logger.warning("No se puede obtener el ID de corredor: AuthService no disponible")
                return None
                
            # Para el administrador (Rodrigo Ponce), usar su ID de corredor fijo (4554)
            if self.es_admin:
                # Según la memoria, el admin tiene el número de corredor 4554
                logger.info("Usuario admin detectado, usando ID de corredor fijo: 4554")
                return 4554
            
            # Obtener información del usuario actual
            # Implementación temporal - en un sistema real, esto debería
            # obtenerse de manera dinámica consultando a la API
            # TODO: Implementar método en AuthService para obtener el ID de corredor del usuario actual
            
            # Como medida temporal, usar un ID por defecto (debería reemplazarse)
            corredor_id = 1  # Valor por defecto - debería obtenerse del perfil del usuario
            logger.warning(f"Usando ID de corredor por defecto: {corredor_id} (implementación temporal)")
            return corredor_id
            
        except Exception as e:
            logger.error(f"Error al obtener ID de corredor: {e}")
            return None

    def resizeEvent(self, event):
        """Controla el comportamiento cuando se cambia el tamaño de la ventana"""
        super().resizeEvent(event)
        # Reajustar las filas de la tabla cuando se cambia el tamaño
        self.tabla.resizeRowsToContents()
