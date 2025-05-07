#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vista de Corredores para la aplicación Broker Seguros.

Esta vista permite gestionar corredores, mostrando una lista
y permitiendo agregar, editar y eliminar corredores.
"""

# Importaciones estándar
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

# Importaciones de terceros
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tableview import Tableview

# Importaciones locales
import sys
sys.path.append('/home/gonzapython/CascadeProjects/Brokerseguros')
from frontend_ttkb.api_client import APIClient
from frontend_ttkb.models.corredor import Corredor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorredoresView(ttk.Frame):
    """
    Vista para la gestión de corredores.
    """
    
    def __init__(self, parent, api_client: APIClient):
        """
        Inicializa la vista de corredores.
        
        Args:
            parent: El widget padre de esta vista.
            api_client: Cliente API para realizar peticiones al backend.
        """
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        
        # Lista de corredores
        self.corredores: List[Corredor] = []
        
        # Variables para filtrado y búsqueda
        self.search_var = ttk.StringVar()
        self.filter_active_var = ttk.BooleanVar(value=True)
        
        # Referencias a widgets
        self.table = None
        self.status_label = None
        
        # Configurar la interfaz
        self._setup_ui()
        
        # Cargar datos iniciales
        self.load_corredores()
    
    def _setup_ui(self):
        """
        Configura la interfaz de usuario de la vista de corredores.
        """
        # Configurar el layout principal
        self.pack(fill=BOTH, expand=True)
        
        # Frame para título y botones superiores
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, padx=10, pady=(10, 5))
        
        # Título
        title_label = ttk.Label(
            header_frame,
            text="Gestión de Corredores",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side=LEFT, padx=5)
        
        # Botón para agregar nuevo corredor
        add_button = ttk.Button(
            header_frame,
            text="Nuevo Corredor",
            bootstyle="success",
            command=self.add_corredor
        )
        add_button.pack(side=RIGHT, padx=5)
        
        # Frame para filtros y búsqueda
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=X, padx=10, pady=5)
        
        # Caja de búsqueda
        search_label = ttk.Label(filter_frame, text="Buscar:")
        search_label.pack(side=LEFT, padx=(0, 5))
        
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=LEFT, padx=5)
        search_entry.bind("<Return>", lambda e: self.search_corredores())
        
        search_button = ttk.Button(
            filter_frame,
            text="Buscar",
            bootstyle="info-outline",
            command=self.search_corredores
        )
        search_button.pack(side=LEFT, padx=5)
        
        # Filtro para mostrar solo activos
        active_check = ttk.Checkbutton(
            filter_frame,
            text="Solo activos",
            variable=self.filter_active_var,
            bootstyle="info-round-toggle",
            command=self.apply_filters
        )
        active_check.pack(side=LEFT, padx=(20, 5))
        
        # Botón para refrescar
        refresh_button = ttk.Button(
            filter_frame,
            text="Refrescar",
            bootstyle="secondary-outline",
            command=self.load_corredores
        )
        refresh_button.pack(side=RIGHT, padx=5)
        
        # Frame para la tabla
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Definición de las columnas de la tabla
        columns = [
            {"text": "#", "width": 50},
            {"text": "Número", "width": 70},
            {"text": "Nombre", "width": 200},
            {"text": "Documento", "width": 100},
            {"text": "Email", "width": 180},
            {"text": "Teléfono", "width": 120},
            {"text": "Registro", "width": 100},
            {"text": "Estado", "width": 80},
            {"text": "Acciones", "width": 120},
        ]
        
        # Crear la tabla
        self.table = Tableview(
            master=table_frame,
            coldata=columns,
            rowdata=[],
            paginated=True,
            searchable=False,
            bootstyle="primary"
        )
        self.table.pack(fill=BOTH, expand=True)
        
        # Barra de estado
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=X, padx=10, pady=5)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Cargando corredores...",
            bootstyle="secondary"
        )
        self.status_label.pack(side=LEFT, padx=5)
    
    def load_corredores(self):
        """
        Carga la lista de corredores desde el backend.
        """
        try:
            # Actualizar estado
            self.status_label.config(text="Cargando corredores...")
            self.update_idletasks()
            
            # Realizar petición al backend
            response = self.api_client.get("api/v1/corredores/?skip=0&limit=100")
            
            if response.status_code == 200:
                # Convertir datos a objetos Corredor
                corredores_data = response.json()
                self.corredores = [Corredor.from_dict(data) for data in corredores_data]
                
                # Actualizar la tabla
                self.update_table()
                
                # Actualizar estado
                self.status_label.config(
                    text=f"Se cargaron {len(self.corredores)} corredores correctamente."
                )
            else:
                logger.error(f"Error al cargar corredores: {response.status_code}")
                self.status_label.config(
                    text=f"Error al cargar corredores: {response.status_code}"
                )
                Messagebox.show_error(
                    "No se pudieron cargar los corredores.",
                    "Error de conexión"
                )
        except Exception as e:
            logger.exception("Error al cargar corredores")
            self.status_label.config(text=f"Error al cargar corredores: {str(e)}")
            Messagebox.show_error(
                f"Error al cargar corredores: {str(e)}",
                "Error"
            )
    
    def update_table(self):
        """
        Actualiza la tabla con los datos de corredores aplicando filtros.
        """
        # Aplicar filtros
        filtered_corredores = self.apply_filters(update_table=False)
        
        # Preparar datos para la tabla
        table_data = []
        for i, corredor in enumerate(filtered_corredores, start=1):
            # Formatear estado para mejor visualización
            estado = "Activo" if corredor.activo else "Inactivo"
            estado_style = "success" if corredor.activo else "danger"
            
            # Crear array de acciones
            acciones = self.create_action_buttons(i - 1, corredor)
            
            # Añadir fila a la tabla
            table_data.append([
                i,  # Índice visual
                corredor.numero,
                corredor.nombre,
                corredor.documento,
                corredor.email or "",
                corredor.telefono or "",
                corredor.fecha_registro or "",
                (estado, estado_style),  # Formato (texto, estilo)
                acciones
            ])
        
        # Actualizar tabla con nuevos datos
        self.table.delete_rows()
        self.table.insert_rows("end", table_data)
        
        # Actualizar etiqueta de estado
        self.status_label.config(
            text=f"Mostrando {len(filtered_corredores)} de {len(self.corredores)} corredores."
        )
    
    def create_action_buttons(self, index: int, corredor: Corredor) -> ttk.Frame:
        """
        Crea los botones de acción para un corredor específico.
        
        Args:
            index: Índice del corredor en la lista filtrada.
            corredor: Objeto Corredor para el que se crean los botones.
            
        Returns:
            Frame con botones de acción.
        """
        # Crear un frame para los botones
        actions_frame = ttk.Frame(self.table)
        
        # Botón de editar
        edit_button = ttk.Button(
            actions_frame,
            text="✏️",  # Emoji de editar
            bootstyle="info-link",
            width=3,
            command=lambda: self.edit_corredor(corredor)
        )
        edit_button.pack(side=LEFT, padx=2)
        
        # Botón de cambiar estado (activar/desactivar)
        toggle_icon = "🔴" if corredor.activo else "🟢"  # Rojo si está activo (para desactivar), verde si está inactivo (para activar)
        toggle_style = "danger-link" if corredor.activo else "success-link"
        toggle_button = ttk.Button(
            actions_frame,
            text=toggle_icon,
            bootstyle=toggle_style,
            width=3,
            command=lambda: self.toggle_corredor_status(corredor)
        )
        toggle_button.pack(side=LEFT, padx=2)
        
        # Botón de ver detalle
        view_button = ttk.Button(
            actions_frame,
            text="👁️",  # Emoji de ojo
            bootstyle="secondary-link",
            width=3,
            command=lambda: self.view_corredor_detail(corredor)
        )
        view_button.pack(side=LEFT, padx=2)
        
        return actions_frame
    
    def search_corredores(self):
        """
        Aplica la búsqueda según el texto ingresado.
        """
        self.update_table()
    
    def apply_filters(self, update_table: bool = True) -> List[Corredor]:
        """
        Aplica filtros a la lista de corredores.
        
        Args:
            update_table: Si es True, actualiza la tabla después de aplicar filtros.
            
        Returns:
            Lista filtrada de corredores.
        """
        # Obtener términos de búsqueda y filtros
        search_text = self.search_var.get().lower()
        only_active = self.filter_active_var.get()
        
        # Aplicar filtros
        filtered_corredores = []
        for corredor in self.corredores:
            # Filtro de activos
            if only_active and not corredor.activo:
                continue
            
            # Filtro de búsqueda
            if search_text:
                # Buscar en varios campos
                searchable_fields = [
                    str(corredor.numero),
                    corredor.nombre.lower(),
                    corredor.documento.lower(),
                    (corredor.email or "").lower(),
                    (corredor.telefono or "").lower()
                ]
                
                if not any(search_text in field for field in searchable_fields):
                    continue
            
            # Si pasa todos los filtros, agregar a la lista
            filtered_corredores.append(corredor)
        
        # Actualizar la tabla si se solicita
        if update_table:
            self.update_table()
        
        return filtered_corredores
    
    def add_corredor(self):
        """
        Muestra el diálogo para agregar un nuevo corredor.
        """
        # Importar el diálogo de corredor
        from frontend_ttkb.views.dialogo_corredor import DialogoCorredor
        
        # Mostrar diálogo de nuevo corredor
        dialogo = DialogoCorredor(
            self,
            self.api_client,
            corredor=None,
            on_success=self.load_corredores
        )
        
        # Hacer que el diálogo sea modal
        self.wait_window(dialogo)
    
    def edit_corredor(self, corredor: Corredor):
        """
        Muestra el diálogo para editar un corredor existente.
        
        Args:
            corredor: El corredor a editar.
        """
        # Importar el diálogo de corredor
        from frontend_ttkb.views.dialogo_corredor import DialogoCorredor
        
        # Mostrar diálogo de edición de corredor
        dialogo = DialogoCorredor(
            self,
            self.api_client,
            corredor=corredor,
            on_success=self.load_corredores
        )
        
        # Hacer que el diálogo sea modal
        self.wait_window(dialogo)
    
    def toggle_corredor_status(self, corredor: Corredor):
        """
        Cambia el estado de un corredor (activo/inactivo).
        
        Args:
            corredor: El corredor cuyo estado se cambiará.
        """
        # Confirmar acción
        action = "desactivar" if corredor.activo else "activar"
        confirmed = Messagebox.show_question(
            f"¿Está seguro que desea {action} al corredor {corredor.nombre}?",
            f"{action.capitalize()} corredor",
            buttons=["No", "Sí"]
        )
        
        if confirmed == "Sí":
            try:
                # Preparar datos para enviar al backend
                corredor_id = corredor.id
                nuevo_estado = not corredor.activo
                
                # Crear un diccionario con los datos mínimos necesarios para actualizar
                data = {
                    "id": corredor_id,
                    "numero": corredor.numero,
                    "documento": corredor.documento,
                    "nombre": corredor.nombre,
                    "activo": nuevo_estado
                }
                
                # Dividir nombre en nombres y apellidos (requerido por el backend)
                nombre_partes = corredor.nombre.split()
                if len(nombre_partes) > 1:
                    data["nombres"] = nombre_partes[0]
                    data["apellidos"] = " ".join(nombre_partes[1:])
                else:
                    data["nombres"] = corredor.nombre
                    data["apellidos"] = ""
                
                # Mapear campos para el backend
                if corredor.email:
                    data["mail"] = corredor.email
                
                if corredor.telefono:
                    data["telefonos"] = corredor.telefono
                    data["movil"] = corredor.telefono
                
                # Localidad (requerido por el backend)
                data["localidad"] = "Montevideo"
                
                # Manejar fecha_baja según estado
                from datetime import date
                if not nuevo_estado:
                    data["fecha_baja"] = date.today().isoformat()
                else:
                    data["fecha_baja"] = None
                
                # Enviar al backend
                response = self.api_client.put(f"api/v1/corredores/{corredor_id}", json=data)
                
                if response.status_code == 200:
                    # Actualizar corredor localmente
                    corredor.activo = nuevo_estado
                    self.update_table()
                    
                    Messagebox.show_info(
                        f"El corredor ha sido {action}do correctamente.",
                        "Cambio de estado"
                    )
                else:
                    # Mostrar error
                    error_msg = f"Error {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    Messagebox.show_error(
                        f"No se pudo {action} al corredor: {error_msg}",
                        "Error"
                    )
            except Exception as e:
                # Capturar cualquier excepción
                logger.exception(f"Error al {action} corredor")
                Messagebox.show_error(
                    f"Error al {action} al corredor: {str(e)}",
                    "Error"
                )
                
                # Recargar datos para asegurar consistencia
                self.load_corredores()
    
    def view_corredor_detail(self, corredor: Corredor):
        """
        Muestra un diálogo con los detalles completos del corredor.
        
        Args:
            corredor: El corredor cuyos detalles se mostrarán.
        """
        # Construir mensaje con detalles
        details = f"Detalles del corredor #{corredor.numero}:\n\n"
        details += f"Nombre: {corredor.nombre}\n"
        details += f"Documento: {corredor.documento}\n"
        details += f"Email: {corredor.email or 'No disponible'}\n"
        details += f"Teléfono: {corredor.telefono or 'No disponible'}\n"
        details += f"Dirección: {corredor.direccion or 'No disponible'}\n"
        details += f"Fecha de registro: {corredor.fecha_registro or 'No disponible'}\n"
        details += f"Estado: {'Activo' if corredor.activo else 'Inactivo'}"
        
        # Mostrar diálogo
        Messagebox.show_info(
            details,
            f"Corredor: {corredor.nombre}"
        )
