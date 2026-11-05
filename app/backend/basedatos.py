"""Configuración de la base de datos SQLite con SQLAlchemy."""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

CARPETA_DATOS = Path(__file__).resolve().parent / "datos"
CARPETA_DATOS.mkdir(exist_ok=True)
RUTA_BASE_DATOS = CARPETA_DATOS / "empleados.db"

engine = create_engine(
    f"sqlite:///{RUTA_BASE_DATOS}",
    connect_args={"check_same_thread": False},
)
SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def obtener_sesion() -> Session:
    sesion = SesionLocal()
    try:
        yield sesion
    finally:
        sesion.close()
