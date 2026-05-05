LookOwl backend

## Pruebas

- [tests/test_auth_service.py](tests/test_auth_service.py): pruebas unitarias para los flujos de autenticación — registro, validación de inicio de sesión, contenido de tokens JWT y cifrado/verificación de contraseñas.
- [tests/test_book_repository.py](tests/test_book_repository.py): pruebas del repositorio de `Book` para persistencia y validación usando SQLite en memoria.

Ejecutar todas las pruebas:

```bash
python -m pytest
```