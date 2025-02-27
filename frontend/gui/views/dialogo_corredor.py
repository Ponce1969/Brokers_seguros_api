"""
Diálogo para crear/editar corredores
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
    QSpinBox,
    QDataWidgetMapper,
)
from PyQt6.QtCore import pyqtSignal, QAbstractItemModel
from typing import Optional, Dict
import logging
from datetime import datetime
from ..models.corredor import Corredor
from ..viewmodels.corredor_viewmodel import CorredorItemModel

# Configurar logging
logger = logging.getLogger(__name__)


class DialogoCorredor(QDialog):
    """Diálogo para crear o editar un corredor"""

    # Señal para notificar que se han guardado los datos
    datos_guardados = pyqtSignal(dict)

    def __init__(
        self,
        parent=None,
        corredor: Optional[Corredor] = None,
        model: Optional[QAbstractItemModel] = None,
    ):
        super().__init__(parent)
        # Si no hay corredor, crear uno vacío con valores por defecto
        if corredor is None:
            corredor = Corredor(
                id=0,  # Se generará al guardar
                numero=0,  # Se generará al guardar
                email="",  # Cambiado de 'mail' a 'email' para coincidir con la definición de la clase
                nombre="",  # Campo requerido
                telefono="",  # Campo requerido
                direccion="",  # Campo requerido
                nombres="",
                apellidos="",
                documento="",
                localidad="",
                matricula="",  # Opcional ahora
                activo=True,
            )
        self.corredor = corredor
        self.model = model or CorredorItemModel()
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.model)

        self.setWindowTitle("Nuevo Corredor" if not corredor.id else "Editar Corredor")
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

        # Nombres
        self.campos["nombres"] = QLineEdit()
        self.campos["nombres"].setPlaceholderText("Nombres")
        form_layout.addRow("Nombres *:", self.campos["nombres"])

        # Apellidos
        self.campos["apellidos"] = QLineEdit()
        self.campos["apellidos"].setPlaceholderText("Apellidos")
        form_layout.addRow("Apellidos *:", self.campos["apellidos"])

        # Documento
        self.campos["documento"] = QLineEdit()
        self.campos["documento"].setPlaceholderText("Número de documento")
        form_layout.addRow("Documento *:", self.campos["documento"])

        # Dirección
        self.campos["direccion"] = QLineEdit()
        self.campos["direccion"].setPlaceholderText("Dirección completa")
        form_layout.addRow("Dirección:", self.campos["direccion"])

        # Localidad
        self.campos["localidad"] = QLineEdit()
        self.campos["localidad"].setPlaceholderText("Localidad")
        form_layout.addRow("Localidad:", self.campos["localidad"])

        # Teléfonos
        self.campos["telefonos"] = QLineEdit()
        self.campos["telefonos"].setPlaceholderText("Teléfonos fijos")
        form_layout.addRow("Teléfonos:", self.campos["telefonos"])

        # Móvil
        self.campos["movil"] = QLineEdit()
        self.campos["movil"].setPlaceholderText("Teléfono móvil")
        form_layout.addRow("Móvil:", self.campos["movil"])

        # Email
        self.campos["email"] = QLineEdit()
        self.campos["email"].setPlaceholderText("correo@ejemplo.com")
        form_layout.addRow("Email *:", self.campos["email"])

        # Observaciones
        self.campos["observaciones"] = QLineEdit()
        self.campos["observaciones"].setPlaceholderText("Observaciones adicionales")
        form_layout.addRow("Observaciones:", self.campos["observaciones"])

        # Matrícula (opcional)
        self.campos["matricula"] = QLineEdit()
        self.campos["matricula"].setPlaceholderText("Número de matrícula (opcional)")
        form_layout.addRow("Matrícula:", self.campos["matricula"])

        # Especialización
        self.campos["especializacion"] = QLineEdit()
        self.campos["especializacion"].setPlaceholderText("Área de especialización")
        form_layout.addRow("Especialización:", self.campos["especializacion"])

        layout.addLayout(form_layout)

        # Botones de acción
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validar_y_aceptar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Configurar el mapper después de crear los widgets
        self.setup_mapper()

    def setup_mapper(self):
        """Configura el QDataWidgetMapper para enlazar los widgets con el modelo"""
        # Mapear cada widget a su columna correspondiente en el modelo
        self.mapper.addMapping(self.campos["numero"], 0)
        self.mapper.addMapping(self.campos["nombres"], 1)
        self.mapper.addMapping(self.campos["apellidos"], 2)
        self.mapper.addMapping(self.campos["documento"], 3)
        self.mapper.addMapping(self.campos["direccion"], 4)
        self.mapper.addMapping(self.campos["localidad"], 5)
        self.mapper.addMapping(self.campos["telefonos"], 6)
        self.mapper.addMapping(self.campos["movil"], 7)
        self.mapper.addMapping(self.campos["email"], 8)
        self.mapper.addMapping(self.campos["observaciones"], 9)
        self.mapper.addMapping(self.campos["matricula"], 10)
        self.mapper.addMapping(self.campos["especializacion"], 11)

        # Si es un nuevo corredor, agregarlo al modelo
        if not self.corredor.id:
            self.model.insertRow(self.model.rowCount())
            self.mapper.setCurrentIndex(self.model.rowCount() - 1)
        else:
            # Buscar el índice del corredor existente
            for row in range(self.model.rowCount()):
                if self.model.data(self.model.index(row, 0)) == self.corredor.numero:
                    self.mapper.setCurrentIndex(row)
                    break

    def validar_campos(self) -> tuple[bool, str]:
        """
        Valida los campos del formulario

        Returns:
            tuple: (válido, mensaje de error)
        """
        # Validar campos requeridos
        if self.campos["numero"].value() <= 0:
            return False, "El número de corredor es requerido"
        if not self.campos["nombres"].text().strip():
            return False, "Los nombres son requeridos"
        if not self.campos["apellidos"].text().strip():
            return False, "Los apellidos son requeridos"
        if not self.campos["documento"].text().strip():
            return False, "El documento es requerido"
        # La matrícula ya no es requerida
        if not self.campos["email"].text().strip():
            return False, "El email es requerido"

        # Validar formato de email
        email = self.campos["email"].text().strip()
        if "@" not in email or "." not in email:
            return False, "El email no tiene un formato válido"

        return True, ""

    def validar_y_aceptar(self):
        """Valida los campos y acepta el diálogo si son válidos"""
        logger.info("🔍 === INICIANDO VALIDACIÓN Y GUARDADO ===")
        logger.info("1. Iniciando validación de campos...")

        try:
            valido, mensaje = self.validar_campos()
            logger.info(
                f"2. Resultado validación: {'✅ Válido' if valido else '❌ Inválido'} - {mensaje if not valido else ''}"
            )

            if valido:
                logger.info("3. Campos válidos, obteniendo datos...")
                datos = self.obtener_datos()
                logger.info(f"4. Datos obtenidos: {datos}")

                logger.info("5. Preparando emisión de señal...")
                logger.info(f"   - Tipo de señal: {type(self.datos_guardados)}")

                logger.info("6. Emitiendo señal...")
                self.datos_guardados.emit(datos)
                logger.info("7. Señal emitida exitosamente")

                logger.info("8. Cerrando diálogo...")
                self.accept()
                logger.info("9. Diálogo cerrado exitosamente")

                # Verificación adicional después del cierre
                logger.info("10. Estado final:")
                logger.info(f"    - Diálogo resultado: {self.result()}")
                logger.info(f"    - Diálogo visible: {self.isVisible()}")
            else:
                logger.warning(f"⚠️ Validación fallida: {mensaje}")
                QMessageBox.warning(self, "Error de Validación", mensaje)

        except Exception as e:
            import traceback
            logger.error(f"❌ Error en validar_y_aceptar: {e}")
            logger.error(f"Stack trace:\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Error", f"Error inesperado: {e}")

    def obtener_datos(self) -> Dict:
        """
        Obtiene los datos del formulario directamente de los campos

        Returns:
            Dict: Diccionario con los datos del corredor
        """
        logger.info("Obteniendo datos del formulario...")
        datos = {
            "numero": self.campos["numero"].value(),
            "nombres": self.campos["nombres"].text().strip(),
            "apellidos": self.campos["apellidos"].text().strip(),
            "documento": self.campos["documento"].text().strip(),
            "direccion": self.campos["direccion"].text().strip() or None,
            "localidad": self.campos["localidad"].text().strip() or None,
            "telefonos": self.campos["telefonos"].text().strip() or None,
            "movil": self.campos["movil"].text().strip() or None,
            "email": self.campos["email"].text().strip(),
            "observaciones": self.campos["observaciones"].text().strip() or None,
            "matricula": self.campos["matricula"].text().strip() or "",
            "especializacion": self.campos["especializacion"].text().strip() or None,
            "fecha_alta": datetime.now().strftime("%Y-%m-%d"),
            "activo": True,
        }
        logger.info(f"Datos obtenidos: {datos}")
        return datos
