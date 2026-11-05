# Reporte · HU-03

**Estado:** ESCALAR A UNA PERSONA
**Costo de agentes:** 1.72 USD
**Ciclos de corrección:** 2

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (12 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 2 failed, 22 passed in 72.29s (0:01:12)
- Triage → automatizador: Ambas pruebas (editar puesto/departamento y dar de baja) terminan mostrando la pantalla "Registrar empleado" en lugar de la vista/flujo de edición o baja del empleado EMP-0010. Esto indica que la prueba no está navegando correctamente al empleado existente (por ejemplo, no completa el Antecedente de crear/ubicar al empleado "EMP-0010" ni navega a su pantalla de edición/baja), por lo que termina en el formulario de registro inicial y nunca llega a disparar la acción de editar o dar de baja, haciendo que el selector get_test_id("mensaje-exito") nunca aparezca.
- Pruebas corregidas
- Pruebas E2E: 2 failed, 22 passed in 55.23s
- Triage → automatizador: Las dos pruebas fallan esperando el elemento "mensaje-exito", pero el snapshot de la página muestra que se quedó en la pantalla "Registrar empleado" (formulario de alta), no en la pantalla de edición/baja del empleado EMP-0010. Esto indica que la prueba no está navegando ni localizando correctamente al empleado existente antes de intentar editar/dar de baja (selector o flujo de navegación incorrecto), en lugar de un fallo real de la aplicación en cumplir el criterio de aceptación.
- Pruebas corregidas
- Pruebas E2E: 2 failed, 22 passed in 61.71s (0:01:01)

## Última ejecución de pruebas
```
2 failed, 22 passed in 61.71s (0:01:01)
- tests.e2e.test_hu_03_e2e::test_cp02_editar_puesto_y_departamento[chromium]
  AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" get_by_test_id("mensaje-exito") with timeout 5000ms
  - waiting for get_by_test_id("mensaje-exito")

Aria snapshot:
- main:
  - heading "Registrar empleado" [level=1]
  - text: Nombre
  - textbox "Nombre"
  - text: Correo
  - textbox "Correo"
  - text: Puesto
  - text
- tests.e2e.test_hu_03_e2e::test_cp10_dar_de_baja_empleado_activo[chromium]
  AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" get_by_test_id("mensaje-exito") with timeout 5000ms
  - waiting for get_by_test_id("mensaje-exito")

Aria snapshot:
- main:
  - heading "Registrar empleado" [level=1]
  - text: Nombre
  - textbox "Nombre"
  - text: Correo
  - textbox "Correo"
  - text: Puesto
  - text
```