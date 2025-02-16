from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ....core import security
from ....core.config import settings
from ....db.crud.usuario import usuario_crud
from ....db.session import get_db
from ....schemas.token import Token

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    usuario = await usuario_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not usuario:
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")
    elif not usuario.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            usuario.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
