from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.cliente_corredor import cliente_corredor_crud
from app.db.database import get_db
from app.schemas.cliente_corredor import (
    ClienteCorredor,
    ClienteCorredorCreate,
    ClienteCorredorUpdate,
)

router = APIRouter()

@router.get("/", response_model=List[ClienteCorredor])
async def get_cliente_corredores(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Recuperar relaciones cliente-corredor.
    """
    relaciones = await cliente_corredor_crud.get_multi(db, skip=skip, limit=limit)
    return relaciones

@router.post("/", response_model=ClienteCorredor)
async def create_cliente_corredor(
    *,
    db: AsyncSession = Depends(get_db),
    cliente_corredor_in: ClienteCorredorCreate
) -> Any:
    """
    Crear nueva relación cliente-corredor.
    """
    relacion = await cliente_corredor_crud.create(db, obj_in=cliente_corredor_in)
    return relacion

@router.get("/{relacion_id}", response_model=ClienteCorredor)
async def get_cliente_corredor(
    relacion_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Obtener relación cliente-corredor por ID.
    """
    relacion = await cliente_corredor_crud.get(db, id=relacion_id)
    if not relacion:
        raise HTTPException(
            status_code=404,
            detail="Relación cliente-corredor no encontrada"
        )
    return relacion

@router.put("/{relacion_id}", response_model=ClienteCorredor)
async def update_cliente_corredor(
    *,
    db: AsyncSession = Depends(get_db),
    relacion_id: int,
    cliente_corredor_in: ClienteCorredorUpdate
) -> Any:
    """
    Actualizar relación cliente-corredor.
    """
    relacion = await cliente_corredor_crud.get(db, id=relacion_id)
    if not relacion:
        raise HTTPException(
            status_code=404,
            detail="Relación cliente-corredor no encontrada"
        )
    relacion = await cliente_corredor_crud.update(db, db_obj=relacion, obj_in=cliente_corredor_in)
    return relacion

@router.delete("/{relacion_id}", response_model=ClienteCorredor)
async def delete_cliente_corredor(
    *,
    db: AsyncSession = Depends(get_db),
    relacion_id: int
) -> Any:
    """
    Eliminar relación cliente-corredor.
    """
    relacion = await cliente_corredor_crud.get(db, id=relacion_id)
    if not relacion:
        raise HTTPException(
            status_code=404,
            detail="Relación cliente-corredor no encontrada"
        )
    relacion = await cliente_corredor_crud.delete(db, id=relacion_id)
    return relacion
