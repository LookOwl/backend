"""
Script de seeding para poblar la base de datos con datos de prueba.

Uso:
    python -m infrastructure.database.seed
"""

import asyncio
from datetime import date

from infrastructure.database.connection import async_session_factory
from infrastructure.database.models.autor import Autor
from infrastructure.database.models.genero import Genero
from infrastructure.database.models.libro import Libro
from infrastructure.database.models.ejemplar import Ejemplar, EstadoEjemplar
from infrastructure.database.models.usuario import Usuario
from domain.enums.roles_usuario import RolUsuario
from core.security import hash_password

# ─── Datos de prueba ───────────────────────────────────────────────

AUTORES = [
    {"nombre": "Gabriel García Márquez"},
    {"nombre": "Jorge Luis Borges"},
    {"nombre": "Isabel Allende"},
    {"nombre": "Julio Cortázar"},
    {"nombre": "Mario Vargas Llosa"},
    {"nombre": "Octavio Paz"},
    {"nombre": "Miguel de Cervantes"},
    {"nombre": "Federico García Lorca"},
]

GENEROS = [
    {"nombre": "Novela"},
    {"nombre": "Cuento"},
    {"nombre": "Poesía"},
    {"nombre": "Ensayo"},
    {"nombre": "Ciencia Ficción"},
    {"nombre": "Fantasía"},
    {"nombre": "Historia"},
    {"nombre": "Filosofía"},
]

LIBROS = [
    {
        "titulo": "Cien años de soledad",
        "isbn": "9780307474728",
        "descripcion": "La historia de la familia Buendía en el pueblo ficticio de Macondo.",
        "editorial": "Sudamericana",
        "fecha_publicacion": date(1967, 6, 5),
        "url_portada": "https://example.com/cien-anios.jpg",
        "lenguaje": "es",
        "num_paginas": 471,
        "autores": ["Gabriel García Márquez"],
        "generos": ["Novela", "Fantasía"],
        "copias": 4,
    },
    {
        "titulo": "El Aleph",
        "isbn": "9780307950949",
        "descripcion": "Colección de cuentos que exploran el infinito y la identidad.",
        "editorial": "Losada",
        "fecha_publicacion": date(1949, 1, 1),
        "url_portada": "https://example.com/aleph.jpg",
        "lenguaje": "es",
        "num_paginas": 208,
        "autores": ["Jorge Luis Borges"],
        "generos": ["Cuento", "Filosofía"],
        "copias": 3,
    },
    {
        "titulo": "La casa de los espíritus",
        "isbn": "9788401352836",
        "descripcion": "Saga familiar que mezcla realismo mágico con historia política de Chile.",
        "editorial": "Plaza & Janés",
        "fecha_publicacion": date(1982, 1, 1),
        "url_portada": "https://example.com/casa-espiritus.jpg",
        "lenguaje": "es",
        "num_paginas": 454,
        "autores": ["Isabel Allende"],
        "generos": ["Novela", "Fantasía"],
        "copias": 3,
    },
    {
        "titulo": "Rayuela",
        "isbn": "9788437604572",
        "descripcion": "Novela experimental que puede leerse en orden lineal o salteado.",
        "editorial": "Sudamericana",
        "fecha_publicacion": date(1963, 6, 28),
        "url_portada": "https://example.com/rayuela.jpg",
        "lenguaje": "es",
        "num_paginas": 736,
        "autores": ["Julio Cortázar"],
        "generos": ["Novela"],
        "copias": 2,
    },
    {
        "titulo": "La ciudad y los perros",
        "isbn": "9788420471969",
        "descripcion": "Retrato de la violencia en un colegio militar de Lima.",
        "editorial": "Seix Barral",
        "fecha_publicacion": date(1963, 1, 1),
        "url_portada": "https://example.com/ciudad-perros.jpg",
        "lenguaje": "es",
        "num_paginas": 416,
        "autores": ["Mario Vargas Llosa"],
        "generos": ["Novela"],
        "copias": 2,
    },
    {
        "titulo": "El laberinto de la soledad",
        "isbn": "9789681603014",
        "descripcion": "Ensayo sobre la identidad mexicana y el carácter nacional.",
        "editorial": "Fondo de Cultura Económica",
        "fecha_publicacion": date(1950, 1, 1),
        "url_portada": "https://example.com/laberinto.jpg",
        "lenguaje": "es",
        "num_paginas": 191,
        "autores": ["Octavio Paz"],
        "generos": ["Ensayo", "Filosofía"],
        "copias": 3,
    },
    {
        "titulo": "Don Quijote de la Mancha",
        "isbn": "9788420412146",
        "descripcion": "Las aventuras del ingenioso hidalgo Don Quijote y su fiel escudero Sancho Panza.",
        "editorial": "Alfaguara",
        "fecha_publicacion": date(1605, 1, 16),
        "url_portada": "https://example.com/quijote.jpg",
        "lenguaje": "es",
        "num_paginas": 1345,
        "autores": ["Miguel de Cervantes"],
        "generos": ["Novela"],
        "copias": 5,
    },
    {
        "titulo": "Romancero gitano",
        "isbn": "9788467033366",
        "descripcion": "Obra poética que fusiona la tradición gitana con el folclore andaluz.",
        "editorial": "Espasa-Calpe",
        "fecha_publicacion": date(1928, 1, 1),
        "url_portada": "https://example.com/romancero.jpg",
        "lenguaje": "es",
        "num_paginas": 152,
        "autores": ["Federico García Lorca"],
        "generos": ["Poesía"],
        "copias": 3,
    },
    {
        "titulo": "El amor en los tiempos del cólera",
        "isbn": "9780307387264",
        "descripcion": "Historia de amor entre Florentino Ariza y Fermina Daza a lo largo de décadas.",
        "editorial": "Sudamericana",
        "fecha_publicacion": date(1985, 1, 1),
        "url_portada": "https://example.com/amor-colera.jpg",
        "lenguaje": "es",
        "num_paginas": 461,
        "autores": ["Gabriel García Márquez"],
        "generos": ["Novela"],
        "copias": 3,
    },
    {
        "titulo": "Ficciones",
        "isbn": "9780307950925",
        "descripcion": "Colección de relatos que exploran laberintos, espejos y bibliotecas infinitas.",
        "editorial": "Sur",
        "fecha_publicacion": date(1944, 1, 1),
        "url_portada": "https://example.com/ficciones.jpg",
        "lenguaje": "es",
        "num_paginas": 304,
        "autores": ["Jorge Luis Borges"],
        "generos": ["Cuento", "Ensayo"],
        "copias": 4,
    },
]

USUARIOS = [
    {
        "nombre": "María López",
        "email": "maria.lopez@biblioteca.com",
        "numero_contacto": "555100101",
        "rol": RolUsuario.BIBLIOTECARIO,
        "password": "biblio123",
    },
    {
        "nombre": "Carlos Ramírez",
        "email": "carlos.ramirez@biblioteca.com",
        "numero_contacto": "555100102",
        "rol": RolUsuario.BIBLIOTECARIO,
        "password": "biblio123",
    },
    {
        "nombre": "Ana Martínez",
        "email": "ana.martinez@example.com",
        "numero_contacto": "555200201",
        "rol": RolUsuario.LECTOR,
        "password": "lector123",
    },
    {
        "nombre": "Pedro Fernández",
        "email": "pedro.fernandez@example.com",
        "numero_contacto": "555200202",
        "rol": RolUsuario.LECTOR,
        "password": "lector123",
    },
    {
        "nombre": "Lucía González",
        "email": "lucia.gonzalez@example.com",
        "numero_contacto": "555200203",
        "rol": RolUsuario.LECTOR,
        "password": "lector123",
    },
    {
        "nombre": "Diego Sánchez",
        "email": "diego.sanchez@example.com",
        "numero_contacto": "555200204",
        "rol": RolUsuario.LECTOR,
        "password": "lector123",
    },
    {
        "nombre": "Elena Torres",
        "email": "elena.torres@example.com",
        "numero_contacto": "555200205",
        "rol": RolUsuario.LECTOR,
        "password": "lector123",
    },
]


# ─── Función principal de seeding ──────────────────────────────────

async def seed_database() -> None:
    """Puebla la base de datos con autores, géneros, libros, ejemplares y usuarios de prueba."""
    async with async_session_factory() as session:
        try:
            # ── Autores ──────────────────────────────────────────
            autor_map: dict[str, Autor] = {}
            for a in AUTORES:
                autor = Autor(nombre=a["nombre"])
                session.add(autor)
                autor_map[a["nombre"]] = autor
            await session.flush()  # obtener IDs sin hacer commit

            # ── Géneros ──────────────────────────────────────────
            genero_map: dict[str, Genero] = {}
            for g in GENEROS:
                genero = Genero(nombre=g["nombre"])
                session.add(genero)
                genero_map[g["nombre"]] = genero
            await session.flush()

            # ── Libros + Ejemplares ──────────────────────────────
            for i, lb in enumerate(LIBROS):
                libro = Libro(
                    titulo=lb["titulo"],
                    isbn=lb["isbn"],
                    descripcion=lb["descripcion"],
                    editorial=lb["editorial"],
                    fecha_publicacion=lb["fecha_publicacion"],
                    url_portada=lb["url_portada"],
                    lenguaje=lb["lenguaje"],
                    num_paginas=lb["num_paginas"],
                    autores=[autor_map[n] for n in lb["autores"]],
                    generos=[genero_map[n] for n in lb["generos"]],
                )
                session.add(libro)
                await session.flush()  # obtener libro.id

                # Crear ejemplares (copias físicas)
                for j in range(1, lb["copias"] + 1):
                    ejemplar = Ejemplar(
                        libro_id=libro.id,
                        codigo=f"{lb['isbn']}-{j:03d}",
                        estado=EstadoEjemplar.DISPONIBLE,
                    )
                    session.add(ejemplar)

                print(f"  ✓ Libro '{lb['titulo']}' + {lb['copias']} ejemplares")

            # ── Usuarios ─────────────────────────────────────────
            for u in USUARIOS:
                usuario = Usuario(
                    nombre=u["nombre"],
                    email=u["email"],
                    numero_contacto=u["numero_contacto"],
                    rol=u["rol"],
                    hash_contrasena=hash_password(u["password"]),
                )
                session.add(usuario)
                print(f"  ✓ Usuario '{u['nombre']}' ({u['rol'].value}) — contraseña: {u['password']}")

            await session.commit()
            print("\n[!] Base de datos poblada exitosamente.")

        except Exception as e:
            await session.rollback()
            print(f"\n[!] Error durante el seeding: {e}")
            raise


# ─── Entry point ───────────────────────────────────────────────────

def main():
    """Ejecuta el seed de forma síncrona."""
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()
