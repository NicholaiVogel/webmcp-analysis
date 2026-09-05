/**
 * Adapter: analysis/site_data/final_ranking.json (+ analysis/FINAL_RANKING.csv)
 * -> final ranked rows.
 *
 * This is the authoritative Stage-4-consolidated ranking produced by the
 * analysis pipeline. The site displays ranks exactly as recorded in the
 * artifact and NEVER re-sorts, re-scores, or re-derives them. 2,492 of the
 * 2,500 corpus slugs are present; the 8 absent slugs are pipeline exclusions
 * and simply have no final row (their Stage 1 material remains available via
 * the corpus adapter, clearly labeled as not-final-ranked).
 */
import fs from 'node:fs';
import { repoPath } from './reviewer-corpus';

export interface FinalRow {
  slug: string;
  rank: number;
  title: string;
  stage: 'S1' | 'S2';
  leverage: number;
  execution: number;
  impact: number;
  creativity: number;
  aggregate: number;
  webmcpVerification: string;
  screenshot: string | null;
}

export function hasFinal(): boolean {
  return fs.existsSync(repoPath('analysis', 'site_data', 'final_ranking.json'));
}

export function loadFinal(): Map<string, FinalRow> {
  const map = new Map<string, FinalRow>();
  const file = repoPath('analysis', 'site_data', 'final_ranking.json');
  if (!fs.existsSync(file)) return map;
  for (const row of JSON.parse(fs.readFileSync(file, 'utf8')) as any[]) {
    map.set(row.slug, {
      slug: row.slug,
      rank: typeof row.rank === 'number' ? row.rank : Number(row.rank),
      title: row.title || row.slug,
      stage: row.stage === 'S2' ? 'S2' : 'S1',
      leverage: row.leverage,
      execution: row.execution,
      impact: row.impact,
      creativity: row.creativity,
      aggregate: row.aggregate,
      webmcpVerification: row.webmcp_verification ?? 'UNVERIFIED',
      screenshot: row.screenshot || null,
    });
  }
  return map;
}

/** Probe capture paths (live-product evidence from Stage 2 interactive testing). */
export function probeCaptures(slug: string): { before: string | null; after: string | null } {
  const dir = repoPath('probes', 'obs');
  const before = `${dir}/${slug}-before.png`;
  const after = `${dir}/${slug}-after.png`;
  return {
    before: fs.existsSync(before) ? before : null,
    after: fs.existsSync(after) ? after : null,
  };
}
