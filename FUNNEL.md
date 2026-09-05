# FUNNEL.md — PRE-REGISTERED Stage 2 selection (v2, frozen 2026-09-05 before any Stage 1 score exists)

Inputs allowed at selection time: Stage 1 outputs only (scores, rationales,
confidence, advance flags, substitution classes, disagreement flags).
NO HanClinto data. NO probe data (probes run during S2). Any adjustment for a
data-quality reason goes in DEVIATIONS.md with its reason.

## Provisional Stage 1 scores (defined before selection)
For each project and each official criterion c in {leverage, execution, impact,
creativity} with blind reviewer scores a and b:
  provisional_c = (a + b) / 2 if |a - b| <= 2
  provisional_c = None        if |a - b| > 2   (DISAGREEMENT flagged)
provisional_aggregate = sum of the four provisional_c, defined only when none is None;
otherwise the project is DISAGREEMENT-flagged and has no provisional aggregate.

## Stage 2 lanes (union; every advanced project records funnel_buckets)
1. TOP_AGGREGATE: top 250 by provisional_aggregate (tie-break: RUBRIC order).
2. CATEGORY_LEADERS: per frozen CATEGORY taxonomy: top 10 provisional_aggregate within
   each category having >= 8 reviewed projects; top 3 for smaller categories.
3. TOP_LEVERAGE: top 100 by provisional leverage (ties by provisional aggregate).
4. TOP_EXECUTION: top 100 by provisional execution (ties likewise).
5. TOP_IMPACT: top 100 by provisional impact (ties likewise).
6. TOP_CREATIVITY: top 100 by provisional creativity (ties likewise).
7. DISAGREEMENT: every DISAGREEMENT-flagged project, or where advance flags differ
   between reviewers. These enter adjudication inside S2.
8. RESCUED: every project with advance=yes from >= 1 reviewer.
9. LOW_CONF_INTERESTING: confidence < 0.6 on both reviews AND >= 1 reviewer listed a
   standout; capped at 100, ordered by seeded hash (sha256(slug+"lowconf"), seed 20260905).
10. SPARSE_BUT_SHOWN: about_excerpt < 1500 chars AND video frame sheets exist AND
    demo_alive=alive; capped at 50, same seeded-hash ordering.
11. RANDOM_CONTROL: 60 projects (seeded hash sha256(slug+"control") ascending) from
    projects entering NO other bucket. Full S2 treatment; estimates false negatives.

Expected union 400-550. Capped lanes that overflow are truncated by the stated hash,
never alphabetically.

## Stage 2 treatment (two independent blind scorers)
Per project: deterministic probe (TRIAGE ONLY -> PUBLICLY_ACCESSIBLE / AUTH_REQUIRED /
POSSIBLE_AUTH_WALL / UNREACHABLE / LOADED_UNVERIFIED / UNKNOWN; never a direct Execution
input; auth is not a penalty, it lowers observation confidence) + one interactive
reviewer driving the central user journey producing NORMALIZED OBSERVATIONS (what a
first-time user sees, whether a meaningful action succeeded, state coherence, whether
observed behavior matches submission claims). Those observations are appended to the
evidence packet. Then TWO BLIND SCORING agents independently rescore all four official
criteria from the expanded packet. Neither may see the other's or the S1 scores.
Evidence depth grows; no single reviewer can override two blind S1 judgments.

## Stage 2 -> Stage 3 finalists
1. Top 60 by the same provisional rules applied to the S2 rescoring (mean where the two
   S2 scorers agree within 2; DISAGREEMENT-flagged otherwise).
2. Every project still DISAGREEMENT-flagged after S2 adjudication review.
No advancement bonus for runtime accessibility, auth model, or verification status.

## Stage 3
Full video review (all sheets + transcript), repo history pinned to the submission
cutoff (Sep 3 2026 13:00 PDT) for project_origin verification, novelty analysis vs the
closest existing product. WebMCP runtime verification where environment allows is
RECORDED as evidence (VERIFIED_RUNTIME / VIDEO_VERIFIED / REPO_VERIFIED / CLAIM_ONLY /
UNVERIFIED / FAILED); it raises evidence confidence, never quality points, and never
advances a project by itself.

## S4 CONSOLIDATION
Latest evidence-backed score per criterion replaces earlier scores (S2 > S1; adjudicated
scores replace both where adjudication ran). aggregate = sum of the four. Rank desc,
tie-break Leverage > Execution > Impact > Creativity > combined confidence > slug.
THEN un-quarantine HanClinto for the comparison columns only.
