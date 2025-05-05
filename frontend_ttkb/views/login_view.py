#!/usr/bin/env python3
"""
Vista de inicio de sesión para Broker Seguros

Permite a usuarios (administrador y corredores) acceder al sistema
con sus credenciales y obtiene el token JWT para sesiones posteriores.
"""

import logging
import json
from typing import Optional, Callable, Dict, Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

# Importaciones locales
import sys
sys.path.append('/home/gonzapython/CascadeProjects/Brokerseguros')
from frontend_ttkb.api_client import APIClient
from frontend_ttkb.config import DEFAULT_USERNAME, DEFAULT_PASSWORD

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LoginView(ttk.Frame):
    """
    Vista de login para la aplicación Broker Seguros.
    
    Permite a los usuarios iniciar sesión en el sistema y
    gestiona la autenticación con el backend.
    """
    
    def __init__(self, parent, on_login_success: Callable[[Dict[str, Any]], None]):
        """
        Inicializa la vista de login.
        
        Args:
            parent: El widget padre de esta vista.
            on_login_success: Función a llamar cuando el login sea exitoso.
                              Recibirá un diccionario con la información del usuario.
        """
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success
        self.api_client = APIClient()
        
        # Variables para los campos del formulario
        self.username_var = ttk.StringVar(value=DEFAULT_USERNAME)
        self.password_var = ttk.StringVar(value=DEFAULT_PASSWORD)
        self.remember_var = ttk.BooleanVar(value=True)
        
        # Configurar la interfaz de usuario
        self.setup_ui()
        
        logger.info("Vista de login inicializada correctamente")
        
    def setup_ui(self):
        """
        Configura los elementos de la interfaz de usuario para el login.
        """
        # Contenedor principal con padding
        self.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        
        # Título y logo (podría agregarse un logo más adelante)
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="Broker Seguros",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=10)
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Sistema de gestión de seguros",
            font=("Helvetica", 12)
        )
        subtitle_label.pack()
        
        # Formulario de login
        form_frame = ttk.Frame(self)
        form_frame.pack(fill=BOTH, expand=YES, pady=20)
        
        # Username
        username_frame = ttk.Frame(form_frame)
        username_frame.pack(fill=X, pady=5)
        
        username_label = ttk.Label(
            username_frame, 
            text="Usuario:",
            width=15,
            anchor=E
        )
        username_label.pack(side=LEFT, padx=(0, 10))
        
        username_entry = ttk.Entry(
            username_frame, 
            textvariable=self.username_var,
            width=30
        )
        username_entry.pack(side=LEFT, fill=X, expand=YES)
        
        # Password
        password_frame = ttk.Frame(form_frame)
        password_frame.pack(fill=X, pady=5)
        
        password_label = ttk.Label(
            password_frame, 
            text="Contraseña:",
            width=15,
            anchor=E
        )
        password_label.pack(side=LEFT, padx=(0, 10))
        
        password_entry = ttk.Entry(
            password_frame, 
            textvariable=self.password_var,
            show="*",
            width=30
        )
        password_entry.pack(side=LEFT, fill=X, expand=YES)
        
        # Remember me checkbox
        remember_frame = ttk.Frame(form_frame)
        remember_frame.pack(fill=X, pady=10)
        
        remember_check = ttk.Checkbutton(
            remember_frame,
            text="Recordar credenciales",
            variable=self.remember_var,
            bootstyle="round-toggle"
        )
        remember_check.pack(padx=(75, 0), anchor=W)
        
        # Botones de acción
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=X, pady=20)
        
        login_button = ttk.Button(
            button_frame,
            text="Iniciar sesión",
            command=self.login,
            bootstyle=SUCCESS,
            width=15
        )
        login_button.pack(side=RIGHT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.parent.destroy,
            bootstyle=DANGER,
            width=15
        )
        cancel_button.pack(side=RIGHT, padx=5)
        
        # Configurar eventos de teclado
        password_entry.bind("<Return>", lambda event: self.login())
        username_entry.bind("<Return>", lambda event: password_entry.focus())
        
        # Dar foco al campo de usuario si está vacío
        if not self.username_var.get():
            username_entry.focus()
        else:
            password_entry.focus()
        
        logger.info("UI de login configurada correctamente")
    
    def login(self):
        """
        Intenta autenticar al usuario con las credenciales proporcionadas.
        """
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        # Validación básica
        if not username or not password:
            Messagebox.show_error(
                "Por favor ingrese nombre de usuario y contraseña",
                "Error de validación"
            )
            return
        
        try:
            # Intentar autenticar usando el cliente API
            logger.info(f"Intentando autenticar a usuario: {username}")
            
            # Llamar al endpoint de login
            result = self.api_client.login(username, password)
            
            if result and "access_token" in result:
                # Login exitoso
                token = result["access_token"]
                token_type = result.get("token_type", "bearer")
                
                # Guardar el token en el cliente API para futuras solicitudes
                self.api_client.set_token(token, token_type)
                
                # Crear un diccionario con la información básica del usuario
                # En esta implementación, asumimos que rpd.ramas@gmail.com es el admin
                # y cualquier otro usuario es un corredor normal
                is_admin = (username.lower() == 'rpd.ramas@gmail.com')
                
                user_info = {
                    'email': username,
                    'nombres': 'Usuario',  # Valores por defecto
                    'apellidos': '',
                    'is_active': True,
                    'is_superuser': is_admin,
                    'role': 'admin' if is_admin else 'corredor',
                    'access_token': token
                }
                
                # Notificar éxito al callback
                logger.info(f"Usuario autenticado correctamente: {username} (Rol: {user_info.get('role', 'desconocido')})")
                self.on_login_success(user_info)
            else:
                # Error de autenticación - credenciales inválidas
                Messagebox.show_error(
                    "Credenciales inválidas. Por favor intente nuevamente.",
                    "Error de autenticación"
                )
        
        except Exception as e:
            # Error en la comunicación con el servidor
            logger.error(f"Error durante la autenticación: {str(e)}")
            Messagebox.show_error(
                f"Error de conexión: {str(e)}",
                "Error de autenticación"
            )
    
    # Hemos eliminado el método get_user_info ya que ahora estamos creando la información del usuario
    # directamente a partir del username durante el login. Esto evita depender del endpoint /api/v1/users/me
