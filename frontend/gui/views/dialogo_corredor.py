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
from PyQt6.QtCore import pyqtSignal, QAbstractItemModel, Qt
from typing import Optional, Dict
import logging
from datetime import datetime
from ..models.corredor import Corredor
from ..viewmodels.corredor.corredor_itemmodel import CorredorItemModel

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
                email="",  # Campo requerido
                nombre="",  # Campo requerido
                telefono="",  # Campo requerido
                direccion="",  # Campo requerido
                activo=True,
            )
        self.corredor = corredor
        self.model = model or CorredorItemModel()
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.model)
        self.es_nuevo = not corredor.id

        self.setWindowTitle("Nuevo Corredor" if self.es_nuevo else "Editar Corredor")
        self.setModal(True)
        # Establecer dimensiones máximas y mínimas para la ventana
        self.setMinimumWidth(400)
        self.setMaximumWidth(500)
        self.setMinimumHeight(350)
        self.setMaximumHeight(500)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal - reducir márgenes y espaciado
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)

        # Form layout para los campos - reducir espaciado
        form_layout = QFormLayout()
        form_layout.setSpacing(4)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Campos del formulario
        self.campos = {}
        
        # Estilo compacto para todos los campos
        campo_style = "height: 28px; padding: 4px; font-size: 12px;"

        # Número de corredor
        self.campos["numero"] = QSpinBox()
        self.campos["numero"].setMinimum(1)
        self.campos["numero"].setMaximum(99999)
        self.campos["numero"].setFixedHeight(28)
        form_layout.addRow("Número *:", self.campos["numero"])

        # Nombre completo
        self.campos["nombre"] = QLineEdit()
        self.campos["nombre"].setPlaceholderText("Nombre completo del corredor")
        self.campos["nombre"].setStyleSheet(campo_style)
        form_layout.addRow("Nombre *:", self.campos["nombre"])

        # Teléfono
        self.campos["telefono"] = QLineEdit()
        self.campos["telefono"].setPlaceholderText("Número de teléfono")
        self.campos["telefono"].setStyleSheet(campo_style)
        form_layout.addRow("Teléfono *:", self.campos["telefono"])

        # Email
        self.campos["email"] = QLineEdit()
        self.campos["email"].setPlaceholderText("correo@ejemplo.com")
        self.campos["email"].setStyleSheet(campo_style)
        form_layout.addRow("Email *:", self.campos["email"])
        
        # Documento (campo obligatorio para el backend)
        self.campos["documento"] = QLineEdit()
        self.campos["documento"].setPlaceholderText("Número de documento")
        self.campos["documento"].setStyleSheet(campo_style)
        form_layout.addRow("Documento *:", self.campos["documento"])
        
        # Contraseña (obligatoria solo para nuevos corredores)
        self.campos["password"] = QLineEdit()
        if self.es_nuevo:
            self.campos["password"].setPlaceholderText("Contraseña para acceso al sistema")
        else:
            self.campos["password"].setPlaceholderText("Dejar vacío para mantener la actual")
        self.campos["password"].setEchoMode(QLineEdit.EchoMode.Password)
        self.campos["password"].setStyleSheet(campo_style)
        label_password = "Contraseña *:" if self.es_nuevo else "Cambiar contraseña:"
        form_layout.addRow(label_password, self.campos["password"])
        
        # Rol (admin o corredor)
        from PyQt6.QtWidgets import QComboBox
        self.campos["rol"] = QComboBox()
        self.campos["rol"].addItem("Corredor", "corredor")
        self.campos["rol"].addItem("Administrador", "admin")
        self.campos["rol"].setCurrentIndex(0)  # Por defecto, rol de corredor
        self.campos["rol"].setStyleSheet(campo_style)
        form_layout.addRow("Rol *:", self.campos["rol"])

        # Dirección
        self.campos["direccion"] = QLineEdit()
        self.campos["direccion"].setPlaceholderText("Dirección completa")
        self.campos["direccion"].setStyleSheet(campo_style)
        form_layout.addRow("Dirección *:", self.campos["direccion"])
        
        # Estado activo/inactivo
        from PyQt6.QtWidgets import QCheckBox
        self.campos["activo"] = QCheckBox("Activo")
        self.campos["activo"].setChecked(True)
        form_layout.addRow("Estado:", self.campos["activo"])

        layout.addLayout(form_layout)

        # Nota para contraseña
        from PyQt6.QtWidgets import QLabel
        if self.es_nuevo:
            nota_password = QLabel("* La contraseña permitirá al corredor acceder al sistema")
        else:
            nota_password = QLabel("* Complete la contraseña solo si desea cambiarla, de lo contrario déjela vacía")
        nota_password.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        layout.addWidget(nota_password)

        # Botones de acción - más compactos
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        # Estilo compacto para los botones
        buttons.setStyleSheet("""
            QPushButton { 
                min-height: 28px; 
                max-height: 30px; 
                padding: 3px 10px;
                font-size: 12px;
            }
        """)
        buttons.accepted.connect(self.validar_y_aceptar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Agregar un pequeño espaciado antes de los botones
        layout.addSpacing(5)

        # Configurar el mapper después de crear los widgets
        self.setup_mapper()

    def setup_mapper(self):
        """Configura el QDataWidgetMapper para enlazar los widgets con el modelo"""
        # Mapear solo los widgets que corresponden a campos en el modelo
        self.mapper.addMapping(self.campos["numero"], 0)  # Número de corredor
        self.mapper.addMapping(self.campos["nombre"], 1)  # Nombre completo
        self.mapper.addMapping(self.campos["telefono"], 2)  # Teléfono
        self.mapper.addMapping(self.campos["email"], 3)    # Email
        self.mapper.addMapping(self.campos["direccion"], 4)  # Dirección
        
        # Para el estado activo, necesitamos mapeo especial o manejarlo manualmente
        # self.mapper.addMapping(self.campos["activo"], 5)  # Activo
        # Establecer estado inicial
        self.campos["activo"].setChecked(self.corredor.activo)
        
        # Si es un corredor existente, rellenar los campos no mapeados
        if self.corredor.id:
            # Establecer el rol actual (si está disponible)
            if hasattr(self.corredor, 'rol'):
                index = 1 if self.corredor.rol == 'admin' else 0
                self.campos["rol"].setCurrentIndex(index)
        
        # Conectar el cambio de número para cargar datos automáticamente
        # En modo edición, queremos cargar datos cuando cambia el número
        if not self.es_nuevo:
            self.campos["numero"].valueChanged.connect(self.cargar_datos_por_numero)
        
        # Si es un nuevo corredor, agregarlo al modelo
        if not self.corredor.id:
            self.model.insertRow(self.model.rowCount())
            self.mapper.setCurrentIndex(self.model.rowCount() - 1)
        else:
            # Buscar el índice del corredor existente
            corredor_encontrado = False
            for row in range(self.model.rowCount()):
                if str(self.model.data(self.model.index(row, 0))) == str(self.corredor.numero):
                    self.mapper.setCurrentIndex(row)
                    corredor_encontrado = True
                    break
                    
            # Si no se encontró el corredor en el modelo, cargar los datos directamente
            if not corredor_encontrado:
                # Cargar datos directamente desde el objeto Corredor
                self.campos["numero"].setValue(self.corredor.numero)
                self.campos["nombre"].setText(self.corredor.nombre)
                self.campos["email"].setText(self.corredor.email)
                self.campos["telefono"].setText(self.corredor.telefono)
                self.campos["direccion"].setText(self.corredor.direccion)
                self.campos["activo"].setChecked(self.corredor.activo)

    def validar_campos(self) -> tuple[bool, str]:
        """
        Valida los campos del formulario

        Returns:
            tuple: (válido, mensaje de error)
        """
        # Validar campos requeridos
        if self.campos["numero"].value() <= 0:
            return False, "El número de corredor es requerido"
        if not self.campos["nombre"].text().strip():
            return False, "El nombre es requerido"
        if not self.campos["telefono"].text().strip():
            return False, "El teléfono es requerido"
        if not self.campos["email"].text().strip():
            return False, "El email es requerido"
        if not self.campos["direccion"].text().strip():
            return False, "La dirección es requerida"
        if not self.campos["documento"].text().strip():
            return False, "El documento es requerido"
            
        # Validar contraseña solo para nuevos corredores
        if self.es_nuevo and not self.campos["password"].text():
            return False, "La contraseña es requerida para nuevos corredores"

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

    def cargar_datos_por_numero(self, numero):
        """
        Carga automáticamente los datos de un corredor cuando se cambia el número
        """
        if numero <= 0:
            return
            
        logger.info(f"Buscando corredor con número: {numero}")
        
        # Buscar corredor en los datos del modelo
        corredor_encontrado = None
        row_encontrada = -1
        
        # Primero comprobamos si tenemos acceso al ViewModel completo
        viewmodel = None
        try:
            from ..core.di_container import contenedor
            from ..viewmodels.corredor.corredor_viewmodel import CorredorViewModel
            viewmodel = contenedor.resolver(CorredorViewModel)
            
            # Intentar buscar el corredor en el ViewModel
            if viewmodel:
                for corredor in viewmodel.corredores:
                    if corredor.numero == numero:
                        corredor_encontrado = corredor
                        break
                        
                if corredor_encontrado:
                    logger.info(f"Corredor encontrado en ViewModel: {corredor_encontrado.nombre}")
                    # Actualizar todos los campos manualmente
                    self.campos["nombre"].setText(corredor_encontrado.nombre)
                    self.campos["email"].setText(corredor_encontrado.email)
                    self.campos["telefono"].setText(corredor_encontrado.telefono)
                    self.campos["direccion"].setText(corredor_encontrado.direccion)
                    self.campos["documento"].setText(corredor_encontrado.documento if hasattr(corredor_encontrado, 'documento') else "")
                    self.campos["activo"].setChecked(corredor_encontrado.activo)
                    
                    # Ajustar rol si está disponible
                    if hasattr(corredor_encontrado, 'rol'):
                        index = 1 if corredor_encontrado.rol == 'admin' else 0
                        self.campos["rol"].setCurrentIndex(index)
                    return
        except Exception as e:
            logger.error(f"Error al buscar corredor en ViewModel: {e}")
            
        # Si no encontramos a través del ViewModel, buscamos en el modelo local
        for row in range(self.model.rowCount()):
            # Buscamos el corredor en todas las filas del modelo
            if str(self.model.data(self.model.index(row, 0))) == str(numero):
                # Encontramos el corredor, guardar su fila
                row_encontrada = row
                logger.info(f"Corredor encontrado en modelo local, fila: {row}")
                break
                
        if row_encontrada >= 0:
            # Usar el mapper para cargar los datos automáticamente
            self.mapper.setCurrentIndex(row_encontrada)
            
            # Ajustar campos no mapeados como activo y rol
            index_data = self.model.index(row_encontrada, 5)  # Columna para activo
            if index_data.isValid():
                activo = self.model.data(index_data)
                if isinstance(activo, str):
                    activo = activo.lower() == 'activo'
                self.campos["activo"].setChecked(activo)
            
            # Mostrar mensaje de datos cargados
            nombre = self.model.data(self.model.index(row_encontrada, 1))
            logger.info(f"Cargados datos de corredor: {nombre}")
        else:
            logger.warning(f"No se encontró corredor con número: {numero}")
            # Mostrar mensaje de error o advertencia
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, 
                "Corredor no encontrado", 
                f"No se encontró ningún corredor con el número {numero}.",
                QMessageBox.StandardButton.Ok
            )
    
    def obtener_datos(self) -> Dict:
        """
        Obtiene los datos del formulario directamente de los campos

        Returns:
            Dict: Diccionario con los datos del corredor
        """
        logger.info("Obteniendo datos del formulario...")
        
        # Nombre completo para corredor
        nombre = self.campos["nombre"].text().strip()
        
        # Obtener el rol seleccionado
        rol_index = self.campos["rol"].currentIndex()
        rol = "admin" if rol_index == 1 else "corredor"
        
        # Datos básicos que siempre se envían
        datos = {
            "numero": self.campos["numero"].value(),
            "nombre": nombre,
            "telefono": self.campos["telefono"].text().strip(),
            "email": self.campos["email"].text().strip(),
            "direccion": self.campos["direccion"].text().strip(),
            "documento": self.campos["documento"].text().strip(),  # Campo requerido por el backend
            "activo": self.campos["activo"].isChecked(),
            "rol": rol,  # Asegurarse de que sea 'rol' y no 'role'
        }
        
        # Solo agregar fecha_registro si es un nuevo corredor
        if self.es_nuevo:
            datos["fecha_registro"] = datetime.now().strftime("%Y-%m-%d")
        
        # Agregar contraseña SOLO si está presente y no está vacía
        password = self.campos["password"].text().strip()
        if password:
            datos["password"] = password
            
        logger.info(f"Datos obtenidos: {datos}")
        return datos
