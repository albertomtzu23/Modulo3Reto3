"""Pruebas E2E de HU-03: edición y baja de empleados."""
import sqlite3
import uuid
from pathlib import Path

import httpx
from playwright.sync_api import expect

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


def test_cp02_editar_puesto_y_departamento(page, url_api, url_web):
    """CP-02: Editar puesto y departamento de un empleado activo."""
    sufijo = uuid.uuid4().hex[:8]
    ana = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Finanzas"
    )

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{ana['id']}")
    expect(fila).to_be_visible()
    fila.get_by_test_id(f"editar-empleado-{ana['id']}").click()

    page.get_by_test_id("empleado-puesto").fill("Analista Senior")
    page.get_by_test_id("empleado-departamento").select_option("Tecnología")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    fila = page.get_by_test_id(f"fila-empleado-{ana['id']}")
    expect(fila).to_contain_text("Analista Senior")
    expect(fila).to_contain_text("Tecnología")
    expect(fila.get_by_test_id(f"numero-empleado-{ana['id']}")).to_have_text(
        ana["numero_empleado"]
    )


def test_cp04_departamento_no_permitido(page, url_api, url_web):
    """CP-04: Error al editar con un departamento que no está en la lista permitida."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Finanzas"
    )

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    fila.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-puesto").fill("Analista Senior")
    # empleado-departamento es un <select> que solo ofrece departamentos
    # válidos (ver GET /api/departamentos), por lo que un usuario no puede
    # elegir "Marketing" desde la interfaz. Se inyecta la opción para poder
    # ejercer la validación del backend, tal como la describe el caso.
    campo_departamento = page.get_by_test_id("empleado-departamento")
    campo_departamento.evaluate(
        """(el, valor) => {
            const opcion = document.createElement('option');
            opcion.value = valor;
            opcion.textContent = valor;
            el.appendChild(opcion);
            el.value = valor;
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }""",
        "Marketing",
    )
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-error")).to_contain_text("departamento")
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_contain_text("Analista")
    expect(fila).to_contain_text("Finanzas")


def test_cp06_puesto_demasiado_corto(page, url_api, url_web):
    """CP-06: Error al editar con un puesto demasiado corto."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Finanzas"
    )

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    fila.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-puesto").fill("A")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-error")).to_contain_text("puesto")
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_contain_text("Analista")


def test_cp08_editar_empleado_de_baja(page, url_api, url_web):
    """CP-08: Error al intentar editar a un empleado dado de baja."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Finanzas"
    )
    _marcar_baja(empleado["id"], "2024-01-01")

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")
    fila.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-puesto").fill("Analista Senior")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-error")).to_have_text(
        "No se puede editar a un empleado dado de baja"
    )
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_contain_text("Analista")
    expect(fila.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")


def test_cp10_dar_de_baja_empleado_activo(page, url_api, url_web):
    """CP-10: Dar de baja a un empleado activo."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Ana López",
        f"ana.lopez.{sufijo}@empresa.com",
        "Analista",
        "Finanzas",
        fecha_ingreso="2020-03-01",
    )

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    fila.get_by_test_id(f"baja-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-fecha-baja").fill("2024-06-15")
    page.get_by_test_id("confirmar-baja").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    expect(fila.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")


def test_cp12_fecha_baja_anterior_a_fecha_ingreso(page, url_api, url_web):
    """CP-12: Error al dar de baja con una fecha de baja anterior a la fecha de ingreso."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Ana López",
        f"ana.lopez.{sufijo}@empresa.com",
        "Analista",
        "Finanzas",
        fecha_ingreso="2020-03-01",
    )

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    fila.get_by_test_id(f"baja-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-fecha-baja").fill("2019-01-10")
    page.get_by_test_id("confirmar-baja").click()

    expect(page.get_by_test_id("mensaje-error")).to_contain_text("fecha_baja")
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Activo")
