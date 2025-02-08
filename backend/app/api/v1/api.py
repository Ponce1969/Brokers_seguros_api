from fastapi import APIRouter

from app.api.v1.endpoints import (
    aseguradoras,
    cliente_corredor,
    clientes,
    corredores,
    monedas,
    movimientos_vigencia,
    tipos_documento,
    tipos_seguro,
    usuarios,
)

api_router = APIRouter()

api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
api_router.include_router(corredores.router, prefix="/corredores", tags=["corredores"])
api_router.include_router(
    aseguradoras.router, prefix="/aseguradoras", tags=["aseguradoras"]
)
api_router.include_router(
    tipos_seguro.router, prefix="/tipos-seguro", tags=["tipos-seguro"]
)
api_router.include_router(
    tipos_documento.router, prefix="/tipos-documento", tags=["tipos-documento"]
)
api_router.include_router(monedas.router, prefix="/monedas", tags=["monedas"])
api_router.include_router(
    movimientos_vigencia.router,
    prefix="/movimientos-vigencia",
    tags=["movimientos-vigencia"],
)
api_router.include_router(
    cliente_corredor.router, prefix="/cliente-corredor", tags=["cliente-corredor"]
)
