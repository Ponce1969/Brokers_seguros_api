from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.permissions import require_permissions
from app.core.roles import Role
from app.db.crud.usuario import usuario_crud
from app.db.crud.corredor import corredor_crud
from app.db.database import get_db
from app.db.models.usuario import Usuario as UsuarioModel
from app.schemas.usuario import Usuario, UsuarioCreate, UsuarioUpdate

router = APIRouter()


@router.get("/", response_model=List[Usuario])
@require_permissions(["usuarios_ver"])
async def get_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> Any:
    """
    Recuperar usuarios.
    """
    return await usuario_crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=Usuario)
@require_permissions(["usuarios_crear"])
async def create_usuario(
    *,
    db: AsyncSession = Depends(get_db),
    usuario_in: UsuarioCreate,
    current_user: UsuarioModel = Depends(get_current_active_user)
) -> Any:
    """
    Crear nuevo usuario.
    """
    # Solo los administradores pueden crear otros administradores
    if usuario_in.role == Role.ADMIN and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden crear otros administradores",
        )

    # Si es un usuario corredor, validar el número de corredor y su existencia
    if usuario_in.role == Role.CORREDOR:
        if not usuario_in.corredor_numero:
            raise HTTPException(
                status_code=400,
                detail="El número de corredor es requerido para usuarios corredores",
            )
        
        # Verificar que el corredor exista
        corredor = await corredor_crud.get_by_numero(db, numero=usuario_in.corredor_numero)
        if not corredor:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró un corredor con el número {usuario_in.corredor_numero}",
            )

    return await usuario_crud.create(db, obj_in=usuario_in)


@router.get("/{usuario_id}", response_model=Usuario)
@require_permissions(["usuarios_ver"])
async def get_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> Any:
    """
    Obtener usuario por ID.
    """
    usuario = await usuario_crud.get(db, id=usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/{usuario_id}", response_model=Usuario)
@require_permissions(["usuarios_editar"])
async def update_usuario(
    *,
    db: AsyncSession = Depends(get_db),
    usuario_id: int,
    usuario_in: UsuarioUpdate,
    current_user: UsuarioModel = Depends(get_current_active_user)
) -> Any:
    """
    Actualizar usuario.
    """
    usuario = await usuario_crud.get(db, id=usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Solo los administradores pueden modificar otros administradores
    if usuario.role == Role.ADMIN and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden modificar otros administradores",
        )

    # Si se está actualizando a un usuario corredor, validar el número de corredor y su existencia
    if usuario_in.role == Role.CORREDOR:
        if not usuario_in.corredor_numero:
            raise HTTPException(
                status_code=400,
                detail="El número de corredor es requerido para usuarios corredores",
            )
            
        # Verificar que el corredor exista
        corredor = await corredor_crud.get_by_numero(db, numero=usuario_in.corredor_numero)
        if not corredor:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró un corredor con el número {usuario_in.corredor_numero}",
            )

    return await usuario_crud.update(db, db_obj=usuario, obj_in=usuario_in)


@router.delete("/{usuario_id}", response_model=Usuario)
@require_permissions(["usuarios_eliminar"])
async def delete_usuario(
    *,
    db: AsyncSession = Depends(get_db),
    usuario_id: int,
    current_user: UsuarioModel = Depends(get_current_active_user)
) -> Any:
    """
    Eliminar usuario.
    """
    usuario = await usuario_crud.get(db, id=usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Solo los administradores pueden eliminar otros administradores
    if usuario.role == Role.ADMIN and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden eliminar otros administradores",
        )

    return await usuario_crud.remove(db, id=usuario_id)
