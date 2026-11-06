"""Pruebas de API de HU-03: edición y baja de empleados."""
import uuid

import httpx


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


def _dar_de_baja(url_api: str, empleado_id: int, fecha_baja: str) -> dict:
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado_id}/baja", json={"fecha_baja": fecha_baja}
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def _obtener_empleado(url_api: str, empleado_id: int) -> dict:
    respuesta = httpx.get(f"{url_api}/api/empleados")
    assert respuesta.status_code == 200
    coincidencias = [e for e in respuesta.json() if e["id"] == empleado_id]
    assert len(coincidencias) == 1
    return coincidencias[0]


def test_cp01_editar_puesto_y_departamento(url_api):
    """CP-01: Editar puesto y departamento de un empleado activo."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Ventas"
    )

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}",
        json={"puesto": "Analista Senior", "departamento": "Finanzas"},
    )
    assert respuesta.status_code == 200

    actualizado = _obtener_empleado(url_api, empleado["id"])
    assert actualizado["puesto"] == "Analista Senior"
    assert actualizado["departamento"] == "Finanzas"


def test_cp03_correo_y_numero_empleado_no_se_modifican(url_api):
    """CP-03: El correo y el número de empleado no se modifican aunque se intenten editar."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"carlos.ruiz.{sufijo}@empresa.com"
    empleado = _crear_empleado(url_api, "Carlos Ruiz", correo, "Analista", "Ventas")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}",
        json={"numero_empleado": "EMP-9999", "correo": "otro@empresa.com"},
    )
    assert respuesta.status_code == 200

    actualizado = _obtener_empleado(url_api, empleado["id"])
    assert actualizado["numero_empleado"] == empleado["numero_empleado"]
    assert actualizado["correo"] == correo


def test_cp04_puesto_fuera_de_rango(url_api):
    """CP-04: Rechazar la edición cuando el puesto queda fuera del rango permitido."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Gerente", "Finanzas"
    )

    respuesta = httpx.put(f"{url_api}/api/empleados/{empleado['id']}", json={"puesto": "A"})
    assert respuesta.status_code == 422


def test_cp06_departamento_no_es_catalogo_valido(url_api):
    """CP-06: Rechazar la edición cuando el departamento no es uno de los catálogos válidos."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Tecnología"
    )

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}", json={"departamento": "Mercadotecnia"}
    )
    assert respuesta.status_code == 422


def test_cp08_baja_con_fecha_igual_a_fecha_ingreso(url_api):
    """CP-08: Dar de baja a un empleado activo con fecha de baja igual a la fecha de ingreso."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Ana López",
        f"ana.lopez.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        fecha_ingreso="2024-01-10",
    )

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2024-01-10"}
    )
    assert respuesta.status_code == 200

    actualizado = _obtener_empleado(url_api, empleado["id"])
    assert actualizado["estado"] == "baja"
    assert actualizado["fecha_baja"] == "2024-01-10"


def test_cp10_baja_con_fecha_anterior_a_fecha_ingreso(url_api):
    """CP-10: Rechazar la baja cuando la fecha de baja es anterior a la fecha de ingreso."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Ana López",
        f"ana.lopez.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        fecha_ingreso="2024-01-10",
    )

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2024-01-09"}
    )
    assert respuesta.status_code == 422


def test_cp12_editar_empleado_dado_de_baja(url_api):
    """CP-12: Rechazar la edición de un empleado que ya está dado de baja."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Ventas"
    )
    _dar_de_baja(url_api, empleado["id"], "2024-06-15")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}", json={"puesto": "Supervisor"}
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "No se puede editar a un empleado dado de baja"
