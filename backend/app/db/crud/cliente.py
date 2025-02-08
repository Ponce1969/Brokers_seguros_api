from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate

from .base import CRUDBase


class CRUDCliente(CRUDBase[Cliente, ClienteCreate, ClienteUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[Cliente]:
        result = await db.execute(select(Cliente).where(Cliente.email == email))
        return result.scalars().first()

    async def get_by_rut(self, db: AsyncSession, *, rut: str) -> Optional[Cliente]:
        result = await db.execute(select(Cliente).where(Cliente.rut == rut))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: ClienteCreate) -> Cliente:
        db_obj = Cliente(
            nombre=obj_in.nombre,
            apellido=obj_in.apellido,
            rut=obj_in.rut,
            email=obj_in.email,
            telefono=obj_in.telefono,
            direccion=obj_in.direccion,
            tipo_documento_id=obj_in.tipo_documento_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Cliente,
        obj_in: Union[ClienteUpdate, Dict[str, Any]],
    ) -> Cliente:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return await super().update(db, db_obj=db_obj, obj_in=update_data)


cliente_crud = CRUDCliente(Cliente)
