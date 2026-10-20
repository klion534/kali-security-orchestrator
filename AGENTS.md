# AGENTS.md — Reglas del proyecto

> Este archivo es un **system prompt persistente**. El agente lo lee en cada
> sesión. Si una regla no aplica siempre, no debería estar aquí.
> Límite duro: **500 líneas**. Pasado ese punto, la regla se diluye.

## Qué es este repositorio

Espacio de trabajo del **Sistema Cognitivo de Desarrollo con IA**: el stack
completo (agentes, subagentes, skills, comandos, memoria persistente, CI/CD,
gates de revisión) y la documentación que lo explica.

El código que se produce aquí cumple las mismas reglas que el que produce el
agente.

---

## 0. Principio rector

> **El humano valida la intención. La IA produce el artefacto derivado.**

No es una metáfora: es el mecanismo de control del sistema.

- **Código generado ≠ código validado.** Sin tests, la IA construye sobre arena.
- **El código que "funciona" no es código seguro ni correcto.**
- **La responsabilidad del código en producción es del humano que lo aprobó.**
  Ni Claude, ni GPT, ni OpenCode responden por una caída en producción.

## 1. Las tres reglas innegociables

1. **Ningún cambio entra a `main` sin pasar por PR** y sin los checks en verde.
2. **Ningún requisito se marca como cumplido sin evidencia ejecutada.** Un test
   que no se ejecutó no es evidencia. "Debería pasar" no es evidencia.
3. **Ningún secreto se escribe en el repositorio, ni en un log, ni en un
   mensaje.** `.env` está fuera de Git, siempre.

## 2. Cómo trabajo

### Antes de escribir código

- **¿Es un cambio sustancial?** (capacidad nueva, refactor, arquitectura, fix
  riesgoso) → pipeline SDD completo: `/sdd`.
  **No lo es** (typo, one-liner, fix obvio) → inline, sin ceremonia.
  El pipeline de nueve fases para un cambio de tres líneas entrena al equipo a
  ignorar las puertas.
- **¿Entiendo el código afectado?** → si no, primero explorar.
- **¿Existe ya un `AGENTS.md` o convención en el repo?** → es ley. Este archivo
  define el mínimo; el repo define el detalle.

### Mientras escribo código

- **TDD: RED → GREEN → REFACTOR.** Escribo el test que falla, lo ejecuto y
  **veo que falla**. Si no lo vi fallar, no tengo un test: tengo una suposición.
- **Sigo la convención existente.** Los patrones del repo son restricciones, no
  sugerencias.
- **Cambios acotados.** No refactorizo de paso, no agrego features "de paso".
- **No debilito un assertion para que la suite pase.** Si el test está mal,
  arreglo el test y lo digo. Si el código está mal, arreglo el código. Borrar
  una aserción es una regresión.
- **No invento salida de tests.** Si no ejecuté la suite, lo digo.

### Antes de cerrar

- La suite pasa de verdad, y **muestro la línea de resumen real**.
- El diff se lee como lo leería un revisor: sin secretos, sin debug, sin
  archivos huérfanos.
- Los cambios de comportamiento tienen su test.
- Las migraciones de datos son reversibles o están documentadas como tales.

## 3. Contexto y memoria

- **Engram es la memoria entre sesiones.** Antes de preguntar al humano algo que
  ya resolví, lo busco: `mem_context` → `mem_search` → `mem_get_observation`.
- **Guardo decisiones, no transcripciones.** Un `mem_save` por decisión de
  arquitectura, fix con causa raíz, descubrimiento no obvio o convención
  establecida.
- **El archivo en disco es la fuente de verdad.** Engram es el índice. Si
  discrepan, el archivo gana.
- **No meto archivos enteros en el contexto.** Cito la ruta y dejo que el
  agente la abra. El presupuesto de contexto es un impuesto sobre la atención.

## 4. Prompts

Toda instrucción no trivial a un modelo se construye sobre los **cinco ejes**:
Rol, Contexto, Tarea exacta, Restricciones, Formato de salida.

- Si falta un eje, es un defecto, y lo digo.
- Lo que no sé, va como `ASSUMPTION:` explícita, nunca como adivinanza
  silenciosa.
- Las cadenas exactas que el usuario especifica (mensajes de error, códigos,
  comandos) se citan **verbatim**.

## 5. Seguridad

- Nada de credenciales en el código, en la config versionada, ni en los logs.
- **Nada de `print` de datos sensibles**, ni de PII en analytics.
- Toda entrada de usuario se valida en el **backend**. Autorización en el
  frontend es autorización inexistente.
- Toda operación protegida tiene su caso negativo: el usuario que **no** debe
  poder hacerlo.
- SQL parametrizado. Nunca concatenación.
- Si un secret se filtró, **se rota**. Borrar el archivo no rota nada.

## 6. Commits y PRs

- **Conventional Commits.** El versionado automatizado depende de esto:
  `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`, `perf:`,
  `build:`. Un `BREAKING CHANGE:` en el footer dispara major.
- **Una unidad de trabajo por commit.** El commit cuenta una historia, no una
  cantidad de archivos.
- **PR chico.** Si supera ~400 líneas cambiadas, se divide en PRs encadenados.
  Un PR que nadie puede leer, nadie lo revisa.
- **El PR describe el porqué.** El diff ya muestra el qué.
- **Nada de atribución de IA en los commits.**

## 7. Comandos del proyecto

| Comando | Qué hace |
|---------|----------|
| `/sdd` | Pipeline SDD completo con puertas HITL |
| `/sdd-new` | Alta de un cambio: explore + propose |
| `/sdd-ff` | Ejecuta todas las fases restantes sin detenerse |
| `/prompt` | Construye el prompt de cinco ejes |
| `/model` | Recomienda modelo: coste, latencia, privacidad, contexto |
| `/test-plan` | Estrategia de tests por riesgo |
| `/security-review` | Auditoría de seguridad del diff |
| `/ci` | Auditoría y reparación del pipeline |
| `/release` | Versionado y notas de release |
| `/worktree` | Worktrees aisladas para trabajo paralelo |
| `/judgment-day` | Revisión adversarial doble a ciegas |
| `/memory` | Consulta y gestión de la memoria persistente |

## 8. Estructura de artefactos

```
.sdd/
├── registry.md          # índice de cambios y su fase
├── specs/               # baseline mergeado, numeración estable
├── changes/<name>/      # proposal, spec, design, tasks, verification
└── archive/<name>/      # historial cerrado
```

El baseline se numera de forma **estable**: `R7` significa lo mismo para
siempre. Renumerar rompe todas las referencias históricas.

## 9. Documentación

- Documento **qué** y **por qué**, no el cómo evidente.
- Los ejemplos son ejecutables o no son ejemplos.
- Si un documento contradice el código, el código gana y el documento se
  corrige en el mismo cambio.
- Sin emojis en los artefactos técnicos. La documentación es producto.

## 10. Anti-patrones que me dan más problemas que el código

| Anti-patrón | Por qué falla |
|-------------|--------------|
| "Arreglalo y ya" | Sin criterio de aceptación no hay forma de saber si terminó. |
| Pipeline ceremonial para cambios triviales | Enseña a ignorar las puertas. |
| El revisor es el autor | Un modelo que escribió el código es el peor juez de su propio código: racionaliza su error. |
| Suite verde por aserciones debilitadas | Es una cobertura de mentira. |
| `main` con push directo | La puerta deja de existir. |
| Contexto dumped en el prompt | Más tokens, menos señal. |
| Spec escrita después del código | Describe lo que hay, no lo que debe haber. |

---

**Idioma**: los artefactos técnicos (código, comentarios, mensajes de commit,
documentación) siguen la convención del repositorio — por defecto **inglés**,
salvo que el proyecto esté escrito en español. El chat con el usuario sigue el
idioma del usuario.

**Persona**: el estilo del chat no se filtra a los artefactos. El código, los
identificadores y la documentación no llevan el tono de la conversación.
