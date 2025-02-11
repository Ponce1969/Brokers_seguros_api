from app.db.session import async_session
from app.db.crud.usuario import usuario_crud
from app.schemas.usuario import UsuarioCreate
from app.core.roles import Role
import asyncio

async def create_admin():
    async with async_session() as db:
        # Verificar si el usuario ya existe
        user = await usuario_crud.get_by_username(db, 'rponce')
        if user:
            print('El usuario rponce ya existe')
            return
        
        # Crear usuario admin
        admin = UsuarioCreate(
            email="rpd.ramas@gmail.com",
            username="rponce",
            password="Gallinal2218**",
            nombre="Rodrigo",
            apellido="Ponce",
            role=Role.ADMIN,
            comision_porcentaje=0,
            telefono="+5491136995733"  # Formato internacional sin espacios
        )
        
        user = await usuario_crud.create(db, obj_in=admin)
        print(f'Usuario administrador creado: {user.username}')

if __name__ == "__main__":
    asyncio.run(create_admin())
