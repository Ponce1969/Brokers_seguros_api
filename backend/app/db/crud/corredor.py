from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.corredor import Corredor
from app.schemas.corredor import CorredorCreate, CorredorUpdate

from .base import CRUDBase


class CRUDCorredor(CRUDBase[Corredor, CorredorCreate, CorredorUpdate]):
    async def get_by_mail(self, db: AsyncSession, *, mail: str) -> Optional[Corredor]:
        result = await db.execute(select(Corredor).where(Corredor.mail == mail))
        return result.scalars().first()

    async def get_by_documento(
        self, db: AsyncSession, *, documento: str
    ) -> Optional[Corredor]:
        result = await db.execute(
            select(Corredor).where(Corredor.documento == documento)
        )
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: CorredorCreate) -> Corredor:
        db_obj = Corredor(
            numero=obj_in.numero,
            nombres=obj_in.nombres,
            apellidos=obj_in.apellidos,
            documento=obj_in.documento,
            direccion=obj_in.direccion,
            localidad=obj_in.localidad,
            telefonos=obj_in.telefonos,
            movil=obj_in.movil,
            mail=obj_in.mail,
            observaciones=obj_in.observaciones,
            matricula=obj_in.matricula,
            especializacion=obj_in.especializacion,
            fecha_alta=obj_in.fecha_alta,
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
