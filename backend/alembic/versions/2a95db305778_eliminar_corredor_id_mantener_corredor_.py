"""eliminar_corredor_id_mantener_corredor_numero

Revision ID: 2a95db305778
Revises: 02c253a26b87
Create Date: 2025-02-10 21:55:23.744078

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2a95db305778"
down_revision: Union[str, None] = "02c253a26b87"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Primero eliminamos la foreign key de corredor_id
    op.drop_constraint(
        "fk_usuarios_corredor_id_corredores", "usuarios", type_="foreignkey"
    )

    # Luego eliminamos la columna corredor_id
    op.drop_column("usuarios", "corredor_id")


def downgrade() -> None:
    # Recreamos la columna corredor_id
    op.add_column("usuarios", sa.Column("corredor_id", sa.Integer(), nullable=True))

    # Recreamos la foreign key
    op.create_foreign_key(
        "fk_usuarios_corredor_id_corredores",
        "usuarios",
        "corredores",
        ["corredor_id"],
        ["numero"],
    )
