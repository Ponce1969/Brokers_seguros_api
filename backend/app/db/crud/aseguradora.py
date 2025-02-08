from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.aseguradora import Aseguradora
from app.schemas.aseguradora import AseguradoraCreate, AseguradoraUpdate

from .base import CRUDBase


class CRUDAseguradora(CRUDBase[Aseguradora, AseguradoraCreate, AseguradoraUpdate]):
    async def get_by_nombre(
        self, db: AsyncSession, *, nombre: str
    ) -> Optional[Aseguradora]:
        result = await db.execute(
            select(Aseguradora).where(Aseguradora.nombre == nombre)
        )
        return result.scalars().first()

    async def create(
        self, db: AsyncSession, *, obj_in: AseguradoraCreate
    ) -> Aseguradora:
        db_obj = Aseguradora(
            nombre=obj_in.nombre,
            direccion=obj_in.direccion,
            telefono=obj_in.telefono,
            email=obj_in.email,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Aseguradora,
        obj_in: Union[AseguradoraUpdate, Dict[str, Any]],
    ) -> Aseguradora:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return await super().update(db, db_obj=db_obj, obj_in=update_data)


aseguradora_crud = CRUDAseguradora(Aseguradora)
