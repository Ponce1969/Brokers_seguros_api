"""
Diálogo base para formularios
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QTabWidget,
)
import logging

logger = logging.getLogger(__name__)


class DialogoBase(QDialog):
    """Clase base para diálogos de formulario"""

    def __init__(self, parent=None, titulo: str = ""):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setMinimumWidth(600)
        self._inicializar_ui()

    def _inicializar_ui(self):
        """Inicializa la interfaz base del diálogo"""
        # Layout principal
        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)

        # Widget de pestañas
        self.tabs = QTabWidget()
        self.layout_principal.addWidget(self.tabs)

        # Crear pestañas
        self._crear_pestanas()

        # Botones de acción
        self.layout_botones = QHBoxLayout()
        self.boton_guardar = QPushButton("Guardar")
        self.boton_cancelar = QPushButton("Cancelar")

        # Conectar señales de los botones
        self.boton_guardar.clicked.connect(self._guardar)
        self.boton_cancelar.clicked.connect(self.reject)

        # Agregar botones al layout
        self.layout_botones.addWidget(self.boton_guardar)
        self.layout_botones.addWidget(self.boton_cancelar)
        self.layout_principal.addLayout(self.layout_botones)

    def _crear_pestanas(self):
        """
        Método a ser implementado por las clases hijas.
        Debe crear y configurar las pestañas del diálogo.
        """
        raise NotImplementedError("Las clases hijas deben implementar _crear_pestanas")

    def _validar_campos(self) -> bool:
        """
        Método a ser implementado por las clases hijas.
        Debe validar los campos del formulario y retornar True si son válidos.
        """
        raise NotImplementedError("Las clases hijas deben implementar _validar_campos")

    def _obtener_datos(self) -> dict:
        """
        Método a ser implementado por las clases hijas.
        Debe retornar un diccionario con los datos del formulario.
        """
        raise NotImplementedError("Las clases hijas deben implementar _obtener_datos")

    def _guardar(self):
        """Maneja el proceso de guardado"""
        try:
            if self._validar_campos():
                datos = self._obtener_datos()
                if datos:
                    self.accept()
        except Exception as e:
            logger.error(f"Error al guardar: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error al guardar los datos: {str(e)}")

    def obtener_datos(self) -> dict:
        """
        Método público para obtener los datos del formulario.
        Retorna None si la validación falla.
        """
        if self._validar_campos():
            return self._obtener_datos()
        return None
