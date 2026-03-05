import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { parseAssemblyOrder } from "./lib/parse-assembly-order";
import { firstDiffLine, normalizeEol } from "./lib/text-utils";
import type { DocBuildMapV1, DocBuildTarget } from "./skill-contract";

type Mode = "write" | "check";

const ROOT_DIR = join(import.meta.dir, "..");
const MAP_PATH = join(ROOT_DIR, "assets", "doc-build-map.v1.json");

function readUtf8(relativePath: string): string {
  const absolutePath = join(ROOT_DIR, relativePath);
  if (!existsSync(absolutePath)) {
    throw new Error(`Missing file: ${relativePath}`);
  }
  try {
    return readFileSync(absolutePath, "utf-8");
  } catch (error) {
    throw new Error(
      `Failed to read file "${relativePath}": ${error instanceof Error ? error.message : String(error)}`
    );
  }
}

function loadDocBuildMap(): DocBuildMapV1 {
  const raw = readUtf8("assets/doc-build-map.v1.json");
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch (error) {
    throw new Error(
      `Failed to parse assets/doc-build-map.v1.json: ${error instanceof Error ? error.message : String(error)}`
    );
  }

  const map = parsed as Partial<DocBuildMapV1>;
  if (map.version !== "doc-build-map.v1") {
    throw new Error(`Invalid doc-build-map version: ${String(map.version)}`);
  }
  if (!map.targets || typeof map.targets !== "object") {
    throw new Error("doc-build-map targets must be an object");
  }

  return map as DocBuildMapV1;
}

function assembleTarget(targetName: string, target: DocBuildTarget): string {
  const sourceRoot = target.sourceDir;
  const orderPath = join(sourceRoot, target.orderFile);
  const orderRaw = readUtf8(orderPath);
  const orderedPartials = parseAssemblyOrder(orderRaw);

  if (orderedPartials.length === 0) {
    throw new Error(`Target "${targetName}" has empty assembly order: ${orderPath}`);
  }

  const seen = new Set<string>();
  const contents: string[] = [];

  for (const partial of orderedPartials) {
    if (!partial.endsWith(".partial.md")) {
      throw new Error(`Target "${targetName}" has invalid partial name: ${partial}`);
    }
    if (seen.has(partial)) {
      throw new Error(`Target "${targetName}" has duplicate partial in order: ${partial}`);
    }
    seen.add(partial);

    const partialPath = join(sourceRoot, partial);
    contents.push(readUtf8(partialPath));
  }

  return contents.join(target.separator);
}

function parseArgValue(args: string[], key: "--target" | "--mode"): string | undefined {
  const idx = args.indexOf(key);
  if (idx === -1) return undefined;
  if (idx + 1 >= args.length) return undefined;
  const value = args[idx + 1];
  if (value.startsWith("--")) return undefined;
  return value;
}

function main(): void {
  const args = process.argv.slice(2);
  const verbose = args.includes("--verbose");
  const targetArg = parseArgValue(args, "--target");
  const modeArg = parseArgValue(args, "--mode");

  if (!targetArg) {
    throw new Error("Missing required argument: --target <skill|interview|templates|review|all>");
  }
  if (!modeArg || (modeArg !== "write" && modeArg !== "check")) {
    throw new Error("Missing or invalid argument: --mode <write|check>");
  }

  const map = loadDocBuildMap();
  const availableTargets = Object.keys(map.targets);
  const selectedTargets =
    targetArg === "all"
      ? availableTargets
      : availableTargets.includes(targetArg)
        ? [targetArg]
        : [];

  if (selectedTargets.length === 0) {
    throw new Error(
      `Unknown target "${targetArg}". Available targets: ${availableTargets.join(", ")}, all`
    );
  }

  const driftErrors: string[] = [];
  const mode = modeArg as Mode;

  for (const targetName of selectedTargets) {
    const target = map.targets[targetName];
    const assembled = assembleTarget(targetName, target);
    const outputAbsolutePath = join(ROOT_DIR, target.output);

    if (mode === "write") {
      writeFileSync(outputAbsolutePath, assembled, "utf-8");
      if (verbose) {
        console.log(`[write] ${targetName} -> ${target.output}`);
      }
      continue;
    }

    if (!existsSync(outputAbsolutePath)) {
      driftErrors.push(`[${targetName}] Missing output file: ${target.output}`);
      continue;
    }

    const current = readFileSync(outputAbsolutePath, "utf-8");
    if (normalizeEol(current) !== normalizeEol(assembled)) {
      const line = firstDiffLine(normalizeEol(current), normalizeEol(assembled));
      driftErrors.push(`[${targetName}] Drift detected in ${target.output} (first diff at line ${line})`);
    } else if (verbose) {
      console.log(`[check] ${targetName} OK`);
    }
  }

  if (driftErrors.length > 0) {
    for (const error of driftErrors) {
      console.error(error);
    }
    process.exit(1);
  }
}

main();
