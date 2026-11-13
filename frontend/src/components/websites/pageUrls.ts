export const MAX_PAGES_PER_WEBSITE = 50;

export function parsePageUrls(text: string | undefined): string[] {
  if (!text) return [];
  const urls = text
    .split(/[\s,]+/)
    .map((u) => u.trim())
    .filter(Boolean);
  return Array.from(new Set(urls));
}

function isHttpUrl(value: string): boolean {
  try {
    const { protocol } = new URL(value);
    return protocol === "http:" || protocol === "https:";
  } catch {
    return false;
  }
}

export function validatePageUrls(text: string | undefined): string | true {
  const urls = parsePageUrls(text);
  if (urls.length > MAX_PAGES_PER_WEBSITE) {
    return `You can add up to ${MAX_PAGES_PER_WEBSITE} pages`;
  }
  const invalid = urls.find((u) => !isHttpUrl(u));
  return invalid ? `Invalid URL: ${invalid}` : true;
}
