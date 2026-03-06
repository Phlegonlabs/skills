import { spawnSync } from "child_process";

function quoteShellArg(value: string): string {
  if (value.length === 0) return "''";
  return `'${value.replace(/'/g, `'\\''`)}'`;
}

export function chmodPlusX(cwd: string, paths: string[]): number | null {
  const command = ["chmod", "+x", ...paths].map(quoteShellArg).join(" ");
  const result = spawnSync("bash", ["-lc", command], {
    cwd,
    encoding: "utf-8",
  });
  return result.status;
}

export function normalizeEol(value: string): string {
  return value.replace(/\r\n/g, "\n");
}
