"""
Vista de login de la aplicación
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFormLayout,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor
import logging
from ..services.auth_service import AuthService
from ..viewmodels.login_viewmodel import LoginViewModel
from ..core.di_container import contenedor
from .ventana_principal import VentanaPrincipal
from ..viewmodels.corredor_viewmodel import CorredorViewModel
from ..utils import theme_manager, IconHelper

logger = logging.getLogger(__name__)

class LoginView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Sistema de Corredores")
        self.setFixedSize(420, 420)  # Tamaño mejorado
        
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
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(50, 40, 50, 40)
        
        primary_color = theme_manager.get_theme_colors().get("--primary-color")
        hover_color = theme_manager.get_theme_colors().get("--hover-color")
        pressed_color = theme_manager.get_theme_colors().get("--pressed-color")
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: #F0F0F5; }}
            QLabel {{ color: {primary_color}; font-size: 14px; }}
            QLineEdit {{
                border: 2px solid #90c2ff;
                border-radius: 6px;
                padding: 8px;
                background-color: #FFFFFF;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {primary_color};
            }}
            QPushButton {{
                background-color: {primary_color};
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ 
                background-color: {hover_color};
            }}
            QPushButton:pressed {{ background-color: {pressed_color}; }}
        """)
        
        title_label = QLabel("Ingreso al Sistema")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Broker Seguros")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.campos = {}
        self.campos["mail"] = QLineEdit()
        self.campos["mail"].setPlaceholderText("ejemplo@correo.com")
        form_layout.addRow("Email:", self.campos["mail"])
        
        self.campos["password"] = QLineEdit()
        self.campos["password"].setEchoMode(QLineEdit.EchoMode.Password)
        self.campos["password"].setPlaceholderText("Ingrese su contraseña")
        form_layout.addRow("Contraseña:", self.campos["password"])
        
        main_layout.addLayout(form_layout)
        
        self.login_button = QPushButton("Ingresar")
        self.login_button.setMinimumHeight(40)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setIcon(IconHelper.get_icon("login", "white"))
        self.login_button.setIconSize(QSize(18, 18))
        self.login_button.clicked.connect(self._handle_login)
        main_layout.addWidget(self.login_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Aplicar efectos de sombra a los componentes principales
        self.apply_shadow(self.login_button, radius=10, offset=3)
        self.apply_shadow(self.campos["mail"], radius=8, offset=2)
        self.apply_shadow(self.campos["password"], radius=8, offset=2)

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
        
    def apply_shadow(self, widget, radius=10, offset=3):
        """Aplica un efecto de sombra a un widget
        
        Args:
            widget: Widget al que aplicar la sombra
            radius: Radio de difuminado de la sombra
            offset: Desplazamiento de la sombra en pixeles
        """
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(radius)
        shadow.setXOffset(offset)
        shadow.setYOffset(offset)
        shadow.setColor(QColor(0, 0, 0, 60))  # Sombra semitransparente: negro con 60/255 de opacidad
        widget.setGraphicsEffect(shadow)
