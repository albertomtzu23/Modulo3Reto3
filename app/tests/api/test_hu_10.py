"""Pruebas de API de HU-10: vacaciones."""
import uuid

import httpx

EMPLEADO_INEXISTENTE = 999999999


def _crear_empleado(
    url_api: str,
    nombre: str,
    correo: str,
    puesto: str,
    departamento: str,
    fecha_ingreso: str,
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


def _solicitar_vacaciones(
    url_api: str, empleado_id: int, fecha_inicio: str, fecha_fin: str
) -> httpx.Response:
    return httpx.post(
        f"{url_api}/api/empleados/{empleado_id}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )


def _registrar_vacaciones(
    url_api: str, empleado_id: int, fecha_inicio: str, fecha_fin: str
) -> dict:
    respuesta = _solicitar_vacaciones(url_api, empleado_id, fecha_inicio, fecha_fin)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_cp01_camino_feliz_dias_habiles_correctos(url_api):
    """CP-01: Camino feliz - una solicitud válida se registra y descuenta los días hábiles correctos."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Ana López",
        f"ana.lopez.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-12-21", "2026-12-31")

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 8
    assert cuerpo["dias_restantes"] == 4


def test_cp03_sabados_domingos_y_festivos_no_se_descuentan(url_api):
    """CP-03: Los sábados, domingos y festivos dentro del periodo no se descuentan."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Carlos Ruiz",
        f"carlos.ruiz.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-09-14", "2026-09-18")

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 4
    assert cuerpo["dias_restantes"] == 8


def test_cp05_el_empleado_no_existe(url_api):
    """CP-05: Error - el empleado no existe."""
    respuesta = _solicitar_vacaciones(
        url_api, EMPLEADO_INEXISTENTE, "2026-07-06", "2026-07-10"
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp06_el_empleado_esta_dado_de_baja(url_api):
    """CP-06: Error - el empleado está dado de baja."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "María Gómez",
        f"maria.gomez.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )
    _dar_de_baja(url_api, empleado["id"], "2024-06-15")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 409
    assert (
        respuesta.json()["detail"]
        == "No se pueden solicitar vacaciones para un empleado dado de baja"
    )


def test_cp07_la_fecha_de_fin_es_anterior_a_la_fecha_de_inicio(url_api):
    """CP-07: Error - la fecha de fin es anterior a la fecha de inicio."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Luis Torres",
        f"luis.torres.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-07-10", "2026-07-06")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp09_el_periodo_cruza_de_un_anio_a_otro(url_api):
    """CP-09: Error - el periodo cruza de un año a otro."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Sofía Reyes",
        f"sofia.reyes.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-12-28", "2027-01-08")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp11_el_anio_solicitado_no_esta_en_la_tabla_de_festivos(url_api):
    """CP-11: Error - el año solicitado no está en la tabla de festivos."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Jorge Díaz",
        f"jorge.diaz.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2028-06-01", "2028-06-05")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"] == "Solo se pueden solicitar vacaciones en 2026 y 2027"
    )


def test_cp13_primer_dia_en_que_se_cumple_exactamente_un_anio_de_antiguedad(url_api):
    """CP-13: Límite - primer día en que se cumple exactamente un año de antigüedad."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Elena Castro",
        f"elena.castro.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2025-12-21",
    )

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-12-21", "2026-12-21")

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 1
    assert cuerpo["dias_restantes"] == 11


def test_cp15_antiguedad_insuficiente_le_faltan_dias_para_cumplir_el_anio(url_api):
    """CP-15: Error - antigüedad insuficiente, le faltan días para cumplir el año."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Pablo Herrera",
        f"pablo.herrera.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2025-12-21",
    )

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-12-18", "2026-12-20")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp17_el_periodo_no_tiene_ningun_dia_habil(url_api):
    """CP-17: Error - el periodo no tiene ningún día hábil."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Valeria Núñez",
        f"valeria.nunez.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-07-11", "2026-07-12")

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp19_se_acepta_usar_exactamente_lo_que_queda_del_tope_anual(url_api):
    """CP-19: Límite - se acepta usar exactamente lo que queda del tope anual."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Diego Molina",
        f"diego.molina.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )
    _registrar_vacaciones(url_api, empleado["id"], "2026-01-05", "2026-01-09")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-07-13", "2026-07-21")

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 7
    assert cuerpo["dias_restantes"] == 0


def test_cp21_la_solicitud_rebasa_los_dias_disponibles_del_anio(url_api):
    """CP-21: Error - la solicitud rebasa los días disponibles del año."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Camila Vargas",
        f"camila.vargas.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )
    _registrar_vacaciones(url_api, empleado["id"], "2026-01-05", "2026-01-08")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-08-03", "2026-08-13")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 8 días hábiles"
    )


def test_cp23_consultar_el_saldo_de_vacaciones_del_anio(url_api):
    """CP-23: Consultar el saldo de vacaciones del año."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Ricardo Peña",
        f"ricardo.pena.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )
    _registrar_vacaciones(url_api, empleado["id"], "2026-12-21", "2026-12-31")

    respuesta = httpx.get(f"{url_api}/api/empleados/{empleado['id']}/vacaciones?anio=2026")

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_usados"] == 8
    assert cuerpo["dias_disponibles"] == 4
    assert len(cuerpo["solicitudes"]) == 1
    solicitud = cuerpo["solicitudes"][0]
    assert solicitud["fecha_inicio"] == "2026-12-21"
    assert solicitud["fecha_fin"] == "2026-12-31"
    assert solicitud["dias_habiles"] == 8
