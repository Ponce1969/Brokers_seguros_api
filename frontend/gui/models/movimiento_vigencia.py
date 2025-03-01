"""
Modelo de datos para MovimientoVigencia
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from uuid import UUID
import logging

# Configurar logging
logger = logging.getLogger(__name__)


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
    corredor_id: Optional[int] = field(default=None)
    tipo_seguro_id: Optional[int] = field(default=None)
    carpeta: Optional[str] = field(default=None)
    endoso: Optional[str] = field(default=None)
    fecha_emision: Optional[date] = field(default=None)
    estado_poliza: str = field(default="activa")
    forma_pago: Optional[str] = field(default=None)
    tipo_endoso: Optional[str] = field(default=None)
    moneda_id: Optional[int] = field(default=None)
    comision: Optional[Decimal] = field(default=None)
    cuotas: Optional[int] = field(default=None)
    observaciones: Optional[str] = field(default=None)

    # Datos relacionados (se llenarán cuando sea necesario)
    cliente_nombre: Optional[str] = field(default=None)
    corredor_nombre: Optional[str] = field(default=None)
    tipo_seguro_nombre: Optional[str] = field(default=None)
    moneda_nombre: Optional[str] = field(default=None)

    @classmethod
    def from_dict(cls, data: dict) -> "MovimientoVigencia":
        """
        Crea una instancia de MovimientoVigencia desde un diccionario

        Args:
            data: Diccionario con los datos del movimiento

        Returns:
            MovimientoVigencia: Nueva instancia de MovimientoVigencia
        """
        try:
            # Convertir campos de fecha
            fecha_inicio = None
            fecha_vencimiento = None
            fecha_emision = None
            
            if data.get("fecha_inicio"):
                try:
                    fecha_inicio = date.fromisoformat(data["fecha_inicio"])
                except ValueError:
                    logger.error(f"Error al procesar fecha_inicio: {data['fecha_inicio']}")
                    raise ValueError(f"Formato de fecha_inicio inválido: {data['fecha_inicio']}")
            
            if data.get("fecha_vencimiento"):
                try:
                    fecha_vencimiento = date.fromisoformat(data["fecha_vencimiento"])
                except ValueError:
                    logger.error(f"Error al procesar fecha_vencimiento: {data['fecha_vencimiento']}")
                    raise ValueError(f"Formato de fecha_vencimiento inválido: {data['fecha_vencimiento']}")
            
            if data.get("fecha_emision"):
                try:
                    fecha_emision = date.fromisoformat(data["fecha_emision"])
                except ValueError:
                    logger.error(f"Error al procesar fecha_emision: {data['fecha_emision']}")
                    raise ValueError(f"Formato de fecha_emision inválido: {data['fecha_emision']}")

            # Validar fechas coherentes
            if fecha_inicio and fecha_vencimiento and fecha_inicio > fecha_vencimiento:
                raise ValueError("La fecha de inicio no puede ser posterior a la fecha de vencimiento")

            # Convertir campos decimales con manejo de precisión
            suma_asegurada = Decimal("0")
            if data.get("suma_asegurada") is not None:
                try:
                    suma_asegurada = Decimal(str(data["suma_asegurada"])).quantize(Decimal("0.01"))
                except (ValueError, TypeError):
                    logger.error(f"Error al procesar suma_asegurada: {data['suma_asegurada']}")
                    raise ValueError(f"Valor inválido para suma_asegurada: {data['suma_asegurada']}")
            
            prima = Decimal("0")
            if data.get("prima") is not None:
                try:
                    prima = Decimal(str(data["prima"])).quantize(Decimal("0.01"))
                except (ValueError, TypeError):
                    logger.error(f"Error al procesar prima: {data['prima']}")
                    raise ValueError(f"Valor inválido para prima: {data['prima']}")
            
            comision = None
            if data.get("comision") is not None:
                try:
                    comision = Decimal(str(data["comision"])).quantize(Decimal("0.01"))
                except (ValueError, TypeError):
                    logger.error(f"Error al procesar comision: {data['comision']}")
                    raise ValueError(f"Valor inválido para comision: {data['comision']}")

            # Validar UUID del cliente
            cliente_id = None
            if data.get("cliente_id"):
                try:
                    if isinstance(data["cliente_id"], str):
                        cliente_id = UUID(data["cliente_id"])
                    else:
                        cliente_id = data["cliente_id"]
                except ValueError:
                    logger.error(f"Error al procesar cliente_id: {data['cliente_id']}")
                    raise ValueError(f"UUID inválido para cliente_id: {data['cliente_id']}")
            else:
                raise ValueError("cliente_id es obligatorio")

            return cls(
                id=data.get("id", 0),
                cliente_id=cliente_id,
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
        except Exception as e:
            logger.error(f"Error al crear MovimientoVigencia desde diccionario: {e}")
            logger.error(f"Datos recibidos: {data}")
            raise

    def to_dict(self) -> dict:
        """
        Convierte la instancia a un diccionario

        Returns:
            dict: Diccionario con los datos del movimiento
        """
        # Formatear decimales con precisión de 2 decimales
        suma_asegurada_str = str(self.suma_asegurada.quantize(Decimal("0.01"))) if self.suma_asegurada is not None else None
        prima_str = str(self.prima.quantize(Decimal("0.01"))) if self.prima is not None else None
        comision_str = str(self.comision.quantize(Decimal("0.01"))) if self.comision is not None else None
        
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
            "suma_asegurada": suma_asegurada_str,
            "prima": prima_str,
            "comision": comision_str,
            "cuotas": self.cuotas,
            "observaciones": self.observaciones,
            # Datos relacionados
            "cliente_nombre": self.cliente_nombre,
            "corredor_nombre": self.corredor_nombre,
            "tipo_seguro_nombre": self.tipo_seguro_nombre,
            "moneda_nombre": self.moneda_nombre,
        }
    
    def _parse_fecha(self, valor: str) -> Optional[date]:
        """
        Parsea una cadena de texto a un objeto date.
        
        Args:
            valor: Cadena de texto en formato 'YYYY-MM-DD'
            
        Returns:
            date: Objeto date o None si hubo un error
            
        Raises:
            ValueError: Si el formato de la fecha es inválido
        """
        if not valor:
            return None
            
        try:
            return date.fromisoformat(valor)
        except ValueError:
            logger.error(f"Error al convertir fecha: {valor}")
            raise ValueError(f"Formato de fecha inválido: {valor}")
    
    def _parse_decimal(self, valor: Any) -> Optional[Decimal]:
        """
        Convierte un valor a Decimal con precisión de 2 decimales.
        
        Args:
            valor: Valor a convertir (str, int, float)
            
        Returns:
            Decimal: Valor convertido a Decimal con precisión de 2 decimales o None
            
        Raises:
            ValueError: Si el valor no puede ser convertido a Decimal
        """
        if valor is None:
            return None
            
        try:
            return Decimal(str(valor)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError, TypeError):
            logger.error(f"Error al convertir a Decimal: {valor}")
            raise ValueError(f"Valor inválido para conversión a Decimal: {valor}")
    
    def _parse_uuid(self, valor: Any) -> Optional[UUID]:
        """
        Convierte un valor a UUID.
        
        Args:
            valor: Valor a convertir (str, UUID)
            
        Returns:
            UUID: Valor convertido a UUID o None
            
        Raises:
            ValueError: Si el valor no puede ser convertido a UUID
        """
        if valor is None:
            return None
            
        if isinstance(valor, UUID):
            return valor
            
        try:
            return UUID(str(valor))
        except (ValueError, TypeError):
            logger.error(f"Error al convertir a UUID: {valor}")
            raise ValueError(f"Valor inválido para conversión a UUID: {valor}")

    def actualizar(self, datos: dict) -> None:
        """
        Actualiza los datos del movimiento con validación de tipos.

        Args:
            datos: Diccionario con los datos a actualizar
        """
        for campo, valor in datos.items():
            if hasattr(self, campo):
                try:
                    # Campos de fecha
                    if campo in ["fecha_inicio", "fecha_vencimiento", "fecha_emision"]:
                        if valor is not None:
                            valor = self._parse_fecha(valor) if isinstance(valor, str) else valor
                    
                    # Campos numéricos enteros
                    elif campo in ["id", "corredor_id", "tipo_seguro_id", "moneda_id", "cuotas"]:
                        if valor is not None and not isinstance(valor, int):
                            try:
                                valor = int(valor)
                            except (ValueError, TypeError):
                                logger.warning(f"Se esperaba un int para {campo}, pero se recibió {type(valor)}")
                                continue
                    
                    # Campos decimales
                    elif campo in ["suma_asegurada", "prima", "comision"]:
                        if valor is not None:
                            valor = self._parse_decimal(valor)
                    
                    # Campo UUID
                    elif campo == "cliente_id" and valor is not None:
                        valor = self._parse_uuid(valor)
                    
                    # Asignar el valor
                    setattr(self, campo, valor)
                    
                except Exception as e:
                    logger.error(f"Error al actualizar campo '{campo}': {e}")
                    raise
        
        # Validar coherencia de fechas después de actualizar
        if self.fecha_inicio and self.fecha_vencimiento and self.fecha_inicio > self.fecha_vencimiento:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de vencimiento")

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
