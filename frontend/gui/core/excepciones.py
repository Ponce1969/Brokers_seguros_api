"""
Excepciones personalizadas para la aplicación
"""

class ErrorBase(Exception):
    """Excepción base para la aplicación"""
    pass

class ErrorAPI(ErrorBase):
    """Error al comunicarse con la API"""
    pass

class ErrorValidacion(ErrorBase):
    """Error de validación de datos"""
    pass
