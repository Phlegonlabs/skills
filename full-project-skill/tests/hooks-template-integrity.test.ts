import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const ROOT = join(import.meta.dir, "..");
const HOOKS_TEMPLATES = [
  join(ROOT, "assets", "hooks", "settings.template.json"),
  join(ROOT, "assets", "hooks", "settings.template.codex.json"),
];

describe("Hooks template integrity", () => {
  test("hooks templates should reference platform hooks scripts", () => {
    for (const templatePath of HOOKS_TEMPLATES) {
      const raw = readFileSync(templatePath, "utf-8");
      const refs = [...raw.matchAll(/\.(?:claude|codex)\/hooks\/([A-Za-z0-9._-]+\.sh)/g)].map(
        (match) => match[1]
      );
      expect(refs.length).toBeGreaterThan(0);
    }
  });

  test("hooks templates should not duplicate script references", () => {
    for (const templatePath of HOOKS_TEMPLATES) {
      const raw = readFileSync(templatePath, "utf-8");
      const refs = [...raw.matchAll(/\.(?:claude|codex)\/hooks\/([A-Za-z0-9._-]+\.sh)/g)].map(
        (match) => match[1]
      );
      expect(new Set(refs).size).toBe(refs.length);
    }
  });
});
