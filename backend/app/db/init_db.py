import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

import os
from app.core.roles import Role
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from app.db.models.usuario import Usuario

# Crear el engine con localhost
DATABASE_URL = f"postgresql+asyncpg://admin_broker:Br0k3rS3gur0s2024@localhost:5432/brokerseguros_db"
async_engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()

async def init_db() -> None:
    """Inicializa la base de datos con el usuario administrador."""
    
    # Crear todas las tablas
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Crear una sesión
    async with AsyncSession(async_engine) as db:
        # Verificar si ya existe un usuario administrador
        admin = await db.get(Usuario, 1)
        if admin is not None:
            print("El usuario administrador ya existe.")
            return

        # Crear el usuario administrador
        admin = Usuario(
            nombre="Rodrigo",
            apellido="Ponce",
            email="rpd.ramas@gmail.com",  # Puedes cambiar esto por el email correcto
            username="rponce",
            hashed_password=get_password_hash("Gallinal2218**"),
            is_active=True,
            is_superuser=True,
            role=Role.ADMIN,
            telefono="+54 9 11 3699 5733",  # Puedes agregar el teléfono si lo deseas
        )
        
        db.add(admin)
        await db.commit()
        print("Usuario administrador creado exitosamente.")

if __name__ == "__main__":
    asyncio.run(init_db())
