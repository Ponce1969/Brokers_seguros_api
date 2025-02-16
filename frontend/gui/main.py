from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QFormLayout
)
from PyQt6.QtCore import Qt
from dotenv import load_dotenv
import os
import requests
import json
from frontend.gui.viewmodels.usuario_viewmodel import UsuarioViewModel
from frontend.gui.models.usuario import Usuario
from frontend.gui.views.usuario_view import VistaUsuarios
from frontend.gui.services.api_service import ServicioAPI
from frontend.gui.repositories.usuario_repository import RepositorioUsuario

# Cargar variables del archivo .env
load_dotenv()
USUARIO_ADMIN = os.getenv("USUARIO_ADMIN")
CONTRASENA_ADMIN = os.getenv("CONTRASENA_ADMIN")

# Configuración inicial
API_URL = "http://localhost:8000/api/v1"

class VistaLogin(QWidget):
    def __init__(self, viewmodel: UsuarioViewModel, servicio_api: ServicioAPI):
        super().__init__()
        self.viewmodel = viewmodel
        self.servicio_api = servicio_api
        self.setWindowTitle("Inicio de Sesión")
        self.setGeometry(100, 100, 320, 200)
        self._inicializar_ui()

    def _inicializar_ui(self) -> None:
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Título centrado
        self.titulo = QLabel("Registrar en Ramas Seguros Generales")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.titulo)

        # Formulario con menos espacio entre elementos
        form_layout = QFormLayout()
        form_layout.setSpacing(5)

        self.entrada_usuario = QLineEdit()
        self.entrada_usuario.setFixedHeight(25)
        form_layout.addRow("Usuario:", self.entrada_usuario)

        self.entrada_contrasena = QLineEdit()
        self.entrada_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        self.entrada_contrasena.setFixedHeight(25)
        form_layout.addRow("Contraseña:", self.entrada_contrasena)
        
        layout.addLayout(form_layout)

        # Botones con menor altura
        self.boton_login = QPushButton("Iniciar Sesión")
        self.boton_login.setFixedHeight(30)
        self.boton_login.clicked.connect(self._iniciar_sesion)
        layout.addWidget(self.boton_login)

        self.boton_crear_admin = QPushButton("Crear Superusuario")
        self.boton_crear_admin.setFixedHeight(30)
        self.boton_crear_admin.clicked.connect(self._crear_superusuario)
        layout.addWidget(self.boton_crear_admin)

    def _obtener_token(self, email: str, password: str) -> str:
        """Obtiene el token de autenticación del backend"""
        try:
            # El backend espera los datos en form-data, no en JSON
            data = {
                "username": email,
                "password": password
            }
            response = requests.post(
                f"{API_URL}/login/access-token",
                data=data  # Cambiado de json a data para enviar como form-data
            )
            response.raise_for_status()
            token_data = response.json()
            if not token_data or 'access_token' not in token_data:
                raise ValueError("La respuesta no contiene un token válido")
            return token_data["access_token"]
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error de Conexión", 
                               f"Error al conectar con el servidor: {str(e)}")
            return None
        except ValueError as e:
            QMessageBox.critical(self, "Error de Autenticación", 
                               f"Error en la respuesta del servidor: {str(e)}")
            return None
        except Exception as e:
            QMessageBox.critical(self, "Error Inesperado", 
                               f"Ocurrió un error inesperado: {str(e)}")
            return None

    def _iniciar_sesion(self) -> None:
        """Maneja el proceso de inicio de sesión"""
        usuario = self.entrada_usuario.text().strip()
        contrasena = self.entrada_contrasena.text()

        if not usuario or not contrasena:
            QMessageBox.warning(self, "Error", "Por favor ingrese usuario y contraseña.")
            return

        # Obtener token de autenticación
        token = self._obtener_token(usuario, contrasena)
        if token:
            try:
                # Establecer el token en el servicio API
                self.servicio_api.establecer_token(token)
                QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
                self.abrir_ventana_principal()
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Error al iniciar la aplicación: {str(e)}")

    def _crear_superusuario(self) -> None:
        if not self.viewmodel.items:
            nuevo_usuario = Usuario(
                email=USUARIO_ADMIN,
                nombre="Administrador",
                apellido="Superusuario",
                is_active=True,
                is_superuser=True
            )
            self.viewmodel.crear_item(nuevo_usuario)
            QMessageBox.information(self, "Éxito", "Superusuario creado exitosamente.")
        else:
            QMessageBox.warning(self, "Error", "Ya hay usuarios registrados.")

    def abrir_ventana_principal(self):
        vista_usuarios = VistaUsuarios(self.viewmodel)
        vista_usuarios.show()

if __name__ == "__main__":
    import sys
    import logging
    from PyQt6.QtWidgets import QApplication
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Crear la aplicación
        app = QApplication(sys.argv)
        
        # Configurar servicios
        logger.info("Iniciando servicios...")
        servicio_api = ServicioAPI(API_URL)
        repositorio_usuario = RepositorioUsuario(servicio_api)
        viewmodel_usuario = UsuarioViewModel(repositorio_usuario)
        
        # Crear y mostrar la ventana de login
        logger.info("Iniciando interfaz de usuario...")
        ventana_login = VistaLogin(viewmodel_usuario, servicio_api)
        ventana_login.show()
        
        # Ejecutar la aplicación
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Error fatal al iniciar la aplicación: {str(e)}")
        QMessageBox.critical(None, "Error Fatal", 
                           f"No se pudo iniciar la aplicación: {str(e)}")
        sys.exit(1)
