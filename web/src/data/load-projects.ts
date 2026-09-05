/**
 * load-projects.ts — the single entry point the site uses to get Projects.
 *
 * Build-time only. Reads the analysis artifacts through the adapters and
 * produces the public Project model.
 *
 * Ranking source of truth: analysis/site_data/final_ranking.json (the
 * pipeline's consolidated output). Ranks are displayed exactly as recorded;
 * this site never re-sorts, re-scores, or re-derives them. The model keeps
 * rankStatus 'provisional' | 'final' so the pages can state what stage backs
 * each row (S1 packet-only vs S2 live-product evidence).
 *
 * Stage 1 blind reviews (analysis/results/*.jsonl) and the consolidated
 * provisional state (analysis/provisional.jsonl) stay attached per project so
 * project pages can expose the reviewer work underneath the final number.
 */
import fs from 'node:fs';
import { loadCorpus, repoPath } from './adapters/reviewer-corpus';
import { loadParsedLinks, playableVideoUrl } from './adapters/parsed-links';
import { loadConsolidated } from './adapters/provisional';
import { loadFinal, probeCaptures, hasFinal } from './adapters/final';
import type { Project } from './schema';

let cache: Project[] | null = null;

export { hasFinal };

export function loadProjects(): Project[] {
  if (cache) return cache;
  const corpus = loadCorpus();
  const links = loadParsedLinks();
  const consolidated = loadConsolidated();
  const final = loadFinal();

  const projects: Project[] = [];
  for (const [slug, c] of corpus) {
    const con = consolidated.get(slug);
    const reviews = con?.reviews ?? [];
    const p = con?.provisional ?? null;
    const l = links.get(slug);
    const f = final.get(slug);

    const reviewCount = Math.min(reviews.length, 2);
    const [r1, r2] = reviews;
    const access = r1?.accessModel ?? r2?.accessModel ?? null;
    const probes = probeCaptures(slug);

    const project: Project = {
      slug,
      rank: f ? f.rank : null,
      rankStatus: f ? 'final' : 'provisional',
      sortAggregate: f ? f.aggregate : (p?.aggregate ?? null),
      finalStage: f ? f.stage : null,
      webmcpVerification: f ? (f.webmcpVerification as Project['webmcpVerification']) : null,
      title: c.title || f?.title || slug,
      pitch: c.pitch,
      category: con?.categories[0] ?? null,
      categorySecondary: con?.categorySecondary ?? null,
      categories: con?.categories ?? [],
      scores: f
        ? {
            leverage: f.leverage,
            execution: f.execution,
            impact: f.impact,
            creativity: f.creativity,
            aggregate: f.aggregate,
          }
        : {
            leverage: p?.scores.leverage ?? null,
            execution: p?.scores.execution ?? null,
            impact: p?.scores.impact ?? null,
            creativity: p?.scores.creativity ?? null,
            aggregate: p?.aggregate ?? null,
          },
      confidence: p?.confidenceMean ?? null,
      reviewCount,
      substitution: [r1?.substitution ?? null, r2?.substitution ?? null],
      origin: [r1?.origin ?? null, r2?.origin ?? null],
      eligibility: [r1?.eligibility ?? null, r2?.eligibility ?? null],
      access,
      links: {
        devpost: c.devpost_url,
        live: l?.live ?? null,
        repository: l?.repository ?? null,
        video: l?.video ? playableVideoUrl(l.video) : null,
      },
      media: {
        devpostScreenshot: fs.existsSync(repoPath('screenshots', `${slug}.png`))
          ? repoPath('screenshots', `${slug}.png`)
          : null,
        videoFrameSheets: c.video_frame_sheets.map((x) => repoPath(x)).filter((x) => fs.existsSync(x)),
        probeBefore: probes.before,
        probeAfter: probes.after,
        galleryCount: c.gallery_image_count,
      },
      corpus: {
        devpostUrl: c.devpost_url,
        aboutExcerpt: c.about_excerpt,
        hasPublicRepo: c.has_public_repo,
        hasDemoLink: c.has_demo_link,
        demoAlive: c.demo_alive,
        hasVideo: c.has_video,
        videoDurationSecs: c.video_duration_secs,
        videoTitle: c.video_title,
      },
      reviews,
      provisional: p,
      redFlags: con?.redFlags ?? [],
      standouts: con?.standouts ?? [],
    };
    projects.push(project);
  }

  // Final-ranked rows in artifact rank order; everything else trails (clearly
  // labeled as not in the final dataset: 8 pipeline-excluded slugs).
  projects.sort((a, b) => {
    const ra = a.rank ?? Number.POSITIVE_INFINITY;
    const rb = b.rank ?? Number.POSITIVE_INFINITY;
    if (ra !== rb) return ra - rb;
    return a.slug.localeCompare(b.slug);
  });
  cache = projects;
  return projects;
}

export function getProject(slug: string): Project | undefined {
  return loadProjects().find((p) => p.slug === slug);
}

export interface SummaryRow {
  slug: string;
  rank: number | null;
  title: string;
  pitch: string;
  category: string | null;
  stage: 'S1' | 'S2' | null;
  verification: string | null;
  leverage: number | null;
  execution: number | null;
  impact: number | null;
  creativity: number | null;
  aggregate: number | null;
  confidence: number | null;
  disagreement: boolean;
  reviewCount: number;
  origin: string | null;
  access: string | null;
  substitution: string | null;
  hasRepo: boolean;
  hasVideo: boolean;
}

/** Client dataset for search/filter/sort on the rankings page — bounded fields only. */
export function loadSummaries(): SummaryRow[] {
  return loadProjects().map((p) => ({
    slug: p.slug,
    rank: p.rank,
    title: p.title,
    pitch: (p.pitch ?? '').slice(0, 140),
    category: p.category,
    stage: p.finalStage,
    verification: p.webmcpVerification,
    leverage: p.scores.leverage,
    execution: p.scores.execution,
    impact: p.scores.impact,
    creativity: p.scores.creativity,
    aggregate: p.scores.aggregate,
    confidence: p.confidence,
    disagreement: p.provisional?.disagreement ?? false,
    reviewCount: p.reviewCount,
    origin: p.origin[0],
    access: p.access,
    substitution: p.substitution[0],
    hasRepo: p.corpus.hasPublicRepo,
    hasVideo: p.corpus.hasVideo,
  }));
}

/** Category taxonomy with counts (reviewer 1 primary), for filters. */
export function loadCategoryCounts(): { name: string; count: number }[] {
  const counts = new Map<string, number>();
  for (const p of loadProjects()) {
    if (p.category) counts.set(p.category, (counts.get(p.category) ?? 0) + 1);
  }
  return [...counts.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
}
