# Sistema Cognitivo de Desarrollo con IA

> **De 0 a producción.** El stack completo de agentes, skills, subagentes,
> memoria persistente y gates de calidad, construido sobre el curso *Desarrollo
> con IA: De 0 a Producción* (Gentleman Programming).

```
El humano valida la intención. La IA produce el artefacto derivado.
```

---

## Qué hay aquí

| | |
|---|---|
| **39 agentes** | 9 del pipeline SDD · 9 especialistas del curso · 14 de Gentle-AI · 7 built-in |
| **19 skills** | 9 construidas desde el curso · 8 de Gentle-AI · 2 externas |
| **14 comandos** | `/sdd` `/sdd-new` `/sdd-ff` `/prompt` `/model` `/test-plan` `/security-review` `/ci` `/release` `/worktree` `/judgment-day` `/memory` … |
| **2 MCP** | Engram (memoria persistente) · Context7 (documentación actual) |
| **3 binarios** | `engram` 3.4.0 · `gentle-ai` 4.2.0 · `gga` 2.10.1 |
| **3 workflows** | CI (lint→test→build) · Security Review con IA · Release Please con notas IA |

---

## Documentación

| Documento | Qué cubre |
|-----------|-----------|
| **[PLAYBOOK-CURSO-IA.md](docs/PLAYBOOK-CURSO-IA.md)** | La síntesis completa de las tres clases, aplicada |
| **[ARQUITECTURA-STACK.md](docs/ARQUITECTURA-STACK.md)** | Las capas, el DAG, los permisos, los gates |
| **[CATALOGO.md](docs/CATALOGO.md)** | Inventario de todo lo instalado |
| **[OPERATIVO.md](docs/OPERATIVO.md)** | El manual de día a día |

---

## El pipeline SDD

```
        ┌──────────┐
        │  EXPLORE │  read-only: entender el codebase
        └────┬─────┘
             ▼
        ┌──────────┐
        │ PROPOSE  │  intención, alcance, no-objetivos, rollback
        └────┬─────┘
             ▼
     ┌───────┴────────┐   ◄── PARALELO
     ▼                ▼
┌─────────┐     ┌──────────┐
│  SPEC   │     │  DESIGN  │  requisitos+escenarios | arquitectura+ADRs
└────┬────┘     └────┬─────┘
     └───────┬────────┘
             ▼
        ┌──────────┐
        │   TASKS   │  numeradas, por fases, con tests mapeados
        └────┬─────┘
             ▼
        ┌──────────┐
        │   APPLY   │  TDD: RED → GREEN → REFACTOR
        └────┬─────┘
             ▼
        ┌──────────┐
        │  VERIFY  │  ejecución real de tests + matriz de cumplimiento
        └────┬─────┘
             ▼
        ┌──────────┐
        │  ARCHIVE │  merge del delta al baseline, cierre del cambio
        └──────────┘
```

Cuatro puertas Human-in-the-Loop: **G1** alcance, **G2** diseño, **G3** plan,
**G4** merge.

---

## Uso diario

```bash
# El comando principal
/sdd <descripción del cambio>

# Construir el prompt de cinco ejes antes de delegar
/prompt <lo que querés que haga el modelo>

# Elegir modelo: coste, latencia, privacidad, ventana de contexto
/model <la tarea>

# Auditoría de seguridad del diff
/security-review

# Estrategia de tests por riesgo
/test-plan <el cambio>

# Revisión adversarial doble a ciegas
/judgment-day

# Memoria persistente
/memory <qué querés que recuerde>
```

---

## Verificación del stack

```bash
./scripts/verify-stack.sh
```

Comprueba binarios, agentes, skills, comandos, MCPs, permisos de secretos y
validez de los workflows.

---

## Estructura

```
.
├── AGENTS.md                   Reglas del proyecto (<500 líneas)
├── opencode.jsonc              Config a nivel de proyecto
├── .sdd/                       Store de artefactos SDD
├── .github/
│   ├── workflows/              ci.yml · security-review.yml · release-please.yml
│   ├── dependabot.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
├── docs/                       PLAYBOOK · ARQUITECTURA · CATALOGO · OPERATIVO
├── nvim/veil.lua               Spec de LazyVim para veil.nvim
├── scripts/verify-stack.sh
├── release-please-config.json
└── .release-please-manifest.json
```

---

## Los tres pilares

1. **Dominio de los fundamentos técnicos.** Sin bases sólidas en arquitectura y
   patrones, es imposible auditar la producción.
2. **Maestría en la orquestación.** `AGENTS.md`, MCPs, skills y flujos
   multiagente deterministas.
3. **Control crítico (HITL).** Juicio crítico sobre la estrategia, para que el
   software no solo funcione, sino que sea sostenible y escalable.

> Las herramientas son efímeras; los fundamentos son permanentes.
