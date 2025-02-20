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

class ErrorAutenticacion(ErrorBase):
    """Error de autenticación"""
    pass

class ErrorAutorizacion(ErrorBase):
    """Error de autorización"""
    pass

class ErrorDatos(ErrorBase):
    """Error en el manejo de datos"""
    pass

class ErrorConfiguracion(ErrorBase):
    """Error en la configuración"""
    pass
