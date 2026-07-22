"""
Capa de conexión a la base de datos.

Diseño clave del proyecto multicloud:
- En local se usa SQLite (un archivo, sin instalar nada).
- En producción (Azure) se usa PostgreSQL, cambiando SOLO la variable
  de entorno DATABASE_URL. El resto del código no cambia.

Esto demuestra el principio de portabilidad entre nubes: la aplicación
no está acoplada a un motor de base de datos concreto.
"""
import os
from sqlmodel import SQLModel, create_engine, Session

# Si existe la variable de entorno DATABASE_URL (en el servidor), se usa esa.
# Si no existe (en tu PC), cae en un archivo SQLite local.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vigia.db")

# connect_args solo es necesario para SQLite; para PostgreSQL se ignora.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def crear_tablas() -> None:
    """Crea las tablas en la base de datos si aún no existen."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Entrega una sesión de base de datos por cada petición (patrón de dependencia)."""
    with Session(engine) as session:
        yield session
