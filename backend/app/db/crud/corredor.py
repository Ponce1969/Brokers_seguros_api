"""
CRUD para el modelo Corredor
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.models.corredor import Corredor
from app.db.models.usuario import Usuario
from app.schemas.corredor import CorredorCreate, CorredorUpdate
from .base import CRUDBase


class CRUDCorredor(CRUDBase[Corredor, CorredorCreate, CorredorUpdate]):
    def __init__(self, model: Type[Corredor]):
        super().__init__(model)

    def _format_response(self, corredor: Corredor) -> dict:
        """
        Formatea un corredor al formato de respuesta estándar.
        """
        return {
            "id": corredor.id,
            "numero": corredor.numero,
            "email": corredor.mail,
            "nombre": f"{corredor.nombres or ''} {corredor.apellidos or ''}".strip(),
            "telefono": corredor.telefonos or "",
            "direccion": corredor.direccion or "",
            "fecha_registro": corredor.fecha_alta,
            "activo": corredor.fecha_baja is None,
        }

    async def get(self, db: AsyncSession, *, id: int) -> Optional[Corredor]:
        """
        Obtiene un corredor por su ID.

        Args:
            db: Sesión de base de datos
            id: ID del corredor

        Returns:
            Optional[Corredor]: Corredor encontrado o None
        """
        query = select(Corredor).where(Corredor.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_numero(self, db: AsyncSession, *, numero: int) -> Optional[Corredor]:
        """
        Obtiene un corredor por su número.

        Args:
            db: Sesión de base de datos
            numero: Número del corredor (4 dígitos)

        Returns:
            Optional[Corredor]: Corredor encontrado o None
        """
        query = select(Corredor).where(Corredor.numero == numero)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update(
        self, db: AsyncSession, *, db_obj: Corredor, obj_in: Dict[str, Any]
    ) -> Corredor:
        """
        Actualiza un corredor.

        Args:
            db: Sesión de base de datos
            db_obj: Objeto corredor existente
            obj_in: Datos a actualizar

        Returns:
            Corredor: Corredor actualizado
        """
        # Si obj_in es un dict, usarlo directamente
        update_data = (
            obj_in
            if isinstance(obj_in, dict)
            else obj_in.model_dump(exclude_unset=True)
        )

        # Actualizar los campos del objeto
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: int) -> Optional[Corredor]:
        """
        Elimina un corredor.

        Args:
            db: Sesión de base de datos
            id: ID del corredor

        Returns:
            Optional[Corredor]: Corredor eliminado o None
        """
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def create(self, db: AsyncSession, *, obj_in: CorredorCreate) -> Corredor:
        """
        Crea un nuevo corredor.

        Args:
            db: Sesión de base de datos
            obj_in: Datos del corredor a crear

        Returns:
            Corredor: Corredor creado
        """
        obj_data = obj_in.model_dump(exclude_unset=True)
        obj_data["fecha_alta"] = datetime.now(timezone.utc)

        db_obj = Corredor(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Corredor]:
        """
        Obtiene una lista de corredores.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar
            limit: Límite de registros a retornar

        Returns:
            List[Corredor]: Lista de corredores
        """
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_corredor_with_user(
        self,
        db: AsyncSession,
        *,
        numero: int,
        nombres: str,
        apellidos: str,
        documento: str,
        direccion: str,
        localidad: str,
        telefonos: str,
        movil: Optional[str],
        mail: str,
        password: str,
        is_superuser: bool = False,
        role: str = "corredor",
        observaciones: Optional[str] = None,
    ) -> tuple[Corredor, Usuario]:
        """
        Crea un corredor y su usuario asociado en una sola operación.

        Returns:
            tuple[Corredor, Usuario]: Tupla con el corredor y el usuario creado
        """
        fecha_alta = datetime.now(timezone.utc)
        corredor = Corredor(
            numero=numero,
            nombres=nombres,
            apellidos=apellidos,
            documento=documento,
            direccion=direccion,
            localidad=localidad,
            telefonos=telefonos,
            movil=movil,
            mail=mail,
            observaciones=observaciones,
            fecha_alta=fecha_alta,
        )

        db.add(corredor)
        await db.flush()

        usuario = Usuario(
            nombre=nombres,
            apellido=apellidos,
            email=mail,
            username=mail,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=is_superuser,
            role=role,
            corredor_numero=numero,
            telefono=telefonos,
        )

        db.add(usuario)
        await db.commit()
        await db.refresh(corredor)
        await db.refresh(usuario)

        return corredor, usuario


corredor_crud = CRUDCorredor(Corredor)
