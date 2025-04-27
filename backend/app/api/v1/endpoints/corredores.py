"""
Endpoints para la gestión de corredores
"""

from typing import Any, List
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.crud.corredor import corredor_crud
from app.db.database import get_db
from app.db.models.corredor import Corredor
from app.schemas.corredor import CorredorCreate, CorredorResponse, CorredorUpdate

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

router = APIRouter()


async def get_corredor_or_404(db: AsyncSession, corredor_id: int) -> Corredor:
    """
    Obtiene un corredor por ID o por número y lanza un HTTPException 404 si no existe.
    """
    # Primero intentamos buscar por ID (nueva estructura)
    corredor = await corredor_crud.get(db, id=corredor_id)
    
    # Si no encontramos por ID, intentamos buscar por número (para compatibilidad)
    if not corredor:
        corredor = await corredor_crud.get_by_numero(db, numero=corredor_id)
    if not corredor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Corredor no encontrado"
        )
    return corredor


@router.get("/", response_model=List[CorredorResponse])
async def get_corredores(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Recuperar corredores.
    """
    corredores = await corredor_crud.get_multi(db, skip=skip, limit=limit)
    return [CorredorResponse.model_validate(c, from_attributes=True) for c in corredores]


@router.post("/", response_model=CorredorResponse, status_code=status.HTTP_201_CREATED)
async def create_corredor(
    *, db: AsyncSession = Depends(get_db), corredor_in: CorredorCreate
) -> Any:
    """
    Crear nuevo corredor.
    """
    try:
        corredor = await corredor_crud.create(db, obj_in=corredor_in)
        return CorredorResponse.model_validate(corredor, from_attributes=True)
    except IntegrityError as e:
        logger.error(f"Error al crear corredor: {e}")
        error_detail = "Error inesperado al crear el corredor"
        if "unique constraint" in str(e.orig).lower():
            if "numero" in str(e.orig).lower():
                error_detail = "El número de corredor ya existe"
            elif "documento" in str(e.orig).lower():
                error_detail = "El documento ya está registrado"
            elif "mail" in str(e.orig).lower():
                error_detail = "El email ya está registrado"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)


@router.post("/admin", response_model=CorredorResponse, status_code=status.HTTP_201_CREATED)
async def create_admin(
    *, db: AsyncSession = Depends(get_db), corredor_in: CorredorCreate
) -> Any:
    """
    Crear corredor administrador inicial.
    Solo funciona si no hay corredores en el sistema.
    """
    try:
        async with db.begin():  # Transacción atómica
            existing_admin = await corredor_crud.get_admin(db)
            if existing_admin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un administrador en el sistema.",
                )

            existing_corredores = await corredor_crud.get_multi(db, limit=1)
            if existing_corredores:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede crear el administrador inicial porque ya existen corredores en el sistema.",
                )

            corredor_data = corredor_in.model_dump()
            corredor_data.update({"role": "admin", "is_active": True, "numero": 1000})

            corredor = await corredor_crud.create(db, obj_in=CorredorCreate(**corredor_data))

        logger.info(
            f"Administrador creado exitosamente: ID={corredor.id}, Número={corredor.numero}"
        )
        return CorredorResponse.model_validate(corredor, from_attributes=True)

    except IntegrityError as e:
        logger.error(f"Error al crear administrador: {e}")
        error_detail = "Error inesperado al crear el administrador"
        if "unique constraint" in str(e.orig).lower():
            error_detail = "Número de corredor ya existe"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)


@router.get("/numero/{numero}", response_model=CorredorResponse)
async def get_corredor_by_numero(numero: int, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Obtener corredor por número.
    """
    corredor = await corredor_crud.get_by_numero(db, numero=numero)
    if not corredor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Corredor con número {numero} no encontrado",
        )
    return CorredorResponse.model_validate(corredor, from_attributes=True)


@router.get("/{corredor_id}", response_model=CorredorResponse)
async def get_corredor(corredor_id: int, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Obtener corredor por ID.
    """
    corredor = await get_corredor_or_404(db, corredor_id)
    return CorredorResponse.model_validate(corredor, from_attributes=True)


@router.put("/{corredor_id}", response_model=CorredorResponse)
async def update_corredor(
    *, db: AsyncSession = Depends(get_db), corredor_id: int, corredor_in: CorredorUpdate
) -> Any:
    """
    Actualizar corredor.
    """
    try:
        logger.info(f"Datos recibidos para actualizar corredor: {corredor_in}")
        corredor = await get_corredor_or_404(db, corredor_id)
        corredor = await corredor_crud.update(db, db_obj=corredor, obj_in=corredor_in)
        return CorredorResponse.model_validate(corredor, from_attributes=True)
    except IntegrityError as e:
        logger.error(f"Error al actualizar corredor: {e}")
        error_detail = "Error inesperado al actualizar el corredor"
        if "unique constraint" in str(e.orig).lower():
            if "documento" in str(e.orig).lower():
                error_detail = "El documento ya está registrado"
            elif "mail" in str(e.orig).lower():
                error_detail = "El email ya está registrado"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)


@router.delete("/{corredor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_corredor(*, db: AsyncSession = Depends(get_db), corredor_id: int) -> None:
    """
    Eliminar corredor.
    """
    corredor = await get_corredor_or_404(db, corredor_id)
    await corredor_crud.delete(db, id=corredor_id)
