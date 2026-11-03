# Orquestador modular de auditoría para Kali Linux

## Header

- **Feature**: `kali-security-orchestrator`
- **Estado**: En progreso; núcleo de políticas y catálogo implementado
- **Workflow**: Organic Driven Development (ODD)
- **Alcance**: Orquestar herramientas defensivas de auditoría, normalizar evidencias y generar informes.
- **Implementación prevista**: Python 3.11+ para ejecución en Kali Linux.
- **Entorno de ejecución**: máquina virtual Kali Linux sobre VirtualBox; macOS solo se usa para desarrollo y tests locales.
- **Entrega**: CLI modular, perfiles declarativos y adaptadores aislados.

## Specs

### S1 — Alcance autorizado y seguro

El orquestador debe exigir un alcance explícito antes de ejecutar herramientas
contra objetivos desplegados. Debe soportar allowlists de dominios, IPs y CIDR,
modo `--dry-run`, límites de velocidad, timeouts, cancelación y perfiles de
riesgo.

**Aceptación**: un objetivo fuera de la allowlist no se ejecuta; `--dry-run`
solo muestra el plan; los perfiles intrusivos requieren autorización explícita.

### S2 — Catálogo extensible de herramientas

Las herramientas deben registrarse mediante adaptadores declarativos con nombre,
binario, versión, categoría, perfil de riesgo, requisitos, argumentos permitidos,
formato de salida y parser de evidencias.

**Aceptación**: añadir una herramienta no requiere modificar el núcleo del
orquestador; una herramienta ausente produce estado `not-installed`, no un
fallo opaco.

### S3 — Cobertura inicial

El catálogo debe contemplar adaptadores para Nmap, Nuclei, OWASP ZAP, Burp Suite,
SQLMap, Gitleaks, TruffleHog y Trivy, además de familias extensibles para
reconocimiento, web/API, red, código, secretos, dependencias, cloud,
contenedores, Kubernetes, móvil, Active Directory, wireless, reversing y
forense.

**Aceptación**: cada adaptador declara si es pasivo, seguro, autenticado, activo
o de laboratorio; las herramientas ofensivas no se ejecutan por defecto.

### S4 — Ejecución reproducible

Cada ejecución debe conservar configuración, versión de herramienta, comando
redactado, timestamps, código de salida, stdout/stderr sanitizados, duración y
estado final.

**Aceptación**: una ejecución puede reanudarse o auditarse sin exponer secretos
ni depender de la memoria del operador.

### S5 — Evidencia normalizada

Los parsers deben convertir resultados heterogéneos a un modelo común con
hallazgo, severidad, confianza, categoría, objetivo, ubicación, evidencia,
referencia, herramienta y recomendación.

**Aceptación**: los informes no incluyen secretos completos, tokens, contraseñas
ni payloads innecesarios.

### S6 — Informes y formatos de salida

El orquestador debe generar Markdown, HTML, JSON y SARIF, con resumen ejecutivo,
inventario de herramientas, cobertura, hallazgos ordenados por riesgo, evidencia,
limitaciones, errores, riesgos aceptados y pendientes.

**Aceptación**: un informe distingue `verified`, `finding`, `not-verified`,
`not-applicable` y `tool-unavailable`.

### S7 — Perfiles operativos

Debe incluir perfiles mínimos `passive`, `safe-web`, `authenticated`, `code`,
`cloud`, `mobile`, `active`, `lab` y `full`, con confirmación previa para
perfiles activos o de laboratorio.

**Aceptación**: el perfil determina herramientas, permisos, límites y nivel de
interacción; no se permite elevar el perfil silenciosamente.

### S8 — Calidad y mantenimiento

El proyecto debe tener tests unitarios para políticas, allowlists, parsers,
redacción y generación de informes; tests de integración con ejecutables falsos;
documentación de instalación y un registro de herramientas soportadas.

**Aceptación**: los tests no atacan objetivos reales ni necesitan credenciales o
herramientas externas instaladas.

## Tasks

- [x] T1 — Explorar el entorno Kali esperado y fijar contratos CLI, configuración y salida.
- [x] T2 — Diseñar el modelo de catálogo, perfiles, alcance, ejecución y evidencia.
- [x] T3 — Implementar CLI, configuración validada y políticas de seguridad.
- [ ] T4 — Implementar runner aislado con timeouts, cancelación y redacción.
- [ ] T5 — Implementar catálogo y adaptadores de la primera cobertura.
- [ ] T6 — Implementar parsers, normalización y almacenamiento de evidencias.
- [ ] T7 — Implementar generadores Markdown, HTML, JSON y SARIF.
- [ ] T8 — Añadir tests unitarios, integración con mocks y documentación de uso.
- [ ] T9 — Ejecutar verificación completa y cerrar riesgos pendientes.

## Log

### L1 — Solicitud original

> dale

### L2 — Alcance acordado

- El repositorio se llama `kali-security-orchestrator`.
- Solo este repositorio usa ODD.
- El catálogo debe ser amplio y extensible, no un script monolítico.
- El uso debe ser autorizado y defensivo, con herramientas intrusivas aisladas
  en perfiles explícitos.

### L3 — Componentes iniciales solicitados

- Nmap.
- Nuclei.
- OWASP ZAP.
- Burp Suite.
- SQLMap.
- Gitleaks.
- TruffleHog.
- Trivy.
- Recolección de evidencias.
- Generación automática de informes.

### L4 — Exploración y decisión de runtime

- `python3 --version`: Python 3.14.5 disponible; compatible con el mínimo
  acordado de Python 3.11+.
- En el entorno macOS actual no están instalados `nmap`, `nuclei`, `zap.sh`,
  `burpsuite`, `sqlmap`, `gitleaks`, `trufflehog` ni `trivy`; el catálogo los
  reporta como `not-installed` sin intentar ejecutarlos.
- La ejecución real queda reservada para Kali o un entorno explícitamente
  autorizado; los tests usan únicamente stdlib y ejecutables simulados.

### L5 — Núcleo implementado

- `src/kali_orchestrator/policy.py`: allowlists de dominios/CIDR y autorización
  explícita para perfiles `active`, `lab` y `full`.
- `src/kali_orchestrator/catalog.py`: catálogo extensible con metadatos de
  categoría, riesgo, perfiles, binarios alternativos y disponibilidad.
- `tests/python/test_policy_and_catalog.py`: 6 tests unitarios; se observó RED
  antes de implementar (`ModuleNotFoundError`) y GREEN después.
- `npm test`: 6 tests Node y 6 tests Python pasaron.

### L6 — Entorno objetivo confirmado

- La ejecución real del catálogo y de los adaptadores ocurrirá en una máquina
  virtual Kali Linux administrada con VirtualBox.
- El entorno macOS no debe instalar ni ejecutar herramientas de pentesting; solo
  valida políticas, catálogo, parsers, informes y ejecutables simulados.
- La detección `installed` / `not-installed` es intencional para permitir el
  mismo código en desarrollo y en Kali, donde se instalarán las herramientas
  autorizadas.

### L7 — CLI de planificación

- `python3 -m kali_orchestrator doctor` informa disponibilidad sin ejecutar
  herramientas de auditoría.
- `python3 -m kali_orchestrator plan --config examples/audit.safe-web.json`
  valida el alcance, perfil y catálogo, y siempre devuelve `dry_run: true`.
- La CLI todavía no ejecuta comandos externos; esa capacidad pertenece a T4 y
  requiere runner, timeouts, cancelación y redacción.

### L8 — Guía de uso

- `docs/GUIA-USO-KALI.md` documenta instalación en VirtualBox, entorno Python,
  diagnóstico, planificación segura, perfiles, limitaciones y resolución de
  problemas.
