import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import pytest
from frontend.gui.viewmodels.cliente.cliente_network_handler import ClienteNetworkHandler

class DummyAPI:
    def __init__(self):
        self.last_post = None
        self.last_put = None
        self.last_delete = None
        self.last_get = None
        self.last_payload = None
        self.should_raise = False

    def post(self, url, payload):
        self.last_post = (url, payload)
        self.last_payload = payload
        if self.should_raise:
            raise Exception("Simulated POST error")
        return {"id": "uuid-123", **payload}

    def put(self, url, payload):
        self.last_put = (url, payload)
        self.last_payload = payload
        if self.should_raise:
            raise Exception("Simulated PUT error")
        return {"id": "uuid-123", **payload}

    def delete(self, url):
        self.last_delete = url
        if self.should_raise:
            raise Exception("Simulated DELETE error")
        return True

    def get(self, url):
        self.last_get = url
        if self.should_raise:
            raise Exception("Simulated GET error")
        return {"id": "uuid-123", "nombres": "Juan", "apellidos": "Pérez"}

    def get_sync(self, url):
        return [{"id": "uuid-123", "numero_cliente": 1, "nombres": "Juan", "apellidos": "Pérez"}]


def test_flujo_creacion_cliente_exitoso():
    """
    Verifica el flujo completo de creación de cliente usando el método público crear_cliente.
    """
    api = DummyAPI()
    handler = ClienteNetworkHandler(api)
    datos = {
        'nombres': 'Ana',
        'apellidos': 'García',
        'tipo_documento_id': 2,
        'numero_documento': '98765432',
        'fecha_nacimiento': '1985-05-20',
        'direccion': 'Av. Siempre Viva 742',
        'localidad': 'Montevideo',
        'telefonos': '24009999',
        'movil': '098765432',
        'mail': 'ana@mail.com',
        'observaciones': 'Cliente preferente',
        'creado_por_id': 2,
        'modificado_por_id': 2
    }
    # No debe lanzar excepción
    result = handler.crear_cliente(datos)
    # Verifica que el último payload enviado es correcto
    for campo in [
        'nombres','apellidos','tipo_documento_id','numero_documento','fecha_nacimiento',
        'direccion','localidad','telefonos','movil','mail','observaciones','creado_por_id','modificado_por_id'
    ]:
        assert campo in api.last_payload
    assert api.last_payload['nombres'] == 'Ana'
    assert result['id'] == 'uuid-123'


def test_flujo_creacion_cliente_error():
    """
    Verifica que el flujo completo de creación de cliente maneja correctamente errores de validación y de API.
    """
    api = DummyAPI()
    handler = ClienteNetworkHandler(api)
    # Caso 1: datos inválidos (falta campo obligatorio)
    datos_invalidos = {
        'nombres': 'Ana',
        # Falta 'apellidos'
        'tipo_documento_id': 2,
        'numero_documento': '98765432',
        'fecha_nacimiento': '1985-05-20',
        'direccion': 'Av. Siempre Viva 742',
        'localidad': 'Montevideo',
        'telefonos': '24009999',
        'movil': '098765432',
        'mail': 'ana@mail.com',
        'observaciones': 'Cliente preferente',
        'creado_por_id': 2,
        'modificado_por_id': 2
    }
    with pytest.raises(ValueError) as excinfo:
        handler.crear_cliente(datos_invalidos)
    assert "apellidos" in str(excinfo.value)

    # Caso 2: error en la API (simulado)
    api.should_raise = True
    datos_validos = {
        'nombres': 'Ana',
        'apellidos': 'García',
        'tipo_documento_id': 2,
        'numero_documento': '98765432',
        'fecha_nacimiento': '1985-05-20',
        'direccion': 'Av. Siempre Viva 742',
        'localidad': 'Montevideo',
        'telefonos': '24009999',
        'movil': '098765432',
        'mail': 'ana@mail.com',
        'observaciones': 'Cliente preferente',
        'creado_por_id': 2,
        'modificado_por_id': 2
    }
    with pytest.raises(Exception) as excinfo2:
        handler.crear_cliente(datos_validos)
    assert "Simulated POST error" in str(excinfo2.value)



def test_flujo_creacion_cliente_exitoso():
    """
    Verifica el flujo completo de creación de cliente usando el método público crear_cliente.
    """
    api = DummyAPI()
    handler = ClienteNetworkHandler(api)
    datos = {
        'nombres': 'Ana',
        'apellidos': 'García',
        'tipo_documento_id': 2,
        'numero_documento': '98765432',
        'fecha_nacimiento': '1985-05-20',
        'direccion': 'Av. Siempre Viva 742',
        'localidad': 'Montevideo',
        'telefonos': '24009999',
        'movil': '098765432',
        'mail': 'ana@mail.com',
        'observaciones': 'Cliente preferente',
        'creado_por_id': 2,
        'modificado_por_id': 2
    }
    # No debe lanzar excepción
    result = handler.crear_cliente(datos)
    # Verifica que el último payload enviado es correcto
    for campo in [
        'nombres','apellidos','tipo_documento_id','numero_documento','fecha_nacimiento',
        'direccion','localidad','telefonos','movil','mail','observaciones','creado_por_id','modificado_por_id'
    ]:
        assert campo in api.last_payload
    assert api.last_payload['nombres'] == 'Ana'
    assert result['id'] == 'uuid-123'


def test_flujo_creacion_cliente_error():
    """
    Verifica que el flujo completo de creación de cliente maneja correctamente errores de validación y de API.
    """
    api = DummyAPI()
    handler = ClienteNetworkHandler(api)
    # Caso 1: datos inválidos (falta campo obligatorio)
    datos_invalidos = {
        'nombres': 'Ana',
        # Falta 'apellidos'
        'tipo_documento_id': 2,
        'numero_documento': '98765432',
        'fecha_nacimiento': '1985-05-20',
        'direccion': 'Av. Siempre Viva 742',
        'localidad': 'Montevideo',
        'telefonos': '24009999',
        'movil': '098765432',
        'mail': 'ana@mail.com',
        'observaciones': 'Cliente preferente',
        'creado_por_id': 2,
        'modificado_por_id': 2
    }
    with pytest.raises(ValueError) as excinfo:
        handler.crear_cliente(datos_invalidos)
    assert "apellidos" in str(excinfo.value)

    # Caso 2: error en la API (simulado)
    api.should_raise = True
    datos_validos = {
        'nombres': 'Ana',
        'apellidos': 'García',
        'tipo_documento_id': 2,
        'numero_documento': '98765432',
        'fecha_nacimiento': '1985-05-20',
        'direccion': 'Av. Siempre Viva 742',
        'localidad': 'Montevideo',
        'telefonos': '24009999',
        'movil': '098765432',
        'mail': 'ana@mail.com',
        'observaciones': 'Cliente preferente',
        'creado_por_id': 2,
        'modificado_por_id': 2
    }
    with pytest.raises(Exception) as excinfo2:
        handler.crear_cliente(datos_validos)
    assert "Simulated POST error" in str(excinfo2.value)

    def __init__(self):
        self.last_post = None
        self.last_put = None
        self.last_delete = None
        self.last_get = None
        self.last_payload = None
        self.should_raise = False

    def post(self, url, payload):
        self.last_post = (url, payload)
        self.last_payload = payload
        if self.should_raise:
            raise Exception("Simulated POST error")
        return {"id": "uuid-123", **payload}

    def put(self, url, payload):
        self.last_put = (url, payload)
        self.last_payload = payload
        if self.should_raise:
            raise Exception("Simulated PUT error")
        return {"id": "uuid-123", **payload}

    def delete(self, url):
        self.last_delete = url
        if self.should_raise:
            raise Exception("Simulated DELETE error")
        return True

    def get(self, url):
        self.last_get = url
        if self.should_raise:
            raise Exception("Simulated GET error")
        return {"id": "uuid-123", "nombres": "Juan", "apellidos": "Pérez"}

    def get_sync(self, url):
        return [{"id": "uuid-123", "numero_cliente": 1, "nombres": "Juan", "apellidos": "Pérez"}]


def test_crear_cliente_payload_valido():
    api = DummyAPI()
    handler = ClienteNetworkHandler(api)
    # Caso 1: Todos los campos obligatorios y opcionales
    datos = {
        'nombres': 'Juan',
        'apellidos': 'Pérez',
        'tipo_documento_id': 1,
        'numero_documento': '12345678',
        'fecha_nacimiento': '1990-01-01',
        'direccion': 'Calle Falsa 123',
        'localidad': 'Montevideo',
        'telefonos': '24001234',
        'movil': '099123456',
        'mail': 'juan@mail.com',
        'observaciones': 'algo opcional',
        'creado_por_id': 1,
        'modificado_por_id': 1
    }
    payload = handler._crear_payload_cliente(datos)
    for campo in [
        'nombres','apellidos','tipo_documento_id','numero_documento','fecha_nacimiento',
        'direccion','localidad','telefonos','movil','mail','creado_por_id','modificado_por_id'
    ]:
        assert campo in payload
    # 'observaciones' opcional
    assert payload['observaciones'] == 'algo opcional'

    # Caso 2: 'observaciones' vacío
    datos2 = datos.copy()
    datos2['observaciones'] = ''
    payload2 = handler._crear_payload_cliente(datos2)
    assert 'observaciones' in payload2  # Puede estar vacío

    # Caso 3: 'observaciones' ausente
    datos3 = datos.copy()
    datos3.pop('observaciones')
    payload3 = handler._crear_payload_cliente(datos3)
    assert 'observaciones' not in payload3 or payload3['observaciones'] == ''

    datos = {
        'nombres': 'Juan',
        'apellidos': 'Pérez',
        'tipo_documento_id': 1,
        'numero_documento': '12345678',
        'fecha_nacimiento': '1990-01-01',
        'direccion': 'Calle Falsa 123',
        'localidad': 'Montevideo',
        'telefonos': '24001234',
        'movil': '099123456',
        'mail': 'juan@mail.com',
        'creado_por_id': 1,
        'modificado_por_id': 1
    }
    payload = handler._crear_payload_cliente(datos)
    assert payload['nombres'] == 'Juan'
    assert payload['apellidos'] == 'Pérez'
    assert payload['mail'] == 'juan@mail.com'
    assert payload['telefonos'] == '24001234'
    assert payload['movil'] == '099123456'
    assert payload['localidad'] == 'Montevideo'


def test_crear_cliente_campos_obligatorios_faltantes():
    api = DummyAPI()
    handler = ClienteNetworkHandler(api)
    datos = {
        'nombres': '',
        'apellidos': '',
        'tipo_documento_id': None,
        'numero_documento': '',
        'fecha_nacimiento': '',
        'direccion': '',
        'localidad': '',
        'telefonos': '',
        'movil': '',
        'mail': '',
        'observaciones': '',
        'creado_por_id': None,
        'modificado_por_id': None
    }
    with pytest.raises(ValueError) as excinfo:
        handler._validar_campos_obligatorios_cliente(datos)
    assert "Faltan campos obligatorios" in str(excinfo.value)


def test_crear_cliente_email_invalido():
    api = DummyAPI()
    handler = ClienteNetworkHandler(api)
    datos = {
        'nombres': 'Juan',
        'apellidos': 'Pérez',
        'tipo_documento_id': 1,
        'numero_documento': '12345678',
        'fecha_nacimiento': '1990-01-01',
        'direccion': 'Calle Falsa 123',
        'localidad': 'Montevideo',
        'telefonos': '24001234',
        'movil': '099123456',
        'mail': 'no-es-email',
        'observaciones': '',
        'creado_por_id': 1,
        'modificado_por_id': 1
    }
    with pytest.raises(ValueError) as excinfo:
        handler._crear_payload_cliente(datos)
    assert "email válido" in str(excinfo.value)


def test_crear_cliente_fecha_nacimiento_invalida():
    api = DummyAPI()
    handler = ClienteNetworkHandler(api)
    datos = {
        'nombres': 'Juan',
        'apellidos': 'Pérez',
        'tipo_documento_id': 1,
        'numero_documento': '12345678',
        'fecha_nacimiento': '01-01-1990',
        'direccion': 'Calle Falsa 123',
        'localidad': 'Montevideo',
        'telefonos': '24001234',
        'movil': '099123456',
        'mail': 'juan@mail.com',
        'observaciones': '',
        'creado_por_id': 1,
        'modificado_por_id': 1
    }
    with pytest.raises(ValueError) as excinfo:
        handler._crear_payload_cliente(datos)
    assert "formato YYYY-MM-DD" in str(excinfo.value)


def test_eliminar_cliente_uuid_vs_numerico():
    api = DummyAPI()
    handler = ClienteNetworkHandler(api)
    # Eliminar con UUID válido
    handler.eliminar_cliente('123e4567-e89b-12d3-a456-426614174000')
    assert api.last_delete == 'api/v1/clientes/123e4567-e89b-12d3-a456-426614174000/'
    # Simular error de entero y fallback a numérico
    class DummyAPIIntError(DummyAPI):
        def delete(self, url):
            # Si es el UUID válido, simula error de parseo de entero
            if url == 'api/v1/clientes/123e4567-e89b-12d3-a456-426614174000/':
                raise Exception('integer parse error')
            # Si es el ID numérico, permite la eliminación
            if url == 'api/v1/clientes/1/':
                self.last_delete = url
                return True
            # Para cualquier otro caso, comportamiento por defecto
            self.last_delete = url
            return True
        def get_sync(self, url):
            # Devuelve siempre el cliente con el UUID válido y numero_cliente=1
            return [{
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "numero_cliente": 1,
                "nombres": "Juan",
                "apellidos": "Pérez"
            }]

    api2 = DummyAPIIntError()
    handler2 = ClienteNetworkHandler(api2)
    handler2.eliminar_cliente('123e4567-e89b-12d3-a456-426614174000')
    assert api2.last_delete == 'api/v1/clientes/1/'
