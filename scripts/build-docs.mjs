#!/usr/bin/env node
// =============================================================================
// build-docs.mjs — The `build` gate.
//
// The project's build artifact is its documentation index: a generated table of
// contents that can never drift from the files on disk, because it is derived
// from them.
//
// Usage: node scripts/build-docs.mjs
// =============================================================================

import { readdirSync, readFileSync, writeFileSync, statSync } from "node:fs"
import { join, relative, basename } from "node:path"
import { fileURLToPath } from "node:url"

const ROOT = join(fileURLToPath(new URL(".", import.meta.url)), "..")
const DOCS = join(ROOT, "docs")
const OUTPUT = join(DOCS, "INDEX.md")

function titleOf(file) {
  const text = readFileSync(file, "utf8")
  const match = text.match(/^#\s+(.+)$/m)
  if (match) return match[1].trim()
  return basename(file, ".md")
}

function descriptionOf(file) {
  const text = readFileSync(file, "utf8")
  const lines = text.split("\n")

  // Prefer the epigraph: the first blockquote under the H1.
  for (const line of lines) {
    const trimmed = line.trim()
    if (trimmed.startsWith("# ")) continue
    if (trimmed === "") continue
    if (trimmed.startsWith(">")) {
      const quote = trimmed.replace(/^>\s*/, "").trim()
      if (quote && !quote.startsWith("|") && !quote.startsWith("-")) {
        return quote.length > 140 ? quote.slice(0, 137).trimEnd() + "..." : quote
      }
    }
    break
  }

  // Fallback: the first prose line that is not a heading, table, code or rule.
  let started = false
  for (const line of lines) {
    const trimmed = line.trim()
    if (!started) {
      if (trimmed.startsWith("# ")) started = true
      continue
    }
    if (trimmed === "") continue
    if (
      trimmed.startsWith("#") ||
      trimmed.startsWith("|") ||
      trimmed.startsWith("```") ||
      trimmed.startsWith("- ") ||
      /^[┌└├│─]/.test(trimmed) ||
      trimmed === "---"
    ) {
      continue
    }
    return trimmed.length > 140 ? trimmed.slice(0, 137).trimEnd() + "..." : trimmed
  }

  return ""
}

if (!statSync(DOCS).isDirectory()) {
  console.error("build: the docs/ directory is missing")
  process.exit(1)
}

const files = readdirSync(DOCS)
  .filter((f) => f.endsWith(".md") && f !== "INDEX.md")
  .sort()

const rows = files.map((file) => {
  const path = join(DOCS, file)
  // The link is relative to the generated index, which lives in docs/.
  const href = relative(DOCS, path)
  return `| [${titleOf(path)}](${href}) | ${descriptionOf(path)} |`
})

const content = `# Índice de documentación

> Generado por \`npm run build\`. No editar a mano: se regenera desde los
> ficheros de \`docs/\`, así que no puede quedar desactualizado.

| Documento | Qué cubre |
|-----------|-----------|
${rows.join("\n")}
`

writeFileSync(OUTPUT, content, "utf8")
console.log(`build: wrote ${relative(ROOT, OUTPUT)} with ${files.length} document(s)`)
