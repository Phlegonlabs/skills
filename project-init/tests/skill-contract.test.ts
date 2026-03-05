import { describe, expect, test } from "bun:test";
import {
  loadInterviewQuestionPack,
  loadQualityGates,
  loadWorkflowMap,
  readSkillMarkdown,
  validateInterviewQuestionPack,
  validateModeConsistency,
  validateQualityGates,
  validateSkillMarkdown,
  validateWorkflowMap,
  verifySkillContract,
} from "../scripts/skill-contract";

describe("Contract files", () => {
  test("workflow-map should pass validation", () => {
    const workflowMap = loadWorkflowMap();
    const errors = validateWorkflowMap(workflowMap);
    expect(errors).toEqual([]);
  });

  test("interview-question-pack should pass validation", () => {
    const questionPack = loadInterviewQuestionPack();
    const errors = validateInterviewQuestionPack(questionPack);
    expect(errors).toEqual([]);
  });

  test("quality-gates should pass validation", () => {
    const qualityGates = loadQualityGates();
    const errors = validateQualityGates(qualityGates);
    expect(errors).toEqual([]);
  });

  test("workflow-map and interview-question-pack mode should stay aligned", () => {
    const workflowMap = loadWorkflowMap();
    const questionPack = loadInterviewQuestionPack();
    const errors = validateModeConsistency(workflowMap, questionPack);
    expect(errors).toEqual([]);
  });

  test("SKILL.md should satisfy quality-gates section/phrase contract", () => {
    const skillMarkdown = readSkillMarkdown();
    const qualityGates = loadQualityGates();
    const errors = validateSkillMarkdown(skillMarkdown, qualityGates);
    expect(errors).toEqual([]);
  });

  test("init mode should keep CLI round naming consistent between docs and contract", () => {
    const workflowMap = loadWorkflowMap();
    if (workflowMap.mode !== "init") {
      expect(workflowMap.mode).not.toBe("init");
      return;
    }

    const skillMarkdown = readSkillMarkdown();
    const questionPack = loadInterviewQuestionPack();
    const initRounds = questionPack.requiredRoundSets.init ?? [];

    expect(skillMarkdown).toContain("CLI: 11C-13C");
    expect(skillMarkdown).not.toContain("CLI: R11C-R13C");
    expect(initRounds).toContain("11C");
    expect(initRounds).toContain("12C");
    expect(initRounds).toContain("13C");
  });

  test("full contract verification should pass", () => {
    const result = verifySkillContract();
    expect(result.errors).toEqual([]);
  });
});
