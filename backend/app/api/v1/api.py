from fastapi import APIRouter

from app.api.v1.endpoints import (
    usuarios,
    clientes,
    corredores,
    aseguradoras,
    polizas,
    tipos_seguro
)

api_router = APIRouter()

api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
api_router.include_router(corredores.router, prefix="/corredores", tags=["corredores"])
api_router.include_router(aseguradoras.router, prefix="/aseguradoras", tags=["aseguradoras"])
api_router.include_router(polizas.router, prefix="/polizas", tags=["polizas"])
api_router.include_router(tipos_seguro.router, prefix="/tipos-seguro", tags=["tipos-seguro"])
