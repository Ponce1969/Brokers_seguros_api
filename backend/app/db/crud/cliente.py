from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate

from .base import CRUDBase


from app.db.models.cliente_corredor import ClienteCorredor

class CRUDCliente(CRUDBase[Cliente, ClienteCreate, ClienteUpdate]):
    async def get_by_mail(self, db: AsyncSession, *, mail: str) -> Optional[Cliente]:
        result = await db.execute(select(Cliente).where(Cliente.mail == mail))
        return result.scalars().first()

    async def get_by_numero_documento(
        self, db: AsyncSession, *, numero_documento: str
    ) -> Optional[Cliente]:
        result = await db.execute(
            select(Cliente).where(Cliente.numero_documento == numero_documento)
        )
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: ClienteCreate) -> Cliente:
        db_obj = Cliente(
            nombres=obj_in.nombres,
            apellidos=obj_in.apellidos,
            tipo_documento_id=obj_in.tipo_documento_id,
            numero_documento=obj_in.numero_documento,
            fecha_nacimiento=obj_in.fecha_nacimiento,
            direccion=obj_in.direccion,
            localidad=obj_in.localidad,
            telefonos=obj_in.telefonos,
            movil=obj_in.movil,
            mail=obj_in.mail,
            observaciones=obj_in.observaciones,
            creado_por_id=obj_in.creado_por_id,
            modificado_por_id=obj_in.modificado_por_id,
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


    async def delete(self, db: AsyncSession, *, id) -> Cliente:
        # Elimina relaciones dependientes en clientes_corredores
        await db.execute(
            ClienteCorredor.__table__.delete().where(ClienteCorredor.cliente_id == id)
        )
        await db.commit()
        # Ahora elimina el cliente
        return await super().delete(db, id=id)

cliente_crud = CRUDCliente(Cliente)
