"""Pruebas E2E de HU-03: edición y baja de empleados."""
import uuid

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


def _dar_de_baja(url_api: str, empleado_id: int, fecha_baja: str) -> dict:
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado_id}/baja", json={"fecha_baja": fecha_baja}
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def test_cp02_editar_puesto_y_departamento(page, url_api, url_web):
    """CP-02: Editar puesto y departamento de un empleado activo."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Ventas"
    )

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    fila.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-puesto").fill("Analista Senior")
    page.get_by_test_id("empleado-departamento").select_option("Finanzas")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_contain_text("Analista Senior")
    expect(fila).to_contain_text("Finanzas")


def test_cp05_puesto_fuera_de_rango(page, url_api, url_web):
    """CP-05: Rechazar la edición cuando el puesto queda fuera del rango permitido."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Gerente", "Finanzas"
    )

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    fila.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-puesto").fill("A")
    page.get_by_test_id("empleado-guardar").click()

    campo_puesto = page.get_by_test_id("empleado-puesto")
    expect(campo_puesto).to_be_visible()
    expect(campo_puesto).to_have_value("A")
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_contain_text("Gerente")


def test_cp07_departamento_no_es_catalogo_valido(page, url_api, url_web):
    """CP-07: Rechazar la edición cuando el departamento no es uno de los catálogos válidos."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Tecnología"
    )

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    fila.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    # empleado-departamento es un <select> que solo ofrece departamentos
    # válidos (ver GET /api/departamentos), por lo que un usuario no puede
    # elegir "Mercadotecnia" desde la interfaz. Se inyecta la opción para
    # poder ejercer la validación del backend, tal como la describe el caso.
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
        "Mercadotecnia",
    )
    page.get_by_test_id("empleado-guardar").click()

    expect(campo_departamento).to_be_visible()
    expect(campo_departamento).to_have_value("Mercadotecnia")
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_contain_text("Tecnología")


def test_cp09_baja_con_fecha_igual_a_fecha_ingreso(page, url_api, url_web):
    """CP-09: Dar de baja a un empleado activo con fecha de baja igual a la fecha de ingreso."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Ana López",
        f"ana.lopez.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        fecha_ingreso="2024-01-10",
    )

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    fila.get_by_test_id(f"baja-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-fecha-baja").fill("2024-01-10")
    page.get_by_test_id("confirmar-baja").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    expect(fila.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")


def test_cp11_baja_con_fecha_anterior_a_fecha_ingreso(page, url_api, url_web):
    """CP-11: Rechazar la baja cuando la fecha de baja es anterior a la fecha de ingreso."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Ana López",
        f"ana.lopez.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        fecha_ingreso="2024-01-10",
    )

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    fila.get_by_test_id(f"baja-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-fecha-baja").fill("2024-01-09")
    page.get_by_test_id("confirmar-baja").click()

    campo_fecha_baja = page.get_by_test_id("empleado-fecha-baja")
    expect(campo_fecha_baja).to_be_visible()
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Activo")


def test_cp13_editar_empleado_dado_de_baja(page, url_api, url_web):
    """CP-13: Rechazar la edición de un empleado que ya está dado de baja."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api, "Ana López", f"ana.lopez.{sufijo}@empresa.com", "Analista", "Ventas"
    )
    _dar_de_baja(url_api, empleado["id"], "2024-06-15")

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")
    fila.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-puesto").fill("Supervisor")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-error")).to_have_text(
        "No se puede editar a un empleado dado de baja"
    )
