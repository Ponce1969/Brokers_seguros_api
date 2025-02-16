"""
Vista principal para la gestión de usuarios
"""

import asyncio
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QLabel,
    QCheckBox,
    QHeaderView,
    QDialog,
    QFormLayout,
    QComboBox,
    QDoubleSpinBox,
)
import logging
from frontend.gui.viewmodels.usuario_viewmodel import UsuarioViewModel
from frontend.gui.models.usuario import Usuario

logger = logging.getLogger(__name__)

# Tipos de documentos soportados
TIPOS_DOCUMENTO = ["Cédula de Identidad", "DNI", "RUT", "CUIT", "Pasaporte", "Otro"]


class DialogoUsuario(QDialog):
    """Diálogo para crear/editar usuarios"""

    def __init__(self, parent=None, usuario: Usuario = None):
        super().__init__(parent)
        self.usuario = usuario
        self.setWindowTitle("Nuevo Usuario" if not usuario else "Editar Usuario")
        self.setMinimumWidth(400)
        self._inicializar_ui()

    def _inicializar_ui(self):
        layout = QFormLayout()
        self.setLayout(layout)

        # Campos del formulario
        self.campo_username = QLineEdit()
        self.campo_email = QLineEdit()
        self.campo_nombres = QLineEdit()
        self.campo_apellidos = QLineEdit()
        self.campo_telefono = QLineEdit()
        self.campo_password = QLineEdit()
        self.campo_password.setEchoMode(QLineEdit.EchoMode.Password)

        # Campos para el documento
        self.combo_tipo_documento = QComboBox()
        self.combo_tipo_documento.addItems(TIPOS_DOCUMENTO)
        self.campo_documento = QLineEdit()
        self.campo_documento.setPlaceholderText("Ingrese el número de documento")

        # Campo número de corredor
        self.campo_corredor_numero = QLineEdit()
        self.campo_corredor_numero.setPlaceholderText("Número del corredor existente")

        # Campos adicionales
        self.campo_comision = QDoubleSpinBox()
        self.campo_comision.setRange(0, 100)
        self.campo_comision.setSuffix("%")
        self.campo_comision.setDecimals(2)
        self.campo_rol = QComboBox()
        self.campo_rol.addItems(["corredor", "admin"])
        self.campo_activo = QCheckBox()
        self.campo_activo.setChecked(True)

        # Campos adicionales para el corredor
        self.campo_direccion = QLineEdit()
        self.campo_localidad = QLineEdit()

        # Agregar campos al layout
        layout.addRow("Username:", self.campo_username)
        layout.addRow("Email:", self.campo_email)
        layout.addRow("Nombres:", self.campo_nombres)
        layout.addRow("Apellidos:", self.campo_apellidos)
        layout.addRow("Tipo de Documento:", self.combo_tipo_documento)
        layout.addRow("Número de Documento:", self.campo_documento)
        layout.addRow("Dirección:", self.campo_direccion)
        layout.addRow("Localidad:", self.campo_localidad)
        layout.addRow("Teléfono:", self.campo_telefono)
        if not self.usuario:  # Solo mostrar campos para nuevos usuarios
            layout.addRow("Contraseña:", self.campo_password)
            layout.addRow("Corredor Numero:", self.campo_corredor_numero)
        layout.addRow("Comisión (%):", self.campo_comision)
        layout.addRow("Rol:", self.campo_rol)
        layout.addRow("Activo:", self.campo_activo)

        # Botones
        botones = QHBoxLayout()
        self.boton_guardar = QPushButton("Guardar")
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_guardar.clicked.connect(self.accept)
        self.boton_cancelar.clicked.connect(self.reject)
        botones.addWidget(self.boton_guardar)
        botones.addWidget(self.boton_cancelar)
        layout.addRow(botones)

        # Si estamos editando, llenar los campos
        if self.usuario:
            self.campo_username.setText(self.usuario.username)
            self.campo_email.setText(self.usuario.email)
            self.campo_nombres.setText(self.usuario.nombres)
            self.campo_apellidos.setText(self.usuario.apellidos)
            self.campo_telefono.setText(self.usuario.telefono or "")
            self.campo_comision.setValue(self.usuario.comision_porcentaje)
            self.campo_rol.setCurrentText(self.usuario.role)
            self.campo_activo.setChecked(self.usuario.is_active)
            self.campo_direccion.setText(self.usuario.direccion or "")
            self.campo_localidad.setText(self.usuario.localidad or "")

            # Manejar el documento
            if self.usuario.documento:
                # Intentar separar el tipo de documento del número
                try:
                    tipo, numero = self.usuario.documento.split(":", 1)
                    if tipo in TIPOS_DOCUMENTO:
                        self.combo_tipo_documento.setCurrentText(tipo)
                        self.campo_documento.setText(numero)
                    else:
                        self.combo_tipo_documento.setCurrentText("Otro")
                        self.campo_documento.setText(self.usuario.documento)
                except ValueError:
                    self.combo_tipo_documento.setCurrentText("Otro")
                    self.campo_documento.setText(self.usuario.documento)

    def validar_campos(self) -> bool:
        """Valida los campos del formulario"""
        campos_requeridos = {
            "username": self.campo_username,
            "email": self.campo_email,
            "nombres": self.campo_nombres,
            "apellidos": self.campo_apellidos,
            "documento": self.campo_documento,
            "dirección": self.campo_direccion,
            "localidad": self.campo_localidad,
        }

        # Validar campos vacíos
        for nombre, campo in campos_requeridos.items():
            if not campo.text().strip():
                QMessageBox.warning(
                    self, "Campos Requeridos", f"El campo {nombre} es requerido."
                )
                campo.setFocus()
                return False

        # Validar contraseña para nuevos usuarios
        if not self.usuario and not self.campo_password.text():
            QMessageBox.warning(
                self,
                "Contraseña Requerida",
                "Debe establecer una contraseña para el nuevo usuario.",
            )
            self.campo_password.setFocus()
            return False

        # Validar número de corredor para nuevos usuarios
        if not self.usuario:
            try:
                numero_corredor = int(self.campo_corredor_numero.text().strip())
                if numero_corredor < 1000 or numero_corredor > 9999:
                    QMessageBox.warning(
                        self,
                        "Número de Corredor Inválido",
                        "El número de corredor debe estar entre 1000 y 9999.",
                    )
                    self.campo_corredor_numero.setFocus()
                    return False
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Número de Corredor Inválido",
                    "El número de corredor debe ser un número entero.",
                )
                self.campo_corredor_numero.setFocus()
                return False

        return True

    def obtener_datos(self) -> dict:
        """Obtiene los datos del formulario"""
        if not self.validar_campos():
            return None

        # Formatear el documento con el tipo
        tipo_documento = self.combo_tipo_documento.currentText()
        numero_documento = self.campo_documento.text().strip()
        documento_completo = f"{tipo_documento}:{numero_documento}"

        datos = {
            "username": self.campo_username.text().strip(),
            "email": self.campo_email.text().strip(),
            "nombres": self.campo_nombres.text().strip(),
            "apellidos": self.campo_apellidos.text().strip(),
            "documento": documento_completo,
            "direccion": self.campo_direccion.text().strip(),
            "localidad": self.campo_localidad.text().strip(),
            "telefono": self.campo_telefono.text().strip(),
            "password": self.campo_password.text() if not self.usuario else None,
            "comision_porcentaje": self.campo_comision.value(),
            "role": self.campo_rol.currentText(),
            "is_active": self.campo_activo.isChecked(),
        }

        # Agregar número de corredor solo para nuevos usuarios
        if not self.usuario:
            datos["corredor_numero"] = int(self.campo_corredor_numero.text().strip())

        return datos


class VistaUsuarios(QWidget):
    """Vista principal para la gestión de usuarios"""

    def _ejecutar_corrutina(self, corrutina):
        """Ejecuta una corrutina en el event loop"""
        try:
            return asyncio.get_event_loop().run_until_complete(corrutina)
        except Exception as e:
            logger.error(f"Error al ejecutar corrutina: {str(e)}")
            raise

    def __init__(self, viewmodel: UsuarioViewModel):
        super().__init__()
        self.viewmodel = viewmodel
        self.setWindowTitle("Gestión de Usuarios")
        self._inicializar_ui()
        self._conectar_senales()
        try:
            self._ejecutar_corrutina(self.viewmodel.cargar_datos())
        except Exception as e:
            logger.error(f"Error al cargar datos iniciales: {str(e)}")
            QMessageBox.critical(
                self,
                "Error de Carga",
                f"No se pudieron cargar los usuarios: {str(e)}\n"
                "Por favor, verifica tu conexión y permisos.",
            )

    def _inicializar_ui(self) -> None:
        """Inicializa los componentes de la interfaz"""
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)

        # Barra superior con título y búsqueda
        layout_superior = QHBoxLayout()

        # Título
        titulo = QLabel("Gestión de Usuarios")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout_superior.addWidget(titulo)

        # Búsqueda
        self.entrada_busqueda = QLineEdit()
        self.entrada_busqueda.setPlaceholderText("Buscar usuarios...")
        layout_superior.addWidget(self.entrada_busqueda)

        # Botón nuevo
        self.boton_nuevo = QPushButton("Nuevo Usuario")
        layout_superior.addWidget(self.boton_nuevo)

        layout_principal.addLayout(layout_superior)

        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(9)
        self.tabla_usuarios.setHorizontalHeaderLabels(
            [
                "Corredor Numero",
                "Nombres",
                "Apellidos",
                "Documento",
                "Email",
                "Teléfono",
                "Comisión",
                "Rol",
                "Activo",
            ]
        )
        header = self.tabla_usuarios.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout_principal.addWidget(self.tabla_usuarios)

        # Botones de acción
        layout_botones = QHBoxLayout()
        self.boton_editar = QPushButton("Editar")
        self.boton_eliminar = QPushButton("Eliminar")
        self.boton_editar.setEnabled(False)
        self.boton_eliminar.setEnabled(False)
        layout_botones.addWidget(self.boton_editar)
        layout_botones.addWidget(self.boton_eliminar)
        layout_principal.addLayout(layout_botones)

        # Indicador de carga
        self.label_estado = QLabel()
        layout_principal.addWidget(self.label_estado)

    def _conectar_senales(self) -> None:
        """Conecta las señales del ViewModel con la vista"""
        self.viewmodel.datos_actualizados.connect(self._actualizar_tabla)
        self.viewmodel.error_ocurrido.connect(self._mostrar_error)
        self.viewmodel.cargando.connect(self._mostrar_estado_carga)

        self.entrada_busqueda.textChanged.connect(
            lambda texto: setattr(self.viewmodel, "filtro_busqueda", texto)
        )
        self.boton_nuevo.clicked.connect(self._mostrar_dialogo_usuario)
        self.boton_editar.clicked.connect(self._editar_usuario_seleccionado)
        self.boton_eliminar.clicked.connect(self._eliminar_usuario_seleccionado)
        self.tabla_usuarios.itemSelectionChanged.connect(self._actualizar_seleccion)

    def _actualizar_tabla(self) -> None:
        """Actualiza la tabla con los datos del ViewModel"""
        try:
            self.tabla_usuarios.setRowCount(0)
            for usuario in self.viewmodel.items:
                fila = self.tabla_usuarios.rowCount()
                self.tabla_usuarios.insertRow(fila)

                # Corredor Numero
                self.tabla_usuarios.setItem(
                    fila, 0, QTableWidgetItem(str(usuario.corredor_numero or ""))
                )
                # Nombres
                self.tabla_usuarios.setItem(fila, 1, QTableWidgetItem(usuario.nombres))
                # Apellidos
                self.tabla_usuarios.setItem(fila, 2, QTableWidgetItem(usuario.apellidos))
                # Documento
                self.tabla_usuarios.setItem(
                    fila, 3, QTableWidgetItem(usuario.documento or "")
                )
                # Email
                self.tabla_usuarios.setItem(fila, 4, QTableWidgetItem(usuario.email))
                # Teléfono
                self.tabla_usuarios.setItem(
                    fila, 5, QTableWidgetItem(usuario.telefono or "")
                )
                # Comisión
                self.tabla_usuarios.setItem(
                    fila, 6, QTableWidgetItem(f"{usuario.comision_porcentaje}%")
                )
                # Rol
                self.tabla_usuarios.setItem(fila, 7, QTableWidgetItem(usuario.role))

                # Checkbox para is_active
                checkbox_activo = QCheckBox()
                checkbox_activo.setChecked(usuario.is_active)
                checkbox_activo.setEnabled(False)
                self.tabla_usuarios.setCellWidget(fila, 8, checkbox_activo)

        except Exception as e:
            logger.error(f"Error al actualizar tabla: {str(e)}")
            self._mostrar_error(f"Error al actualizar la tabla: {str(e)}")

    def _mostrar_error(self, mensaje: str) -> None:
        """Muestra un mensaje de error"""
        logger.error(f"Error en la vista: {mensaje}")
        QMessageBox.critical(self, "Error", mensaje)

    def _mostrar_estado_carga(self, cargando: bool) -> None:
        """Actualiza el indicador de carga"""
        self.label_estado.setText("Cargando..." if cargando else "")
        self.setEnabled(not cargando)

    def _actualizar_seleccion(self) -> None:
        """Actualiza el usuario seleccionado en el ViewModel"""
        try:
            filas_seleccionadas = self.tabla_usuarios.selectedItems()
            if not filas_seleccionadas:
                self.viewmodel.seleccionar_item(None)
                self.boton_editar.setEnabled(False)
                self.boton_eliminar.setEnabled(False)
                return

            fila = filas_seleccionadas[0].row()
            usuario = next(
                (
                    u
                    for u in self.viewmodel.items
                    if str(u.corredor_numero)
                    == self.tabla_usuarios.item(fila, 0).text()
                ),
                None,
            )
            self.viewmodel.seleccionar_item(usuario)
            self.boton_editar.setEnabled(True)
            self.boton_eliminar.setEnabled(True)
        except Exception as e:
            logger.error(f"Error al actualizar selección: {str(e)}")
            self._mostrar_error(f"Error al seleccionar usuario: {str(e)}")

    def _mostrar_dialogo_usuario(self) -> None:
        """Muestra el diálogo para crear/editar usuario"""
        if not self.viewmodel.item_seleccionado:
            # Mostrar mensaje informativo sobre el proceso
            info = QMessageBox(self)
            info.setIcon(QMessageBox.Icon.Information)
            info.setWindowTitle("Información Importante")
            info.setText("Proceso de Creación de Usuario Corredor")
            info.setInformativeText(
                "Para crear un usuario corredor, recuerde:\n\n"
                "1. Primero debe crear el corredor con su número asignado (1000-9999)\n"
                "2. Luego crear el usuario asociado usando el mismo número de corredor\n\n"
                "¿Desea continuar con la creación del usuario?"
            )
            info.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if info.exec() == QMessageBox.StandardButton.No:
                return

        dialogo = DialogoUsuario(self, self.viewmodel.item_seleccionado)
        while True:  # Bucle para mantener el diálogo abierto si hay errores
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                datos = dialogo.obtener_datos()
                if datos is None:  # Validación falló
                    continue
                try:
                    if self.viewmodel.item_seleccionado:
                        self._ejecutar_corrutina(
                            self.viewmodel.actualizar_usuario(
                                self.viewmodel.item_seleccionado.id, **datos
                            )
                        )
                    else:
                        self._ejecutar_corrutina(
                            self.viewmodel.crear_usuario(**datos)
                        )
                    break  # Salir del bucle si la operación fue exitosa
                except Exception as e:
                    logger.error(f"Error al guardar usuario: {str(e)}")
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error al guardar usuario: {str(e)}\n"
                        "Por favor, corrija los datos e intente nuevamente.",
                    )
                    continue  # Mantener el diálogo abierto para corregir
            else:
                break  # Usuario canceló

    def _editar_usuario_seleccionado(self) -> None:
        """Abre el diálogo para editar el usuario seleccionado"""
        if self.viewmodel.item_seleccionado:
            self._mostrar_dialogo_usuario()

    def _eliminar_usuario_seleccionado(self) -> None:
        """Elimina el usuario seleccionado"""
        if not self.viewmodel.item_seleccionado:
            return

        try:
            respuesta = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Está seguro de eliminar el usuario "
                f"{self.viewmodel.item_seleccionado.nombres} {self.viewmodel.item_seleccionado.apellidos}?\n"
                "Esta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                self._ejecutar_corrutina(
                    self.viewmodel.eliminar_usuario(self.viewmodel.item_seleccionado.id)
                )
        except Exception as e:
            logger.error(f"Error al eliminar usuario: {str(e)}")
            self._mostrar_error(f"Error al eliminar usuario: {str(e)}")
