from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.movimiento_vigencia import movimiento_vigencia_crud
from app.db.database import get_db
from app.schemas.movimiento_vigencia import (
    MovimientoVigencia,
    MovimientoVigenciaCreate,
    MovimientoVigenciaUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[MovimientoVigencia])
async def get_movimientos_vigencia(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Recuperar movimientos de vigencia.
    """
    movimientos = await movimiento_vigencia_crud.get_multi(db, skip=skip, limit=limit)
    return movimientos


@router.post("/", response_model=MovimientoVigencia)
async def create_movimiento_vigencia(
    *, db: AsyncSession = Depends(get_db), movimiento_in: MovimientoVigenciaCreate
) -> Any:
    """
    Crear nuevo movimiento de vigencia.
    """
    movimiento = await movimiento_vigencia_crud.create(db, obj_in=movimiento_in)
    return movimiento


@router.get("/{movimiento_id}", response_model=MovimientoVigencia)
async def get_movimiento_vigencia(
    movimiento_id: int, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Obtener movimiento de vigencia por ID.
    """
    movimiento = await movimiento_vigencia_crud.get(db, id=movimiento_id)
    if not movimiento:
        raise HTTPException(
            status_code=404, detail="Movimiento de vigencia no encontrado"
        )
    return movimiento


@router.put("/{movimiento_id}", response_model=MovimientoVigencia)
async def update_movimiento_vigencia(
    *,
    db: AsyncSession = Depends(get_db),
    movimiento_id: int,
    movimiento_in: MovimientoVigenciaUpdate,
) -> Any:
    """
    Actualizar movimiento de vigencia.
    """
    movimiento = await movimiento_vigencia_crud.get(db, id=movimiento_id)
    if not movimiento:
        raise HTTPException(
            status_code=404, detail="Movimiento de vigencia no encontrado"
        )
    movimiento = await movimiento_vigencia_crud.update(
        db, db_obj=movimiento, obj_in=movimiento_in
    )
    return movimiento


@router.delete("/{movimiento_id}", response_model=MovimientoVigencia)
async def delete_movimiento_vigencia(
    *, db: AsyncSession = Depends(get_db), movimiento_id: int
) -> Any:
    """
    Eliminar movimiento de vigencia.
    """
    movimiento = await movimiento_vigencia_crud.get(db, id=movimiento_id)
    if not movimiento:
        raise HTTPException(
            status_code=404, detail="Movimiento de vigencia no encontrado"
        )
    movimiento = await movimiento_vigencia_crud.delete(db, id=movimiento_id)
    return movimiento
