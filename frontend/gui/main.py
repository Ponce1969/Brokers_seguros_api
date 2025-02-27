"""
Punto de entrada principal de la aplicación
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtNetwork import QNetworkProxyFactory
from frontend.gui.views.login_view import LoginView
from frontend.gui.core.di_container import contenedor
from frontend.gui.services.network_manager import NetworkManager

# Configurar logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Configurar niveles específicos por módulo
logging.getLogger('frontend.gui.services.network_manager').setLevel(logging.WARNING)
logging.getLogger('frontend.gui.models').setLevel(logging.WARNING)
logging.getLogger('frontend.gui.viewmodels').setLevel(logging.WARNING)
logging.getLogger('frontend.gui.views').setLevel(logging.WARNING)

# Solo mostrar logs importantes de la aplicación principal
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    """Función principal que inicia la aplicación"""
    try:
        # Suprimir mensajes de advertencia sobre propiedades QSS no reconocidas
        import os
        os.environ["QT_LOGGING_RULES"] = "qt.qpa.style=false"
        
        # Inicializar la aplicación Qt
        app = QApplication(sys.argv)

        # Configuración de red para QNetworkAccessManager
        QNetworkProxyFactory.setUseSystemConfiguration(True)

        logger.info("🚀 Iniciando aplicación...")

        # Asegurarse de que el NetworkManager esté inicializado
        network_manager = contenedor.resolver(NetworkManager)

        # Crear y mostrar la ventana de login
        login_window = LoginView()

        # Centrar la ventana en la pantalla
        screen = app.primaryScreen().geometry()
        x = (screen.width() - login_window.width()) // 2
        y = (screen.height() - login_window.height()) // 2
        login_window.move(x, y)

        logger.info("✨ Mostrando ventana de login")
        login_window.show()

        return app.exec()

    except Exception as e:
        logger.error(f"❌ Error al iniciar la aplicación: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
