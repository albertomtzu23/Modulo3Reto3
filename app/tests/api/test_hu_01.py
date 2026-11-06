"""Pruebas de API de HU-01: registro de empleados."""
import re
import uuid
from datetime import date, timedelta

import httpx


def _registrar(url_api: str, **campos) -> httpx.Response:
    return httpx.post(f"{url_api}/api/empleados", json=campos)


def _crear_empleado(url_api: str, **campos) -> dict:
    respuesta = _registrar(url_api, **campos)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _obtener_por_correo(url_api: str, correo: str) -> dict | None:
    respuesta = httpx.get(f"{url_api}/api/empleados")
    assert respuesta.status_code == 200
    coincidencias = [e for e in respuesta.json() if e["correo"] == correo]
    return coincidencias[0] if coincidencias else None


def test_cp01_registro_exitoso_normaliza_correo_y_asigna_numero(url_api):
    """CP-01: Registro exitoso de un empleado con datos válidos."""
    sufijo = uuid.uuid4().hex[:8]
    correo_enviado = f"ANA.PEREZ.{sufijo}@EMPRESA.COM"
    correo_normalizado = correo_enviado.lower()

    respuesta = _registrar(
        url_api,
        nombre="Ana Pérez",
        correo=correo_enviado,
        puesto="Analista de RRHH",
        departamento="Recursos Humanos",
        fecha_ingreso="2024-05-01",
    )

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["correo"] == correo_normalizado
    assert cuerpo["estado"] == "activo"
    # La base de datos acumula empleados de pruebas anteriores, así que el
    # consecutivo no siempre es 0001: se valida el formato, no el número.
    assert re.fullmatch(r"EMP-\d{4}", cuerpo["numero_empleado"])

    empleado_guardado = _obtener_por_correo(url_api, correo_normalizado)
    assert empleado_guardado is not None
    assert empleado_guardado["nombre"] == "Ana Pérez"
    assert empleado_guardado["puesto"] == "Analista de RRHH"
    assert empleado_guardado["departamento"] == "Recursos Humanos"
    assert empleado_guardado["fecha_ingreso"] == "2024-05-01"


def test_cp03_rechazo_por_correo_ya_registrado(url_api):
    """CP-03: Rechazo por correo ya registrado."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"carlos.ruiz.{sufijo}@empresa.com"
    _crear_empleado(
        url_api,
        nombre="Carlos Ruiz",
        correo=correo,
        puesto="Vendedor",
        departamento="Ventas",
        fecha_ingreso="2024-03-10",
    )

    respuesta = _registrar(
        url_api,
        nombre="Carlos Ruiz",
        correo=correo.upper(),
        puesto="Vendedor",
        departamento="Ventas",
        fecha_ingreso="2024-03-10",
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "El correo ya está registrado"

    respuesta_lista = httpx.get(f"{url_api}/api/empleados")
    coincidencias = [e for e in respuesta_lista.json() if e["correo"] == correo]
    assert len(coincidencias) == 1


def test_cp05_rechazo_por_correo_no_corporativo(url_api):
    """CP-05: Rechazo por correo que no es corporativo."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"luis.gomez.{sufijo}@gmail.com"

    respuesta = _registrar(
        url_api,
        nombre="Luis Gómez",
        correo=correo,
        puesto="Contador",
        departamento="Finanzas",
        fecha_ingreso="2024-02-15",
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "Usa el correo corporativo @empresa.com"
    assert _obtener_por_correo(url_api, correo) is None


def test_cp07_rechazo_por_nombre_fuera_de_longitud_minima(url_api):
    """CP-07: Rechazo por nombre que no cumple la longitud mínima."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"a.{sufijo}@empresa.com"

    respuesta = _registrar(
        url_api,
        nombre="A",
        correo=correo,
        puesto="Operario",
        departamento="Operaciones",
        fecha_ingreso="2024-01-20",
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "El campo 'nombre' no es válido."
    assert _obtener_por_correo(url_api, correo) is None


def test_cp09_rechazo_por_fecha_de_ingreso_futura(url_api):
    """CP-09: Rechazo por fecha de ingreso futura."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"maria.lopez.{sufijo}@empresa.com"
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()

    respuesta = _registrar(
        url_api,
        nombre="María López",
        correo=correo,
        puesto="Desarrolladora",
        departamento="Tecnología",
        fecha_ingreso=fecha_futura,
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "La fecha de ingreso no puede ser futura"
    assert _obtener_por_correo(url_api, correo) is None
