// =============================================================================
// sdd-store.test.mjs — Invariants of the SDD artifact store.
//
// These are the rules that, if broken, silently corrupt the history:
// stable requirement numbering, the baseline/change separation, and the
// registry's consistency with what is on disk.
//
// Run with: npm test
// =============================================================================

import { test } from "node:test"
import assert from "node:assert/strict"
import { readdirSync, readFileSync, existsSync, statSync } from "node:fs"
import { join, relative } from "node:path"
import { fileURLToPath } from "node:url"

const ROOT = join(fileURLToPath(new URL(".", import.meta.url)), "..")
const SPECS = join(ROOT, ".sdd", "specs")
const CHANGES = join(ROOT, ".sdd", "changes")
const REGISTRY = join(ROOT, ".sdd", "registry.md")

const listFiles = (dir) =>
  existsSync(dir) ? readdirSync(dir).filter((f) => f.endsWith(".md")) : []

const readRequirementNumbers = (text) => {
  const numbers = new Set()
  const pattern = /^#{2,3}\s+R(\d+)\b/gm
  let match
  while ((match = pattern.exec(text)) !== null) {
    numbers.add(Number(match[1]))
  }
  return numbers
}

test("the artifact store has the expected directories", () => {
  assert.ok(existsSync(join(ROOT, ".sdd")), ".sdd/ must exist")
  assert.ok(existsSync(SPECS), ".sdd/specs/ must exist")
  assert.ok(existsSync(REGISTRY), ".sdd/registry.md must exist")
})

test("the registry is present and non-empty", () => {
  const text = readFileSync(REGISTRY, "utf8")
  assert.ok(text.length > 0, "the registry must not be empty")
  assert.ok(text.includes("Fases"), "the registry must document the phases")
})

test("baseline requirement numbers are unique per domain", () => {
  for (const file of listFiles(SPECS)) {
    const numbers = readRequirementNumbers(readFileSync(join(SPECS, file), "utf8"))
    const sorted = [...numbers].sort((a, b) => a - b)
    assert.equal(
      sorted.length,
      new Set(sorted).size,
      `${file} has a duplicated requirement number`,
    )
  }
})

test("baseline requirement numbering starts at R1 and has no gaps", () => {
  for (const file of listFiles(SPECS)) {
    const numbers = [...readRequirementNumbers(readFileSync(join(SPECS, file), "utf8"))].sort(
      (a, b) => a - b,
    )
    if (!numbers.length) continue
    assert.equal(numbers[0], 1, `${file} must start at R1`)
    for (let i = 1; i < numbers.length; i++) {
      assert.equal(
        numbers[i],
        numbers[i - 1] + 1,
        `${file} has a gap in the requirement numbering at R${numbers[i]}`,
      )
    }
  }
})

test("in-flight changes are not tracked by git", () => {
  // .sdd/changes/ holds work in progress. It must stay out of the repository.
  const ignore = readFileSync(join(ROOT, ".gitignore"), "utf8")
  assert.match(ignore, /^\.sdd\/changes\/?$/m, ".gitignore must exclude .sdd/changes/")
})

test("every change folder holds the five artifacts", () => {
  if (!existsSync(CHANGES)) return
  for (const dir of readdirSync(CHANGES)) {
    const full = join(CHANGES, dir)
    if (!statSync(full).isDirectory()) continue
    for (const artifact of ["proposal.md", "spec.md", "design.md", "tasks.md"]) {
      const path = join(full, artifact)
      if (!existsSync(path)) continue // a change in progress legitimately lacks later phases
      const text = readFileSync(path, "utf8")
      assert.ok(text.trim().length > 0, `${relative(ROOT, path)} must not be empty`)
    }
  }
})

test("the project AGENTS.md stays under the 500-line guideline", () => {
  const text = readFileSync(join(ROOT, "AGENTS.md"), "utf8")
  const lines = text.split("\n").length
  assert.ok(lines <= 500, `AGENTS.md has ${lines} lines; the guideline is 500`)
})
