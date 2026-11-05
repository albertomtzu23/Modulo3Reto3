"""Pruebas de API de HU-02: consulta del directorio de empleados."""
import sqlite3
import uuid
from pathlib import Path

import httpx

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


def test_cp01_ver_directorio_completo(url_api):
    """CP-01: Ver el directorio completo de empleados."""
    sufijo = uuid.uuid4().hex[:8]
    ana = _crear_empleado(
        url_api, "Ana Torres", f"ana.torres.{sufijo}@empresa.com", "Desarrolladora", "Tecnología"
    )
    luis = _crear_empleado(
        url_api, "Luis Gómez", f"luis.gomez.{sufijo}@empresa.com", "Vendedor", "Ventas"
    )

    respuesta = httpx.get(f"{url_api}/api/empleados")
    assert respuesta.status_code == 200
    empleados = respuesta.json()

    # La base es persistente y sin limpieza entre corridas: en vez de exigir
    # exactamente 2 elementos en total, se verifica que ambos creados aquí
    # aparecen con sus datos correctos.
    por_correo = {e["correo"]: e for e in empleados}
    assert ana["correo"] in por_correo
    assert luis["correo"] in por_correo
    assert por_correo[ana["correo"]]["nombre"] == "Ana Torres"
    assert por_correo[ana["correo"]]["puesto"] == "Desarrolladora"
    assert por_correo[ana["correo"]]["departamento"] == "Tecnología"
    assert por_correo[ana["correo"]]["estado"] == "activo"
    assert por_correo[luis["correo"]]["nombre"] == "Luis Gómez"
    assert por_correo[luis["correo"]]["puesto"] == "Vendedor"
    assert por_correo[luis["correo"]]["departamento"] == "Ventas"
    assert por_correo[luis["correo"]]["estado"] == "activo"


def test_cp03_buscar_por_nombre_sin_distinguir_mayusculas(url_api):
    """CP-03: Buscar un empleado por nombre sin distinguir mayúsculas de minúsculas."""
    sufijo = uuid.uuid4().hex[:8]
    nombre = f"María López {sufijo}"
    correo = f"maria.lopez.{sufijo}@empresa.com"
    _crear_empleado(url_api, nombre, correo, "Analista", "Finanzas")

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": f"MARÍA LÓPEZ {sufijo}"})
    assert respuesta.status_code == 200
    empleados = respuesta.json()
    assert len(empleados) == 1
    assert empleados[0]["nombre"] == nombre
    assert empleados[0]["correo"] == correo


def test_cp05_buscar_por_correo_sin_distinguir_mayusculas(url_api):
    """CP-05: Buscar un empleado por correo sin distinguir mayúsculas de minúsculas."""
    sufijo = uuid.uuid4().hex[:8]
    correo = f"carlos.ruiz.{sufijo}@empresa.com"
    _crear_empleado(url_api, "Carlos Ruiz", correo, "Contador", "Finanzas")

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": correo.upper()})
    assert respuesta.status_code == 200
    empleados = respuesta.json()
    assert len(empleados) == 1
    assert empleados[0]["correo"] == correo
    assert empleados[0]["nombre"] == "Carlos Ruiz"


def test_cp07_filtrar_por_departamento(url_api):
    """CP-07: Filtrar empleados por departamento."""
    sufijo = uuid.uuid4().hex[:8]
    sofia = _crear_empleado(
        url_api, "Sofía Reyes", f"sofia.reyes.{sufijo}@empresa.com", "Analista Financiera", "Finanzas"
    )
    _crear_empleado(
        url_api, "Jorge Paredes", f"jorge.paredes.{sufijo}@empresa.com", "Desarrollador", "Tecnología"
    )

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"departamento": "Finanzas"})
    assert respuesta.status_code == 200
    empleados = respuesta.json()

    # El filtro puede acumular empleados de Finanzas de otras corridas; lo
    # relevante es que no se cuelen otros departamentos y que Sofía esté.
    assert all(e["departamento"] == "Finanzas" for e in empleados)
    coincidencias = [e for e in empleados if e["correo"] == sofia["correo"]]
    assert len(coincidencias) == 1
    assert coincidencias[0]["nombre"] == "Sofía Reyes"


def test_cp09_empleado_de_baja_sigue_en_directorio(url_api):
    """CP-09: Un empleado dado de baja sigue apareciendo en el directorio."""
    sufijo = uuid.uuid4().hex[:8]
    pedro = _crear_empleado(
        url_api, "Pedro Salas", f"pedro.salas.{sufijo}@empresa.com", "Operador", "Operaciones"
    )
    _marcar_baja(pedro["id"], "2024-05-10")

    respuesta = httpx.get(f"{url_api}/api/empleados")
    assert respuesta.status_code == 200
    empleados = respuesta.json()
    coincidencias = [e for e in empleados if e["correo"] == pedro["correo"]]
    assert len(coincidencias) == 1
    assert coincidencias[0]["estado"] == "baja"
    assert coincidencias[0]["fecha_baja"] == "2024-05-10"


def test_cp11_buscar_texto_sin_coincidencias(url_api):
    """CP-11: Buscar un texto que no coincide con ningún empleado."""
    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": "xyz-no-existe"})
    assert respuesta.status_code == 200
    assert respuesta.json() == []
