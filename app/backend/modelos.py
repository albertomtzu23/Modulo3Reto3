"""Modelos SQLAlchemy del dominio de empleados."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from basedatos import Base

DEPARTAMENTOS_VALIDOS = [
    "Tecnología",
    "Ventas",
    "Finanzas",
    "Recursos Humanos",
    "Operaciones",
]


class Empleado(Base):
    __tablename__ = "empleados"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    numero_empleado: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(80))
    correo: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    puesto: Mapped[str] = mapped_column(String(60))
    departamento: Mapped[str] = mapped_column(String(40))
    fecha_ingreso: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(10), default="activo")
    fecha_baja: Mapped[date | None] = mapped_column(Date, nullable=True, default=None)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
