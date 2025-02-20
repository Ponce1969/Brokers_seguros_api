"""
Diálogo para crear/editar corredores
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QDialogButtonBox,
    QMessageBox,
    QSpinBox,
)
from typing import Optional, Dict
import logging
from ..models.corredor import Corredor

# Configurar logging
logger = logging.getLogger(__name__)

class DialogoCorredor(QDialog):
    """Diálogo para crear o editar un corredor"""

    def __init__(self, parent=None, corredor: Optional[Corredor] = None):
        super().__init__(parent)
        self.corredor = corredor
        self.setWindowTitle("Nuevo Corredor" if not corredor else "Editar Corredor")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Form layout para los campos
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Campos del formulario
        self.campos = {}

        # Número de corredor
        self.campos["numero"] = QSpinBox()
        self.campos["numero"].setMinimum(1)
        self.campos["numero"].setMaximum(99999)
        form_layout.addRow("Número *:", self.campos["numero"])

        # Email (usuario)
        self.campos["email"] = QLineEdit()
        self.campos["email"].setPlaceholderText("correo@ejemplo.com")
        form_layout.addRow("Email *:", self.campos["email"])

        # Contraseña
        self.campos["password"] = QLineEdit()
        self.campos["password"].setEchoMode(QLineEdit.EchoMode.Password)
        self.campos["password"].setPlaceholderText("Contraseña para el corredor")
        form_layout.addRow("Contraseña *:", self.campos["password"])

        # Nombre
        self.campos["nombre"] = QLineEdit()
        self.campos["nombre"].setPlaceholderText("Nombre completo")
        form_layout.addRow("Nombre *:", self.campos["nombre"])

        # Teléfono
        self.campos["telefono"] = QLineEdit()
        self.campos["telefono"].setPlaceholderText("+56 9 1234 5678")
        form_layout.addRow("Teléfono:", self.campos["telefono"])

        # Dirección
        self.campos["direccion"] = QLineEdit()
        self.campos["direccion"].setPlaceholderText("Dirección completa")
        form_layout.addRow("Dirección:", self.campos["direccion"])

        layout.addLayout(form_layout)

        # Botones de acción
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validar_y_aceptar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Si estamos editando, llenar los campos
        if self.corredor:
            self.llenar_campos()

    def llenar_campos(self):
        """Llena los campos con los datos del corredor"""
        if self.corredor.numero:
            self.campos["numero"].setValue(self.corredor.numero)
        self.campos["email"].setText(self.corredor.email)
        self.campos["nombre"].setText(self.corredor.nombre)
        if self.corredor.telefono:
            self.campos["telefono"].setText(self.corredor.telefono)
        if self.corredor.direccion:
            self.campos["direccion"].setText(self.corredor.direccion)
        # No llenamos la contraseña por seguridad

    def validar_campos(self) -> tuple[bool, str]:
        """
        Valida los campos del formulario
        
        Returns:
            tuple: (válido, mensaje de error)
        """
        # Validar campos requeridos
        if self.campos["numero"].value() <= 0:
            return False, "El número de corredor es requerido"
        if not self.campos["email"].text().strip():
            return False, "El email es requerido"
        if not self.campos["password"].text().strip() and not self.corredor:
            return False, "La contraseña es requerida para nuevos corredores"
        if not self.campos["nombre"].text().strip():
            return False, "El nombre es requerido"

        # Validar formato de email
        email = self.campos["email"].text().strip()
        if "@" not in email or "." not in email:
            return False, "El email no tiene un formato válido"

        # Validar longitud mínima de contraseña para nuevos corredores
        if not self.corredor and len(self.campos["password"].text()) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"

        return True, ""

    def validar_y_aceptar(self):
        """Valida los campos y acepta el diálogo si son válidos"""
        valido, mensaje = self.validar_campos()
        if valido:
            self.accept()
        else:
            QMessageBox.warning(self, "Error de Validación", mensaje)

    def obtener_datos(self) -> Dict:
        """
        Obtiene los datos del formulario
        
        Returns:
            Dict: Diccionario con los datos del corredor
        """
        datos = {
            "numero": self.campos["numero"].value(),
            "email": self.campos["email"].text().strip(),
            "nombre": self.campos["nombre"].text().strip(),
            "telefono": self.campos["telefono"].text().strip() or None,
            "direccion": self.campos["direccion"].text().strip() or None,
        }
        
        # Solo incluir contraseña si se ha proporcionado una
        password = self.campos["password"].text().strip()
        if password:
            datos["password"] = password
            
        return datos
