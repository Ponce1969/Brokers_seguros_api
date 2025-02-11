from typing import Any, Dict, List, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.cliente_corredor import ClienteCorredor
from app.schemas.cliente_corredor import ClienteCorredorCreate, ClienteCorredorUpdate

from .base import CRUDBase


class CRUDClienteCorredor(
    CRUDBase[ClienteCorredor, ClienteCorredorCreate, ClienteCorredorUpdate]
):
    async def get_by_cliente(
        self, db: AsyncSession, *, cliente_id: int
    ) -> List[ClienteCorredor]:
        result = await db.execute(
            select(ClienteCorredor).where(ClienteCorredor.cliente_id == cliente_id)
        )
        return result.scalars().all()

    async def get_by_corredor(
        self, db: AsyncSession, *, corredor_numero: int
    ) -> List[ClienteCorredor]:
        result = await db.execute(
            select(ClienteCorredor).where(ClienteCorredor.corredor_numero == corredor_numero)
        )
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: ClienteCorredorCreate
    ) -> ClienteCorredor:
        db_obj = ClienteCorredor(
            cliente_id=obj_in.cliente_id,
            corredor_numero=obj_in.corredor_numero,
            fecha_asignacion=obj_in.fecha_asignacion
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ClienteCorredor,
        obj_in: Union[ClienteCorredorUpdate, Dict[str, Any]],
    ) -> ClienteCorredor:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return await super().update(db, db_obj=db_obj, obj_in=update_data)


cliente_corredor_crud = CRUDClienteCorredor(ClienteCorredor)
