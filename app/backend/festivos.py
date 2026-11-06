"""Festivos oficiales y cálculo de días hábiles para vacaciones (HU-10)."""
from datetime import date, timedelta

FESTIVOS: dict[int, set[date]] = {
    2026: {
        date(2026, 1, 1),
        date(2026, 2, 2),
        date(2026, 3, 16),
        date(2026, 5, 1),
        date(2026, 9, 16),
        date(2026, 11, 16),
        date(2026, 12, 25),
    },
    2027: {
        date(2027, 1, 1),
        date(2027, 2, 1),
        date(2027, 3, 15),
        date(2027, 5, 1),
        date(2027, 9, 16),
        date(2027, 11, 15),
        date(2027, 12, 25),
    },
}


def dias_habiles(fecha_inicio: date, fecha_fin: date) -> int:
    """Cuenta los días hábiles entre dos fechas, incluyendo ambos extremos."""
    festivos_anio = FESTIVOS.get(fecha_inicio.year, set())
    dias = 0
    fecha = fecha_inicio
    while fecha <= fecha_fin:
        if fecha.weekday() < 5 and fecha not in festivos_anio:
            dias += 1
        fecha += timedelta(days=1)
    return dias
