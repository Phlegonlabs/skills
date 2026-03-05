export function normalizeEol(content: string): string {
  return content.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
}

export function firstDiffLine(a: string, b: string): number {
  const aLines = a.split("\n");
  const bLines = b.split("\n");
  const maxLen = Math.max(aLines.length, bLines.length);
  for (let i = 0; i < maxLen; i += 1) {
    if ((aLines[i] ?? "") !== (bLines[i] ?? "")) {
      return i + 1;
    }
  }
  return maxLen + 1;
}
