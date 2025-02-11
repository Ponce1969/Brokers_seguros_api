"""agregar_secuencia_cliente_numero

Revision ID: d1a48cbb86c
Revises: c1a48cbb86c
Create Date: 2025-02-11 01:26:23.744078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1a48cbb86c'
down_revision: Union[str, None] = 'c1a48cbb86c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear la secuencia
    op.execute("CREATE SEQUENCE IF NOT EXISTS cliente_numero_seq START 1")
    
    # Asegurarnos de que la columna numero_cliente use la secuencia
    op.execute("""
        ALTER TABLE clientes 
        ALTER COLUMN numero_cliente 
        SET DEFAULT nextval('cliente_numero_seq')
    """)


def downgrade() -> None:
    # Remover el valor por defecto de la columna
    op.execute("""
        ALTER TABLE clientes 
        ALTER COLUMN numero_cliente 
        DROP DEFAULT
    """)
    
    # Eliminar la secuencia
    op.execute("DROP SEQUENCE IF EXISTS cliente_numero_seq")
