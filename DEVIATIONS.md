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
