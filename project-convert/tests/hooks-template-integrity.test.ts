import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "bun:test";
import { ROOT_DIR, validateHookScriptsExist } from "../scripts/skill-contract";

describe("Hook template integrity", () => {
  test("settings templates should reference existing hook scripts", () => {
    const errors = validateHookScriptsExist();
    expect(errors).toEqual([]);
  });

  test("hook installer script should exist", () => {
    expect(existsSync(join(ROOT_DIR, "scripts", "setup-hooks.sh"))).toBe(true);
  });

  test("setup-hooks merge should preserve existing nested hooks", () => {
    const installerPath = join(ROOT_DIR, "scripts", "setup-hooks.sh");
    const script = readFileSync(installerPath, "utf-8");

    expect(script.includes("existing.hooks = { ...existing.hooks, ...hooks };")).toBe(false);
    expect(script.includes("const mergeDeep = (current, incoming) =>")).toBe(true);
    expect(script.includes("const stableStringify = (value) =>")).toBe(true);
  });
});
