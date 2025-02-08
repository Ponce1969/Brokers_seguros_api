from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.tipo_documento import tipo_documento_crud
from app.db.database import get_db
from app.schemas.tipo_documento import (
    TipoDocumento,
    TipoDocumentoCreate,
    TipoDocumentoUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[TipoDocumento])
async def get_tipos_documento(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Recuperar tipos de documento.
    """
    tipos_documento = await tipo_documento_crud.get_multi(db, skip=skip, limit=limit)
    return tipos_documento


@router.post("/", response_model=TipoDocumento)
async def create_tipo_documento(
    *, db: AsyncSession = Depends(get_db), tipo_documento_in: TipoDocumentoCreate
) -> Any:
    """
    Crear nuevo tipo de documento.
    """
    tipo_documento = await tipo_documento_crud.create(db, obj_in=tipo_documento_in)
    return tipo_documento


@router.get("/{tipo_documento_id}", response_model=TipoDocumento)
async def get_tipo_documento(
    tipo_documento_id: int, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Obtener tipo de documento por ID.
    """
    tipo_documento = await tipo_documento_crud.get(db, id=tipo_documento_id)
    if not tipo_documento:
        raise HTTPException(status_code=404, detail="Tipo de documento no encontrado")
    return tipo_documento


@router.put("/{tipo_documento_id}", response_model=TipoDocumento)
async def update_tipo_documento(
    *,
    db: AsyncSession = Depends(get_db),
    tipo_documento_id: int,
    tipo_documento_in: TipoDocumentoUpdate,
) -> Any:
    """
    Actualizar tipo de documento.
    """
    tipo_documento = await tipo_documento_crud.get(db, id=tipo_documento_id)
    if not tipo_documento:
        raise HTTPException(status_code=404, detail="Tipo de documento no encontrado")
    tipo_documento = await tipo_documento_crud.update(
        db, db_obj=tipo_documento, obj_in=tipo_documento_in
    )
    return tipo_documento


@router.delete("/{tipo_documento_id}", response_model=TipoDocumento)
async def delete_tipo_documento(
    *, db: AsyncSession = Depends(get_db), tipo_documento_id: int
) -> Any:
    """
    Eliminar tipo de documento.
    """
    tipo_documento = await tipo_documento_crud.get(db, id=tipo_documento_id)
    if not tipo_documento:
        raise HTTPException(status_code=404, detail="Tipo de documento no encontrado")
    tipo_documento = await tipo_documento_crud.delete(db, id=tipo_documento_id)
    return tipo_documento
