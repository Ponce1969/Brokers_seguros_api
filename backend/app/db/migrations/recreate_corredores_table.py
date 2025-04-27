"""Script para recrear la tabla corredores con la nueva estructura

Este script elimina y recrea la tabla corredores con un id autoincremental
y numero como campo único.
"""

import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Crear engine
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)


async def recreate_table():
    """Recrear la tabla corredores con la nueva estructura"""
    async with engine.begin() as conn:
        # Verificar si la tabla existe
        logger.info("Verificando si la tabla corredores existe...")
        result = await conn.execute(text(
            """SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'corredores'
            )"""
        ))
        row = result.fetchone()
        table_exists = row[0]
        
        if table_exists:
            # Eliminar la tabla corredores si existe
            logger.info("Eliminando tabla corredores existente...")
            await conn.execute(text("DROP TABLE IF EXISTS corredores CASCADE"))
        
        # Crear la tabla corredores con la nueva estructura
        logger.info("Creando tabla corredores con la nueva estructura...")
        await conn.execute(text("""
            CREATE TABLE corredores (
                id SERIAL PRIMARY KEY,
                numero INTEGER NOT NULL UNIQUE,
                nombres VARCHAR(30),
                apellidos VARCHAR(30) NOT NULL,
                documento VARCHAR(20) NOT NULL UNIQUE,
                direccion VARCHAR(70) NOT NULL,
                localidad VARCHAR(15) NOT NULL,
                telefonos VARCHAR(20),
                movil VARCHAR(20),
                mail VARCHAR(40) NOT NULL UNIQUE,
                observaciones TEXT,
                fecha_alta DATE,
                fecha_baja DATE,
                matricula VARCHAR(50),
                especializacion VARCHAR(100)
            )
        """))
        
        logger.info("Tabla corredores recreada exitosamente!")


async def main():
    try:
        logger.info("Iniciando recreación de la tabla corredores...")
        await recreate_table()
        logger.info("Proceso completado exitosamente!")
    except Exception as e:
        logger.error(f"Error durante la recreación de la tabla: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
