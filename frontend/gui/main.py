"""
Punto de entrada principal de la aplicación
"""

import sys
import logging
import asyncio
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from gui.views.login_view import LoginView

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def handle_exception(loop, context):
    """Manejador global de excepciones para el event loop"""
    logger.error(f"❌ Error en el event loop: {context}")

def main():
    """Función principal que inicia la aplicación"""
    try:
        # Crear la aplicación Qt
        app = QApplication(sys.argv)
        
        # Configurar el event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_exception_handler(handle_exception)
        
        # Crear timer para procesar el event loop
        timer = QTimer()
        timer.timeout.connect(lambda: loop.stop() if loop.is_running() else None)
        timer.start(50)  # 50ms interval
        
        logger.info("🚀 Iniciando aplicación...")

        # Crear y mostrar la ventana de login
        login_window = LoginView()

        # Centrar la ventana en la pantalla
        screen = app.primaryScreen().geometry()
        x = (screen.width() - login_window.width()) // 2
        y = (screen.height() - login_window.height()) // 2
        login_window.move(x, y)

        logger.info("✨ Mostrando ventana de login")
        login_window.show()

        # Configurar el manejador de señales para limpieza
        def signal_handler(signum, frame):
            logger.info("🛑 Señal de terminación recibida")
            loop.stop()
            app.quit()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Iniciar el loop de eventos
        return app.exec()

    except Exception as e:
        logger.error(f"❌ Error al iniciar la aplicación: {str(e)}")
        raise
    finally:
        if 'loop' in locals():
            loop.close()

if __name__ == "__main__":
    sys.exit(main())
