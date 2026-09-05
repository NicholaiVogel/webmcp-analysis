# VOLUME.md — compute and scope ledger

Final numbers, corrected after the ranking bugfix (see Output volume and
DEVIATIONS.md 2026-09-05 "FINAL RANKING v1"). Session 20260905_075512_8f5462
completed 2026-09-05 ~13:39 MDT (last activity 13:38:56; ~5.7h wall from the
07:55:47 start). Sources: Hermes session store (~/.hermes/state.db —
sessions, session_model_usage, async_delegations) plus artifact counts from
analysis/. This document covers the volume and scope of the AI-driven
analysis only; methodology lives in PROTOCOL.md, FUNNEL.md, RUBRIC.md,
CALIBRATION.md, CATEGORIES.md, and DEVIATIONS.md.

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

Parent session (glm-5.3-flash), final:

| Lane | API calls | Input | Output | Cache read | Reasoning |
|---|---|---|---|---|---|
| Main agent loop | 347 | 495,429 | 277,080 | 70,896,320 | 85,389 |
| Background compass/review lane | 17 | 948,622 | 32,943 | 6,728,832 | 18,349 |
| Aux (title gen, approvals) | 4 | 1,973 | 2,314 | 0 | 2,286 |
| Parent subtotal | 368 | 1,446,024 | 312,337 | 77,625,152 | 106,024 |

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

Grand totals, all agents:

| Metric | Value |
|---|---|
| API calls | 8,182 |
| Input + output + reasoning (excl. cache reads) | 255,522,981 |
| Same, including parent cache reads | 333,148,133 |
| Fleet share of non-cached I/O | 99.3% |

## Time volume

| Metric | Value |
|---|---|
| Delegation window (first dispatch 10:15:56 to last completion 13:34:52 MDT) | 3.32h |
| Cumulative subagent runtime | 70.6 agent-hours |
| Wall compression vs sequential | ~21x (70.6 agent-hours inside a 3.3h window) |

## Output volume produced

| Artifact | Count |
|---|---|
| Blind review records, S1 round 1 (analysis/results/r1-*.jsonl) | 2,617 records / 300 files |
| Blind review records, S1 round 2 (r2-*.jsonl) | 2,616 records / 300 files |
| Interactive observation records (obs-*.jsonl) | 716 records / 121 files |
| S2 rescoring verdicts (s2/rescore/*.md) | 120 files (60 a-series + 60 b-series, 6 projects each = 716 projects × 2 scorers, incl. overlap) |
| Total individual review/observation/verification records | ~6,069 |
| Provisional S1 scored projects (provisional.jsonl) | 2,500 (all OK); 2,469 with numeric aggregate, range 4.0-38.5 (scale 4-40) |
| Final ranked projects (final_ranking.json / FINAL_RANKING.csv) | 2,500 of 2,500 corpus, each exactly once (after 2026-09-05 bugfix; v1 had 2,492) |
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
