#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vista principal para la aplicación Broker Seguros con ttkbootstrap.

Esta vista contiene el menú lateral y gestiona la navegación entre las
diferentes secciones de la aplicación.
"""

# Importaciones estándar
import logging
from typing import Dict, Any, Optional, List, Callable

# Importaciones de terceros
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Importaciones locales
import sys
sys.path.append('/home/gonzapython/CascadeProjects/Brokerseguros')
from frontend_ttkb.api_client import APIClient

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MainView(ttk.Frame):
    """
    Vista principal de la aplicación que contiene el menú lateral
    y gestiona la navegación entre las diferentes secciones.
    """
    
    def __init__(self, parent, user_info: Dict[str, Any]):
        """
        Inicializa la vista principal.
        
        Args:
            parent: El widget padre de esta vista.
            user_info: Información del usuario autenticado.
        """
        super().__init__(parent)
        self.parent = parent
        self.user_info = user_info
        self.api_client = APIClient()
        
        # Obtener el rol del usuario
        self.is_admin = user_info.get('is_superuser', False)
        self.role = user_info.get('role', 'corredor')
        self.user_email = user_info.get('email', 'Usuario')
        
        # Configurar el token de autenticación en el cliente API
        token = user_info.get('access_token')
        if token:
            self.api_client.set_token(token, 'bearer')
        
        # Crear las variables para las vistas
        self.current_view = None
        self.content_frame = None
        self.menu_frame = None
        
        # Configurar la interfaz de usuario
        self._setup_ui()
        
        logger.info(f"Vista principal inicializada para usuario: {self.user_email} (Rol: {self.role})")
    
    def _setup_ui(self):
        """
        Configura la interfaz de usuario de la vista principal.
        """
        # Configurar el layout principal
        self.pack(fill=BOTH, expand=True)
        
        # Crear un frame para el menú lateral (izquierda)
        self.menu_frame = ttk.Frame(self, bootstyle="primary")
        self.menu_frame.pack(side=LEFT, fill=Y, padx=0, pady=0)
        
        # Crear un frame para el contenido principal (derecha)
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)
        
        # Configurar el menú lateral
        self._setup_sidebar()
        
        # Mostrar un contenido inicial de bienvenida
        self._show_welcome_view()
    
    def _setup_sidebar(self):
        """
        Configura el menú lateral con las opciones de navegación.
        """
        # Título del menú
        title_frame = ttk.Frame(self.menu_frame, bootstyle="primary")
        title_frame.pack(side=TOP, fill=X, padx=10, pady=10)
        
        title_label = ttk.Label(
            title_frame, 
            text="Broker Seguros", 
            font=("Helvetica", 12, "bold"),
            bootstyle="inverse-primary"
        )
        title_label.pack(side=TOP, padx=5, pady=5)
        
        # Separador
        ttk.Separator(self.menu_frame).pack(fill=X, padx=10)
        
        # Botones de navegación
        nav_frame = ttk.Frame(self.menu_frame, bootstyle="primary")
        nav_frame.pack(side=TOP, fill=X, padx=10, pady=10)
        
        # Botón de Clientes (visible para todos)
        btn_clientes = ttk.Button(
            nav_frame, 
            text="Clientes", 
            bootstyle="primary-outline",
            command=self._show_clientes_view
        )
        btn_clientes.pack(fill=X, padx=5, pady=5)
        
        # Botón de Corredores (solo visible para administradores)
        if self.is_admin:
            btn_corredores = ttk.Button(
                nav_frame, 
                text="Corredores", 
                bootstyle="primary-outline",
                command=self._show_corredores_view
            )
            btn_corredores.pack(fill=X, padx=5, pady=5)
        
        # Botón de Movimientos (visible para todos)
        btn_movimientos = ttk.Button(
            nav_frame, 
            text="Movimientos", 
            bootstyle="primary-outline",
            command=self._show_movimientos_view
        )
        btn_movimientos.pack(fill=X, padx=5, pady=5)
        
        # Información del usuario en la parte inferior
        user_frame = ttk.Frame(self.menu_frame, bootstyle="primary")
        user_frame.pack(side=BOTTOM, fill=X, padx=10, pady=10)
        
        # Separador antes de la información del usuario
        ttk.Separator(self.menu_frame).pack(side=BOTTOM, fill=X, padx=10, pady=5)
        
        # Etiqueta "Usuario"
        user_label = ttk.Label(
            user_frame, 
            text="Usuario:", 
            font=("Helvetica", 9),
            bootstyle="inverse-primary"
        )
        user_label.pack(side=TOP, anchor=W, padx=5)
        
        # Correo del usuario
        email_label = ttk.Label(
            user_frame, 
            text=self.user_email, 
            font=("Helvetica", 8),
            bootstyle="inverse-primary"
        )
        email_label.pack(side=TOP, anchor=W, padx=5)
        
        # Rol del usuario
        role_text = "Administrador" if self.is_admin else "Corredor"
        role_label = ttk.Label(
            user_frame, 
            text=f"Rol: {role_text}", 
            font=("Helvetica", 8),
            bootstyle="inverse-primary"
        )
        role_label.pack(side=TOP, anchor=W, padx=5, pady=(0, 5))
    
    def _clear_content(self):
        """
        Limpia el contenido actual del frame principal.
        """
        # Eliminar todos los widgets del frame de contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _show_welcome_view(self):
        """
        Muestra la vista de bienvenida.
        """
        self._clear_content()
        
        # Crear un mensaje de bienvenida
        welcome_frame = ttk.Frame(self.content_frame)
        welcome_frame.pack(fill=BOTH, expand=True)
        
        # Título de bienvenida
        title = ttk.Label(
            welcome_frame, 
            text="¡Bienvenido a Broker Seguros!", 
            font=("Helvetica", 16, "bold")
        )
        title.pack(pady=(50, 20))
        
        # Mensaje personalizado según el rol
        if self.is_admin:
            message = "Acceso completo al sistema como administrador."
        else:
            message = "Acceso a la gestión de clientes y transacciones."
        
        subtitle = ttk.Label(
            welcome_frame, 
            text=message, 
            font=("Helvetica", 12)
        )
        subtitle.pack(pady=10)
        
        # Instrucciones
        instructions = ttk.Label(
            welcome_frame, 
            text="Utilice el menú lateral para navegar por las diferentes secciones.", 
            font=("Helvetica", 10)
        )
        instructions.pack(pady=10)
    
    def _show_clientes_view(self):
        """
        Muestra la vista de clientes.
        """
        self._clear_content()
        
        # Placeholder para la vista de clientes
        label = ttk.Label(
            self.content_frame, 
            text="Vista de Clientes (En desarrollo)", 
            font=("Helvetica", 14, "bold")
        )
        label.pack(pady=50)
        
        # TODO: Implementar la vista real de clientes
    
    def _show_corredores_view(self):
        """
        Muestra la vista de corredores (solo para administradores).
        """
        if not self.is_admin:
            logger.warning("Intento de acceso a vista de corredores por un usuario no administrador")
            return
        
        self._clear_content()
        
        # Placeholder para la vista de corredores
        label = ttk.Label(
            self.content_frame, 
            text="Vista de Corredores (En desarrollo)", 
            font=("Helvetica", 14, "bold")
        )
        label.pack(pady=50)
        
        # TODO: Implementar la vista real de corredores
    
    def _show_movimientos_view(self):
        """
        Muestra la vista de movimientos.
        """
        self._clear_content()
        
        # Placeholder para la vista de movimientos
        label = ttk.Label(
            self.content_frame, 
            text="Vista de Movimientos (En desarrollo)", 
            font=("Helvetica", 14, "bold")
        )
        label.pack(pady=50)
        
        # TODO: Implementar la vista real de movimientos
