from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.corredor import Corredor
from app.db.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate
from app.core.security import get_password_hash
from datetime import datetime, timezone

class CRUDCorredor:
    async def create_corredor_with_user(
        self,
        db: AsyncSession,
        *,
        numero: int,
        nombres: str,
        apellidos: str,
        documento: str,
        direccion: str,
        localidad: str,
        telefonos: str,
        movil: Optional[str],
        mail: str,
        password: str,
        is_superuser: bool = False,
        role: str = "corredor",
        observaciones: Optional[str] = None
    ) -> tuple[Corredor, Usuario]:
        """
        Crea un corredor y su usuario asociado en una sola operación.
        """
        # Crear el corredor
        corredor = Corredor(
            numero=numero,
            nombres=nombres,
            apellidos=apellidos,
            documento=documento,
            direccion=direccion,
            localidad=localidad,
            telefonos=telefonos,
            movil=movil,
            mail=mail,
            observaciones=observaciones,
            fecha_alta=datetime.now(timezone.utc)
        )
        
        db.add(corredor)
        await db.flush()  # Asegurar que el corredor se guarde y tenga un ID
        
        # Crear el usuario asociado
        usuario = Usuario(
            nombre=nombres,
            apellido=apellidos,
            email=mail,
            username=mail,  # Usar el email como username por defecto
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=is_superuser,
            role=role,
            corredor_numero=numero,
            telefono=telefonos
        )
        
        db.add(usuario)
        await db.commit()
        await db.refresh(corredor)
        await db.refresh(usuario)
        
        return corredor, usuario

corredor_crud = CRUDCorredor()
