# Frontend Qt Network Migration

## Cambios Realizados

Se ha migrado el frontend a usar QNetworkAccessManager para todas las comunicaciones HTTP, eliminando el uso de aiohttp y código asíncrono.

### Principales Cambios

1. Eliminación de código antiguo:
   - Eliminado `api_service.py` (aiohttp)
   - Eliminada capa de repositories
   - Eliminado código asíncrono

2. Implementación de QNetworkAccessManager:
   - Manejo de peticiones HTTP
   - Manejo de respuestas y errores
   - Integración con señales Qt

## Uso de QNetworkAccessManager

### Características Principales

- Abstracción de alto nivel para operaciones HTTP
- Manejo automático de cookies y autenticación
- Soporte para HTTP/2 por defecto
- Manejo de redirecciones configurable

### Ejemplo de Uso

```python
from PyQt6.QtCore import QUrl
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest

class MiClase:
    def __init__(self):
        self.api = QNetworkAccessManager()
        self.api.response_received.connect(self._handle_response)
        self.api.error_occurred.connect(self._handle_error)

    def hacer_peticion(self):
        request = QNetworkRequest(QUrl("http://api.ejemplo.com/datos"))
        self.api.get(request)

    def _handle_response(self, response):
        # Procesar respuesta
        pass

    def _handle_error(self, error_msg):
        # Manejar error
        pass
```

### Notas Importantes

1. Redirecciones:
   - Política por defecto: `QNetworkRequest::NoLessSafeRedirectPolicy`
   - Para manejo manual: `request.setAttribute(QNetworkRequest::RedirectPolicyAttribute, QNetworkRequest::ManualRedirectPolicy)`

2. HTTP/2:
   - Habilitado por defecto
   - Para deshabilitar: `request.setAttribute(QNetworkRequest::Http2AllowedAttribute, false)`

3. Señales:
   - `errorOccurred` en lugar de `error` (cambio en Qt6)
   - Manejo de respuestas a través de señales

## Estructura del Código

```
frontend/gui/
├── services/
│   └── network_manager.py     # Wrapper de QNetworkAccessManager
├── viewmodels/
│   ├── corredor_viewmodel.py  # Usa NetworkManager
│   └── movimiento_vigencia_viewmodel.py
└── views/
    └── ...
```

## Referencias

- [Qt Network Documentation](https://doc.qt.io/qt-6/qtnetwork-index.html)
- [QNetworkAccessManager Class](https://doc.qt.io/qt-6/qnetworkaccessmanager.html)
- [QNetworkRequest Class](https://doc.qt.io/qt-6/qnetworkrequest.html)
- [QNetworkReply Class](https://doc.qt.io/qt-6/qnetworkreply.html)
