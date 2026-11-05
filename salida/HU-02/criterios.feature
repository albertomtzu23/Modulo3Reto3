# language: es

Característica: Consultar el directorio de empleados
  Como persona del área de Recursos Humanos
  Quiero ver el directorio de empleados, buscarlos por nombre o correo y filtrarlos por departamento
  Para encontrar rápido a una persona

  Escenario: Ver el directorio completo de empleados
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | puesto          | departamento      | estado |
      | EMP-0001        | Ana Torres    | Analista        | Tecnología        | activo |
      | EMP-0002        | Luis Gómez    | Ejecutivo       | Ventas            | activo |
    Cuando consulto el directorio de empleados
    Entonces veo 2 empleados en el directorio
    Y cada fila muestra el número de empleado, nombre, puesto, departamento y estado

  Escenario: Buscar un empleado por nombre sin distinguir mayúsculas de minúsculas
    Dado que existe el empleado "María López" con correo "maria.lopez@empresa.com"
    Cuando busco en el directorio el texto "maría lópez"
    Entonces veo 1 resultado
    Y el resultado corresponde al empleado "María López"

  Escenario: Buscar un empleado por correo sin distinguir mayúsculas de minúsculas
    Dado que existe el empleado "Carlos Ruiz" con correo "carlos.ruiz@empresa.com"
    Cuando busco en el directorio el texto "CARLOS.RUIZ@EMPRESA.COM"
    Entonces veo 1 resultado
    Y el resultado corresponde al empleado "Carlos Ruiz"

  Escenario: Filtrar empleados por departamento
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | puesto          | departamento      | estado |
      | EMP-0003        | Sofía Reyes   | Contadora       | Finanzas          | activo |
      | EMP-0004        | Jorge Paredes | Técnico         | Tecnología        | activo |
    Cuando filtro el directorio por el departamento "Finanzas"
    Entonces veo 1 resultado
    Y el resultado corresponde al empleado "Sofía Reyes"
    Y el departamento mostrado es "Finanzas"

  Escenario: Un empleado dado de baja sigue apareciendo en el directorio
    Dado que existe el empleado "Pedro Salas" con estado "baja" y fecha de baja "2024-05-10"
    Cuando consulto el directorio de empleados
    Entonces veo al empleado "Pedro Salas" en el listado
    Y su estado mostrado es "baja"

  Escenario: Buscar un texto que no coincide con ningún empleado
    Dado que existen empleados registrados en el directorio
    Cuando busco en el directorio el texto "xyz-no-existe"
    Entonces veo el mensaje "No se encontraron resultados"
    Y no se muestra ninguna fila de empleados

# Preguntas abiertas
# - No se especifica si la búsqueda por nombre/correo es por coincidencia exacta o parcial (contiene el texto).
# - No se especifica qué debe mostrar la pantalla si se filtra por un departamento que no es uno de los cinco valores válidos (Tecnología, Ventas, Finanzas, Recursos Humanos, Operaciones).
# - No se especifica si se pueden combinar búsqueda por texto y filtro por departamento al mismo tiempo.
# - No se especifica el orden en que se muestran los resultados ni si hay paginación.
