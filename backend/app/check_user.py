import asyncio

from app.db.crud.usuario import usuario_crud
from app.db.session import async_session


async def check_user():
    async with async_session() as db:
        user = await usuario_crud.get_by_username(db, "rponce")
        print(
            f"Usuario: {user.username}, Role: {user.role}, Is Superuser: {user.is_superuser}"
        )


if __name__ == "__main__":
    asyncio.run(check_user())
