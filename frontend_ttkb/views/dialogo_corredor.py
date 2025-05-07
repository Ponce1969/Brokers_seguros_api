#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diálogo para crear y editar corredores en la aplicación Broker Seguros.

Este diálogo permite al usuario ingresar y modificar la información
de un corredor, validando los datos antes de enviarlos al backend.
"""

# Importaciones estándar
import logging
from typing import Dict, Any, Optional, Callable
import re
from datetime import datetime, date

# Importaciones de terceros
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.validation import add_validation
from ttkbootstrap.scrolled import ScrolledFrame

# Importaciones locales
import sys
sys.path.append('/home/gonzapython/CascadeProjects/Brokerseguros')
from frontend_ttkb.api_client import APIClient
from frontend_ttkb.models.corredor import Corredor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DialogoCorredor(ttk.Toplevel):
    """
    Diálogo para crear y editar corredores.
    """
    
    def __init__(
        self,
        parent,
        api_client: APIClient,
        corredor: Optional[Corredor] = None,
        on_success: Optional[Callable] = None
    ):
        """
        Inicializa el diálogo de corredor.
        
        Args:
            parent: Widget padre.
            api_client: Cliente API para realizar peticiones al backend.
            corredor: Corredor a editar. Si es None, se creará uno nuevo.
            on_success: Función a llamar cuando se guarde correctamente.
        """
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        self.corredor = corredor
        self.on_success = on_success
        self.edit_mode = corredor is not None
        
        # Variables para los campos del formulario
        self.numero_var = ttk.StringVar()
        self.nombre_var = ttk.StringVar()
        self.documento_var = ttk.StringVar()
        self.email_var = ttk.StringVar()
        self.telefono_var = ttk.StringVar()
        self.direccion_var = ttk.StringVar()
        self.activo_var = ttk.BooleanVar(value=True)
        
        # Variables para mensajes de validación
        self.error_messages = {}
        
        # Configurar la ventana
        self._setup_window()
        
        # Configurar la interfaz de usuario
        self._setup_ui()
        
        # Cargar datos si estamos editando
        if self.edit_mode:
            self._load_corredor_data()
            
        # Centrar la ventana
        self.update_idletasks()  # Asegurarse de que la ventana se ha dibujado
        self.center_window()
        
        # Focus en el primer campo
        if not self.edit_mode:
            self.widget_numero.focus_set()
        else:
            self.widget_nombre.focus_set()
    
    def _setup_window(self):
        """
        Configura las propiedades de la ventana de diálogo.
        """
        # Título de la ventana
        action = "Editar" if self.edit_mode else "Nuevo"
        self.title(f"{action} Corredor")
        
        # Hacer la ventana modal
        self.transient(self.parent)
        self.grab_set()
        
        # Configurar dimensiones y posición
        self.minsize(400, 450)
        
        # No permitir redimensionar
        self.resizable(False, False)
    
    def _setup_ui(self):
        """
        Configura la interfaz de usuario del diálogo.
        """
        # Crear un frame con scroll
        main_frame = ScrolledFrame(self, autohide=True)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Frame contenedor
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Título
        action = "Editar" if self.edit_mode else "Nuevo"
        title_label = ttk.Label(
            content_frame,
            text=f"{action} Corredor",
            font=("Helvetica", 14, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 10))
        
        # Frame para el formulario
        form_frame = ttk.Frame(content_frame)
        form_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Campos del formulario
        # Definir el ancho estándar para las etiquetas y los campos
        label_width = 15
        field_width = 30
        
        # Campo: Número de corredor
        row = 0
        numero_label = ttk.Label(form_frame, text="Número:", width=label_width, anchor=E)
        numero_label.grid(row=row, column=0, sticky=W, padx=5, pady=5)
        
        self.widget_numero = ttk.Entry(
            form_frame,
            textvariable=self.numero_var,
            width=field_width,
            state="readonly" if self.edit_mode else "normal"
        )
        self.widget_numero.grid(row=row, column=1, sticky=W, padx=5, pady=5)
        
        # Validación: Solo números
        if not self.edit_mode:
            add_validation(self.widget_numero, "key", r"^\d*$")
        
        # Campo: Nombre
        row += 1
        nombre_label = ttk.Label(form_frame, text="Nombre:", width=label_width, anchor=E)
        nombre_label.grid(row=row, column=0, sticky=W, padx=5, pady=5)
        
        self.widget_nombre = ttk.Entry(
            form_frame,
            textvariable=self.nombre_var,
            width=field_width
        )
        self.widget_nombre.grid(row=row, column=1, sticky=W, padx=5, pady=5)
        
        # Campo: Documento
        row += 1
        documento_label = ttk.Label(form_frame, text="Documento:", width=label_width, anchor=E)
        documento_label.grid(row=row, column=0, sticky=W, padx=5, pady=5)
        
        self.widget_documento = ttk.Entry(
            form_frame,
            textvariable=self.documento_var,
            width=field_width
        )
        self.widget_documento.grid(row=row, column=1, sticky=W, padx=5, pady=5)
        
        # Campo: Email
        row += 1
        email_label = ttk.Label(form_frame, text="Email:", width=label_width, anchor=E)
        email_label.grid(row=row, column=0, sticky=W, padx=5, pady=5)
        
        self.widget_email = ttk.Entry(
            form_frame,
            textvariable=self.email_var,
            width=field_width
        )
        self.widget_email.grid(row=row, column=1, sticky=W, padx=5, pady=5)
        
        # Campo: Teléfono
        row += 1
        telefono_label = ttk.Label(form_frame, text="Teléfono:", width=label_width, anchor=E)
        telefono_label.grid(row=row, column=0, sticky=W, padx=5, pady=5)
        
        self.widget_telefono = ttk.Entry(
            form_frame,
            textvariable=self.telefono_var,
            width=field_width
        )
        self.widget_telefono.grid(row=row, column=1, sticky=W, padx=5, pady=5)
        
        # Campo: Dirección
        row += 1
        direccion_label = ttk.Label(form_frame, text="Dirección:", width=label_width, anchor=E)
        direccion_label.grid(row=row, column=0, sticky=W, padx=5, pady=5)
        
        self.widget_direccion = ttk.Entry(
            form_frame,
            textvariable=self.direccion_var,
            width=field_width
        )
        self.widget_direccion.grid(row=row, column=1, sticky=W, padx=5, pady=5)
        
        # Campo: Activo (solo en modo edición)
        if self.edit_mode:
            row += 1
            activo_label = ttk.Label(form_frame, text="Estado:", width=label_width, anchor=E)
            activo_label.grid(row=row, column=0, sticky=W, padx=5, pady=5)
            
            self.widget_activo = ttk.Checkbutton(
                form_frame,
                text="Activo",
                variable=self.activo_var,
                bootstyle="success-round-toggle"
            )
            self.widget_activo.grid(row=row, column=1, sticky=W, padx=5, pady=5)
        
        # Separador
        row += 1
        separator = ttk.Separator(form_frame)
        separator.grid(row=row, column=0, columnspan=2, sticky=EW, padx=5, pady=10)
        
        # Botones
        row += 1
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        # Botón Cancelar
        cancel_button = ttk.Button(
            buttons_frame,
            text="Cancelar",
            bootstyle="secondary",
            command=self.destroy
        )
        cancel_button.pack(side=LEFT, padx=5)
        
        # Botón Guardar
        save_button = ttk.Button(
            buttons_frame,
            text="Guardar",
            bootstyle="primary",
            command=self.save_corredor
        )
        save_button.pack(side=LEFT, padx=5)
    
    def _load_corredor_data(self):
        """
        Carga los datos del corredor en los campos del formulario.
        """
        if not self.corredor:
            return
        
        # Cargar datos en las variables
        self.numero_var.set(str(self.corredor.numero) if self.corredor.numero else "")
        self.nombre_var.set(self.corredor.nombre or "")
        self.documento_var.set(self.corredor.documento or "")
        self.email_var.set(self.corredor.email or "")
        self.telefono_var.set(self.corredor.telefono or "")
        self.direccion_var.set(self.corredor.direccion or "")
        self.activo_var.set(self.corredor.activo)
    
    def validate_form(self) -> bool:
        """
        Valida los campos del formulario.
        
        Returns:
            True si todos los campos son válidos, False en caso contrario.
        """
        # Limpiar errores anteriores
        for key in self.error_messages:
            if key in self.__dict__:
                widget = self.__dict__[key]
                widget.config(bootstyle="default")
        
        self.error_messages = {}
        valid = True
        
        # Validar número
        if not self.edit_mode:  # Solo validar en modo creación
            numero = self.numero_var.get().strip()
            if not numero:
                self.error_messages["widget_numero"] = "El número de corredor es obligatorio"
                self.widget_numero.config(bootstyle="danger")
                valid = False
            elif not numero.isdigit():
                self.error_messages["widget_numero"] = "El número debe ser un valor numérico"
                self.widget_numero.config(bootstyle="danger")
                valid = False
        
        # Validar nombre
        nombre = self.nombre_var.get().strip()
        if not nombre:
            self.error_messages["widget_nombre"] = "El nombre es obligatorio"
            self.widget_nombre.config(bootstyle="danger")
            valid = False
        elif len(nombre) < 3:
            self.error_messages["widget_nombre"] = "El nombre debe tener al menos 3 caracteres"
            self.widget_nombre.config(bootstyle="danger")
            valid = False
        
        # Validar documento
        documento = self.documento_var.get().strip()
        if not documento:
            self.error_messages["widget_documento"] = "El documento es obligatorio"
            self.widget_documento.config(bootstyle="danger")
            valid = False
        
        # Validar email
        email = self.email_var.get().strip()
        if email and not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            self.error_messages["widget_email"] = "El formato del email no es válido"
            self.widget_email.config(bootstyle="danger")
            valid = False
        
        # Mostrar mensaje de error si hay alguno
        if not valid:
            error_msg = "\n".join(list(self.error_messages.values()))
            Messagebox.show_error(
                "Por favor, corrija los siguientes errores:\n\n" + error_msg,
                "Error de validación"
            )
        
        return valid
    
    def get_corredor_data(self) -> Dict[str, Any]:
        """
        Obtiene los datos del formulario en formato para enviar al backend.
        
        Returns:
            Diccionario con los datos del corredor formateados para el backend.
        """
        # Obtener valores básicos
        data = {
            "numero": int(self.numero_var.get().strip()) if self.numero_var.get().strip() else None,
            "documento": self.documento_var.get().strip(),
            "nombre": self.nombre_var.get().strip(),
            "email": self.email_var.get().strip() or None,
            "telefono": self.telefono_var.get().strip() or None,
            "direccion": self.direccion_var.get().strip() or None,
        }
        
        # Dividir nombre completo en nombres y apellidos para el backend
        nombres_completos = data["nombre"].split()
        if len(nombres_completos) > 1:
            data["nombres"] = nombres_completos[0]  # Primer nombre
            data["apellidos"] = " ".join(nombres_completos[1:])  # Resto como apellidos
        else:
            data["nombres"] = data["nombre"]
            data["apellidos"] = ""  # Apellido vacío si no hay espacio en el nombre
            
        # Mapear email a mail para el backend
        if data["email"] is not None:
            data["mail"] = data["email"]
        
        # Mapear telefono a telefonos y movil para el backend
        if data["telefono"] is not None:
            data["telefonos"] = data["telefono"]
            data["movil"] = data["telefono"]
            
        # Agregar localidad (requerido por el backend)
        data["localidad"] = "Montevideo"  # Valor predeterminado
        
        # Agregar estado solo en modo edición
        if self.edit_mode:
            # Manejar fecha_baja según estado activo
            if self.activo_var.get():
                data["fecha_baja"] = None  # Null si está activo
            else:
                # Si no está activo y no tiene fecha_baja, usar la fecha actual
                data["fecha_baja"] = date.today().isoformat()
            
            # Si estamos editando, asegurarnos de incluir el ID
            if self.corredor and self.corredor.id:
                data["id"] = self.corredor.id
        
        return data
    
    def save_corredor(self):
        """
        Guarda los datos del corredor en el backend.
        """
        # Validar el formulario
        if not self.validate_form():
            return
        
        try:
            # Obtener datos del formulario
            data = self.get_corredor_data()
            
            # Log para depuración
            logger.info(f"Datos a enviar al backend: {data}")
            
            # Determinar endpoint y método según modo
            if self.edit_mode:
                # Actualizar corredor existente
                corredor_id = self.corredor.id
                response = self.api_client.put(f"api/v1/corredores/{corredor_id}", json=data)
                success_message = "Corredor actualizado correctamente"
            else:
                # Crear nuevo corredor
                response = self.api_client.post("api/v1/corredores/", json=data)
                success_message = "Corredor creado correctamente"
            
            # Verificar respuesta
            if response.status_code in (200, 201):
                # Mostrar mensaje de éxito
                Messagebox.show_info(
                    success_message,
                    "Operación exitosa"
                )
                
                # Llamar al callback de éxito si existe
                if self.on_success:
                    self.on_success()
                
                # Cerrar el diálogo
                self.destroy()
            else:
                # Mostrar error
                error_msg = f"Error {response.status_code}: {response.text}"
                logger.error(error_msg)
                Messagebox.show_error(
                    f"No se pudo guardar el corredor: {error_msg}",
                    "Error"
                )
        except Exception as e:
            # Capturar cualquier excepción
            logger.exception("Error al guardar corredor")
            Messagebox.show_error(
                f"Error al guardar corredor: {str(e)}",
                "Error"
            )
    
    def center_window(self):
        """
        Centra la ventana en la pantalla.
        """
        self.update_idletasks()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        
        self.geometry(f"{width}x{height}+{x}+{y}")
