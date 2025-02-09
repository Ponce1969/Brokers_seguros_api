# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.db.models.aseguradora import Aseguradora  # noqa
from app.db.models.cliente import Cliente  # noqa
from app.db.models.cliente_corredor import ClienteCorredor  # noqa
from app.db.models.corredor import Corredor  # noqa
from app.db.models.moneda import Moneda  # noqa
from app.db.models.movimiento_vigencia import MovimientoVigencia  # noqa
from app.db.models.tipo_documento import TipoDocumento  # noqa
from app.db.models.tipo_seguro import TipoSeguro  # noqa
from app.db.models.usuario import Usuario  # noqa
