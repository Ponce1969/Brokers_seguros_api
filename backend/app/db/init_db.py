import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.roles import Role
from app.core.security import get_password_hash

# Importar la configuración para obtener la URL de la base de datos
from app.core.config import settings

# Usar la URL de la base de datos desde las variables de entorno
DATABASE_URL = str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(DATABASE_URL, echo=True)


async def init_db() -> None:
    """Inicializa la base de datos con el usuario administrador."""

    # Importar todos los modelos para que SQLAlchemy los conozca
    from app.db.base_class import Base
    from app.db.models import Usuario, Corredor

    # Crear todas las tablas
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Tablas creadas exitosamente.")

    # Crear una sesión
    async with AsyncSession(async_engine) as db:
        # Verificar si ya existe un usuario administrador
        try:
            # Primero verificamos si la tabla existe haciendo una consulta simple
            result = await db.execute("SELECT 1 FROM usuarios LIMIT 1")
            # Si llegamos aquí, la tabla existe, ahora verificamos si existe el admin
            admin = await db.get(Usuario, 1)
            if admin is not None:
                print("El usuario administrador ya existe.")
                return
        except Exception as e:
            # Si hay un error, probablemente la tabla existe pero está vacía
            print(f"Verificando existencia de usuario: {e}")

        # Crear el corredor para el administrador
        from datetime import date
        from sqlalchemy import text
        
        # Definimos el número del corredor administrador
        numero_admin = 4554
        
        # Con la nueva estructura, id es autoincremental y numero es un campo único
        corredor_admin = Corredor(
            numero=numero_admin,  # Número específico para el corredor administrador (identificador de negocio)
            nombres="Rodrigo",
            apellidos="Ponce",
            documento="17775367",  # Documento requerido
            direccion="Av. Principal 123",  # Dirección requerida
            localidad="Montevideo",
            mail="rpd.ramas@gmail.com",
            movil="+598 99 123 456",
            telefonos="+598 2345 6789",
            fecha_alta=date.today(),  # Fecha de alta actual
            # fecha_baja=None  # Al ser None, indica que está activo
        )
        
        db.add(corredor_admin)
        await db.commit()
        print(f"Corredor administrador creado exitosamente con número: {numero_admin}")
        
        # Crear el usuario administrador vinculado al corredor
        admin = Usuario(
            nombre="Rodrigo",
            apellido="Ponce",
            email="rpd.ramas@gmail.com",
            username="rponce",
            hashed_password=get_password_hash("Gallinal2218**"),
            is_active=True,
            is_superuser=True,
            role=Role.ADMIN,
            corredor_numero=numero_admin,  # Vinculamos al corredor por su nu00famero (identificador de negocio)
            comision_porcentaje=10.0,  # Asignamos un porcentaje de comisión
            telefono="+598 99 123 456",
        )
        
        db.add(admin)
        await db.commit()
        print("Usuario administrador creado exitosamente.")


if __name__ == "__main__":
    asyncio.run(init_db())
