"""
Configuración del frontend

Este archivo mantiene todas las constantes y configuraciones del frontend en un solo lugar
para facilitar cambios y mantenimiento.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la API
API_URL = os.getenv("API_URL", "http://localhost:8000")
API_PREFIX = os.getenv("API_PREFIX", "api/v1")

# Endpoints de la API
ENDPOINT_LOGIN = f"{API_PREFIX}/login/access-token"
ENDPOINT_USERS_ME = f"{API_PREFIX}/users/me"
ENDPOINT_CLIENTES = f"{API_PREFIX}/clientes"
ENDPOINT_CORREDORES = f"{API_PREFIX}/corredores"
ENDPOINT_MOVIMIENTOS = f"{API_PREFIX}/movimientos"

# Configuración de la UI
APP_TITLE = "Broker Seguros"
APP_WIDTH = 1024
APP_HEIGHT = 768

# Tema de la aplicación
APP_THEME = "cosmo"  # Opciones: 'cosmo', 'flatly', 'litera', 'minty', 'lumen', 'sandstone', 'yeti', 'pulse', 'united', 'morph', 'journal', 'darkly'

# Modos de visualización
MODO_ADMIN = "admin"
MODO_CORREDOR = "corredor"

# Credenciales predeterminadas para desarrollo
DEFAULT_USERNAME = os.getenv("DEFAULT_ADMIN_EMAIL", "rpd.ramas@gmail.com")
DEFAULT_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "Gallinal2218**")

# Configuración de tiempo de espera para peticiones HTTP (en segundos)
HTTP_TIMEOUT = 10

# Mensajes de la aplicación
MSG_ERROR_AUTENTICACION = "Error de autenticación: credenciales inválidas o sesión expirada"
MSG_ERROR_PERMISOS = "No tiene permisos para realizar esta acción"
MSG_ERROR_CONEXION = "No se pudo conectar con el servidor. Verifique su conexión a internet"
MSG_ERROR_DATOS = "Los datos recibidos no tienen el formato esperado"
MSG_ERROR_SERVIDOR = "Error en el servidor. Contacte al administrador del sistema"
MSG_SESION_EXPIRADA = "Su sesión ha expirado. Por favor, inicie sesión nuevamente."

# Configuración de paginación
PAGINA_TAMANO = 10
