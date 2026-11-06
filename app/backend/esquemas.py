"""Esquemas Pydantic para el recurso empleado."""
import re
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

PATRON_CORREO_CORPORATIVO = re.compile(r"^[^@\s]+@empresa\.com$")


class EmpleadoCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    correo: str
    puesto: str = Field(min_length=2, max_length=60)
    departamento: str
    fecha_ingreso: date

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if not PATRON_CORREO_CORPORATIVO.match(valor):
            raise ValueError("Usa el correo corporativo @empresa.com")
        return valor


class EmpleadoEditar(BaseModel):
    puesto: str | None = Field(default=None, min_length=2, max_length=60)
    departamento: str | None = None


class EmpleadoBaja(BaseModel):
    fecha_baja: date


class EmpleadoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_empleado: str
    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: date
    estado: str
    fecha_baja: date | None
    creado_en: datetime


class VacacionesCrear(BaseModel):
    fecha_inicio: date
    fecha_fin: date


class VacacionesSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    empleado_id: int
    fecha_inicio: date
    fecha_fin: date
    dias_habiles: int
    dias_restantes: int


class SolicitudResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_inicio: date
    fecha_fin: date
    dias_habiles: int


class VacacionesSaldo(BaseModel):
    empleado_id: int
    anio: int
    dias_usados: int
    dias_disponibles: int
    solicitudes: list[SolicitudResumen]
