import { describe, expect, test } from "bun:test";
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

const ROOT = join(import.meta.dir, "..");
const PARTIALS_DIR = join(ROOT, "references", "partials");
const PARTIALS_AGENTS_DIR = join(ROOT, "references", "partials-agents");

describe("Partial template contracts", () => {
  test("claude partials should contain required files", () => {
    expect(existsSync(PARTIALS_DIR)).toBe(true);
    const files = new Set(readdirSync(PARTIALS_DIR));
    const required = [
      "_assembly-order.md",
      "01-header.partial.md",
      "02-execution-protocol.partial.md",
      "03-key-docs.partial.md",
      "04-tech-stack.partial.md",
      "05-commands.partial.md",
      "06-structure.partial.md",
      "07-conventions.partial.md",
      "08-ai-behavior.partial.md",
      "09-status-contract.partial.md",
      "10-footer.partial.md",
    ];

    for (const file of required) {
      expect(files.has(file)).toBe(true);
    }
  });

  test("agents partials should contain required files", () => {
    expect(existsSync(PARTIALS_AGENTS_DIR)).toBe(true);
    const files = new Set(readdirSync(PARTIALS_AGENTS_DIR));
    const required = [
      "_assembly-order.md",
      "01-header.partial.md",
      "02-operating-mode.partial.md",
      "03-key-docs.partial.md",
      "04-tech-stack.partial.md",
      "05-commands.partial.md",
      "06-orchestration.partial.md",
      "07-task-protocol.partial.md",
      "08-coding-constraints.partial.md",
    ];

    for (const file of required) {
      expect(files.has(file)).toBe(true);
    }
  });
});
