# language: es

Característica: Editar y dar de baja a un empleado
  Como persona del área de Recursos Humanos
  Quiero cambiar el puesto y el departamento de un empleado, y poder darlo de baja
  Para mantener el directorio al día sin perder el historial

  Escenario: Editar puesto y departamento de un empleado activo
    Dado un empleado activo con id 1, número de empleado "EMP-0001", correo "ana.lopez@empresa.com", puesto "Analista" y departamento "Ventas"
    Cuando edito el puesto a "Analista Senior" y el departamento a "Finanzas"
    Entonces la API responde 200
    Y el empleado con id 1 tiene puesto "Analista Senior" y departamento "Finanzas"
    Y se muestra el mensaje en "mensaje-exito"

  Escenario: El correo y el número de empleado no se modifican aunque se intenten editar
    Dado un empleado activo con id 2, número de empleado "EMP-0002" y correo "carlos.ruiz@empresa.com"
    Cuando edito al empleado enviando número de empleado "EMP-9999" y correo "otro@empresa.com"
    Entonces la API responde 200
    Y el empleado con id 2 conserva el número de empleado "EMP-0002" y el correo "carlos.ruiz@empresa.com"

  Escenario: Rechazar la edición cuando el puesto queda fuera del rango permitido
    Dado un empleado activo con id 3 y puesto "Gerente"
    Cuando edito el puesto a "A"
    Entonces la API responde 422
    Y la pantalla muestra el campo "puesto" para corregir

  Escenario: Rechazar la edición cuando el departamento no es uno de los catálogos válidos
    Dado un empleado activo con id 4 y departamento "Tecnología"
    Cuando edito el departamento a "Mercadotecnia"
    Entonces la API responde 422
    Y la pantalla muestra el campo "departamento" para corregir

  Escenario: Dar de baja a un empleado activo con fecha de baja igual a la fecha de ingreso (límite: primer día válido)
    Dado un empleado activo con id 5 y fecha_ingreso "2024-01-10"
    Cuando doy de baja al empleado con id 5 usando fecha_baja "2024-01-10"
    Entonces la API responde 200
    Y el empleado con id 5 tiene estado "baja" y fecha_baja "2024-01-10"
    Y el empleado sigue apareciendo en "tabla-empleados" con estado "Baja" en "estado-empleado-5"

  Escenario: Rechazar la baja cuando la fecha de baja es anterior a la fecha de ingreso
    Dado un empleado activo con id 6 y fecha_ingreso "2024-01-10"
    Cuando doy de baja al empleado con id 6 usando fecha_baja "2024-01-09"
    Entonces la API responde 422
    Y la pantalla muestra el campo "fecha_baja" para corregir

  Escenario: Rechazar la edición de un empleado que ya está dado de baja
    Dado un empleado dado de baja con id 7
    Cuando edito el puesto del empleado con id 7 a "Supervisor"
    Entonces la API responde 409
    Y el mensaje de error es "No se puede editar a un empleado dado de baja"

# Preguntas abiertas
# - Las reglas de negocio indican que un dato inválido (regla 3) y una fecha_baja anterior a la
#   fecha de ingreso responden 422 "y la pantalla muestra qué campo corregir", pero no dan el texto
#   exacto del mensaje. Los escenarios de error usan una descripción del campo a corregir; falta
#   confirmar el texto literal que debe mostrar la pantalla (mensaje-error) en estos casos.
# - No se especifica si intentar enviar un número de empleado o correo distintos al editar debe
#   generar un error (por ejemplo 422) o simplemente ignorarse. El escenario "El correo y el número
#   de empleado no se modifican..." asume que la API ignora esos campos y responde 200; falta
#   confirmar este comportamiento con el dueño del producto.
