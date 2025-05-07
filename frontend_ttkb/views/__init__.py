"""
Vistas para la aplicación Broker Seguros.

Este paquete contiene todas las vistas (interfaces) de la aplicación.
"""

# Importar todas las vistas para asegurar su disponibilidad
from frontend_ttkb.views.login_view import LoginView
from frontend_ttkb.views.main_view import MainView
from frontend_ttkb.views.cliente_view import ClienteView

# Importar explícitamente la vista de corredores y su diálogo
try:
    from frontend_ttkb.views.corredores_view import CorredoresView
    from frontend_ttkb.views.dialogo_corredor import DialogoCorredor
    __all__ = ['LoginView', 'MainView', 'ClienteView', 'CorredoresView', 'DialogoCorredor']
except ImportError as e:
    import logging
    logging.getLogger(__name__).error(f"Error al importar vistas de corredores: {e}")
    __all__ = ['LoginView', 'MainView', 'ClienteView']
