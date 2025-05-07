#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicacion de Broker Seguros

Esta nueva implementacion utiliza ttkbootstrap para una interfaz moderna
y esta diseñada para alinearse perfectamente con lo que el backend entrega.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from dotenv import load_dotenv

# Importaciones locales
import sys
sys.path.append('/home/gonzapython/CascadeProjects/Brokerseguros')
from frontend_ttkb.views.login_view import LoginView
from frontend_ttkb.views.main_view import MainView
from frontend_ttkb.views.cliente_view import ClienteView
from frontend_ttkb.api_client import APIClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importaciones locales
from frontend_ttkb.config import APP_TITLE, APP_WIDTH, APP_HEIGHT, APP_THEME

class BrokerSegurosApp:
    """
    Aplicacion principal para Broker Seguros.
    
    Esta clase maneja la interfaz de usuario principal y la navegacion
    entre diferentes vistas de la aplicacion.
    """
    
    def __init__(self):
        """
        Inicializa la aplicacion principal.
        """
        # Crear la ventana principal con ttkbootstrap
        self.root = ttk.Window(
            title=APP_TITLE,
            themename=APP_THEME,
            size=(APP_WIDTH, APP_HEIGHT),
            position=(100, 100),
            minsize=(800, 600)
        )
        
        # Cliente API para comunicarse con el backend
        self.api_client = APIClient()
        
        # Datos del usuario autenticado
        self.user_data = None
        
        # Vista actual (principal o login)
        self.current_view = None
        
        # Frame principal para contener las vistas
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=YES)
        
        # Configurar el cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Mostrar la vista de login inicialmente
        self.show_login()
        
        logger.info("Aplicacion inicializada correctamente")
    
    def setup_main_view(self):
        """
        Configura la vista principal de la aplicación después del login.
        """
        # Limpiar el frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Crear una estructura de tres partes: barra lateral, contenido y barra de estado
        self.sidebar_frame = ttk.Frame(self.main_frame, bootstyle=SECONDARY)
        self.content_frame = ttk.Frame(self.main_frame)
        self.status_frame = ttk.Frame(self.main_frame, height=25)
        
        # Colocar los frames en la ventana
        self.sidebar_frame.pack(side=LEFT, fill=Y, padx=0, pady=0)
        self.content_frame.pack(side=TOP, fill=BOTH, expand=YES, padx=10, pady=10)
        self.status_frame.pack(side=BOTTOM, fill=X, padx=0, pady=0)
        
        # Configurar barra lateral con opciones de menú
        self.setup_sidebar()
        
        # Configurar barra de estado
        self.setup_status_bar()
        
        # Mostrar panel de bienvenida
        self.show_welcome_panel()
        
        logger.info("Vista principal configurada correctamente")
    
    def setup_sidebar(self):
        """
        Configura la barra lateral de navegación.
        """
        # Título de la barra lateral
        sidebar_title = ttk.Label(
            self.sidebar_frame,
            text="MENÚ",
            font=("Helvetica", 12, "bold"),
            bootstyle="inverse-secondary"
        )
        sidebar_title.pack(fill=X, padx=10, pady=10)
        
        # Botones de navegación
        button_width = 20
        
        # Botón de clientes (visible para todos)
        clientes_btn = ttk.Button(
            self.sidebar_frame,
            text="Clientes",
            command=self.show_clientes,
            width=button_width,
            bootstyle="secondary-outline"
        )
        clientes_btn.pack(fill=X, padx=5, pady=2)
        
        # Botón de corredores (solo visible para administradores)
        if self.user_data and self.user_data.get('role') == 'admin':
            corredores_btn = ttk.Button(
                self.sidebar_frame,
                text="Corredores",
                command=self.show_corredores,
                width=button_width,
                bootstyle="secondary-outline"
            )
            corredores_btn.pack(fill=X, padx=5, pady=2)
        
        # Botón de movimientos (visible para todos)
        movimientos_btn = ttk.Button(
            self.sidebar_frame,
            text="Movimientos",
            command=self.show_movimientos,
            width=button_width,
            bootstyle="secondary-outline"
        )
        movimientos_btn.pack(fill=X, padx=5, pady=2)
        
        # Separador
        ttk.Separator(self.sidebar_frame).pack(fill=X, padx=5, pady=10)
        
        # Información del usuario
        if self.user_data:
            user_frame = ttk.LabelFrame(self.sidebar_frame, text="Usuario")
            user_frame.pack(fill=X, padx=5, pady=5)
            
            # Nombre del usuario
            nombre = f"{self.user_data.get('nombres', '')} {self.user_data.get('apellidos', '')}".strip()
            nombre = nombre if nombre else self.user_data.get('email', 'Usuario')
            ttk.Label(user_frame, text=nombre, wraplength=180).pack(anchor=W, padx=5, pady=2)
            
            # Rol del usuario
            rol = "Administrador" if self.user_data.get('role') == 'admin' else "Corredor"
            ttk.Label(user_frame, text=f"Rol: {rol}").pack(anchor=W, padx=5, pady=2)
        
        # Botón de cerrar sesión
        logout_btn = ttk.Button(
            self.sidebar_frame,
            text="Cerrar Sesión",
            command=self.logout,
            width=button_width,
            bootstyle="secondary-outline"
        )
        logout_btn.pack(side=BOTTOM, fill=X, padx=5, pady=10)
    
    def setup_status_bar(self):
        """
        Configura la barra de estado en la parte inferior.
        """
        # Separador antes de la barra de estado
        ttk.Separator(self.main_frame).pack(fill=X, pady=2)
        
        # Barra de estado (texto a la izquierda)
        self.status_label = ttk.Label(self.status_frame, text="Listo")
        self.status_label.pack(side=LEFT, padx=10)
        
        # Texto de la versión (a la derecha)
        version_label = ttk.Label(self.status_frame, text="v0.1.0")
        version_label.pack(side=RIGHT, padx=10)
    
    def show_welcome_panel(self):
        """
        Muestra el panel de bienvenida al iniciar la aplicación.
        """
        # Limpiar el área de contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Panel de bienvenida
        welcome_frame = ttk.Frame(self.content_frame)
        welcome_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        
        # Título de bienvenida
        welcome_title = ttk.Label(
            welcome_frame,
            text="¡Bienvenido a Broker Seguros!",
            font=("Helvetica", 18, "bold")
        )
        welcome_title.pack(pady=20)
        
        # Mensaje personalizado para el usuario
        if self.user_data:
            nombre = f"{self.user_data.get('nombres', '')} {self.user_data.get('apellidos', '')}".strip()
            nombre = nombre if nombre else self.user_data.get('email', 'Usuario')
            msg = f"Hola {nombre}, selecciona una opción del menú para comenzar."
        else:
            msg = "Selecciona una opción del menú para comenzar."
            
        welcome_msg = ttk.Label(
            welcome_frame,
            text=msg,
            font=("Helvetica", 12)
        )
        welcome_msg.pack(pady=10)
        
        # Información del sistema
        info_frame = ttk.LabelFrame(welcome_frame, text="Información del Sistema")
        info_frame.pack(fill=X, expand=NO, pady=20)
        
        # Contenido de la información
        ttk.Label(info_frame, text=f"Tema: {APP_THEME}").pack(anchor=W, padx=10, pady=5)
        ttk.Label(info_frame, text=f"Resolución: {APP_WIDTH}x{APP_HEIGHT}").pack(anchor=W, padx=10, pady=5)
        ttk.Label(info_frame, text="Versión: 0.1.0").pack(anchor=W, padx=10, pady=5)
        
        # Actualizar barra de estado
        self.status_label.config(text="Listo")

    def show_login(self):
        """
        Muestra la vista de login.
        """
        # Limpiar el frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Crear la vista de login
        self.current_view = LoginView(self.main_frame, self.on_login_success)
        
        logger.info("Vista de login mostrada")
    
    def on_login_success(self, user_data: Dict[str, Any]):
        """
        Callback que se ejecuta cuando el login es exitoso.
        
        Args:
            user_data: Datos del usuario autenticado.
        """
        # Guardar datos del usuario
        self.user_data = user_data
        logger.info(f"Login exitoso para usuario: {user_data.get('email')} (Rol: {user_data.get('role')})")
        
        # Configurar el cliente API con el token
        self.api_client.set_token(self.user_data.get('access_token'))
        
        # Mostrar la vista principal
        self.setup_main_view()
    
    def logout(self):
        """
        Cierra la sesión del usuario.
        """
        # Eliminar datos del usuario
        self.user_data = None
        
        # Limpiar token
        self.api_client.clear_token()
        
        # Volver a la vista de login
        self.show_login()
        
        logger.info("Usuario cerró sesión")
    
    def show_clientes(self):
        """
        Muestra la vista de clientes con todas sus funcionalidades.
        """
        # Limpiar el área de contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Crear la vista de clientes
        cliente_view = ClienteView(
            self.content_frame,
            self.api_client,
            self.user_data
        )
        cliente_view.pack(fill=BOTH, expand=YES)
        
        # Actualizar barra de estado
        self.status_label.config(text="Vista de clientes")
        
    def show_corredores(self):
        """
        Muestra la vista de corredores completa con todas sus funcionalidades.
        """
        # Verificar que el usuario tenga permisos de administrador
        if self.user_data.get('role') != 'admin':
            logger.warning("Intento de acceso a vista de corredores por un usuario no administrador")
            Messagebox.show_warning(
                "No tienes permisos para acceder a la gestión de corredores.",
                "Acceso restringido"
            )
            return
        
        logger.info("Cargando vista de corredores...")
            
        # Limpiar el área de contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        try:
            # Importar la vista de corredores
            from frontend_ttkb.views.corredores_view import CorredoresView
            
            # Crear la vista de corredores
            corredor_view = CorredoresView(
                self.content_frame,
                self.api_client
            )
            
            # Actualizar barra de estado
            self.status_label.config(text="Vista de corredores cargada exitosamente")
            logger.info(f"Vista de corredores mostrada para usuario: {self.user_data.get('email')} (Rol: {self.user_data.get('role')})")
        except Exception as e:
            # Manejar cualquier error durante la carga
            logger.error(f"Error al cargar vista de corredores: {str(e)}")
            
            # Mostrar mensaje de error
            Messagebox.show_error(
                f"No se pudo cargar la vista de corredores: {str(e)}",
                "Error"
            )
            
            # Mostrar vista placeholder en caso de error
            ttk.Label(
                self.content_frame, 
                text="Error al cargar la vista de Corredores",
                font=("Helvetica", 16, "bold")
            ).pack(pady=20)
            
            # Actualizar barra de estado
            self.status_label.config(text="Error al cargar vista de corredores")
        self.status_label.config(text="Vista de corredores")

    def show_movimientos(self):
        """
        Muestra la vista de movimientos (placeholder).
        """
        # Limpiar el área de contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Título
        ttk.Label(
            self.content_frame, 
            text="Vista de Movimientos",
            font=("Helvetica", 16, "bold")
        ).pack(pady=20)
        
        ttk.Label(
            self.content_frame,
            text="La vista de movimientos se implementará en el próximo paso.",
            font=("Helvetica", 12)
        ).pack(pady=10)
        
        # Actualizar barra de estado
        self.status_label.config(text="Vista de movimientos")
    
    def test_connection(self):
        """
        Prueba la conexion con el backend.
        """
        try:
            import requests
            from frontend_ttkb.config import API_URL
            
            # Intentar conectar con el backend
            response = requests.get(f"{API_URL}/api/v1/clientes/", timeout=5)
            
            if response.status_code == 200:
                # Mostrar un ejemplo de los datos recibidos
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    sample = data[0] if len(data) > 0 else {}
                    sample_text = ", ".join([f"{k}: {v}" for k, v in list(sample.items())[:5]])
                    message = f"¡Conexión exitosa! Recibidos {len(data)} registros\n\nPrimer registro (muestra): {sample_text}..."
                else:
                    message = f"¡Conexión exitosa! Respuesta: {data}"
                Messagebox.show_info(message, "Prueba de conexion")
            else:
                Messagebox.show_error(f"Error {response.status_code}: {response.text}", "Error de conexion")
        
        except Exception as e:
            logger.error(f"Error al probar conexion: {e}")
            Messagebox.show_error(f"Error: {str(e)}", "Error de conexion")
    
    def on_close(self):
        """
        Maneja el cierre de la aplicacion.
        """
        logger.info("Cerrando aplicacion...")
        self.root.destroy()
    
    def run(self):
        """
        Ejecuta la aplicacion.
        """
        logger.info("Iniciando la aplicacion...")
        self.root.mainloop()


def main():
    """
    Funcion principal para iniciar la aplicacion.
    """
    # Cargar variables de entorno
    load_dotenv()
    
    # Iniciar la aplicacion
    app = BrokerSegurosApp()
    app.run()


if __name__ == "__main__":
    main()
