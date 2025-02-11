from app.db.session import async_session
from app.db.crud.usuario import usuario_crud
import asyncio

async def check_user():
    async with async_session() as db:
        user = await usuario_crud.get_by_username(db, 'rponce')
        print(f'Usuario encontrado: {user is not None}')
        if user:
            print(f'Username: {user.username}')
            print(f'Email: {user.email}')
            print(f'Role: {user.role}')
            print(f'Is active: {user.is_active}')

if __name__ == "__main__":
    asyncio.run(check_user())
