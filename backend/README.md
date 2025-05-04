# Backend BrokerSeguros

## Historial de Migraciones y Cambios Técnicos - 2025-05-01

**Resumen de hitos y acciones realizadas el 1 de mayo de 2025 en el proyecto BrokerSeguros:**

1. Se recreó y activó el entorno virtual `.venv` en backend, reinstalando todas las dependencias desde requirements.txt.
2. Se corrigieron importaciones de UUID en modelos para compatibilidad con SQLAlchemy 2.x y PostgreSQL.
3. Se resolvieron problemas de conexión cambiando el host de la base de datos a `localhost` para desarrollo local.
4. Se sincronizó el historial de migraciones Alembic con la base de datos existente usando `alembic stamp head`.
5. Se generó y aplicó una migración Alembic para borrado en cascada en la relación clientes-corredores.
6. Se eliminaron clientes de prueba desde la API para dejar la base limpia para pruebas funcionales.
7. Se realizó commit profesional de todos los cambios relevantes, incluyendo código, migraciones y utilidades frontend.

**Estado actual:** El entorno está listo y versionado, con la base y los modelos sincronizados, y la lógica de asociación cliente-corredor lista para pruebas y desarrollo.

---

## Instrucciones de uso de los endpoints principales

### Autenticación

La mayoría de los endpoints requieren autenticación mediante JWT. Obtén un token usando el endpoint de login:

```
POST /api/v1/login/access-token
{
  "username": "admin@brokerseguros.com",
  "password": "<tu-contraseña>"
}
```

El token debe incluirse en el header:
```
Authorization: Bearer <token>
```

### Crear un cliente

```
POST /api/v1/clientes/
Content-Type: application/json
Authorization: Bearer <token>
{
  "nombres": "Juan",
  "apellidos": "Pérez",
  "tipo_documento_id": 1,
  "numero_documento": "12345678",
  "fecha_nacimiento": "1990-01-01",
  "direccion": "Calle Falsa 123",
  "localidad": "Montevideo",
  "telefonos": "27110000",
  "movil": "099123456",
  "mail": "juan.perez@example.com",
  "observaciones": "Cliente de prueba"
}
```

### Consultar todos los clientes

```
GET /api/v1/clientes/
Authorization: Bearer <token>
```

### Consultar un cliente por ID

```
GET /api/v1/clientes/{cliente_id}
Authorization: Bearer <token>
```

### Borrar un cliente por ID

```
DELETE /api/v1/clientes/{cliente_id}
Authorization: Bearer <token>
```

- El parámetro `cliente_id` es el UUID del cliente (campo `id` en la respuesta de consulta).
- El borrado es en cascada: elimina también las relaciones en clientes_corredores.

### Notas adicionales
- Los endpoints siguen la convención REST y devuelven errores claros en caso de fallos de validación o integridad.
- Para más endpoints y detalles, consulta la documentación Swagger en `/docs` o `/redoc`.

## Instalación y configuración rápida

1. **Clona el repositorio y entra al backend:**
   ```bash
   git clone <repo_url>
   cd Brokerseguros/backend
   ```
2. **Crea y activa el entorno virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Instala las dependencias:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. **Configura variables de entorno:**
   - Copia y edita el archivo `.env` según tus necesidades.
5. **Ejecuta migraciones Alembic:**
   ```bash
   alembic upgrade head
   ```
6. **Inicia el servidor:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Estructura de carpetas relevante

- `app/`              - Código fuente principal (API, modelos, lógica)
- `alembic/`           - Migraciones de base de datos
- `tests/`             - Pruebas automáticas (si existen)
- `.env`               - Variables de entorno (no versionar en producción)

## Principales endpoints REST

### Autenticación
- `POST /api/v1/login/access-token` — Obtiene un JWT para autenticación

### Clientes
- `POST /api/v1/clientes/` — Crea cliente y lo asocia automáticamente al corredor creador
- `GET /api/v1/clientes/` — Lista todos los clientes
- `GET /api/v1/clientes/{cliente_id}` — Detalle de cliente
- `DELETE /api/v1/clientes/{cliente_id}` — Elimina cliente (borrado en cascada)

### Corredores
- `GET /api/v1/corredores/` — Lista corredores
- `GET /api/v1/corredores/{corredor_id}/clientes` — Clientes asociados a un corredor

### Pólizas
- `GET /api/v1/polizas/` — Lista pólizas
- `POST /api/v1/polizas/` — Crea póliza
- `DELETE /api/v1/polizas/{poliza_id}` — Elimina póliza

### Otros recursos
- `GET /api/v1/aseguradoras/` — Lista aseguradoras
- `GET /api/v1/tipos_documento/` — Tipos de documento válidos

## Ejemplo de autenticación y uso

```bash
# Autenticación
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@brokerseguros.com", "password": "<tu-contraseña>"}'

# Crear cliente
curl -X POST "http://localhost:8000/api/v1/clientes/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombres": "Juan",
    "apellidos": "Pérez",
    "tipo_documento_id": 1,
    "numero_documento": "12345678",
    "fecha_nacimiento": "1990-01-01",
    "direccion": "Calle Falsa 123",
    "localidad": "Montevideo",
    "telefonos": "27110000",
    "movil": "099123456",
    "mail": "juan.perez@example.com",
    "observaciones": "Cliente de prueba"
  }'

# Borrar cliente
curl -X DELETE "http://localhost:8000/api/v1/clientes/<cliente_id>" \
  -H "Authorization: Bearer <token>"
```

## Migraciones Alembic
- Para generar una nueva migración:
  ```bash
  alembic revision --autogenerate -m "mensaje descriptivo"
  ```
- Para aplicar migraciones:
  ```bash
  alembic upgrade head
  ```
- Si la base ya tiene tablas pero no historial Alembic, usa:
  ```bash
  alembic stamp head
  ```

## Documentación interactiva
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Notas importantes
- Los endpoints requieren autenticación JWT.
- El borrado de clientes es en cascada y elimina asociaciones.
- Los modelos usan UUID como identificadores principales.
- La lógica de asociación cliente-corredor es automática y robusta.

---



Este backend implementa la lógica de negocio, API REST y acceso a base de datos para el sistema BrokerSeguros. Incluye integración con FastAPI, SQLAlchemy, Alembic y autenticación JWT, además de migraciones y utilidades para mantener la integridad y trazabilidad del sistema.

Para detalles de instalación, configuración y uso, consulta la documentación interna y los comentarios en el código fuente.
