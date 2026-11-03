# Historical SDD Artifact Store

> Archivo histórico del antiguo pipeline **Spec-Driven Development**.
> El workflow activo del proyecto es ODD; las features nuevas viven en
> `odd/tasks/<feature-name>.md`.
> El código es un artefacto transitorio y derivado. **Esto** es lo durable.

## Estructura

```
.sdd/
├── registry.md              # índice de cambios y su fase actual
├── specs/                   # BASELINE — requisitos mergeados, numeración estable
│   └── <dominio>.md
├── changes/                 # cambios en curso (gitignored)
│   └── <change-name>/
│       ├── proposal.md      # WHAT y WHY
│       ├── spec.md          # requisitos R1..Rn + escenarios Given/When/Then
│       ├── design.md        # HOW + ADRs
│       ├── tasks.md         # checklist numerado, por fases, con tests
│       └── verification.md  # matriz de cumplimiento + salida real de tests
└── archive/                 # historial cerrado
    └── <change-name>/
```

## Las reglas que no se rompen

1. **El baseline se numera de forma estable.** `R7` significa lo mismo para
   siempre. Renumerar rompe todas las referencias históricas de todos los
   artefactos, las tareas y las verificaciones. Los requisitos nuevos toman el
   siguiente número libre.

2. **El archivo es la fuente de verdad.** Engram (`sdd/<change>/<type>`) es el
   índice que permite recuperar el contexto entre sesiones. Si discrepan, el
   archivo gana.

3. **Nada se marca como cumplido sin evidencia ejecutada.** Una verificación
   sin la salida real del comando de tests no es una verificación.

4. **El Removal se registra, no se borra.** Un requisito retirado queda en el
   baseline con su nota de por qué y su plan de migración.

5. **Los requisitos van con su número y su escenario.** Un requisito sin
   escenario no es testeable, y por lo tanto no es un requisito.

## Nombres de cambio

Kebab-case, describiendo el **cambio**, no el tipo:

- `checkout-refund-policy` ✅
- `add-refunds` ⚠️ ambiguo
- `feature-1` ❌

## Ciclo de vida

```
propose ──▶ [G1] ──▶ spec ∥ design ──▶ [G2] ──▶ tasks ──▶ [G3]
                                                            │
                                                            ▼
                                    archive ◀── [G4] ◀── verify ◀── apply
```

Las puertas G1..G4 son Human-in-the-Loop. El orquestador se detiene en cada
una y espera aprobación.

## Persistencia en Engram

| Artefacto | Topic key |
|-----------|-----------|
| Proposal | `sdd/<change>/proposal` |
| Spec | `sdd/<change>/spec` |
| Design | `sdd/<change>/design` |
| Tasks | `sdd/<change>/tasks` |
| Verification | `sdd/<change>/verification` |

El nombre determinista es lo que permite que cualquier fase encuentre de forma
fiable lo que escribió otra fase.
