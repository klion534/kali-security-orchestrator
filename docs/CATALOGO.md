# Catálogo del Stack

> Inventario completo de lo instalado: agentes, skills, comandos, MCPs, binarios
> y ficheros de pipeline.

---

## 1. Subagentes (18)

### Pipeline SDD (9)

| Agente | Modo | Permisos | Qué hace | Artefacto |
|--------|------|----------|----------|-----------|
| `sdd-orchestrator` | primary | `edit: deny`, `task: sdd-*` | Coordina el pipeline. No escribe código. | — |
| `sdd-explore` | subagent | read-only | Mapea el codebase: `path:line` como evidencia | informe |
| `sdd-propose` | subagent | escribe | Intención, alcance, no-objetivos, rollback | `proposal.md` |
| `sdd-spec` | subagent | escribe | Requisitos `R1..Rn` con Given/When/Then | `spec.md` |
| `sdd-design` | subagent | escribe | Arquitectura, ADRs, migraciones, observabilidad | `design.md` |
| `sdd-tasks` | subagent | escribe | Checklist numerado, por fases, con tests | `tasks.md` |
| `sdd-apply` | subagent | escribe | TDD: RED → GREEN → REFACTOR | código + tests |
| `sdd-verify` | subagent | `edit: deny` | Ejecuta tests reales, matriz de cumplimiento | `verification.md` |
| `sdd-archive` | subagent | escribe | Merge del delta al baseline, cierre | baseline + archivo |

### Especialistas del curso (9)

| Agente | Qué resuelve | Siguiente skill |
|--------|--------------|-----------------|
| `prompt-engineer` | Construye el prompt de cinco ejes | `prompt-perfect` |
| `context-engineer` | Presupuesto de contexto, compresión, aislamiento | `context-engineering` |
| `model-selector` | Coste, latencia, privacidad, ventana de contexto | `model-selection` |
| `test-engineer` | Qué testear con IA: matriz por riesgo | `testing-strategy` |
| `security-reviewer` | Auditoría read-only del diff | `ci-cd-pipeline` |
| `ci-engineer` | Pipeline, gates, branch protection | `ci-cd-pipeline` |
| `release-engineer` | Versionado, changelog, notas con IA | `ci-cd-pipeline` |
| `knowledge-curator` | RAG: corpus, chunking, citas, evaluación | `rag-knowledge-base` |
| `git-worktree-guardian` | Aislamiento para escritores paralelos | `git-worktrees` |

### Los que ya venían de Gentle-AI (14 adicionales)

| Agente | Rol |
|--------|-----|
| `gentle-orchestrator` | Orquestador ODD (default agent) |
| `gentle-ai-explore` / `gentle-ai-worker` / `gentle-ai-verify` | Triángulo ODD |
| `gentleman` | Persona: arquitecto senior, mentor |
| `jd-judge-a` / `jd-judge-b` | Jueces ciegos de Judgment Day |
| `jd-fix-agent` | Corrección quirúrgica acotada |
| `review-risk` | Lente R1 — seguridad, límites de privilegio |
| `review-resilience` | Lente R4 — fallbacks, reintentos, observabilidad |
| `review-readability` | Lente R2 — naming, complejidad, intención |
| `review-reliability` | Lente R3 — tests, cobertura útil, determinismo |
| `review-refuter` / `review-validator` | Verificación dirigida del review nativo |

**Total: 39 agentes** (18 propios + 14 de Gentle-AI + 7 built-in de OpenCode).

---

## 2. Skills (19)

### Propias del curso (9)

| Skill | Trigger | Contenido |
|-------|---------|-----------|
| `sdd-workflow` | SDD, especificación, propuesta, `/sdd` | Store de artefactos, contratos de fase, modos SDD, protocolo de contexto, reglas duras |
| `prompt-perfect` | prompt engineering, cinco ejes, construir prompt | Los cinco ejes, prompt malo vs. bueno, procedimiento, anti-patrones |
| `context-engineering` | ventana de contexto, tokens, compresión | Presupuesto por clases, 4 técnicas, recuperación, anti-patrones |
| `model-selection` | elegir modelo, local vs cloud, coste | Dos ecosistemas, procedimiento, tabla de routing, anti-patrones |
| `testing-strategy` | qué testear, edge cases, QA | Matriz P0-P4, checklist de 8 puntos, pirámide, RED→GREEN→REFACTOR |
| `ci-cd-pipeline` | CI/CD, GitHub Actions, PR, gates | Reglas de oro, workflow de referencia, seguridad, releases, checklist |
| `rag-knowledge-base` | RAG, NotebookLM, corpus, citas | Chunking, retrieval híbrido, prompt de grounding, evaluación |
| `git-worktrees` | worktree, multiagente, colisión | Reglas de aislamiento, comandos, chequeo de solapamiento, conflictos |
| `veil-secrets` | veil.nvim, ocultar .env, streaming | Instalación, config, comandos, defensa en 5 capas |

### De Gentle-AI (8)

`judgment-day` · `chained-pr` · `work-unit-commits` · `cognitive-doc-design` ·
`skill-creator` · `skill-improver` · `skill-registry` · `go-testing`

### Externas (2)

`customize-opencode` (built-in) · `pinokio`

---

## 3. Comandos slash (14)

| Comando | Agente | Qué hace |
|---------|--------|----------|
| `/sdd` | `sdd-orchestrator` | Pipeline completo con las 4 puertas HITL |
| `/sdd-new` | `sdd-orchestrator` | Alta de cambio: explore + propose, para en G1 |
| `/sdd-ff` | `sdd-orchestrator` | Fast-forward: todas las fases sin detenerse |
| `/prompt` | `prompt-engineer` | Prompt de cinco ejes + diagnóstico |
| `/model` | `model-selector` | Recomendación de modelo con coste y privacidad |
| `/test-plan` | `test-engineer` | Estrategia de tests por riesgo |
| `/security-review` | `security-reviewer` | Auditoría de seguridad del diff |
| `/ci` | `ci-engineer` | Auditoría y reparación del pipeline |
| `/release` | `release-engineer` | Versionado y notas de release con IA |
| `/worktree` | `git-worktree-guardian` | Worktrees aisladas para trabajo paralelo |
| `/judgment-day` | — | Revisión adversarial doble a ciegas |
| `/memory` | — | Consulta y gestión de la memoria persistente |
| `/skill-registry` | — | Reindexa las skills disponibles |
| `/skill-creator` | — | Crea una skill nueva con frontmatter válido |

---

## 4. MCP y plugins

| Componente | Tipo | Función |
|------------|------|---------|
| **Engram** | MCP local (`engram mcp --tools=agent`) | Memoria persistente: SQLite + FTS5, búsqueda BM25, 21 herramientas de agente |
| **Context7** | MCP remoto | Documentación actual de librerías y frameworks |
| `plugins/engram.ts` | Plugin OpenCode | Tracking de sesión, protocolo de memoria, recuperación tras compaction |
| `tui-plugins/gentle-logo.tsx` | Plugin TUI | Banner |
| `opencode-subagent-statusline` | Statusline | Actividad de subagentes en el sidebar |

---

## 5. Binarios instalados

| Binario | Versión | Origen | Para qué |
|---------|---------|--------|----------|
| `engram` | 3.4.0 | `Gentleman-Programming/engram` | Memoria persistente + MCP server |
| `gentle-ai` | 4.2.0 | `Gentleman-Programming/gentle-ai` | Configurador del stack (17 agentes soportados) |
| `gga` | 2.10.1 | `Gentleman-Programming/gentleman-guardian-angel` | Code review con IA, provider-agnostic |

**Instalados en `/usr/local/bin`.** Verificados con SHA-256 contra los
`checksums.txt` oficiales de cada release.

> Homebrew no funcionaba en esta máquina (Xcode 15.4 en un Mac Intel requiere
> Xcode 26.6 para compilar desde fuente), así que se instalaron los binarios
> precompilados de los releases oficiales, con checksum verificado.

---

## 6. Ficheros de pipeline

| Fichero | Propósito |
|---------|-----------|
| `.github/workflows/ci.yml` | Lint → test → build en cada PR, con concurrency y least privilege |
| `.github/workflows/security-review.yml` | Security review con IA en cada PR |
| `.github/workflows/release-please.yml` | Versionado + changelog + release notes con IA |
| `.github/dependabot.yml` | Actualizaciones de dependencias |
| `.github/PULL_REQUEST_TEMPLATE.md` | Contrato de PR |
| `.github/CODEOWNERS` | Revisores automáticos por ruta |
| `release-please-config.json` | Config de Release Please |
| `.release-please-manifest.json` | Versión actual (**nunca editar a mano**) |
| `.gga` | Config de Guardian Angel |
| `.env.example` | Contrato de variables de entorno |
| `.gitignore` | `.env`, `.worktrees/`, artefactos |
| `nvim/veil.lua` | Spec de LazyVim para veil.nvim |
| `opencode.jsonc` | Config a nivel de proyecto (excepciones de la deny-list) |

### Los tres gates de CI

Los mismos scripts que ejecuta el CI, ejecutables en local. Si pasan local,
el CI pasa: el gate es el mismo código.

| Gate | Comando | Qué valida |
|------|---------|-----------|
| **lint** | `npm run lint` | JSON, JSONC, YAML, shell (`bash -n`) y frontmatter de skills. Patrones de credenciales. Ficheros obligatorios. |
| **test** | `npm test` | Invariantes del store SDD: numeración estable de requisitos sin huecos, separación baseline/cambios, límite de 500 líneas del `AGENTS.md` |
| **build** | `npm run build` | Regenera `docs/INDEX.md` desde los ficheros en disco, así que el índice no puede quedar desactualizado |

Sin dependencias de runtime: solo `yaml` como devDependency para parsear
YAML con un parser real en lugar de una heurística escrita a mano.

---

## 7. Store de artefactos SDD

```
.sdd/
├── registry.md              # índice de cambios y fase actual
├── specs/                   # baseline mergeado (numeración estable)
├── changes/<change-name>/
│   ├── proposal.md
│   ├── spec.md
│   ├── design.md
│   ├── tasks.md
│   └── verification.md
└── archive/<change-name>/
```

---

## 8. Verificación

```bash
# Qué hay instalado
opencode agent list          # 39 agentes
opencode debug skill         # 19 skills
opencode debug config        # config resuelta

# Los binarios
engram --version
gentle-ai --version
gga version

# Los tres gates de CI
npm run lint
npm test
npm run build

# El stack completo, en una pasada
./scripts/verify-stack.sh
```

---

## 9. Comandos de mantenimiento

```bash
# Re-sincronizar los assets gestionados por Gentle-AI
gentle-ai sync

# Diagnóstico read-only
gentle-ai doctor

# Actualizar las herramientas
gentle-ai upgrade

# Refrescar el registro de skills del proyecto
gentle-ai skill-registry refresh

# Instalar el hook de GGA en un repo
gga init && gga install

# Telemetría (opt-out)
gentle-ai telemetry disable
```
