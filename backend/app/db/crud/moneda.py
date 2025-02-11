from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.moneda import Moneda
from app.schemas.moneda import MonedaCreate, MonedaUpdate

from .base import CRUDBase


class CRUDMoneda(CRUDBase[Moneda, MonedaCreate, MonedaUpdate]):
    async def get_by_codigo(self, db: AsyncSession, *, codigo: str) -> Optional[Moneda]:
        result = await db.execute(select(Moneda).where(Moneda.codigo == codigo))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: MonedaCreate) -> Moneda:
        db_obj = Moneda(
            codigo=obj_in.codigo,
            nombre=obj_in.nombre,
            simbolo=obj_in.simbolo,
            descripcion=obj_in.descripcion,
            es_default=obj_in.es_default,
            esta_activa=obj_in.esta_activa
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Moneda,
        obj_in: Union[MonedaUpdate, Dict[str, Any]],
    ) -> Moneda:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return await super().update(db, db_obj=db_obj, obj_in=update_data)


moneda_crud = CRUDMoneda(Moneda)
