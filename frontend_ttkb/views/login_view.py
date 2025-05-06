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
        self.pack(fill=BOTH, expand=YES, padx=40, pady=40)
        
        # Marco principal con borde y sombra
        main_frame = ttk.Frame(self, bootstyle="default")
        main_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        
        # Título y logo
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=X, pady=(20, 10))
        
        # Crear un círculo azul como logo provisional
        logo_canvas = ttk.Canvas(title_frame, width=80, height=80, highlightthickness=0)
        logo_canvas.pack(pady=(10, 5))
        
        # Dibujar un círculo azul con un "BS" dentro (Broker Seguros)
        logo_canvas.create_oval(10, 10, 70, 70, fill="#3a7ebf", outline="#2a5c8f", width=2)
        logo_canvas.create_text(40, 40, text="BS", fill="white", font=("Arial", 24, "bold"))
        
        title_label = ttk.Label(
            title_frame,
            text="Broker Seguros",
            font=("Helvetica", 24, "bold"),
            bootstyle="info"
        )
        title_label.pack(pady=(5, 0))
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Sistema de gestión de seguros",
            font=("Helvetica", 12),
            bootstyle="secondary"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Separador decorativo
        separator = ttk.Separator(main_frame)
        separator.pack(fill=X, padx=40, pady=10)
        
        # Formulario de login
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=BOTH, expand=YES, padx=40, pady=(0, 20))
        
        # Username con icono
        username_frame = ttk.Frame(form_frame)
        username_frame.pack(fill=X, pady=10)
        
        # Etiqueta de usuario con icono
        username_label = ttk.Label(
            username_frame, 
            text="Usuario",
            bootstyle="info"
        )
        username_label.pack(anchor=W, padx=(0, 10), pady=(0, 5))
        
        # Campo de entrada con estilo mejorado
        username_entry = ttk.Entry(
            username_frame, 
            textvariable=self.username_var,
            width=35,
            bootstyle="info"
        )
        username_entry.pack(fill=X, expand=YES)
        
        # Password con icono
        password_frame = ttk.Frame(form_frame)
        password_frame.pack(fill=X, pady=10)
        
        # Etiqueta de contraseña con icono
        password_label = ttk.Label(
            password_frame, 
            text="Contraseña",
            bootstyle="info"
        )
        password_label.pack(anchor=W, padx=(0, 10), pady=(0, 5))
        
        # Campo de contraseña con estilo mejorado
        password_entry = ttk.Entry(
            password_frame, 
            textvariable=self.password_var,
            show="●",  # Punto sólido en lugar de asterisco
            width=35,
            bootstyle="info"
        )
        password_entry.pack(fill=X, expand=YES)
        
        # Opciones adicionales
        options_frame = ttk.Frame(form_frame)
        options_frame.pack(fill=X, pady=15)
        
        # Checkbox de recordar en la izquierda
        remember_check = ttk.Checkbutton(
            options_frame,
            text="Recordar credenciales",
            variable=self.remember_var,
            bootstyle="round-toggle-info"
        )
        remember_check.pack(side=LEFT)
        
        # Enlace de olvidé mi contraseña a la derecha
        forgot_link = ttk.Label(
            options_frame,
            text="¿Olvidó su contraseña?",
            cursor="hand2",
            bootstyle="info"
        )
        forgot_link.pack(side=RIGHT)
        forgot_link.bind("<Button-1>", lambda e: Messagebox.show_info(
            "Esta funcionalidad estará disponible próximamente.",
            "Recordatorio de contraseña"
        ))
        
        # Separador decorativo antes de los botones
        separator2 = ttk.Separator(form_frame)
        separator2.pack(fill=X, pady=15)
        
        # Botones de acción
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=X, pady=10)
        
        # Botón principal de iniciar sesión
        login_button = ttk.Button(
            button_frame,
            text="INICIAR SESIÓN",
            command=self.login,
            bootstyle="info",
            width=20
        )
        login_button.pack(side=RIGHT, padx=5)
        
        # Botón de cancelar
        cancel_button = ttk.Button(
            button_frame,
            text="CANCELAR",
            command=self.parent.destroy,
            bootstyle="outline-danger",
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
