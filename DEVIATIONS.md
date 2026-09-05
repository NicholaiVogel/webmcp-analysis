# DEVIATIONS.md

## 2026-09-05 — S2 funnel: RESCUED lane collapsed (Nicholai approved Option A)

**What happened.** FUNNEL.md lane 8 (RESCUED: any project with advance=yes from >=1
reviewer) was written expecting reviewers to advance ~20-30% of projects. Measured
after S1: 2,186 / 2,469 scored projects (88.5%) received advance=yes from at least one
reviewer. The lane stopped selecting — it admitted nearly everything.

**Decision (approved by Nicholai, Option A).** Stage 2 runs on the 716 projects that
enter through the pre-registered core lanes: TOP_AGGREGATE (250), CATEGORY_LEADERS,
TOP_LEVERAGE / TOP_EXECUTION / TOP_IMPACT / TOP_CREATIVITY (100 each), DISAGREEMENT
(336), RANDOM_CONTROL (60). Projects that entered ONLY via RESCUED (1,542) do not get
S2 treatment; their final ranking uses S1 provisional scores. LOW_CONF_INTERESTING and
SPARSE_BUT_SHOWN remain defined but contributed no projects outside other lanes at
selection time.

**Why this is not post-hoc threshold tuning.** The cutoff was not moved after
inspecting which specific projects benefited. The lane was disabled because the
selection signal it was supposed to carry (selective human-in-the-loop rescue) was
measured to be absent. RESCUED membership is still recorded for every project and
appears as a column in final outputs.

**Frozen lists:** `analysis/funnel_selection.json` (lane tags per project),
`analysis/funnel_order.json` (S2 processing order by provisional aggregate).

## 2026-09-05 — FINAL RANKING v1: 8 projects dropped by combination bug (FIXED)

**What happened.** The first `analysis/FINAL_RANKING.csv` / `final_ranking.json`
contained 2,492 of the expected 2,496 ranked projects (2,500 minus 4 unmatched
corpus slugs). Root cause: in the combination step, S2 scorer pairs whose
per-criterion scores diverged by more than 2 had those criteria set to None
(DISAGREEMENT flag). The provisional-aggregate then became None, and the rank
builder emitted those projects with `s2_aggregate=None`, which sorted as
excluded. 8 projects were affected: arrastra-relay, circuit-lab, livingpage,
lore-wjdexz, prodpermit, promo-1l6nrv, seatline-kolkata, ufo-web. All 8 were
fully processed: S1-scored (25.0-35.5 provisional), observed live, and rescored
by both S2 scorers — they were lost only in the combine step.

**Fix.** Combination re-run with the protocol rule applied correctly:
|a-b|<=2 -> mean; |a-b|>2 -> per FUNNEL.md the project is DISAGREEMENT-flagged
and proceeds to adjudication, not exclusion. Adjudication for these 8 is the
documented fallback: use the S2 mean where it exists and mark
`adjudication: pending` in the row; if a criterion pair still diverges after
adjudication the mean is used with confidence capped at 0.5. No other
projects' scores change.

**Verification.** Combination re-run: the ranking now contains **2,500 of 2,500**
corpus projects, each exactly once (the earlier "expected 2,496" was a
mis-arithmetic in the first incident note: 2,492 + 8 reinstated = 2,500, because
no corpus slugs had been dropped in S1 — the provisional step had already covered
all 2,500). The 8 reinstated projects appear at their computed ranks:
ufo-web 235, seatline-kolkata 236, arrastra-relay 265, prodpermit 295,
promo-1l6nrv 500, livingpage 709, lore-wjdexz 710, circuit-lab 712.

## 2026-09-05 — Video capture gap: source sheet undercounted video_links

**What happened.** 88 projects' Devpost pages had demo videos whose links were not
present in the source sheet's `video_links` column (2,412 of 2,500 did have one).
These projects were reviewed with `has_video: false` and `video_evidence` marked
unclear. This is a CAPTURE gap, not a reviewer error — reviewers correctly reported
what was in their packets. One user-visible instance: slug `bingus` (Sushi Daw)
actually has a submitted YouTube video (170s).

**Fix.** Video_links re-extraction pass from live Devpost HTML for all 2,500 pages;
keyframes generated for newly found videos. Affects future stages only; S1/S2
scores already finalized stand, with this limitation recorded.

**Status.** bingus: video id -ObHnsF4Cg4, 87 frames / 3 contact sheets extracted,
corpus record updated. Broader re-extraction queued.

## 2026-09-05 — BLOCKER FIXED: final ranking was stage-concatenated, not globally sorted

**What happened.** The first FINAL_RANKING.csv/site JSON sorted Stage 2 projects
among themselves and appended Stage 1-only projects after them. Result: ranks 1-716
were all S2 (aggregates 38.0 down to 4.0), ranks 717-2500 were all S1-only (34.5
down to 4.0). 731,223 cross-stage ordering inversions; e.g. rank 716 (S2, 4.0)
outranked rank 717 (S1-only, 34.5). Independent audit (correctness-audit.md)
caught this; I verified the defect (731,223 inversions confirmed) and fixed it.

**Fix.** Rebuilt the ranking with ONE global comparator over ALL 2,500 projects:
S2 aggregate where valid S2 scoring exists, else S1 provisional aggregate; sort by
aggregate desc, then leverage/execution/impact/creativity desc, then slug asc.
Fail-closed monotonicity assertion added (adjacent aggregate must be non-increasing).
CSV and site-data regenerated from the fixed ranking and re-verified monotonic.

**Effect on the published table.** Top of the table (S2-heavy) is unchanged; ranks
shift substantially for mid-table projects, and S1-only projects now interleave by
score. bingus (Sushi Daw) moves from rank 167 to rank 480 — the earlier 167 was an
artifact of it sitting in the S2 block.

**Lesson encoded.** Every future regeneration must run the monotonicity assertion;
any adjacent inversion is a hard failure, not a warning.

## 2026-09-05 — RE-SCORING PASS launched (video-metadata defect + audio modality bias)

Scope (analysis/rerun_scope.json, 1353 projects, S1-only):
- 1344 packets had has_video=false while frame sheets existed on disk and were
  listed for viewing (video_meta collector hit YouTube IP wall at 261/2398).
- 40 music-audio projects get an audio-neutrality directive (31 overlap with
  the video group): sonic quality is NOT ASSESSABLE and must move confidence,
  never scores.
- 22 music-audio projects already in S2 keep their live-observation scores;
  sensitivity table to be published.

Deviations from S1 protocol (pre-registered here, before any re-review ran):
1. Packets rebuilt with corrected video fields (has_video/sheets/frame_count)
   — the correction itself. All other fields source-identical to S1 corpus
   (verified: 0 mismatches across 1353 on non-corrected fields).
2. Reviewer preamble (make_prompt_v2.py) states sheets are AUTHORITATIVE
   video evidence; otherwise identical rubric/schema/rules to S1.
3. Audio-neutrality directive appended to flagged packets only.
4. Single re-scoring round (not two): this pass corrects an evidence defect,
   it does not re-measure inter-reviewer variance. S1's two-round design
   already measured variance (mean delta 0.46 dry-run); the corrected pass
   inherits those calibration ranges.
5. Score combination: same rules as S1 (|delta|<=2 mean; else mean+cap,
   labeled). Re-scored aggregates REPLACE S1 aggregates for the 1353; S2
   scores unchanged. Final ranking regenerated after, monotonic gate on.

Known limitation carried forward: duration known for only 261 videos;
transcripts 216/2398 (IP wall). Packets mark duration null rather than 0.

## 2026-09-05 — RE-SCORING COMPLETE: ranking regenerated (S1R stage introduced)

All 136 rr reviewer files landed and validated: 1353 records = 1353 scope slugs,
0 missing, 0 extra, 0 schema problems. (rr-0135 correctly holds 3 records — final
prompt batch size was 3, not a truncation.)

Combination per pre-registered rules: rr aggregates replace S1 aggregates for the
1353; S2 untouched. Mean |aggregate delta| = 1.69; biggest gain +7.5
(clip-magic-webmcp-contact-request 21.5->29); biggest drop -4.5
(research-devices-webmcp, supplypilot).

Stage labels in final_ranking.json now distinguish: S2 (716, live-tested),
S1 (431, original two-round blind review), S1R (1353, re-scored single-round with
corrected evidence). Every S1R row carries evidence.rescored = {round, prior
aggregate, new aggregate, audio_neutral} for full auditability.

New top of table: physical-ai-webmcp-command-center and handrail-8v6gls reach 38.0
on re-scored evidence (both previously under-scored due to the video-flag defect);
alza/grenz/mace/pillbox/substrate hold. bingus rank 480 -> 848 (its score was
unchanged at 32.5; peers rose as their video evidence was finally counted).

Known cost: 4/136 reviewers reported vision rate/open-file limits mid-run and fell
back to packet text with reduced confidence (recorded in their confidence fields,
not silent). This mirrors the original S1 pass limitation and is accepted.
