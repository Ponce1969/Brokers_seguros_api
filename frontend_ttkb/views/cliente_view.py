#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vista de clientes para la aplicaciu00f3n Broker Seguros con ttkbootstrap.

Esta vista muestra la lista de clientes y permite realizar operaciones CRUD sobre ellos.
"""

# Importaciones estu00e1ndar
import logging
from typing import Dict, Any, Optional, List, Callable
import uuid
from datetime import datetime

# Importaciones de terceros
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
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
    Vista para la gestiu00f3n de clientes.
    """
    
    def __init__(self, parent, api_client: APIClient, user_info: Dict[str, Any]):
        """
        Inicializa la vista de clientes.
        
        Args:
            parent: El widget padre de esta vista.
            api_client: Cliente API para comunicarse con el backend.
            user_info: Informaciu00f3n del usuario autenticado.
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
        
        # Tu00edtulo de la vista
        title_label = ttk.Label(
            control_frame,
            text="Gestiu00f3n de Clientes",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side=LEFT, padx=5)
        
        # Botu00f3n de agregar cliente
        add_button = ttk.Button(
            control_frame,
            text="Agregar Cliente",
            command=self._add_cliente,
            bootstyle="success"
        )
        add_button.pack(side=RIGHT, padx=5)
        
        # Botu00f3n de actualizar lista
        refresh_button = ttk.Button(
            control_frame,
            text="Actualizar",
            command=self.load_clientes,
            bootstyle="primary"
        )
        refresh_button.pack(side=RIGHT, padx=5)
        
        # Campo de bu00fasqueda
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
        
        # Crear y configurar la tabla
        coldata = [
            {"text": "ID", "stretch": False, "width": 80},
            {"text": "Nombre", "stretch": True},
            {"text": "Email", "stretch": True},
            {"text": "Telu00e9fono", "stretch": False, "width": 120},
            {"text": "Localidad", "stretch": True},
            {"text": "Fecha Registro", "stretch": False, "width": 150},
            {"text": "Acciones", "stretch": False, "width": 150},
        ]
        
        # Crear la tabla
        self.table = Tableview(
            master=table_frame,
            coldata=coldata,
            rowdata=[],
            paginated=True,
            searchable=True,
            bootstyle="primary",
            pagesize=10,
            height=10,
        )
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
    
    def load_clientes(self):
        """
        Carga los clientes desde el backend y actualiza la tabla.
        """
        try:
            logger.info("Cargando clientes desde el backend...")
            
            # Obtener los clientes segu00fan el rol del usuario
            if self.is_admin:
                # Para administradores, obtener todos los clientes
                raw_clientes = self.api_client.get_clientes(role='admin')
            else:
                # Para corredores, obtener solo sus clientes
                raw_clientes = self.api_client.get_clientes(role='corredor')
            
            # Convertir los datos crudos a objetos Cliente
            self.clientes = []
            for cliente_data in raw_clientes:
                try:
                    cliente = Cliente.from_dict(cliente_data)
                    self.clientes.append(cliente)
                except Exception as e:
                    logger.error(f"Error al procesar cliente: {str(e)}")
            
            # Actualizar la tabla
            self._update_table()
            
            # Actualizar la etiqueta de total
            self.total_label.config(text=f"Total de clientes: {len(self.clientes)}")
            
            logger.info(f"Cargados {len(self.clientes)} clientes")
            
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
        # Limpiar la tabla
        self.table.delete_rows()
        
        # Agregar filas para cada cliente
        for cliente in self.clientes:
            # Formatear la fecha como string legible
            fecha_registro = cliente.fecha_registro.strftime("%d/%m/%Y") if cliente.fecha_registro else ""
            
            # Crear el botu00f3n de acciones para esta fila
            actions_frame = ttk.Frame(self.table)
            
            edit_button = ttk.Button(
                actions_frame,
                text="Editar",
                bootstyle="info-outline",
                width=8,
                command=lambda c=cliente: self._edit_cliente(c)
            )
            edit_button.pack(side=LEFT, padx=2)
            
            delete_button = ttk.Button(
                actions_frame,
                text="Eliminar",
                bootstyle="danger-outline",
                width=8,
                command=lambda c=cliente: self._delete_cliente(c)
            )
            delete_button.pack(side=LEFT, padx=2)
            
            # Agregar la fila a la tabla
            self.table.insert_row(
                "end",
                values=(
                    str(cliente.id)[:8],  # Mostramos solo los primeros 8 caracteres del UUID
                    cliente.nombre,
                    cliente.email,
                    cliente.telefono,
                    cliente.localidad,
                    fecha_registro,
                    "",  # Este valor se reemplaza con los botones de acciu00f3n
                )
            )
            
            # Au00f1adir los botones de acciu00f3n a la u00faltima columna
            last_row = self.table.get_rows()[-1]
            self.table.set_cell_data(last_row, 6, value="", image=None, window=actions_frame)
    
    def _search_clientes(self):
        """
        Busca clientes segu00fan el texto ingresado en el campo de bu00fasqueda.
        """
        search_text = self.search_var.get().lower()
        
        if not search_text:
            # Si la bu00fasqueda estu00e1 vacu00eda, mostrar todos los clientes
            self._update_table()
            return
        
        # Filtrar clientes segu00fan el texto de bu00fasqueda
        filtered_clientes = []
        for cliente in self.clientes:
            # Buscar en nombre, email, telu00e9fono y localidad
            if (search_text in cliente.nombre.lower() or
                search_text in cliente.email.lower() or
                search_text in cliente.telefono.lower() or
                search_text in cliente.localidad.lower()):
                filtered_clientes.append(cliente)
        
        # Guardar temporalmente los clientes filtrados
        original_clientes = self.clientes
        self.clientes = filtered_clientes
        
        # Actualizar la tabla con los resultados
        self._update_table()
        
        # Actualizar la etiqueta de total
        self.total_label.config(text=f"Resultados: {len(filtered_clientes)} de {len(original_clientes)}")
        
        # Restaurar la lista original de clientes
        self.clientes = original_clientes
    
    def _add_cliente(self):
        """
        Abre el diu00e1logo para agregar un nuevo cliente.
        """
        # TODO: Implementar el diu00e1logo de agregar cliente
        logger.info("Funciu00f3n agregar cliente au00fan no implementada")
        Messagebox.show_info(
            "La funciu00f3n para agregar clientes se implementaru00e1 en el pru00f3ximo paso.",
            "Funciu00f3n no implementada"
        )
    
    def _edit_cliente(self, cliente: Cliente):
        """
        Abre el diu00e1logo para editar un cliente existente.
        
        Args:
            cliente: El cliente a editar.
        """
        # TODO: Implementar el diu00e1logo de editar cliente
        logger.info(f"Funciu00f3n editar cliente au00fan no implementada para cliente ID: {cliente.id}")
        Messagebox.show_info(
            f"La funciu00f3n para editar el cliente {cliente.nombre} se implementaru00e1 en el pru00f3ximo paso.",
            "Funciu00f3n no implementada"
        )
    
    def _delete_cliente(self, cliente: Cliente):
        """
        Muestra un diu00e1logo de confirmaciu00f3n y elimina el cliente si se confirma.
        
        Args:
            cliente: El cliente a eliminar.
        """
        # Mostrar diu00e1logo de confirmaciu00f3n
        confirm = Messagebox.show_question(
            f"u00bfEstu00e1 seguro que desea eliminar al cliente {cliente.nombre}?",
            "Confirmar eliminaciu00f3n",
            buttons=['Su00ed', 'No']
        )
        
        if confirm == 'Su00ed':
            try:
                # TODO: Implementar la eliminaciu00f3n real del cliente
                logger.info(f"Funciu00f3n eliminar cliente au00fan no implementada para cliente ID: {cliente.id}")
                Messagebox.show_info(
                    f"La funciu00f3n para eliminar el cliente {cliente.nombre} se implementaru00e1 en el pru00f3ximo paso.",
                    "Funciu00f3n no implementada"
                )
            except Exception as e:
                logger.error(f"Error al eliminar cliente: {str(e)}")
                Messagebox.show_error(
                    f"No se pudo eliminar el cliente: {str(e)}",
                    "Error al eliminar"
                )
