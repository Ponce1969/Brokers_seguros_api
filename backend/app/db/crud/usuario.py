from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


class CRUDUsuario:
    async def get(self, db: AsyncSession, id: int) -> Optional[Usuario]:
        result = await db.execute(select(Usuario).filter(Usuario.id == id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[Usuario]:
        result = await db.execute(select(Usuario).filter(Usuario.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(
        self, db: AsyncSession, username: str
    ) -> Optional[Usuario]:
        result = await db.execute(select(Usuario).filter(Usuario.username == username))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Usuario]:
        result = await db.execute(select(Usuario).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: UsuarioCreate) -> Usuario:
        db_obj = Usuario(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=obj_in.password,  # Aquí deberías hashear la contraseña
            nombre=obj_in.nombre,
            apellido=obj_in.apellido,
            role=obj_in.role,
            is_active=True,
            is_superuser=False,
            comision_porcentaje=obj_in.comision_porcentaje,
            telefono=obj_in.telefono,
            corredor_numero=obj_in.corredor_numero,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: Usuario, obj_in: UsuarioUpdate
    ) -> Usuario:
        update_data = obj_in.dict(exclude_unset=True)

        # Si hay una contraseña en los datos de actualización, deberíamos hashearla
        if "password" in update_data:
            update_data["hashed_password"] = update_data.pop(
                "password"
            )  # Aquí deberías hashear la contraseña

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: int) -> Optional[Usuario]:
        result = await db.execute(select(Usuario).filter(Usuario.id == id))
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj


usuario_crud = CRUDUsuario()
