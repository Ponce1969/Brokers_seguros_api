"""
Vista de login de la aplicación
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFormLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import logging

from ..services.auth_service import AuthService
from ..viewmodels.login_viewmodel import LoginViewModel
from ..core.di_container import contenedor
from .ventana_principal import VentanaPrincipal
from ..viewmodels.corredor_viewmodel import CorredorViewModel

# Configurar logging
logger = logging.getLogger(__name__)


class LoginView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Sistema de Corredores")
        self.setFixedSize(400, 400)

        # Crear instancias de servicios
        self.auth_service = AuthService()
        self.viewmodel = LoginViewModel(self.auth_service)
        
        # Conectar señales del ViewModel
        self.viewmodel.login_successful.connect(self._handle_login_success)
        self.viewmodel.login_failed.connect(self._handle_login_error)
        
        self.init_ui()

        # Referencia a la ventana principal
        self.ventana_principal = None

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Widget y layout principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Título
        title_label = QLabel("Ingreso al Sistema")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Subtítulo
        subtitle_label = QLabel("Broker Seguros")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)

        # Espaciador
        main_layout.addSpacing(20)

        # Form layout para los campos
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Campos del formulario
        self.campos = {}

        # Email
        self.campos["mail"] = QLineEdit()
        self.campos["mail"].setPlaceholderText("ejemplo@correo.com")
        self.campos["mail"].setMinimumHeight(35)
        form_layout.addRow("Email:", self.campos["mail"])

        # Contraseña
        self.campos["password"] = QLineEdit()
        self.campos["password"].setEchoMode(QLineEdit.EchoMode.Password)
        self.campos["password"].setPlaceholderText("Ingrese su contraseña")
        self.campos["password"].setMinimumHeight(35)
        form_layout.addRow("Contraseña:", self.campos["password"])

        main_layout.addLayout(form_layout)

        # Espaciador
        main_layout.addSpacing(20)

        # Botón de login
        self.login_button = QPushButton("Ingresar")
        self.login_button.setMinimumHeight(40)
        # Cargar estilos desde el archivo QSS
        try:
            with open('frontend/gui/resources/styles.qss', 'r') as f:
                self.login_button.setStyleSheet(f.read())
        except Exception as e:
            logger.warning(f"No se pudo cargar el archivo de estilos: {e}")
            
        self.login_button.clicked.connect(self._handle_login)
        main_layout.addWidget(self.login_button)

        # Espaciador final
        main_layout.addStretch()

    def _handle_login(self):
        """Maneja el evento de login"""
        # Validar email y contraseña
        email = self.campos["mail"].text().strip()
        password = self.campos["password"].text()

        valido, mensaje = self.viewmodel.validar_campos(email, password)
        if not valido:
            QMessageBox.critical(self, "Error", mensaje)
            return

        # Realizar login
        self.login_button.setEnabled(False)
        try:
            self.viewmodel.login(email, password)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")
            self.login_button.setEnabled(True)

    def _handle_login_success(self, data: dict):
        """Maneja el login exitoso"""
        try:
            # Crear el ViewModel del corredor con el token
            corredor_viewmodel = CorredorViewModel()
            if "access_token" in data:
                corredor_viewmodel.api.set_token(data["access_token"])

            # Crear la ventana principal
            self.ventana_principal = VentanaPrincipal(
                viewmodel_corredor=corredor_viewmodel,
                rol_usuario=self.viewmodel.get_user_role(),
            )

            # Mostrar la ventana principal
            self.ventana_principal.show()

            # Cerrar la ventana de login
            self.close()

        except Exception as e:
            logger.error(f"Error al iniciar la aplicación: {e}")
            QMessageBox.critical(
                self, "Error", f"Error al iniciar la aplicación: {str(e)}"
            )
        finally:
            self.login_button.setEnabled(True)

    def _handle_login_error(self, error_msg: str):
        """Maneja los errores de login"""
        QMessageBox.critical(self, "Error", error_msg)
        self.login_button.setEnabled(True)
