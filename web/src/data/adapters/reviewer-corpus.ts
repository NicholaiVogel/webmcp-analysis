/**
 * Adapter: analysis/reviewer_corpus.jsonl -> sanitized corpus facts.
 * Zero judgment fields exist in this artifact by design (assert_clean.py gates it).
 */
import fs from 'node:fs';
import path from 'node:path';

export interface CorpusRow {
  slug: string;
  title: string;
  devpost_url: string | null;
  pitch: string | null;
  about_excerpt: string | null;
  has_public_repo: boolean;
  has_demo_link: boolean;
  demo_alive: string | null;
  gallery_image_count: number | null;
  has_video: boolean;
  video_duration_secs: number | null;
  video_title: string | null;
  video_frame_sheets: string[];
}

const REPO = '/mnt/work/webmcp-analysis';

export function repoPath(...parts: string[]): string {
  return path.join(REPO, ...parts);
}

export function loadCorpus(): Map<string, CorpusRow> {
  const file = repoPath('analysis', 'reviewer_corpus.jsonl');
  const map = new Map<string, CorpusRow>();
  for (const line of fs.readFileSync(file, 'utf8').split('\n')) {
    if (!line.trim()) continue;
    const r = JSON.parse(line);
    map.set(r.slug, {
      slug: r.slug,
      title: r.title ?? r.slug,
      devpost_url: r.devpost_url ?? null,
      pitch: r.pitch || null,
      about_excerpt: r.about_excerpt || null,
      has_public_repo: r.has_public_repo === true,
      has_demo_link: r.has_demo_link === true,
      demo_alive: r.demo_alive || null,
      gallery_image_count: typeof r.gallery_image_count === 'number' ? r.gallery_image_count : null,
      has_video: r.has_video === true,
      video_duration_secs: r.video_duration_secs ? Number(r.video_duration_secs) : null,
      video_title: r.video_title || null,
      video_frame_sheets: Array.isArray(r.video_frame_sheets) ? r.video_frame_sheets : [],
    });
  }
  return map;
}
