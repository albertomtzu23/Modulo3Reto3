# language: es
# HU-01 · Registrar empleado

Característica: Registrar empleado
  Como persona del área de Recursos Humanos
  quiero registrar a un empleado con su nombre, correo corporativo, puesto, departamento y fecha de ingreso
  para darlo de alta en la empresa

  Escenario: Registro exitoso de un empleado con datos válidos
    Dado que no existe ningún empleado con el correo "ANA.PEREZ@EMPRESA.COM"
    Y es el primer empleado que se registra en el sistema
    Cuando registro un empleado con nombre "Ana Pérez", correo "ANA.PEREZ@EMPRESA.COM", puesto "Analista de RRHH", departamento "Recursos Humanos" y fecha de ingreso "2024-05-01"
    Entonces el sistema responde con código 201
    Y el empleado se guarda con estado "activo"
    Y el correo del empleado se guarda como "ana.perez@empresa.com"
    Y el sistema asigna el número de empleado "EMP-0001"
    Y la pantalla muestra el mensaje de confirmación "Empleado EMP-0001 registrado con éxito"

  Escenario: Rechazo por correo ya registrado
    Dado que ya existe un empleado registrado con el correo "carlos.ruiz@empresa.com"
    Cuando registro un empleado con nombre "Carlos Ruiz", correo "CARLOS.RUIZ@EMPRESA.COM", puesto "Vendedor", departamento "Ventas" y fecha de ingreso "2024-03-10"
    Entonces el sistema responde con código 409
    Y la pantalla muestra el mensaje "El correo ya está registrado"
    Y no se crea un nuevo empleado

  Escenario: Rechazo por correo que no es corporativo
    Dado que no existe ningún empleado con el correo "luis.gomez@gmail.com"
    Cuando registro un empleado con nombre "Luis Gómez", correo "luis.gomez@gmail.com", puesto "Contador", departamento "Finanzas" y fecha de ingreso "2024-02-15"
    Entonces el sistema responde con código 422
    Y la pantalla muestra el mensaje "Usa el correo corporativo @empresa.com"
    Y no se crea un nuevo empleado

  Escenario: Rechazo por nombre que no cumple la longitud mínima
    Dado que no existe ningún empleado con el correo "a@empresa.com"
    Cuando registro un empleado con nombre "A", correo "a@empresa.com", puesto "Operario", departamento "Operaciones" y fecha de ingreso "2024-01-20"
    Entonces el sistema responde con código 422
    Y la pantalla indica que el campo "nombre" debe corregirse
    Y no se crea un nuevo empleado

  Escenario: Rechazo por fecha de ingreso futura
    Dado que no existe ningún empleado con el correo "maria.lopez@empresa.com"
    Y la fecha actual es "2024-06-01"
    Cuando registro un empleado con nombre "María López", correo "maria.lopez@empresa.com", puesto "Desarrolladora", departamento "Tecnología" y fecha de ingreso "2024-06-02"
    Entonces el sistema responde con código 422
    Y la pantalla muestra el mensaje "La fecha de ingreso no puede ser futura"
    Y no se crea un nuevo empleado

# Preguntas abiertas
# - No se especifica el formato exacto del mensaje de confirmación en pantalla; se asumió "Empleado {numero_empleado} registrado con éxito".
# - No se especifica qué pasa si "departamento" recibe un valor fuera de la lista permitida (se asume que cae bajo la regla 3 de "cualquier otro dato inválido", pero no hay mensaje específico definido).
