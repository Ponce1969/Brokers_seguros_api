"""Script de migración para agregar el campo id a la tabla corredores

Este script realiza los siguientes cambios:
1. Agrega una columna id autoincremental a la tabla corredores
2. Convierte la columna numero de clave primaria a campo único
3. Preserva los datos existentes
"""

import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Crear engine y sessionmaker
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def run_migration():
    """Ejecuta la migración para agregar el campo id a la tabla corredores"""
    async with engine.begin() as conn:
        # Paso 1: Crear una tabla temporal con la nueva estructura
        logger.info("Creando tabla temporal con la nueva estructura...")
        await conn.execute(
            text(
                """
                CREATE TABLE corredores_temp (
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
                """
            )
        )

        # Paso 2: Copiar los datos de la tabla original a la temporal
        logger.info("Copiando datos a la tabla temporal...")
        await conn.execute(
            text(
                """
                INSERT INTO corredores_temp 
                (numero, nombres, apellidos, documento, direccion, localidad, telefonos, 
                movil, mail, observaciones, fecha_alta, fecha_baja, matricula, especializacion)
                SELECT numero, nombres, apellidos, documento, direccion, localidad, telefonos, 
                movil, mail, observaciones, fecha_alta, fecha_baja, matricula, especializacion
                FROM corredores
                """
            )
        )

        # Paso 3: Eliminar la tabla original
        logger.info("Eliminando tabla original...")
        await conn.execute(text("DROP TABLE corredores CASCADE"))

        # Paso 4: Renombrar la tabla temporal a la original
        logger.info("Renombrando tabla temporal...")
        await conn.execute(text("ALTER TABLE corredores_temp RENAME TO corredores"))

        # Paso 5: Recrear las relaciones con otras tablas
        logger.info("Recreando relaciones con otras tablas...")
        # Relación con usuarios
        await conn.execute(
            text(
                """
                ALTER TABLE usuarios 
                ADD CONSTRAINT fk_usuarios_corredor 
                FOREIGN KEY (corredor_numero) REFERENCES corredores(numero)
                """
            )
        )

        # Relación con clientes_corredores
        await conn.execute(
            text(
                """
                ALTER TABLE clientes_corredores 
                ADD CONSTRAINT fk_clientes_corredores_corredor 
                FOREIGN KEY (corredor_id) REFERENCES corredores(numero)
                """
            )
        )

        # Relación con movimientos_vigencia
        await conn.execute(
            text(
                """
                ALTER TABLE movimientos_vigencia 
                ADD CONSTRAINT fk_movimientos_vigencia_corredor 
                FOREIGN KEY (corredor_id) REFERENCES corredores(numero)
                """
            )
        )

        logger.info("Migración completada con éxito!")


async def main():
    """Función principal para ejecutar la migración"""
    try:
        logger.info("Iniciando migración para agregar id a la tabla corredores...")
        await run_migration()
        logger.info("Migración completada exitosamente!")
    except Exception as e:
        logger.error(f"Error durante la migración: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
