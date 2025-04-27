"""Script para verificar la estructura del corredor administrador"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.models import Corredor

async def verify_corredor():
    # Crear engine y session factory
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Verificar el corredor administrador
    async with session_factory() as session:
        # Buscar el corredor por nu00famero
        result = await session.execute(select(Corredor).where(Corredor.numero == 4554))
        corredor = result.scalar_one_or_none()
        
        if corredor:
            print("Corredor administrador encontrado correctamente")
            print(f"ID: {corredor.id} (autoincremental)")
            print(f"Numero: {corredor.numero} (identificador de negocio)")
            print(f"Nombre: {corredor.nombres} {corredor.apellidos}")
            print(f"Email: {corredor.mail}")
        else:
            print("No se encontru00f3 el corredor administrador")

if __name__ == "__main__":
    asyncio.run(verify_corredor())
