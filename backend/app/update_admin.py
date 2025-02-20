import asyncio
from app.db.session import async_session
from app.db.crud.usuario import usuario_crud

async def update_admin():
    async with async_session() as db:
        try:
            # Obtener el usuario por username
            user = await usuario_crud.get_by_username(db, "rponce")
            if user:
                # Actualizar a superusuario
                user.is_superuser = True
                await db.commit()
                print(f"""
Usuario administrador actualizado:
- Nombre: {user.nombre} {user.apellido}
- Username: {user.username}
- Role: {user.role}
- Superusuario: {user.is_superuser}
                """)
            else:
                print("Usuario rponce no encontrado")
        except Exception as e:
            print(f"Error al actualizar el administrador: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(update_admin())
