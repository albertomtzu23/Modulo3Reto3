# Decisiones · HU-10

Corrida con defensas del 5 de noviembre de 2026: estado LISTA, 0 ciclos, 1.63 USD en agentes y 59 pruebas pasadas. En `auditoria.jsonl`, que incluye corridas anteriores, corresponde al tramo de 21:39:52 a 21:46:37. Ajusté la fábrica con apoyo de Claude Code.

## 1. Workflow y agente

Son agentes el analista, el diseñador, el plan, la construcción, el despliegue y el automatizador: deciden qué leer y cómo resolver (el desarrollador hizo 46 llamadas a herramientas). `filtrar_historia` y `triage` solo clasifican y enrutan. Son workflow el orden del grafo, los validadores y `MAX_CICLOS = 2`, porque ese resultado no debe depender del modelo.

## 2. Validación

`validar_gherkin` exigió los 8 mensajes exactos; `validar_plan` y Pydantic revisaron los 24 casos; `verificar_app` comprobó `/api/salud` y `npm run build`; `verificar_pruebas_escritas` confirmó un test por caso, y `ejecutar_pruebas` dio 59 passed. El analista necesitó 2 intentos: el primero no pasó la validación, el código le devolvió los problemas y el segundo pasó. Es reflexión con un evaluador determinista. Limitación: esos problemas no se guardan, así que no puedo citar cuál fue.

## 3. Mi intervención

Respondí `si` a las preguntas abiertas del analista (largo máximo por solicitud y saldo independiente por año). Antes de aprobar el plan revisé los días festivos, el tope de 12 días y el cálculo de días hábiles; lo aprobé sin rechazos. Después, en `localhost:8080`, registré un día de vacaciones: se descontó de los 12 del año y el registro solo está disponible para empleados activos. También decidí usar los mensajes de `convenciones_vacaciones.md`, aunque difieren de la tabla de la guía, porque la misma guía indica que las pruebas ocultas se construyen con ese archivo y con `reglas_vacaciones.md`.

## 4. Arquitectura

Es un orquestador de flujo fijo en LangGraph: las etapas no cambian entre historias, y un supervisor que decidiera el recorrido añadiría costo y variación sin ganar nada. Tiene paralelización (despliegue y automatizador arrancaron a las 21:44:39), humano en el bucle (`interrupt`) y un supervisor acotado: `triage` enruta, no corrige, y aquí no se activó. La defensa es en profundidad: el filtro bloqueó HU-99 antes del analista, y los hooks limitan a los agentes; sus huecos están en `salida/seguridad.md`.

## 5. Qué falló y qué corregí

En HU-10 no hubo fallas de pruebas ni ciclos de corrección. Antes, en otras historias:

- **HU-03:** 2 pruebas E2E fallaban porque `mensaje-exito` desaparecía al cerrar el formulario, y el triage culpaba al automatizador. Agregué la regla a `convenciones_app.md`, ajusté el prompt de `triage.py` y, en `flujo_s4.py`, los fallos repetidos pasan al desarrollador.
- **HU-01:** `test_cp04` contaba filas antes de que cargara la tabla. Agregué al automatizador la regla de esperar a que los datos estén visibles.

Corregí a los agentes y no sus resultados porque un parche solo arregla ese archivo, mientras que la regla aplica a las historias siguientes. Además, el reto prohíbe editar a mano.

Pendiente: ningún criterio prueba el aniversario del 29 de febrero. El código lo contempla, pero mis pruebas no lo cubren.
