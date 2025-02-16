"""
Vista principal para la gestión de corredores
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
    QDialog,
    QFormLayout,
    QDateEdit,
    QHeaderView,
)
from PyQt6.QtCore import Qt
import logging
from datetime import date
from frontend.gui.viewmodels.corredor_viewmodel import CorredorViewModel
from frontend.gui.models.corredor import Corredor

logger = logging.getLogger(__name__)


class DialogoCorredor(QDialog):
    """Diálogo para crear/editar corredor"""

    def __init__(self, parent=None, corredor: Corredor = None):
        super().__init__(parent)
        self.corredor = corredor
        self.setWindowTitle("Nuevo" if not corredor else "Editar")
        self.setMinimumWidth(400)
        self._inicializar_ui()

    def _inicializar_ui(self):
        layout = QFormLayout()
        self.setLayout(layout)

        # Campos del formulario
        self.campo_numero = QLineEdit()
        self.campo_numero.setPlaceholderText("Numero entre 1000-9999")
        self.campo_nombres = QLineEdit()
        self.campo_apellidos = QLineEdit()
        self.campo_documento = QLineEdit()
        self.campo_direccion = QLineEdit()
        self.campo_localidad = QLineEdit()
        self.campo_telefonos = QLineEdit()
        self.campo_movil = QLineEdit()
        self.campo_mail = QLineEdit()
        self.campo_fecha_alta = QDateEdit()
        self.campo_fecha_alta.setDate(date.today())
        self.campo_fecha_alta.setCalendarPopup(True)

        # Agregar campos al layout
        layout.addRow("Numero:", self.campo_numero)
        layout.addRow("Nombres:", self.campo_nombres)
        layout.addRow("Apellidos:", self.campo_apellidos)
        layout.addRow("Documento:", self.campo_documento)
        layout.addRow("Dirección:", self.campo_direccion)
        layout.addRow("Localidad:", self.campo_localidad)
        layout.addRow("Teléfono:", self.campo_telefonos)
        layout.addRow("Móvil:", self.campo_movil)
        layout.addRow("Email:", self.campo_mail)
        layout.addRow("Fecha de Alta:", self.campo_fecha_alta)

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
        if self.corredor:
            self.campo_nombres.setText(self.corredor.nombres)
            self.campo_apellidos.setText(self.corredor.apellidos)
            self.campo_documento.setText(self.corredor.documento)
            self.campo_direccion.setText(self.corredor.direccion)
            self.campo_localidad.setText(self.corredor.localidad)
            self.campo_telefonos.setText(self.corredor.telefonos or "")
            self.campo_movil.setText(self.corredor.movil or "")
            self.campo_mail.setText(self.corredor.mail)
            if self.corredor.fecha_alta:
                self.campo_fecha_alta.setDate(self.corredor.fecha_alta)
            if self.corredor.numero:
                self.campo_numero.setText(str(self.corredor.numero))

    def validar_campos(self) -> bool:
        """Valida los campos del formulario"""
        campos_requeridos = {
            "numero": self.campo_numero,
            "nombres": self.campo_nombres,
            "apellidos": self.campo_apellidos,
            "documento": self.campo_documento,
            "dirección": self.campo_direccion,
            "localidad": self.campo_localidad,
            "email": self.campo_mail,
        }

        # Validar campos vacíos
        for nombre, campo in campos_requeridos.items():
            if not campo.text().strip():
                QMessageBox.warning(
                    self, "Campos Requeridos", f"El campo {nombre} es requerido."
                )
                campo.setFocus()
                return False

        # Validar número de corredor
        try:
            numero = int(self.campo_numero.text())
            if numero < 1000 or numero > 9999:
                QMessageBox.warning(
                    self,
                    "Numero Invalido",
                    "El numero debe estar entre 1000 y 9999.",
                )
                self.campo_numero.setFocus()
                return False
        except ValueError:
            QMessageBox.warning(
                self,
                "Numero Invalido",
                "El numero debe ser un numero entero.",
            )
            self.campo_numero.setFocus()
            return False

        # Validar formato de email
        if "@" not in self.campo_mail.text():
            QMessageBox.warning(
                self,
                "Email Inválido",
                "Por favor, ingrese una dirección de email válida.",
            )
            self.campo_mail.setFocus()
            return False

        return True

    def obtener_datos(self) -> dict:
        """Obtiene los datos del formulario"""
        if not self.validar_campos():
            return None

        datos = {
            "numero": int(self.campo_numero.text().strip()),
            "nombres": self.campo_nombres.text().strip(),
            "apellidos": self.campo_apellidos.text().strip(),
            "documento": self.campo_documento.text().strip(),
            "direccion": self.campo_direccion.text().strip(),
            "localidad": self.campo_localidad.text().strip(),
            "telefonos": self.campo_telefonos.text().strip() or None,
            "movil": self.campo_movil.text().strip() or None,
            "mail": self.campo_mail.text().strip(),
            "fecha_alta": self.campo_fecha_alta.date().toPyDate(),
        }

        return datos


class VistaCorredores(QWidget):
    """Vista principal para la gestión de corredores"""

    def _ejecutar_corrutina(self, corrutina):
        """Ejecuta una corrutina en el event loop"""
        try:
            return asyncio.get_event_loop().run_until_complete(corrutina)
        except Exception as e:
            logger.error(f"Error al ejecutar corrutina: {str(e)}")
            raise

    def __init__(self, viewmodel: CorredorViewModel):
        """Inicializa la vista"""
        super().__init__()
        self.viewmodel = viewmodel
        self.setWindowTitle("Corredores")
        self._inicializar_ui()
        self._conectar_senales()
        try:
            self._ejecutar_corrutina(self.viewmodel.cargar_datos())
        except Exception as e:
            logger.error(f"Error al cargar datos iniciales: {str(e)}")
            QMessageBox.critical(
                self,
                "Error de Carga",
                f"No se pudieron cargar los corredores: {str(e)}\n"
                "Por favor, verifica tu conexión y permisos.",
            )

    def _inicializar_ui(self) -> None:
        """Inicializa los componentes de la interfaz"""
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)

        # Barra superior con título y búsqueda
        layout_superior = QHBoxLayout()

        # Título
        titulo = QLabel("Corredores")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout_superior.addWidget(titulo)

        # Búsqueda
        self.entrada_busqueda = QLineEdit()
        self.entrada_busqueda.setPlaceholderText("Buscar...")
        layout_superior.addWidget(self.entrada_busqueda)

        # Botón nuevo
        self.boton_nuevo = QPushButton("Nuevo")
        layout_superior.addWidget(self.boton_nuevo)

        layout_principal.addLayout(layout_superior)

        # Tabla de corredores
        self.tabla_corredores = QTableWidget()
        self.tabla_corredores.setColumnCount(8)
        self.tabla_corredores.setHorizontalHeaderLabels(
            [
                "Numero",
                "Nombres",
                "Apellidos",
                "Documento",
                "Mail",
                "Telefonos",
                "Localidad",
                "Estado",
            ]
        )
        # Ajustar el ancho de las columnas
        header = self.tabla_corredores.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Numero
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nombres
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Apellidos
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Documento
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Mail
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Telefonos
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Localidad
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Estado
        layout_principal.addWidget(self.tabla_corredores)

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
        self.boton_nuevo.clicked.connect(self._mostrar_dialogo_corredor)
        self.boton_editar.clicked.connect(self._editar_corredor_seleccionado)
        self.boton_eliminar.clicked.connect(self._eliminar_corredor_seleccionado)
        self.tabla_corredores.itemSelectionChanged.connect(self._actualizar_seleccion)

    def _actualizar_tabla(self) -> None:
        """Actualiza la tabla con los datos del ViewModel"""
        try:
            self.tabla_corredores.setRowCount(0)
            for corredor in self.viewmodel.items:
                fila = self.tabla_corredores.rowCount()
                self.tabla_corredores.insertRow(fila)

                # Nº Corredor
                self.tabla_corredores.setItem(
                    fila, 0, QTableWidgetItem(str(corredor.numero or ""))
                )
                # Nombre
                self.tabla_corredores.setItem(fila, 1, QTableWidgetItem(corredor.nombres))
                # Apellido
                self.tabla_corredores.setItem(
                    fila, 2, QTableWidgetItem(corredor.apellidos)
                )
                # Documento
                self.tabla_corredores.setItem(
                    fila, 3, QTableWidgetItem(corredor.documento)
                )
                # Email
                self.tabla_corredores.setItem(fila, 4, QTableWidgetItem(corredor.mail))
                # Teléfono
                self.tabla_corredores.setItem(
                    fila, 5, QTableWidgetItem(corredor.telefonos or corredor.movil or "")
                )
                # Localidad
                self.tabla_corredores.setItem(
                    fila, 6, QTableWidgetItem(corredor.localidad)
                )
                # Estado
                self.tabla_corredores.setItem(fila, 7, QTableWidgetItem(corredor.estado))

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
        """Actualiza el corredor seleccionado en el ViewModel"""
        try:
            filas_seleccionadas = self.tabla_corredores.selectedItems()
            if not filas_seleccionadas:
                self.viewmodel.seleccionar_item(None)
                self.boton_editar.setEnabled(False)
                self.boton_eliminar.setEnabled(False)
                return

            fila = filas_seleccionadas[0].row()
            corredor = next(
                (
                    c
                    for c in self.viewmodel.items
                    if str(c.numero) == self.tabla_corredores.item(fila, 0).text()
                ),
                None,
            )
            self.viewmodel.seleccionar_item(corredor)
            self.boton_editar.setEnabled(True)
            self.boton_eliminar.setEnabled(True)
        except Exception as e:
            logger.error(f"Error al actualizar selección: {str(e)}")
            self._mostrar_error(f"Error al seleccionar corredor: {str(e)}")

    def _mostrar_dialogo_corredor(self) -> None:
        """Muestra el diálogo para crear/editar corredor"""
        dialogo = DialogoCorredor(self, self.viewmodel.item_seleccionado)
        while True:  # Bucle para mantener el diálogo abierto si hay errores
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                datos = dialogo.obtener_datos()
                if datos is None:  # Validación falló
                    continue
                try:
                    if self.viewmodel.item_seleccionado:
                        self._ejecutar_corrutina(
                            self.viewmodel.actualizar_corredor(
                                self.viewmodel.item_seleccionado.numero, **datos
                            )
                        )
                    else:
                        self._ejecutar_corrutina(
                            self.viewmodel.crear_corredor(**datos)
                        )
                    break  # Salir del bucle si la operación fue exitosa
                except Exception as e:
                    logger.error(f"Error al guardar corredor: {str(e)}")
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error al guardar corredor: {str(e)}\n"
                        "Por favor, corrija los datos e intente nuevamente.",
                    )
                    continue  # Mantener el diálogo abierto para corregir
            else:
                break  # Usuario canceló

    def _editar_corredor_seleccionado(self) -> None:
        """Abre el diálogo para editar el corredor seleccionado"""
        if self.viewmodel.item_seleccionado:
            self._mostrar_dialogo_corredor()

    def _eliminar_corredor_seleccionado(self) -> None:
        """Elimina el corredor seleccionado"""
        if not self.viewmodel.item_seleccionado:
            return

        try:
            respuesta = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Está seguro de eliminar "
                f"{self.viewmodel.item_seleccionado.nombre_completo}?\n"
                "Esta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                self._ejecutar_corrutina(
                    self.viewmodel.eliminar_corredor(
                        self.viewmodel.item_seleccionado.numero
                    )
                )
        except Exception as e:
            logger.error(f"Error al eliminar corredor: {str(e)}")
            self._mostrar_error(f"Error al eliminar corredor: {str(e)}")
