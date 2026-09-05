/**
 * Adapter: analysis/site_data/final_ranking.json (+ analysis/final_ranking.json)
 * -> final ranked rows.
 *
 * This is the authoritative consolidated ranking produced by the analysis
 * pipeline (scripts/build_final_ranking.py). The site displays ranks exactly
 * as recorded in the artifact and NEVER re-sorts, re-scores, or re-derives
 * them. All 2,500 corpus slugs are present. Stage values: S2 (live-tested),
 * S1 (original two-round blind review), S1R (re-scored 2026-09-05 after the
 * video-evidence defect correction; see DEVIATIONS.md).
 */
import fs from 'node:fs';
import { repoPath } from './reviewer-corpus';

export interface FinalRow {
  slug: string;
  rank: number;
  title: string;
  stage: 'S1' | 'S1R' | 'S2';
  leverage: number;
  execution: number;
  impact: number;
  creativity: number;
  aggregate: number;
  confidence: number | null;
  adjudication: string | null;
  webmcpVerification: string;
  screenshot: string | null;
  /** rescore provenance from the rich artifact (round, prior/new aggregate, audio_neutral) */
  rescored: { round: string; priorAggregate: number; newAggregate: number; audioNeutral: boolean } | null;
  /** evidence flags from the rich artifact */
  hasVideoFrames: boolean;
  hadLiveObservation: boolean;
  hadProbe: boolean;
}

export function hasFinal(): boolean {
  return fs.existsSync(repoPath('analysis', 'site_data', 'final_ranking.json'));
}

interface RichRow {
  final_rank: number;
  slug: string;
  stage: string;
  scores: Record<string, number>;
  aggregate: number;
  verification: string;
  adjudication: string;
  confidence: number;
  title: string;
  devpost_url: string;
  screenshot: string;
  evidence: {
    live_observation?: boolean;
    video_frames?: boolean;
    probe?: boolean;
    rescored?: { round: string; prior_aggregate: number; new_aggregate: number; audio_neutral?: boolean };
  };
}

function toFinalRow(row: RichRow): FinalRow {
  const rs = row.evidence?.rescored;
  return {
    slug: row.slug,
    rank: row.final_rank,
    title: row.title || row.slug,
    // S1R = re-scored with corrected evidence; first-class alongside S1/S2
    stage: row.stage === 'S2' ? 'S2' : row.stage === 'S1R' ? 'S1R' : 'S1',
    leverage: row.scores.leverage,
    execution: row.scores.execution,
    impact: row.scores.impact,
    creativity: row.scores.creativity,
    aggregate: row.aggregate,
    confidence: typeof row.confidence === 'number' ? row.confidence : null,
    adjudication: row.adjudication || null,
    webmcpVerification: row.verification ?? 'UNVERIFIED',
    screenshot: row.screenshot || null,
    rescored: rs
      ? {
          round: rs.round,
          priorAggregate: rs.prior_aggregate,
          newAggregate: rs.new_aggregate,
          audioNeutral: rs.audio_neutral === true,
        }
      : null,
    hasVideoFrames: row.evidence?.video_frames === true,
    hadLiveObservation: row.evidence?.live_observation === true,
    hadProbe: row.evidence?.probe === true,
  };
}

/** Prefer the rich artifact (per-project provenance); fall back to site_data. */
export function loadFinal(): Map<string, FinalRow> {
  const map = new Map<string, FinalRow>();
  const rich = repoPath('analysis', 'final_ranking.json');
  const siteData = repoPath('analysis', 'site_data', 'final_ranking.json');
  if (fs.existsSync(rich)) {
    const d = JSON.parse(fs.readFileSync(rich, 'utf8'));
    for (const row of d.ranking as RichRow[]) map.set(row.slug, toFinalRow(row));
    return map;
  }
  if (!fs.existsSync(siteData)) return map;
  for (const row of JSON.parse(fs.readFileSync(siteData, 'utf8')) as any[]) {
    map.set(row.slug, {
      slug: row.slug,
      rank: typeof row.rank === 'number' ? row.rank : Number(row.rank),
      title: row.title || row.slug,
      stage: row.stage === 'S2' ? 'S2' : row.stage === 'S1R' ? 'S1R' : 'S1',
      leverage: row.leverage,
      execution: row.execution,
      impact: row.impact,
      creativity: row.creativity,
      aggregate: row.aggregate,
      confidence: typeof row.confidence === 'number' ? row.confidence : null,
      adjudication: null,
      webmcpVerification: row.webmcp_verification ?? 'UNVERIFIED',
      screenshot: row.screenshot || null,
      rescored: null,
      hasVideoFrames: false,
      hadLiveObservation: false,
      hadProbe: false,
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
