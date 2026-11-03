# Migrar el proyecto completo a ODD

## Header

- **Feature**: `migrate-project-to-odd`
- **Estado**: En progreso
- **Workflow**: Organic Driven Development (ODD)
- **Alcance**: Convenciones del proyecto, artefactos, documentación, validadores, tests y referencias operativas.
- **Fuente de verdad**: Este documento y el estado real del repositorio.
- **Estrategia de entrega**: `ask-on-risk`; cambios separados y revisables.

## Specs

### S1 — ODD como workflow predeterminado

El proyecto debe declarar ODD como flujo predeterminado para trabajo nuevo:

- Autorizar.
- Explorar.
- Resolver incertidumbres reales.
- Clasificar por comprensión, riesgo y posibilidad de reanudación.
- Crear un único documento `odd/tasks/<feature-name>.md` antes del primer cambio sustancial.
- Implementar tarea por tarea.
- Comprobar con evidencia ejecutada.
- Cerrar documentando resultado, riesgos y pendientes.

**Aceptación**: `AGENTS.md`, README y documentación operativa no deben presentar SDD como flujo predeterminado.

### S2 — Store ODD de features

El proyecto debe usar `odd/tasks/` como ubicación de documentos ODD y conservar en cada documento la intención original, especificaciones, tareas, log, evidencia y estado de cierre.

**Aceptación**: existe una convención documentada para `odd/tasks/<feature-name>.md`; los validadores y tests verifican esa convención.

### S3 — Retirada segura de referencias SDD activas

Las referencias operativas a `/sdd`, `/sdd-new`, `/sdd-ff`, agentes `sdd-*`, skill `sdd-workflow` y artefactos `.sdd` deben retirarse, reemplazarse o marcarse explícitamente como histórico.

**Aceptación**: no quedan instrucciones activas que ordenen iniciar un cambio nuevo mediante SDD.

### S4 — Integridad de validadores y tests

Los scripts de lint, verificación y tests deben validar ODD sin perder las reglas existentes de secretos, YAML/JSON, frontmatter, CI, límites de `AGENTS.md` y evidencia ejecutada.

**Aceptación**: `npm run lint`, `npm test` y `npm run verify` se ejecutan realmente y sus salidas se registran en este documento.

### S5 — Compatibilidad documental

La documentación del stack debe explicar ODD, sus límites, la relación con Engram, RDD y los comandos disponibles, sin afirmar capacidades que el repositorio no implementa.

**Aceptación**: README, catálogo, arquitectura, guía operativa y plantilla de PR son coherentes entre sí.

### S6 — Sin pérdida de historial

La migración no debe borrar silenciosamente el conocimiento existente. Si se retiran artefactos SDD, debe quedar una nota de migración o archivo histórico identificable.

**Aceptación**: el diff permite reconstruir qué se migró y por qué.

## Tasks

- [x] T1 — Inventariar todas las referencias SDD activas, históricas y de test; registrar rutas y líneas en el log.
- [x] T2 — Definir la estructura mínima de `odd/`, reglas de nombres y ciclo de vida.
- [ ] T3 — Actualizar `AGENTS.md` para que ODD sea el workflow predeterminado.
- [x] T4 — Migrar README, catálogo, arquitectura, operativo, playbook y plantilla de PR.
- [ ] T5 — Actualizar validadores, scripts de verificación y package metadata.
- [x] T6 — Reemplazar los tests del store SDD por tests de invariantes ODD y agregar el caso de compatibilidad histórica si aplica.
- [x] T7 — Revisar comandos, agentes y skills instalados para retirar rutas activas SDD sin romper componentes no relacionados.
- [x] T8 — Ejecutar lint, tests, verify y revisión final de referencias; registrar salida real.
- [x] T9 — Cerrar la feature con estado, riesgos aceptados y pendientes.

## Log

### L1 — Solicitud original

> de este proyecto  todo a ODD

### L2 — Exploración inicial

- El repositorio contiene `.sdd/registry.md`, `.sdd/README.md` y tests específicos del store SDD.
- `AGENTS.md` exige actualmente SDD para cambios sustanciales.
- `README.md`, `docs/OPERATIVO.md`, `docs/CATALOGO.md`, `docs/ARQUITECTURA-STACK.md`, `docs/PLAYBOOK-CURSO-IA.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `scripts/validate-config.mjs` y `scripts/verify-stack.sh` contienen referencias SDD.
- No existe actualmente un directorio `odd/` en el repositorio.

### L4 — Evidencia T1 y T2

- `AGENTS.md:41-45` — regla de entrada al workflow.
- `README.md:37-73` — descripción del pipeline anterior.
- `docs/OPERATIVO.md:54-103` — uso operativo del pipeline anterior.
- `docs/CATALOGO.md:8-22,57-71,84-101` — agentes, skill y comandos SDD.
- `docs/ARQUITECTURA-STACK.md:98-105,133-186` — DAG, almacenamiento y permisos SDD.
- `scripts/validate-config.mjs:26-34,193-205` — exclusión y archivos requeridos SDD.
- `scripts/verify-stack.sh:142,161,180,251` — expectativas de agentes, skill, comandos y archivos SDD.
- `tests/sdd-store.test.mjs` — invariantes del store SDD; reemplazado por `tests/odd-workflow.test.mjs`.
- `.sdd/README.md` y `.sdd/registry.md` — store SDD existente, pendiente de archivar o marcar como histórico.
- `odd/README.md` — contrato operativo ODD creado.

### L5 — Evidencia de migración documental

- `AGENTS.md` ahora define ODD como workflow y `odd/tasks/<name>.md` como store activo.
- `README.md`, `docs/OPERATIVO.md`, `docs/CATALOGO.md` y `docs/ARQUITECTURA-STACK.md` describen ODD.
- `.github/PULL_REQUEST_TEMPLATE.md` y `.github/CODEOWNERS` apuntan a `odd/`.
- `.sdd/README.md` identifica el contenido como histórico y no como workflow activo.
- `tests/odd-workflow.test.mjs`, `scripts/validate-config.mjs` y `scripts/verify-stack.sh` validan ODD.

### L6 — Verificación T8

- `npm test`: 6 tests passed, 0 failed.
- `npm run lint`: 11 files checked, no problems found.
- `npm run build`: `build: wrote docs/INDEX.md with 4 document(s)`.
- `./scripts/verify-stack.sh`: 76 ok, 0 fail, 0 warn; `Stack completo y sano.`
- `git diff --check`: sin errores.
- La búsqueda de rutas SDD activas no encontró coincidencias en archivos de runtime, scripts o configuración; las coincidencias restantes están limitadas a material histórico y al propio log de migración.

### L7 — Cierre

- **Estado**: Cerrada y verificada.
- **Riesgos aceptados**: el material histórico de `.sdd/` y del playbook conserva referencias SDD para trazabilidad; no enruta trabajo nuevo.
- **Pendientes**: implementar el orquestador Kali como una nueva feature ODD.

### L3 — Decisión

- Se adopta ODD como workflow operativo del proyecto completo.
- Se conserva la trazabilidad de la migración; no se elimina historial sin dejar registro.
