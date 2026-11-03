#!/usr/bin/env node
// =============================================================================
// validate-config.mjs — The `lint` gate.
//
// Validates every machine-readable file in the repository so a malformed
// config never reaches main. Zero dependencies: it uses Node's built-ins and
// a small structural YAML check.
//
// Usage: node scripts/validate-config.mjs
// =============================================================================

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs"
import { join, extname, relative, basename } from "node:path"
import { execFileSync } from "node:child_process"
import { fileURLToPath } from "node:url"
import YAML from "yaml"

const ROOT = join(fileURLToPath(new URL(".", import.meta.url)), "..")
const errors = []
const checked = { json: 0, yaml: 0, jsonc: 0, shell: 0, frontmatter: 0 }

const fail = (file, message) => errors.push(`${file}: ${message}`)

// --- Directory walk ---------------------------------------------------------

const SKIP_DIRS = new Set([
  "node_modules",
  ".git",
  ".worktrees",
  "dist",
  "build",
  "coverage",
  ".atl",
])

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    if (SKIP_DIRS.has(entry)) continue
    const full = join(dir, entry)
    const st = statSync(full)
    if (st.isDirectory()) walk(full, out)
    else out.push(full)
  }
  return out
}

// --- JSON / JSONC ------------------------------------------------------------

function stripJsonComments(text) {
  // Remove // and /* */ comments outside of strings.
  let result = ""
  let inString = false
  let inLine = false
  let inBlock = false
  for (let i = 0; i < text.length; i++) {
    const c = text[i]
    const next = text[i + 1]
    if (inLine) {
      if (c === "\n") {
        inLine = false
        result += c
      }
      continue
    }
    if (inBlock) {
      if (c === "*" && next === "/") {
        inBlock = false
        i++
      }
      continue
    }
    if (inString) {
      result += c
      if (c === "\\") {
        result += next ?? ""
        i++
      } else if (c === '"') {
        inString = false
      }
      continue
    }
    if (c === '"') {
      inString = true
      result += c
      continue
    }
    if (c === "/" && next === "/") {
      inLine = true
      i++
      continue
    }
    if (c === "/" && next === "*") {
      inBlock = true
      i++
      continue
    }
    result += c
  }
  return result
}

function validateJson(file, text, allowComments) {
  try {
    JSON.parse(allowComments ? stripJsonComments(text) : text)
    return true
  } catch (error) {
    fail(file, `invalid JSON: ${error.message}`)
    return false
  }
}

// --- YAML --------------------------------------------------------------------

function validateYaml(file, text) {
  try {
    const doc = YAML.parseDocument(text, { uniqueKeys: true, prettyErrors: true })

    if (doc.errors.length) {
      for (const error of doc.errors) {
        fail(file, `invalid YAML: ${error.message}`)
      }
      return false
    }
    if (doc.warnings.length) {
      for (const warning of doc.warnings) {
        fail(file, `YAML warning: ${warning.message}`)
      }
      return false
    }

    const value = doc.toJS()
    if (value === null || typeof value !== "object" || Array.isArray(value)) {
      fail(file, "the YAML root must be a mapping")
      return false
    }
    return true
  } catch (error) {
    fail(file, `invalid YAML: ${error.message}`)
    return false
  }
}

// --- Frontmatter -------------------------------------------------------------

function validateFrontmatter(file, text) {
  if (!text.startsWith("---")) {
    fail(file, "missing YAML frontmatter")
    return
  }
  const end = text.indexOf("\n---", 3)
  if (end < 0) {
    fail(file, "unterminated frontmatter")
    return
  }
  const block = text.slice(3, end)
  if (!/^name:\s*\S+/m.test(block)) fail(file, "frontmatter is missing 'name'")
  if (!/^description:\s*\S+/m.test(block)) fail(file, "frontmatter is missing 'description'")
}

// --- Run ---------------------------------------------------------------------

const files = walk(ROOT)

for (const file of files) {
  const rel = relative(ROOT, file)
  const ext = extname(file)

  if (ext === ".json") {
    checked.json++
    validateJson(rel, readFileSync(file, "utf8"), false)
  } else if (ext === ".jsonc") {
    checked.jsonc++
    validateJson(rel, readFileSync(file, "utf8"), true)
  } else if (ext === ".yml" || ext === ".yaml") {
    checked.yaml++
    validateYaml(rel, readFileSync(file, "utf8"))
  } else if (ext === ".sh" || basename(file) === "verify-stack.sh") {
    checked.shell++
    try {
      execFileSync("bash", ["-n", file], { stdio: "pipe" })
    } catch (error) {
      fail(rel, `shell syntax error: ${String(error.stderr ?? error.message).trim()}`)
    }
  } else if (basename(file) === "SKILL.md") {
    checked.frontmatter++
    validateFrontmatter(rel, readFileSync(file, "utf8"))
  }
}

// --- Required files ----------------------------------------------------------

const REQUIRED = [
  "package.json",
  ".env.example",
  ".gitignore",
  "AGENTS.md",
  "odd/README.md",
  "odd/tasks",
  ".github/workflows/ci.yml",
  ".github/workflows/security-review.yml",
  ".github/workflows/release-please.yml",
  ".github/PULL_REQUEST_TEMPLATE.md",
  "release-please-config.json",
  ".release-please-manifest.json",
]

for (const file of REQUIRED) {
  if (!existsSync(join(ROOT, file))) fail(file, "required file is missing")
}

// --- Secret hygiene ----------------------------------------------------------

const SECRET_PATTERNS = [
  /sk-[A-Za-z0-9]{20,}/,
  /ghp_[A-Za-z0-9]{30,}/,
  /AKIA[0-9A-Z]{16}/,
  /-----BEGIN [A-Z ]*PRIVATE KEY-----/,
]

for (const file of files) {
  const rel = relative(ROOT, file)
  if (rel === ".env" || rel.startsWith(".env.")) {
    if (rel !== ".env.example") fail(rel, "an environment file is tracked")
    continue
  }
  if (/\.(md|example)$/.test(rel)) continue
  const text = readFileSync(file, "utf8")
  for (const pattern of SECRET_PATTERNS) {
    if (pattern.test(text)) {
      fail(rel, `matches the credential pattern ${pattern}`)
    }
  }
}

// --- Report ------------------------------------------------------------------

const total = Object.values(checked).reduce((a, b) => a + b, 0)

if (errors.length) {
  console.error(`lint: ${errors.length} problem(s) found\n`)
  for (const error of errors) console.error(`  ${error}`)
  process.exit(1)
}

console.log(`lint: ${total} files checked (${checked.json} json, ${checked.jsonc} jsonc, ${checked.yaml} yaml, ${checked.shell} shell, ${checked.frontmatter} frontmatter) — no problems found`)
