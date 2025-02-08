from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.corredor import corredor_crud
from app.db.database import get_db
from app.schemas.corredor import Corredor, CorredorCreate, CorredorUpdate

router = APIRouter()


@router.get("/", response_model=List[Corredor])
async def get_corredores(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Recuperar corredores.
    """
    corredores = await corredor_crud.get_multi(db, skip=skip, limit=limit)
    return corredores


@router.post("/", response_model=Corredor)
async def create_corredor(
    *, db: AsyncSession = Depends(get_db), corredor_in: CorredorCreate
) -> Any:
    """
    Crear nuevo corredor.
    """
    corredor = await corredor_crud.create(db, obj_in=corredor_in)
    return corredor


@router.get("/{corredor_id}", response_model=Corredor)
async def get_corredor(corredor_id: int, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Obtener corredor por ID.
    """
    corredor = await corredor_crud.get(db, id=corredor_id)
    if not corredor:
        raise HTTPException(status_code=404, detail="Corredor no encontrado")
    return corredor


@router.put("/{corredor_id}", response_model=Corredor)
async def update_corredor(
    *, db: AsyncSession = Depends(get_db), corredor_id: int, corredor_in: CorredorUpdate
) -> Any:
    """
    Actualizar corredor.
    """
    corredor = await corredor_crud.get(db, id=corredor_id)
    if not corredor:
        raise HTTPException(status_code=404, detail="Corredor no encontrado")
    corredor = await corredor_crud.update(db, db_obj=corredor, obj_in=corredor_in)
    return corredor


@router.delete("/{corredor_id}", response_model=Corredor)
async def delete_corredor(
    *, db: AsyncSession = Depends(get_db), corredor_id: int
) -> Any:
    """
    Eliminar corredor.
    """
    corredor = await corredor_crud.get(db, id=corredor_id)
    if not corredor:
        raise HTTPException(status_code=404, detail="Corredor no encontrado")
    corredor = await corredor_crud.delete(db, id=corredor_id)
    return corredor
