from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.config import settings

# Establecemos conexión con la base de datos
engine = create_engine(settings.DATABASE_URL)

# Generador de sesión
SessionLocal = sessionmaker(
   autoflush=False,
   bind=engine
)

# Función de inicialización para operaciones SQL
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
