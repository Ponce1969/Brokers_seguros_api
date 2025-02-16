from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QFormLayout
)
from PyQt6.QtCore import Qt
from dotenv import load_dotenv
import os
from ..viewmodels.usuario_viewmodel import UsuarioViewModel
from ..models.usuario import Usuario
from .usuario_view import VistaUsuarios  # Importar la vista de usuarios

# Cargar variables del archivo .env
load_dotenv()
USUARIO_ADMIN = os.getenv("USUARIO_ADMIN")
CONTRASENA_ADMIN = os.getenv("CONTRASENA_ADMIN")

class VistaLogin(QWidget):
    def __init__(self, viewmodel: UsuarioViewModel):
        super().__init__()
        self.viewmodel = viewmodel
        self.setWindowTitle("Inicio de Sesión")
        self.setGeometry(100, 100, 320, 200)  # Reducir tamaño
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
        form_layout.setSpacing(5)  # Espaciado reducido

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
        layout.addWidget(self.boton_login)

        self.boton_crear_admin = QPushButton("Crear Superusuario")
        self.boton_crear_admin.setFixedHeight(30)
        layout.addWidget(self.boton_crear_admin)

    def _iniciar_sesion(self) -> None:
        usuario = self.entrada_usuario.text()
        contrasena = self.entrada_contrasena.text()

        if usuario == USUARIO_ADMIN and contrasena == CONTRASENA_ADMIN:
            QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
            self.abrir_ventana_principal()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Credenciales incorrectas.")

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

