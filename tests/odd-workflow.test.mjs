// odd-workflow.test.mjs — Invariants of the ODD feature-document store.

import { test } from "node:test"
import assert from "node:assert/strict"
import { readdirSync, readFileSync, existsSync } from "node:fs"
import { join } from "node:path"
import { fileURLToPath } from "node:url"

const ROOT = join(fileURLToPath(new URL(".", import.meta.url)), "..")
const ODD = join(ROOT, "odd")
const TASKS = join(ODD, "tasks")

const listFiles = (dir) =>
  existsSync(dir) ? readdirSync(dir).filter((file) => file.endsWith(".md")) : []

test("the ODD store has the expected directories", () => {
  assert.ok(existsSync(ODD), "odd/ must exist")
  assert.ok(existsSync(TASKS), "odd/tasks/ must exist")
})

test("the ODD contract is present", () => {
  const text = readFileSync(join(ODD, "README.md"), "utf8")
  assert.match(text, /Organic Driven Development/, "ODD README must identify the workflow")
  assert.match(text, /odd\/tasks\/<feature-name>\.md/, "ODD README must document feature files")
})

test("ODD feature documents contain the required sections", () => {
  for (const file of listFiles(TASKS)) {
    const text = readFileSync(join(TASKS, file), "utf8")
    assert.match(text, /^## Specs$/m, `${file} must contain Specs`)
    assert.match(text, /^## Tasks$/m, `${file} must contain Tasks`)
    assert.match(text, /^## Log$/m, `${file} must contain Log`)
  }
})

test("ODD specification numbering starts at S1 and has no gaps", () => {
  for (const file of listFiles(TASKS)) {
    const text = readFileSync(join(TASKS, file), "utf8")
    const numbers = [...text.matchAll(/^### S(\d+)\b/gm)]
      .map((match) => Number(match[1]))
      .sort((a, b) => a - b)

    if (!numbers.length) continue
    assert.equal(numbers[0], 1, `${file} must start at S1`)
    assert.equal(new Set(numbers).size, numbers.length, `${file} has duplicate specification numbers`)
    for (let i = 1; i < numbers.length; i++) {
      assert.equal(numbers[i], numbers[i - 1] + 1, `${file} has a specification gap at S${numbers[i]}`)
    }
  }
})

test("AGENTS.md stays under the 500-line guideline", () => {
  const text = readFileSync(join(ROOT, "AGENTS.md"), "utf8")
  assert.ok(text.split("\n").length <= 500, "AGENTS.md must stay under 500 lines")
})

test("operational files do not route new work through SDD", () => {
  const files = [
    "AGENTS.md",
    "README.md",
    "docs/OPERATIVO.md",
    "docs/CATALOGO.md",
    "docs/ARQUITECTURA-STACK.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
  ]
  const legacyRoute = /(?:\/sdd(?:-|\b)|sdd-workflow|Pipeline SDD|\.sdd\/changes)/i

  for (const file of files) {
    const text = readFileSync(join(ROOT, file), "utf8")
    assert.doesNotMatch(text, legacyRoute, `${file} must not route new work through SDD`)
  }
})
