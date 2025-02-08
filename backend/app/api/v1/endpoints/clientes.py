from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.cliente import cliente_crud
from app.db.database import get_db
from app.schemas.cliente import Cliente, ClienteCreate, ClienteUpdate

router = APIRouter()


@router.get("/", response_model=List[Cliente])
async def get_clientes(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Recuperar clientes.
    """
    clientes = await cliente_crud.get_multi(db, skip=skip, limit=limit)
    return clientes


@router.post("/", response_model=Cliente)
async def create_cliente(
    *, db: AsyncSession = Depends(get_db), cliente_in: ClienteCreate
) -> Any:
    """
    Crear nuevo cliente.
    """
    cliente = await cliente_crud.create(db, obj_in=cliente_in)
    return cliente


@router.get("/{cliente_id}", response_model=Cliente)
async def get_cliente(cliente_id: int, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Obtener cliente por ID.
    """
    cliente = await cliente_crud.get(db, id=cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.put("/{cliente_id}", response_model=Cliente)
async def update_cliente(
    *, db: AsyncSession = Depends(get_db), cliente_id: int, cliente_in: ClienteUpdate
) -> Any:
    """
    Actualizar cliente.
    """
    cliente = await cliente_crud.get(db, id=cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente = await cliente_crud.update(db, db_obj=cliente, obj_in=cliente_in)
    return cliente


@router.delete("/{cliente_id}", response_model=Cliente)
async def delete_cliente(*, db: AsyncSession = Depends(get_db), cliente_id: int) -> Any:
    """
    Eliminar cliente.
    """
    cliente = await cliente_crud.get(db, id=cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente = await cliente_crud.delete(db, id=cliente_id)
    return cliente
