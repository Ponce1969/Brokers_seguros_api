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


from app.db.crud.usuario import usuario_crud
from app.db.crud.cliente_corredor import cliente_corredor_crud
from app.schemas.cliente_corredor import ClienteCorredorCreate

@router.post("/", response_model=Cliente)
async def create_cliente(
    *, db: AsyncSession = Depends(get_db), cliente_in: ClienteCreate
) -> Any:
    """
    Crear nuevo cliente.
    """
    # Validar unicidad de mail y numero_documento
    if await cliente_crud.get_by_mail(db, mail=cliente_in.mail):
        raise HTTPException(status_code=409, detail="El email ya está registrado")
    if await cliente_crud.get_by_numero_documento(db, numero_documento=cliente_in.numero_documento):
        raise HTTPException(status_code=409, detail="El número de documento ya está registrado")
    # Crear el cliente
    cliente = await cliente_crud.create(db, obj_in=cliente_in)
    # Lógica robusta: asociar automáticamente al corredor si existe
    from datetime import datetime, timezone
    usuario = await usuario_crud.get(db, id=cliente_in.creado_por_id)
    if usuario and usuario.corredor_numero:
        await cliente_corredor_crud.create(
            db,
            obj_in=ClienteCorredorCreate(
                cliente_id=cliente.id,
                corredor_numero=usuario.corredor_numero,
                fecha_asignacion=datetime.now(timezone.utc)
            )
        )
    # Refrescar el cliente para forzar el recálculo de corredores_count
    await db.refresh(cliente)
    return cliente


from uuid import UUID

@router.get("/{cliente_id}", response_model=Cliente)
async def get_cliente(cliente_id: UUID, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Obtener cliente por ID.
    """
    cliente = await cliente_crud.get(db, id=cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.put("/{cliente_id}", response_model=Cliente)
async def update_cliente(
    *, db: AsyncSession = Depends(get_db), cliente_id: UUID, cliente_in: ClienteUpdate
) -> Any:
    """
    Actualizar cliente.
    """
    cliente = await cliente_crud.get(db, id=cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente = await cliente_crud.update(db, db_obj=cliente, obj_in=cliente_in)
    return cliente


from uuid import UUID

@router.delete("/{cliente_id}", response_model=Cliente)
async def delete_cliente(*, db: AsyncSession = Depends(get_db), cliente_id: UUID) -> Any:
    """
    Eliminar cliente.
    """
    cliente = await cliente_crud.get(db, id=cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente = await cliente_crud.delete(db, id=cliente_id)
    return cliente
