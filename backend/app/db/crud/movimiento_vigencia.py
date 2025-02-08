from typing import Any, Dict, List, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.movimiento_vigencia import MovimientoVigencia
from app.schemas.movimiento_vigencia import (
    MovimientoVigenciaCreate,
    MovimientoVigenciaUpdate,
)

from .base import CRUDBase


class CRUDMovimientoVigencia(
    CRUDBase[MovimientoVigencia, MovimientoVigenciaCreate, MovimientoVigenciaUpdate]
):
    async def get_by_cliente(
        self, db: AsyncSession, *, cliente_id: int
    ) -> List[MovimientoVigencia]:
        result = await db.execute(
            select(MovimientoVigencia).where(
                MovimientoVigencia.cliente_id == cliente_id
            )
        )
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: MovimientoVigenciaCreate
    ) -> MovimientoVigencia:
        db_obj = MovimientoVigencia(
            fecha_inicio=obj_in.fecha_inicio,
            fecha_termino=obj_in.fecha_termino,
            prima=obj_in.prima,
            cliente_id=obj_in.cliente_id,
            aseguradora_id=obj_in.aseguradora_id,
            tipo_seguro_id=obj_in.tipo_seguro_id,
            moneda_id=obj_in.moneda_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: MovimientoVigencia,
        obj_in: Union[MovimientoVigenciaUpdate, Dict[str, Any]],
    ) -> MovimientoVigencia:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return await super().update(db, db_obj=db_obj, obj_in=update_data)


movimiento_vigencia_crud = CRUDMovimientoVigencia(MovimientoVigencia)
