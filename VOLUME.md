# VOLUME.md — compute and scope ledger

Status: STALE — a video-metadata bug surfaced at ~14:30 MDT that invalidated
the video-evidence fields in 1,640 packets (1,344 S1-only + 296 S2-funnel), so
Stage-1 rescoring and re-consolidation of the affected projects is pending a
re-run decision; the totals below are the ledger of work done SO FAR and will
move again. Numbers last reconciled 2026-09-05 14:33 MDT. Session
20260905_075512_8f5462 (start 07:55:47; last activity 14:27:28, still open).
Sources: Hermes session store (~/.hermes/state.db — sessions,
session_model_usage, async_delegations) plus artifact counts from analysis/.
This document covers the volume and scope of the AI-driven analysis only;
methodology lives in PROTOCOL.md, FUNNEL.md, RUBRIC.md, CALIBRATION.md,
CATEGORIES.md, and DEVIATIONS.md.

## Scope of the experiment

Independent product-based analysis of the ~2,500 public submissions to the
WebMCP Challenge, scored on the four official criteria (WebMCP Leverage,
Execution, Potential Impact, Creativity & Ambition; equally weighted). Design:
multi-stage funnel (pilot, S1 broad blind review, S2 deep-dive, S4
consolidation; S3 finalist deep-dive not run in this session), multiple
independent blind AI reviewers per project, physical quarantine of prior
rankings (HanClinto) as a control group, and a fresh-context subagent per
review unit so no reviewer sees another's output or any conversation history.

Target population: 2,500 projects (analysis/corpus.jsonl and
analysis/reviewer_corpus.jsonl, both exactly 2,500 lines).

Stage outcome:

| Stage | Design | Outcome |
|---|---|---|
| Pilot dry run | 2 independent reviewers, 12-project packet | done (1 of 2 reviewers timed out; repaired) |
| S1 round 1 (r1) | 300 review units over full corpus, 2 reviews per project by design | done |
| S1 round 2 (r2) | 300 review units over full corpus | done |
| S2 interactive observations | observer drives live product, 716-project queue | done (716/716 records) |
| S2 blind rescoring | 2 independent scorers (a/b series) in 6-project sets | done (120 scorer-runs; 716/716 projects carry S2 scores in the final ranking) |
| S4 consolidation | latest evidence-backed scores → final ranking | done: 2,500 projects ranked (2,492 in v1; 8 reinstated by the 2026-09-05 adjudication bugfix), FINAL_RANKING.csv |
| S3 finalist deep-dive | video/repo-history/novelty for finalists | not run in this session |

## Agents used

Parent orchestration: 1 session (Hermes CLI, glm-5.3-flash via z.ai),
2026-09-05 07:55:47 to ~13:38:56 MDT (~5.7h wall).

Subagent fleet: 872 subagent instances across 22 delegation batches, all on
gpt-5.6-luna. Each task was a fresh, isolated agent with zero prior context.

| Phase | Batches | Tasks | Completed | Failed | Interrupted | Timeout |
|---|---|---|---|---|---|---|
| Pilot | 1 | 2 | 1 | 0 | 0 | 1 |
| S1 round 1 (r1) | 5 pure + 2 mixed | 314 | 308 | 6 | 0 | 0 |
| S1 round 2 (r2) | 8 pure + 3 mixed | 307 | 305 | 2 | 0 | 0 |
| S2 observations | 2 pure + 1 mixed | 129 | 117 | 0 | 12 | 0 |
| S2 rescoring | 3 | 120 | 120 | 0 | 0 | 0 |
| Total | 22 batches | 872 | 851 | 8 | 12 | 1 |

Mixed batches (batch boundaries fell mid-phase): 2× R1/R2, 1× R2/OBS; their
tasks are attributed per-task in the token table.

All failures/interruptions were re-covered by repair dispatches: 32
repair-labeled units (r1: 16, r2: 6, S2 observations: 10).

## Token volume

Parent session (glm-5.3-flash), as of 14:33 MDT:

| Lane | API calls | Input | Output | Cache read | Reasoning |
|---|---|---|---|---|---|
| Main agent loop | 396 | 558,552 | 296,055 | 97,539,648 | 91,032 |
| Background compass/review lane | 21 | 1,485,794 | 43,616 | 8,327,872 | 23,750 |
| Aux (title gen, approvals, vision) | 5 | 4,664 | 2,515 | 0 | 2,286 |
| Parent subtotal | 422 | 2,049,010 | 342,186 | 105,867,520 | 117,068 |

Subagent fleet (gpt-5.6-luna, 872 tasks):

| Metric | Value |
|---|---|
| API calls | 7,814 |
| Input tokens | 248,018,170 |
| Output tokens | 5,640,426 |
| Fleet input+output | 253,658,596 |
| Mean input per task | 284,425 |
| Mean output per task | 6,468 |

Subagent token figures are as reported by the delegation harness;
provider-side caching inside individual subagent lifetimes is not broken out,
so fleet input is an upper bound on billable input.

Per-phase fleet tokens (per-task attribution; mixed batches split):

| Phase | Tasks | Input | Output |
|---|---|---|---|
| Pilot | 2 | 487,852 | 28,685 |
| S1 round 1 | 314 | 85,722,195 | 2,230,324 |
| S1 round 2 | 307 | 89,668,826 | 2,287,132 |
| S2 observations | 129 | 43,265,530 | 330,213 |
| S2 rescoring | 120 | 28,873,767 | 764,072 |
| Fleet total | 872 | 248,018,170 | 5,640,426 |

Grand totals, all agents (as of 14:33 MDT):

| Metric | Value |
|---|---|
| API calls | 8,236 |
| Input + output + reasoning (excl. cache reads) | 256,166,860 |
| Same, including parent cache reads | 362,034,380 |
| Fleet share of non-cached I/O | 99.0% |

## Time volume

| Metric | Value |
|---|---|
| Session wall (07:55:47 start, open at snapshot; last activity 14:27:28) | 6.5h |
| Delegation window (first dispatch 10:15:56 to last completion 13:34:52 MDT) | 3.32h |
| Cumulative subagent runtime | 70.6 agent-hours |
| Wall compression vs sequential | ~21x (70.6 agent-hours inside a 3.3h window) |

## Output volume produced

| Artifact | Count |
|---|---|
| Blind review records, S1 round 1 (analysis/results/r1-*.jsonl) | 2,617 records / 300 files |
| Blind review records, S1 round 2 (r2-*.jsonl) | 2,616 records / 300 files |
| Interactive observation records (obs-*.jsonl) | 716 records / 121 files |
| S2 rescoring verdicts (s2/rescore/*.md) | 120 files (60 a-series + 60 b-series) covering 716 projects × 2 independent scorers = 1,432 blind rescores |
| Total individual review/observation/verification records | 7,381 (5,233 S1 reviews + 716 observations + 1,432 rescores) |
| Provisional S1 scored projects (provisional.jsonl) | 2,500 (all OK); 2,469 with numeric aggregate, range 4.0-38.5 (scale 4-40) |
| Final ranked projects (final_ranking.json / FINAL_RANKING.csv) | 2,500 of 2,500 corpus, each exactly once (after 2026-09-05 adjudication bugfix; v1 had 2,492) — SUPERSEDED by the pending video-metadata re-run |
| Projects carrying S2 blind rescoring (s2_scores in final ranking) | 716 of 716 queued (708 clean means + 8 reinstated with adjudication: mean-capped) |
| Final aggregates, S2-scored projects | range 4.0-38.0 |
| WebMCP verification labels on S2-scored projects (post-fix) | VERIFIED_RUNTIME 217, CLAIM_ONLY 236, VIDEO_VERIFIED 69, REPO_VERIFIED 15, FAILED 107, UNVERIFIED 72 |
| Live probe results (probe_results.jsonl) | 16 (S2 probing was incremental, not fleet-wide) |
| Reviewer slot manifests (analysis/batches/) | 40 (20 per S1 round) |
| site_data export (web display bundle) | final_ranking.json, 816K |

Note on record counts: nominal S1 design is 2 rounds × 2,500 = 5,000 blind
review records; 5,233 were produced, the surplus coming from repair units
re-reviewing packets after failed or interrupted first passes.

Ranking completeness: the first consolidation (v1, ~13:35 MDT) emitted 2,492
of 2,500 projects. Root cause (per DEVIATIONS.md 2026-09-05 "FINAL RANKING
v1"): the combination step nulled per-criterion scores when the two S2
scorers diverged by >2, which nulled those projects' aggregates and silently
sorted them out of the ranking — a combination-script bug, not a methodology
decision. Fix applied the written protocol rule (divergence >2 → adjudication,
not exclusion): the 8 projects (ufo-web, seatline-kolkata, arrastra-relay,
prodpermit, promo-1l6nrv, livingpage, lore-wjdexz, circuit-lab) were
reinstated with computed scores and `adjudication: mean-capped`, at ranks 235,
236, 265, 295, 500, 709, 710, 712. Verified post-fix: 2,500 rows, 2,500 unique
slugs, set-equal to the corpus, no duplicates; ranks below 712 unchanged; top
3 unchanged (alza 38.0, grenz-a-policy-layer-for-webmcp 38.0, mace 37.5).

Video-metadata incident (surfaced ~14:30 MDT, re-run pending): the
video_meta.py collector hit YouTube's IP wall at ~260 videos, so 1,640
projects carried self-contradictory packets — video contact sheets on disk
and listed in the packet, but `has_video: false` with no duration. Damage
splits three ways: 296 projects in the S2 funnel (low impact — their live
observations dominated the rescoring), 1,344 S1-only projects (real risk of
video evidence under-weighted), and 598 projects with genuinely no video
(packets honest, no action). Proposed fix awaiting go-ahead: re-score the
1,344 S1-only projects (optionally all 1,640) with corrected packets, then
re-combine; estimated 3-4 hours at demonstrated rates. Until that lands, the
current FINAL_RANKING is provisional.

## Why the volume looks like this

Every review unit is a fresh agent that re-reads its full instruction, rubric,
and evidence packet from scratch (mean ~284k input tokens to produce ~6.5k
output tokens). That is the cost of the blind, no-shared-context reviewer
design: isolation is bought with re-read tokens. The parent session stays thin
(~1.4M non-cached input across 368 calls) because all per-project work is
pushed into disposable subagents. Fleet = 99.3% of all non-cached I/O.

## Method note

Counting convention: delegation goals are matched 1:1 with results by index,
so per-phase splits are per-task, not per-batch (3 batches span two phases).
Session end time is taken from last_activity_at (the CLI records ended_at as
NULL on exit). Subagent counts are delegation tasks; each was one isolated
agent instance with its own tool session. Token columns are the harness's
reported per-task cumulative usage as recorded in async_delegations event
payloads.
