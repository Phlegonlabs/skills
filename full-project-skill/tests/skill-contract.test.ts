import { describe, expect, test } from "bun:test";
import {
  loadDocBuildMap,
  loadInterviewQuestionPack,
  loadQualityGates,
  loadWorkflowMap,
  readSkillMarkdown,
  validateDocBuildMap,
  validateHookScriptsExist,
  validateInterviewQuestionPack,
  validatePartialsExist,
  validateConditionalDocumentAlignment,
  validateDesignTemplateCoverage,
  validateQualityGates,
  validateRequiredChecksAgainstPackageScripts,
  validateUpdateModeCompleteness,
  validateVersionsFreshnessWarnings,
  validateVersionsRegistry,
  validateWorkflowMap,
} from "../scripts/skill-contract";

describe("Contract files", () => {
  test("workflow-map should pass validation", () => {
    const workflowMap = loadWorkflowMap();
    const errors = validateWorkflowMap(workflowMap);
    expect(errors).toEqual([]);
  });

  test("question-pack should pass validation", () => {
    const questionPack = loadInterviewQuestionPack();
    const errors = validateInterviewQuestionPack(questionPack);
    expect(errors).toEqual([]);
  });

  test("quality-gates should pass validation", () => {
    const qualityGates = loadQualityGates();
    const errors = validateQualityGates(qualityGates);
    expect(errors).toEqual([]);
  });

  test("workflow and quality-gates conditional document rules should align", () => {
    const workflowMap = loadWorkflowMap();
    const qualityGates = loadQualityGates();
    const errors = validateConditionalDocumentAlignment(workflowMap, qualityGates);
    expect(errors).toEqual([]);
  });

  test("hook scripts referenced in settings should exist", () => {
    const errors = validateHookScriptsExist();
    expect(errors).toEqual([]);
  });

  test("requiredChecks should match package.json scripts", () => {
    const qualityGates = loadQualityGates();
    const errors = validateRequiredChecksAgainstPackageScripts(qualityGates);
    expect(errors).toEqual([]);
  });

  test("versions registry should pass validation", () => {
    const errors = validateVersionsRegistry();
    expect(errors).toEqual([]);
  });

  test("versions freshness should warn when _lastUpdated is older than 6 months", () => {
    const warnings = validateVersionsFreshnessWarnings(new Date(Date.UTC(2026, 11, 1)));
    expect(warnings.length).toBeGreaterThan(0);
    expect(warnings[0]).toContain("_lastUpdated");
  });

  test("versions freshness should not warn within 6 months", () => {
    const warnings = validateVersionsFreshnessWarnings(new Date(Date.UTC(2026, 4, 1)));
    expect(warnings).toEqual([]);
  });

  test("versions freshness should warn when _lastUpdated is in the future", () => {
    const warnings = validateVersionsFreshnessWarnings(new Date(Date.UTC(2025, 0, 1)));
    expect(warnings.length).toBeGreaterThan(0);
    expect(warnings[0]).toContain("in the future");
  });

  test("partial template directories should pass validation", () => {
    const errors = validatePartialsExist();
    expect(errors).toEqual([]);
  });
});

describe("Validation error paths", () => {
  test("workflow-map should report version mismatch", () => {
    const workflowMap = loadWorkflowMap();
    const invalidMap = { ...workflowMap, version: "workflow-map.v2" as "workflow-map.v1" };
    const errors = validateWorkflowMap(invalidMap);
    expect(errors.some((error) => error.includes("version mismatch"))).toBe(true);
  });

  test("workflow-map should report missing tier key", () => {
    const workflowMap = loadWorkflowMap();
    const invalidMap = {
      ...workflowMap,
      tiers: {
        standard: workflowMap.tiers.standard,
      },
    } as typeof workflowMap;
    const errors = validateWorkflowMap(invalidMap);
    expect(errors.some((error) => error.includes("tiers must be exactly"))).toBe(true);
  });

  test("question-pack should report empty update rounds", () => {
    const questionPack = loadInterviewQuestionPack();
    const invalidPack = {
      ...questionPack,
      update: {
        ...questionPack.update,
        bug_fix: [],
      },
    };
    const errors = validateInterviewQuestionPack(invalidPack);
    expect(errors.some((error) => error.includes("update.bug_fix must not be empty"))).toBe(true);
  });

  test("quality-gates should report version mismatch", () => {
    const qualityGates = loadQualityGates();
    const invalidGates = { ...qualityGates, version: "quality-gates.v2" as "quality-gates.v1" };
    const errors = validateQualityGates(invalidGates);
    expect(errors.some((error) => error.includes("version mismatch"))).toBe(true);
  });

  test("quality-gates should report missing design-doc required section", () => {
    const qualityGates = loadQualityGates();
    const invalidGates = {
      ...qualityGates,
      designDocRequiredSections: {
        ...qualityGates.designDocRequiredSections,
        sections: qualityGates.designDocRequiredSections.sections.filter(
          (section) => section !== "Component Inventory"
        ),
      },
    };
    const errors = validateQualityGates(invalidGates);
    expect(
      errors.some((error) =>
        error.includes("designDocRequiredSections.sections missing required section: Component Inventory")
      )
    ).toBe(true);
  });

  test("doc-build map should report invalid targets object", () => {
    const map = loadDocBuildMap();
    const invalidMap = {
      ...map,
      targets: undefined,
    } as unknown as typeof map;
    const errors = validateDocBuildMap(invalidMap);
    expect(errors).toContain("doc-build-map targets must be an object");
  });
});

describe("Workflow invariants", () => {
  test("standard tier should stay default with simplified review chain", () => {
    const workflowMap = loadWorkflowMap();
    expect(workflowMap.tiers.standard.isDefault).toBe(true);
    expect(workflowMap.tiers.standard.reviewAgents).toEqual([
      "agent-2",
      "agent-3",
      "codex-review",
    ]);
  });

  test("complex tier should include codex + post-codex review chain", () => {
    const workflowMap = loadWorkflowMap();
    expect(workflowMap.tiers.complex.reviewAgents).toEqual([
      "agent-1",
      "agent-2",
      "agent-3",
      "codex-review",
      "agent-2-post-codex",
      "agent-3-post-codex",
    ]);
  });

  test("update type ranges should preserve current process intent", () => {
    const workflowMap = loadWorkflowMap();
    expect(workflowMap.updateTypes.new_feature.roundRange).toEqual([3, 8]);
    expect(workflowMap.updateTypes.bug_fix.roundRange).toEqual([1, 3]);
    expect(workflowMap.updateTypes.change.roundRange).toEqual([2, 5]);
  });

  test("convert profile ranges should preserve current process intent", () => {
    const workflowMap = loadWorkflowMap();
    expect(workflowMap.convertProfiles.baseline_conversion.roundRange).toEqual([2, 4]);
    expect(workflowMap.convertProfiles.upgrade_conversion.roundRange).toEqual([3, 6]);
  });

  test("userPreferencesCheckRound should be R10.7", () => {
    const questionPack = loadInterviewQuestionPack();
    expect(questionPack.rules.userPreferencesCheckRound).toBe("R10.7");
  });

  test("required generated docs should include AGENTS.md and task trackers", () => {
    const workflowMap = loadWorkflowMap();
    expect(workflowMap.generatedDocuments).toContain("AGENTS.md");
    expect(workflowMap.generatedDocuments).toContain("tasks/todo.md");
    expect(workflowMap.generatedDocuments).toContain("tasks/lessons.md");
    expect(workflowMap.generatedDocuments).toContain("docs/design.md");
  });

  test("mode detection should include convert policy signals", () => {
    const workflowMap = loadWorkflowMap();
    expect(workflowMap.modeDetection.codeRoots).toContain("src/");
    expect(workflowMap.modeDetection.codeRoots).toContain("apps/*/src");
    expect(workflowMap.modeDetection.convertModePolicy).toContain("convert");
  });
});

describe("requiredChecks vs package.json drift detection", () => {
  test("should detect missing script when requiredChecks references nonexistent script", () => {
    const fakeGates = {
      ...loadQualityGates(),
      requiredChecks: ["bun run contract:check", "bun run nonexistent:script"],
    };
    const errors = validateRequiredChecksAgainstPackageScripts(fakeGates);
    expect(errors.length).toBe(1);
    expect(errors[0]).toContain("nonexistent:script");
  });

  test("should pass when all requiredChecks match package.json scripts", () => {
    const gates = loadQualityGates();
    const errors = validateRequiredChecksAgainstPackageScripts(gates);
    expect(errors).toEqual([]);
  });

  test("should reject unsupported requiredChecks command format", () => {
    const fakeGates = {
      ...loadQualityGates(),
      requiredChecks: ["npm run test"],
    };
    const errors = validateRequiredChecksAgainstPackageScripts(fakeGates);
    expect(errors.length).toBe(1);
    expect(errors[0]).toContain("unsupported format");
  });
});

describe("Update mode completeness", () => {
  test("validateUpdateModeCompleteness should pass with current files", () => {
    const skillMd = readSkillMarkdown();
    const workflowMap = loadWorkflowMap();
    const questionPack = loadInterviewQuestionPack();
    const errors = validateUpdateModeCompleteness(skillMd, workflowMap, questionPack);
    expect(errors).toEqual([]);
  });

  test("updatePhaseOrder should include phase-3.7 user annotation review", () => {
    const workflowMap = loadWorkflowMap();
    expect(workflowMap.updatePhaseOrder).toContain("update-phase-3.7-user-annotation-review");
  });

  test("updatePhaseOrder should have phase-3.7 after phase-3.5 and before phase-4", () => {
    const workflowMap = loadWorkflowMap();
    const order = workflowMap.updatePhaseOrder;
    const idx35 = order.indexOf("update-phase-3.5-documentation-review");
    const idx37 = order.indexOf("update-phase-3.7-user-annotation-review");
    const idx4 = order.indexOf("update-phase-4-next-steps");
    expect(idx35).toBeLessThan(idx37);
    expect(idx37).toBeLessThan(idx4);
  });

  test("convertPhaseOrder should include phase-3.7 user annotation review", () => {
    const workflowMap = loadWorkflowMap();
    expect(workflowMap.convertPhaseOrder).toContain("convert-phase-3.7-user-annotation-review");
  });

  test("convertPhaseOrder should have phase-3.7 after phase-3.5 and before phase-4", () => {
    const workflowMap = loadWorkflowMap();
    const order = workflowMap.convertPhaseOrder;
    const idx35 = order.indexOf("convert-phase-3.5-documentation-review");
    const idx37 = order.indexOf("convert-phase-3.7-user-annotation-review");
    const idx4 = order.indexOf("convert-phase-4-next-steps");
    expect(idx35).toBeLessThan(idx37);
    expect(idx37).toBeLessThan(idx4);
  });

  test("new_feature interview rounds should include F0", () => {
    const questionPack = loadInterviewQuestionPack();
    expect(questionPack.update.new_feature).toContain("F0");
    expect(questionPack.update.new_feature[0]).toBe("F0");
    expect(questionPack.update.new_feature).toContain("F4.5");
    expect(questionPack.update.new_feature).toContain("F8");
  });

  test("convert interview rounds should include CV0 and CU4", () => {
    const questionPack = loadInterviewQuestionPack();
    expect(questionPack.convert.baseline_conversion[0]).toBe("CV0");
    expect(questionPack.convert.baseline_conversion).toContain("CV3");
    expect(questionPack.convert.upgrade_conversion[0]).toBe("CV0");
    expect(questionPack.convert.upgrade_conversion).toContain("CU4");
  });

  test("init interview rounds should place 2.8 between 2.7 and R1", () => {
    const questionPack = loadInterviewQuestionPack();
    const rounds = questionPack.init.rounds.map((round) => round.id);
    const idx27 = rounds.indexOf("2.7");
    const idx28 = rounds.indexOf("2.8");
    const idxR1 = rounds.indexOf("R1");
    expect(idx27).toBeGreaterThanOrEqual(0);
    expect(idx28).toBeGreaterThanOrEqual(0);
    expect(idxR1).toBeGreaterThanOrEqual(0);
    expect(idx27).toBeLessThan(idx28);
    expect(idx28).toBeLessThan(idxR1);
  });

  test("init interview rounds should include optional mobile rounds", () => {
    const questionPack = loadInterviewQuestionPack();
    const roundMap = new Map(questionPack.init.rounds.map((round) => [round.id, round]));
    expect(roundMap.get("R11M")?.required).toBe(false);
    expect(roundMap.get("R12M")?.required).toBe(false);
    expect(roundMap.get("R13M")?.required).toBe(false);
  });

  test("each update type should have at least 1 interview round", () => {
    const questionPack = loadInterviewQuestionPack();
    expect(questionPack.update.new_feature.length).toBeGreaterThanOrEqual(1);
    expect(questionPack.update.bug_fix.length).toBeGreaterThanOrEqual(1);
    expect(questionPack.update.change.length).toBeGreaterThanOrEqual(1);
  });

  test("each convert profile should have at least 1 interview round", () => {
    const questionPack = loadInterviewQuestionPack();
    expect(questionPack.convert.baseline_conversion.length).toBeGreaterThanOrEqual(1);
    expect(questionPack.convert.upgrade_conversion.length).toBeGreaterThanOrEqual(1);
  });

  test("conditional documents should include docs/decisions.md", () => {
    const workflowMap = loadWorkflowMap();
    expect(workflowMap.conditionalDocuments).toBeDefined();
    const decisionDoc = workflowMap.conditionalDocuments?.find(
      (d) => d.path === "docs/decisions.md"
    );
    expect(decisionDoc).toBeDefined();
    expect(decisionDoc!.condition).toBe("standard_or_complex_tier");
  });

  test("workflow-map should reject unsupported conditional document condition tokens", () => {
    const workflowMap = loadWorkflowMap();
    const invalidMap = {
      ...workflowMap,
      conditionalDocuments: [{ path: "docs/decisions.md", condition: "legacy_condition" }],
    };
    const errors = validateWorkflowMap(invalidMap);
    expect(errors.some((error) => error.includes("condition must be one of"))).toBe(true);
  });

  test("quality-gates should reject unsupported conditional generated-doc condition tokens", () => {
    const qualityGates = loadQualityGates();
    const invalidGates = {
      ...qualityGates,
      conditionalGeneratedDocs: [{ path: "docs/decisions.md", condition: "legacy_condition" }],
    };
    const errors = validateQualityGates(invalidGates);
    expect(errors.some((error) => error.includes("condition must be one of"))).toBe(true);
  });

  test("conditional document alignment check should detect mismatches", () => {
    const workflowMap = loadWorkflowMap();
    const qualityGates = loadQualityGates();
    const mismatchedGates = {
      ...qualityGates,
      conditionalGeneratedDocs: [{ path: "docs/other.md", condition: "standard_or_complex_tier" }],
    };
    const errors = validateConditionalDocumentAlignment(workflowMap, mismatchedGates);
    expect(errors.length).toBeGreaterThan(0);
  });

  test("workflow-map should reject non-array conditionalDocuments", () => {
    const workflowMap = loadWorkflowMap();
    const invalidMap = {
      ...workflowMap,
      conditionalDocuments: {
        path: "docs/decisions.md",
        condition: "standard_or_complex_tier",
      },
    } as unknown as typeof workflowMap;
    const errors = validateWorkflowMap(invalidMap);
    expect(errors.some((error) => error.includes("must be an array"))).toBe(true);
  });

  test("SKILL.md should contain Update Phase 3.7 section", () => {
    const skillMd = readSkillMarkdown();
    expect(skillMd).toContain("### Update Phase 3.7");
    expect(skillMd).toContain("User Annotation Review");
  });

  test("SKILL.md should contain Convert/Upgrade mode section", () => {
    const skillMd = readSkillMarkdown();
    expect(skillMd).toContain("## Convert/Upgrade Mode");
    expect(skillMd).toContain("### Convert Phase 3.7");
  });

  test("SKILL.md Update Phase 3.5 should reference cross-model review", () => {
    const skillMd = readSkillMarkdown();
    expect(skillMd).toContain("Cross-Model Review (Mandatory):");
  });

  test("SKILL.md should use F0-F8 update round range wording", () => {
    const skillMd = readSkillMarkdown();
    expect(skillMd).toContain("F0-F8");
  });

  test("design template should contain required design-doc sections", () => {
    const qualityGates = loadQualityGates();
    const errors = validateDesignTemplateCoverage(qualityGates);
    expect(errors).toEqual([]);
  });

  test("SKILL.md Update Phase 1 should have specific codebase scan strategy", () => {
    const skillMd = readSkillMarkdown();
    expect(skillMd).toContain("Scan strategy:");
    expect(skillMd).toContain("Grep for key patterns");
  });
});
