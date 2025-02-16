from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.tipo_documento import TipoDocumento
from app.schemas.tipo_documento import TipoDocumentoCreate, TipoDocumentoUpdate

from .base import CRUDBase


class CRUDTipoDocumento(
    CRUDBase[TipoDocumento, TipoDocumentoCreate, TipoDocumentoUpdate]
):
    async def get_by_nombre(
        self, db: AsyncSession, *, nombre: str
    ) -> Optional[TipoDocumento]:
        result = await db.execute(
            select(TipoDocumento).where(TipoDocumento.nombre == nombre)
        )
        return result.scalars().first()

    async def create(
        self, db: AsyncSession, *, obj_in: TipoDocumentoCreate
    ) -> TipoDocumento:
        db_obj = TipoDocumento(
            codigo=obj_in.codigo,
            nombre=obj_in.nombre,
            descripcion=obj_in.descripcion,
            es_default=obj_in.es_default,
            esta_activo=obj_in.esta_activo,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: TipoDocumento,
        obj_in: Union[TipoDocumentoUpdate, Dict[str, Any]],
    ) -> TipoDocumento:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return await super().update(db, db_obj=db_obj, obj_in=update_data)


tipo_documento_crud = CRUDTipoDocumento(TipoDocumento)
