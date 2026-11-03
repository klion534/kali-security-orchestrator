# Organic Driven Development

Este proyecto usa **Organic Driven Development (ODD)** como flujo operativo
predeterminado.

## Ciclo

1. **Autorizar**: distinguir una explicación o exploración de una solicitud que autoriza cambios.
2. **Explorar**: entender el repositorio, las convenciones y el riesgo antes de escribir.
3. **Resolver incertidumbres**: investigar solo las decisiones que puedan cambiar la solución.
4. **Clasificar**: mantener el trabajo pequeño cuando pueda reanudarse desde la solicitud y el diff; crear seguimiento cuando sea sustancial.
5. **Registrar**: antes del primer cambio sustancial, crear `odd/tasks/<feature-name>.md`.
6. **Implementar**: avanzar tarea por tarea, con pruebas aplicables.
7. **Comprobar**: registrar únicamente evidencia ejecutada y separar fallos de pendientes.
8. **Cerrar**: documentar resultado, riesgos aceptados y trabajo restante.

## Documento de feature

Cada feature sustancial tiene un único documento con:

- `## Specs`: requisitos numerados, criterios de aceptación y comprobaciones.
- `## Tasks`: tareas estables, alcance y estado.
- `## Log`: solicitud original, decisiones, evidencias y cambios de alcance.

El archivo en disco es la fuente de verdad. Engram conserva un índice recuperable
del documento, pero no sustituye el archivo.

## Reglas

- Una tarea no se marca completa sin evidencia real.
- La prueba test-first se aplica cuando existe un runner determinista adecuado.
- Los cambios se mantienen en unidades revisables y con Conventional Commits.
- ODD no autoriza commits, pushes, despliegues ni acceso a producción por sí mismo.
- RDD y Engram son componentes complementarios; no son fases adicionales de ODD.
