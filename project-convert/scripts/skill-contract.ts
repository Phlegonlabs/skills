import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

type SkillMode = "init" | "update" | "convert";

export interface SplitWorkflowMapV1 {
  version: "split-workflow-map.v1";
  mode: SkillMode;
  requiredDocuments: string[];
  requiredChecks: string[];
  requiredProtocolReference: string;
  hookInstaller: string;
}

export interface SplitInterviewQuestionPackV1 {
  version: "split-interview-question-pack.v1";
  mode: SkillMode;
  requiredRoundSets: Record<string, string[]>;
  rules: {
    maxQuestionsPerRound: number;
    followUpCaps: Record<string, number>;
  };
}

export interface SplitQualityGatesV1 {
  version: "split-quality-gates.v1";
  requiredReferenceFiles: string[];
  requiredSkillSections: string[];
  requiredPhrases: string[];
  requiredChecks: string[];
}

export interface VerificationResult {
  errors: string[];
  warnings: string[];
}

export const ROOT_DIR = join(import.meta.dir, "..");
const ASSETS_DIR = join(ROOT_DIR, "assets");
const SKILL_MD_PATH = join(ROOT_DIR, "SKILL.md");
const REQUIRED_MODE_SET = new Set<SkillMode>(["init", "update", "convert"]);
const REQUIRED_BASE_DOCS = ["docs/architecture.md", "docs/plans.md"];
const REQUIRED_CHECKS = ["bun run contract:check", "bun run typecheck", "bun run test"];

function loadJsonFile<T>(absolutePath: string, label: string): T {
  if (!existsSync(absolutePath)) {
    throw new Error(`Missing ${label}: ${absolutePath}`);
  }
  try {
    return JSON.parse(readFileSync(absolutePath, "utf-8")) as T;
  } catch (error) {
    throw new Error(
      `Invalid JSON in ${label}: ${error instanceof Error ? error.message : String(error)}`
    );
  }
}

export function loadWorkflowMap(): SplitWorkflowMapV1 {
  return loadJsonFile<SplitWorkflowMapV1>(
    join(ASSETS_DIR, "workflow-map.v1.json"),
    "assets/workflow-map.v1.json"
  );
}

export function loadInterviewQuestionPack(): SplitInterviewQuestionPackV1 {
  return loadJsonFile<SplitInterviewQuestionPackV1>(
    join(ASSETS_DIR, "interview-question-pack.v1.json"),
    "assets/interview-question-pack.v1.json"
  );
}

export function loadQualityGates(): SplitQualityGatesV1 {
  return loadJsonFile<SplitQualityGatesV1>(
    join(ASSETS_DIR, "quality-gates.v1.json"),
    "assets/quality-gates.v1.json"
  );
}

export function readSkillMarkdown(): string {
  if (!existsSync(SKILL_MD_PATH)) {
    throw new Error(`Missing SKILL.md: ${SKILL_MD_PATH}`);
  }
  return readFileSync(SKILL_MD_PATH, "utf-8");
}

function isSkillMode(value: string): value is SkillMode {
  return REQUIRED_MODE_SET.has(value as SkillMode);
}

export function validateWorkflowMap(map: SplitWorkflowMapV1): string[] {
  const errors: string[] = [];

  if (map.version !== "split-workflow-map.v1") {
    errors.push(`workflow-map version mismatch: ${String(map.version)}`);
  }
  if (!isSkillMode(String(map.mode))) {
    errors.push(`workflow-map mode must be one of init/update/convert (received "${String(map.mode)}")`);
  }
  if (!Array.isArray(map.requiredDocuments) || map.requiredDocuments.length === 0) {
    errors.push("workflow-map requiredDocuments must not be empty");
  } else {
    for (const doc of REQUIRED_BASE_DOCS) {
      if (!map.requiredDocuments.includes(doc)) {
        errors.push(`workflow-map requiredDocuments missing ${doc}`);
      }
    }
  }
  if (!Array.isArray(map.requiredChecks) || map.requiredChecks.length === 0) {
    errors.push("workflow-map requiredChecks must not be empty");
  } else {
    for (const check of REQUIRED_CHECKS) {
      if (!map.requiredChecks.includes(check)) {
        errors.push(`workflow-map requiredChecks missing "${check}"`);
      }
    }
  }
  if (map.requiredProtocolReference !== "references/interview.md") {
    errors.push(
      `workflow-map requiredProtocolReference must be "references/interview.md" (received "${String(
        map.requiredProtocolReference
      )}")`
    );
  }
  if (map.hookInstaller !== "scripts/setup-hooks.sh") {
    errors.push(
      `workflow-map hookInstaller must be "scripts/setup-hooks.sh" (received "${String(map.hookInstaller)}")`
    );
  }

  return errors;
}

export function validateInterviewQuestionPack(pack: SplitInterviewQuestionPackV1): string[] {
  const errors: string[] = [];

  if (pack.version !== "split-interview-question-pack.v1") {
    errors.push(`interview-question-pack version mismatch: ${String(pack.version)}`);
  }
  if (!isSkillMode(String(pack.mode))) {
    errors.push(
      `interview-question-pack mode must be one of init/update/convert (received "${String(pack.mode)}")`
    );
  }

  if (
    !pack.requiredRoundSets ||
    typeof pack.requiredRoundSets !== "object" ||
    Array.isArray(pack.requiredRoundSets)
  ) {
    errors.push("interview-question-pack requiredRoundSets must be an object");
    return errors;
  }

  const entries = Object.entries(pack.requiredRoundSets);
  if (entries.length === 0) {
    errors.push("interview-question-pack requiredRoundSets must not be empty");
  }

  for (const [roundSetName, rounds] of entries) {
    if (!Array.isArray(rounds) || rounds.length === 0) {
      errors.push(`interview-question-pack requiredRoundSets.${roundSetName} must not be empty`);
    }
  }

  if (pack.rules.maxQuestionsPerRound !== 2) {
    errors.push("interview-question-pack rules.maxQuestionsPerRound must be 2");
  }
  if (
    !pack.rules.followUpCaps ||
    typeof pack.rules.followUpCaps !== "object" ||
    Array.isArray(pack.rules.followUpCaps) ||
    Object.keys(pack.rules.followUpCaps).length === 0
  ) {
    errors.push("interview-question-pack rules.followUpCaps must not be empty");
  } else {
    for (const [key, value] of Object.entries(pack.rules.followUpCaps)) {
      if (!Number.isInteger(value) || value <= 0) {
        errors.push(`interview-question-pack rules.followUpCaps.${key} must be a positive integer`);
      }
    }
  }

  if (pack.mode === "init") {
    const rounds = pack.requiredRoundSets.init ?? [];
    for (const roundId of ["2.8", "R10.7", "R14"]) {
      if (!rounds.includes(roundId)) {
        errors.push(`interview-question-pack init rounds missing ${roundId}`);
      }
    }
  }

  if (pack.mode === "update") {
    const newFeature = pack.requiredRoundSets.new_feature ?? [];
    const bugFix = pack.requiredRoundSets.bug_fix ?? [];
    const change = pack.requiredRoundSets.change ?? [];

    for (const roundId of ["F0", "F8"]) {
      if (!newFeature.includes(roundId)) {
        errors.push(`interview-question-pack update.new_feature missing ${roundId}`);
      }
    }
    for (const roundId of ["B1", "B3"]) {
      if (!bugFix.includes(roundId)) {
        errors.push(`interview-question-pack update.bug_fix missing ${roundId}`);
      }
    }
    for (const roundId of ["C1", "C5"]) {
      if (!change.includes(roundId)) {
        errors.push(`interview-question-pack update.change missing ${roundId}`);
      }
    }
  }

  if (pack.mode === "convert") {
    const baseline = pack.requiredRoundSets.baseline_conversion ?? [];
    const upgrade = pack.requiredRoundSets.upgrade_conversion ?? [];

    for (const roundId of ["CV0", "CV3"]) {
      if (!baseline.includes(roundId)) {
        errors.push(`interview-question-pack convert.baseline_conversion missing ${roundId}`);
      }
    }
    for (const roundId of ["CV0", "CU4"]) {
      if (!upgrade.includes(roundId)) {
        errors.push(`interview-question-pack convert.upgrade_conversion missing ${roundId}`);
      }
    }
  }

  return errors;
}

export function validateQualityGates(gates: SplitQualityGatesV1): string[] {
  const errors: string[] = [];
  if (gates.version !== "split-quality-gates.v1") {
    errors.push(`quality-gates version mismatch: ${String(gates.version)}`);
  }
  if (!Array.isArray(gates.requiredReferenceFiles) || gates.requiredReferenceFiles.length === 0) {
    errors.push("quality-gates requiredReferenceFiles must not be empty");
  }
  if (!Array.isArray(gates.requiredSkillSections) || gates.requiredSkillSections.length === 0) {
    errors.push("quality-gates requiredSkillSections must not be empty");
  }
  if (!Array.isArray(gates.requiredPhrases) || gates.requiredPhrases.length === 0) {
    errors.push("quality-gates requiredPhrases must not be empty");
  }
  if (!Array.isArray(gates.requiredChecks) || gates.requiredChecks.length === 0) {
    errors.push("quality-gates requiredChecks must not be empty");
  } else {
    for (const check of REQUIRED_CHECKS) {
      if (!gates.requiredChecks.includes(check)) {
        errors.push(`quality-gates requiredChecks missing "${check}"`);
      }
    }
  }
  return errors;
}

export function validateReferenceFilesExist(gates: SplitQualityGatesV1): string[] {
  const errors: string[] = [];
  for (const relativePath of gates.requiredReferenceFiles) {
    const absolutePath = join(ROOT_DIR, relativePath);
    if (!existsSync(absolutePath)) {
      errors.push(`required reference file not found: ${relativePath}`);
    }
  }
  return errors;
}

export function validateRequiredChecksAgainstPackageScripts(gates: SplitQualityGatesV1): string[] {
  const errors: string[] = [];
  const packageJsonPath = join(ROOT_DIR, "package.json");

  if (!existsSync(packageJsonPath)) {
    errors.push("package.json not found — cannot validate requiredChecks");
    return errors;
  }

  let packageJson: { scripts?: Record<string, string> };
  try {
    packageJson = JSON.parse(readFileSync(packageJsonPath, "utf-8"));
  } catch (error) {
    errors.push(
      `failed to parse package.json: ${error instanceof Error ? error.message : String(error)}`
    );
    return errors;
  }

  const scriptNames = new Set(Object.keys(packageJson.scripts ?? {}));
  for (const check of gates.requiredChecks) {
    const match = check.match(/^bun run (\S+)$/);
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

export function validateSkillMarkdown(skillMarkdown: string, gates: SplitQualityGatesV1): string[] {
  const errors: string[] = [];

  for (const section of gates.requiredSkillSections) {
    if (!containsExactLine(skillMarkdown, section)) {
      errors.push(`SKILL.md missing required section: ${section}`);
    }
  }
  for (const phrase of gates.requiredPhrases) {
    if (!skillMarkdown.includes(phrase)) {
      errors.push(`SKILL.md missing required phrase: ${phrase}`);
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
      errors.push(
        `failed to parse hooks template: ${error instanceof Error ? error.message : String(error)}`
      );
      continue;
    }

    const commands: string[] = [];
    const visit = (node: unknown): void => {
      if (Array.isArray(node)) {
        for (const item of node) {
          visit(item);
        }
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

export function validateModeConsistency(
  workflowMap: SplitWorkflowMapV1,
  questionPack: SplitInterviewQuestionPackV1
): string[] {
  if (workflowMap.mode === questionPack.mode) {
    return [];
  }
  return [
    `mode mismatch: workflow-map mode is "${workflowMap.mode}" but interview-question-pack mode is "${questionPack.mode}"`,
  ];
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

  let workflowMap: SplitWorkflowMapV1 | undefined;
  let questionPack: SplitInterviewQuestionPackV1 | undefined;
  let qualityGates: SplitQualityGatesV1 | undefined;
  let skillMarkdown: string | undefined;

  run("load workflow-map", () => {
    workflowMap = loadWorkflowMap();
  });
  run("load interview-question-pack", () => {
    questionPack = loadInterviewQuestionPack();
  });
  run("load quality-gates", () => {
    qualityGates = loadQualityGates();
  });
  run("read SKILL.md", () => {
    skillMarkdown = readSkillMarkdown();
  });

  if (workflowMap) {
    run("validate workflow-map", () => {
      errors.push(...validateWorkflowMap(workflowMap!));
    });
  }
  if (questionPack) {
    run("validate interview-question-pack", () => {
      errors.push(...validateInterviewQuestionPack(questionPack!));
    });
  }
  if (qualityGates) {
    run("validate quality-gates", () => {
      errors.push(...validateQualityGates(qualityGates!));
    });
    run("validate required reference files", () => {
      errors.push(...validateReferenceFilesExist(qualityGates!));
    });
    run("validate required checks against package scripts", () => {
      errors.push(...validateRequiredChecksAgainstPackageScripts(qualityGates!));
    });
  }
  if (skillMarkdown && qualityGates) {
    run("validate SKILL markdown contract", () => {
      errors.push(...validateSkillMarkdown(skillMarkdown!, qualityGates!));
    });
  }
  if (workflowMap && questionPack) {
    run("validate mode consistency", () => {
      errors.push(...validateModeConsistency(workflowMap!, questionPack!));
    });
  }
  run("validate hook scripts", () => {
    errors.push(...validateHookScriptsExist());
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
