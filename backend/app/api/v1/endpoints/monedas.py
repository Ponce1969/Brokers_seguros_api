from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.moneda import moneda_crud
from app.db.database import get_db
from app.schemas.moneda import Moneda, MonedaCreate, MonedaUpdate

router = APIRouter()


@router.get("/", response_model=List[Moneda])
async def get_monedas(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Recuperar monedas.
    """
    monedas = await moneda_crud.get_multi(db, skip=skip, limit=limit)
    return monedas


@router.post("/", response_model=Moneda)
async def create_moneda(
    *, db: AsyncSession = Depends(get_db), moneda_in: MonedaCreate
) -> Any:
    """
    Crear nueva moneda.
    """
    moneda = await moneda_crud.create(db, obj_in=moneda_in)
    return moneda


@router.get("/{moneda_id}", response_model=Moneda)
async def get_moneda(moneda_id: int, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Obtener moneda por ID.
    """
    moneda = await moneda_crud.get(db, id=moneda_id)
    if not moneda:
        raise HTTPException(status_code=404, detail="Moneda no encontrada")
    return moneda


@router.put("/{moneda_id}", response_model=Moneda)
async def update_moneda(
    *, db: AsyncSession = Depends(get_db), moneda_id: int, moneda_in: MonedaUpdate
) -> Any:
    """
    Actualizar moneda.
    """
    moneda = await moneda_crud.get(db, id=moneda_id)
    if not moneda:
        raise HTTPException(status_code=404, detail="Moneda no encontrada")
    moneda = await moneda_crud.update(db, db_obj=moneda, obj_in=moneda_in)
    return moneda


@router.delete("/{moneda_id}", response_model=Moneda)
async def delete_moneda(*, db: AsyncSession = Depends(get_db), moneda_id: int) -> Any:
    """
    Eliminar moneda.
    """
    moneda = await moneda_crud.get(db, id=moneda_id)
    if not moneda:
        raise HTTPException(status_code=404, detail="Moneda no encontrada")
    moneda = await moneda_crud.delete(db, id=moneda_id)
    return moneda
