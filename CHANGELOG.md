# Changelog

Cambios relevantes de la fábrica y de la aplicación que genera, del más reciente al más antiguo.

## 1.0.1 · 2026-11-05

Solo documentación, sin cambios de comportamiento.

- README con instalación para Mac, Linux y Windows, diagrama del flujo, ejemplos y problemas frecuentes.
- Este changelog.
- 53 docstrings en `agentes/` y `flujos/`. Se comprobó, comparando el árbol de sintaxis contra el commit anterior, que el código ejecutable no cambió.
- Corregido el docstring de `dibuja_grafo`, que mencionaba un parámetro inexistente.
- Sin docstring a propósito: `seguridad/hooks.py`, para no alterar los hooks, y los modelos Pydantic de salida estructurada, cuyo docstring puede enviarse al modelo.

## 1.0.0 · 2026-11-05

HU-10 Solicitar vacaciones, generada por la fábrica.

- Corrida con defensas: estado `LISTA`, 0 ciclos de corrección y 59 pruebas pasadas.
- API `POST` y `GET /api/empleados/{id}/vacaciones`, tabla de festivos de 2026 y 2027, y pantalla de vacaciones en el directorio.
- Demostración del ataque HU-99 y `salida/seguridad.md`: el filtro bloqueó la historia, con riesgos residuales documentados.
- `salida/HU-10/decisiones.md`.
- Scripts `probar_hooks.py` e `ingenuo_detalle.py` en `ejemplos/s4_seguridad/`.

## 0.3.0 · 2026-11-05

Ajustes de la fábrica antes de correr HU-10.

- **Analista:** exige los mensajes exactos de la tabla de errores (`CONTRATOS`) y permite hasta 3 intentos.
- **Diseñador:** copia los mensajes de error letra por letra.
- **Automatizador:** usa un empleado nuevo por prueba, compara mensajes exactos, espera a que carguen los datos y acepta por terminal la falla que debe corregir.
- **Triage:** recibe las convenciones y no asigna al automatizador fallas de la app; si los mismos fallos se repiten tras corregir las pruebas, pasan al desarrollador.
- **Verificación:** la trazabilidad revisa solo las pruebas de la historia, porque los `CP-xx` se repiten entre historias.
- **Contexto:** el mensaje de éxito debe seguir visible al cerrar un formulario.
- Resultado: HU-03 quedó `LISTA` con 25 pruebas, y se generaron las pruebas de HU-01.

## 0.2.0 · 2026-11-04

Repositorio de entrega.

- Fábrica publicada sin llaves, con `.env.example` de ejemplo.
- Contexto y reglas de HU-10.
- En Windows, `_correr` encuentra `npm.cmd` con `shutil.which` (`WinError 2`).

## 0.1.0 · 2026-10-30

Fábrica de los laboratorios del curso.

- Seis agentes, flujos de las sesiones 2 a 4 con LangGraph, y hooks de seguridad con auditoría.
- HU-01 y HU-02 pasadas por la fábrica.
