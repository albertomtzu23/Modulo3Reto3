# language: es
Característica: Solicitar vacaciones
  Como empleado de la empresa
  Quiero solicitar días de vacaciones indicando una fecha de inicio y una de fin
  Para que mi solicitud quede registrada y sepa cuántos días me quedan en el año

  Escenario: Camino feliz - una solicitud válida se registra y descuenta los días hábiles correctos
    Dado un empleado activo con id 7, número EMP-0007 y fecha_ingreso "2018-03-01"
    Y el empleado no tiene solicitudes de vacaciones registradas en 2026
    Cuando se envía "POST /api/empleados/7/vacaciones" con fecha_inicio "2026-12-21" y fecha_fin "2026-12-31"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" de la respuesta es 8
    Y el campo "dias_restantes" de la respuesta es 4
    Y en la pantalla el campo "vacaciones-mensaje" muestra "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."

  Escenario: Los sábados, domingos y festivos dentro del periodo no se descuentan
    Dado un empleado activo con id 8, número EMP-0008 y fecha_ingreso "2018-03-01"
    Y el empleado no tiene solicitudes de vacaciones registradas en 2026
    Cuando se envía "POST /api/empleados/8/vacaciones" con fecha_inicio "2026-09-14" y fecha_fin "2026-09-18"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" de la respuesta es 4
    Y el campo "dias_restantes" de la respuesta es 8

  Escenario: Error - el empleado no existe
    Dado que no existe ningún empleado con id 999
    Cuando se envía "POST /api/empleados/999/vacaciones" con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la respuesta tiene código 404
    Y el campo "detail" de la respuesta es "Empleado no encontrado"

  Escenario: Error - el empleado está dado de baja
    Dado un empleado con id 9, número EMP-0009, fecha_ingreso "2018-03-01" y estado "baja"
    Cuando se envía "POST /api/empleados/9/vacaciones" con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la respuesta tiene código 409
    Y el campo "detail" de la respuesta es "No se pueden solicitar vacaciones para un empleado dado de baja"

  Escenario: Error - la fecha de fin es anterior a la fecha de inicio
    Dado un empleado activo con id 10, número EMP-0010 y fecha_ingreso "2018-03-01"
    Cuando se envía "POST /api/empleados/10/vacaciones" con fecha_inicio "2026-07-10" y fecha_fin "2026-07-06"
    Entonces la respuesta tiene código 400
    Y el campo "detail" de la respuesta es "La fecha de fin no puede ser anterior a la fecha de inicio"

  Escenario: Error - el periodo cruza de un año a otro
    Dado un empleado activo con id 11, número EMP-0011 y fecha_ingreso "2018-03-01"
    Cuando se envía "POST /api/empleados/11/vacaciones" con fecha_inicio "2026-12-28" y fecha_fin "2027-01-08"
    Entonces la respuesta tiene código 400
    Y el campo "detail" de la respuesta es "Las vacaciones deben estar dentro de un mismo año calendario"

  Escenario: Error - el año solicitado no está en la tabla de festivos
    Dado un empleado activo con id 12, número EMP-0012 y fecha_ingreso "2018-03-01"
    Cuando se envía "POST /api/empleados/12/vacaciones" con fecha_inicio "2028-06-01" y fecha_fin "2028-06-05"
    Entonces la respuesta tiene código 400
    Y el campo "detail" de la respuesta es "Solo se pueden solicitar vacaciones en 2026 y 2027"

  Escenario: Límite - primer día en que se cumple exactamente un año de antigüedad
    Dado un empleado activo con id 13, número EMP-0013 y fecha_ingreso "2025-12-21"
    Y el empleado no tiene solicitudes de vacaciones registradas en 2026
    Cuando se envía "POST /api/empleados/13/vacaciones" con fecha_inicio "2026-12-21" y fecha_fin "2026-12-21"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" de la respuesta es 1
    Y el campo "dias_restantes" de la respuesta es 11

  Escenario: Error - antigüedad insuficiente, le faltan días para cumplir el año
    Dado un empleado activo con id 14, número EMP-0014 y fecha_ingreso "2025-12-21"
    Cuando se envía "POST /api/empleados/14/vacaciones" con fecha_inicio "2026-12-18" y fecha_fin "2026-12-20"
    Entonces la respuesta tiene código 400
    Y el campo "detail" de la respuesta es "Se requiere al menos un año de antigüedad a la fecha de inicio"

  Escenario: Error - el periodo no tiene ningún día hábil
    Dado un empleado activo con id 15, número EMP-0015 y fecha_ingreso "2018-03-01"
    Cuando se envía "POST /api/empleados/15/vacaciones" con fecha_inicio "2026-07-11" y fecha_fin "2026-07-12"
    Entonces la respuesta tiene código 400
    Y el campo "detail" de la respuesta es "El periodo no incluye días hábiles"

  Escenario: Límite - se acepta usar exactamente lo que queda del tope anual
    Dado un empleado activo con id 16, número EMP-0016 y fecha_ingreso "2018-03-01"
    Y el empleado ya tiene 5 días hábiles usados en 2026
    Cuando se envía "POST /api/empleados/16/vacaciones" con fecha_inicio "2026-07-13" y fecha_fin "2026-07-21"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" de la respuesta es 7
    Y el campo "dias_restantes" de la respuesta es 0

  Escenario: Error - la solicitud rebasa los días disponibles del año
    Dado un empleado activo con id 17, número EMP-0017 y fecha_ingreso "2018-03-01"
    Y el empleado ya tiene 4 días hábiles usados en 2026
    Cuando se envía "POST /api/empleados/17/vacaciones" con una fecha_inicio y fecha_fin cuyo periodo tiene 9 días hábiles en 2026
    Entonces la respuesta tiene código 400
    Y el campo "detail" de la respuesta es "La solicitud excede los días disponibles: quedan 8 días hábiles"

  Escenario: Consultar el saldo de vacaciones del año
    Dado un empleado activo con id 18, número EMP-0018 y fecha_ingreso "2018-03-01"
    Y el empleado tiene registrada una solicitud del "2026-12-21" al "2026-12-31" con 8 días hábiles en 2026
    Cuando se envía "GET /api/empleados/18/vacaciones?anio=2026"
    Entonces la respuesta tiene código 200
    Y el campo "dias_usados" de la respuesta es 8
    Y el campo "dias_disponibles" de la respuesta es 4
    Y la lista "solicitudes" de la respuesta tiene 1 elemento con fecha_inicio "2026-12-21", fecha_fin "2026-12-31" y dias_habiles 8

# Preguntas abiertas
# - No se especifica si existe un límite de longitud máxima para una sola solicitud de vacaciones (más allá del tope anual de 12 días). Se asume que no hay restricción adicional más allá de las reglas 1, 2 y 3.
# - No se especifica el comportamiento si se envían fechas en 2026 y 2027 simultáneamente en años distintos de saldo ya usado (por ejemplo, si una solicitud de diciembre de 2026 afecta el saldo de 2027). Se asume que cada año calendario tiene su propio saldo independiente, según la regla 2.
