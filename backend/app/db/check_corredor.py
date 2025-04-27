"""Script para verificar si existe el corredor administrador"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.db.models import Corredor

async def check_corredor():
    # Crear engine y sessionmaker
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Verificar si existe el corredor administrador
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Corredor).where(Corredor.numero == 4554))
        corredor = result.scalar_one_or_none()
        
        print(f"Corredor administrador encontrado: {corredor is not None}")
        if corredor:
            print(f"ID: {corredor.id}, Numero: {corredor.numero}, Nombre: {corredor.nombres} {corredor.apellidos}")
        else:
            print("El corredor administrador no existe en la base de datos.")

if __name__ == "__main__":
    asyncio.run(check_corredor())
