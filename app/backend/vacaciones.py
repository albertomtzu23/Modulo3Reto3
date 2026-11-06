"""Reglas de negocio de vacaciones (HU-10), separadas de las rutas."""
from datetime import date


def fecha_aniversario(fecha_ingreso: date) -> date:
    """Primer día en que se cumple un año desde fecha_ingreso.

    Si fecha_ingreso es 29 de febrero, el aniversario en un año no bisiesto
    cae el 1 de marzo (regla de negocio HU-10).
    """
    try:
        return fecha_ingreso.replace(year=fecha_ingreso.year + 1)
    except ValueError:
        return date(fecha_ingreso.year + 1, 3, 1)


def cumple_antiguedad(fecha_ingreso: date, fecha_inicio: date) -> bool:
    return fecha_inicio >= fecha_aniversario(fecha_ingreso)
