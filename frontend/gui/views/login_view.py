"""
Vista de login de la aplicación
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFormLayout,
    QHBoxLayout, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize, QCoreApplication
from PyQt6.QtGui import QFont, QColor, QIcon
import logging
from ..services.auth_service import AuthService
from ..viewmodels.login_viewmodel import LoginViewModel
from ..core.di_container import contenedor
from .ventana_principal import VentanaPrincipal
from ..viewmodels.corredor_viewmodel import CorredorViewModel
from ..utils import IconHelper, apply_shadow, apply_button_shadow, apply_card_shadow, apply_input_shadow
from ..utils.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)

class LoginView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Sistema de Corredores")
        self.setFixedSize(500, 500)  # Tamaño aumentado para acomodar campos más anchos
        self.setObjectName("login_window")  # Para poder aplicar estilos específicos
        
        self.viewmodel = contenedor.resolver(LoginViewModel)
        if self.viewmodel is None:
            logger.error("No se pudo resolver LoginViewModel del contenedor")
            raise RuntimeError("Error al inicializar LoginViewModel")
        
        # Verificar que el auth_service dentro del viewmodel no sea None
        if self.viewmodel.auth_service is None:
            logger.error("AuthService es None en el LoginViewModel")
            raise RuntimeError("Error al inicializar AuthService en el LoginViewModel")
        
        self.viewmodel.login_successful.connect(self._handle_login_success)
        self.viewmodel.login_failed.connect(self._handle_login_error)
        
        self.init_ui()
        self.ventana_principal = None

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Definir colores directamente
        primary_color = "#1a73e8"    # Azul principal
        hover_color = "#1967d2"     # Azul hover
        pressed_color = "#185abc"   # Azul pressed
        input_bg = "#f6f8fa"        # Fondo inputs
        input_border = "#d2e3fc"    # Borde inputs
        input_focus = "#8ab4f8"     # Borde focus
        shadow_color = "rgba(60, 64, 67, 0.15)"  # Sombras
        second_text = "#5f6368"     # Texto secundario
        
        # Aplicar estilos específicos para el login
        self.setStyleSheet(f"""
            QMainWindow#login_window {{ 
                background-color: palette(window); /* Usar color de fondo de la paleta */
            }}
            QWidget#login_container {{ 
                background-color: palette(base); 
                border-radius: 10px; 
            }}
            QLabel {{ 
                color: palette(text); /* Usar color de texto de la paleta */
                font-size: 14px; 
                font-weight: 400;
            }}
            QLabel#title_label {{ 
                color: {primary_color}; 
                font-size: 22px; 
                font-weight: 600; 
                margin-bottom: 8px;
            }}
            /* Se eliminó el estilo del subtítulo */
            QLineEdit {{
                border: 2px solid #90c2ff;  /* Borde azul claro visible en modo claro */
                border-radius: 8px;
                padding: 12px;
                background-color: palette(base);
                color: palette(text);
                font-size: 14px;
                selection-background-color: {primary_color};
                selection-color: white;
                min-height: 20px;
            }}
            QLineEdit:hover {{
                border-color: {input_focus};
            }}
            QLineEdit:focus {{
                border-color: {input_focus};
                background-color: palette(base);
            }}
            QLineEdit::placeholder {{
                color: palette(mid-light);
                opacity: 0.7;
            }}
            QPushButton#login_button {{
                background-color: {primary_color};
                color: white;
                border-radius: 5px;
                padding: 6px;
                font-size: 13px;
                font-weight: 500;
                min-height: 32px;
                text-align: center;
            }}
            QPushButton#login_button:hover {{ 
                background-color: {hover_color};
            }}
            QPushButton#login_button:pressed {{ 
                background-color: {pressed_color}; 
                padding-top: 13px;
                padding-bottom: 11px;
            }}
        """)
        
        # Contenedor principal con fondo blanco y sombra - más ancho para los campos
        login_container = QWidget()
        login_container.setObjectName("login_container")
        container_layout = QVBoxLayout(login_container)
        container_layout.setContentsMargins(40, 35, 40, 35)  # Márgenes laterales aumentados
        container_layout.setSpacing(20)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(login_container)
        
        # Aplicar sombra al contenedor principal
        apply_shadow(login_container, radius=15, offset=0, color=QColor(0, 0, 0, 30))
        
        # Título principal
        title_label = QLabel("Ingreso al Sistema")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Espacio reducido entre título y campos
        container_layout.addSpacing(10)
        
        # Formulario de entrada
        form_layout = QFormLayout()
        form_layout.setSpacing(40)  # Aumentado a 40 para una separación mucho mayor
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Campos de entrada con estilos mejorados
        self.campos = {}
        
        # Configurar etiquetas y campos con ancho suficiente para correos electrónicos completos
        email_label = QLabel("Correo electrónico:")
        self.campos["mail"] = QLineEdit()
        self.campos["mail"].setPlaceholderText("ejemplo@correo.com")
        self.campos["mail"].setMinimumHeight(45)
        self.campos["mail"].setMinimumWidth(250)  # Ancho mínimo para que quepa un correo completo
        
        # Añadir el campo de correo al formulario
        form_layout.addRow(email_label, self.campos["mail"])
        
        # Añadir espacio adicional entre los campos
        form_layout.addItem(QSpacerItem(20, 15))
        
        password_label = QLabel("Contraseña:")
        self.campos["password"] = QLineEdit()
        self.campos["password"].setEchoMode(QLineEdit.EchoMode.Password)
        self.campos["password"].setPlaceholderText("Ingrese su contraseña")
        self.campos["password"].setMinimumHeight(45)
        self.campos["password"].setMinimumWidth(250)  # Mismo ancho que el campo de correo
        form_layout.addRow(password_label, self.campos["password"])
        
        # Ajustar el layout del formulario para dar más espacio a los campos
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        container_layout.addLayout(form_layout)
        
        # Añadir espacio adicional entre el formulario y el botón de login
        container_layout.addSpacing(40)
        
        # Botón de ingreso con mejor estilo
        self.login_button = QPushButton("Ingresar al Sistema")
        self.login_button.setObjectName("login_button")
        self.login_button.setMinimumHeight(32)
        self.login_button.setMinimumWidth(160)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        # Quitamos el icono problemático - solo texto es suficiente
        # self.login_button.setIcon(IconHelper.get_icon("login", "white"))
        # self.login_button.setIconSize(QSize(20, 20))
        self.login_button.clicked.connect(self._handle_login)
        container_layout.addWidget(self.login_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Espaciador para crear margen inferior
        container_layout.addSpacing(5)
        
        # Añadir botón para alternar temas (claro/oscuro)
        theme_button = QPushButton()
        theme_button.setObjectName("theme_button")
        theme_button.setFixedSize(40, 40)
        theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        theme_button.setToolTip("Alternar entre tema claro y oscuro")
        self._update_theme_button_icon(theme_button)
        theme_button.clicked.connect(lambda: self._toggle_theme(theme_button))
        
        # Aplicar estilo al botón de tema
        theme_button.setStyleSheet("""
            QPushButton#theme_button {
                background-color: transparent;
                border-radius: 20px;
                border: 1px solid palette(mid);
                padding: 5px;
            }
            QPushButton#theme_button:hover {
                background-color: palette(midlight);
            }
        """)
        
        # Añadir el botón de tema en la parte superior derecha
        theme_layout = QHBoxLayout()
        theme_layout.addStretch()
        theme_layout.addWidget(theme_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        container_layout.insertLayout(0, theme_layout)
        
        # Aplicar efectos de sombra a los componentes principales
        apply_button_shadow(self.login_button)  # Usar función especializada para botones
        
        # Connect Enter key to login
        self.campos["mail"].returnPressed.connect(self._handle_login)
        self.campos["password"].returnPressed.connect(self._handle_login)

    def _handle_login(self):
        email = self.campos["mail"].text().strip()
        password = self.campos["password"].text()
        valido, mensaje = self.viewmodel.validar_campos(email, password)
        if not valido:
            QMessageBox.critical(self, "Error", mensaje)
            return
        self.login_button.setEnabled(False)
        try:
            self.viewmodel.login(email, password)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")
            self.login_button.setEnabled(True)

    def _handle_login_success(self, data: dict):
        try:
            corredor_viewmodel = contenedor.resolver(CorredorViewModel)
            if "access_token" in data:
                corredor_viewmodel.api.set_token(data["access_token"])
            self.ventana_principal = VentanaPrincipal(viewmodel_corredor=corredor_viewmodel, rol_usuario=self.viewmodel.get_user_role())
            self.ventana_principal.show()
            self.close()
        except Exception as e:
            logger.error(f"Error al iniciar la aplicación: {e}")
            QMessageBox.critical(self, "Error", f"Error al iniciar la aplicación: {str(e)}")
        finally:
            self.login_button.setEnabled(True)

    def _handle_login_error(self, error_msg: str):
        QMessageBox.critical(self, "Error", error_msg)
        self.login_button.setEnabled(True)
    
    def _toggle_theme(self, theme_button):
        """Alterna entre tema claro y oscuro"""
        app = QCoreApplication.instance()
        ThemeManager.toggle_theme(app)
        self._update_theme_button_icon(theme_button)
        
    def _update_theme_button_icon(self, theme_button):
        """Actualiza el icono del botón según el tema actual"""
        app = QCoreApplication.instance()
        current_theme = ThemeManager.get_current_theme(app)
        
        if current_theme == Theme.DARK:
            # En tema oscuro, mostrar icono de sol (para cambiar a claro)
            theme_button.setIcon(IconHelper.get_icon("light_mode"))
        else:
            # En tema claro, mostrar icono de luna (para cambiar a oscuro)
            theme_button.setIcon(IconHelper.get_icon("dark_mode"))
            
        # Ajustar tamaño para iconos PNG (24x24 pixels)
        theme_button.setIconSize(QSize(24, 24))
    
    # El método apply_shadow ha sido eliminado y reemplazado por las funciones
    # del módulo shadow_helper para mayor consistencia y mantenibilidad
