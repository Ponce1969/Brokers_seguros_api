from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.tipo_seguro import TipoSeguro
from app.schemas.tipo_seguro import TipoSeguroCreate, TipoSeguroUpdate

from .base import CRUDBase


class CRUDTipoSeguro(CRUDBase[TipoSeguro, TipoSeguroCreate, TipoSeguroUpdate]):
    async def get_by_nombre(
        self, db: AsyncSession, *, nombre: str
    ) -> Optional[TipoSeguro]:
        result = await db.execute(select(TipoSeguro).where(TipoSeguro.nombre == nombre))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: TipoSeguroCreate) -> TipoSeguro:
        db_obj = TipoSeguro(nombre=obj_in.nombre, descripcion=obj_in.descripcion)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: TipoSeguro,
        obj_in: Union[TipoSeguroUpdate, Dict[str, Any]],
    ) -> TipoSeguro:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return await super().update(db, db_obj=db_obj, obj_in=update_data)


tipo_seguro_crud = CRUDTipoSeguro(TipoSeguro)
