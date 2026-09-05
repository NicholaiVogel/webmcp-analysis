/**
 * Adapter: raw/parsed.jsonl -> public links (live URL, repository, video).
 * Link lists come from the scraped Devpost pages; classification is mechanical
 * (github.com -> repository, video platform -> video, else first non-image link
 * that is not a social/dead giveaway domain). No judgment is applied here.
 */
import fs from 'node:fs';
import { repoPath } from './reviewer-corpus';

export interface ParsedLinks {
  live: string | null;
  repository: string | null;
  video: string | null;
}

const SOCIAL = /(discord\.com|linkedin\.com|twitter\.com|x\.com|t\.me|reddit\.com)/i;
const VIDEO = /(youtube\.com|youtu\.be|vimeo\.com|loom\.com)/i;

/**
 * Devpost lists demo videos as /embed/ iframe sources, which do not play when
 * opened directly. Rewrite the known embed shapes to watchable URLs. Unknown
 * shapes pass through untouched. Mechanical normalization only.
 */
export function playableVideoUrl(url: string): string {
  let out = url.replace(/&amp;/g, '&');
  const yt = out.match(/youtube\.com\/embed\/([A-Za-z0-9_-]{6,})/i);
  if (yt) return `https://www.youtube.com/watch?v=${yt[1]}`;
  const vimeo = out.match(/vimeo\.com\/video\/(\d+)/i);
  if (vimeo) return `https://vimeo.com/${vimeo[1]}`;
  return out;
}

export function loadParsedLinks(): Map<string, ParsedLinks> {
  const file = repoPath('raw', 'parsed.jsonl');
  const map = new Map<string, ParsedLinks>();
  if (!fs.existsSync(file)) return map;
  for (const line of fs.readFileSync(file, 'utf8').split('\n')) {
    if (!line.trim()) continue;
    const r = JSON.parse(line);
    const github: string[] = Array.isArray(r.github) ? r.github : [];
    const demo: string[] = Array.isArray(r.demo_links) ? r.demo_links : [];
    const links: string[] = Array.isArray(r.links) ? r.links : [];
    const videoEntry: string | undefined = typeof r.video === 'string' && r.video ? r.video : undefined;

    const repository = github[0] ?? null;
    let video: string | null = videoEntry ?? null;
    let live: string | null = null;
    if (!video) {
      const inDemo = new Set(demo);
      for (const l of [...demo, ...links]) {
        if (VIDEO.test(l)) { video = l; break; }
      }
      if (!live) {
        live =
          demo.find((l) => !SOCIAL.test(l) && !VIDEO.test(l) && !/^https?:\/\/[^/]*(devpost|cloudfront)\./i.test(l)) ??
          links.find((l) => !SOCIAL.test(l) && !VIDEO.test(l) && !inDemo.has(l) && !/\.(png|jpg|jpeg|webp|gif)$/i.test(l) && !/^https?:\/\/[^/]*(devpost|cloudfront)\./i.test(l)) ??
          null;
      }
    }
    if (!live) live = null;
    map.set(r.slug, { live, repository, video });
  }
  return map;
}
