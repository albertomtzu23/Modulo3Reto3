"""Pruebas E2E de HU-01: registro de empleados."""
import re
import uuid
from datetime import date, timedelta

import httpx
from playwright.sync_api import expect


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


def _contar_filas(page) -> int:
    return page.locator('[data-testid^="fila-empleado-"]').count()


def _llenar_formulario(page, nombre, correo, puesto, departamento, fecha_ingreso):
    page.get_by_test_id("empleado-nombre").fill(nombre)
    page.get_by_test_id("empleado-correo").fill(correo)
    page.get_by_test_id("empleado-puesto").fill(puesto)
    page.get_by_test_id("empleado-departamento").select_option(departamento)
    page.get_by_test_id("empleado-fecha-ingreso").fill(fecha_ingreso)


def test_cp02_registro_exitoso(page, url_web):
    """CP-02: Registro exitoso de un empleado con datos válidos."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"ANA.PEREZ.{sufijo}@EMPRESA.COM"

    page.goto(url_web)
    _llenar_formulario(
        page, "Ana Pérez", correo, "Analista de RRHH", "Recursos Humanos", "2024-05-01"
    )
    page.get_by_test_id("empleado-guardar").click()

    # El consecutivo depende de los empleados ya creados por otras pruebas.
    expect(page.get_by_test_id("mensaje-exito")).to_have_text(
        re.compile(r"^Empleado EMP-\d{4} registrado con éxito$")
    )


def test_cp04_rechazo_por_correo_ya_registrado(page, url_api, url_web):
    """CP-04: Rechazo por correo ya registrado."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"carlos.ruiz.{sufijo}@empresa.com"
    empleado = _crear_empleado(url_api, "Carlos Ruiz", correo, "Vendedor", "Ventas", "2024-03-10")

    page.goto(url_web)
    expect(page.get_by_test_id(f"fila-empleado-{empleado['id']}")).to_be_visible()
    filas_antes = _contar_filas(page)
    _llenar_formulario(
        page, "Carlos Ruiz", correo.upper(), "Vendedor", "Ventas", "2024-03-10"
    )
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-error")).to_have_text("El correo ya está registrado")
    assert _contar_filas(page) == filas_antes


def test_cp06_rechazo_por_correo_no_corporativo(page, url_web):
    """CP-06: Rechazo por correo que no es corporativo."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"luis.gomez.{sufijo}@gmail.com"

    page.goto(url_web)
    _llenar_formulario(page, "Luis Gómez", correo, "Contador", "Finanzas", "2024-02-15")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-error")).to_have_text(
        "Usa el correo corporativo @empresa.com"
    )


def test_cp08_rechazo_por_nombre_fuera_de_longitud_minima(page, url_web):
    """CP-08: Rechazo por nombre que no cumple la longitud mínima."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"a.{sufijo}@empresa.com"

    page.goto(url_web)
    _llenar_formulario(page, "A", correo, "Operario", "Operaciones", "2024-01-20")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("empleado-nombre")).to_have_attribute("aria-invalid", "true")
    expect(page.get_by_test_id("mensaje-error")).to_have_text("El campo 'nombre' no es válido.")


def test_cp10_rechazo_por_fecha_de_ingreso_futura(page, url_web):
    """CP-10: Rechazo por fecha de ingreso futura."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"maria.lopez.{sufijo}@empresa.com"
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()

    page.goto(url_web)
    _llenar_formulario(
        page, "María López", correo, "Desarrolladora", "Tecnología", fecha_futura
    )
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-error")).to_have_text(
        "La fecha de ingreso no puede ser futura"
    )
