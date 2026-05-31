## Cambios realizados

### Migrar SQLAlchemy Session a AsyncSession
Necesario para introducir verdadera asincronía. Session se comporta de manera síncrona -> Bloquea operaciones -> El servidor no se comporta como uno asíncrono que maneja múltiple requests

### Introducir el patrón Unit of Work

`UoW` es un patrón que atomiza las transacciones, que en nuestro caso serán a la base de datos. La clase `UoW` es la encargada de mantener la referencia a los distintos repositorios, siendo el punto de acceso a éstos. Además, maneja explícitamente el flujo de transacciones. El esquema general es el siguiente:
```python
    class UnitOfWork:
        def __init__(self, async_session):
            self.async_session = async_session
            #Init repos
            self.repo = Repo(async_session)
            #more
            
        def __aenter__(self):
            self.begin_transaction()
            return self

        def __aexit__(self,*args):
            
            if(error):
                self.async_session.rollback()
            else:
                self.async_session.commit()
```

Usualmente un `UoW` viene con métodos `begin()`, `commit()`, `rollback()`, etc, cuyo propósito es delegar al objeto que lo instancia que maneje el flujo. Sin embargo, como se ve previamente, podemos usar los métodos base `__aenter__` y `__aexit__`, los cuales son llamados al inicio y fin de una cláusula `async with ...`
```python
    #Suponer una clase que tiene como miembro un `uow`
    #Entonces sus métodos sería
    uow : UnitOfWork
    def foo(self):
        async with self.uow as uow:
            some_result = uow.repo.get() 
```
Finalmente, el cambio fundamental es que los repositorios no necesitan ser inyectados, y que la capa de servicios no necesita interactuar con los repositorios, sino con el `UoW`

### Redis
Redis es un sistema de almacenamiento de memoria de alta velocidad, que suele ser usado para distintas cosas, la más sonada ser usado como caché. Para nuestros propósitos, sirven para mantener los dos índices usados en el sistema de préstamos y devoluciones.
Ventajas:
- Rápido acceso: Se mantiene los índices en un servicio en memoria, en lugar de estar realizando queries lentas sobre la base de datos
Desventajas:
- Introduce problemas de concurrencia. Solución: `UoW` + `Orchestrator`

Con el propósito de usar Redis, se han introducido:
- Un controlador explícito del servicio
- Un lock manejado por el `Orchestrator` sobre los índices

### Orchestrator

El patrón `Orchestrator` sirve para coordinar múttiples operaciones relacionadas a un caso de uso o conjuntos de casos de uso relacionados entre sí. En este caso, servirá cmo orquestador global entre las transacciones a la base de datos y el acceso a los indices de Redis.
