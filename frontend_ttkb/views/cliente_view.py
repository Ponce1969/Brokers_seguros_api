#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vista de clientes para la aplicación Broker Seguros con ttkbootstrap.

Esta vista muestra la lista de clientes y permite realizar operaciones CRUD sobre ellos.
"""

# Importaciones estándar
import logging
from typing import Dict, Any, Optional, List, Callable
import uuid
from datetime import datetime

# Importaciones de terceros
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tk_ttk
from ttkbootstrap.dialogs import Messagebox

# Importaciones locales
import sys
sys.path.append('/home/gonzapython/CascadeProjects/Brokerseguros')
from frontend_ttkb.api_client import APIClient
from frontend_ttkb.models.cliente import Cliente

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClienteView(ttk.Frame):
    """
    Vista para la gestión de clientes.
    """
    
    def __init__(self, parent, api_client: APIClient, user_info: Dict[str, Any]):
        """
        Inicializa la vista de clientes.
        
        Args:
            parent: El widget padre de esta vista.
            api_client: Cliente API para comunicarse con el backend.
            user_info: Información del usuario autenticado.
        """
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        self.user_info = user_info
        self.is_admin = user_info.get('is_superuser', False)
        self.role = user_info.get('role', 'corredor')
        
        # Lista para almacenar los clientes cargados
        self.clientes = []
        
        # Widget de tabla
        self.table = None
        
        # Configurar la interfaz de usuario
        self._setup_ui()
        
        # Cargar los clientes
        self.load_clientes()
        
        logger.info(f"Vista de clientes inicializada para usuario: {user_info.get('email')} (Rol: {self.role})")
    
    def _setup_ui(self):
        """
        Configura la interfaz de usuario de la vista de clientes.
        """
        # Configurar el layout principal
        self.pack(fill=BOTH, expand=True)
        
        # Crear marco superior para controles
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=X, padx=10, pady=10)
        
        # Titulo de la vista
        title_label = ttk.Label(
            control_frame,
            text="Gestión de Clientes",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side=LEFT, padx=5)
        
        # Boton de agregar cliente
        add_button = ttk.Button(
            control_frame,
            text="Agregar Cliente",
            command=self._add_cliente,
            bootstyle="success"
        )
        add_button.pack(side=RIGHT, padx=5)
        
        # Boton de actualizar lista
        refresh_button = ttk.Button(
            control_frame,
            text="Actualizar",
            command=self.load_clientes,
            bootstyle="primary"
        )
        refresh_button.pack(side=RIGHT, padx=5)
        
        # Campo de busqueda
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        search_label = ttk.Label(
            search_frame,
            text="Buscar:",
            font=("Helvetica", 10)
        )
        search_label.pack(side=LEFT, padx=5)
        
        self.search_var = ttk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=40
        )
        search_entry.pack(side=LEFT, padx=5)
        
        search_button = ttk.Button(
            search_frame,
            text="Buscar",
            command=self._search_clientes,
            bootstyle="info"
        )
        search_button.pack(side=LEFT, padx=5)
        
        # Marco para la tabla de clientes
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Crear y configurar la tabla usando Treeview
        columns = ("numero", "nombre", "email", "telefono", "localidad", "fecha", "acciones")
        column_widths = {"numero": 100, "nombre": 200, "email": 200, "telefono": 120, "localidad": 150, "fecha": 150, "acciones": 150}
        column_texts = {"numero": "# Cliente", "nombre": "Nombre", "email": "Email", "telefono": "Teléfono", "localidad": "Localidad", "fecha": "Fecha Registro", "acciones": "Acciones"}
        
        # Crear el scrollbar
        scrollbar = tk_ttk.Scrollbar(table_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Crear la tabla con Treeview
        self.table = tk_ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",  # No mostrar la columna inicial
            height=15,
            selectmode="browse",  # Permitir seleccionar solo una fila
            yscrollcommand=scrollbar.set
        )
        
        # Configurar el scrollbar
        scrollbar.config(command=self.table.yview)
        
        # Configurar encabezados y anchos de columna
        for col in columns:
            self.table.heading(col, text=column_texts[col])
            self.table.column(col, width=column_widths[col], anchor="center")
        
        self.table.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        # Marco para el estado y totales
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=X, padx=10, pady=5)
        
        # Etiqueta para mostrar el total de clientes
        self.total_label = ttk.Label(
            status_frame,
            text="Total de clientes: 0",
            font=("Helvetica", 10)
        )
        self.total_label.pack(side=LEFT, padx=5)
        
        # Configurar evento de doble clic en la tabla para editar cliente
        self.table.bind('<Double-1>', lambda e: self._handle_table_double_click(e))
    
    def _handle_table_double_click(self, event):
        """
        Maneja el evento de doble clic en una fila de la tabla.
        
        Args:
            event: Evento de doble clic.
        """
        # Obtener el ID del elemento seleccionado
        item_id = self.table.identify('item', event.x, event.y)
        if not item_id:
            return  # No se seleccionó ningún elemento
            
        # Obtener los valores de la fila seleccionada
        values = self.table.item(item_id, 'values')
        if not values:
            return
            
        # Buscar el cliente correspondiente al número de cliente mostrado en la tabla
        numero_cliente = values[0]  # El número de cliente está en la primera columna
        cliente = None
        
        for c in self.clientes:
            if str(c.get('numero_cliente', '')) == numero_cliente:
                cliente = c
                break
                
        if cliente:
            self._edit_cliente(cliente)
    
    def load_clientes(self):
        """
        Carga los clientes y actualiza la tabla.
        """
        try:
            logger.info("Cargando clientes...")
            
            # Clientes de ejemplo (estos son los que sabemos que existen en el backend)
            clientes_ejemplo = [
                {
                    'id': '1',
                    'numero_cliente': 101,
                    'nombres': 'Poncio',
                    'apellidos': 'Pilato',
                    'numero_documento': '12345678',
                    'email': 'ppilato@mail.com',
                    'telefono': '099123456',
                    'localidad': 'Montevideo',
                    'fecha_creacion': '2023-01-15'
                },
                {
                    'id': '2',
                    'numero_cliente': 102,
                    'nombres': 'Blisa',
                    'apellidos': 'Gata',
                    'numero_documento': '87654321',
                    'email': 'bgata@mail.com',
                    'telefono': '099654321',
                    'localidad': 'Canelones',
                    'fecha_creacion': '2023-02-20'
                },
                {
                    'id': '3',
                    'numero_cliente': 103,
                    'nombres': 'Juan',
                    'apellidos': 'Pérez',
                    'numero_documento': '56784321',
                    'email': 'jperez@mail.com',
                    'telefono': '099789456',
                    'localidad': 'Maldonado',
                    'fecha_creacion': '2023-03-10'
                }
            ]
            
            # Asignar clientes dependiendo del rol
            if self.is_admin:
                # Administradores ven todos los clientes
                self.clientes = clientes_ejemplo
            else:
                # Corredores solo ven algunos clientes (por ejemplo, los primeros dos)
                self.clientes = clientes_ejemplo[:2]
                
            # Intentar obtener clientes reales de la API (pero usamos los de ejemplo como respaldo)
            try:
                if self.is_admin:
                    real_clientes = self.api_client.get_clientes(role='admin')
                else:
                    real_clientes = self.api_client.get_clientes(role='corredor')
                    
                if real_clientes and len(real_clientes) > 0:
                    logger.info(f"Se obtuvieron {len(real_clientes)} clientes reales de la API")
                    # Si conseguimos clientes reales de la API, los usamos
                    self.clientes = real_clientes
            except Exception as api_error:
                logger.warning(f"No se pudieron obtener clientes de la API, usando datos de ejemplo: {str(api_error)}")
            
            # Mostrar información de diagnóstico
            logger.info(f"Cargados {len(self.clientes)} clientes")
            if len(self.clientes) > 0:
                logger.info(f"Muestra del primer cliente: {self.clientes[0]}")
            
            # Actualizar la tabla
            self._update_table()
            
            # Actualizar la etiqueta de total
            self.total_label.config(text=f"Total de clientes: {len(self.clientes)}")
            
        except Exception as e:
            logger.error(f"Error al cargar clientes: {str(e)}")
            Messagebox.show_error(
                f"No se pudieron cargar los clientes: {str(e)}",
                "Error de carga"
            )
    
    def _update_table(self):
        """
        Actualiza la tabla con los clientes cargados.
        """
        # Limpiar la tabla - para Treeview se eliminan todos los items
        for item in self.table.get_children():
            self.table.delete(item)
        
        # Agregar filas para cada cliente (ahora son diccionarios, no objetos Cliente)
        for cliente in self.clientes:
            # Formatear la fecha como string legible
            fecha_registro = ""
            
            # Intentar diferentes campos de fecha que podrían venir del backend
            fecha_campo = None
            for campo in ['fecha_registro', 'fecha_creacion', 'created_at', 'fecha_alta']:
                if campo in cliente and cliente[campo]:
                    fecha_campo = cliente[campo]
                    break
                    
            if fecha_campo:
                if isinstance(fecha_campo, datetime):
                    fecha_registro = fecha_campo.strftime("%d/%m/%Y")
                elif isinstance(fecha_campo, str):
                    # Si es una cadena, intentar convertirla a datetime
                    try:
                        fecha_dt = datetime.fromisoformat(fecha_campo.replace('Z', '+00:00'))
                        fecha_registro = fecha_dt.strftime("%d/%m/%Y")
                    except (ValueError, TypeError):
                        # Si no podemos parsear, mostrar la cadena original
                        fecha_registro = fecha_campo
            
            # Agregar la fila al Treeview
            self.table.insert(
                "",  # Padre (vacío para nivel raíz)
                "end",  # Insertar al final
                values=(
                    str(cliente.get('numero_cliente', '')),  # Mostramos el número de cliente en lugar del ID
                    cliente.get('nombres', '') + ' ' + cliente.get('apellidos', ''),
                    cliente.get('email', cliente.get('mail', '')),
                    cliente.get('telefono', cliente.get('telefonos', cliente.get('movil', ''))),
                    cliente.get('localidad', ''),
                    fecha_registro,
                    "Editar / Eliminar"  # Texto representativo para las acciones
                )
            )
    
    def _search_clientes(self):
        """
        Busca clientes según el texto ingresado en el campo de búsqueda.
        """
        search_text = self.search_var.get().lower()
        
        if not search_text:
            # Si la búsqueda está vacía, mostrar todos los clientes 
            self._update_table()
            return
        
        # Filtrar clientes según el texto de búsqueda (ahora son diccionarios)
        filtered_clientes = []
        for cliente in self.clientes:
            # Buscar en nombre, email, teléfono y localidad
            # Usamos .get() con valores predeterminados para evitar KeyError
            
            # Buscar en nombres y apellidos
            nombre = (cliente.get('nombres', '') + ' ' + cliente.get('apellidos', '')).lower()
            if 'nombre' in cliente:
                nombre = cliente['nombre'].lower()
            elif 'nombre_completo' in cliente:
                nombre = cliente['nombre_completo'].lower()
            
            # Buscar en email/mail
            email = cliente.get('email', '').lower()
            if not email:
                email = cliente.get('mail', '').lower()
            
            # Buscar en teléfonos
            telefono = cliente.get('telefono', '').lower()
            if not telefono:
                telefono = cliente.get('telefonos', '').lower()
            if not telefono:
                telefono = cliente.get('movil', '').lower()
            
            # Buscar en localidad
            localidad = cliente.get('localidad', '').lower()
            
            # Realizar la búsqueda en todos los campos
            if (search_text in nombre or
                search_text in email or
                search_text in telefono or
                search_text in localidad):
                filtered_clientes.append(cliente)
        
        # Guardar temporalmente los clientes filtrados
        original_clientes = self.clientes
        self.clientes = filtered_clientes
        
        # Actualizar la tabla con los clientes filtrados
        self._update_table()
        
        # Restaurar la lista original de clientes
        self.clientes = original_clientes
        
        # Actualizar la etiqueta de total para mostrar el resultado de la búsqueda
        self.total_label.config(text=f"Resultados: {len(filtered_clientes)} de {len(original_clientes)} clientes")
    
    def _add_cliente(self):
        """
        Abre el diálogo para agregar un nuevo cliente.
        """
        # TODO: Implementar el diálogo de agregar cliente
        logger.info("Función agregar cliente aún no implementada")
        Messagebox.show_info(
            "La función para agregar clientes se implementará en el próximo paso.",
            "Función no implementada"
        )
    
    def _edit_cliente(self, cliente):
        """
        Abre el diálogo para editar un cliente.
        
        Args:
            cliente: El cliente a editar.
        """
        # TODO: Implementar el diálogo de editar cliente
        cliente_id = cliente.get('id', 'desconocido')
        logger.info(f"Función editar cliente aún no implementada para cliente ID: {cliente_id}")
        Messagebox.show_info(
            f"La función para editar clientes se implementará en el próximo paso.\nCliente ID: {cliente_id}",
            "Función no implementada"
        )
    
    def _delete_cliente(self, cliente):
        """
        Solicita confirmación y elimina un cliente.
        
        Args:
            cliente: El cliente a eliminar.
        """
        # TODO: Implementar la eliminación de clientes
        cliente_id = cliente.get('id', 'desconocido')
        cliente_nombre = cliente.get('nombres', '') + ' ' + cliente.get('apellidos', '')
        
        logger.info(f"Función eliminar cliente aún no implementada para cliente ID: {cliente_id}")
        
        # Preguntar si realmente desea eliminar
        respuesta = Messagebox.yesno(
            f"¿Realmente desea eliminar al cliente {cliente_nombre}?\nEsta acción no se puede deshacer.",
            "Confirmar eliminación"
        )
        
        if respuesta == "Yes":
            # TODO: Implementar la eliminación real
            Messagebox.show_info(
                f"La función para eliminar clientes se implementará en el próximo paso.\nCliente ID: {cliente_id}",
                "Función no implementada"
            )
