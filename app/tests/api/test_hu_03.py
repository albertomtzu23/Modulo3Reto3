"""Pruebas de API de HU-03: edición y baja de empleados."""
import sqlite3
import uuid
from pathlib import Path

import httpx

# Base de datos real del backend: no hay forma de preparar un empleado dado
# de baja a través de la API, así que se marca directamente en la base.
RUTA_BASE_DATOS = Path(__file__).resolve().parents[2] / "backend" / "datos" / "empleados.db"


def _crear_empleado(
    url_api: str,
    nombre: str,
    correo: str,
    puesto: str,
    departamento: str,
    fecha_ingreso: str = "2023-01-10",
) -> dict:
    respuesta = httpx.post(
        f"{url_api}/api/empleados",
        json={
            "nombre": nombre,
            "correo": correo,
            "puesto": puesto,
            "departamento": departamento,
            "fecha_ingreso": fecha_ingreso,
        },
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _marcar_baja(empleado_id: int, fecha_baja: str) -> None:
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    try:
        conexion.execute(
            "UPDATE empleados SET estado = 'baja', fecha_baja = ? WHERE id = ?",
            (fecha_baja, empleado_id),
        )
        conexion.commit()
    finally:
        conexion.close()


def test_cp01_editar_puesto_y_departamento(url_api):
    """CP-01: Editar puesto y departamento de un empleado activo."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"ana.lopez.{sufijo}@empresa.com"
    ana = _crear_empleado(url_api, "Ana López", correo, "Analista", "Finanzas")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{ana['id']}",
        json={"puesto": "Analista Senior", "departamento": "Tecnología"},
    )
    assert respuesta.status_code == 200
    actualizado = respuesta.json()
    assert actualizado["puesto"] == "Analista Senior"
    assert actualizado["departamento"] == "Tecnología"
    assert actualizado["numero_empleado"] == ana["numero_empleado"]
    assert actualizado["correo"] == correo


def test_cp03_departamento_no_permitido(url_api):
    """CP-03: Error al editar con un departamento que no está en la lista permitida."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Finanzas"
    )

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}", json={"departamento": "Marketing"}
    )
    assert respuesta.status_code == 422
    assert "departamento" in respuesta.json()["detail"]


def test_cp05_puesto_demasiado_corto(url_api):
    """CP-05: Error al editar con un puesto demasiado corto."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Finanzas"
    )

    respuesta = httpx.put(f"{url_api}/api/empleados/{empleado['id']}", json={"puesto": "A"})
    assert respuesta.status_code == 422
    assert "puesto" in respuesta.json()["detail"]


def test_cp07_editar_empleado_de_baja(url_api):
    """CP-07: Error al intentar editar a un empleado dado de baja."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Finanzas"
    )
    _marcar_baja(empleado["id"], "2024-01-01")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}", json={"puesto": "Analista Senior"}
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "No se puede editar a un empleado dado de baja"


def test_cp09_dar_de_baja_empleado_activo(url_api):
    """CP-09: Dar de baja a un empleado activo."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Ana López",
        f"ana.lopez.{sufijo}@empresa.com",
        "Analista",
        "Finanzas",
        fecha_ingreso="2020-03-01",
    )

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2024-06-15"}
    )
    assert respuesta.status_code == 200
    actualizado = respuesta.json()
    assert actualizado["estado"] == "baja"
    assert actualizado["fecha_baja"] == "2024-06-15"

    directorio = httpx.get(f"{url_api}/api/empleados")
    assert directorio.status_code == 200
    coincidencias = [e for e in directorio.json() if e["id"] == empleado["id"]]
    assert len(coincidencias) == 1


def test_cp11_fecha_baja_anterior_a_fecha_ingreso(url_api):
    """CP-11: Error al dar de baja con una fecha de baja anterior a la fecha de ingreso."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Ana López",
        f"ana.lopez.{sufijo}@empresa.com",
        "Analista",
        "Finanzas",
        fecha_ingreso="2020-03-01",
    )

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2019-01-10"}
    )
    assert respuesta.status_code == 422
    assert "fecha_baja" in respuesta.json()["detail"]
