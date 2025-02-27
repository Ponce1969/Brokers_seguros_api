"""
Servicio para manejar las comunicaciones con la API REST usando QNetworkAccessManager
"""

from PyQt6.QtCore import QObject, pyqtSignal, QUrl, QByteArray
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import json
from typing import Optional, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)

class NetworkManager(QObject):
    # Señales para notificar respuestas y errores
    response_received = pyqtSignal(object)  # Para respuestas JSON (puede ser dict o list)
    error_occurred = pyqtSignal(str)      # Para errores
    token_expired = pyqtSignal()          # Para manejar expiración de token

    def __init__(self, base_url: str = "http://localhost:8000", parent: Optional[QObject] = None):
        super().__init__(parent)
        self.base_url = base_url.rstrip("/")
        self.manager = QNetworkAccessManager()
        self.token: Optional[str] = None
        
        # Conectar la señal finished del manager
        self.manager.finished.connect(self._handle_response)

    def set_token(self, token: str) -> None:
        """Establece el token de autenticación para las peticiones"""
        self.token = token

    def _create_request(self, endpoint: str) -> QNetworkRequest:
        """Crea una petición HTTP con las cabeceras necesarias"""
        url = QUrl(f"{self.base_url}/{endpoint}")
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        
        if self.token:
            request.setRawHeader(b"Authorization", f"Bearer {self.token}".encode())
        
        return request

    def _handle_response(self, reply: QNetworkReply) -> None:
        """Procesa la respuesta HTTP recibida"""
        try:
            if reply.error() == QNetworkReply.NetworkError.NoError:
                response_data = reply.readAll().data().decode('utf-8')
                try:
                    json_data = json.loads(response_data)
                    self.response_received.emit(json_data)
                except json.JSONDecodeError as e:
                    logger.error(f"Error decodificando JSON: {e}")
                    self.error_occurred.emit("Error al procesar la respuesta del servidor")
            else:
                error_msg = reply.errorString()
                if reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute) == 401:
                    self.token_expired.emit()
                logger.error(f"Error en la petición: {error_msg}")
                self.error_occurred.emit(error_msg)
        except Exception as e:
            logger.error(f"Error procesando respuesta: {e}")
            self.error_occurred.emit(str(e))
        finally:
            reply.deleteLater()

    def get(self, endpoint: str) -> None:
        """Realiza una petición GET"""
        request = self._create_request(endpoint)
        self.manager.get(request)

    def post(self, endpoint: str, data: Dict[str, Any]) -> None:
        """Realiza una petición POST"""
        request = self._create_request(endpoint)
        json_data = QByteArray(json.dumps(data).encode('utf-8'))
        self.manager.post(request, json_data)

    def put(self, endpoint: str, data: Dict[str, Any]) -> None:
        """Realiza una petición PUT"""
        request = self._create_request(endpoint)
        json_data = QByteArray(json.dumps(data).encode('utf-8'))
        self.manager.put(request, json_data)

    def delete(self, endpoint: str) -> None:
        """Realiza una petición DELETE"""
        request = self._create_request(endpoint)
        self.manager.deleteResource(request)
