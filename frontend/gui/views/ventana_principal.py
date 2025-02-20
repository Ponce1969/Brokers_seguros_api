"""
Ventana principal de la aplicación
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from gui.viewmodels.corredor_viewmodel import CorredorViewModel
from gui.viewmodels.movimiento_vigencia_viewmodel import MovimientoVigenciaViewModel
from gui.views.corredor_view import VistaCorredores
from gui.views.movimiento_vigencia_view import VistaMovimientosVigencia
import logging

logger = logging.getLogger(__name__)


class VentanaPrincipal(QMainWindow):
    """Ventana principal de la aplicación"""

    def __init__(self, viewmodel_corredor: CorredorViewModel, rol_usuario: str):
        super().__init__()
        self.viewmodel_corredor = viewmodel_corredor
        self.viewmodel_movimientos = MovimientoVigenciaViewModel()
        self.rol_usuario = rol_usuario
        self.setWindowTitle("Broker Seguros - Sistema de Gestión")
        self.setGeometry(100, 100, 1200, 800)
        self._inicializar_ui()

    def _inicializar_ui(self):
        """Inicializa la interfaz de usuario"""
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        # Layout principal
        layout_principal = QHBoxLayout()
        widget_central.setLayout(layout_principal)

        # Panel de navegación (izquierda)
        panel_navegacion = QWidget()
        layout_navegacion = QVBoxLayout()
        panel_navegacion.setLayout(layout_navegacion)
        panel_navegacion.setFixedWidth(200)

        # Título del panel de navegación
        titulo_nav = QLabel("Menú Principal")
        titulo_nav.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_nav.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout_navegacion.addWidget(titulo_nav)

        # Estilo común para los botones
        estilo_boton = """
            QPushButton {
                text-align: left;
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007bff;
                color: white;
                font-size: 12px;
                margin-bottom: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """

        # Botones de navegación
        self.boton_corredores = QPushButton("Corredores")
        self.boton_corredores.setStyleSheet(estilo_boton)
        
        self.boton_clientes = QPushButton("Clientes")
        self.boton_clientes.setStyleSheet(estilo_boton)
        
        self.boton_movimientos = QPushButton("Movimientos Vigencias")
        self.boton_movimientos.setStyleSheet(estilo_boton)

        # Conectar botones a sus funciones
        self.boton_corredores.clicked.connect(lambda: self.cambiar_vista("corredores"))
        self.boton_clientes.clicked.connect(lambda: self.cambiar_vista("clientes"))
        self.boton_movimientos.clicked.connect(lambda: self.cambiar_vista("movimientos"))

        # Agregar botones al layout de navegación
        layout_navegacion.addWidget(self.boton_corredores)
        layout_navegacion.addWidget(self.boton_clientes)
        layout_navegacion.addWidget(self.boton_movimientos)

        # Configurar visibilidad según el rol
        self.configurar_permisos_rol()

        # Agregar espacio flexible al final
        layout_navegacion.addStretch()

        # Stack de vistas (derecha)
        self.stack_vistas = QStackedWidget()

        # Determinar si el usuario es admin
        es_admin = self.rol_usuario.lower() == "admin"

        # Inicializar vistas
        self.vista_corredores = VistaCorredores(
            self.viewmodel_corredor,
            es_admin=es_admin
        )
        self.stack_vistas.addWidget(self.vista_corredores)

        # Vista de movimientos
        self.vista_movimientos = VistaMovimientosVigencia(
            self.viewmodel_movimientos,
            es_admin=es_admin
        )
        self.stack_vistas.addWidget(self.vista_movimientos)

        # Placeholder para vista de clientes
        self.vista_clientes = QWidget()
        self.stack_vistas.addWidget(self.vista_clientes)

        # Agregar paneles al layout principal
        layout_principal.addWidget(panel_navegacion)
        layout_principal.addWidget(self.stack_vistas)

        # Mostrar la vista inicial según el rol
        if es_admin:
            self.cambiar_vista("corredores")
        else:
            self.cambiar_vista("movimientos")

    def configurar_permisos_rol(self):
        """Configura la visibilidad de los elementos según el rol del usuario"""
        es_admin = self.rol_usuario.lower() == "admin"
        
        # El botón de corredores solo está disponible para administradores
        self.boton_corredores.setVisible(es_admin)
        
        # Los demás botones están disponibles para todos los usuarios
        # pero su funcionalidad puede estar limitada según el rol

    def cambiar_vista(self, vista: str):
        """Cambia la vista actual en el stack"""
        try:
            if vista == "corredores":
                self.stack_vistas.setCurrentWidget(self.vista_corredores)
                self.boton_corredores.setStyleSheet(self.boton_corredores.styleSheet() + "background-color: #004085;")
                self.boton_clientes.setStyleSheet(self.boton_clientes.styleSheet().replace("background-color: #004085;", ""))
                self.boton_movimientos.setStyleSheet(self.boton_movimientos.styleSheet().replace("background-color: #004085;", ""))
            elif vista == "clientes":
                self.stack_vistas.setCurrentWidget(self.vista_clientes)
                self.boton_clientes.setStyleSheet(self.boton_clientes.styleSheet() + "background-color: #004085;")
                self.boton_corredores.setStyleSheet(self.boton_corredores.styleSheet().replace("background-color: #004085;", ""))
                self.boton_movimientos.setStyleSheet(self.boton_movimientos.styleSheet().replace("background-color: #004085;", ""))
            elif vista == "movimientos":
                self.stack_vistas.setCurrentWidget(self.vista_movimientos)
                self.boton_movimientos.setStyleSheet(self.boton_movimientos.styleSheet() + "background-color: #004085;")
                self.boton_corredores.setStyleSheet(self.boton_corredores.styleSheet().replace("background-color: #004085;", ""))
                self.boton_clientes.setStyleSheet(self.boton_clientes.styleSheet().replace("background-color: #004085;", ""))
        except Exception as e:
            logger.error(f"Error al cambiar vista: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cambiar de vista: {str(e)}\n"
                "Por favor, contacte al soporte técnico.",
            )
