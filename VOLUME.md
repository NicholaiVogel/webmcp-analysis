# VOLUME.md — compute and scope ledger

FINAL tallies, 2026-09-05 17:05 MDT, after the video-metadata re-run
(S1R), the music-audio sensitivity pass, and the tracked ranking rebuild.
The experiment ran across three orchestrator sessions: the main analysis
session 20260905_075512_8f5462 (07:55:47-15:54:43, glm-5.3-flash), the
re-score continuation session 20260905_155443_8746c3 (15:54:43-16:53,
same model), and the results-site session 20260905_121301_eaf8fd
(12:28:55-16:54, glm-5.3-flash). Subagent fleet: gpt-5.6-luna throughout.
Sources: Hermes session store (~/.hermes/state.db) plus artifact counts
from analysis/. Scope and methodology: PROTOCOL.md, FUNNEL.md, RUBRIC.md,
CALIBRATION.md, CATEGORIES.md, DEVIATIONS.md, correctness-audit.md.

## Scope of the experiment

Independent product-based analysis of all 2,500 public submissions to the
WebMCP Challenge, scored on the four official criteria (WebMCP Leverage,
Execution, Potential Impact, Creativity & Ambition; equally weighted).
Design: multi-stage funnel (pilot, S1 broad blind review, S2 deep-dive,
S4 consolidation), multiple independent blind AI reviewers per project,
physical quarantine of prior rankings (HanClinto) as a control group, and
a fresh-context subagent per review unit so no reviewer sees another's
output or any conversation history. Two data-quality defects found and
fixed during the run (S2 adjudication drop-out; video-metadata IP-wall
gap), each with a scoped re-run rather than a silent patch.

Stage outcome (final):

| Stage | Design | Outcome |
|---|---|---|
| Pilot dry run | 2 independent reviewers, 12-project packet | done (1 timeout, repaired) |
| S1 round 1 (r1) | 300 blind review units over full corpus | done |
| S1 round 2 (r2) | 300 blind review units over full corpus | done |
| S2 interactive observations | observer drives live product, 716-project queue | done (716/716 records) |
| S2 blind rescoring | 2 independent scorers (a/b series) | done (1,432 rescores) |
| S1R video remediation | 1,353 video-affected + audio-neutral re-scores | done (136 reviewer units) |
| Music-audio sensitivity | 22 S2-funnel music projects tabulated | done (music_audio_s2_sensitivity.md) |
| S4 consolidation | tracked builder, fail-closed assertions, BUILD_MANIFEST | done: 2,500/2,500 ranked, monotonic, hash-manifested |
| S3 finalist deep-dive | video/repo-history/novelty for finalists | not run |

## Agents used

| Role | Instances | Model |
|---|---|---|
| Orchestrator, main analysis | 1 session (8.0h, 07:55-15:54) | glm-5.3-flash |
| Orchestrator, re-score continuation | 1 session (1.0h, 15:54-16:53) | glm-5.3-flash |
| Orchestrator, results site | 1 session (4.4h, 12:28-16:54) | glm-5.3-flash |
| Pilot reviewers | 2 | gpt-5.6-luna |
| S1 blind reviewers | 621 units | gpt-5.6-luna |
| S2 observers | 129 units | gpt-5.6-luna |
| S2 blind rescoring agents | 120 units | gpt-5.6-luna |
| S1R re-scoring reviewers | 136 units | gpt-5.6-luna |
| Adversarial audits (packet builder, rerun scope) | 2 | gpt-5.6-luna |
| Site design/build agents | 21 | gpt-5.6-luna |
| (misc subagent units) | 3 | gpt-5.6-luna |
| Total subagent units | 1,032 | |
| Total agents incl. 3 orchestrators | 1,035 | |

Subagent units = subagent sessions parented to the three orchestrators
(872 main + 139 rescore + 21 site); each was an isolated fresh-context
agent. Main-session statuses: 851 completed, 8 failed, 12 interrupted,
1 timeout; all re-covered by 32 repair units.

## Token volume

Per-session, from the session store:

| Session | Role | API calls | Input | Output | Cache reads |
|---|---|---|---|---|---|
| 20260905_075512_8f5462 | orchestrator, main | 456 | 3,259,698 | 378,927 | 125,067,648 |
| 20260905_155443_8746c3 | orchestrator, rescore | 140 | 418,460 | 59,194 | 17,730,368 |
| 20260905_121301_eaf8fd | orchestrator, site | 524 | 573,994 | 319,972 | 137,859,712 |
| 1,032 subagent sessions | fleet | 9,073 | 47,478,255 | 6,798,832 | 245,603,840 |
| Total | | 10,193 | 51,730,407 | 7,556,925 | 526,261,568 |

Input split for the fleet: the sessions table separates provider-side
cache reads, so true fresh input is 47.5M; the delegation harness's
per-task figures (248.0M main + 36.7M rescore + 8.3M site = 293.0M
gross) include cache reads inside each subagent's lifetime.

Grand totals:

| Metric | Value |
|---|---|
| Non-cached input + output (billable-shaped) | 59,287,332 |
| Cache-read tokens | 526,261,568 |
| All token movement incl. cache | 585,548,900 |
| API calls | 10,193 |

## Time volume

| Metric | Value |
|---|---|
| Wall clock, main session | 8.0h (07:55:47-15:54:43) |
| Wall clock, rescore continuation | 1.0h (15:54:43-16:53) |
| Wall clock, site session | 4.4h (12:28:55-16:54) |
| Delegation windows (main 10:15-13:34, rescore 16:01-16:38) | 3.32h + 0.62h |
| Cumulative subagent runtime | 80.2 agent-hours (main 70.6 + rescore 8.8 + site 0.8) |
| Wall compression vs sequential | ~20x (80.2 agent-hours inside 3.9h of delegation windows) |

## Output volume produced

| Artifact | Count |
|---|---|
| Blind review records, S1 round 1 (results/r1-*.jsonl) | 2,617 |
| Blind review records, S1 round 2 (r2-*.jsonl) | 2,616 |
| Interactive observation records (obs-*.jsonl) | 716 |
| S2 blind rescores (s2/rescore/, 2 scorers × 716) | 1,432 |
| S1R re-score records (results/rr/, 136 reviewer files) | 1,353 (0 missing, 0 extra, schema-validated) |
| Total judgments behind the final ranking | 8,734 |
| Final ranked projects | 2,500/2,500 (S2 716, S1R 1,353, S1 431), unique, monotonic, hash-manifested (BUILD_MANIFEST.json) |
| Music-audio sensitivity table | 22 projects, published |
| Correctness audit | correctness-audit.md, 13-point release gate |
| Site design/build artifacts | 21 agent outputs (design explorations, first-viewport candidates) |

Top of the final table: physical-ai-webmcp-command-center and
handrail-8v6gls 38.0 (S1R, previously video-under-scored), alza 38.0
(S2, VERIFIED_RUNTIME), incident-command and paperveil 38.0. Sushi Daw
(bingus) 32.5 unchanged, rank 480 -> 848 as peers' video evidence was
finally counted. Re-run deltas: mean |delta| 1.69, max +7.5, max -4.5.
Known accepted cost: 4/136 S1R reviewers hit vision rate limits and fell
back to packet text with reduced (recorded) confidence.

## Incident ledger

1. S2 adjudication drop-out (~13:35): combination step nulled aggregates
   on >2 divergence and sorted 8 projects out of the ranking. Fixed per
   protocol (adjudication, mean-capped); 2,500/2,500 restored.
2. Video-metadata IP wall (~14:30 discovery): video_meta.py stopped at
   ~260 of 2,398 videos; 1,640 packets self-contradictory (sheets on
   disk, has_video=false). Re-mediated by S1R re-score of 1,353
   affected projects (296 already in S2 funnel were dominated by live
   observation; 598 had no video and needed nothing).
3. Music-audio modality penalty (audit finding): reviewers marked audio
   "not assessable" and it leaked into execution scores. 40 S1-only
   music projects re-scored audio-neutral (part of the 1,353); 22
   S2-funnel projects got a published sensitivity table instead.
4. Ranking sort defect (pre-rebuild): output was stage-concatenated,
   not globally sorted. Fixed with tracked builder
   scripts/build_final_ranking.py + fail-closed assertions +
   BUILD_MANIFEST.json hashes.

## Why the volume looks like this

Every review unit is a fresh agent that re-reads its full instruction,
rubric, and evidence packet from scratch (~46k true input tokens per
subagent after cache accounting; harness-reported gross ~284k including
intra-session cache reads). That is the cost of the blind,
no-shared-context reviewer design: isolation is bought with re-read
tokens. The orchestrators stay thin (~8.5% of non-cached I/O) because
all per-project work is pushed into disposable subagents. Re-runs were
scoped to affected subsets, not whole-stage re-launches: 1,353 of 2,500
re-scored rather than 5,000.

## Method note

Subagent unit counts are subagent sessions in the session store parented
to the three orchestrators; the per-role phase splits (621 S1 / 129
observers / 120 rescoring / 136 S1R / 2 audits / 21 site) are delegation
tasks matched 1:1 with results by index.
Orchestrator token lanes are summed across session_model_usage rows
(main, background_review, approval, title_generation, vision). Fleet
per-session token rows are the authoritative fresh-input figures; the
delegation harness's per-task token objects double-count provider cache
reads and are retained in git history for the per-phase split. Session
end times use last_activity_at (CLI leaves ended_at NULL). All counts
reconciled 2026-09-05 ~17:05 MDT.
