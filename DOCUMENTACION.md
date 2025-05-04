# Documentación técnica: Estado actual de Backend y Frontend

## 1. Endpoints principales del Backend

### `/api/v1/clientes/` (GET)
- **Propósito:** Listar todos los clientes asociados al sistema o al corredor autenticado.
- **Respuesta esperada:**
  ```json
  [
    {
      "id": "uuid",
      "nombre": "Nombre Apellido",
      "email": "correo@dominio.com",
      "telefono": "099123456",
      "direccion": "...",
      "documento": "..."
    }
  ]
  ```
- **Notas:**
  - El campo `nombre` es el nombre completo, no separado.
  - Puede haber campos extra según la versión del backend, pero los anteriores son los mínimos para el frontend.

### `/api/v1/clientes/` (POST)
- **Propósito:** Crear un nuevo cliente y asociarlo automáticamente al corredor autenticado.
- **Request esperado:**
  ```json
  {
    "nombres": "Nombre",
    "apellidos": "Apellido",
    "mail": "correo@dominio.com",
    "telefonos": "099123456",
    "movil": "099123456",
    "localidad": "Montevideo",
    "direccion": "...",
    "documento": "..."
  }
  ```
- **Notas:**
  - El frontend debe transformar los datos antes de enviar (ver tabla de mapeo).
  - El backend requiere `localidad` y `documento`.
  - El campo `mail` corresponde a `email` en el frontend.
  - El cliente creado queda asociado al corredor creador.

### `/api/v1/clientes/{id}` (PUT)
- **Propósito:** Actualizar los datos de un cliente existente.
- **Request esperado:** Igual que el POST, pero todos los campos deben estar presentes.

### `/api/v1/corredores/` (GET/POST/PUT)
- **Notas:**
  - El campo `documento` ahora está presente tanto en request como en response.
  - El frontend debe mapear correctamente los campos.

---

## 2. Mapeo de datos Frontend ↔ Backend

| Frontend (visual) | Backend (request) |
|-------------------|------------------|
| nombre            | nombres, apellidos (separados) |
| email             | mail             |
| telefono          | telefonos, movil |
| documento         | documento        |
| localidad         | localidad        |
| dirección         | direccion        |

- El ViewModel del frontend realiza la transformación automáticamente.
- Si el backend responde con `nombre`, el frontend lo divide en `nombres` y `apellidos` si es necesario.

---

## 3. Problemas conocidos y soluciones implementadas

- **Desajuste de modelos:** El backend y el frontend usan nombres de campos diferentes. El ViewModel del frontend realiza el mapeo automático antes de enviar los datos.
- **Campo `documento` faltante:** Ya solucionado. El campo está presente en todas las respuestas y requests.
- **Error 422 (Unprocessable Entity):** Suele deberse a campos requeridos faltantes o mal mapeados. Verifica el mapeo y que todos los campos estén presentes.
- **Clientes no aparecen tras crearse:** Ahora, los clientes se asocian correctamente al corredor creador mediante una relación automática en el backend.
- **Filtrado incorrecto en frontend:** Antes, el frontend filtraba mal y mostraba brokers en la tabla de clientes. Esto ya está corregido.
- **Carga de iconos SVG:** Las rutas de iconos fueron corregidas en los archivos QSS para que apunten a la carpeta de recursos.

---

## 4. Ejemplo de transformación de datos

### Visualización en el frontend:
```json
{
  "nombre": "Ana Pérez",
  "email": "ana@correo.com",
  "telefono": "099111222",
  "direccion": "18 de Julio 1234",
  "documento": "12345678"
}
```

### Payload enviado al backend:
```json
{
  "nombres": "Ana",
  "apellidos": "Pérez",
  "mail": "ana@correo.com",
  "telefonos": "099111222",
  "movil": "099111222",
  "localidad": "Montevideo",
  "direccion": "18 de Julio 1234",
  "documento": "12345678"
}
```

---

## 5. Preguntas frecuentes (FAQ)

- **¿Por qué el frontend mostraba brokers en la tabla de clientes?**
  Porque antes no se filtraban correctamente los registros; ya está solucionado.

- **¿Por qué recibo error 422 al crear/actualizar?**
  Verifica que todos los campos requeridos estén presentes y bien mapeados.

- **¿Qué hago si un cliente creado no aparece en la lista?**
  Ahora el backend asocia automáticamente el cliente al corredor creador. Si sigue sin aparecer, revisar logs y la relación en la base de datos.

- **¿Qué campos son obligatorios para crear un cliente?**
  Todos los del ejemplo de payload, especialmente `nombres`, `apellidos`, `mail`, `telefonos`, `localidad` y `documento`.

---

## 6. Notas para desarrolladores

- Si agregas o cambias un campo en el backend, revisa y actualiza el mapeo en el ViewModel del frontend.
- Mantén este documento actualizado para evitar dudas recurrentes.
- Si surge un error nuevo, documenta la causa y la solución aquí.

---

## 7. Estado de alineación Backend ↔ Frontend

- **El backend está alineado:** Los endpoints cumplen con los contratos descritos arriba y los campos requeridos están presentes y validados.
- **El frontend realiza transformaciones:** Debido a diferencias históricas, el frontend transforma los datos antes de enviar y después de recibir. Esto se hace para mantener la UX y cumplir con los requisitos del backend.
- **¡IMPORTANTE!** Si el backend cambia la estructura de los datos (nombres de campos, campos obligatorios, etc.), el frontend puede dejar de funcionar correctamente hasta que se adapte el mapeo en el ViewModel.
- **Referencia:** El mapeo de datos se realiza principalmente en:
  - `frontend/gui/viewmodels/cliente_viewmodel.py`
  - `frontend/gui/viewmodels/cliente/cliente_network_handler.py`
- **Testing:** Para validar la alineación y el correcto funcionamiento, consulta y ejecuta los tests en `tests/test_clientes.py`.

---

## 8. Depuración rápida y buenas prácticas

- **¿Ves un error 422 o datos que no aparecen?**
  1. Verifica los logs del frontend y backend.
  2. Asegúrate de que todos los campos requeridos estén presentes y correctamente nombrados (ver tabla de mapeo).
  3. Consulta este documento antes de modificar código.

- **¿Agregas un campo nuevo en el backend?**
  1. Actualiza este documento.
  2. Actualiza el mapeo en el frontend (ver archivos de referencia arriba).
  3. Agrega o ajusta tests si es posible.

- **¿No sabes si el problema es del backend o del frontend?**
  - Revisa los ejemplos de request/response y usa herramientas como Postman para probar el endpoint directamente.
  - Si el backend responde bien pero el frontend falla, revisa el mapeo y la lógica en el ViewModel.
  - Si el backend falla, revisa los logs y asegúrate de que los datos cumplen el contrato esperado.

---

**Última actualización:** 2025-05-04
