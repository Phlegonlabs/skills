import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "bun:test";
import { ROOT_DIR, loadQualityGates, validateReferenceFilesExist } from "../scripts/skill-contract";

describe("Quality gates", () => {
  test("required checks should keep the 3-step verification chain", () => {
    const qualityGates = loadQualityGates();
    expect(qualityGates.requiredChecks).toEqual([
      "bun run contract:check",
      "bun run typecheck",
      "bun run test",
    ]);
  });

  test("required reference files should include core docs and all files should exist", () => {
    const qualityGates = loadQualityGates();
    expect(qualityGates.requiredReferenceFiles).toContain("references/interview.md");
    expect(qualityGates.requiredReferenceFiles).toContain("references/templates.md");
    expect(qualityGates.requiredReferenceFiles).toContain("references/review.md");
    expect(qualityGates.requiredReferenceFiles).toContain("references/decisions-template.md");
    expect(qualityGates.requiredReferenceFiles).toContain("references/agents-template.md");
    expect(qualityGates.requiredReferenceFiles).toContain("references/task-templates.md");
    expect(qualityGates.requiredReferenceFiles).toContain("references/tech-components.md");

    const errors = validateReferenceFilesExist(qualityGates);
    expect(errors).toEqual([]);
  });

  test("doc-build-map should not point to missing source trees when present", () => {
    const mapPath = join(ROOT_DIR, "assets", "doc-build-map.v1.json");
    if (!existsSync(mapPath)) {
      expect(existsSync(mapPath)).toBe(false);
      return;
    }

    const parsed = JSON.parse(readFileSync(mapPath, "utf-8")) as {
      targets?: Record<string, { sourceDir?: string }>;
    };

    const targets = parsed.targets ?? {};
    for (const target of Object.values(targets)) {
      if (target.sourceDir) {
        expect(existsSync(join(ROOT_DIR, target.sourceDir))).toBe(true);
      }
    }
  });
});
