from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.tipo_seguro import tipo_seguro_crud
from app.db.database import get_db
from app.schemas.tipo_seguro import TipoSeguro, TipoSeguroCreate, TipoSeguroUpdate

router = APIRouter()


@router.get("/", response_model=List[TipoSeguro])
async def get_tipos_seguro(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Recuperar tipos de seguro.
    """
    tipos_seguro = await tipo_seguro_crud.get_multi(db, skip=skip, limit=limit)
    return tipos_seguro


@router.post("/", response_model=TipoSeguro)
async def create_tipo_seguro(
    *, db: AsyncSession = Depends(get_db), tipo_seguro_in: TipoSeguroCreate
) -> Any:
    """
    Crear nuevo tipo de seguro.
    """
    tipo_seguro = await tipo_seguro_crud.create(db, obj_in=tipo_seguro_in)
    return tipo_seguro


@router.get("/{tipo_seguro_id}", response_model=TipoSeguro)
async def get_tipo_seguro(
    tipo_seguro_id: int, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Obtener tipo de seguro por ID.
    """
    tipo_seguro = await tipo_seguro_crud.get(db, id=tipo_seguro_id)
    if not tipo_seguro:
        raise HTTPException(status_code=404, detail="Tipo de seguro no encontrado")
    return tipo_seguro


@router.put("/{tipo_seguro_id}", response_model=TipoSeguro)
async def update_tipo_seguro(
    *,
    db: AsyncSession = Depends(get_db),
    tipo_seguro_id: int,
    tipo_seguro_in: TipoSeguroUpdate,
) -> Any:
    """
    Actualizar tipo de seguro.
    """
    tipo_seguro = await tipo_seguro_crud.get(db, id=tipo_seguro_id)
    if not tipo_seguro:
        raise HTTPException(status_code=404, detail="Tipo de seguro no encontrado")
    tipo_seguro = await tipo_seguro_crud.update(
        db, db_obj=tipo_seguro, obj_in=tipo_seguro_in
    )
    return tipo_seguro


@router.delete("/{tipo_seguro_id}", response_model=TipoSeguro)
async def delete_tipo_seguro(
    *, db: AsyncSession = Depends(get_db), tipo_seguro_id: int
) -> Any:
    """
    Eliminar tipo de seguro.
    """
    tipo_seguro = await tipo_seguro_crud.get(db, id=tipo_seguro_id)
    if not tipo_seguro:
        raise HTTPException(status_code=404, detail="Tipo de seguro no encontrado")
    tipo_seguro = await tipo_seguro_crud.delete(db, id=tipo_seguro_id)
    return tipo_seguro
