import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "bun:test";
import {
  ROOT_DIR,
  loadDocBuildMap,
  validateDocBuildMap,
  validateGeneratedArtifacts,
} from "../scripts/skill-contract";
import { parseAssemblyOrder } from "../scripts/lib/parse-assembly-order";

describe("Doc build map", () => {
  test("should load and validate map with required targets", () => {
    const map = loadDocBuildMap();
    const errors = validateDocBuildMap(map);

    expect(errors).toEqual([]);
    expect(Object.keys(map.targets).sort()).toEqual(["interview", "review", "skill", "templates"]);
  });

  test("target output paths should match contract", () => {
    const map = loadDocBuildMap();
    expect(map.targets.skill.output).toBe("SKILL.md");
    expect(map.targets.interview.output).toBe("references/interview.md");
    expect(map.targets.templates.output).toBe("references/templates.md");
    expect(map.targets.review.output).toBe("references/review.md");
  });
});

describe("Assembly order parser", () => {
  test("should parse numbered list entries", () => {
    const parsed = parseAssemblyOrder("# Order\n\n1. a.partial.md\n2. b.partial.md\n");
    expect(parsed).toEqual(["a.partial.md", "b.partial.md"]);
  });

  test("should ignore non-numbered and condition declaration lines", () => {
    const parsed = parseAssemblyOrder(
      "# Order\n\nfoo\nCondition blocks supported in partial content:\n- `{{#IF X}}`\n1. c.partial.md\n"
    );
    expect(parsed).toEqual(["c.partial.md"]);
  });

  test("should return empty array for content without list entries", () => {
    const parsed = parseAssemblyOrder("# Empty\n\nNo numbered list here.\n");
    expect(parsed).toEqual([]);
  });

  test("should trim trailing whitespace in numbered list entries", () => {
    const parsed = parseAssemblyOrder("1. foo.partial.md  \n");
    expect(parsed).toEqual(["foo.partial.md"]);
  });
});

describe("Source partial completeness", () => {
  test("all source directories, order files, and listed partials should exist", () => {
    const map = loadDocBuildMap();

    for (const target of Object.values(map.targets)) {
      const sourceDirAbs = join(ROOT_DIR, target.sourceDir);
      expect(existsSync(sourceDirAbs)).toBe(true);

      const orderAbs = join(sourceDirAbs, target.orderFile);
      expect(existsSync(orderAbs)).toBe(true);

      const partials = parseAssemblyOrder(readFileSync(orderAbs, "utf-8"));
      expect(partials.length).toBeGreaterThan(0);
      for (const partial of partials) {
        expect(existsSync(join(sourceDirAbs, partial))).toBe(true);
      }
    }
  });

  test("source directories should not contain orphan partial files", () => {
    const map = loadDocBuildMap();

    for (const target of Object.values(map.targets)) {
      const sourceDirAbs = join(ROOT_DIR, target.sourceDir);
      const orderAbs = join(sourceDirAbs, target.orderFile);
      const partials = parseAssemblyOrder(readFileSync(orderAbs, "utf-8"));
      const listed = new Set(partials);
      const allPartials = readdirSync(sourceDirAbs).filter((name: string) => name.endsWith(".partial.md"));

      for (const partial of allPartials) {
        expect(listed.has(partial)).toBe(true);
      }
    }
  });
});

describe("Artifact drift", () => {
  test("generated artifacts should match source assembly", () => {
    const map = loadDocBuildMap();
    const errors = validateGeneratedArtifacts(map);
    expect(errors).toEqual([]);
  });
});
