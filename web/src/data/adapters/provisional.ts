/**
 * Adapter: analysis/provisional.jsonl -> consolidated Stage 1 state per project,
 * plus the raw blind reviews from analysis/results/*.jsonl (reviewer identity,
 * stage, per-criterion rationale/evidence/confidence preserved verbatim).
 *
 * This file NEVER re-scores. Provisional means are read from the artifact;
 * when analysis/provisional.jsonl does not exist yet, a DEV-ONLY placeholder
 * provider renders clearly-marked placeholder judgments instead (removed the
 * moment the real artifact lands).
 */
import fs from 'node:fs';
import { repoPath } from './reviewer-corpus';
import type { Criterion, ProvisionalScore, Review, Stage } from '../schema';

const CRIT: Criterion[] = ['leverage', 'execution', 'impact', 'creativity'];

interface ResultRecord {
  slug: string;
  category?: string;
  category_secondary?: string;
  one_line?: string;
  what_it_does?: string;
  access_model?: string;
  substitution?: string;
  leverage?: number;
  leverage_rationale?: string;
  leverage_evidence?: string[];
  leverage_confidence?: number;
  execution?: number;
  execution_rationale?: string;
  execution_evidence?: string[];
  execution_confidence?: number;
  impact?: number;
  impact_rationale?: string;
  impact_evidence?: string[];
  impact_confidence?: number;
  creativity?: number;
  creativity_rationale?: string;
  creativity_evidence?: string[];
  creativity_confidence?: number;
  usability?: number;
  usability_note?: string;
  project_origin?: string;
  eligibility?: string;
  video_evidence?: { proves_product?: string; agent_invokes_tools?: string; result_shown?: string };
  red_flags?: string[];
  standouts?: string[];
  overall_confidence?: number;
  advance?: string;
  advance_reason?: string;
}

function recordToReview(rec: ResultRecord, round: 1 | 2): Review {
  const crit = (c: Criterion) => {
    const s = rec[`${c}` as keyof ResultRecord] as number | undefined;
    return {
      score: typeof s === 'number' ? s : 0,
      rationale: (rec[`${c}_rationale`] as string | undefined) ?? '',
      evidence: (rec[`${c}_evidence`] as string[] | undefined) ?? [],
      confidence: (rec[`${c}_confidence`] as number | undefined) ?? 0,
    };
  };
  return {
    reviewerLabel: round === 1 ? 'Reviewer A (round 1)' : 'Reviewer B (round 2)',
    stage: 'S1' as Stage,
    scores: { leverage: crit('leverage').score, execution: crit('execution').score, impact: crit('impact').score, creativity: crit('creativity').score },
    criteria: {
      leverage: crit('leverage'),
      execution: crit('execution'),
      impact: crit('impact'),
      creativity: crit('creativity'),
    },
    overallConfidence: typeof rec.overall_confidence === 'number' ? rec.overall_confidence : null,
    oneLine: rec.one_line ?? null,
    whatItDoes: rec.what_it_does ?? null,
    advance: rec.advance ?? null,
    advanceReason: rec.advance_reason ?? null,
    substitution: rec.substitution ?? null,
    usability: { score: typeof rec.usability === 'number' ? rec.usability : null, note: rec.usability_note ?? null },
    origin: rec.project_origin ?? null,
    eligibility: rec.eligibility ?? null,
    accessModel: rec.access_model ?? null,
    redFlags: Array.isArray(rec.red_flags) ? rec.red_flags : [],
    standouts: Array.isArray(rec.standouts) ? rec.standouts : [],
    videoEvidence: rec.video_evidence
      ? {
          provesProduct: rec.video_evidence.proves_product ?? null,
          agentInvokesTools: rec.video_evidence.agent_invokes_tools ?? null,
          resultShown: rec.video_evidence.result_shown ?? null,
        }
      : null,
  };
}

export interface ConsolidatedReviews {
  reviews: Review[];
  provisional: ProvisionalScore | null;
  categories: string[];
  categorySecondary: string | null;
  redFlags: string[];
  standouts: string[];
}

export function loadConsolidated(): Map<string, ConsolidatedReviews> {
  const map = new Map<string, ConsolidatedReviews>();

  // Raw blind reviews, preserving reviewer-slot identity.
  const perSlug = new Map<string, { round: 1 | 2; rec: ResultRecord }[]>();
  const resultsDir = repoPath('analysis', 'results');
  if (fs.existsSync(resultsDir)) {
    for (const f of fs.readdirSync(resultsDir)) {
      if (!f.endsWith('.jsonl')) continue;
      const round: 1 | 2 = f.startsWith('r1-') ? 1 : 2;
      const content = fs.readFileSync(fs.realpathSync(`${resultsDir}/${f}`), 'utf8');
      for (const line of content.split('\n')) {
        if (!line.trim()) continue;
        let rec: ResultRecord;
        try { rec = JSON.parse(line); } catch { continue; }
        if (!rec?.slug) continue;
        const arr = perSlug.get(rec.slug) ?? [];
        // Keep at most the first record per round (attempt-1 attempt artifacts repeat).
        if (!arr.some((x) => x.round === round)) arr.push({ round, rec });
        perSlug.set(rec.slug, arr);
      }
    }
  }

  // Consolidated provisional state.
  const provFile = repoPath('analysis', 'provisional.jsonl');
  const prov = new Map<string, any>();
  if (fs.existsSync(provFile)) {
    for (const line of fs.readFileSync(provFile, 'utf8').split('\n')) {
      if (!line.trim()) continue;
      try {
        const r = JSON.parse(line);
        if (r?.slug) prov.set(r.slug, r);
      } catch { /* skip malformed line */ }
    }
  }

  for (const [slug, arr] of perSlug) {
    const sorted = [...arr].sort((a, b) => a.round - b.round);
    const reviews = sorted.map((x) => recordToReview(x.rec, x.round));
    const categories = sorted.map((x) => x.rec.category ?? '').filter(Boolean);
    const p = prov.get(slug);
    let provisional: ProvisionalScore | null = null;
    if (p?.provisional) {
      provisional = {
        scores: {
          leverage: p.provisional.scores?.leverage ?? null,
          execution: p.provisional.scores?.execution ?? null,
          impact: p.provisional.scores?.impact ?? null,
          creativity: p.provisional.scores?.creativity ?? null,
        },
        aggregate: p.provisional.aggregate ?? null,
        disagreement: p.provisional.disagreement === true,
        advanceConflict: p.provisional.advance_conflict === true,
        confidenceMean: p.provisional.confidence_mean ?? null,
      };
    }
    const reds = new Set<string>();
    const sos = new Set<string>();
    for (const x of sorted) {
      for (const f of x.rec.red_flags ?? []) reds.add(f);
      for (const s of x.rec.standouts ?? []) sos.add(s);
    }
    map.set(slug, {
      reviews,
      provisional,
      categories,
      categorySecondary: sorted[0]?.rec.category_secondary ?? null,
      redFlags: [...reds].slice(0, 6),
      standouts: [...sos].slice(0, 6),
    });
  }

  return map;
}
