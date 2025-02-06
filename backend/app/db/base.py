# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base
from app.db.models.aseguradora import Aseguradora
from app.db.models.cliente import Cliente
from app.db.models.cliente_corredor import ClienteCorredor
from app.db.models.corredor import Corredor
from app.db.models.moneda import Moneda
from app.db.models.movimiento_vigencia import MovimientoVigencia
from app.db.models.tipo_documento import TipoDocumento
from app.db.models.tipo_seguro import TipoSeguro
from app.db.models.usuario import Usuario
