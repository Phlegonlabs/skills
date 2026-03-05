import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const ROOT = join(import.meta.dir, "..");
const HOOKS_TEMPLATE = join(ROOT, "assets", "hooks", "settings.template.json");

describe("Hooks template integrity", () => {
  test("hooks template should reference at least one .claude/hooks/*.sh script", () => {
    const raw = readFileSync(HOOKS_TEMPLATE, "utf-8");
    const refs = [...raw.matchAll(/\.claude\/hooks\/([A-Za-z0-9._-]+\.sh)/g)].map(
      (match) => match[1]
    );

    expect(refs.length).toBeGreaterThan(0);
  });

  test("hooks template should not duplicate script references", () => {
    const raw = readFileSync(HOOKS_TEMPLATE, "utf-8");
    const refs = [...raw.matchAll(/\.claude\/hooks\/([A-Za-z0-9._-]+\.sh)/g)].map(
      (match) => match[1]
    );

    expect(new Set(refs).size).toBe(refs.length);
  });
});
