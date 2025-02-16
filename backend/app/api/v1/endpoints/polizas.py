# Importaciones estándar
import logging
from datetime import date, timedelta
from io import BytesIO
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import openpyxl

# Importaciones de terceros
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.ext.asyncio import AsyncSession

# Importaciones locales
from app.api.deps import get_current_active_user
from app.core.permissions import require_permissions
from app.db.crud.poliza import poliza_crud
from app.db.database import get_db
from app.db.models.movimiento_vigencia import TipoDuracion
from app.db.models.usuario import Usuario as UsuarioModel
from app.schemas.poliza import (
    EstadisticasDuracion,
    EstadisticasResponse,
    Poliza,
    PolizaCreate,
    PolizaDetalle,
    PolizaUpdate,
)

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes para códigos de estado
HTTP_400_BAD_REQUEST = 400
HTTP_403_FORBIDDEN = 403

router = APIRouter()


# Modelos Pydantic para nuevas funcionalidades
class ConfiguracionAlertas(BaseModel):
    notificar_por_email: bool = True
    notificar_por_sms: bool = False
    dias_antes_vencimiento: int = 7


class PlantillaNotificacion(BaseModel):
    asunto: str
    mensaje: str


# Funciones de utilidad
def validar_rango_fechas(
    vencimiento_desde: Optional[date], vencimiento_hasta: Optional[date]
) -> None:
    """
    Verifica que la fecha 'vencimiento_desde' sea menor o igual a 'vencimiento_hasta'.
    """
    if (
        vencimiento_desde
        and vencimiento_hasta
        and vencimiento_desde > vencimiento_hasta
    ):
        logger.error(
            "La fecha 'vencimiento_desde' debe ser anterior a 'vencimiento_hasta'"
        )
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="La fecha 'vencimiento_desde' debe ser anterior a 'vencimiento_hasta'",
        )


def aplicar_filtros_por_corredor(
    filters: Dict[str, Union[UUID, int, str, date]], current_user: UsuarioModel
) -> None:
    """
    Si el usuario es un corredor, restringe los resultados a sus pólizas.
    """
    if current_user.role == "corredor":
        filters["corredor_id"] = current_user.corredor_numero


def validar_permisos_corredor(
    poliza: Any, current_user: UsuarioModel, accion: str
) -> None:
    """
    Valida los permisos de un corredor para una póliza específica.
    """
    if (
        current_user.role == "corredor"
        and poliza.corredor_numero != current_user.corredor_numero
    ):
        logger.error(f"No tiene permiso para {accion} esta póliza")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=f"No tiene permiso para {accion} esta póliza",
        )


# Funciones para notificaciones
async def enviar_email(destinatario: str, asunto: str, mensaje: str) -> None:
    """
    Simula el envío de un email.
    """
    logger.info(f"Enviando email a {destinatario}: {asunto} - {mensaje}")


async def enviar_sms(destinatario: str, mensaje: str) -> None:
    """
    Simula el envío de un SMS.
    """
    logger.info(f"Enviando SMS a {destinatario}: {mensaje}")


async def enviar_notificacion(poliza: Poliza, usuario: UsuarioModel) -> None:
    """
    Envía notificaciones por email y SMS sobre el vencimiento de una póliza.
    """
    plantilla = (
        obtener_plantilla_notificacion()
    )  # Obtén la plantilla desde la base de datos
    mensaje = plantilla.mensaje.format(
        numero_poliza=poliza.numero_poliza,
        fecha_vencimiento=poliza.fecha_vencimiento,
    )

    if usuario.configuracion_alertas.notificar_por_email and usuario.email:
        await enviar_email(
            destinatario=usuario.email,
            asunto=plantilla.asunto,
            mensaje=mensaje,
        )

    if usuario.configuracion_alertas.notificar_por_sms and usuario.telefono:
        await enviar_sms(
            destinatario=usuario.telefono,
            mensaje=mensaje,
        )


def obtener_plantilla_notificacion() -> PlantillaNotificacion:
    """
    Obtiene la plantilla de notificación desde la base de datos.
    """
    # Aquí puedes implementar la lógica para obtener la plantilla desde la base de datos
    return PlantillaNotificacion(
        asunto="Vencimiento de Póliza",
        mensaje="La póliza {numero_poliza} vence el {fecha_vencimiento}.",
    )


# Endpoints existentes (sin cambios)
@router.get("/estadisticas/", response_model=EstadisticasResponse)
@require_permissions(["polizas_ver"])
async def get_estadisticas_polizas(
    db: AsyncSession = Depends(get_db),
    estado: Optional[str] = Query(
        "activa", description="Estado de las pólizas a incluir"
    ),
    fecha_inicio: Optional[date] = Query(
        None, description="Fecha de inicio para filtrar"
    ),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin para filtrar"),
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> EstadisticasResponse:
    """
    Obtener estadísticas de pólizas agrupadas por tipo de duración.
    """
    filters = {"estado": estado, "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
    aplicar_filtros_por_corredor(filters, current_user)

    try:
        stats_by_duration, suma_total, prima_total, total_polizas = (
            await poliza_crud.get_estadisticas(db, **filters)
        )
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Error al obtener estadísticas"
        )

    estadisticas_por_duracion = [
        EstadisticasDuracion(
            tipo_duracion=stat.tipo_duracion,
            cantidad_polizas=stat.cantidad_polizas,
            suma_asegurada_total=stat.suma_asegurada_total or 0.0,
            prima_total=stat.prima_total or 0.0,
        )
        for stat in stats_by_duration
    ]

    return EstadisticasResponse(
        total_polizas=total_polizas,
        suma_asegurada_total=suma_total,
        prima_total=prima_total,
        por_duracion=estadisticas_por_duracion,
    )


# Endpoints nuevos para notificaciones y alertas
@router.get("/notificar-vencimientos/")
@require_permissions(["polizas_ver"])
async def notificar_vencimientos(
    db: AsyncSession = Depends(get_db),
    dias_antes: int = Query(7, description="Días antes del vencimiento para notificar"),
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> Dict[str, str]:
    """
    Verifica las pólizas próximas a vencer y envía notificaciones.
    """
    fecha_hoy = date.today()
    vencimiento_desde = fecha_hoy
    vencimiento_hasta = fecha_hoy + timedelta(days=dias_antes)

    filters = {
        "vencimiento_desde": vencimiento_desde,
        "vencimiento_hasta": vencimiento_hasta,
        "incluir_vencidas": False,
    }

    aplicar_filtros_por_corredor(filters, current_user)

    try:
        polizas = await poliza_crud.get_multi(db, **filters)
        for poliza in polizas:
            await enviar_notificacion(poliza, current_user)
    except Exception as e:
        logger.error(f"Error al notificar vencimientos: {e}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Error al notificar vencimientos"
        )

    return {"message": "Notificaciones enviadas correctamente"}


@router.post("/programar-verificacion-vencimientos/")
@require_permissions(["polizas_ver"])
async def programar_verificacion_vencimientos(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    dias_antes: int = Query(7, description="Días antes del vencimiento para notificar"),
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> Dict[str, str]:
    """
    Programa una tarea en segundo plano para verificar vencimientos y enviar notificaciones.
    """
    background_tasks.add_task(notificar_vencimientos, db, dias_antes, current_user)
    return {"message": "Tarea programada correctamente"}


@router.put("/configurar-alertas/", response_model=ConfiguracionAlertas)
@require_permissions(["polizas_ver"])
async def configurar_alertas(
    configuracion: ConfiguracionAlertas,
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> ConfiguracionAlertas:
    """
    Configura las preferencias de alertas para el usuario actual.
    """
    # Aquí puedes guardar la configuración en la base de datos
    current_user.configuracion_alertas = configuracion
    return configuracion


@router.post("/plantillas-notificacion/", response_model=PlantillaNotificacion)
@require_permissions(["polizas_ver"])
async def crear_plantilla_notificacion(
    plantilla: PlantillaNotificacion,
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> PlantillaNotificacion:
    """
    Crea o actualiza una plantilla de notificación.
    """
    # Aquí puedes guardar la plantilla en la base de datos
    return plantilla


# Endpoints existentes (sin cambios)
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
        description="Buscar pólizas que vencen en los próximos N días",
    ),
    numero_poliza: Optional[str] = None,
    tipo_seguro_id: Optional[int] = None,
    moneda_id: Optional[int] = None,
    suma_asegurada_min: Optional[float] = None,
    suma_asegurada_max: Optional[float] = None,
    prima_min: Optional[float] = None,
    prima_max: Optional[float] = None,
    cliente_nombre: Optional[str] = Query(
        None, description="Buscar por nombre del cliente"
    ),
    cliente_apellido: Optional[str] = Query(
        None, description="Buscar por apellido del cliente"
    ),
    tipo_duracion: Optional[TipoDuracion] = Query(
        None, description="Filtrar por tipo de duración"
    ),
    ordenar_por: Optional[str] = Query(
        None,
        description="Campo por el cual ordenar (ej: fecha_inicio, suma_asegurada, nombres, apellidos)",
    ),
    orden: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> List[Poliza]:
    """
    Recuperar pólizas con filtros opcionales.
    """
    if proximo_vencimiento is not None:
        vencimiento_desde = date.today()
        vencimiento_hasta = vencimiento_desde + timedelta(days=proximo_vencimiento)
        incluir_vencidas = False  # Forzar a False cuando se usa proximo_vencimiento

    validar_rango_fechas(vencimiento_desde, vencimiento_hasta)

    filters = {
        "cliente_id": cliente_id,
        "corredor_id": corredor_id,
        "estado": estado,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "vencimiento_desde": vencimiento_desde,
        "vencimiento_hasta": vencimiento_hasta,
        "incluir_vencidas": incluir_vencidas,
        "numero_poliza": numero_poliza,
        "tipo_seguro_id": tipo_seguro_id,
        "moneda_id": moneda_id,
        "suma_asegurada_min": suma_asegurada_min,
        "suma_asegurada_max": suma_asegurada_max,
        "prima_min": prima_min,
        "prima_max": prima_max,
        "cliente_nombre": cliente_nombre,
        "cliente_apellido": cliente_apellido,
        "tipo_duracion": tipo_duracion,
        "ordenar_por": ordenar_por,
        "orden": orden,
    }

    aplicar_filtros_por_corredor(filters, current_user)

    try:
        polizas = await poliza_crud.get_multi(db, skip=skip, limit=limit, **filters)
    except Exception as e:
        logger.error(f"Error al obtener pólizas: {e}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Error al obtener pólizas"
        )

    return polizas


# Resto de endpoints existentes (sin cambios)
@router.post("/", response_model=Poliza)
@require_permissions(["polizas_crear"])
async def create_poliza(
    *,
    db: AsyncSession = Depends(get_db),
    poliza_in: PolizaCreate,
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> Poliza:
    """
    Crear nueva póliza.
    """
    poliza = await poliza_crud.get_by_numero(db, numero_poliza=poliza_in.numero_poliza)
    if poliza:
        logger.error("Ya existe una póliza con este número")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Ya existe una póliza con este número",
        )

    if current_user.role == "corredor":
        if (
            poliza_in.corredor_id
            and poliza_in.corredor_id != current_user.corredor_numero
        ):
            logger.error("No puede crear pólizas para otros corredores")
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="No puede crear pólizas para otros corredores",
            )
        poliza_in.corredor_id = current_user.corredor_numero

    return await poliza_crud.create(db, obj_in=poliza_in)


@router.get("/{poliza_id}", response_model=PolizaDetalle)
@require_permissions(["polizas_ver"])
async def get_poliza(
    poliza_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> PolizaDetalle:
    """
    Obtener una póliza específica por ID.
    """
    poliza = await poliza_crud.get(db, id=poliza_id)
    if not poliza:
        logger.error("Póliza no encontrada")
        raise HTTPException(status_code=404, detail="Póliza no encontrada")

    validar_permisos_corredor(poliza, current_user, "ver")
    return poliza


@router.put("/{poliza_id}", response_model=Poliza)
@require_permissions(["polizas_editar"])
async def update_poliza(
    *,
    db: AsyncSession = Depends(get_db),
    poliza_id: int,
    poliza_in: PolizaUpdate,
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> Poliza:
    """
    Actualizar una póliza existente.
    """
    poliza = await poliza_crud.get(db, id=poliza_id)
    if not poliza:
        logger.error("Póliza no encontrada")
        raise HTTPException(status_code=404, detail="Póliza no encontrada")

    validar_permisos_corredor(poliza, current_user, "modificar")
    return await poliza_crud.update(db, db_obj=poliza, obj_in=poliza_in)


@router.delete("/{poliza_id}", response_model=Poliza)
@require_permissions(["polizas_eliminar"])
async def delete_poliza(
    *,
    db: AsyncSession = Depends(get_db),
    poliza_id: int,
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> Poliza:
    """
    Eliminar una póliza.
    """
    poliza = await poliza_crud.get(db, id=poliza_id)
    if not poliza:
        logger.error("Póliza no encontrada")
        raise HTTPException(status_code=404, detail="Póliza no encontrada")

    validar_permisos_corredor(poliza, current_user, "eliminar")
    return await poliza_crud.delete(db, id=poliza_id)


@router.get("/exportar/excel/")
@require_permissions(["polizas_ver"])
async def exportar_polizas_excel(
    db: AsyncSession = Depends(get_db),
    estado: Optional[str] = Query(
        "activa", description="Estado de las pólizas a incluir"
    ),
    fecha_inicio: Optional[date] = Query(
        None, description="Fecha de inicio para filtrar"
    ),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin para filtrar"),
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> StreamingResponse:
    """
    Exportar pólizas a un archivo Excel.
    """
    filters = {"estado": estado, "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
    aplicar_filtros_por_corredor(filters, current_user)

    polizas = await poliza_crud.get_multi(db, **filters)

    # Crear un libro de trabajo de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Pólizas"

    # Agregar encabezados
    ws.append(
        ["ID", "Número de Póliza", "Cliente", "Estado", "Suma Asegurada", "Prima"]
    )

    # Agregar datos de pólizas
    for poliza in polizas:
        ws.append(
            [
                poliza.id,
                poliza.numero_poliza,
                poliza.cliente_rel.nombres + " " + poliza.cliente_rel.apellidos,
                poliza.estado_poliza,
                poliza.suma_asegurada,
                poliza.prima,
            ]
        )

    # Guardar el archivo en memoria
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=polizas.xlsx"},
    )


@router.get("/exportar/pdf/")
@require_permissions(["polizas_ver"])
async def exportar_polizas_pdf(
    db: AsyncSession = Depends(get_db),
    estado: Optional[str] = Query(
        "activa", description="Estado de las pólizas a incluir"
    ),
    fecha_inicio: Optional[date] = Query(
        None, description="Fecha de inicio para filtrar"
    ),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin para filtrar"),
    current_user: UsuarioModel = Depends(get_current_active_user),
) -> StreamingResponse:
    """
    Exportar pólizas a un archivo PDF.
    """
    filters = {"estado": estado, "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
    aplicar_filtros_por_corredor(filters, current_user)

    polizas = await poliza_crud.get_multi(db, **filters)

    # Crear un archivo PDF en memoria
    output = BytesIO()
    p = canvas.Canvas(output, pagesize=letter)
    width, height = letter

    # Agregar encabezados
    p.drawString(100, height - 50, "ID")
    p.drawString(200, height - 50, "Número de Póliza")
    p.drawString(300, height - 50, "Cliente")
    p.drawString(400, height - 50, "Estado")
    p.drawString(500, height - 50, "Suma Asegurada")
    p.drawString(600, height - 50, "Prima")

    # Agregar datos de pólizas
    y = height - 70
    for poliza in polizas:
        p.drawString(100, y, str(poliza.id))
        p.drawString(200, y, poliza.numero_poliza)
        p.drawString(
            300, y, f"{poliza.cliente_rel.nombres} {poliza.cliente_rel.apellidos}"
        )
        p.drawString(400, y, poliza.estado_poliza)
        p.drawString(500, y, str(poliza.suma_asegurada))
        p.drawString(600, y, str(poliza.prima))
        y -= 20  # Espacio entre filas

    p.showPage()
    p.save()
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=polizas.pdf"},
    )
