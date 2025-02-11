from datetime import date, timedelta
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.permissions import require_permissions
from app.db.crud.poliza import poliza_crud
from app.db.database import get_db
from app.db.models.usuario import Usuario as UsuarioModel
from app.db.models.movimiento_vigencia import TipoDuracion
from app.schemas.poliza import Poliza, PolizaCreate, PolizaDetalle, PolizaUpdate

router = APIRouter()


@router.get("/", response_model=List[Poliza])
@require_permissions(["polizas_ver"])
async def get_polizas(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    cliente_id: Optional[UUID] = None,
    corredor_id: Optional[int] = None,
    estado: Optional[str] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    vencimiento_desde: Optional[date] = None,
    vencimiento_hasta: Optional[date] = None,
    incluir_vencidas: bool = Query(False, description="Incluir pólizas ya vencidas"),
    proximo_vencimiento: Optional[int] = Query(
        None,
        ge=1,
        le=365,
        description="Buscar pólizas que vencen en los próximos N días"
    ),
    numero_poliza: Optional[str] = None,
    tipo_seguro_id: Optional[int] = None,
    moneda_id: Optional[int] = None,
    suma_asegurada_min: Optional[float] = None,
    suma_asegurada_max: Optional[float] = None,
    prima_min: Optional[float] = None,
    prima_max: Optional[float] = None,
    cliente_nombre: Optional[str] = Query(None, description="Buscar por nombre del cliente"),
    cliente_apellido: Optional[str] = Query(None, description="Buscar por apellido del cliente"),
    tipo_duracion: Optional[TipoDuracion] = Query(None, description="Filtrar por tipo de duración"),
    ordenar_por: Optional[str] = Query(
        None, 
        description="Campo por el cual ordenar (ej: fecha_inicio, suma_asegurada, nombres, apellidos)"
    ),
    orden: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> Any:
    """
    Recuperar pólizas con filtros opcionales.
    
    Filtros de fecha de vencimiento:
    - Usar vencimiento_desde y vencimiento_hasta para un rango específico
    - Usar proximo_vencimiento para pólizas que vencen en los próximos N días
    - Usar incluir_vencidas para incluir pólizas ya vencidas en los resultados
    
    Ejemplos de uso:
    1. Pólizas que vencen en los próximos 30 días:
       ?proximo_vencimiento=30
    
    2. Pólizas que vencen en un rango específico:
       ?vencimiento_desde=2024-12-31&vencimiento_hasta=2025-12-31
    
    3. Pólizas vencidas en un rango:
       ?vencimiento_desde=2024-01-01&vencimiento_hasta=2024-12-31&incluir_vencidas=true
       
    4. Pólizas por tipo de duración:
       ?tipo_duracion=diaria
    """
    # Si se especifica proximo_vencimiento, calcular el rango de fechas
    if proximo_vencimiento is not None:
        vencimiento_desde = date.today()
        vencimiento_hasta = vencimiento_desde + timedelta(days=proximo_vencimiento)
        incluir_vencidas = False  # Forzar a False cuando se usa proximo_vencimiento
    
    # Validar fechas de vencimiento
    if vencimiento_desde and vencimiento_hasta and vencimiento_desde > vencimiento_hasta:
        raise HTTPException(
            status_code=400,
            detail="La fecha 'vencimiento_desde' debe ser anterior a 'vencimiento_hasta'"
        )
    
    # Si el usuario es corredor, solo puede ver sus propias pólizas
    if current_user.role == "corredor":
        corredor_id = current_user.corredor_numero
    
    polizas = await poliza_crud.get_multi(
        db,
        skip=skip,
        limit=limit,
        cliente_id=cliente_id,
        corredor_id=corredor_id,
        estado=estado,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        vencimiento_desde=vencimiento_desde,
        vencimiento_hasta=vencimiento_hasta,
        incluir_vencidas=incluir_vencidas,
        numero_poliza=numero_poliza,
        tipo_seguro_id=tipo_seguro_id,
        moneda_id=moneda_id,
        suma_asegurada_min=suma_asegurada_min,
        suma_asegurada_max=suma_asegurada_max,
        prima_min=prima_min,
        prima_max=prima_max,
        cliente_nombre=cliente_nombre,
        cliente_apellido=cliente_apellido,
        tipo_duracion=tipo_duracion,
        ordenar_por=ordenar_por,
        orden=orden
    )
    return polizas


@router.post("/", response_model=Poliza)
@require_permissions(["polizas_crear"])
async def create_poliza(
    *,
    db: AsyncSession = Depends(get_db),
    poliza_in: PolizaCreate,
    current_user: UsuarioModel = Depends(get_current_active_user)
) -> Any:
    """
    Crear nueva póliza.
    """
    # Verificar si el número de póliza ya existe
    poliza = await poliza_crud.get_by_numero(db, numero_poliza=poliza_in.numero_poliza)
    if poliza:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una póliza con este número"
        )
    
    # Si el usuario es corredor, solo puede crear pólizas para sí mismo
    if current_user.role == "corredor":
        if poliza_in.corredor_id and poliza_in.corredor_id != current_user.corredor_numero:
            raise HTTPException(
                status_code=403,
                detail="No puede crear pólizas para otros corredores"
            )
        poliza_in.corredor_id = current_user.corredor_numero
    
    return await poliza_crud.create(db, obj_in=poliza_in)


@router.get("/{poliza_id}", response_model=PolizaDetalle)
@require_permissions(["polizas_ver"])
async def get_poliza(
    poliza_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_active_user)
) -> Any:
    """
    Obtener una póliza específica por ID.
    """
    poliza = await poliza_crud.get(db, id=poliza_id)
    if not poliza:
        raise HTTPException(
            status_code=404,
            detail="Póliza no encontrada"
        )
    
    # Si el usuario es corredor, solo puede ver sus propias pólizas
    if current_user.role == "corredor" and poliza.corredor_numero != current_user.corredor_numero:
        raise HTTPException(
            status_code=403,
            detail="No tiene permiso para ver esta póliza"
        )
    
    return poliza


@router.put("/{poliza_id}", response_model=Poliza)
@require_permissions(["polizas_editar"])
async def update_poliza(
    *,
    db: AsyncSession = Depends(get_db),
    poliza_id: int,
    poliza_in: PolizaUpdate,
    current_user: UsuarioModel = Depends(get_current_active_user)
) -> Any:
    """
    Actualizar una póliza.
    """
    poliza = await poliza_crud.get(db, id=poliza_id)
    if not poliza:
        raise HTTPException(
            status_code=404,
            detail="Póliza no encontrada"
        )
    
    # Si el usuario es corredor, solo puede modificar sus propias pólizas
    if current_user.role == "corredor" and poliza.corredor_numero != current_user.corredor_numero:
        raise HTTPException(
            status_code=403,
            detail="No tiene permiso para modificar esta póliza"
        )
    
    return await poliza_crud.update(db, db_obj=poliza, obj_in=poliza_in)


@router.delete("/{poliza_id}", response_model=Poliza)
@require_permissions(["polizas_eliminar"])
async def delete_poliza(
    *,
    db: AsyncSession = Depends(get_db),
    poliza_id: int,
    current_user: UsuarioModel = Depends(get_current_active_user)
) -> Any:
    """
    Eliminar una póliza.
    """
    poliza = await poliza_crud.get(db, id=poliza_id)
    if not poliza:
        raise HTTPException(
            status_code=404,
            detail="Póliza no encontrada"
        )
    
    # Si el usuario es corredor, solo puede eliminar sus propias pólizas
    if current_user.role == "corredor" and poliza.corredor_numero != current_user.corredor_numero:
        raise HTTPException(
            status_code=403,
            detail="No tiene permiso para eliminar esta póliza"
        )
    
    return await poliza_crud.delete(db, id=poliza_id)
