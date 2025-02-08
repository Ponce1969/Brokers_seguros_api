from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.corredor import Corredor
from app.schemas.corredor import CorredorCreate, CorredorUpdate

from .base import CRUDBase


class CRUDCorredor(CRUDBase[Corredor, CorredorCreate, CorredorUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[Corredor]:
        result = await db.execute(select(Corredor).where(Corredor.email == email))
        return result.scalars().first()

    async def get_by_rut(self, db: AsyncSession, *, rut: str) -> Optional[Corredor]:
        result = await db.execute(select(Corredor).where(Corredor.rut == rut))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: CorredorCreate) -> Corredor:
        db_obj = Corredor(
            nombre=obj_in.nombre,
            apellido=obj_in.apellido,
            rut=obj_in.rut,
            email=obj_in.email,
            telefono=obj_in.telefono,
            direccion=obj_in.direccion,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Corredor,
        obj_in: Union[CorredorUpdate, Dict[str, Any]],
    ) -> Corredor:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return await super().update(db, db_obj=db_obj, obj_in=update_data)


corredor_crud = CRUDCorredor(Corredor)
