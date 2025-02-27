"""
Diálogo para la configuración inicial del sistema
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QSpinBox,
)
from PyQt6.QtCore import Qt
import logging
from gui.viewmodels.corredor_viewmodel import CorredorViewModel
from gui.core.excepciones import ErrorAPI, ErrorValidacion

logger = logging.getLogger(__name__)


class DialogoConfigInicial(QDialog):
    """Diálogo para la configuración inicial del sistema"""

    def __init__(self, viewmodel: CorredorViewModel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.setWindowTitle("Configuración Inicial del Sistema")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Conectar señales del viewmodel
        self.viewmodel.error_ocurrido.connect(self._mostrar_error)
        self.viewmodel.corredor_actualizado.connect(self._admin_creado)
        
        self._inicializar_ui()

    def _inicializar_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Título
        titulo = QLabel("Configuración del Administrador")
        titulo.setStyleSheet("font-size: 14px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        # Descripción
        descripcion = QLabel(
            "No se ha detectado ningún administrador en el sistema.\n"
            "Por favor, configure el usuario administrador inicial."
        )
        descripcion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        descripcion.setWordWrap(True)
        layout.addWidget(descripcion)

        # Formulario
        form_layout = QFormLayout()

        # Campo número de corredor
        self.campo_numero = QSpinBox()
        self.campo_numero.setRange(1000, 9999)
        self.campo_numero.setValue(1000)
        self.campo_numero.setFixedHeight(25)
        form_layout.addRow("Número de Corredor:", self.campo_numero)

        # Campos personales
        self.campo_nombres = QLineEdit()
        self.campo_apellidos = QLineEdit()
        self.campo_documento = QLineEdit()
        self.campo_email = QLineEdit()
        self.campo_telefono = QLineEdit()
        self.campo_direccion = QLineEdit()
        self.campo_localidad = QLineEdit()
        self.campo_password = QLineEdit()
        self.campo_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.campo_confirmar_password = QLineEdit()
        self.campo_confirmar_password.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Nombres:", self.campo_nombres)
        form_layout.addRow("Apellidos:", self.campo_apellidos)
        form_layout.addRow("Documento:", self.campo_documento)
        form_layout.addRow("Email:", self.campo_email)
        form_layout.addRow("Teléfono:", self.campo_telefono)
        form_layout.addRow("Dirección:", self.campo_direccion)
        form_layout.addRow("Localidad:", self.campo_localidad)
        form_layout.addRow("Contraseña:", self.campo_password)
        form_layout.addRow("Confirmar Contraseña:", self.campo_confirmar_password)

        layout.addLayout(form_layout)

        # Botones
        self.boton_crear = QPushButton("Crear Administrador")
        self.boton_crear.clicked.connect(self._crear_administrador)
        layout.addWidget(self.boton_crear)

    def _validar_campos(self) -> bool:
        """Valida los campos del formulario"""
        campos = {
            "nombres": self.campo_nombres,
            "apellidos": self.campo_apellidos,
            "documento": self.campo_documento,
            "email": self.campo_email,
            "teléfono": self.campo_telefono,
            "dirección": self.campo_direccion,
            "localidad": self.campo_localidad,
        }

        # Validar campos vacíos
        for nombre, campo in campos.items():
            if not campo.text().strip():
                QMessageBox.warning(
                    self, "Campos Requeridos", f"El campo {nombre} es requerido."
                )
                campo.setFocus()
                return False

        # Validar email
        if "@" not in self.campo_email.text():
            QMessageBox.warning(
                self, "Email Inválido", "Por favor ingrese un email válido."
            )
            self.campo_email.setFocus()
            return False

        # Validar contraseñas
        if not self.campo_password.text():
            QMessageBox.warning(
                self, "Contraseña Requerida", "Debe ingresar una contraseña."
            )
            self.campo_password.setFocus()
            return False

        if self.campo_password.text() != self.campo_confirmar_password.text():
            QMessageBox.warning(
                self,
                "Contraseñas No Coinciden",
                "Las contraseñas ingresadas no coinciden.",
            )
            self.campo_password.setFocus()
            return False

        return True

    def _crear_administrador(self):
        """Crea el usuario administrador"""
        if not self._validar_campos():
            return

        try:
            datos = {
                "numero": self.campo_numero.value(),
                "nombres": self.campo_nombres.text().strip(),
                "apellidos": self.campo_apellidos.text().strip(),
                "documento": self.campo_documento.text().strip(),
                "mail": self.campo_email.text().strip(),
                "telefonos": self.campo_telefono.text().strip(),
                "direccion": self.campo_direccion.text().strip(),
                "localidad": self.campo_localidad.text().strip(),
                "password": self.campo_password.text(),
                "role": "admin",
                "is_active": True,
            }

            # Deshabilitar el botón mientras se procesa
            self.boton_crear.setEnabled(False)
            self.boton_crear.setText("Creando administrador...")
            
            # Crear el administrador
            self.viewmodel.crear_corredor(datos)

        except Exception as e:
            self._mostrar_error(f"Error inesperado: {str(e)}")
            logger.error(f"Error inesperado al crear administrador: {str(e)}")
            self.boton_crear.setEnabled(True)
            self.boton_crear.setText("Crear Administrador")

    def _mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, "Error", mensaje)
        self.boton_crear.setEnabled(True)
        self.boton_crear.setText("Crear Administrador")

    def _admin_creado(self, corredor):
        """Maneja la creación exitosa del administrador"""
        QMessageBox.information(
            self,
            "Éxito",
            "Administrador creado exitosamente.\n"
            "Ahora puede iniciar sesión con su email y contraseña.",
        )
        self.accept()
