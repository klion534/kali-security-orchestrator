# Manual Operativo

> Cómo se usa el stack en el día a día. Sin teoría: qué se tipea, qué pasa, qué
> mirar.

---

## 1. Primer arranque

```bash
# Verificar que todo está en su lugar
./scripts/verify-stack.sh

# Los tres gates de CI, en local
npm run lint     # valida JSON, JSONC, YAML, shell y frontmatter
npm test         # invariantes de los documentos ODD
npm run build    # regenera docs/INDEX.md

# Estado de memoria persistente
engram doctor

# Diagnóstico del stack gestionado
gentle-ai doctor
```

Los tres scripts de `package.json` son los mismos que ejecuta el CI. Si pasan
en local, el CI pasa. No hay mystery: el gate es el mismo código.

Si algo falla, el script dice exactamente qué. Los binarios van en
`/usr/local/bin`; si no están, re-exportalos:

```bash
curl -sL https://github.com/Gentleman-Programming/engram/releases/download/v3.4.0/engram_3.4.0_darwin_amd64.tar.gz | tar xz -C /tmp
install -m 0755 /tmp/engram /usr/local/bin/engram
```

> En esta máquina Homebrew no compila desde fuente (Xcode 15.4 en un Mac Intel
> requiere 26.6), así que los binarios se instalaron desde los releases
> oficiales con SHA-256 verificado.

---

## 2. El bucle de trabajo

### 2.1 Cambio trivial (typo, un-liner, fix obvio)

```
opencode
> Corregí el typo en el README
```

Sin pipeline. Sin ceremonia. El AGENTS.md lo dice explícitamente.

### 2.2 Cambio sustancial (feature, refactor, fix riesgoso)

```
opencode
> Implementar la política de reembolso de 30 días
```

El orquestador explora primero y crea `odd/tasks/checkout-refund-policy.md`
antes del primer cambio sustancial. Revisás la intención y el alcance, y luego
avanza tarea por tarea con evidencia.

### 2.3 Cambio en curso

```
opencode
> Continuar checkout-refund-policy
```

El orquestador lee `odd/tasks/checkout-refund-policy.md`, reconcilia el estado
real del repositorio y retoma desde la primera tarea incompleta. No reinicia.

### 2.4 Trabajo pequeño (ya sabés lo que querés)

```
opencode
> Corregí el typo en el README
```

No crea un documento durable cuando el cambio es entendido, de riesgo contenido
y puede reanudarse desde la solicitud y el diff.

---

## 3. Los comandos, uno por uno

### ODD — workflow predeterminado

ODD autoriza, explora, clasifica, registra el trabajo sustancial, implementa y
comprueba. El documento de feature es `odd/tasks/<feature-name>.md`.

No es una fase adicional ni un comando nuevo: es el comportamiento operativo
definido por `AGENTS.md` y `odd/README.md`.

### `/prompt` — el prompt de cinco ejes

```
> /prompt Necesito un endpoint de login en FastAPI con bcrypt y JWT
```

Te devuelve el prompt listo para copiar, más la tabla de auditoría de los
cinco ejes, las suposiciones declaradas y el riesgo residual.

**Cuándo usarlo:** siempre que la instrucción a un modelo no sea trivial.
Un "arreglá esto" de tres palabras no necesita cinco ejes.

### `/model` — qué modelo corre esta fase

```
> /model Analizar la arquitectura de un monorepo con 400 microservicios
```

Te da: clasificación de la tarea, restricciones, tabla de candidatos,
recomendación, runner-up, coste estimado y el riesgo de la recomendación.

### `/test-plan` — qué testear

```
> /test-plan El endpoint de reembolso con la ventana de 30 días
```

Matriz P0-P4, plan de tests con archivo y tipo, edge cases, regresiones a
proteger, gaps y los dobles de test necesarios.

### `/security-review` — auditoría del diff

```
> /security-review
> /security-review 42
```

Read-only. Solo reporta. No arregla. Cada hallazgo lleva `path:line`, exploit
concreto, impacto y una línea de fix.

### `/ci` — pipeline y gates

```
> /ci
```

Audita lo que hay, escribe los workflows que faltan, y te da el comando exacto
de branch protection que tenés que correr vos.

### `/release` — versionado y notas

```
> /release
```

Determina el bump desde los conventional commits, y genera la **narrativa** de
release: highlights en términos de usuario, breaking changes con el paso de
migración, migraciones y notas de upgrade.

### `/worktree` — aislamiento para trabajo paralelo

```
> /worktree crear feature-a
> /worktree list
> /worktree limpiar
```

### `/judgment-day` — revisión adversarial

```
> /judgment-day
```

Dos jueces ciegos en paralelo sobre el mismo target congelado. Como máximo dos
rondas de corrección acotada. Veredicto terminal: `APPROVED` o `ESCALATED`.

**No corre junto al 4R sobre el mismo target.**

### `/memory` — la memoria persistente

```
> /memory ¿qué decidimos sobre el modelo de datos de órdenes?
> /memory guardá que el TTL de la cache es 60s
```

---

## 4. Subagentes: cuándo invocarlos a mano

Los subagentes se invocan con `@` o los usa el orquestador. Invocalos
directamente cuando querés **una opinión específica** sin el pipeline:

| Comando | Para qué |
|---------|----------|
| `@gentle-ai-explore` | Mapa rápido del codebase, read-only |
| `@prompt-engineer` | Construir el prompt de cinco ejes |
| `@context-engineer` | Auditoría de presupuesto de contexto |
| `@model-selector` | Recomendación de modelo con coste |
| `@test-engineer` | Estrategia de tests por riesgo |
| `@security-reviewer` | Auditoría de seguridad de un diff |
| `@ci-engineer` | Diseño de pipeline y gates |
| `@release-engineer` | Versionado y notas |
| `@knowledge-curator` | Diseño de una base RAG |
| `@git-worktree-guardian` | Aislamiento para autores paralelos |

---

## 5. Skills: carga bajo demanda

Las skills se cargan solas cuando el pedido coincide con su trigger. No tenés
que invocarlas. Si querés forzar una:

| Skill | Cuándo la vas a necesitar |
|-------|---------------------------|
| `cognitive-doc-design` | Cuando redactes o revises documentos para reducir carga cognitiva |
| `prompt-perfect` | Antes de delegar algo no trivial |
| `context-engineering` | Cuando la sesión pierde el hilo |
| `model-selection` | Cuando el coste o la privacidad pesan |
| `testing-strategy` | Antes de escribir tests de código generado |
| `ci-cd-pipeline` | Cuando toques los workflows |
| `rag-knowledge-base` | Cuando el agente tiene que responder desde un corpus |
| `git-worktrees` | Cuando haya autores paralelos |
| `veil-secrets` | Cuando trabajes con `.env` o transmitas pantalla |

**Después de instalar o quitar skills**, refrescá el registro:

```bash
gentle-ai skill-registry refresh
```

---

## 6. Trabajo en paralelo

```bash
# 1. Crear el worktree
/worktree crear feature-a

# 2. En la sesión, movela al worktree
#    (OpenCode: la sesión se mueve al directorio aislado)

# 3. Trabajar, commitear

# 4. Mergear por PR
# 5. Limpiar
/worktree limpiar
```

**Regla antes de paralelizar:** listá los archivos que escribe cada agente. Si
se solapan, no son paralelos: son secuenciales.

---

## 7. Git, PRs y releases

### Commits

```bash
git checkout -b feat/checkout-refund-policy
# ... trabajo ...
git add -A
git commit -m "feat(checkout): enforce the 30-day refund window"
```

Conventional Commits, una unidad de trabajo por commit, sin atribución de IA.

### PR

Todo entra por PR. Nunca push directo a `main`.

Branch protection, una sola vez por repo:

```bash
gh api -X PATCH repos/:owner/:repo/branches/main \
  -F protection='{"required_status_checks":{"strict":true,"contexts":["Lint","Test (node 20)","Build"]},"enforce_admins":true,"required_pull_request_reviews":{"required_approving_review_count":1}}'
```

### GGA — el review en el commit

```bash
gga init        # una vez por repo
gga install     # instala el hook de pre-commit
gga run         # revisa lo staged
gga run --pr-mode  # revisa el PR completo
```

El hook usa `AGENTS.md` como fuente de estándares. Si el review bloquea, el
commit no pasa.

### Release

El merge a `main` dispara Release Please, que abre un **Release PR** con el
bump de versión y el changelog. Mergear ese PR publica el release.

**Nunca edites `.release-please-manifest.json` a mano.**

---

## 8. Secretos

```bash
# 1. Nunca commitees .env
echo ".env" >> .gitignore

# 2. Template commiteado
cp .env.example .env

# 3. Escaneo en pre-commit
#    (gitleaks o trufflehog)

# 4. En el editor, veil.nvim oculta los valores
#    <leader>sv toggle, <leader>sp peek
```

**El stack ya deniega `read` y `edit` sobre `.env`, `.pem`, `.key`, `.ssh/`,
`credentials.json` y `secrets/`.** La excepción es `.env.example` (plantilla,
sin valores reales).

**Si un secret se filtró: se rota. Borrar el archivo no rota nada.**

---

## 9. Cuando algo falla

| Síntoma | Causa probable | Qué hacer |
|---------|----------------|-----------|
| El agente no encuentra una skill | El registro está desactualizado | `gentle-ai skill-registry refresh` |
| Los MCPs no aparecen | Sesión vieja | Reiniciá OpenCode y creá una sesión nueva |
| `opencode` no arranca tras editar config | Config inválida | `OPENCODE_DISABLE_PROJECT_CONFIG=1 opencode` |
| El subagente se quedó colgado | Contexto perdido | `mem_context` → `mem_search` → leé el archivo real |
| Un test falla que antes pasaba | Cambio real | **No** debilitas la aserción. Arreglá la causa. |
| El pipeline no corre | YAML inválido | `opencode debug config` no ayuda: validá el YAML |
| El review pide cosas imposibles | Regla demasiado dura en `AGENTS.md` | Ajustá la regla, no el review |

---

## 10. Mantenimiento

```bash
# Actualizar los assets gestionados por Gentle-AI
gentle-ai sync

# Actualizar las herramientas
gentle-ai upgrade

# Telemetría (opt-out)
gentle-ai telemetry disable

# Estado de la memoria
engram doctor
engram list          # ¿qué hay guardado?

# Revisar el estado de la revisión por recibos
gentle-ai review mode status
```

---

## 11. La regla que resume todo

> **El humano valida la intención. La IA produce el artefacto derivado.**

Todo lo de arriba existe para sostener esa frase:

- Los **agentes** hacen el trabajo pesado, en contextos frescos y aislados.
- Las **skills** cargan el conocimiento justo cuando hace falta.
- **Engram** evita que la amnesia te obligue a re-explicar decisiones.
- **ODD** mantiene la intención, el progreso y la evidencia en un documento recuperable por feature.
- El **CI/CD** y los **gates** impiden que lo no verificado llegue a
  producción.
- El **HITL** te devuelve la decisión donde tiene que estar: en tu cabeza.
