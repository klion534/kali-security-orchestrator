# SDD Registry

> Índice de todos los cambios y su fase actual.
> El orquestador lee este archivo para saber dónde reanudar.

## Cambios

| Cambio | Fase | Estado | Actualizado | Spec |
|--------|------|--------|-------------|------|
| _(ninguno todavía)_ | — | — | — | — |

## Fases

| Fase | Artefacto | Estado |
|------|-----------|--------|
| explore | informe de exploración | — |
| propose | `proposal.md` | — |
| spec | `spec.md` | — |
| design | `design.md` | — |
| tasks | `tasks.md` | — |
| apply | código + tests | — |
| verify | `verification.md` | — |
| archive | baseline + archivo | — |

## Baseline

| Dominio | Fichero | Requisitos | Actualizado |
|---------|---------|------------|-------------|
| _(ninguno todavía)_ | — | — | — |

## Notas

- El baseline mergeado vive en `.sdd/specs/`.
- La numeración de requisitos (`R1`, `R2`, ...) es **estable y global por
  dominio**. Nunca se renumera.
- Los cambios en curso viven en `.sdd/changes/` y están gitignored: son trabajo
  en progreso, no historial.
