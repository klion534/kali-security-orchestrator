# Playbook — Desarrollo con IA: De 0 a Producción

> Síntesis operativa de las tres clases del curso **Desarrollo con IA: De 0 a
> Producción** (Gentleman Programming), aplicada a este repositorio.
>
> No es un resumen teórico. Es el manual que dice **qué hacer, cuándo, y cómo
> saber que lo hiciste bien**.

---

## Índice

1. [El nuevo paradigma](#1-el-nuevo-paradigma)
2. [Fundamentos técnicos: qué hay bajo el capó](#2-fundamentos-técnicos-qué-hay-bajo-el-capó)
3. [Elección de modelo](#3-elección-de-modelo)
4. [Ingeniería de prompts](#4-ingeniería-de-prompts)
5. [RAG: el guardarraíl de la verdad](#5-rag-el-guardarraíl-de-la-verdad)
6. [Vibe coding vs. ingeniería de software](#6-vibe-coding-vs-ingiería-de-software)
7. [La ventana de contexto](#7-la-ventana-de-contexto)
8. [Agentes, multiagentes y worktrees](#8-agentes-multiagentes-y-worktrees)
9. [Spec-Driven Development](#9-spec-driven-development)
10. [El stack agéntico: MCP, Skills, AGENTS.md](#10-el-stack-agéntico-mcpskillsagentsmd)
11. [Engram: la memoria que resuelve la amnesia](#11-engram-la-memoria-que-resuelve-la-amnesia)
12. [Human in the Loop](#12-human-in-the-loop)
13. [De código a producción: testing, CI/CD y releases](#13-de-código-a-producción-testing-cicd-y-releases)
14. [El checklist del orquestador](#14-el-checklist-del-orquestador)

---

## 1. El nuevo paradigma

### La realidad del sector

La IA dejó de ser un accesorio y pasó a ser **el motor central de la
competitividad**. No se trata de escribir código más rápido: se trata de
liderar un ecosistema donde la ejecución manual se delega a modelos
generativos, mientras el humano asume la responsabilidad del **diseño, la
integridad y la escalabilidad** del sistema.

El desarrollador de 2026 no es un "usuario de chat". Es un **arquitecto y
orquestador con fundamentos de ingeniería inquebrantables**.

> "Aconsejar a otros que dejen de aprender a escribir código porque la IA lo va
> a automatizar será recordado como uno de los peores consejos profesionales de
> la historia." — Andrew Ng

La programación sigue siendo el lenguaje del control. La IA es el motor de
ejecución.

### Las cuatro claves

1. **Crear software no es programar.** Es diseñar, decidir y verificar.
2. **Especializarse ya no es suficiente.** El mercado no busca usuarios de
   chat, busca orquestadores.
3. **La IA no puede dominarte.** Si no entiendes lo que produce, no es
   escalable.
4. **Utilizar IA no es opcional.** Es la infraestructura del oficio.

### SWE-Bench verificado

El benchmark de referencia: **500 problemas reales de GitHub**, validados por
anotadores humanos, que miden si un modelo puede resolver problemas de
ingeniería de software del mundo real generando parches para bases de código
Python.

**Por qué importa en este proyecto:** el benchmark no mide "qué tan bonito
escribes el prompt". Mide si el sistema **completa tareas de ingeniería
completas**. Ese es el estándar contra el que hay que medir este stack.

---

## 2. Fundamentos técnicos: qué hay bajo el capó

Entender esto no es opcional. Es lo que separa a quien usa la IA de quien la
**dirige**.

| Concepto | Qué es realmente | Dónde te muerde |
|----------|------------------|-----------------|
| **LLM** | Entidad matemática que predice la siguiente secuencia. No razona: predice sobre lo aprendido. | Confundir "parece que razona" con "razona". |
| **Parámetros** | Las "conexiones neuronales" del modelo. Más parámetros = más capacidad de representar conceptos abstractos. | Elegir un modelo por tamaño sin mirar la tarea. |
| **Tokens** | Las piezas en las que el modelo divide el texto. **Es la unidad de cobro y de atención.** | overlooking que el modelo no lee palabras, lee tokens. |
| **Costes** | Lo que cuesta cada respuesta, cobrado por tokens. | Ignorar el coste en tareas que se reintentan 5 veces. |
| **Ventana de contexto** | La memoria a corto plazo. El máximo que puede leer, procesar y recordar a la vez. | Excederla: el modelo "olvida" el principio del documento y **alucina**. |
| **Multimodalidad** | Ver imágenes, oír audio, analizar vídeo. | No poder arreglar un bug que solo existe en un screenshot. |
| **Latencia** | Tiempo hasta el primer token. | UX de la herramienta; y el tiempo real del equipo. |
| **Alucinaciones** | El mayor defecto del LLM: cuando no sabe, se inventa la respuesta. | Todo lo que no esté anclado a una fuente verificable. |
| **Razonamiento vs. rapidez** | Los modelos de razonamiento pausan, planifican y verifican sus pasos internamente. | Usar el modelo rápido para un problema difícil, y pagar 5 reintentos. |

### El error de razonamiento más caro

> "Funciona" **no** significa "es correcto".
>
> El código generado por IA sin tests es **deuda técnica por diseño**. La IA
> genera más rápido de lo que podemos revisarlo, y no comprende las
> ramificaciones de seguridad de cada línea que escribe.

---

## 3. Elección de modelo

### Los dos ecosistemas

| | **Ecosistema local** | **Ecosistema cloud** |
|---|---|---|
| **Herramientas** | LM Studio (visual), Ollama (terminal) | APIs de frontera |
| **Privacidad** | Absoluta: los datos no salen de la máquina | Los datos salen a servidores de terceros |
| **Coste** | Cero por token; coste fijo alto (hardware) | Por token; sin coste fijo |
| **Contexto** | Generalmente menor | Generalmente amplio (100k → 1M+) |
| **Ideal para** | Lógica propietaria, datos sensibles, tareas simples de alto volumen, trabajo offline | Arquitectura, requisitos ambiguos, debugging difícil, generación de código a escala |

**Regla:** la soberanía de los datos gana a cualquier delta de capacidad. Datos
regulados o lógica propietaria no salen de la máquina sin una decisión
explícita.

### La tabla de routing de este proyecto

| Fase / tarea | Clase de modelo | Por qué |
|--------------|-----------------|---------|
| Explorar | rápido y barato | Leer y resumir; no hace falta profundidad de razonamiento |
| Construir prompts | barato | Transformación estructurada |
| Spec, Design | **razonamiento** | Resolver ambigüedad, analizar trade-offs |
| Implementar | modelo fuerte de código | La capacidad central |
| **Verificar** | fuerte, **de otra familia** | Otra familia de modelos encuentra otros bugs |
| **Revisión de seguridad** | **otra familia que la del autor** | El autor nunca juzga su propio código |
| Resumir / changelog | el más barato | Mecánico |

> **El revisor no puede ser el autor.** Un modelo que escribió el código
> racionaliza su propio error. Usá un proveedor distinto para la verificación.

---

## 4. Ingeniería de prompts

> "Garbage in, garbage out" nunca estuvo tan vigente como en la era de los LLM.

### El prompt perfecto: cinco ejes

| # | Eje | Pregunta | Qué previene |
|---|-----|----------|--------------|
| 1 | **Rol** | ¿Quién soy? | Profundidad y especialidad equivocadas |
| 2 | **Contexto** | ¿Dónde estamos? | Stack adivinado, dominio adivinado |
| 3 | **Tarea exacta** | ¿Qué necesitas? | Un "sistema" en lugar de un entregable |
| 4 | **Restricciones** | ¿Qué límites hay? | Contraseñas en texto plano, sin manejo de errores |
| 5 | **Formato de salida** | ¿Cómo lo quieres? | Prosa que hay que re-parsear |

### El mal prompt

> "Haz un código para un login en Python."

Sin contexto (¿web, CLI, microservicio?), sin tecnología específica (¿Flask,
Django, FastAPI?), sin reglas de seguridad (contraseñas en texto plano),
sin formato. El modelo tiene que **adivinar**, y va a adivinar mal de una
forma que no se integra con tu proyecto.

### El buen prompt

```markdown
[1. Rol]
Actúa como un desarrollador backend Senior especializado en ciberseguridad.

[2. Contexto]
Estoy construyendo una API REST para un e-commerce usando Python 3.10.
La base de datos es PostgreSQL 15. El proyecto ya tiene FastAPI, SQLAlchemy 2
y pyjwt instalados; no añadas dependencias.

[3. Tarea]
Escribe el endpoint de login de usuarios.

[4. Restricciones]
- Framework: FastAPI. Estilo: async/await, dependency injection para la sesión.
- Contraseñas con bcrypt; nunca en texto plano, nunca reversibles.
- JWT HS256, expiración 15 minutos, `sub` = id de usuario.
- Errores: 401 con body {"error":"invalid_credentials"} para credenciales
  inválidas (mismo mensaje para usuario inexistente y contraseña incorrecta);
  422 para payload malformado.
- No incluyas documentación, ejemplos de uso ni README.

[5. Formato]
Devuelve únicamente el bloque de código completo del archivo, con comentarios
breves donde la intención no sea obvia. Sin explicaciones previas ni posteriores.
```

### Reglas

- **El prompt tiene que funcionar en frío.** Pegarlo en una sesión nueva, sin
  otro contexto, y seguir siendo ejecutable. Ese es el test.
- **Prohibidos los cuantificadores vagos**: "robusto", "seguro", "optimizado",
  "limpio". Reemplazar por un criterio verificable, o borrar.
- **El formato de salida incluye los negativos**: "sin explicaciones", "sin
  TODOs", "sin dependencias nuevas".
- **Lo que no sé va como `ASSUMPTION:` explícita**, nunca como adivinanza
  silenciosa.
- **Las cadenas exactas se citan verbatim** en el idioma del usuario.

---

## 5. RAG: el guardarraíl de la verdad

RAG ancla el conocimiento del modelo a documentos específicos, eliminando
alucinaciones y forzándolo a operar dentro de una base de conocimiento
verificada.

### El modelo NotebookLM

1. **Tú eliges las fuentes.** YouTube, docs, PDFs, sitios web, Drive. El modelo
   no decide qué es autoritativo — esa decisión ES el valor del sistema.
2. **Chunking por significado**, no por tamaño fijo. Un chunk debe bastar para
   responder una pregunta por sí solo.
3. **Embeddings + índice** (híbrido: semántico + BM25 por keyword).
4. **Retrieval** del top-k más relevante, con re-ranking.
5. **Respuesta anclada** solo a los chunks recuperados, con cita por afirmación.
6. **Citas numeradas** que llevan al punto exacto de la fuente.

### La regla que lo hace funcionar

> Si la respuesta no está en el contexto recuperado, la salida correcta es
> *"The provided sources do not cover this"*. El modelo **tiene que poder
> abstener**, y el prompt tiene que premiar la abstención sobre la
> adivinanza.

### La herramienta de estudio

NotebookLM convierte el consumo pasivo de datos en aprendizaje activo:

| Herramienta | Qué genera | Para qué sirve |
|-------------|------------|----------------|
| Mapa mental | Estructura visual de los conceptos | Comparar estructuras de un vistazo |
| Resumen de audio/vídeo | Un podcast de ~5 min | Repasar mientras viajas |
| Tarjetas didácticas | Una baraja de preguntas/respuestas | Autoevaluación y repetición espaciada |
| Cuestionario | Una prueba formal | Medir qué aprendiste y qué reforzar |

**Uso en este proyecto:** los apuntes del curso se pueden indexar como corpus
y consultar con citas verificables en lugar de improvisar.

### Anti-patrones

| Anti-patrón | Por qué falla |
|-------------|--------------|
| El corpus infinito | Todo se indexa → cada query recupera ruido. Hay que curar. |
| Chunking por tamaño fijo | Corta funciones por la mitad. Garantiza malas respuestas. |
| Sin ruta de "no sé" | El modelo inventa. Hay que darle la salida explícita. |
| Solo búsqueda vectorial | Los identificadores exactos (códigos de error, versiones) se encuentran por keyword. |
| Citas sin verificar | Una cita que no contiene la afirmación es peor que no citar. |
| Sin set de evaluación | No puedes saber si tu cambio ayudó. Mide antes y después. |

---

## 6. Vibe coding vs. ingeniería de software

| | Vibe coding | Ingeniería de software |
|---|---|---|
| **Guía** | Intuición | Diseño, control, pruebas, mantenimiento |
| **El código es** | El objetivo | Un artefacto transitorio y derivado |
| **El humano es** | El que corrige errores | El **Validador de Intención** |
| **Escala** | Se rompe | Se mantiene |

La diferencia no es de ella. Es de **dónde viene la intención**.

> En SDD, el humano valida la intención y el código se convierte en un artefacto
> transitorio y derivado. Ese es el cambio de paradigma completo.

---

## 7. La ventana de contexto

### El problema

> "La mayoría de los desarrolladores usan la IA como un chat glorificado. Esto
> no es un problema del modelo — es un problema de **ARQUITECTURA**."

La memoria de la IA es grande, pero limitada. La IA a veces "simplifica" el
contexto (compresión). Formas de compresión: *summarization*, *sliding windows*,
*compresión jerárquica*, *guardados en memoria*.

### Las cuatro técnicas

| Técnica | Qué hace | Cuándo |
|---------|----------|--------|
| **Aislamiento por subagente** | El subagente arranca con contexto **fresco**. El padre queda limpio. | Exploración, verificación aislada, escritores paralelos |
| **Divulgación progresiva** | No se pega el spec entero. Se pega el índice y quien lo necesita abre la sección. | `AGENTS.md` < 500 líneas, skills, registro de skills |
| **Compresión jerárquica** | Se comprime en capas, y **nunca se comprime una decisión**. | Sesiones largas, proyectos de varias semanas |
| **Recuperación de contexto** | Tras compactar: `mem_context` → `mem_search` → `mem_get_observation` → **leer el archivo real**. | Reanudar trabajo |

### La regla del presupuesto

> **Cada token en la ventana es un impuesto sobre la atención. Gastémoslo en
> señal.**

| Clase | Ejemplos | Tratamiento |
|-------|----------|-------------|
| **Ancla** | La tarea, las restricciones, el spec, los criterios de aceptación | Siempre presente. Nunca comprimida. |
| **Referencia** | Contratos de API, schemas, tipos | A demanda, citada por ruta |
| **Trabajo** | El diff en discusión, el archivo actual | Rota entra y sale |
| **Ruido** | Dumps de archivos completos, logs, historia no relacionada | Nunca entra |

### Lo que nunca se comprime

**Las decisiones, las restricciones y las preguntas abiertas.** Perder *"elegimos
soft delete porque el requisito de auditoría prohíbe el borrado duro"* es
catastrófico. Perder el log crudo es gratis.

---

## 8. Agentes, multiagentes y worktrees

### Qué es un agente

Un sistema que puede **percibir, decidir y actuar** para cumplir un objetivo.
Usa modelos para razonar sobre qué hacer, usa herramientas externas (APIs, BD,
código) y opera de forma semi-autónoma o autónoma.

### El bucle del agente vs. el chatbot

| Chatbot | Agente |
|---------|--------|
| Pregunta → Respuesta | Bucle autónomo |
| Sin acceso al sistema | Lee y escribe archivos |
| Un solo turno | Ejecuta y verifica |
| Requiere copy-paste | Itera |

### El problema de concurrencia

En entornos multiagente aparece el problema: **múltiples IAs intentando mutar
los mismos archivos simultáneamente**.

La solución arquitectónica son los **Git Worktrees**: cada agente trabaja en
una carpeta física independiente vinculada a una rama distinta. Se eliminan las
colisiones y la orquestación asíncrona se vuelve segura.

```
main-repo/                 ← worktree principal, en main, limpio
├── .worktrees/
│   ├── feature-a/         ← agente A, rama feature/a
│   └── feature-b/         ← agente B, rama feature/b
```

**Reglas duras:**
- Un worktree por agente. Nunca se comparte directorio.
- Una rama por worktree.
- El worktree principal se queda en `main` y limpio.
- Los worktrees viven en `.worktrees/`, gitignored.
- **Superficies disjuntas**: si dos agentes tocan el mismo archivo, no son
  paralelos — son secuenciales.
- La integración vuelve por **PR**. Un worktree no es una estrategia de merge.

---

## 9. Spec-Driven Development

### La inversión

```
Vibe coding:   intuición -> código -> esperanza
Ingeniería:    intención -> spec -> diseño -> tareas -> código -> EVIDENCIA
```

### El pipeline

```
        ┌──────────┐
        │  EXPLORE │  read-only: entender el codebase
        └────┬─────┘
             ▼
        ┌──────────┐
        │ PROPOSE  │  intención, alcance, rollback
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
        │   TASKS   │  numeradas, por fases, testeables
        └────┬─────┘
             ▼
        ┌──────────┐
        │   APPLY   │  TDD: RED -> GREEN -> REFACTOR
        └────┬─────┘
             ▼
        ┌──────────┐
        │  VERIFY  │  ejecución real + matriz de cumplimiento
        └────┬─────┘
             ▼
        ┌──────────┐
        │  ARCHIVE │  merge del delta, cierre del cambio
        └──────────┘
```

`SPEC` y `DESIGN` corren **en paralelo**, en contextos aislados. Esa
independencia es el punto: dos perspectivas, y el orquestador reconcilia.

### Las tres modalidades de SDD

| Modalidad | El spec | El código | Cuándo |
|-----------|---------|-----------|--------|
| **Spec First** | Lo escribes tú | La IA escribe el código | Desarrollo nuevo, proceso repetible |
| **Spec Anchored** | Los docs evolucionan con el código; la IA los actualiza | — | Documentación viva, proyectos activos |
| **Spec As Source** | "Desarrollas" dentro del requerimiento | Todo autogenerado, sin edición humana directa | Dominios altamente constringidos |

### El contrato de resultado

Cada subagente devuelve siempre lo mismo:

```
**Status**: success | partial | blocked
**Summary**: 1-3 frases
**Artifacts**: rutas exactas
**Next**: próxima fase, o "none"
**Risks**: riesgos concretos, o "None"
```

Sin contrato no hay orquestación — solo caos.

### Las puertas HITL

| Puerta | Momento | Qué se muestra |
|--------|---------|----------------|
| G1 Alcance | tras `propose` | Intención, dentro/fuera de alcance, rollback |
| G2 Diseño | tras `spec` + `design` | Requisitos, escenarios, ADRs, riesgos |
| G3 Plan | tras `tasks` | Lista numerada, por fases, con mapeo a tests |
| G4 Merge | tras `verify` | Matriz de cumplimiento, salida real de tests, riesgo residual |

---

## 10. El stack agéntico: MCP, Skills, AGENTS.md

### La evolución de los editores

```
2022 — IDEs clásicos (autocompletado)
2023 — Chat-based coding
2024 — Copilots
2025 — AI agents
2026 — AI-first development environments
```

### Las cuatro capacidades del AI-First IDE

1. **Contexto completo** — el modelo ve todo el proyecto, no solo el archivo.
2. **Edición multi-archivo** — cambios coordinados en varios ficheros a la vez.
3. **Ejecución real** — comandos, tests y builds dentro del proyecto.
4. **Iteración autónoma** — detecta errores y se autocorrige.

**El desarrollador pasa a ser el director del proceso.**

### Plan Mode

El agente primero elabora un plan detallado, te lo muestra para revisión, y
**solo ejecuta cuando das el OK**. Evita cambios destructivos.

| Úsalo cuando | No lo uses cuando |
|---------------|-------------------|
| Tareas grandes | Tareas pequeñas |
| Refactors | Correcciones obvias |
| Supervisión de estrategia | Prototipado rápido |

### AGENTS.md — el system prompt persistente

Archivos de texto que actúan como prompts persistentes del proyecto.

**Regla dura: no debe exceder 500 líneas.** Pasado ese punto, el ruido diluye
la señal y el contexto se infla sin valor.

**Qué incluir:**
- Qué es el proyecto y qué NO es
- Stack y comandos (build, test, lint)
- Convenciones de código reales del repo
- Reglas de testing
- Reglas de seguridad
- Flujo de trabajo de git/PR
- Los anti-patrones que dan problemas

**Qué NO incluir:** el código en sí, historia del proyecto,Documentation de
otras herramientas, ni reglas que solo aplican una vez.

### MCP — Model Context Protocol

Interfaz estándar para conectar cualquier herramienta.

| MCP | Skills |
|-----|--------|
| **Servicios externos** | **Conocimiento interno** |
| Acceso a herramientas | Instrucciones y mejores prácticas |
| Conexión en tiempo real | El agente las lee **antes** de actuar |
| Acciones sobre servicios externos | Archivos `SKILL.md` + scripts |
| API estándar (JSON-RPC) | No siempre se usan |

**MCP es poder; Skills es conocimiento.** No son intercambiables.

### Skills — conocimiento modular

Gracias a plataformas como `skills.sh`, se dota al agente de habilidades
ultra-específicas (p. ej. *Frontend Design Expert*) de forma **modular**.

Esto mantiene el **contexto principal limpio** y asegura que el agente solo
cargue las reglas de diseño React cuando realmente está trabajando en un
componente de frontend. **Optimiza tokens y precisión.**

> Las skills de este repo: `sdd-workflow`, `prompt-perfect`,
> `context-engineering`, `model-selection`, `testing-strategy`,
> `ci-cd-pipeline`, `rag-knowledge-base`, `git-worktrees`, `veil-secrets`.

### El problema del contexto y su solución

La evolución histórica del stack fue impulsada por **dolor real**, no por
tendencia:

```
Monolito (un AGENTS.md gigante)
   ↓  ¿el contexto se infla?
Skills Registry — del monolito a módulos
   ↓  ¿el agente olvida entre sesiones?
Engram — resolviendo la amnesia
   ↓  ¿y las decisiones de negocio?
Human in the Loop — el humano decide
```

---

## 11. Engram: la memoria que resuelve la amnesia

**Go binary · SQLite + FTS5 · BM25 search · MCP Server · Agent-agnostic**

```
Agente (Claude Code / OpenCode / Gemini CLI / Codex / VS Code / ...)
    ↓ MCP stdio
Engram (un solo binario Go)
    ↓
SQLite + FTS5 (~/.engram/engram.db)
```

Una base de datos, un archivo, cero dependencias. Funciona con cualquier agente
compatible con MCP.

### Por qué importa

El coste de una sesión nueva no son los tokens: es **tú, re-explicando las
mismas decisiones cada mañana**. Engram lo elimina: el agente escribe lo que
aprende mientras trabaja y lo busca **antes de buscarte a vos**.

### El protocolo

- **Al inicio de la sesión:** resolver el proyecto → `mem_context` →
  `mem_search`.
- **Durante:** `mem_save` proactivo tras cada decisión, fix, descubrimiento o
  convención.
- **Al cerrar:** `mem_session_summary` con Goal / Instructions / Discoveries /
  Accomplished / Next Steps / Relevant Files.

### Nombres deterministas

`engram` / `sdd/{change-name}/{artifact-type}` — así cualquier fase encuentra
de forma fiable lo que escribió otra fase.

---

## 12. Human in the Loop

El HITL no es "pedir permiso". Es **diseñar el sistema para que las decisiones
que importan las tome una persona**.

Tres niveles de autonomía:

| Nivel | El agente decide | El humano decide |
|-------|------------------|------------------|
| **Asistido** | Cómo | Qué y cuándo |
| **Supervisado** | Cómo, dentro del alcance | El alcance y las gates |
| **Autónomo** | Todo dentro de límites duros | Los límites |

**Lo que nunca se delega:** el alcance del negocio, los valores por defecto que
afectan a usuarios, y el deployment a producción.

---

## 13. De código a producción: testing, CI/CD y releases

### El riesgo oculto

> **Más IA = más velocidad = más riesgo oculto.**

| Síntoma | Causa real |
|---------|-----------|
| La IA genera código más rápido de lo que podemos revisarlo | Volumen sin gates |
| Múltiples tareas en paralelo = pérdida de contexto | Contexto no particionado |
| "Funciona" no significa seguro ni correcto | Sin tests |
| El ritmo de cambio supera la capacidad de entender qué cambia | Sin spec |
| Deuda técnica invisible | Sin ownership ni revisión |

### La IA no conoce tu negocio

> **Producción exige confianza, no esperanza.**

**Principio de Responsabilidad Profesional:** el desarrollador es el único
responsable legal y profesional del código en producción. Si el sistema falla
y compromete datos o ingresos, el cliente no le va a pedir cuentas a Claude ni a
GPT. La responsabilidad recae en quien aprobó el despliegue.

### Qué testear cuando programas con IA

> "Generar código con IA ≠ validar código. Sin tests, la IA construye sobre
> arena."

**No se trata de testearlo todo, sino de blindar el valor de negocio.** El
criterio es el riesgo, no la cobertura:

| Prioridad | Qué | Ejemplo |
|------------|-----|---------|
| P0 | Lógica crítica de negocio, dinero, auth, permisos, integridad de datos | Elegibilidad de reembolso, cálculo de precio, roles |
| P1 | Flujos核心 y sus bordes | Los 5 journeys principales + límites |
| P2 | Contratos, integraciones, superficie de API | Formas de respuesta, códigos de error |
| P3 | Performance, resiliencia, observabilidad | Carga, timeouts, degradación |
| P4 | Cosmético, copy, layout | Normalmente no vale un test |

**Tip del curso:** se puede delegar en la IA la redacción de la suite, pero el
desarrollador debe **definir y validar** que los escenarios sean realistas y
cubran los casos de borde del negocio.

### CI/CD mínimo viable

| Concepto | Qué es |
|----------|--------|
| **CI** | Cada push compila y pasa los tests automáticamente. Si algo rompe, se detecta al instante. |
| **CD** | Si pasa los tests, llega a producción solo, sin que nadie pulse un botón. |
| **PR** | Petición formal de integrar. Antes: CI corre todos los checks y los demás revisan. Si algo falla, **el merge queda bloqueado**. |

**Las reglas de oro:**
1. Toda feature entra vía PR a `main`.
2. **Nunca push directo a `main`.** Se bloquea la rama para que solo acepte
   merges vía PR.
3. Todo PR ejecuta: **lint** (formato), **validaciones** (seguridad), **tests**
   (funciona), **build**.
4. Si algo falla → el PR se bloquea.
5. `main` siempre está lista para producción.

### GitHub Actions

Un `.yml` en `.github/workflows/`. La redacción se delega a la IA, pero debe
definir pasos claros: instalación de dependencias, ejecución del linter, paso
exitoso de la suite de tests. GitHub levanta una VM, ejecuta tus pasos y, si
algo falla, te avisa y bloquea el PR.

### CI/CD inteligente gracias a la IA

**Code Review automático con agentes IA.** Cada PR recibe una revisión
automática que comprueba:
- ¿Sigue las convenciones del proyecto?
- ¿Hay problemas de rendimiento obvios?
- ¿La lógica tiene sentido?
- ¿Faltan tests para algún caso?
- ¿Hay problemas de seguridad?

**Security Review automático.** La seguridad no es un añadido; es un requisito
arquitectónico. La IA genera código rápido pero puede introducir
vulnerabilidades: SQL injection, XSS, secrets expuestos, dependencias
vulnerables. Herramientas: `claude-code-security-review` (Action oficial de
Anthropic), CodeRabbit, Copilot reviews, GGA.

### Release Please

El versionado solía sufrir de hastío burocrático → documentación pobre. Google
resolvió esto con **Release Please**:

**Tras cada merge en `main`:**
- Se crea automáticamente un **Release PR**
- Se actualiza `package.json` con la nueva versión
- El changelog se regenera desde los conventional commits

**Al hacer merge del Release PR:**
- Segundo deploy a producción
- Se crea el tag `vX.Y.Z`
- Se publica el GitHub Release
- Las release notes se generan **con IA** (el extra que añadimos nosotros)

El versionado sigue Conventional Commits:

| Tipo | Bump |
|------|------|
| `fix:` | patch |
| `feat:` | minor |
| `BREAKING CHANGE:` | major |
| `docs:`, `test:`, `chore:`, `ci:`, `refactor:`, `perf:` | — |

---

## 14. El checklist del orquestador

### Antes de cada tarea

- [ ] ¿Es sustancial? Si no → inline.
- [ ] ¿Entiendo el código afectado? Si no → explorar primero.
- [ ] ¿Consulté la memoria? `mem_context` / `mem_search` antes de preguntar.
- [ ] ¿La instrucción tiene los cinco ejes? Rol, contexto, tarea, restricciones,
      formato.
- [ ] ¿Sé qué modelo corresponde? Coste, latencia, contexto, privacidad.

### Durante

- [ ] El subagente tiene un brief completo: objetivo, rutas, standards, contrato
      de salida, y **"no delegues"**.
- [ ] Las escrituras paralelas están en superficies disjuntas (o en worktrees).
- [ ] TDD: vi el test fallar antes de hacerlo pasar.

### Antes de cerrar

- [ ] La suite pasó **de verdad**, y muestro la línea de resumen real.
- [ ] Cada requisito del spec tiene su evidencia ejecutada.
- [ ] El diff se lee como lo leería un revisor.
- [ ] Sin secretos, sin debug, sin archivos huérfanos.
- [ ] Los commits son unidades de trabajo revisables.
- [ ] `mem_save` de la decisión.
- [ ] `mem_session_summary` antes de cerrar la sesión.

### Antes de mergear

- [ ] PR, no push directo.
- [ ] Lint, tests, build y security review en verde.
- [ ] Revisión humana: el autor no es el revisor.
- [ ] `main` queda verde.

---

## Cierre

> **Las herramientas son efímeras; los fundamentos son permanentes.**

El éxito en 2026 no depende de qué IA uses, sino de tu capacidad para mantener
la arquitectura, las pruebas y el mantenimiento **por encima del ruido
tecnológico**.

En 2026, la IA no ha eliminado al desarrollador: ha eliminado la mediocridad
técnica. La tecnología se encarga de la mecánica, pero la responsabilidad de la
visión, la ética y la calidad final recae en el humano.

**El control final siempre pertenece al profesional.**

Los tres pilares del profesional de élite:

1. **Dominio de fundamentos técnicos** — sin bases sólidas es imposible auditar
   la producción.
2. **Maestría en orquestación** — `AGENTS.md`, MCPs, skills y flujos
   multiagente deterministas.
3. **Control crítico (HITL)** — juicio crítico sobre la estrategia, para que el
   software no solo funcione, sino que sea sostenible y escalable en
   producción.
