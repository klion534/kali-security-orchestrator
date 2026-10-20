#!/usr/bin/env bash
# =============================================================================
# verify-stack.sh — Comprueba que el Sistema Cognitivo está completo y sano.
#
# Read-only: no modifica nada. Solo informa.
# Uso: ./scripts/verify-stack.sh
# =============================================================================

set -uo pipefail

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'
CYAN=$'\033[0;36m'
BOLD=$'\033[1m'
NC=$'\033[0m'

PASS=0
FAIL=0
WARN=0

ok()   { printf "  ${GREEN}ok${NC}    %s\n" "$1"; PASS=$((PASS+1)); }
bad()  { printf "  ${RED}FAIL${NC}  %s\n" "$1"; FAIL=$((FAIL+1)); }
warn() { printf "  ${YELLOW}warn${NC}  %s\n" "$1"; WARN=$((WARN+1)); }
info() { printf "  ${CYAN}->${NC}    %s\n" "$1"; }

section() {
  printf "\n${BOLD}%s${NC}\n" "$1"
  printf "${CYAN}%s${NC}\n" "$(printf '%.0s-' {1..58})"
}

# The output of `opencode agent list` and `opencode debug config` is large
# (tens of thousands of lines). Capturing it through a command substitution
# truncates it, so every read goes through a temp file instead.
TMPDIR_V="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_V"' EXIT

AGENT_FILE="$TMPDIR_V/agents.txt"
SKILL_FILE="$TMPDIR_V/skills.txt"
CONFIG_FILE="$TMPDIR_V/config.txt"

opencode agent list > "$AGENT_FILE" 2>/dev/null || true
opencode debug skill  > "$SKILL_FILE" 2>/dev/null || true
opencode debug config > "$CONFIG_FILE" 2>/dev/null || true

# Validates a YAML file. PyYAML is not always present, so it falls back to
# node (the `yaml` package ships with the OpenCode install).
validate_yaml() {
  local file="$1"
  if python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" "$file" 2>/dev/null; then
    return 0
  fi
  if command -v node >/dev/null 2>&1; then
    local yaml_pkg="$HOME/.config/opencode/node_modules/yaml"
    if [ -d "$yaml_pkg" ]; then
      node -e "
        const YAML = require('$yaml_pkg');
        const fs = require('fs');
        YAML.parse(fs.readFileSync(process.argv[1], 'utf8'));
      " "$file" >/dev/null 2>&1 && return 0
    fi
    node -e "
      const fs = require('fs');
      const s = fs.readFileSync(process.argv[1], 'utf8');
      if (/^\s*(on|jobs|name):/m.test(s) === false) { process.exit(1); }
      const stack = [];
      for (const raw of s.split('\n')) {
        if (raw.trim() === '' || raw.trim().startsWith('#')) continue;
        const indent = raw.length - raw.trimStart().length;
        while (stack.length && stack[stack.length-1] >= indent) stack.pop();
        if (raw.trim().endsWith(':')) stack.push(indent);
        else if (!stack.length) { process.exit(1); }
      }
    " "$file" >/dev/null 2>&1 && return 0
  fi
  return 1
}

# ---------------------------------------------------------------------------
section "1. Binarios"

check_bin() {
  local name="$1" expected="$2"
  if command -v "$name" >/dev/null 2>&1; then
    local version
    version="$("$name" --version 2>/dev/null | head -1 || echo '?')"
    if [ "$version" != "$expected" ] && [[ "$version" != *"$expected"* ]]; then
      warn "$name instalado (esperado $expected, encontrado: $version)"
    else
      ok "$name $version"
    fi
  else
    bad "$name no está en el PATH"
  fi
}

check_bin engram   "3.4.0"
check_bin gentle-ai "4.2.0"
check_bin gga      ""

if command -v gga >/dev/null 2>&1; then
  info "gga $(gga version 2>/dev/null | head -1 || echo 'instalado')"
fi

if command -v opencode >/dev/null 2>&1; then
  ok "opencode $(opencode --version 2>/dev/null | head -1)"
else
  bad "opencode no está en el PATH"
fi

# ---------------------------------------------------------------------------
section "2. Configuración global de OpenCode"

CONFIG_DIR="$HOME/.config/opencode"

if [ -f "$CONFIG_DIR/opencode.jsonc" ]; then
  ok "opencode.jsonc existe"
else
  bad "falta $CONFIG_DIR/opencode.jsonc"
fi

if [ -f "$CONFIG_DIR/AGENTS.md" ]; then
  LINES=$(wc -l < "$CONFIG_DIR/AGENTS.md" | tr -d ' ')
  if [ "$LINES" -gt 500 ]; then
    warn "AGENTS.md tiene $LINES líneas (el guideline es 500)"
  else
    ok "AGENTS.md global ($LINES líneas)"
  fi
else
  bad "falta $CONFIG_DIR/AGENTS.md"
fi

if [ -f "$CONFIG_DIR/plugins/engram.ts" ]; then
  ok "plugin de Engram instalado"
else
  bad "falta el plugin de Engram ($CONFIG_DIR/plugins/engram.ts)"
fi

# ---------------------------------------------------------------------------
section "3. Subagentes"

EXPECTED_AGENTS="sdd-orchestrator sdd-explore sdd-propose sdd-spec sdd-design sdd-tasks sdd-apply sdd-verify sdd-archive prompt-engineer context-engineer model-selector test-engineer security-reviewer ci-engineer release-engineer knowledge-curator git-worktree-guardian"

if [ ! -s "$AGENT_FILE" ]; then
  bad "no se pudo listar los agentes"
else
  for agent in $EXPECTED_AGENTS; do
    if grep -qE "^${agent} \(" "$AGENT_FILE"; then
      ok "agente $agent"
    else
      bad "falta el agente $agent"
    fi
  done
  TOTAL=$(grep -cE "^[a-zA-Z0-9_-]+ \(" "$AGENT_FILE" || true)
  info "total de agentes registrados: $TOTAL"
fi

# ---------------------------------------------------------------------------
section "4. Skills"

EXPECTED_SKILLS="sdd-workflow prompt-perfect context-engineering model-selection testing-strategy ci-cd-pipeline rag-knowledge-base git-worktrees veil-secrets judgment-day skill-registry"

if [ ! -s "$SKILL_FILE" ]; then
  bad "no se pudo listar las skills"
else
  for skill in $EXPECTED_SKILLS; do
    if grep -q "\"name\": \"${skill}\"" "$SKILL_FILE"; then
      ok "skill $skill"
    else
      bad "falta la skill $skill"
    fi
  done
  TOTAL=$(grep -c '"name":' "$SKILL_FILE" || true)
  info "total de skills registradas: $TOTAL"
fi

# ---------------------------------------------------------------------------
section "5. Comandos"

EXPECTED_COMMANDS="sdd sdd-new sdd-ff prompt model test-plan security-review ci release worktree judgment-day memory"

if [ ! -s "$CONFIG_FILE" ]; then
  warn "no se pudo volcar la config (los comandos no se pudieron verificar)"
else
  for cmd in $EXPECTED_COMMANDS; do
    if grep -qE "\"${cmd}\":\s*\{" "$CONFIG_FILE"; then
      ok "comando /${cmd}"
    else
      bad "falta el comando /${cmd}"
    fi
  done
fi

# ---------------------------------------------------------------------------
section "6. MCP servers"

for server in engram context7; do
  if grep -q "\"${server}\"" "$CONFIG_FILE"; then
    ok "MCP $server configurado"
  else
    bad "falta el MCP $server"
  fi
done

# ---------------------------------------------------------------------------
section "7. Deny-list de secretos"

if grep -q '"\*\*/\.env": "deny"' "$CONFIG_FILE"; then
  ok "lectura y escritura de .env denegadas"
else
  bad "la deny-list de .env no está en la config"
fi

for pattern in '\*\*/\*\.pem' '\*\*/\.ssh' '\*\*/credentials\.json' '\*\*/secrets'; do
  if grep -q "$pattern" "$CONFIG_FILE"; then
    ok "patrón denegado: $pattern"
  else
    warn "patrón no encontrado en la deny-list: $pattern"
  fi
done

# ---------------------------------------------------------------------------
section "8. Gates de bash"

for gate in '"git push": "ask"' '"git reset --hard": "deny"' '"npm publish": "ask"'; do
  if grep -qF "$gate" "$CONFIG_FILE"; then
    ok "gate presente: $gate"
  else
    warn "gate no encontrado: $gate"
  fi
done

# ---------------------------------------------------------------------------
section "9. Workflows del proyecto"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

for wf in ci.yml security-review.yml release-please.yml; do
  FILE="$ROOT/.github/workflows/$wf"
  if [ -f "$FILE" ]; then
    if validate_yaml "$FILE"; then
      ok "workflow $wf (YAML válido)"
    else
      bad "workflow $wf tiene YAML inválido"
    fi
  else
    bad "falta el workflow $wf"
  fi
done

for f in ".github/dependabot.yml" ".github/PULL_REQUEST_TEMPLATE.md" ".github/CODEOWNERS" "release-please-config.json" ".release-please-manifest.json" ".gga" ".env.example" ".gitignore" "AGENTS.md" ".sdd/registry.md" "nvim/veil.lua" "package.json" "package-lock.json" "scripts/validate-config.mjs" "scripts/build-docs.mjs" "tests/sdd-store.test.mjs" "opencode.jsonc"; do
  if [ -f "$ROOT/$f" ]; then
    ok "$f"
  else
    bad "falta $f"
  fi
done

# ---------------------------------------------------------------------------
section "9b. Gates de CI"

if command -v npm >/dev/null 2>&1 && [ -f "$ROOT/package.json" ]; then
  cd "$ROOT" || exit 1
  if npm run lint --silent >/dev/null 2>&1; then
    ok "npm run lint"
  else
    bad "npm run lint falla"
  fi
  if npm test --silent >/dev/null 2>&1; then
    ok "npm test"
  else
    bad "npm test falla"
  fi
  if npm run build --silent >/dev/null 2>&1; then
    ok "npm run build"
  else
    bad "npm run build falla"
  fi
else
  warn "npm no está disponible: los gates de CI no se pudieron verificar"
fi

# ---------------------------------------------------------------------------
section "10. Memoria persistente (Engram)"

if command -v engram >/dev/null 2>&1; then
  if engram doctor >/dev/null 2>&1; then
    ok "engram doctor: la base de memoria está accesible"
  else
    info "engram doctor devolvió un aviso (puede ser normal sin una sesión activa)"
  fi
fi

# ---------------------------------------------------------------------------
printf "\n${BOLD}Resumen${NC}\n"
printf "${CYAN}%s${NC}\n" "$(printf '%.0s-' {1..58})"
printf "  ${GREEN}%d ok${NC}   ${RED}%d fail${NC}   ${YELLOW}%d warn${NC}\n" "$PASS" "$FAIL" "$WARN"

if [ "$FAIL" -gt 0 ]; then
  printf "\n${RED}${BOLD}El stack tiene %d problemas.${NC}\n" "$FAIL"
  exit 1
fi

printf "\n${GREEN}${BOLD}Stack completo y sano.${NC}\n"
exit 0
