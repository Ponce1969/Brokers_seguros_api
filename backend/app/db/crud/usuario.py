from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
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
            hashed_password=get_password_hash(
                obj_in.password
            ),  # Contraseña hasheada con bcrypt
            nombre=obj_in.nombre,
            apellido=obj_in.apellido,
            role=obj_in.role,
            is_active=True,
            is_superuser=False,
            corredor_numero=obj_in.corredor_numero,
            comision_porcentaje=obj_in.comision_porcentaje,
            telefono=obj_in.telefono,
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
            password = update_data.pop("password")
            update_data["hashed_password"] = get_password_hash(
                password
            )  # Contraseña hasheada con bcrypt

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

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[Usuario]:
        """
        Autentica un usuario usando su email/username y contraseña.

        Args:
            db: Sesión de base de datos
            email: Email o username del usuario
            password: Contraseña en texto plano

        Returns:
            Usuario si la autenticación es exitosa, None en caso contrario
        """
        # Intentar autenticar por email
        usuario = await self.get_by_email(db, email=email)
        if not usuario:
            # Si no se encuentra por email, intentar por username
            usuario = await self.get_by_username(db, username=email)
            if not usuario:
                return None

        if not verify_password(password, usuario.hashed_password):
            return None
        return usuario


usuario_crud = CRUDUsuario()
