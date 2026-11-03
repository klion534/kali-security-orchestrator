# Guía de uso en Kali Linux sobre VirtualBox

## Estado actual

La versión actual permite:

- Validar un plan de auditoría.
- Comprobar el alcance autorizado.
- Clasificar el perfil de ejecución.
- Detectar herramientas instaladas.
- Generar un plan en modo `dry_run`.
- Ejecutar adaptadores iniciales mediante un runner aislado, con autorización
  explícita, timeout y redacción.

Los adaptadores iniciales cubren Nmap, Nuclei, OWASP ZAP, SQLMap, Gitleaks,
TruffleHog y Trivy. Burp Suite queda como integración manual/API. Deben
validarse en Kali antes de considerarlos aptos para una auditoría real.

## 1. Preparar la máquina virtual

La ejecución real está pensada para una VM Kali Linux administrada con
VirtualBox. macOS se utiliza únicamente para desarrollo y tests.

### Carpeta compartida de VirtualBox

1. Apagá la VM.
2. En VirtualBox, abrí **Configuración → Carpetas compartidas**.
3. Agregá la carpeta del proyecto del Mac.
4. Activá **Automontar** y **Hacer permanente**.
5. Iniciá Kali.

Si Kali no permite leer la carpeta compartida:

```bash
sudo usermod -aG vboxsf "$USER"
```

Cerrá la sesión gráfica y volvé a entrar para que el grupo tenga efecto.

La carpeta normalmente aparecerá como:

```text
/media/sf_<nombre-de-la-carpeta>
```

Copiá el proyecto al directorio personal de Kali. Trabajar sobre una copia
local de la VM evita problemas de permisos y rendimiento:

```bash
cp -r /media/sf_kali-security-orchestrator ~/kali-security-orchestrator
cd ~/kali-security-orchestrator
```

## 2. Instalar dependencias base

```bash
sudo apt update
sudo apt install -y git python3 python3-venv nodejs npm
```

Crear el entorno Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
```

Verificar versiones:

```bash
python3 --version
node --version
npm --version
```

El proyecto requiere Python 3.11 o superior. Las herramientas de Kali se
instalan y mantienen dentro de la VM, no en macOS.

## 3. Verificar el proyecto

```bash
npm install
npm test
npm run lint
npm run build
./scripts/verify-stack.sh
```

No continúes si los tests fallan. Un resultado esperado actualmente es:

```text
6 tests Node + 9 tests Python: OK
lint: ... no problems found
Stack completo y sano.
```

## 4. Diagnosticar herramientas

```bash
PYTHONPATH=src python3 -m kali_orchestrator doctor
```

El comando devuelve JSON con cada herramienta, su categoría, riesgo,
ejecutable detectado y estado:

- `installed`: el binario está disponible en `PATH`.
- `not-installed`: el catálogo lo conoce, pero no está instalado.

El diagnóstico no ejecuta auditorías ni realiza conexiones contra objetivos.

## 5. Crear un plan seguro

Copiá el ejemplo:

```bash
cp examples/audit.safe-web.json /tmp/my-audit.json
```

Editá únicamente objetivos propios o autorizados:

```json
{
  "scope": {
    "domains": ["app.example.com"],
    "networks": []
  },
  "profile": "safe-web",
  "authorized": false,
  "targets": ["https://app.example.com"],
  "tools": ["nmap", "nuclei", "owasp-zap"],
  "output_dir": "artifacts"
}
```

Validá el plan:

```bash
PYTHONPATH=src python3 -m kali_orchestrator plan \
  --config /tmp/my-audit.json
```

La salida debe incluir:

```json
{
  "dry_run": true,
  "profile": "safe-web",
  "targets": ["https://app.example.com"]
}
```

La CLI actual rechaza:

- Objetivos fuera de la allowlist.
- Dominios o redes no definidos.
- Herramientas desconocidas.
- Perfiles inexistentes.
- Perfiles `active`, `lab` o `full` sin `authorized: true`.
- Configuraciones con `dry_run: false`.

## 6. Perfiles

| Perfil | Uso | Estado actual |
|--------|-----|---------------|
| `passive` | Reconocimiento pasivo | Planificación |
| `safe-web` | Revisión web controlada | Planificación |
| `authenticated` | Auditoría con acceso autorizado | Planificación |
| `code` | Código, secretos y dependencias | Planificación |
| `cloud` | Cloud y Kubernetes | Planificación |
| `mobile` | Aplicaciones móviles | Planificación |
| `active` | Pruebas activas | Requiere autorización explícita |
| `lab` | Herramientas de laboratorio | Requiere autorización explícita |
| `full` | Cobertura combinada | Requiere autorización explícita |

## 7. Runner experimental

El runner de T4 ya aplica autorización, `shell=False`, timeout, cancelación y
redacción. La ejecución real requiere una configuración con:

```json
{
  "profile": "safe-web",
  "authorized": true,
  "dry_run": false
}
```

La invocación exige confirmación explícita:

```bash
PYTHONPATH=src python3 -m kali_orchestrator run \
  --config /ruta/al/plan-autorizado.json \
  --tool nmap \
  --target https://app.example.com \
  --execute
```

Usalo únicamente en Kali, con un objetivo autorizado. El runner no ejecuta
mediante shell y no inventa argumentos; el adaptador construye los argumentos
base y `--arg` permite añadir argumentos explícitos.

## 8. Reglas de seguridad

- Trabajá únicamente sobre sistemas propios o autorizados.
- No uses producción para las primeras pruebas.
- No agregues credenciales al JSON, al repositorio ni a los logs.
- No ejecutes fuerza bruta, explotación, persistencia o pruebas de carga sin
  una autorización específica y un entorno controlado.
- El estado `not-installed` no significa que una herramienta sea segura ni que
  el objetivo esté auditado; solo indica que el binario no fue encontrado.
- La página de éxito de un pago nunca debe tratarse como evidencia de pago.

## 9. Problemas frecuentes

### `ModuleNotFoundError: kali_orchestrator`

Desde la raíz del repositorio:

```bash
export PYTHONPATH="$PWD/src"
```

### La carpeta compartida no aparece

Verificá el nombre configurado en VirtualBox y que el usuario pertenezca a
`vboxsf`:

```bash
groups
sudo usermod -aG vboxsf "$USER"
```

Después cerrá la sesión de Kali y volvé a entrar.

### Una herramienta aparece como `not-installed`

Es un diagnóstico, no un error del orquestador. Instalá la herramienta dentro
de Kali siguiendo su documentación oficial y ejecutá nuevamente `doctor`.

## Estado pendiente

El núcleo del runner, los adaptadores iniciales, la normalización de evidencias
y los informes ya están implementados. Falta validar los binarios y sus formatos
de salida dentro de Kali Linux en VirtualBox; esa verificación no se realiza en
macOS ni contra objetivos reales desde los tests.
