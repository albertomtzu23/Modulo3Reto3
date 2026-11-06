"""API de gestión de empleados."""
import unicodedata
from datetime import date, datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from basedatos import Base, engine, obtener_sesion
from esquemas import (
    EmpleadoBaja,
    EmpleadoCrear,
    EmpleadoEditar,
    EmpleadoSalida,
    VacacionesCrear,
    VacacionesSaldo,
    VacacionesSalida,
)
from festivos import FESTIVOS, dias_habiles
from modelos import DEPARTAMENTOS_VALIDOS, Empleado, Vacaciones
from vacaciones import cumple_antiguedad

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestión de empleados")

TOPE_ANUAL_DIAS_VACACIONES = 12


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(request, exc: RequestValidationError) -> JSONResponse:
    primer_error = exc.errors()[0]
    mensaje = str(primer_error.get("msg", "Datos inválidos"))
    prefijo = "Value error, "
    if mensaje.startswith(prefijo):
        mensaje = mensaje[len(prefijo):]
    else:
        campo = primer_error.get("loc", ["campo"])[-1]
        mensaje = f"El campo '{campo}' no es válido."
    return JSONResponse(status_code=422, content={"detail": mensaje})


def normalizar_texto(texto: str) -> str:
    """Pasa a minúsculas y quita acentos para comparar sin distinguirlos."""
    sin_acentos = unicodedata.normalize("NFKD", texto)
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    return sin_acentos.lower()


def siguiente_numero_empleado(sesion: Session) -> str:
    ultimo = sesion.query(Empleado).order_by(Empleado.id.desc()).first()
    consecutivo = int(ultimo.numero_empleado.split("-")[1]) + 1 if ultimo else 1
    return f"EMP-{consecutivo:04d}"


@app.get("/api/salud")
def salud() -> dict:
    return {"estado": "ok"}


@app.get("/api/departamentos")
def listar_departamentos() -> list[str]:
    return DEPARTAMENTOS_VALIDOS


@app.get("/api/empleados", response_model=list[EmpleadoSalida])
def listar_empleados(
    buscar: str | None = Query(default=None),
    departamento: str | None = Query(default=None),
    sesion: Session = Depends(obtener_sesion),
) -> list[Empleado]:
    empleados = sesion.query(Empleado).order_by(Empleado.id).all()

    if departamento is not None:
        empleados = [e for e in empleados if e.departamento == departamento]

    if buscar:
        texto = normalizar_texto(buscar)
        empleados = [
            e
            for e in empleados
            if texto in normalizar_texto(e.nombre) or texto in normalizar_texto(e.correo)
        ]

    return empleados


@app.post("/api/empleados", response_model=EmpleadoSalida, status_code=201)
def registrar_empleado(
    datos: EmpleadoCrear, sesion: Session = Depends(obtener_sesion)
) -> Empleado:
    if datos.departamento not in DEPARTAMENTOS_VALIDOS:
        raise HTTPException(
            status_code=422,
            detail=(
                "El campo 'departamento' debe corregirse: usa uno de "
                f"{', '.join(DEPARTAMENTOS_VALIDOS)}"
            ),
        )

    if datos.fecha_ingreso > date.today():
        raise HTTPException(
            status_code=422, detail="La fecha de ingreso no puede ser futura"
        )

    existente = sesion.query(Empleado).filter(Empleado.correo == datos.correo).first()
    if existente is not None:
        raise HTTPException(status_code=409, detail="El correo ya está registrado")

    empleado = Empleado(
        numero_empleado=siguiente_numero_empleado(sesion),
        nombre=datos.nombre,
        correo=datos.correo,
        puesto=datos.puesto,
        departamento=datos.departamento,
        fecha_ingreso=datos.fecha_ingreso,
        estado="activo",
        fecha_baja=None,
        creado_en=datetime.utcnow(),
    )
    sesion.add(empleado)
    sesion.commit()
    sesion.refresh(empleado)
    return empleado


@app.put("/api/empleados/{id}", response_model=EmpleadoSalida)
def editar_empleado(
    id: int, datos: EmpleadoEditar, sesion: Session = Depends(obtener_sesion)
) -> Empleado:
    empleado = sesion.get(Empleado, id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se puede editar a un empleado dado de baja",
        )

    if datos.departamento is not None and datos.departamento not in DEPARTAMENTOS_VALIDOS:
        raise HTTPException(
            status_code=422,
            detail=(
                "El campo 'departamento' debe corregirse: usa uno de "
                f"{', '.join(DEPARTAMENTOS_VALIDOS)}"
            ),
        )

    if datos.puesto is not None:
        empleado.puesto = datos.puesto
    if datos.departamento is not None:
        empleado.departamento = datos.departamento

    sesion.commit()
    sesion.refresh(empleado)
    return empleado


@app.post("/api/empleados/{id}/baja", response_model=EmpleadoSalida)
def dar_de_baja_empleado(
    id: int, datos: EmpleadoBaja, sesion: Session = Depends(obtener_sesion)
) -> Empleado:
    empleado = sesion.get(Empleado, id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if datos.fecha_baja < empleado.fecha_ingreso:
        raise HTTPException(
            status_code=422,
            detail=(
                "El campo 'fecha_baja' debe corregirse: no puede ser anterior "
                "a la fecha de ingreso"
            ),
        )

    empleado.estado = "baja"
    empleado.fecha_baja = datos.fecha_baja
    sesion.commit()
    sesion.refresh(empleado)
    return empleado


def dias_usados_en_anio(sesion: Session, empleado_id: int, anio: int) -> int:
    solicitudes = (
        sesion.query(Vacaciones)
        .filter(
            Vacaciones.empleado_id == empleado_id,
            Vacaciones.fecha_inicio >= date(anio, 1, 1),
            Vacaciones.fecha_inicio <= date(anio, 12, 31),
        )
        .all()
    )
    return sum(solicitud.dias_habiles for solicitud in solicitudes)


@app.post(
    "/api/empleados/{id}/vacaciones", response_model=VacacionesSalida, status_code=201
)
def solicitar_vacaciones(
    id: int, datos: VacacionesCrear, sesion: Session = Depends(obtener_sesion)
) -> dict:
    empleado = sesion.get(Empleado, id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se pueden solicitar vacaciones para un empleado dado de baja",
        )

    if datos.fecha_fin < datos.fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio",
        )

    if datos.fecha_inicio.year != datos.fecha_fin.year:
        raise HTTPException(
            status_code=400,
            detail="Las vacaciones deben estar dentro de un mismo año calendario",
        )

    anio = datos.fecha_inicio.year
    if anio not in FESTIVOS:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden solicitar vacaciones en 2026 y 2027",
        )

    if not cumple_antiguedad(empleado.fecha_ingreso, datos.fecha_inicio):
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un año de antigüedad a la fecha de inicio",
        )

    dias_solicitados = dias_habiles(datos.fecha_inicio, datos.fecha_fin)
    if dias_solicitados == 0:
        raise HTTPException(status_code=400, detail="El periodo no incluye días hábiles")

    disponibles = TOPE_ANUAL_DIAS_VACACIONES - dias_usados_en_anio(sesion, id, anio)
    if dias_solicitados > disponibles:
        raise HTTPException(
            status_code=400,
            detail=(
                "La solicitud excede los días disponibles: "
                f"quedan {disponibles} días hábiles"
            ),
        )

    solicitud = Vacaciones(
        empleado_id=id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        dias_habiles=dias_solicitados,
    )
    sesion.add(solicitud)
    sesion.commit()
    sesion.refresh(solicitud)

    return {
        "id": solicitud.id,
        "empleado_id": solicitud.empleado_id,
        "fecha_inicio": solicitud.fecha_inicio,
        "fecha_fin": solicitud.fecha_fin,
        "dias_habiles": solicitud.dias_habiles,
        "dias_restantes": disponibles - dias_solicitados,
    }


@app.get("/api/empleados/{id}/vacaciones", response_model=VacacionesSaldo)
def consultar_vacaciones(
    id: int,
    anio: int | None = Query(default=None),
    sesion: Session = Depends(obtener_sesion),
) -> dict:
    empleado = sesion.get(Empleado, id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    anio_consulta = anio or date.today().year
    solicitudes = (
        sesion.query(Vacaciones)
        .filter(
            Vacaciones.empleado_id == id,
            Vacaciones.fecha_inicio >= date(anio_consulta, 1, 1),
            Vacaciones.fecha_inicio <= date(anio_consulta, 12, 31),
        )
        .order_by(Vacaciones.fecha_inicio)
        .all()
    )
    dias_usados = sum(solicitud.dias_habiles for solicitud in solicitudes)

    return {
        "empleado_id": id,
        "anio": anio_consulta,
        "dias_usados": dias_usados,
        "dias_disponibles": TOPE_ANUAL_DIAS_VACACIONES - dias_usados,
        "solicitudes": solicitudes,
    }
