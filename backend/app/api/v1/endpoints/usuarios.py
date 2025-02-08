from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.usuario import usuario_crud
from app.db.database import get_db
from app.schemas.usuario import Usuario, UsuarioCreate, UsuarioUpdate

router = APIRouter()


@router.get("/", response_model=List[Usuario])
async def get_usuarios(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Recuperar usuarios.
    """
    return await usuario_crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=Usuario)
async def create_usuario(
    *, db: AsyncSession = Depends(get_db), usuario_in: UsuarioCreate
) -> Any:
    """
    Crear nuevo usuario.
    """
    return await usuario_crud.create(db, obj_in=usuario_in)


@router.get("/{usuario_id}", response_model=Usuario)
async def get_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Obtener usuario por ID.
    """
    usuario = await usuario_crud.get(db, id=usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/{usuario_id}", response_model=Usuario)
async def update_usuario(
    *, db: AsyncSession = Depends(get_db), usuario_id: int, usuario_in: UsuarioUpdate
) -> Any:
    """
    Actualizar usuario.
    """
    usuario = await usuario_crud.get(db, id=usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return await usuario_crud.update(db, db_obj=usuario, obj_in=usuario_in)


@router.delete("/{usuario_id}", response_model=Usuario)
async def delete_usuario(*, db: AsyncSession = Depends(get_db), usuario_id: int) -> Any:
    """
    Eliminar usuario.
    """
    usuario = await usuario_crud.get(db, id=usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return await usuario_crud.remove(db, id=usuario_id)
