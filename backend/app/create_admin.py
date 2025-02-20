import asyncio
from app.db.session import async_session
from app.db.crud.corredor import corredor_crud

async def create_corredor():
    async with async_session() as db:
        try:
            # Crear un corredor común y su usuario asociado
            corredor, usuario = await corredor_crud.create_corredor_with_user(
                db,
                numero=4555,  # Número diferente al anterior
                nombres="Juan",
                apellidos="García",
                documento="87654321",
                direccion="Av. Principal 123",
                localidad="Montevideo",
                telefonos="91234567",
                movil="91234567",
                mail="jgarcia@corredor.com",
                password="Corredor2024**",
                is_superuser=False,  # No es superusuario
                role="corredor",  # Rol de corredor normal
                observaciones="Corredor regular"
            )
            
            print(f"""
Corredor creado exitosamente:
- Nombre: {corredor.nombres} {corredor.apellidos}
- Número de corredor: {corredor.numero}
- Email: {usuario.email}
- Username: {usuario.username}
- Rol: {usuario.role}
- Superusuario: {usuario.is_superuser}
            """)
            
        except Exception as e:
            print(f"Error al crear el corredor: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(create_corredor())
