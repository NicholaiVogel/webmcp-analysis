/**
 * Public website-facing data model for the WebMCP analysis results site.
 *
 * The site is a CONSUMER of analysis artifacts. Nothing here re-scores,
 * re-weights, or re-interprets quality: adapters translate artifact rows into
 * this model verbatim. Null means "the analysis does not provide it" — never
 * zero. The four official criteria are the only scoring spine; diagnostics
 * (substitution, usability, access, eligibility) ride along as metadata.
 */

/** The four official judging criteria. Aggregate = sum of these four (4-40). */
export type Criterion = 'leverage' | 'execution' | 'impact' | 'creativity';
export const CRITERIA: readonly Criterion[] = ['leverage', 'execution', 'impact', 'creativity'] as const;

export const CRITERION_LABELS: Record<Criterion, string> = {
  leverage: 'WebMCP Leverage',
  execution: 'Execution',
  impact: 'Potential Impact',
  creativity: 'Creativity & Ambition',
};

/** How far the pipeline has gotten for this project. */
export type RankStatus =
  | 'provisional'   // Stage 1 consolidated only
  | 'final';        // present in analysis/site_data/final_ranking.json

export type Stage = 'S1' | 'S2' | 'S3' | 'S4';

/** WebMCP runtime verification level (PROTOCOL evidence labeling; S2+ only). */
export type VerificationLevel =
  | 'VERIFIED_RUNTIME'
  | 'VIDEO_VERIFIED'
  | 'REPO_VERIFIED'
  | 'CLAIM_ONLY'
  | 'UNVERIFIED'
  | 'FAILED'
  | null;

/** One blind reviewer's judgment of one criterion. Verbatim from the artifact. */
export interface CriterionJudgment {
  score: number;            // 1-10
  rationale: string;
  evidence: string[];
  confidence: number;       // 0-1
}

/** One complete blind review of a project (one reviewer-slot output). */
export interface Review {
  reviewerLabel: string;    // e.g. "Reviewer A (round 1)" — identity/index preserved
  stage: Stage;
  scores: Record<Criterion, number>;
  criteria: Record<Criterion, CriterionJudgment>;
  overallConfidence: number | null;
  oneLine: string | null;
  whatItDoes: string | null;
  advance: string | null;         // "yes" | "no" as recorded
  advanceReason: string | null;
  substitution: string | null;    // diagnostic, never a score
  usability: { score: number | null; note: string | null }; // diagnostic
  origin: string | null;          // new | pre_existing | unclear
  eligibility: string | null;     // LIKELY_ELIGIBLE | UNCLEAR | LIKELY_INELIGIBLE
  accessModel: string | null;     // none | login | api-key | unclear — metadata, not a judgment
  redFlags: string[];
  standouts: string[];
  videoEvidence: {
    provesProduct: string | null;
    agentInvokesTools: string | null;
    resultShown: string | null;
  } | null;
}

/**
 * Consolidated provisional state per FUNNEL.md: per-criterion mean when both
 * blind reviews agree within 2; null + disagreement flag otherwise.
 * Displayed exactly as that state — a null criterion is NEVER rendered as 0.
 */
export interface ProvisionalScore {
  scores: Record<Criterion, number | null>;
  aggregate: number | null;
  disagreement: boolean;
  advanceConflict: boolean;
  confidenceMean: number | null;
}

export interface ProjectLinks {
  devpost: string | null;
  live: string | null;
  repository: string | null;
  video: string | null;
}

/** Media are labeled by what they actually prove. Never presented as runtime verification. */
export interface ProjectMedia {
  devpostScreenshot: string | null; // path to screenshots/<slug>.png — Devpost PAGE capture
  videoFrameSheets: string[];       // paths under raw/frames/<video_id>/ — submitted demo video
  probeBefore: string | null;       // probes/obs/<slug>-before.png — live-product capture (S2 interactive testing)
  probeAfter: string | null;        // probes/obs/<slug>-after.png — live-product capture after interaction
  galleryCount: number | null;
}

export interface Project {
  slug: string;
  rank: number | null;              // artifact rank; null when absent from final_ranking.json
  rankStatus: RankStatus;
  finalStage: 'S1' | 'S1R' | 'S2' | null; // evidence depth backing the final score
  webmcpVerification: VerificationLevel;
  sortAggregate: number | null;
  title: string;
  pitch: string | null;
  category: string | null;          // reviewer 1 primary; categories[] has both
  categorySecondary: string | null;
  categories: string[];             // both blind reviewers' primaries, in order
  scores: {
    leverage: number | null;
    execution: number | null;
    impact: number | null;
    creativity: number | null;
    aggregate: number | null;
  };
  confidence: number | null;        // artifact confidence, else mean of blind reviewers' own confidence
  rescored: { priorAggregate: number; newAggregate: number; audioNeutral: boolean } | null;
  reviewCount: number;              // 0, 1 (pipeline gap), or 2
  substitution: [string | null, string | null]; // diagnostics per reviewer
  origin: [string | null, string | null];
  eligibility: [string | null, string | null];
  access: string | null;
  links: ProjectLinks;
  media: ProjectMedia;
  corpus: {
    devpostUrl: string | null;
    aboutExcerpt: string | null;
    hasPublicRepo: boolean;
    hasDemoLink: boolean;
    demoAlive: string | null;       // alive | dead | unknown
    hasVideo: boolean;
    videoDurationSecs: number | null;
    videoTitle: string | null;
  };
  reviews: Review[];
  provisional: ProvisionalScore | null;
  redFlags: string[];
  standouts: string[];
}

/** Sort tie-break per PROTOCOL/RUBRIC: aggregate, then L > E > I > C, then confidence, then slug. */
export function compareProjects(a: Project, b: Project): number {
  const agg = (p: Project) => p.sortAggregate ?? -1;
  if (agg(b) !== agg(a)) return agg(b) - agg(a);
  for (const c of CRITERIA) {
    const av = a.scores[c] ?? -1;
    const bv = b.scores[c] ?? -1;
    if (av !== bv) return bv - av;
  }
  const ca = a.confidence ?? -1;
  const cb = b.confidence ?? -1;
  if (ca !== cb) return cb - ca;
  return a.slug.localeCompare(b.slug);
}
