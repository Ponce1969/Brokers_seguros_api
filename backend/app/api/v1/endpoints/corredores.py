from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.corredor import corredor_crud
from app.db.database import get_db
from app.schemas.corredor import Corredor, CorredorCreate, CorredorUpdate
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/", response_model=List[Corredor])
async def get_corredores(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Recuperar corredores.
    """
    corredores = await corredor_crud.get_multi(db, skip=skip, limit=limit)
    return corredores


@router.post("/", response_model=Corredor)
async def create_corredor(
    *, db: AsyncSession = Depends(get_db), corredor_in: CorredorCreate
) -> Any:
    """
    Crear nuevo corredor.
    """
    corredor = await corredor_crud.create(db, obj_in=corredor_in)
    return corredor


@router.post("/admin", response_model=Corredor)
async def create_admin(
    *, db: AsyncSession = Depends(get_db), corredor_in: CorredorCreate
) -> Any:
    """
    Crear corredor administrador inicial.
    Solo funciona si no hay corredores en el sistema.
    """
    # Verificar si ya existen corredores
    existing_corredores = await corredor_crud.get_multi(db, limit=1)
    if existing_corredores:
        raise HTTPException(
            status_code=400,
            detail="No se puede crear el administrador inicial porque ya existen corredores en el sistema"
        )

    # Asegurarse de que el rol sea admin
    corredor_data = corredor_in.dict()
    corredor_data["role"] = "admin"
    corredor_data["is_active"] = True
    
    # Asignar número de corredor inicial
    corredor_data["numero"] = 1000  # Número inicial para el primer corredor

    # Crear el corredor administrador
    corredor = await corredor_crud.create(db, obj_in=CorredorCreate(**corredor_data))
    return corredor


@router.get("/{corredor_id}", response_model=Corredor)
async def get_corredor(corredor_id: int, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Obtener corredor por ID.
    """
    corredor = await corredor_crud.get(db, id=corredor_id)
    if not corredor:
        raise HTTPException(status_code=404, detail="Corredor no encontrado")
    return corredor


@router.put("/{corredor_id}", response_model=Corredor)
async def update_corredor(
    *, db: AsyncSession = Depends(get_db), corredor_id: int, corredor_in: CorredorUpdate
) -> Any:
    """
    Actualizar corredor.
    """
    corredor = await corredor_crud.get(db, id=corredor_id)
    if not corredor:
        raise HTTPException(status_code=404, detail="Corredor no encontrado")
    corredor = await corredor_crud.update(db, db_obj=corredor, obj_in=corredor_in)
    return corredor


@router.delete("/{corredor_id}", response_model=Corredor)
async def delete_corredor(
    *, db: AsyncSession = Depends(get_db), corredor_id: int
) -> Any:
    """
    Eliminar corredor.
    """
    corredor = await corredor_crud.get(db, id=corredor_id)
    if not corredor:
        raise HTTPException(status_code=404, detail="Corredor no encontrado")
    corredor = await corredor_crud.delete(db, id=corredor_id)
    return corredor
