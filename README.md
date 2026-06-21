LookOwl backend

## Población de la base de datos (seed)

El script `infrastructure/database/seed.py` inserta datos de prueba: autores, géneros, libros con ejemplares y usuarios.

### Con Docker (recomendado)

```bash
# 1. Levantar la base de datos
docker compose up -d pos_db

# 2. Aplicar migraciones
docker compose run --rm migrate

# 3. Ejecutar el seed
docker compose run --rm app python -m infrastructure.database.seed
```

### Sin Docker (local)

Requiere PostgreSQL corriendo y un archivo `.env` con `ASYNC_DATABASE_URL` configurado.

```bash
alembic upgrade head
python -m infrastructure.database.seed
```

### Datos insertados

| Entidad    | Cantidad |
|------------|----------|
| Autores    | 8        |
| Géneros    | 8        |
| Libros     | 10       |
| Usuarios   | 7 (2 bibliotecarios + 5 lectores) |

**Contraseñas de prueba:** `biblio123` (bibliotecarios) y `lector123` (lectores).

## Pruebas

- [tests/test_auth_service.py](tests/test_auth_service.py): pruebas unitarias para los flujos de autenticación — registro, validación de inicio de sesión, contenido de tokens JWT y cifrado/verificación de contraseñas.
- [tests/test_book_repository.py](tests/test_book_repository.py): pruebas del repositorio de `Book` para persistencia y validación usando SQLite en memoria.
- [tests/test_endpoints.py](tests/test_endpoints.py): pruebas de endpoints principales.

Ejecutar todas las pruebas:

```bash
python -m pytest
```