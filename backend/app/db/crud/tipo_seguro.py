from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.tipo_seguro import TipoSeguro
from app.schemas.tipo_seguro import TipoSeguroCreate, TipoSeguroUpdate

from .base import CRUDBase


class CRUDTipoSeguro(CRUDBase[TipoSeguro, TipoSeguroCreate, TipoSeguroUpdate]):
    async def get_by_codigo(
        self, db: AsyncSession, *, codigo: str
    ) -> Optional[TipoSeguro]:
        result = await db.execute(select(TipoSeguro).where(TipoSeguro.codigo == codigo))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: TipoSeguroCreate) -> TipoSeguro:
        db_obj = TipoSeguro(
            codigo=obj_in.codigo,
            nombre=obj_in.nombre,
            descripcion=obj_in.descripcion,
            es_default=obj_in.es_default,
            esta_activo=obj_in.esta_activo,
            categoria=obj_in.categoria,
            cobertura=obj_in.cobertura,
            vigencia_default=obj_in.vigencia_default,
            aseguradora_id=obj_in.aseguradora_id,
        )
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
