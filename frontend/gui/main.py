from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QFormLayout,
    QMainWindow,
    QStackedWidget,
)
from PyQt6.QtCore import Qt
from dotenv import load_dotenv
import os
import requests
import asyncio
import logging
from frontend.gui.viewmodels.usuario_viewmodel import UsuarioViewModel
from frontend.gui.viewmodels.corredor_viewmodel import CorredorViewModel
from frontend.gui.models.usuario import Usuario
from frontend.gui.models.corredor import Corredor
from frontend.gui.views.usuario_view import VistaUsuarios
from frontend.gui.views.corredor_view import VistaCorredores
from frontend.gui.services.api_service import ServicioAPI
from frontend.gui.repositories.usuario_repository import RepositorioUsuario
from frontend.gui.repositories.corredor_repository import RepositorioCorredor

# Cargar variables del archivo .env
load_dotenv()
USUARIO_ADMIN = os.getenv("USUARIO_ADMIN")
CONTRASENA_ADMIN = os.getenv("CONTRASENA_ADMIN")

# Configuración inicial
API_URL = "http://localhost:8000/api/v1"


class VentanaPrincipal(QMainWindow):
    """Ventana principal que contiene todas las vistas"""

    def __init__(self, viewmodel_usuario: UsuarioViewModel, viewmodel_corredor: CorredorViewModel):
        super().__init__()
        self.setWindowTitle("Broker Seguros")
        self.setGeometry(100, 100, 1200, 800)

        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout = QVBoxLayout(widget_central)

        # Barra de navegación
        barra_navegacion = QHBoxLayout()
        self.boton_usuarios = QPushButton("Usuarios")
        self.boton_corredores = QPushButton("Corredores")
        barra_navegacion.addWidget(self.boton_usuarios)
        barra_navegacion.addWidget(self.boton_corredores)
        layout.addLayout(barra_navegacion)

        # Stack de vistas
        self.stack = QStackedWidget()
        self.viewmodel_usuario = viewmodel_usuario
        self.viewmodel_corredor = viewmodel_corredor
        
        # Inicializar vistas como None
        self._vista_usuarios = None
        self._vista_corredores = None
        
        # Agregar un widget vacío inicialmente
        widget_placeholder = QWidget()
        self.stack.addWidget(widget_placeholder)
        layout.addWidget(self.stack)

        # Conectar señales
        self.boton_usuarios.clicked.connect(self._mostrar_vista_usuarios)
        self.boton_corredores.clicked.connect(self._mostrar_vista_corredores)

        # Mostrar la vista de usuarios por defecto
        self._mostrar_vista_usuarios()

    def _mostrar_vista_usuarios(self):
        """Muestra la vista de usuarios, creándola si no existe"""
        if not self._vista_usuarios:
            self._vista_usuarios = VistaUsuarios(self.viewmodel_usuario)
            self.stack.addWidget(self._vista_usuarios)
        self.stack.setCurrentWidget(self._vista_usuarios)

    def _mostrar_vista_corredores(self):
        """Muestra la vista de corredores, creándola si no existe"""
        if not self._vista_corredores:
            self._vista_corredores = VistaCorredores(self.viewmodel_corredor)
            self.stack.addWidget(self._vista_corredores)
        self.stack.setCurrentWidget(self._vista_corredores)


class VistaLogin(QWidget):
    def __init__(self, viewmodel_usuario: UsuarioViewModel, servicio_api: ServicioAPI):
        super().__init__()
        self.viewmodel_usuario = viewmodel_usuario
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
            data = {"username": email, "password": password}
            response = requests.post(
                f"{API_URL}/login/access-token",
                data=data,  # Cambiado de json a data para enviar como form-data
            )
            response.raise_for_status()
            token_data = response.json()
            if not token_data or "access_token" not in token_data:
                raise ValueError("La respuesta no contiene un token válido")
            return token_data["access_token"]
        except requests.RequestException as e:
            QMessageBox.critical(
                self,
                "Error de Conexión",
                f"Error al conectar con el servidor: {str(e)}",
            )
            return None
        except ValueError as e:
            QMessageBox.critical(
                self,
                "Error de Autenticación",
                f"Error en la respuesta del servidor: {str(e)}",
            )
            return None
        except Exception as e:
            QMessageBox.critical(
                self, "Error Inesperado", f"Ocurrió un error inesperado: {str(e)}"
            )
            return None

    def _ejecutar_corrutina(self, corrutina):
        """Ejecuta una corrutina en el event loop"""
        try:
            return asyncio.get_event_loop().run_until_complete(corrutina)
        except Exception as e:
            logger.error(f"Error al ejecutar corrutina: {str(e)}")
            raise

    async def _configurar_admin(self):
        """Configura el corredor para el admin"""
        try:
            datos_corredor = {
                "numero": 1001,
                "nombres": "Rodrigo",
                "apellidos": "Ponce",
                "documento": "12345678",
                "direccion": "Dirección de Rodrigo",
                "localidad": "Montevideo",
                "telefonos": "+5491136995733",
                "mail": "rpd.ramas@gmail.com",
                "fecha_alta": "2025-02-16"
            }
            repositorio_corredor = RepositorioCorredor(self.servicio_api)
            corredor = await repositorio_corredor.crear(Corredor(**datos_corredor))
            
            # Actualizar usuario con el número de corredor
            datos_usuario = {
                "id": 1,
                "username": "rponce",
                "email": "rpd.ramas@gmail.com",
                "nombres": "Rodrigo",
                "apellidos": "Ponce",
                "is_active": True,
                "is_superuser": False,
                "role": "admin",
                "corredor_numero": 1001,
                "comision_porcentaje": 0.0,
                "telefono": "+5491136995733"
            }
            await self.viewmodel_usuario._repositorio.actualizar(Usuario(**datos_usuario))
        except Exception as e:
            logger.error(f"Error al configurar corredor para admin: {str(e)}")

    def _iniciar_sesion(self) -> None:
        """Maneja el proceso de inicio de sesión"""
        usuario = self.entrada_usuario.text().strip()
        contrasena = self.entrada_contrasena.text()

        if not usuario or not contrasena:
            QMessageBox.warning(
                self, "Error", "Por favor ingrese usuario y contraseña."
            )
            return

        # Obtener token de autenticación
        token = self._obtener_token(usuario, contrasena)
        if token:
            try:
                # Establecer el token en el servicio API
                self.servicio_api.establecer_token(token)
                
                # Crear corredor para Rodrigo Ponce si no existe
                if usuario == "rpd.ramas@gmail.com":
                    try:
                        self._ejecutar_corrutina(self._configurar_admin())
                    except Exception as e:
                        logger.error(f"Error al configurar admin: {str(e)}")
                
                QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
                self.abrir_ventana_principal()
                self.hide()  # Ocultar la ventana de login en lugar de cerrarla
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Error al iniciar la aplicación: {str(e)}"
                )

    def _crear_superusuario(self) -> None:
        if not self.viewmodel_usuario.items:
            nuevo_usuario = Usuario(
                email=USUARIO_ADMIN,
                nombre="Administrador",
                apellido="Superusuario",
                is_active=True,
                is_superuser=True,
            )
            self.viewmodel_usuario.crear_item(nuevo_usuario)
            QMessageBox.information(self, "Éxito", "Superusuario creado exitosamente.")
        else:
            QMessageBox.warning(self, "Error", "Ya hay usuarios registrados.")

    def abrir_ventana_principal(self):
        # Crear viewmodel para corredores
        repositorio_corredor = RepositorioCorredor(self.servicio_api)
        viewmodel_corredor = CorredorViewModel(repositorio_corredor)

        # Crear y mostrar la ventana principal
        self.ventana_principal = VentanaPrincipal(self.viewmodel_usuario, viewmodel_corredor)
        self.ventana_principal.show()
        self.ventana_principal.raise_()  # Asegura que la ventana esté al frente


if __name__ == "__main__":
    import sys
    import logging
    from PyQt6.QtWidgets import QApplication

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
        QMessageBox.critical(
            None, "Error Fatal", f"No se pudo iniciar la aplicación: {str(e)}"
        )
        sys.exit(1)
