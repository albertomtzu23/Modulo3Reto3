# language: es
Característica: Editar y dar de baja a un empleado
  Como persona del área de Recursos Humanos
  Quiero cambiar el puesto y el departamento de un empleado, y poder darlo de baja
  Para mantener el directorio al día sin perder el historial

  Antecedentes:
    Dado que existe un empleado activo con numero_empleado "EMP-0010", correo "ana.lopez@empresa.com", puesto "Analista" y departamento "Finanzas"

  Escenario: Editar puesto y departamento de un empleado activo
    Dado el empleado "EMP-0010" con estado "activo"
    Cuando edito el puesto a "Analista Senior" y el departamento a "Tecnología"
    Entonces la respuesta tiene código 200
    Y el empleado "EMP-0010" queda con puesto "Analista Senior" y departamento "Tecnología"
    Y el numero_empleado sigue siendo "EMP-0010"
    Y el correo sigue siendo "ana.lopez@empresa.com"

  Escenario: Error al editar con un departamento que no está en la lista permitida
    Dado el empleado "EMP-0010" con estado "activo"
    Cuando edito el departamento a "Marketing"
    Entonces la respuesta tiene código 422
    Y la pantalla muestra que el campo "departamento" debe corregirse

  Escenario: Error al editar con un puesto demasiado corto
    Dado el empleado "EMP-0010" con estado "activo"
    Cuando edito el puesto a "A"
    Entonces la respuesta tiene código 422
    Y la pantalla muestra que el campo "puesto" debe corregirse

  Escenario: Error al intentar editar a un empleado dado de baja
    Dado el empleado "EMP-0010" con estado "baja"
    Cuando edito el puesto a "Analista Senior"
    Entonces la respuesta tiene código 409
    Y el mensaje es "No se puede editar a un empleado dado de baja"

  Escenario: Dar de baja a un empleado activo
    Dado el empleado "EMP-0010" con estado "activo" y fecha_ingreso "2020-03-01"
    Cuando doy de baja al empleado "EMP-0010" con fecha_baja "2024-06-15"
    Entonces la respuesta tiene código 200
    Y el empleado "EMP-0010" queda con estado "baja" y fecha_baja "2024-06-15"
    Y el empleado "EMP-0010" sigue apareciendo en el directorio

  Escenario: Error al dar de baja con una fecha de baja anterior a la fecha de ingreso
    Dado el empleado "EMP-0010" con estado "activo" y fecha_ingreso "2020-03-01"
    Cuando doy de baja al empleado "EMP-0010" con fecha_baja "2019-01-10"
    Entonces la respuesta tiene código 422
    Y la pantalla muestra que el campo "fecha_baja" debe corregirse

# Preguntas abiertas
# - ¿Qué debe responder el sistema si en una edición se envían numero_empleado o correo con un valor distinto al actual? (¿se ignoran silenciosamente o se devuelve un error, por ejemplo 422?)
# - ¿Cuál es el mensaje exacto y el código de respuesta cuando la fecha_baja es anterior a la fecha_ingreso? Se asumió 422 por analogía con la regla 3, pero no hay un mensaje definido en las reglas de negocio.
# - ¿Se puede dar de baja nuevamente a un empleado que ya está en estado "baja"? No hay una regla que lo defina.
# - ¿Se pueden editar otros campos del empleado (nombre, fecha_ingreso) además de puesto y departamento? La historia solo menciona puesto y departamento.
