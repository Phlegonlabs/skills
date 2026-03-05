import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { parseAssemblyOrder } from "./lib/parse-assembly-order";
import { firstDiffLine, normalizeEol } from "./lib/text-utils";

type TierKey = "standard" | "complex";
type UpdateTypeKey = "new_feature" | "bug_fix" | "change";
type ConditionalDocumentCondition = "standard_or_complex_tier";
type DesignDocRequiredSectionsCondition = "gui_project";
type ConditionalDocumentRule = {
  path: string;
  condition: string;
};
type DesignDocRequiredSectionsRule = {
  condition: string;
  sections: string[];
};

export interface TierConfig {
  isDefault: boolean;
  targetQuestions: number;
  // Base round range for full init-mode interviews by tier.
  baseRoundRange: [number, number];
  followUpCap: number;
  milestoneRange: [number, number];
  reviewAgents: string[];
}

export interface WorkflowMapV1 {
  version: "workflow-map.v1";
  modeDetection: {
    updateModeDocs: string[];
    corruptedStatePolicy: string;
  };
  tiers: Record<TierKey, TierConfig>;
  initPhaseOrder: string[];
  updatePhaseOrder: string[];
  updateTypes: Record<
    UpdateTypeKey,
    {
      // Round range for update-mode interviews only.
      roundRange: [number, number];
      followUpCapRange: [number, number];
    }
  >;
  generatedDocuments: string[];
  conditionalDocuments?: ConditionalDocumentRule[];
  productionReadinessGate: {
    milestoneKey: string;
    mustBeFinalMilestone: boolean;
  };
}

export interface InterviewQuestionPackV1 {
  version: "interview-question-pack.v1";
  init: {
    minRoundsByTier: Record<TierKey, number>;
    rounds: Array<{
      id: string;
      title: string;
      bucket: string;
      required: boolean;
    }>;
  };
  update: Record<UpdateTypeKey, string[]>;
  rules: {
    maxQuestionsPerRound: number;
    followUpRoundFormat: string;
    techStackLockRound: string;
    userPreferencesCheckRound: string;
  };
}

export interface QualityGatesV1 {
  version: "quality-gates.v1";
  requiredReferenceFiles: string[];
  requiredSkillSections: string[];
  requiredPhrases: string[];
  requiredGeneratedDocs: string[];
  conditionalGeneratedDocs?: ConditionalDocumentRule[];
  designDocRequiredSections: DesignDocRequiredSectionsRule;
  requiredChecks: string[];
}

export interface DocBuildTarget {
  sourceDir: string;
  orderFile: string;
  output: string;
  conditionalBlocks: boolean;
  separator: string;
}

export interface DocBuildMapV1 {
  version: "doc-build-map.v1";
  targets: Record<string, DocBuildTarget>;
}

export interface VerificationResult {
  errors: string[];
  warnings: string[];
}

const REQUIRED_TIERS: TierKey[] = ["standard", "complex"];
const REQUIRED_UPDATE_TYPES: UpdateTypeKey[] = ["new_feature", "bug_fix", "change"];
const REQUIRED_UPDATE_MODE_DOCS = ["docs/architecture.md", "docs/plans.md"];
const REQUIRED_INIT_ROUNDS = [
  "2.5",
  "2.7",
  "2.8",
  "R1",
  "R2",
  "R3",
  "R4",
  "R5",
  "R6",
  "R7",
  "R8",
  "R9",
  "R10",
  "R10.3",
  "R10.5",
  "R10.7",
  "R11",
  "R11M",
  "R12M",
  "R13M",
  "11C",
  "12C",
  "13C",
  "R14",
];
const REQUIRED_NEW_FEATURE_UPDATE_ROUNDS = ["F0", "F1", "F2", "F3", "F4", "F4.5", "F5", "F6", "F7", "F8"];
const REQUIRED_DOCS = [
  "docs/architecture.md",
  "docs/plans.md",
  "docs/implement.md",
  "docs/secrets.md",
  "docs/documentation.md",
  "docs/design.md",
  "tasks/todo.md",
  "tasks/lessons.md",
  "CLAUDE.md",
  "AGENTS.md",
];
const REQUIRED_VERSION_CATEGORIES = [
  "core",
  "meta-frameworks",
  "routing",
  "ui",
  "state",
  "backend",
  "testing",
  "tools",
];
const REQUIRED_CLAUDE_PARTIALS = [
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
  "_assembly-order.md",
];
const REQUIRED_AGENT_PARTIALS = [
  "01-header.partial.md",
  "02-operating-mode.partial.md",
  "03-key-docs.partial.md",
  "04-tech-stack.partial.md",
  "05-commands.partial.md",
  "06-orchestration.partial.md",
  "07-task-protocol.partial.md",
  "08-coding-constraints.partial.md",
  "_assembly-order.md",
];
const REQUIRED_DOC_BUILD_TARGETS = ["skill", "interview", "templates", "review"];
const REQUIRED_DESIGN_DOC_SECTIONS = [
  "Component Inventory",
  "Composition Patterns",
  "Interactive Patterns",
  "Layout System",
  "Living Design Guide",
  "File Conventions",
  "Common Mistakes",
];
const KNOWN_CONDITIONAL_DOCUMENT_CONDITIONS: ReadonlySet<ConditionalDocumentCondition> = new Set([
  "standard_or_complex_tier",
]);
const KNOWN_DESIGN_DOC_REQUIRED_SECTION_CONDITIONS: ReadonlySet<DesignDocRequiredSectionsCondition> =
  new Set(["gui_project"]);

export const ROOT_DIR = join(import.meta.dir, "..");
export const ASSETS_DIR = join(ROOT_DIR, "assets");
export const SKILL_MD_PATH = join(ROOT_DIR, "SKILL.md");
export const DOC_BUILD_MAP_PATH = join(ASSETS_DIR, "doc-build-map.v1.json");
export const TEMPLATES_MD_PATH = join(ROOT_DIR, "references", "templates.md");

type JsonFileShape = {
  label: string;
  version: string;
  requiredKeys: string[];
};

const WORKFLOW_MAP_SHAPE: JsonFileShape = {
  label: "workflow-map",
  version: "workflow-map.v1",
  requiredKeys: [
    "modeDetection",
    "tiers",
    "initPhaseOrder",
    "updatePhaseOrder",
    "updateTypes",
    "generatedDocuments",
    "productionReadinessGate",
  ],
};

const INTERVIEW_QUESTION_PACK_SHAPE: JsonFileShape = {
  label: "interview-question-pack",
  version: "interview-question-pack.v1",
  requiredKeys: ["init", "update", "rules"],
};

const QUALITY_GATES_SHAPE: JsonFileShape = {
  label: "quality-gates",
  version: "quality-gates.v1",
  requiredKeys: [
    "requiredReferenceFiles",
    "requiredSkillSections",
    "requiredPhrases",
    "requiredGeneratedDocs",
    "designDocRequiredSections",
    "requiredChecks",
  ],
};

const DOC_BUILD_MAP_SHAPE: JsonFileShape = {
  label: "doc-build-map",
  version: "doc-build-map.v1",
  requiredKeys: ["targets"],
};

function validateJsonFileShape(
  absolutePath: string,
  parsed: unknown,
  shape: JsonFileShape
): Record<string, unknown> {
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new Error(`Invalid ${shape.label} at ${absolutePath}: top-level JSON must be an object`);
  }

  const candidate = parsed as Record<string, unknown>;
  if (candidate.version !== shape.version) {
    throw new Error(
      `Invalid ${shape.label} at ${absolutePath}: expected version "${shape.version}", received "${String(
        candidate.version
      )}"`
    );
  }

  for (const key of shape.requiredKeys) {
    if (!(key in candidate)) {
      throw new Error(`Invalid ${shape.label} at ${absolutePath}: missing required top-level key "${key}"`);
    }
  }

  return candidate;
}

function loadJsonFile<T>(absolutePath: string, shape: JsonFileShape): T {
  if (!existsSync(absolutePath)) {
    throw new Error(`Missing file: ${absolutePath}`);
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(readFileSync(absolutePath, "utf-8"));
  } catch (error) {
    throw new Error(
      `Invalid JSON at ${absolutePath}: ${error instanceof Error ? error.message : String(error)}`
    );
  }

  return validateJsonFileShape(absolutePath, parsed, shape) as T;
}

export function loadWorkflowMap(): WorkflowMapV1 {
  return loadJsonFile<WorkflowMapV1>(join(ASSETS_DIR, "workflow-map.v1.json"), WORKFLOW_MAP_SHAPE);
}

export function loadInterviewQuestionPack(): InterviewQuestionPackV1 {
  return loadJsonFile<InterviewQuestionPackV1>(
    join(ASSETS_DIR, "interview-question-pack.v1.json"),
    INTERVIEW_QUESTION_PACK_SHAPE
  );
}

export function loadQualityGates(): QualityGatesV1 {
  return loadJsonFile<QualityGatesV1>(join(ASSETS_DIR, "quality-gates.v1.json"), QUALITY_GATES_SHAPE);
}

export function loadDocBuildMap(): DocBuildMapV1 {
  return loadJsonFile<DocBuildMapV1>(DOC_BUILD_MAP_PATH, DOC_BUILD_MAP_SHAPE);
}

export function readSkillMarkdown(): string {
  if (!existsSync(SKILL_MD_PATH)) {
    throw new Error(`Missing SKILL.md: ${SKILL_MD_PATH}`);
  }
  return readFileSync(SKILL_MD_PATH, "utf-8");
}

export function validateWorkflowMap(map: WorkflowMapV1): string[] {
  const errors: string[] = [];

  if (map.version !== "workflow-map.v1") {
    errors.push(`workflow-map version mismatch: ${map.version}`);
  }

  const tierKeys = Object.keys(map.tiers).sort();
  const expectedTierKeys = [...REQUIRED_TIERS].sort();
  const hasExactTierKeys =
    tierKeys.length === expectedTierKeys.length &&
    tierKeys.every((key, index) => key === expectedTierKeys[index]);
  if (!hasExactTierKeys) {
    errors.push(`workflow-map tiers must be exactly ${expectedTierKeys.join(", ")}`);
  }

  const defaultTierKeys = REQUIRED_TIERS.filter((tier) => map.tiers[tier]?.isDefault);
  if (defaultTierKeys.length !== 1) {
    errors.push(`workflow-map must have exactly one default tier, found: ${defaultTierKeys.join(", ")}`);
  }
  if (map.tiers.standard?.isDefault !== true) {
    errors.push("workflow-map standard tier must be the default tier");
  }

  for (const tier of REQUIRED_TIERS) {
    const config = map.tiers[tier];
    if (!config) continue;

    if (config.baseRoundRange[0] > config.baseRoundRange[1]) {
      errors.push(`${tier} baseRoundRange is invalid`);
    }
    if (config.milestoneRange[0] > config.milestoneRange[1]) {
      errors.push(`${tier} milestoneRange is invalid`);
    }
    if (config.followUpCap <= 0) {
      errors.push(`${tier} followUpCap must be > 0`);
    }
    if (config.reviewAgents.length === 0) {
      errors.push(`${tier} reviewAgents must not be empty`);
    }
  }

  for (const doc of REQUIRED_UPDATE_MODE_DOCS) {
    if (!map.modeDetection.updateModeDocs.includes(doc)) {
      errors.push(`workflow-map modeDetection.updateModeDocs missing ${doc}`);
    }
  }

  for (const updateType of REQUIRED_UPDATE_TYPES) {
    const config = map.updateTypes[updateType];
    if (!config) {
      errors.push(`workflow-map updateTypes missing ${updateType}`);
      continue;
    }
    if (config.roundRange[0] > config.roundRange[1]) {
      errors.push(`workflow-map updateTypes.${updateType}.roundRange is invalid`);
    }
    if (config.followUpCapRange[0] > config.followUpCapRange[1]) {
      errors.push(`workflow-map updateTypes.${updateType}.followUpCapRange is invalid`);
    }
  }

  for (const doc of REQUIRED_DOCS) {
    if (!map.generatedDocuments.includes(doc)) {
      errors.push(`workflow-map generatedDocuments missing ${doc}`);
    }
  }

  if (map.productionReadinessGate.mustBeFinalMilestone !== true) {
    errors.push("workflow-map productionReadinessGate.mustBeFinalMilestone must be true");
  }

  if (!map.initPhaseOrder.includes("phase-2.5-multi-agent-documentation-review")) {
    errors.push("workflow-map initPhaseOrder missing phase-2.5-multi-agent-documentation-review");
  }
  if (!map.updatePhaseOrder.includes("update-phase-3.5-documentation-review")) {
    errors.push("workflow-map updatePhaseOrder missing update-phase-3.5-documentation-review");
  }
  errors.push(
    ...validateConditionalDocumentRules("workflow-map conditionalDocuments", map.conditionalDocuments)
  );

  return errors;
}

export function validateInterviewQuestionPack(pack: InterviewQuestionPackV1): string[] {
  const errors: string[] = [];

  if (pack.version !== "interview-question-pack.v1") {
    errors.push(`interview-question-pack version mismatch: ${pack.version}`);
  }

  for (const tier of REQUIRED_TIERS) {
    if (pack.init.minRoundsByTier[tier] === undefined) {
      errors.push(`interview-question-pack missing minRoundsByTier.${tier}`);
    }
  }

  const roundIds = new Set(pack.init.rounds.map((round) => round.id));
  for (const requiredRound of REQUIRED_INIT_ROUNDS) {
    if (!roundIds.has(requiredRound)) {
      errors.push(`interview-question-pack missing init round ${requiredRound}`);
    }
  }

  for (const updateType of REQUIRED_UPDATE_TYPES) {
    const rounds = pack.update[updateType];
    if (!Array.isArray(rounds) || rounds.length === 0) {
      errors.push(`interview-question-pack update.${updateType} must not be empty`);
    }
  }
  for (const round of REQUIRED_NEW_FEATURE_UPDATE_ROUNDS) {
    if (!pack.update.new_feature.includes(round)) {
      errors.push(`interview-question-pack update.new_feature missing ${round}`);
    }
  }
  if (pack.update.new_feature[0] !== "F0") {
    errors.push("interview-question-pack update.new_feature must start with F0");
  }

  if (pack.rules.techStackLockRound !== "R10.7") {
    errors.push("interview-question-pack rules.techStackLockRound must be R10.7");
  }
  if (pack.rules.userPreferencesCheckRound !== "R10.7") {
    errors.push("interview-question-pack rules.userPreferencesCheckRound must be R10.7");
  }
  if (pack.rules.maxQuestionsPerRound !== 2) {
    errors.push("interview-question-pack rules.maxQuestionsPerRound must be 2");
  }

  return errors;
}

export function validateQualityGates(gates: QualityGatesV1): string[] {
  const errors: string[] = [];

  if (gates.version !== "quality-gates.v1") {
    errors.push(`quality-gates version mismatch: ${gates.version}`);
  }

  if (gates.requiredReferenceFiles.length === 0) {
    errors.push("quality-gates requiredReferenceFiles must not be empty");
  }
  if (gates.requiredSkillSections.length === 0) {
    errors.push("quality-gates requiredSkillSections must not be empty");
  }
  if (gates.requiredGeneratedDocs.length === 0) {
    errors.push("quality-gates requiredGeneratedDocs must not be empty");
  }
  if (gates.requiredChecks.length === 0) {
    errors.push("quality-gates requiredChecks must not be empty");
  }
  errors.push(...validateDesignDocRequiredSections(gates.designDocRequiredSections));

  for (const doc of REQUIRED_DOCS) {
    if (!gates.requiredGeneratedDocs.includes(doc)) {
      errors.push(`quality-gates requiredGeneratedDocs missing ${doc}`);
    }
  }
  errors.push(
    ...validateConditionalDocumentRules(
      "quality-gates conditionalGeneratedDocs",
      gates.conditionalGeneratedDocs
    )
  );

  return errors;
}

function validateDesignDocRequiredSections(rule: DesignDocRequiredSectionsRule | undefined): string[] {
  const errors: string[] = [];

  if (!rule || typeof rule !== "object" || Array.isArray(rule)) {
    errors.push("quality-gates designDocRequiredSections must be an object");
    return errors;
  }
  if (
    typeof rule.condition !== "string" ||
    !KNOWN_DESIGN_DOC_REQUIRED_SECTION_CONDITIONS.has(
      rule.condition as DesignDocRequiredSectionsCondition
    )
  ) {
    const allowed = [...KNOWN_DESIGN_DOC_REQUIRED_SECTION_CONDITIONS].join(", ");
    errors.push(
      `quality-gates designDocRequiredSections.condition must be one of: ${allowed} (received "${String(
        rule.condition
      )}")`
    );
  }
  if (!Array.isArray(rule.sections) || rule.sections.length === 0) {
    errors.push("quality-gates designDocRequiredSections.sections must not be empty");
    return errors;
  }

  const normalizedSections = new Set<string>();
  for (let index = 0; index < rule.sections.length; index += 1) {
    const section = rule.sections[index];
    if (typeof section !== "string" || section.trim() === "") {
      errors.push(`quality-gates designDocRequiredSections.sections[${index}] must be a non-empty string`);
      continue;
    }
    const normalized = section.trim();
    if (normalizedSections.has(normalized)) {
      errors.push(`quality-gates designDocRequiredSections.sections has duplicate: ${normalized}`);
    }
    normalizedSections.add(normalized);
  }

  for (const requiredSection of REQUIRED_DESIGN_DOC_SECTIONS) {
    if (!normalizedSections.has(requiredSection)) {
      errors.push(
        `quality-gates designDocRequiredSections.sections missing required section: ${requiredSection}`
      );
    }
  }

  return errors;
}

function validateConditionalDocumentRules(
  source: string,
  rules: ConditionalDocumentRule[] | undefined | unknown
): string[] {
  const errors: string[] = [];
  if (!rules) return errors;
  if (!Array.isArray(rules)) {
    errors.push(`${source} must be an array when provided`);
    return errors;
  }

  const seen = new Set<string>();
  for (let index = 0; index < rules.length; index += 1) {
    const rule = rules[index];
    if (!rule || typeof rule.path !== "string" || rule.path.trim() === "") {
      errors.push(`${source}[${index}] path must be a non-empty string`);
    }
    if (
      !rule ||
      typeof rule.condition !== "string" ||
      !KNOWN_CONDITIONAL_DOCUMENT_CONDITIONS.has(rule.condition as ConditionalDocumentCondition)
    ) {
      const allowed = [...KNOWN_CONDITIONAL_DOCUMENT_CONDITIONS].join(", ");
      errors.push(
        `${source}[${index}] condition must be one of: ${allowed} (received "${String(rule?.condition)}")`
      );
    }

    const key = `${rule?.path ?? ""}::${rule?.condition ?? ""}`;
    if (seen.has(key)) {
      errors.push(`${source} has duplicate conditional document rule: ${key}`);
    }
    seen.add(key);
  }

  return errors;
}

function normalizeConditionalDocumentRules(rules: ConditionalDocumentRule[] | undefined): string[] {
  return (rules ?? []).map((rule) => `${rule.path}::${rule.condition}`).sort();
}

export function validateConditionalDocumentAlignment(
  map: WorkflowMapV1,
  gates: QualityGatesV1
): string[] {
  const errors: string[] = [];
  const workflowRules = normalizeConditionalDocumentRules(map.conditionalDocuments);
  const gateRules = normalizeConditionalDocumentRules(gates.conditionalGeneratedDocs);

  const aligned =
    workflowRules.length === gateRules.length &&
    workflowRules.every((rule, index) => rule === gateRules[index]);

  if (!aligned) {
    errors.push(
      "conditional document rules mismatch between workflow-map.conditionalDocuments and quality-gates.conditionalGeneratedDocs"
    );
    errors.push(
      `workflow-map conditional documents: ${workflowRules.length > 0 ? workflowRules.join(", ") : "(none)"}`
    );
    errors.push(
      `quality-gates conditional documents: ${gateRules.length > 0 ? gateRules.join(", ") : "(none)"}`
    );
  }

  return errors;
}

export function validateReferenceFilesExist(gates: QualityGatesV1): string[] {
  const errors: string[] = [];
  for (const relativePath of gates.requiredReferenceFiles) {
    const absolutePath = join(ROOT_DIR, relativePath);
    if (!existsSync(absolutePath)) {
      errors.push(`required reference file not found: ${relativePath}`);
    }
  }
  return errors;
}

export function validateHookScriptsExist(): string[] {
  const errors: string[] = [];
  const hooksTemplatePaths = [
    join(ASSETS_DIR, "hooks", "settings.template.json"),
    join(ASSETS_DIR, "hooks", "settings.template.codex.json"),
  ];
  const hooksDir = join(ASSETS_DIR, "hooks");

  const scriptNames = new Set<string>();
  for (const hooksTemplatePath of hooksTemplatePaths) {
    if (!existsSync(hooksTemplatePath)) {
      errors.push(`hooks template not found: ${hooksTemplatePath}`);
      continue;
    }

    let parsed: unknown;
    try {
      parsed = JSON.parse(readFileSync(hooksTemplatePath, "utf-8"));
    } catch (error) {
      errors.push(`failed to parse hooks template: ${error instanceof Error ? error.message : String(error)}`);
      continue;
    }

    const commands: string[] = [];
    const visit = (node: unknown): void => {
      if (Array.isArray(node)) {
        for (const item of node) visit(item);
        return;
      }
      if (!node || typeof node !== "object") return;

      const candidate = node as Record<string, unknown>;
      if (typeof candidate.command === "string") {
        commands.push(candidate.command);
      }
      for (const value of Object.values(candidate)) {
        visit(value);
      }
    };

    visit(parsed);

    for (const command of commands) {
      const matches = command.matchAll(/bash\s+\.(?:claude|codex)\/hooks\/([A-Za-z0-9._-]+\.sh)/g);
      for (const match of matches) {
        scriptNames.add(match[1]);
      }
    }
  }

  for (const scriptName of scriptNames) {
    const absolutePath = join(hooksDir, scriptName);
    if (!existsSync(absolutePath)) {
      errors.push(`hook script missing for settings reference: assets/hooks/${scriptName}`);
    }
  }

  return errors;
}

export function validateVersionsRegistry(): string[] {
  const errors: string[] = [];
  const versionsPath = join(ASSETS_DIR, "versions.json");

  if (!existsSync(versionsPath)) {
    return ["versions registry missing: assets/versions.json"];
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(readFileSync(versionsPath, "utf-8"));
  } catch (error) {
    return [`failed to parse assets/versions.json: ${error instanceof Error ? error.message : String(error)}`];
  }

  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    return ["assets/versions.json must be a JSON object"];
  }

  const versions = parsed as Record<string, unknown>;

  for (const category of REQUIRED_VERSION_CATEGORIES) {
    if (!(category in versions)) {
      errors.push(`assets/versions.json missing required category: ${category}`);
      continue;
    }
    const value = versions[category];
    if (typeof value !== "object" || value === null || Array.isArray(value)) {
      errors.push(`assets/versions.json category must be object: ${category}`);
    }
  }

  return errors;
}

function toMonthIndex(date: Date): number {
  return date.getUTCFullYear() * 12 + date.getUTCMonth();
}

function parseYearMonth(value: string): { year: number; month: number } | null {
  const match = value.match(/^(\d{4})-(\d{2})$/);
  if (!match) return null;
  const year = Number.parseInt(match[1], 10);
  const month = Number.parseInt(match[2], 10);
  if (!Number.isInteger(year) || !Number.isInteger(month) || month < 1 || month > 12) {
    return null;
  }
  return { year, month };
}

export function validateVersionsFreshnessWarnings(now: Date = new Date()): string[] {
  const warnings: string[] = [];
  const versionsPath = join(ASSETS_DIR, "versions.json");

  if (!existsSync(versionsPath)) {
    return warnings;
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(readFileSync(versionsPath, "utf-8"));
  } catch {
    return warnings;
  }

  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    return warnings;
  }

  const versions = parsed as Record<string, unknown>;
  const lastUpdated = versions._lastUpdated;
  if (typeof lastUpdated !== "string") {
    return warnings;
  }

  const parsedYearMonth = parseYearMonth(lastUpdated);
  if (!parsedYearMonth) {
    warnings.push(
      `assets/versions.json _lastUpdated format should be YYYY-MM (received "${lastUpdated}")`
    );
    return warnings;
  }

  const lastUpdatedMonthIndex = parsedYearMonth.year * 12 + (parsedYearMonth.month - 1);
  const currentMonthIndex = toMonthIndex(now);
  const monthDelta = currentMonthIndex - lastUpdatedMonthIndex;
  if (monthDelta < 0) {
    warnings.push(
      `assets/versions.json _lastUpdated is in the future: ${lastUpdated} (current UTC month ${now.toISOString().slice(0, 7)})`
    );
  } else if (monthDelta > 6) {
    warnings.push(
      `assets/versions.json appears stale: _lastUpdated=${lastUpdated} (${monthDelta} months old, recommended <= 6 months)`
    );
  }

  return warnings;
}

export function validatePartialsExist(): string[] {
  const errors: string[] = [];
  const claudePartialsDir = join(ROOT_DIR, "references", "partials");
  const agentsPartialsDir = join(ROOT_DIR, "references", "partials-agents");

  const verifyDir = (dirPath: string, requiredFiles: string[], label: string): void => {
    if (!existsSync(dirPath)) {
      errors.push(`missing partial directory: ${label}`);
      return;
    }
    const files = new Set(readdirSync(dirPath));
    for (const file of requiredFiles) {
      if (!files.has(file)) {
        errors.push(`${label} missing required file: ${file}`);
      }
    }
  };

  verifyDir(claudePartialsDir, REQUIRED_CLAUDE_PARTIALS, "references/partials");
  verifyDir(agentsPartialsDir, REQUIRED_AGENT_PARTIALS, "references/partials-agents");

  return errors;
}

function assembleDocBuildTarget(targetName: string, target: DocBuildTarget): {
  output: string;
  orderedPartials: string[];
  sourceRootRelative: string;
} {
  const sourceRootRelative = target.sourceDir;
  const sourceRootAbsolute = join(ROOT_DIR, sourceRootRelative);
  const orderPathRelative = join(sourceRootRelative, target.orderFile);
  const orderPathAbsolute = join(ROOT_DIR, orderPathRelative);

  if (!existsSync(sourceRootAbsolute)) {
    throw new Error(`doc-build target "${targetName}" missing sourceDir: ${sourceRootRelative}`);
  }
  if (!existsSync(orderPathAbsolute)) {
    throw new Error(`doc-build target "${targetName}" missing orderFile: ${orderPathRelative}`);
  }

  const orderContent = readFileSync(orderPathAbsolute, "utf-8");
  const orderedPartials = parseAssemblyOrder(orderContent);
  if (orderedPartials.length === 0) {
    throw new Error(`doc-build target "${targetName}" has empty assembly order: ${orderPathRelative}`);
  }

  const seen = new Set<string>();
  const contents: string[] = [];

  for (const partialName of orderedPartials) {
    if (!partialName.endsWith(".partial.md")) {
      throw new Error(
        `doc-build target "${targetName}" order includes non-partial entry: ${partialName}`
      );
    }
    if (seen.has(partialName)) {
      throw new Error(`doc-build target "${targetName}" has duplicate partial: ${partialName}`);
    }
    seen.add(partialName);

    const partialPathRelative = join(sourceRootRelative, partialName);
    const partialPathAbsolute = join(ROOT_DIR, partialPathRelative);
    if (!existsSync(partialPathAbsolute)) {
      throw new Error(`doc-build target "${targetName}" missing partial: ${partialPathRelative}`);
    }

    contents.push(readFileSync(partialPathAbsolute, "utf-8"));
  }

  return {
    output: contents.join(target.separator),
    orderedPartials,
    sourceRootRelative,
  };
}

export function validateDocBuildMap(map: DocBuildMapV1): string[] {
  const errors: string[] = [];

  if (map.version !== "doc-build-map.v1") {
    errors.push(`doc-build-map version mismatch: ${String(map.version)}`);
  }

  if (!map.targets || typeof map.targets !== "object") {
    errors.push("doc-build-map targets must be an object");
    return errors;
  }

  for (const targetName of REQUIRED_DOC_BUILD_TARGETS) {
    const target = map.targets[targetName];
    if (!target) {
      errors.push(`doc-build-map missing required target: ${targetName}`);
      continue;
    }

    if (!target.sourceDir || !target.orderFile || !target.output) {
      errors.push(`doc-build-map target "${targetName}" must define sourceDir/orderFile/output`);
    }
    if (typeof target.separator !== "string") {
      errors.push(`doc-build-map target "${targetName}" separator must be a string`);
    }
  }

  for (const [targetName, target] of Object.entries(map.targets)) {
    if (!target.sourceDir || !target.orderFile || !target.output) {
      errors.push(`doc-build-map target "${targetName}" has invalid empty fields`);
    }
    if (typeof target.conditionalBlocks !== "boolean") {
      errors.push(`doc-build-map target "${targetName}" conditionalBlocks must be boolean`);
    }
  }

  return errors;
}

export function validateGeneratedArtifacts(map: DocBuildMapV1): string[] {
  const errors: string[] = [];

  for (const [targetName, target] of Object.entries(map.targets)) {
    try {
      const assembled = assembleDocBuildTarget(targetName, target);
      const sourceRootAbsolute = join(ROOT_DIR, assembled.sourceRootRelative);
      const outputAbsolute = join(ROOT_DIR, target.output);

      const orphanPartials = readdirSync(sourceRootAbsolute)
        .filter((file: string) => file.endsWith(".partial.md"))
        .filter((file: string) => !assembled.orderedPartials.includes(file));
      if (orphanPartials.length > 0) {
        errors.push(
          `doc-build target "${targetName}" has orphan partials not listed in ${target.orderFile}: ${orphanPartials.join(", ")}`
        );
      }

      if (!existsSync(outputAbsolute)) {
        errors.push(`doc-build target "${targetName}" output missing: ${target.output}`);
        continue;
      }

      const outputContent = readFileSync(outputAbsolute, "utf-8");
      const normalizedOutput = normalizeEol(outputContent);
      const normalizedAssembled = normalizeEol(assembled.output);

      if (normalizedOutput !== normalizedAssembled) {
        const line = firstDiffLine(normalizedOutput, normalizedAssembled);
        errors.push(
          `doc-build drift for target "${targetName}" in ${target.output} (first diff line ${line})`
        );
      }
    } catch (error) {
      errors.push(error instanceof Error ? error.message : String(error));
    }
  }

  return errors;
}

export function validateRequiredChecksAgainstPackageScripts(gates: QualityGatesV1): string[] {
  const errors: string[] = [];
  const packageJsonPath = join(ROOT_DIR, "package.json");

  if (!existsSync(packageJsonPath)) {
    errors.push("package.json not found — cannot validate requiredChecks");
    return errors;
  }

  let pkg: { scripts?: Record<string, string> };
  try {
    pkg = JSON.parse(readFileSync(packageJsonPath, "utf-8"));
  } catch (error) {
    errors.push(
      `failed to parse package.json: ${error instanceof Error ? error.message : String(error)}`
    );
    return errors;
  }

  const scriptNames = new Set(Object.keys(pkg.scripts ?? {}));

  for (const check of gates.requiredChecks) {
    const match = check.match(/^bun run (\S+)/);
    if (!match) {
      errors.push(
        `requiredChecks uses unsupported format "${check}" (expected "bun run <script>")`
      );
      continue;
    }
    const scriptName = match[1];
    if (!scriptNames.has(scriptName)) {
      errors.push(
        `requiredChecks references "bun run ${scriptName}" but package.json has no "${scriptName}" script`
      );
    }
  }

  return errors;
}

function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function containsExactLine(content: string, line: string): boolean {
  return new RegExp(`^${escapeRegex(line)}$`, "m").test(content);
}

export function validateSkillMarkdown(skillMd: string, gates: QualityGatesV1): string[] {
  const errors: string[] = [];

  for (const section of gates.requiredSkillSections) {
    if (!containsExactLine(skillMd, section)) {
      errors.push(`SKILL.md missing required section: ${section}`);
    }
  }

  for (const phrase of gates.requiredPhrases) {
    if (!skillMd.includes(phrase)) {
      errors.push(`SKILL.md missing required phrase: ${phrase}`);
    }
  }

  for (const check of gates.requiredChecks) {
    if (!skillMd.includes(check)) {
      errors.push(`SKILL.md missing required check command: ${check}`);
    }
  }

  return errors;
}

export function validateDesignTemplateCoverage(gates: QualityGatesV1): string[] {
  const errors: string[] = [];
  if (!existsSync(TEMPLATES_MD_PATH)) {
    errors.push("references/templates.md not found — cannot validate designDocRequiredSections coverage");
    return errors;
  }

  const templatesMd = readFileSync(TEMPLATES_MD_PATH, "utf-8");
  for (const section of gates.designDocRequiredSections.sections) {
    if (!templatesMd.includes(section)) {
      errors.push(`references/templates.md missing design section marker: ${section}`);
    }
  }

  return errors;
}

export function validateUpdateModeCompleteness(
  skillMd: string,
  map: WorkflowMapV1,
  pack: InterviewQuestionPackV1
): string[] {
  const errors: string[] = [];

  // Verify SKILL.md contains Update Phase 3.7 (user annotation review)
  if (!skillMd.includes("### Update Phase 3.7")) {
    errors.push("SKILL.md missing Update Phase 3.7 (user annotation review)");
  }

  // Verify interview-question-pack update arrays are non-empty and each type has at least 1 round
  for (const updateType of REQUIRED_UPDATE_TYPES) {
    const rounds = pack.update[updateType];
    if (!Array.isArray(rounds) || rounds.length === 0) {
      errors.push(`interview-question-pack update.${updateType} must have at least 1 round`);
    }
  }

  // Verify workflow-map updatePhaseOrder contains the review step (phase-3.7)
  if (!map.updatePhaseOrder.includes("update-phase-3.7-user-annotation-review")) {
    errors.push("workflow-map updatePhaseOrder missing update-phase-3.7-user-annotation-review");
  }

  // Verify workflow-map updatePhaseOrder contains the documentation review step
  if (!map.updatePhaseOrder.includes("update-phase-3.5-documentation-review")) {
    errors.push("workflow-map updatePhaseOrder missing update-phase-3.5-documentation-review");
  }
  if (!skillMd.includes("F0-F8")) {
    errors.push("SKILL.md update New Feature round range must reference F0-F8");
  }

  return errors;
}

export function verifySkillContract(): VerificationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  const run = (label: string, fn: () => void): void => {
    try {
      fn();
    } catch (error) {
      errors.push(`${label} failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  };
  const runWarning = (fn: () => void): void => {
    try {
      fn();
    } catch {
      // warnings are best-effort only
    }
  };

  let workflowMap: WorkflowMapV1 | undefined;
  let interviewPack: InterviewQuestionPackV1 | undefined;
  let qualityGates: QualityGatesV1 | undefined;
  let docBuildMap: DocBuildMapV1 | undefined;
  let skillMd: string | undefined;

  run("load workflow-map", () => {
    workflowMap = loadWorkflowMap();
  });
  run("load interview-question-pack", () => {
    interviewPack = loadInterviewQuestionPack();
  });
  run("load quality-gates", () => {
    qualityGates = loadQualityGates();
  });
  run("load doc-build-map", () => {
    docBuildMap = loadDocBuildMap();
  });
  run("read SKILL.md", () => {
    skillMd = readSkillMarkdown();
  });

  if (workflowMap) {
    run("validate workflow-map", () => {
      errors.push(...validateWorkflowMap(workflowMap!));
    });
  }
  if (interviewPack) {
    run("validate interview-question-pack", () => {
      errors.push(...validateInterviewQuestionPack(interviewPack!));
    });
  }
  if (qualityGates) {
    run("validate quality-gates", () => {
      errors.push(...validateQualityGates(qualityGates!));
    });
    run("validate reference files", () => {
      errors.push(...validateReferenceFilesExist(qualityGates!));
    });
    run("validate required checks against package scripts", () => {
      errors.push(...validateRequiredChecksAgainstPackageScripts(qualityGates!));
    });
    run("validate design template coverage", () => {
      errors.push(...validateDesignTemplateCoverage(qualityGates!));
    });
  }
  if (docBuildMap) {
    run("validate doc-build-map", () => {
      errors.push(...validateDocBuildMap(docBuildMap!));
    });
    run("validate generated artifacts", () => {
      errors.push(...validateGeneratedArtifacts(docBuildMap!));
    });
  }
  if (skillMd && qualityGates) {
    run("validate SKILL markdown contract", () => {
      errors.push(...validateSkillMarkdown(skillMd!, qualityGates!));
    });
  }
  if (workflowMap && qualityGates) {
    run("validate conditional document alignment", () => {
      errors.push(...validateConditionalDocumentAlignment(workflowMap!, qualityGates!));
    });
  }
  if (skillMd && workflowMap && interviewPack) {
    run("validate update mode completeness", () => {
      errors.push(...validateUpdateModeCompleteness(skillMd!, workflowMap!, interviewPack!));
    });
  }

  run("validate hook scripts", () => {
    errors.push(...validateHookScriptsExist());
  });
  run("validate versions registry", () => {
    errors.push(...validateVersionsRegistry());
  });
  runWarning(() => {
    warnings.push(...validateVersionsFreshnessWarnings());
  });
  run("validate partial templates", () => {
    errors.push(...validatePartialsExist());
  });

  return { errors, warnings };
}

export function formatVerificationResult(result: VerificationResult): string {
  if (result.errors.length === 0) {
    if (result.warnings.length === 0) {
      return "Contract check passed: no drift detected.";
    }
    return [
      "Contract check passed with warnings:",
      ...result.warnings.map((warning) => `- [warning] ${warning}`),
    ].join("\n");
  }

  const lines = ["Contract check failed:", ...result.errors.map((error) => `- ${error}`)];
  if (result.warnings.length > 0) {
    lines.push(...result.warnings.map((warning) => `- [warning] ${warning}`));
  }
  return lines.join("\n");
}
