import { describe, expect, test } from "bun:test";
import {
  validateConditionalDocumentAlignment,
  loadQualityGates,
  loadWorkflowMap,
  validateReferenceFilesExist,
} from "../scripts/skill-contract";

describe("Quality gates", () => {
  test("required reference files should exist", () => {
    const qualityGates = loadQualityGates();
    const errors = validateReferenceFilesExist(qualityGates);
    expect(errors).toEqual([]);
  });

  test("required checks should match command contract", () => {
    const qualityGates = loadQualityGates();
    expect(qualityGates.requiredChecks).toEqual([
      "bun run contract:check",
      "bun run typecheck",
      "bun run test",
    ]);
  });

  test("workflow map generated docs should include all quality-gate required docs", () => {
    const qualityGates = loadQualityGates();
    const workflowMap = loadWorkflowMap();

    for (const doc of qualityGates.requiredGeneratedDocs) {
      expect(workflowMap.generatedDocuments).toContain(doc);
    }
  });

  test("production-readiness gate must stay final milestone", () => {
    const workflowMap = loadWorkflowMap();
    expect(workflowMap.productionReadinessGate.mustBeFinalMilestone).toBe(true);
  });

  test("decisions-template should be in requiredReferenceFiles", () => {
    const qualityGates = loadQualityGates();
    expect(qualityGates.requiredReferenceFiles).toContain("references/decisions-template.md");
  });

  test("new reference templates should be required", () => {
    const qualityGates = loadQualityGates();
    expect(qualityGates.requiredReferenceFiles).toContain("references/agents-template.md");
    expect(qualityGates.requiredReferenceFiles).toContain("references/task-templates.md");
    expect(qualityGates.requiredReferenceFiles).toContain("references/tech-components.md");
  });

  test("generated docs should include task tracking files and AGENTS.md", () => {
    const qualityGates = loadQualityGates();
    expect(qualityGates.requiredGeneratedDocs).toContain("tasks/todo.md");
    expect(qualityGates.requiredGeneratedDocs).toContain("tasks/lessons.md");
    expect(qualityGates.requiredGeneratedDocs).toContain("AGENTS.md");
    expect(qualityGates.requiredGeneratedDocs).toContain("docs/design.md");
  });

  test("conditional generated docs should use normalized condition tokens", () => {
    const qualityGates = loadQualityGates();
    const decisionDoc = qualityGates.conditionalGeneratedDocs?.find(
      (doc) => doc.path === "docs/decisions.md"
    );
    expect(decisionDoc).toBeDefined();
    expect(decisionDoc?.condition).toBe("standard_or_complex_tier");
  });

  test("workflow and quality gates conditional docs should stay aligned", () => {
    const qualityGates = loadQualityGates();
    const workflowMap = loadWorkflowMap();
    const errors = validateConditionalDocumentAlignment(workflowMap, qualityGates);
    expect(errors).toEqual([]);
  });
});

