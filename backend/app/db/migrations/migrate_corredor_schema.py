"""Script de migración para modificar el esquema de la tabla corredores

Este script realiza los siguientes cambios:
1. Crea una nueva tabla corredores con id autoincremental y numero como campo único
2. Migra los datos de la tabla original a la nueva estructura
3. Actualiza las relaciones con otras tablas

Este enfoque es más profesional y preparado para el futuro crecimiento de la aplicación.
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
    """Ejecuta la migración para modificar el esquema de la tabla corredores"""
    async with engine.begin() as conn:
        # Verificar si la tabla corredores existe
        result = await conn.execute(text(
            """SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'corredores'
            )"""
        ))
        row = await result.fetchone()
        corredores_exists = row[0]
        
        if not corredores_exists:
            logger.info("La tabla corredores no existe. Creando desde cero...")
            await conn.execute(
                text(
                    """
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
                    """
                )
            )
            logger.info("Tabla corredores creada correctamente.")
            return


        # Paso 1: Crear una tabla temporal con la nueva estructura
        logger.info("Creando tabla temporal con la nueva estructura...")
        await conn.execute(
            text(
                """
                CREATE TABLE corredores_new (
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
                INSERT INTO corredores_new 
                (numero, nombres, apellidos, documento, direccion, localidad, telefonos, 
                movil, mail, observaciones, fecha_alta, fecha_baja, matricula, especializacion)
                SELECT numero, nombres, apellidos, documento, direccion, localidad, telefonos, 
                movil, mail, observaciones, fecha_alta, fecha_baja, matricula, especializacion
                FROM corredores
                """
            )
        )

        # Paso 3: Verificar y eliminar restricciones de clave foránea
        logger.info("Verificando restricciones de clave foránea...")
        result = await conn.execute(text(
            """
            SELECT tc.table_name, tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND ccu.table_name = 'corredores'
            """
        ))
        constraints = await result.fetchall()
        
        for constraint in constraints:
            table_name, constraint_name = constraint
            logger.info(f"Eliminando restricción {constraint_name} de la tabla {table_name}...")
            await conn.execute(text(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name} CASCADE"))
            
        # Paso 4: Eliminar la tabla original
        logger.info("Eliminando tabla original...")
        await conn.execute(text("DROP TABLE corredores CASCADE"))

        # Paso 5: Renombrar la tabla temporal a la original
        logger.info("Renombrando tabla temporal...")
        await conn.execute(text("ALTER TABLE corredores_new RENAME TO corredores"))

        # Paso 6: Verificar relaciones que necesitan ser recreadas
        logger.info("Verificando relaciones que necesitan ser recreadas...")
        result = await conn.execute(text(
            """
            SELECT kcu.table_name, kcu.column_name
            FROM information_schema.tables t
            JOIN information_schema.columns c ON t.table_name = c.table_name
            LEFT JOIN information_schema.key_column_usage kcu ON c.table_name = kcu.table_name AND c.column_name = kcu.column_name
            WHERE c.column_name LIKE '%corredor%' AND t.table_name != 'corredores'
            """
        ))
        relations = await result.fetchall()
        
        for relation in relations:
            table_name, column_name = relation
            logger.info(f"Recreando relación para {table_name}.{column_name}...")
            constraint_name = f"fk_{table_name}_{column_name}"
            await conn.execute(text(
                f"""
                ALTER TABLE {table_name} 
                ADD CONSTRAINT {constraint_name} 
                FOREIGN KEY ({column_name}) REFERENCES corredores(numero)
                """
            ))
            
        logger.info("Migración completada con éxito!")


async def main():
    """Función principal para ejecutar la migración"""
    try:
        logger.info("Iniciando migración para modificar el esquema de la tabla corredores...")
        await run_migration()
        logger.info("Migración completada exitosamente!")
    except Exception as e:
        logger.error(f"Error durante la migración: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
