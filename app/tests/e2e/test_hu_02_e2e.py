"""Pruebas E2E de HU-02: directorio de empleados."""
import sqlite3
import uuid
from pathlib import Path

import httpx
from playwright.sync_api import expect

# Base de datos real del backend: la API no expone forma de dar de baja a un
# empleado, así que esta es la única manera de preparar esa precondición.
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


def test_cp02_ver_directorio_completo(page, url_api, url_web):
    """CP-02: Ver el directorio completo de empleados."""
    sufijo = uuid.uuid4().hex[:8]
    ana = _crear_empleado(
        url_api, "Ana Torres", f"ana.torres.{sufijo}@empresa.com", "Desarrolladora", "Tecnología"
    )
    luis = _crear_empleado(
        url_api, "Luis Gómez", f"luis.gomez.{sufijo}@empresa.com", "Vendedor", "Ventas"
    )

    page.goto(url_web)

    fila_ana = page.get_by_test_id(f"fila-empleado-{ana['id']}")
    fila_luis = page.get_by_test_id(f"fila-empleado-{luis['id']}")

    expect(page.get_by_test_id("tabla-empleados")).to_be_visible()
    expect(fila_ana).to_be_visible()
    expect(fila_luis).to_be_visible()
    expect(fila_ana.get_by_test_id(f"numero-empleado-{ana['id']}")).to_have_text(
        ana["numero_empleado"]
    )
    expect(fila_ana.get_by_test_id(f"estado-empleado-{ana['id']}")).to_have_text("Activo")
    expect(fila_luis.get_by_test_id(f"numero-empleado-{luis['id']}")).to_have_text(
        luis["numero_empleado"]
    )
    expect(fila_luis.get_by_test_id(f"estado-empleado-{luis['id']}")).to_have_text("Activo")


def test_cp04_buscar_por_nombre_sin_distinguir_mayusculas(page, url_api, url_web):
    """CP-04: Buscar un empleado por nombre sin distinguir mayúsculas de minúsculas."""
    sufijo = uuid.uuid4().hex[:8]
    nombre = f"María López {sufijo}"
    maria = _crear_empleado(
        url_api, nombre, f"maria.lopez.{sufijo}@empresa.com", "Analista", "Finanzas"
    )

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(f"MARÍA LÓPEZ {sufijo}")

    tabla = page.get_by_test_id("tabla-empleados")
    filas = tabla.locator("[data-testid^='fila-empleado-']")
    expect(filas).to_have_count(1)
    fila = page.get_by_test_id(f"fila-empleado-{maria['id']}")
    expect(fila).to_be_visible()
    expect(fila.get_by_test_id(f"numero-empleado-{maria['id']}")).to_have_text(
        maria["numero_empleado"]
    )


def test_cp06_buscar_por_correo_sin_distinguir_mayusculas(page, url_api, url_web):
    """CP-06: Buscar un empleado por correo sin distinguir mayúsculas de minúsculas."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"carlos.ruiz.{sufijo}@empresa.com"
    carlos = _crear_empleado(url_api, "Carlos Ruiz", correo, "Contador", "Finanzas")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(correo.upper())

    tabla = page.get_by_test_id("tabla-empleados")
    filas = tabla.locator("[data-testid^='fila-empleado-']")
    expect(filas).to_have_count(1)
    fila = page.get_by_test_id(f"fila-empleado-{carlos['id']}")
    expect(fila).to_be_visible()
    expect(fila.get_by_test_id(f"numero-empleado-{carlos['id']}")).to_have_text(
        carlos["numero_empleado"]
    )


def test_cp08_filtrar_por_departamento(page, url_api, url_web):
    """CP-08: Filtrar empleados por departamento."""
    sufijo = uuid.uuid4().hex[:8]
    sofia = _crear_empleado(
        url_api, "Sofía Reyes", f"sofia.reyes.{sufijo}@empresa.com", "Analista Financiera", "Finanzas"
    )
    _crear_empleado(
        url_api, "Jorge Paredes", f"jorge.paredes.{sufijo}@empresa.com", "Desarrollador", "Tecnología"
    )

    page.goto(url_web)
    page.get_by_test_id("filtro-departamento").select_option("Finanzas")

    fila = page.get_by_test_id(f"fila-empleado-{sofia['id']}")
    expect(fila).to_be_visible()
    expect(fila.get_by_test_id(f"numero-empleado-{sofia['id']}")).to_have_text(
        sofia["numero_empleado"]
    )

    # El filtro puede acumular empleados de Finanzas de otras corridas; lo
    # relevante es que ninguna fila visible pertenezca a otro departamento.
    filas = page.get_by_test_id("tabla-empleados").locator("[data-testid^='fila-empleado-']")
    total = filas.count()
    for indice in range(total):
        assert "Finanzas" in filas.nth(indice).inner_text()


def test_cp10_empleado_de_baja_sigue_en_directorio(page, url_api, url_web):
    """CP-10: Un empleado dado de baja sigue apareciendo en el directorio."""
    sufijo = uuid.uuid4().hex[:8]
    pedro = _crear_empleado(
        url_api, "Pedro Salas", f"pedro.salas.{sufijo}@empresa.com", "Operador", "Operaciones"
    )
    _marcar_baja(pedro["id"], "2024-05-10")

    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{pedro['id']}")
    expect(fila).to_be_visible()
    expect(fila.get_by_test_id(f"estado-empleado-{pedro['id']}")).to_have_text("Baja")


def test_cp12_buscar_texto_sin_coincidencias(page, url_web):
    """CP-12: Buscar un texto que no coincide con ningún empleado."""
    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill("xyz-no-existe")

    expect(page.get_by_test_id("sin-resultados")).to_have_text("No se encontraron resultados")
    expect(page.locator("[data-testid^='fila-empleado-']")).to_have_count(0)
