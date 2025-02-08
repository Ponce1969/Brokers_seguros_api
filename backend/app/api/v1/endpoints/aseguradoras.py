from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.aseguradora import aseguradora_crud
from app.db.database import get_db
from app.schemas.aseguradora import Aseguradora, AseguradoraCreate, AseguradoraUpdate

router = APIRouter()


@router.get("/", response_model=List[Aseguradora])
async def get_aseguradoras(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Recuperar aseguradoras.
    """
    aseguradoras = await aseguradora_crud.get_multi(db, skip=skip, limit=limit)
    return aseguradoras


@router.post("/", response_model=Aseguradora)
async def create_aseguradora(
    *, db: AsyncSession = Depends(get_db), aseguradora_in: AseguradoraCreate
) -> Any:
    """
    Crear nueva aseguradora.
    """
    aseguradora = await aseguradora_crud.create(db, obj_in=aseguradora_in)
    return aseguradora


@router.get("/{aseguradora_id}", response_model=Aseguradora)
async def get_aseguradora(
    aseguradora_id: int, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Obtener aseguradora por ID.
    """
    aseguradora = await aseguradora_crud.get(db, id=aseguradora_id)
    if not aseguradora:
        raise HTTPException(status_code=404, detail="Aseguradora no encontrada")
    return aseguradora


@router.put("/{aseguradora_id}", response_model=Aseguradora)
async def update_aseguradora(
    *,
    db: AsyncSession = Depends(get_db),
    aseguradora_id: int,
    aseguradora_in: AseguradoraUpdate,
) -> Any:
    """
    Actualizar aseguradora.
    """
    aseguradora = await aseguradora_crud.get(db, id=aseguradora_id)
    if not aseguradora:
        raise HTTPException(status_code=404, detail="Aseguradora no encontrada")
    aseguradora = await aseguradora_crud.update(
        db, db_obj=aseguradora, obj_in=aseguradora_in
    )
    return aseguradora


@router.delete("/{aseguradora_id}", response_model=Aseguradora)
async def delete_aseguradora(
    *, db: AsyncSession = Depends(get_db), aseguradora_id: int
) -> Any:
    """
    Eliminar aseguradora.
    """
    aseguradora = await aseguradora_crud.get(db, id=aseguradora_id)
    if not aseguradora:
        raise HTTPException(status_code=404, detail="Aseguradora no encontrada")
    aseguradora = await aseguradora_crud.delete(db, id=aseguradora_id)
    return aseguradora
