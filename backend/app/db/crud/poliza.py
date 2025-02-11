from datetime import date, datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models.movimiento_vigencia import MovimientoVigencia, TipoDuracion
from app.db.models.cliente import Cliente
from app.schemas.poliza import PolizaCreate, PolizaUpdate


class CRUDPoliza:
    async def get(self, db: AsyncSession, id: int) -> Optional[MovimientoVigencia]:
        """Obtener una póliza por su ID."""
        result = await db.execute(
            select(MovimientoVigencia)
            .filter(MovimientoVigencia.id == id)
            .options(
                joinedload(MovimientoVigencia.cliente_rel),
                joinedload(MovimientoVigencia.corredor_rel),
                joinedload(MovimientoVigencia.tipo_seguro_rel),
                joinedload(MovimientoVigencia.moneda_rel)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_numero(
        self, db: AsyncSession, numero_poliza: str
    ) -> Optional[MovimientoVigencia]:
        """Obtener una póliza por su número."""
        result = await db.execute(
            select(MovimientoVigencia).filter(MovimientoVigencia.numero_poliza == numero_poliza)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        cliente_id: Optional[UUID] = None,
        corredor_id: Optional[int] = None,
        estado: Optional[str] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        vencimiento_desde: Optional[date] = None,
        vencimiento_hasta: Optional[date] = None,
        incluir_vencidas: bool = False,
        numero_poliza: Optional[str] = None,
        tipo_seguro_id: Optional[int] = None,
        moneda_id: Optional[int] = None,
        suma_asegurada_min: Optional[float] = None,
        suma_asegurada_max: Optional[float] = None,
        prima_min: Optional[float] = None,
        prima_max: Optional[float] = None,
        cliente_nombre: Optional[str] = None,
        cliente_apellido: Optional[str] = None,
        tipo_duracion: Optional[TipoDuracion] = None,
        ordenar_por: Optional[str] = None,
        orden: Optional[str] = "asc"
    ) -> List[MovimientoVigencia]:
        """
        Obtener múltiples pólizas con filtros opcionales.
        """
        # Comenzamos con un join entre pólizas y clientes
        query = select(MovimientoVigencia).join(
            Cliente,
            MovimientoVigencia.cliente_id == Cliente.id
        )
        
        # Aplicar filtros si se proporcionan
        if cliente_id:
            query = query.filter(MovimientoVigencia.cliente_id == cliente_id)
        if corredor_id:
            query = query.filter(MovimientoVigencia.corredor_id == corredor_id)
        if estado:
            query = query.filter(MovimientoVigencia.estado_poliza == estado)
        if fecha_inicio and fecha_fin:
            query = query.filter(MovimientoVigencia.fecha_inicio >= fecha_inicio)
            query = query.filter(MovimientoVigencia.fecha_inicio <= fecha_fin)
        
        # Filtros de vencimiento
        if vencimiento_desde or vencimiento_hasta:
            # Aplicar filtros de rango de fechas
            if vencimiento_desde:
                query = query.filter(MovimientoVigencia.fecha_vencimiento >= vencimiento_desde)
            if vencimiento_hasta:
                query = query.filter(MovimientoVigencia.fecha_vencimiento <= vencimiento_hasta)
            
            # Si no incluimos vencidas, filtramos por estado activa
            if not incluir_vencidas:
                query = query.filter(MovimientoVigencia.estado_poliza == "activa")
        
        if numero_poliza:
            query = query.filter(MovimientoVigencia.numero_poliza.ilike(f"%{numero_poliza}%"))
        if tipo_seguro_id:
            query = query.filter(MovimientoVigencia.tipo_seguro_id == tipo_seguro_id)
        if moneda_id:
            query = query.filter(MovimientoVigencia.moneda_id == moneda_id)
        if suma_asegurada_min is not None:
            query = query.filter(MovimientoVigencia.suma_asegurada >= suma_asegurada_min)
        if suma_asegurada_max is not None:
            query = query.filter(MovimientoVigencia.suma_asegurada <= suma_asegurada_max)
        if prima_min is not None:
            query = query.filter(MovimientoVigencia.prima >= prima_min)
        if prima_max is not None:
            query = query.filter(MovimientoVigencia.prima <= prima_max)
        
        # Filtro por tipo de duración
        if tipo_duracion:
            query = query.filter(MovimientoVigencia.tipo_duracion == tipo_duracion)
        
        # Filtros de cliente
        if cliente_nombre:
            query = query.filter(Cliente.nombres.ilike(f"%{cliente_nombre}%"))
        if cliente_apellido:
            query = query.filter(Cliente.apellidos.ilike(f"%{cliente_apellido}%"))

        # Aplicar ordenamiento
        if ordenar_por:
            # Si el ordenamiento es por campos del cliente
            if ordenar_por in ["nombres", "apellidos"]:
                column = getattr(Cliente, ordenar_por)
            else:
                column = getattr(MovimientoVigencia, ordenar_por, None)
            
            if column is not None:
                if orden.lower() == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        
        # Cargar relaciones
        query = query.options(
            joinedload(MovimientoVigencia.cliente_rel),
            joinedload(MovimientoVigencia.corredor_rel),
            joinedload(MovimientoVigencia.tipo_seguro_rel),
            joinedload(MovimientoVigencia.moneda_rel)
        )
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: PolizaCreate
    ) -> MovimientoVigencia:
        """Crear una nueva póliza."""
        db_obj = MovimientoVigencia(
            cliente_id=obj_in.cliente_id,
            corredor_id=obj_in.corredor_id,
            tipo_seguro_id=obj_in.tipo_seguro_id,
            carpeta=obj_in.carpeta,
            numero_poliza=obj_in.numero_poliza,
            endoso=obj_in.endoso,
            fecha_inicio=obj_in.fecha_inicio,
            fecha_vencimiento=obj_in.fecha_vencimiento,
            fecha_emision=obj_in.fecha_emision,
            estado_poliza=obj_in.estado_poliza,
            forma_pago=obj_in.forma_pago,
            tipo_endoso=obj_in.tipo_endoso,
            moneda_id=obj_in.moneda_id,
            suma_asegurada=obj_in.suma_asegurada,
            prima=obj_in.prima,
            comision=obj_in.comision,
            cuotas=obj_in.cuotas,
            observaciones=obj_in.observaciones,
            tipo_duracion=TipoDuracion(obj_in.tipo_duracion)
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: MovimientoVigencia,
        obj_in: PolizaUpdate
    ) -> MovimientoVigencia:
        """Actualizar una póliza existente."""
        update_data = obj_in.dict(exclude_unset=True)
        
        # Convertir tipo_duracion a enum si está presente
        if 'tipo_duracion' in update_data:
            update_data['tipo_duracion'] = TipoDuracion(update_data['tipo_duracion'])
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: int) -> MovimientoVigencia:
        """Eliminar una póliza."""
        obj = await self.get(db=db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj


poliza_crud = CRUDPoliza()
