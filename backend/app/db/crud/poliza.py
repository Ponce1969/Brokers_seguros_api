from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models.cliente import Cliente
from app.db.models.movimiento_vigencia import MovimientoVigencia, TipoDuracion
from app.schemas.poliza import PolizaCreate, PolizaUpdate


class CRUDPoliza:
    """Clase para manejar operaciones CRUD de pólizas."""

    def _apply_filters(self, query, **filters):
        """Aplica filtros opcionales a la consulta."""
        if filters.get("cliente_id"):
            query = query.filter(MovimientoVigencia.cliente_id == filters["cliente_id"])
        if filters.get("corredor_id"):
            query = query.filter(
                MovimientoVigencia.corredor_id == filters["corredor_id"]
            )
        if filters.get("estado"):
            query = query.filter(MovimientoVigencia.estado_poliza == filters["estado"])
        if filters.get("fecha_inicio") and filters.get("fecha_fin"):
            query = query.filter(
                MovimientoVigencia.fecha_inicio.between(
                    filters["fecha_inicio"], filters["fecha_fin"]
                )
            )
        if filters.get("numero_poliza"):
            query = query.filter(
                MovimientoVigencia.numero_poliza.ilike(f"%{filters['numero_poliza']}%")
            )
        return query

    def _joined_load_options(self):
        """Opciones de carga para relaciones relacionadas con MovimientoVigencia."""
        return (
            joinedload(MovimientoVigencia.cliente_rel),
            joinedload(MovimientoVigencia.corredor_rel),
            joinedload(MovimientoVigencia.tipo_seguro_rel),
            joinedload(MovimientoVigencia.moneda_rel),
        )

    async def get(self, db: AsyncSession, id: int) -> Optional[MovimientoVigencia]:
        """Obtener una póliza por su ID."""
        result = await db.execute(
            select(MovimientoVigencia)
            .filter(MovimientoVigencia.id == id)
            .options(*self._joined_load_options())
        )
        return result.scalar_one_or_none()

    async def get_by_numero(
        self, db: AsyncSession, numero_poliza: str
    ) -> Optional[MovimientoVigencia]:
        """Obtener una póliza por su número."""
        result = await db.execute(
            select(MovimientoVigencia).filter(
                MovimientoVigencia.numero_poliza == numero_poliza
            )
        )
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, **filters) -> List[MovimientoVigencia]:
        """Obtener múltiples pólizas con filtros opcionales."""
        query = select(MovimientoVigencia).join(
            Cliente, MovimientoVigencia.cliente_id == Cliente.id
        )
        query = self._apply_filters(query, **filters)
        query = (
            query.options(*self._joined_load_options())
            .offset(filters.get("skip", 0))
            .limit(filters.get("limit", 100))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: PolizaCreate
    ) -> MovimientoVigencia:
        """Crear una nueva póliza."""
        db_obj = MovimientoVigencia(**obj_in.dict())
        db_obj.tipo_duracion = TipoDuracion(obj_in.tipo_duracion)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: MovimientoVigencia, obj_in: PolizaUpdate
    ) -> MovimientoVigencia:
        """Actualizar una póliza existente."""
        update_data = obj_in.dict(exclude_unset=True)
        if "tipo_duracion" in update_data:
            update_data["tipo_duracion"] = TipoDuracion(update_data["tipo_duracion"])
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self, db: AsyncSession, *, id: int
    ) -> Optional[MovimientoVigencia]:
        """Eliminar una póliza por ID."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def get_estadisticas(
        self, db: AsyncSession, **filters
    ) -> Tuple[List[Dict], float, float, int]:
        """Obtener estadísticas de pólizas agrupadas por tipo de duración."""
        query = select(
            MovimientoVigencia.tipo_duracion,
            func.count(MovimientoVigencia.id).label("cantidad_polizas"),
            func.sum(MovimientoVigencia.suma_asegurada).label("suma_asegurada_total"),
            func.sum(MovimientoVigencia.prima).label("prima_total"),
        ).group_by(MovimientoVigencia.tipo_duracion)
        query = self._apply_filters(query, **filters)
        result = await db.execute(query)
        stats_by_duration = result.all()
        totals_query = select(
            func.count(MovimientoVigencia.id).label("total_polizas"),
            func.coalesce(func.sum(MovimientoVigencia.suma_asegurada), 0).label(
                "suma_asegurada_total"
            ),
            func.coalesce(func.sum(MovimientoVigencia.prima), 0).label("prima_total"),
        )
        totals_query = self._apply_filters(totals_query, **filters)
        totals_result = await db.execute(totals_query)
        totals = totals_result.first()
        return (
            stats_by_duration,
            totals.suma_asegurada_total,
            totals.prima_total,
            totals.total_polizas,
        )


poliza_crud = CRUDPoliza()
