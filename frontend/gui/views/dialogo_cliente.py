"""Dialogo para crear/editar cliente"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDateEdit,
    QDialogButtonBox,
    QMessageBox,
    QSpinBox,
    QDataWidgetMapper,
    QComboBox,
    QTextEdit
)
from PyQt6.QtCore import pyqtSignal, QAbstractItemModel, Qt, QDate
from typing import Optional, Dict, List
import logging
from datetime import datetime, date
from ..models.cliente import Cliente
from ..models.tipo_documento import TipoDocumento
from ..viewmodels.cliente_itemmodel import ClienteItemModel
from ..viewmodels.tipo_documento_viewmodel import TipoDocumentoViewModel

# Configurar logging
logger = logging.getLogger(__name__)


class DialogoCliente(QDialog):
    """Dialogo para crear o editar un cliente"""

    # Señal para notificar que se han guardado los datos
    datos_guardados = pyqtSignal(dict)

    def __init__(
        self,
        parent=None,
        cliente: Optional[Cliente] = None,
        model: Optional[QAbstractItemModel] = None,
        corredor_id: int = None,
    ):
        super().__init__(parent)
        # Guardar el ID del corredor que crea este cliente
        self.corredor_id = corredor_id
        
        # Si no hay cliente, crear uno vacío con valores por defecto
        if cliente is None:
            cliente = Cliente(
                id="",  # ID (se generará al guardar)
                numero_cliente=0,  # Identificador de negocio (se generará al guardar)
                nombres="",  # Nombres (campo requerido)
                apellidos="",  # Apellidos (campo requerido)
                tipo_documento_id=0,  # Se asignará al cargar los tipos de documento
                numero_documento="",  # Número de documento (campo requerido)
                telefonos="",  # Teléfono fijo (campo requerido)
                movil="",  # Teléfono móvil (campo requerido)
                direccion="",  # Dirección (campo requerido)
                localidad="Montevideo",  # Localidad por defecto
                mail="",  # Email
                fecha_nacimiento=None,  # Fecha de nacimiento
                observaciones=""  # Observaciones
            )

        self.cliente = cliente
        self.model = model or ClienteItemModel()
        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(self.model)
        self.es_nuevo = not cliente.id
        
        # Obtener instancia del ViewModel para tipos de documento
        from ..core.di_container import contenedor
        self.tipo_documento_vm = contenedor.resolver(TipoDocumentoViewModel)
        
        # Conectar señales del ViewModel
        self.tipo_documento_vm.tipos_actualizados.connect(self.actualizar_combo_tipos_documento)
        self.tipo_documento_vm.error_ocurrido.connect(self.mostrar_error)

        self.setWindowTitle("Nuevo Cliente" if self.es_nuevo else "Editar Cliente")
        self.setModal(True)
        self.resize(550, 650)

        self.init_ui()
        
        # Cargar tipos de documento después de inicializar la UI
        self.tipo_documento_vm.cargar_tipos_documento()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)

        # Formulario
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Campos del formulario
        # Nombres
        self.nombres_input = QLineEdit(self.cliente.nombres)
        form_layout.addRow("Nombres:", self.nombres_input)

        # Apellidos
        self.apellidos_input = QLineEdit(self.cliente.apellidos)
        form_layout.addRow("Apellidos:", self.apellidos_input)

        # Tipo de documento (se cargará dinámicamente)
        self.tipo_doc_combo = QComboBox()
        form_layout.addRow("Tipo de Documento:", self.tipo_doc_combo)
        
        # Nota: Los items se cargarán cuando llegue la respuesta del backend
        # vía la señal tipos_actualizados conectada a actualizar_combo_tipos_documento

        # Número de documento
        self.documento_input = QLineEdit(self.cliente.numero_documento)
        form_layout.addRow("Número de Documento:", self.documento_input)

        # Fecha de nacimiento
        self.fecha_nac_input = QDateEdit()
        self.fecha_nac_input.setCalendarPopup(True)
        self.fecha_nac_input.setDisplayFormat("dd/MM/yyyy")
        if self.cliente.fecha_nacimiento:
            if isinstance(self.cliente.fecha_nacimiento, str):
                try:
                    fecha = QDate.fromString(self.cliente.fecha_nacimiento, "yyyy-MM-dd")
                    self.fecha_nac_input.setDate(fecha)
                except:
                    # Usar fecha actual como respaldo
                    self.fecha_nac_input.setDate(QDate.currentDate())
            elif isinstance(self.cliente.fecha_nacimiento, date):
                fecha = QDate(self.cliente.fecha_nacimiento.year, 
                              self.cliente.fecha_nacimiento.month, 
                              self.cliente.fecha_nacimiento.day)
                self.fecha_nac_input.setDate(fecha)
        else:
            # Si no hay fecha, usar fecha actual como valor por defecto
            self.fecha_nac_input.setDate(QDate.currentDate())
        form_layout.addRow("Fecha de Nacimiento:", self.fecha_nac_input)

        # Dirección
        self.direccion_input = QLineEdit(self.cliente.direccion or "")
        form_layout.addRow("Dirección:", self.direccion_input)

        # Localidad
        self.localidad_input = QLineEdit(self.cliente.localidad or "Montevideo")
        form_layout.addRow("Localidad:", self.localidad_input)

        # Teléfono fijo
        self.telefono_input = QLineEdit(self.cliente.telefonos or "")
        form_layout.addRow("Teléfono fijo:", self.telefono_input)

        # Teléfono móvil
        self.movil_input = QLineEdit(self.cliente.movil or "")
        form_layout.addRow("Teléfono móvil:", self.movil_input)

        # Email
        self.email_input = QLineEdit(self.cliente.mail or "")
        form_layout.addRow("Email:", self.email_input)

        # Observaciones
        self.observaciones_input = QTextEdit()
        self.observaciones_input.setPlainText(self.cliente.observaciones or "")
        self.observaciones_input.setAcceptRichText(False)
        form_layout.addRow("Observaciones:", self.observaciones_input)
        
        # Agregar formulario al layout principal
        main_layout.addLayout(form_layout)

        # Configuración de los botones de aceptar/cancelar
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        # Conectar evento de aceptación del diálogo
        self.accepted.connect(self.guardar_datos)
        
    def actualizar_combo_tipos_documento(self, tipos_documento: List[TipoDocumento]):
        """
        Actualiza el combobox con los tipos de documento recibidos del backend
        """
        logger.info(f"Actualizando combobox con {len(tipos_documento)} tipos de documento")
        
        # Guardar selección actual si existe
        tipo_id_actual = None
        if self.tipo_doc_combo.count() > 0:
            tipo_id_actual = self.tipo_doc_combo.currentData()
        elif self.cliente.tipo_documento_id:
            tipo_id_actual = self.cliente.tipo_documento_id
            
        # Limpiar combo
        self.tipo_doc_combo.clear()
        
        # Si no hay tipos, añadir un elemento de aviso
        if not tipos_documento:
            self.tipo_doc_combo.addItem("No hay tipos de documento disponibles", 0)
            logger.warning("No se recibieron tipos de documento del backend")
            return
            
        # Añadir tipos al combo
        tipo_default_encontrado = False
        index_a_seleccionar = 0
        
        for i, tipo in enumerate(tipos_documento):
            if tipo.esta_activo:  # Solo añadir tipos activos
                self.tipo_doc_combo.addItem(str(tipo), tipo.id)
                
                # Si coincide con el tipo actual, seleccionarlo
                if tipo_id_actual and tipo.id == tipo_id_actual:
                    index_a_seleccionar = self.tipo_doc_combo.count() - 1
                
                # Si es el tipo por defecto y no hay tipo actual, seleccionarlo
                if tipo.es_default and not tipo_id_actual:
                    index_a_seleccionar = self.tipo_doc_combo.count() - 1
                    tipo_default_encontrado = True
        
        # Si no hay tipo actual ni tipo por defecto, seleccionar el primero
        if not tipo_id_actual and not tipo_default_encontrado and self.tipo_doc_combo.count() > 0:
            index_a_seleccionar = 0
            
        # Establecer el tipo seleccionado
        if self.tipo_doc_combo.count() > 0:
            self.tipo_doc_combo.setCurrentIndex(index_a_seleccionar)
            logger.info(f"Tipo de documento seleccionado: {self.tipo_doc_combo.currentText()} (ID: {self.tipo_doc_combo.currentData()})")
    
    def mostrar_error(self, mensaje: str):
        """
        Muestra un mensaje de error en un diálogo
        """
        logger.error(f"Error: {mensaje}")
        QMessageBox.critical(self, "Error", mensaje)

    def obtener_datos(self) -> Dict:
        """Obtiene los datos del formulario
        
        Returns:
            Dict: Diccionario con los datos del cliente
        """
        # Obtener el tipo de documento seleccionado
        tipo_documento_id = self.tipo_doc_combo.currentData()
        
        # Verificar que haya un tipo de documento válido seleccionado
        if not tipo_documento_id:
            raise ValueError("Debe seleccionar un tipo de documento válido")
        
        # Convertir a entero para asegurar compatibilidad con el backend
        try:
            tipo_documento_id = int(tipo_documento_id)
        except (ValueError, TypeError):
            logger.error(f"Error al convertir tipo_documento_id a entero: {tipo_documento_id}")
            raise ValueError(f"El tipo de documento seleccionado no es válido: {tipo_documento_id}")
            
        fecha_nac = self.fecha_nac_input.date().toString("yyyy-MM-dd")
        if fecha_nac == QDate.currentDate().toString("yyyy-MM-dd"):
            fecha_nac = None  # No enviar la fecha actual como fecha de nacimiento
            
        # Recopilar datos del formulario
        datos = {
            "id": self.cliente.id,  # Mantener el ID existente
            "nombres": self.nombres_input.text().strip(),
            "apellidos": self.apellidos_input.text().strip(),
            "tipo_documento_id": tipo_documento_id,
            "numero_documento": self.documento_input.text().strip(),
            "fecha_nacimiento": fecha_nac,
            "direccion": self.direccion_input.text().strip(),
            "localidad": self.localidad_input.text().strip(),
            "telefonos": self.telefono_input.text().strip(),
            "movil": self.movil_input.text().strip(),
            "mail": self.email_input.text().strip(),
            "observaciones": self.observaciones_input.toPlainText().strip()
        }
        
        # Agregar el ID del corredor si está disponible (para asociar el cliente al corredor)
        if hasattr(self, 'corredor_id') and self.corredor_id is not None:
            datos['corredor_id'] = self.corredor_id
            logger.info(f"Asociando cliente al corredor ID: {self.corredor_id}")
        
        return datos

    def validar_campos(self) -> tuple:
        """
        Valida los campos del formulario

        Returns:
            tuple: (válido, mensaje de error)
        """
        # Validar campos requeridos
        if not self.nombres_input.text().strip():
            return False, "Los nombres son requeridos"
        if not self.apellidos_input.text().strip():
            return False, "Los apellidos son requeridos"
            
        # Validar tipo de documento
        if self.tipo_doc_combo.count() == 0:
            return False, "No hay tipos de documento disponibles. Contacte al administrador."
        if not self.tipo_doc_combo.currentData():
            return False, "Debe seleccionar un tipo de documento válido"
            
        if not self.documento_input.text().strip():
            return False, "El número de documento es requerido"
        if not self.direccion_input.text().strip():
            return False, "La dirección es requerida"
        if not self.telefono_input.text().strip() and not self.movil_input.text().strip():
            return False, "Debe proporcionar al menos un teléfono (fijo o móvil)"
        if not self.email_input.text().strip():
            return False, "El email es requerido"

        # Validar formato de email
        email = self.email_input.text().strip()
        if "@" not in email or "." not in email:
            return False, "El email no tiene un formato válido"

        return True, ""

    def guardar_datos(self):
        """Valida y guarda los datos del formulario"""
        try:
            # Validar datos
            valido, mensaje = self.validar_campos()
            if not valido:
                QMessageBox.warning(self, "Validación", mensaje)
                return
                
            # Obtener datos del formulario
            try:
                datos = self.obtener_datos()
            except ValueError as e:
                QMessageBox.warning(self, "Validación", str(e))
                return
            
            # Emitir señal con los datos
            self.datos_guardados.emit(datos)
            
            # Cerrar diálogo
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar los datos: {str(e)}")
            logger.error(f"Error al guardar datos: {e}")

    def cargar_datos_por_id(self, id: str):
        """Carga los datos del cliente por su ID
        
        Args:
            id: ID del cliente a cargar
        """
        # Implementar si es necesario para cargar desde el modelo
        pass

    def cargar_datos(self, cliente: Cliente):
        """Carga los datos de un cliente en el formulario
        
        Args:
            cliente: Cliente a cargar
        """
        self.cliente = cliente
        
        # Cargar datos en los campos
        self.nombres_input.setText(cliente.nombres or "")
        self.apellidos_input.setText(cliente.apellidos or "")
        
        # Establecer tipo de documento
        index = self.tipo_doc_combo.findData(cliente.tipo_documento_id)
        if index >= 0:
            self.tipo_doc_combo.setCurrentIndex(index)
            
        self.documento_input.setText(cliente.numero_documento or "")
        
        # Cargar fecha de nacimiento
        if cliente.fecha_nacimiento:
            if isinstance(cliente.fecha_nacimiento, str):
                fecha = QDate.fromString(cliente.fecha_nacimiento, "yyyy-MM-dd")
                self.fecha_nac_input.setDate(fecha)
            elif isinstance(cliente.fecha_nacimiento, date):
                fecha = QDate(cliente.fecha_nacimiento.year, 
                            cliente.fecha_nacimiento.month, 
                            cliente.fecha_nacimiento.day)
                self.fecha_nac_input.setDate(fecha)
                
        self.direccion_input.setText(cliente.direccion or "")
        self.localidad_input.setText(cliente.localidad or "Montevideo")
        self.telefono_input.setText(cliente.telefonos or "")
        self.movil_input.setText(cliente.movil or "")
        self.email_input.setText(cliente.mail or "")
        self.observaciones_input.setPlainText(cliente.observaciones or "")
