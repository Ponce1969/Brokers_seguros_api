"""
Ventana principal de la aplicación
"""

import logging
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
from PyQt6.QtCore import Qt, QSize
from frontend.gui.viewmodels.corredor_viewmodel import CorredorViewModel
from frontend.gui.viewmodels.movimiento_vigencia_viewmodel import MovimientoVigenciaViewModel
from frontend.gui.views.corredor_view import VistaCorredores
from frontend.gui.views.movimiento_vigencia_view import VistaMovimientosVigencia
from frontend.gui.utils import theme_manager, IconHelper

# Configurar logging
logger = logging.getLogger(__name__)


class VentanaPrincipal(QMainWindow):
    """Ventana principal de la aplicación"""

    def __init__(self, viewmodel_corredor: CorredorViewModel, rol_usuario: str, viewmodel_movimientos: MovimientoVigenciaViewModel = None):
        super().__init__()
        self.viewmodel_corredor = viewmodel_corredor
        
        # Obtener el ViewModel de movimientos del contenedor si no se proporciona
        if viewmodel_movimientos is None:
            from ..core.di_container import contenedor
            self.viewmodel_movimientos = contenedor.resolver(MovimientoVigenciaViewModel)
        else:
            self.viewmodel_movimientos = viewmodel_movimientos
            
        self.rol_usuario = rol_usuario
        self.setWindowTitle("Broker Seguros - Sistema de Gestión")
        self.setGeometry(100, 100, 1200, 800)
        self._inicializar_ui()
        
        # Cargar datos iniciales
        self.viewmodel_corredor.cargar_corredores()

    def _inicializar_ui(self):
        """Inicializa la interfaz de usuario"""
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        # Layout principal
        layout_principal = QHBoxLayout()
        widget_central.setLayout(layout_principal)
        
        # Aplicar estilo al fondo de la ventana
        background_color = theme_manager.get_theme_colors().get("--background")
        border_color = theme_manager.get_theme_colors().get("--border-color")
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {background_color};
            }}
            QDialog {{
                background-color: {background_color};
                border: 1px solid {border_color};
                border-radius: 5px;
            }}
        """)

        # Panel de navegación (izquierda)
        panel_navegacion = QWidget()
        layout_navegacion = QVBoxLayout()
        panel_navegacion.setLayout(layout_navegacion)
        panel_navegacion.setFixedWidth(200)

        # Título del panel de navegación
        titulo_nav = QLabel("Menú Principal")
        titulo_nav.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_nav.setObjectName("titulo_nav")
        # Aplicar estilo directamente al título
        background_title = theme_manager.get_theme_colors().get("--nav-title-bg")
        text_color = theme_manager.get_theme_colors().get("--text-color")
        titulo_nav.setStyleSheet(f"""
            QLabel#titulo_nav {{
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background-color: {background_title};
                color: {text_color};
                border-radius: 5px;
                margin-bottom: 10px;
            }}
        """)

        layout_navegacion.addWidget(titulo_nav)

        # Botones de navegación
        self.boton_corredores = QPushButton("Corredores")
        self.boton_clientes = QPushButton("Clientes")
        self.boton_movimientos = QPushButton("Movimientos Vigencias")

        # Aplicar estilos directamente a los botones
        primary_color = theme_manager.get_theme_colors().get("--primary-color")
        hover_color = theme_manager.get_theme_colors().get("--hover-color")
        pressed_color = theme_manager.get_theme_colors().get("--pressed-color")
        
        nav_button_style = f"""
            QPushButton {{
                background-color: {primary_color};
                color: white;
                border: none;
                padding: 12px;
                text-align: left;
                font-size: 12px;
                margin-bottom: 8px;
                border-radius: 5px;
            }}
            
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            
            QPushButton:pressed, QPushButton[active="true"] {{
                background-color: {pressed_color};
            }}
        """
        
        self.boton_corredores.setStyleSheet(nav_button_style)
        self.boton_clientes.setStyleSheet(nav_button_style)
        self.boton_movimientos.setStyleSheet(nav_button_style)
        
        # Añadir iconos a los botones
        primary_color = theme_manager.get_theme_colors().get("--primary-color")
        
        self.boton_corredores.setIcon(IconHelper.get_icon("user", primary_color))
        self.boton_clientes.setIcon(IconHelper.get_icon("users", primary_color))
        self.boton_movimientos.setIcon(IconHelper.get_icon("calendar", primary_color))
        
        # Hacer que los botones sean más grandes y atractivos
        for btn in [self.boton_corredores, self.boton_clientes, self.boton_movimientos]:
            btn.setMinimumHeight(50)
            btn.setIconSize(QSize(24, 24))
        
        # Establecer el botón de corredores como active por defecto
        self.boton_corredores.setProperty("active", "true")

        # Conectar botones a sus funciones
        self.boton_corredores.clicked.connect(lambda: self.cambiar_vista("corredores"))
        self.boton_clientes.clicked.connect(lambda: self.cambiar_vista("clientes"))
        self.boton_movimientos.clicked.connect(
            lambda: self.cambiar_vista("movimientos")
        )

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
            self.viewmodel_corredor, es_admin=es_admin
        )
        self.stack_vistas.addWidget(self.vista_corredores)

        # Vista de movimientos
        self.vista_movimientos = VistaMovimientosVigencia(
            self.viewmodel_movimientos, es_admin=es_admin
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
                self.boton_corredores.setProperty("active", True)
                self.boton_clientes.setProperty("active", False)
                self.boton_movimientos.setProperty("active", False)
            elif vista == "clientes":
                self.stack_vistas.setCurrentWidget(self.vista_clientes)
                self.boton_corredores.setProperty("active", False)
                self.boton_clientes.setProperty("active", True)
                self.boton_movimientos.setProperty("active", False)
            elif vista == "movimientos":
                self.stack_vistas.setCurrentWidget(self.vista_movimientos)
                self.boton_corredores.setProperty("active", False)
                self.boton_clientes.setProperty("active", False)
                self.boton_movimientos.setProperty("active", True)

            # Forzar actualización de estilos
            self.boton_corredores.style().unpolish(self.boton_corredores)
            self.boton_corredores.style().polish(self.boton_corredores)
            self.boton_clientes.style().unpolish(self.boton_clientes)
            self.boton_clientes.style().polish(self.boton_clientes)
            self.boton_movimientos.style().unpolish(self.boton_movimientos)
            self.boton_movimientos.style().polish(self.boton_movimientos)

        except Exception as e:
            logger.error(f"Error al cambiar vista: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cambiar de vista: {str(e)}\n"
                "Por favor, contacte al soporte técnico.",
            )
