"""Pruebas E2E de HU-10: vacaciones."""
import uuid

import httpx
from playwright.sync_api import expect


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


def _registrar_vacaciones(
    url_api: str, empleado_id: int, fecha_inicio: str, fecha_fin: str
) -> dict:
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado_id}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _abrir_vacaciones(page, url_web, empleado_id):
    page.goto(url_web)
    fila = page.get_by_test_id(f"fila-empleado-{empleado_id}")
    expect(fila).to_be_visible()
    fila.get_by_test_id(f"vacaciones-abrir-{empleado_id}").click()
    expect(page.get_by_test_id("vacaciones-disponibles")).not_to_have_text("...")


def test_cp02_camino_feliz_dias_habiles_correctos(page, url_api, url_web):
    """CP-02: Camino feliz - una solicitud válida se registra y descuenta los días hábiles correctos."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Ana López",
        f"ana.lopez.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )

    _abrir_vacaciones(page, url_web, empleado["id"])
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-21")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-31")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."
    )


def test_cp04_sabados_domingos_y_festivos_no_se_descuentan(page, url_api, url_web):
    """CP-04: Los sábados, domingos y festivos dentro del periodo no se descuentan."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Carlos Ruiz",
        f"carlos.ruiz.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )

    _abrir_vacaciones(page, url_web, empleado["id"])
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-09-14")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-09-18")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 4 días hábiles. Te quedan 8 días hábiles en 2026."
    )


def test_cp08_la_fecha_de_fin_es_anterior_a_la_fecha_de_inicio(page, url_api, url_web):
    """CP-08: Error - la fecha de fin es anterior a la fecha de inicio."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Luis Torres",
        f"luis.torres.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )

    _abrir_vacaciones(page, url_web, empleado["id"])
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-10")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-06")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp10_el_periodo_cruza_de_un_anio_a_otro(page, url_api, url_web):
    """CP-10: Error - el periodo cruza de un año a otro."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Sofía Reyes",
        f"sofia.reyes.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )

    _abrir_vacaciones(page, url_web, empleado["id"])
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-28")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2027-01-08")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp12_el_anio_solicitado_no_esta_en_la_tabla_de_festivos(page, url_api, url_web):
    """CP-12: Error - el año solicitado no está en la tabla de festivos."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Jorge Díaz",
        f"jorge.diaz.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )

    _abrir_vacaciones(page, url_web, empleado["id"])
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2028-06-01")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2028-06-05")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solo se pueden solicitar vacaciones en 2026 y 2027"
    )


def test_cp14_primer_dia_en_que_se_cumple_exactamente_un_anio_de_antiguedad(
    page, url_api, url_web
):
    """CP-14: Límite - primer día en que se cumple exactamente un año de antigüedad."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Elena Castro",
        f"elena.castro.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2025-12-21",
    )

    _abrir_vacaciones(page, url_web, empleado["id"])
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-21")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-21")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 1 días hábiles. Te quedan 11 días hábiles en 2026."
    )


def test_cp16_antiguedad_insuficiente_le_faltan_dias_para_cumplir_el_anio(
    page, url_api, url_web
):
    """CP-16: Error - antigüedad insuficiente, le faltan días para cumplir el año."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Pablo Herrera",
        f"pablo.herrera.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2025-12-21",
    )

    _abrir_vacaciones(page, url_web, empleado["id"])
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-18")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-20")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp18_el_periodo_no_tiene_ningun_dia_habil(page, url_api, url_web):
    """CP-18: Error - el periodo no tiene ningún día hábil."""
    sufijo = uuid.uuid4().hex[:8]
    empleado = _crear_empleado(
        url_api,
        "Valeria Núñez",
        f"valeria.nunez.{sufijo}@empresa.com",
        "Analista",
        "Ventas",
        "2018-03-01",
    )

    _abrir_vacaciones(page, url_web, empleado["id"])
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-11")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-12")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "El periodo no incluye días hábiles"
    )


def test_cp20_se_acepta_usar_exactamente_lo_que_queda_del_tope_anual(page, url_api, url_web):
    """CP-20: Límite - se acepta usar exactamente lo que queda del tope anual."""
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

    _abrir_vacaciones(page, url_web, empleado["id"])
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-13")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-21")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 7 días hábiles. Te quedan 0 días hábiles en 2026."
    )


def test_cp22_la_solicitud_rebasa_los_dias_disponibles_del_anio(page, url_api, url_web):
    """CP-22: Error - la solicitud rebasa los días disponibles del año."""
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

    _abrir_vacaciones(page, url_web, empleado["id"])
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-08-03")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-08-13")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "La solicitud excede los días disponibles: quedan 8 días hábiles"
    )


def test_cp24_consultar_el_saldo_de_vacaciones_del_anio(page, url_api, url_web):
    """CP-24: Consultar el saldo de vacaciones del año."""
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

    _abrir_vacaciones(page, url_web, empleado["id"])

    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("4")
