# Arquitectura del Stack Cognitivo

> Cómo está montado el sistema, qué capa hace qué, y por qué está así.

---

## Vista general

```
┌──────────────────────────────────────────────────────────────────────┐
│  CAPA 5 — HUMANO                                                    │
│  Validador de intención · Puertas HITL · Decisiones de negocio     │
│  La que aprueba el deployment. La única responsable legal.          │
└───────────────────────────────▲──────────────────────────────────────┘
                                │ gates, aprobaciones
┌───────────────────────────────┴──────────────────────────────────────┐
│  CAPA 4 — ORQUESTACIÓN                                               │
│  gentle-orchestrator (ODD) · agentes especializados                │
│  Autorización · documento de feature · contratos de resultado       │
└───────────────────────────────▲──────────────────────────────────────┘
                                │ briefs, contratos
┌───────────────────────────────┴──────────────────────────────────────┐
│  CAPA 3 — EJECUCIÓN                                                 │
│  39 agentes: ODD · especialistas · review 4R · JD                   │
│  Contexto fresco por subagente · Parallel writers en worktrees      │
└───────────────────────────────▲──────────────────────────────────────┘
                                │ reglas, conocimiento bajo demanda
┌───────────────────────────────┴──────────────────────────────────────┐
│  CAPA 2 — CONOCIMIENTO                                              │
│  19 skills (carga bajo demanda) · Skill Registry (router)           │
│  AGENTS.md (<500 líneas) · MCP: Context7 · Docs de referencia        │
└───────────────────────────────▲──────────────────────────────────────┘
                                │ contexto, herramientas, memoria
┌───────────────────────────────┴──────────────────────────────────────┐
│  CAPA 1 — INFRAESTRUCTURA                                           │
│  OpenCode 1.18 · Engram MCP (SQLite+FTS5) · Plugins · Permisos      │
│  Deny-list de secretos · TUI themes · Gentle-AI                     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Las tres capas que hacen que esto funcione

### 1. Control del contexto

El problema: "la mayoría de los desarrolladores usan la IA como un chat
glorificado. Esto no es un problema del modelo — es un problema de
**arquitectura**."

La solución es una cadena de acumulaciones, cada una nacida de un dolor real:

```
Monolito            →  todo en un AGENTS.md gigante → contexto inflado
   ↓
Skills Registry     →  reglas modulares, carga bajo demanda → contexto limpio
   ↓
Engram              →  memoria persistente entre sesiones → amnesia resuelta
   ↓
Human in the Loop   →  el humano decide lo que importa → control real
```

### 2. Orquestación determinista

El orquestador **nunca hace trabajo real**. Solo coordina.

| Nivel | Mecanismo | Alcance |
|-------|-----------|---------|
| **1 — Basic** | Task tool nativo | Subagentes puntuales, tareas independientes y paralelas |
| **2 — Agent Teams Lite** | Markdown puro, cero dependencias | Orquestación declarativa, compatible multi-provider |
| **3 — Full Agent Teams** | DAG completo | Fases secuenciales y paralelas, contratos de resultado, persistencia, approval gates |

Este repo opera en el **nivel 3**, sobre OpenCode.

**Contratos de resultado:** cada subagente produce un output estructurado que
el siguiente consume como input. Sin contratos no hay orquestación — solo caos.

**Fases paralelas:** Spec Writer y Designer corren simultáneamente en
subagentes independientes. El orquestador espera ambos outputs antes de
continuar.

**Persistencia:** cada fase lee memoria de ejecuciones anteriores y escribe
nuevos aprendizajes. El sistema mejora con cada run.

### 3. Evidencia

La diferencia entre "funciona" y "está verificado".

| Sin evidencia | Con evidencia |
|----------------|---------------|
| "Los tests deberían pasar" | `12 passed, 0 failed` + el comando exacto |
| "Revisé el código" | Matriz de cumplimiento requisito → check → resultado |
| "No hay problemas de seguridad" | Hallazgos con `path:line`, exploit e impacto |
| "Cumple el spec" | Requisitos mapeados a tests que existen y se ejecutaron |

---

## El ciclo de Organic Driven Development

```
                     AUTORIZAR
                         │
                      EXPLORAR
                         │
              RESOLVER INCERTIDUMBRES
                         │
                      CLASIFICAR
                         │
                      REGISTRAR
             odd/tasks/<feature-name>.md
                         │
                     IMPLEMENTAR
                         │
                      COMPROBAR
                         │
                        CERRAR
```

El documento de feature es el contrato recuperable. El trabajo pequeño no crea
artefactos durables; el trabajo sustancial conserva Specs, Tasks, Log y evidencia
en un único archivo.

---

## Persistencia: dos capas, un solo patrón

| Capa |.Store | Fuente de verdad | Sobrevive |
|------|-------|------------------|-----------|
| **Disco** | `odd/tasks/<name>.md` | **Sí** | Sí |
| **Memoria** | Engram, `odd/<name>/tasks` | No (es el índice) | Sí |

**Regla:** el archivo es la verdad, la memoria es el índice. Si discrepan, el
archivo gana. Por eso la recuperación de contexto siempre termina leyendo el
archivo real:

```
mem_context → mem_search → mem_get_observation → leer el archivo → reconciliar
```

---

## El sistema de permisos

### Deny-list de secretos (capa de infraestructura)

Activa por defecto en `~/.config/opencode/opencode.jsonc`:

| Patrón | read | edit |
|--------|------|------|
| `**/.env`, `**/.env.*` | deny | deny |
| `**/*.pem`, `**/*.key`, `**/*.p12`, `**/*.pfx` | deny | deny |
| `**/.ssh/**` | deny | deny |
| `**/credentials.json` | deny | deny |
| `**/secrets`, `**/secrets/**` | deny | deny |
| `**/.aws/credentials` | deny | deny |
| `**/.config/gh/hosts.yaml` | deny | deny |

El agente **no puede leer ni escribir** un secreto. No es una recomendación:
es una denegación en la capa de permisos.

### Gates de bash (protección del sistema)

- `git push` → **ask**
- `git push --force` / `-f` / `-fu` → **deny**
- `git reset --hard` → **deny**
- `git clean -f` / `-fd` → **deny**
- `rm -rf *` → **ask**, `rm -rf /` / `~` / `$HOME` → **deny**
- `chmod -R 777` → **deny**
- `DROP DATABASE` / `DROP TABLE` / `TRUNCATE` → **ask**
- `npm publish` → **ask**
- `ssh` / `scp` / `sftp` / `rsync` → **ask** (autorización remota es explícita)

### Permisos por rol

| Agente | edit | write | bash | task |
|--------|------|-------|------|------|
| `gentle-orchestrator` | deny | deny | allow | especialistas autorizados |
| `gentle-ai-explore` | deny | deny | solo lectura | deny |
| `gentle-ai-verify` | deny | allow (el log) | tests | deny |
| `gentle-ai-worker` | allow | allow | tests + git | deny |
| `security-reviewer` | deny | deny | solo lectura | deny |
| `review-risk` / `readability` / `reliability` / `resilience` | deny | deny | deny | deny |
| `jd-judge-a` / `jd-judge-b` | deny | deny | — | deny |

**El orquestador no puede escribir código.** Esa restricción es el diseño, no
una limitación.

---

## Las dos capas de revisión

```
                    ┌──────────────────────────┐
                    │   4R — Revisión negociada  │
                    │  Risk · Resilience ·       │
                    │  Readability · Reliability  │
                    │  (gentle-ai review)        │
                    └──────────────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │  Judgment Day — adversarial │
                    │  2 jueces ciegos, 2 rondas │
                    │  (skill judgment-day)      │
                    └──────────────────────────┘
```

**No se ejecutan ambos sobre el mismo target.** Judgment Day reemplaza al 4R
como método adversarial para ese target.

- El **4R** es revisión por lentes, con evidencia y recibos.
- **Judgment Day** es confrontación ciega: dos jueces que no se ven, hasta dos
  rondas de corrección acotada, y un veredicto terminal
  (`APPROVED` / `ESCALATED`).

Ninguno de los dos autoriza entrega. Commit, push, PR y release siguen bajo
política ordinaria del repo y bajo decisión humana.

---

## GGA — el guardián del commit

```
git commit → archivos staged → revisión IA (cualquier LLM) → pass/fail
```

- **Provider-agnostic**: Claude, Gemini, Codex, OpenCode, Cursor, Kilo, Kiro,
  Ollama, LM Studio, GitHub Models, MiniMax.
- **Pure Bash**: sin runtime, funciona en macOS, Linux, Windows (Git Bash), WSL.
- **Caching inteligente**: salta los archivos sin cambios.
- **Modo PR**: `gga run --pr-mode` revisa el PR completo, no solo el último
  commit.

Se integra con el `AGENTS.md` del proyecto como fuente de estándares.

---

## veil.nvim — la quinta capa de defensa de secretos

| Capa | Herramienta | Protege |
|------|-------------|---------|
| 1 | `.gitignore` + `.env.example` | El repo nunca contiene el secreto |
| 2 | Pre-commit secret scanning | El secreto nunca se commitea |
| 3 | **veil.nvim** | El secreto nunca aparece en tu pantalla |
| 4 | Permisos de OpenCode | El agente nunca toca el secreto |
| 5 | Security review en CI | El secreto nunca llega a `main` |

Las cinco. La capa 3 sola no alcanza: protege el stream, no el commit.

---

## Diagrama de decisión: ¿qué ruta tomo?

```
                    ┌──────────────────────────────┐
                    │ ¿Es un cambio sustancial?     │
                    └───────────┬──────────────────┘
                     no         │ sí
          ┌───────────────────┐  ▼
          │  Inline.         │  ┌──────────────────────────┐
          │  Sin ceremonia.  │  │ ¿Entiendo el código?     │
          └───────────────────┘  └────────┬─────────────────┘
                                no        │ sí
            ┌───────────────────────┐     ▼
            │ gentle-ai-explore     │  ┌──────────────────────────┐
            └───────────────────────┘  │ ¿Hay dos Writers en      │
                                        │ paralelo?               │
                                        └───────┬──────────┬───────┘
                                           no  │          │ sí
                          ┌────────────────────┘          ▼
                          ▼                    ┌──────────────────────┐
              ┌───────────────────────┐        │ git-worktree-guardian│
              │ Documento ODD        │        └──────────────────────┘
              │ + tareas verificables │
              └───────────────────────┘
```

---

## Mapa de archivos

### Global (`~/.config/opencode/`)

```
opencode.jsonc          Config: MCP, agentes, permisos, plugins
AGENTS.md               System prompt global (persona + protocolo Engram)
agent/                  agentes ODD y especialistas markdown
skills/                 19 skills (10 del curso + 9 de Gentle-AI)
commands/               14 comandos slash
plugins/engram.ts       Plugin de Engram (tracking + compaction recovery)
themes/                 Temas Gentleman
tui.json                Registro del plugin de statusline
```

### Proyecto

```
AGENTS.md               Reglas del proyecto (<500 líneas)
odd/                    Documentos de features ODD
.github/workflows/      ci.yml · security-review.yml · release-please.yml
.github/                dependabot · PR template · CODEOWNERS
docs/                   PLAYBOOK · ARQUITECTURA · CATALOGO · OPERATIVO
nvim/veil.lua           Spec de LazyVim para veil.nvim
scripts/                Utilidades de verificación del stack
```
