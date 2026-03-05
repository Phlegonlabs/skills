export function parseAssemblyOrder(content: string): string[] {
  const partials: string[] = [];

  for (const rawLine of content.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (line.length === 0) continue;
    if (line.startsWith("#")) continue;
    if (line.startsWith("Condition blocks supported")) continue;
    if (line.startsWith("- ")) continue;

    const match = line.match(/^\d+\.\s+(.+)$/);
    if (!match) continue;

    partials.push(match[1].trim());
  }

  return partials;
}
