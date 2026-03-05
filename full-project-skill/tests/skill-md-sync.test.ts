import { describe, expect, test } from "bun:test";
import {
  loadQualityGates,
  readSkillMarkdown,
  validateSkillMarkdown,
  verifySkillContract,
} from "../scripts/skill-contract";

describe("SKILL.md sync", () => {
  test("should include core workflow phases", () => {
    const skill = readSkillMarkdown();
    expect(skill).toContain("### Phase 1: Interactive Interview");
    expect(skill).toContain("### Phase 2: Generate Documentation");
    expect(skill).toContain("### Phase 2.5: Multi-Agent Documentation Review");
    expect(skill).toContain("## Update Mode (modifying an existing project)");
    expect(skill).toContain("### Update Phase 3: Update Documentation");
  });

  test("should include engineering and quality sections", () => {
    const skill = readSkillMarkdown();
    expect(skill).toContain("## Engineering Layer");
    expect(skill).toContain("### Contract Files");
    expect(skill).toContain("### Script Entry Points");
    expect(skill).toContain("### Quality Gates");
  });

  test("should satisfy required sections and phrases in quality-gates config", () => {
    const skill = readSkillMarkdown();
    const qualityGates = loadQualityGates();
    const errors = validateSkillMarkdown(skill, qualityGates);
    expect(errors).toEqual([]);
  });

  test("should mention Claude Code Hooks in Phase 3", () => {
    const skill = readSkillMarkdown();
    expect(skill).toContain("Claude Code Hooks");
  });

  test("should mention task tracking files and tech component reference", () => {
    const skill = readSkillMarkdown();
    expect(skill).toContain("tasks/todo.md");
    expect(skill).toContain("tasks/lessons.md");
    expect(skill).toContain("references/tech-components.md");
  });

  test("full contract verification should pass", () => {
    const result = verifySkillContract();
    expect(result.errors).toEqual([]);
  });
});

