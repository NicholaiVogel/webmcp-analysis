# FUNNEL.md — PRE-REGISTERED Stage 2 selection (frozen 2026-09-05, before any Stage 1 score exists)

Inputs allowed at selection time: Stage 1 outputs only (scores, rationales,
confidence, advance, substitutions, disagreements). NO HanClinto data. NO probe data
(probes run during S2). If a rule's literal application must be adjusted for a
data-quality reason, the adjustment and reason go in DEVIATIONS.md.

Selection = UNION of the following deterministic buckets, tracked per project:

1. TOP_AGGREGATE: top 250 by post-adjudication aggregate (ties broken per RUBRIC).
2. CATEGORY_LEADERS: top 10 aggregate within each `category` value (any category with
   >= 8 reviewed projects contributes its top 10; smaller categories contribute top 3).
3. TOP_LEVERAGE: top 100 by WebMCP Leverage.
4. TOP_EXECUTION: top 100 by Execution.
5. TOP_CREATIVITY: top 100 by Creativity & Ambition.
6. SUBSTITUTION_LEADERS: every project classified TRANSFORMATIVE by both reviewers
   (or adjudicated as such).
7. DISAGREEMENT: every project with |reviewer delta| > 2 on any official criterion,
   or advance=yes from one reviewer and advance=no from the other.
8. RESCUED: every project nominated advance=yes by at least one reviewer regardless of
   aggregate (rescue = the advance flag, not a hunch).
9. LOW_CONF_INTERESTING: confidence < 0.6 on BOTH reviews AND at least one reviewer
   standouts[] non-empty, up to 100 by slug order.
10. SPARSE_BUT_SHOWN: about_excerpt < 1500 chars AND (video frames exist AND
    demo_alive=alive), up to 50 by slug order.
11. RANDOM_CONTROL: 60 uniformly random projects (seed 20260905b) from projects that
    entered NO other bucket. They receive full S2 treatment; bucket is tracked.

Expected union size ~400-500. Every project carries `funnel_buckets: [...]`.

S2 reviewer treatment per project (see PROTOCOL.md): probe triage + live interaction
attempt of the central user journey + all-four-criteria rescore with change reasons +
webmcp_runtime_verification field. Output feeds S3 finalist pool: top 60 aggregate
plus all VERIFIED_RUNTIME projects plus bucket-7 stragglers flagged by S2 reviewer.
