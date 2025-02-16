# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.db.models import (  # noqa
    TipoDocumento,
    Moneda,
    TipoSeguro,
    Aseguradora,
    Corredor,
    Usuario,
    Cliente,
    ClienteCorredor,
    MovimientoVigencia,
)
