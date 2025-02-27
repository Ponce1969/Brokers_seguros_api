"""
Modelo de datos para MovimientoVigencia
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass
class MovimientoVigencia:
    """
    Modelo de datos para representar un Movimiento de Vigencia
    """

    id: int
    cliente_id: UUID
    numero_poliza: str
    fecha_inicio: date
    fecha_vencimiento: date
    suma_asegurada: Decimal
    prima: Decimal

    # Campos opcionales
    corredor_id: Optional[int] = None
    tipo_seguro_id: Optional[int] = None
    carpeta: Optional[str] = None
    endoso: Optional[str] = None
    fecha_emision: Optional[date] = None
    estado_poliza: str = "activa"
    forma_pago: Optional[str] = None
    tipo_endoso: Optional[str] = None
    moneda_id: Optional[int] = None
    comision: Optional[Decimal] = None
    cuotas: Optional[int] = None
    observaciones: Optional[str] = None

    # Datos relacionados (se llenarán cuando sea necesario)
    cliente_nombre: Optional[str] = None
    corredor_nombre: Optional[str] = None
    tipo_seguro_nombre: Optional[str] = None
    moneda_nombre: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "MovimientoVigencia":
        """
        Crea una instancia de MovimientoVigencia desde un diccionario

        Args:
            data: Diccionario con los datos del movimiento

        Returns:
            MovimientoVigencia: Nueva instancia de MovimientoVigencia
        """
        # Convertir campos de fecha
        fecha_inicio = (
            date.fromisoformat(data["fecha_inicio"])
            if data.get("fecha_inicio")
            else None
        )
        fecha_vencimiento = (
            date.fromisoformat(data["fecha_vencimiento"])
            if data.get("fecha_vencimiento")
            else None
        )
        fecha_emision = (
            date.fromisoformat(data["fecha_emision"])
            if data.get("fecha_emision")
            else None
        )

        # Convertir campos decimales
        suma_asegurada = (
            Decimal(str(data["suma_asegurada"]))
            if data.get("suma_asegurada") is not None
            else Decimal("0")
        )
        prima = (
            Decimal(str(data["prima"]))
            if data.get("prima") is not None
            else Decimal("0")
        )
        comision = (
            Decimal(str(data["comision"])) if data.get("comision") is not None else None
        )

        return cls(
            id=data.get("id", 0),
            cliente_id=(
                UUID(data["cliente_id"])
                if isinstance(data.get("cliente_id"), str)
                else data.get("cliente_id")
            ),
            corredor_id=data.get("corredor_id"),
            tipo_seguro_id=data.get("tipo_seguro_id"),
            carpeta=data.get("carpeta"),
            numero_poliza=data.get("numero_poliza", ""),
            endoso=data.get("endoso"),
            fecha_inicio=fecha_inicio,
            fecha_vencimiento=fecha_vencimiento,
            fecha_emision=fecha_emision,
            estado_poliza=data.get("estado_poliza", "activa"),
            forma_pago=data.get("forma_pago"),
            tipo_endoso=data.get("tipo_endoso"),
            moneda_id=data.get("moneda_id"),
            suma_asegurada=suma_asegurada,
            prima=prima,
            comision=comision,
            cuotas=data.get("cuotas"),
            observaciones=data.get("observaciones"),
            # Datos relacionados
            cliente_nombre=data.get("cliente_nombre"),
            corredor_nombre=data.get("corredor_nombre"),
            tipo_seguro_nombre=data.get("tipo_seguro_nombre"),
            moneda_nombre=data.get("moneda_nombre"),
        )

    def to_dict(self) -> dict:
        """
        Convierte la instancia a un diccionario

        Returns:
            dict: Diccionario con los datos del movimiento
        """
        return {
            "id": self.id,
            "cliente_id": str(self.cliente_id) if self.cliente_id else None,
            "corredor_id": self.corredor_id,
            "tipo_seguro_id": self.tipo_seguro_id,
            "carpeta": self.carpeta,
            "numero_poliza": self.numero_poliza,
            "endoso": self.endoso,
            "fecha_inicio": (
                self.fecha_inicio.isoformat() if self.fecha_inicio else None
            ),
            "fecha_vencimiento": (
                self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None
            ),
            "fecha_emision": (
                self.fecha_emision.isoformat() if self.fecha_emision else None
            ),
            "estado_poliza": self.estado_poliza,
            "forma_pago": self.forma_pago,
            "tipo_endoso": self.tipo_endoso,
            "moneda_id": self.moneda_id,
            "suma_asegurada": str(self.suma_asegurada),
            "prima": str(self.prima),
            "comision": str(self.comision) if self.comision is not None else None,
            "cuotas": self.cuotas,
            "observaciones": self.observaciones,
            # Datos relacionados
            "cliente_nombre": self.cliente_nombre,
            "corredor_nombre": self.corredor_nombre,
            "tipo_seguro_nombre": self.tipo_seguro_nombre,
            "moneda_nombre": self.moneda_nombre,
        }

    @property
    def estado_display(self) -> str:
        """Devuelve el estado de la póliza en formato legible"""
        return self.estado_poliza.capitalize()

    @property
    def vigente(self) -> bool:
        """Indica si la póliza está vigente"""
        hoy = date.today()
        return (
            self.fecha_inicio <= hoy <= self.fecha_vencimiento
            and self.estado_poliza.lower() == "activa"
        )
