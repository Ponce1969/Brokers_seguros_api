from app.db.session import async_session
from app.db.crud.usuario import usuario_crud
import asyncio

async def update_admin():
    async with async_session() as db:
        user = await usuario_crud.get_by_username(db, 'rponce')
        user.is_superuser = True
        await db.commit()
        print(f'Usuario actualizado: {user.username}, Role: {user.role}, Is Superuser: {user.is_superuser}')

if __name__ == "__main__":
    asyncio.run(update_admin())
