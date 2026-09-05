# WebMCP Challenge Independent Product-Based Study

## Goal
Rank ALL 2,500 submissions (not just top 10) on product quality and WebMCP leverage,
using product-based evidence, independent of HanClinto's description-based analysis.

## Evidence sources (kept separate; never let prose substitute for product)
1. DEVPOST TEXT (corpus: pitch + about text)
2. SCREENSHOTS (screenshots/<slug>.png, 2500 captured)
3. DEMO VIDEO (raw/video_meta.jsonl: duration, title, transcript; keyframes for finalists)
4. LIVE PRODUCT (S2 deterministic probe + S2 reviewer screenshots)
5. REPOSITORY (analysis/signals.jsonl: stars, last push, archived)
6. LINK LIVENESS (demo_alive)

## Quarantine (CRITICAL)
raw/hanclinto/* and ALL sheet judgment columns (scores, strengths, weaknesses, verdicts,
ranks, review_tier) are the CONTROL GROUP. Reviewers never see them. They join only in
the final consolidation step to compute agreement/disagreement deltas.

## Reviewer blinding & calibration
- Randomized slug assignment (seed=20260905, order shuffled).
- 40 calibration anchors (deterministic proxies, not HanClinto tiers) rotated so each
  anchor is reviewed by 3 different reviewers; every reviewer gets ~12 anchors.
- Anchor stats (mean, spread) detect harsh/generous reviewers. No mechanical
  normalization; disagreement goes to adjudication.
- Reviewers blind to each other; only adjudicator sees both.

## Stage 1 — broad review (all 2500, 20 Luna reviewers x ~125 projects)
Evidence packet: devpost text (<=9k chars), video duration+transcript (<=6k), pitch,
signals (demo liveness, repo stats). Output: strict JSONL, one object per project.

Per-project fields:
  slug, category (one of: game, music-audio, dev-tool, productivity, business-crm,
    education, creative-art, agent-infra, data-viz, writing, commerce, health, finance,
    social, research, other),
  one_line, what_it_does (<=40 words),
  access_model: none|login|api-key|unclear,
  substitution: TRANSFORMATIVE|MAJOR_DELTA|MEANINGFUL_DELTA|MINOR_DELTA|COSMETIC
    (question asked literally: could a person with an on-device agent — ChatGPT, Codex,
    Hermes — already do this through generic browser automation?),
  leverage_1_10 (what does WebMCP change; tool COUNT is not leverage),
  execution_claimed_1_10 (coherence/intentionality/completeness AS DESCRIBED+SHOWN in
    evidence; no aesthetic penalties),
  impact_1_10 (category-neutral: real audience, real problem, niche counts),
  creativity_1_10 (novelty of concept + interaction model),
  usability_1_10 (setup friction, login burden, first-run clarity, likely usability),
  video_evidence {proves_product: yes|no|partial, agent_invokes_tools: yes|no|unclear,
    result_shown: yes|no|unclear},
  red_flags[], standouts[], confidence 0-1, advance: yes|no

## Funnel to Stage 2 (multiple entrances; ~400 projects)
top aggregate; top per category; top creativity; top execution_claimed; top leverage;
advance=yes; sparse-description-strong-signal; low-confidence-but-interesting;
random control sample (25).

## Stage 2 — observed-product review (Luna reviewers + deterministic probe)
Deterministic probe per funnel project (scripts/probe_demo.py): load demo URL in
agent-browser, wait, screenshot to probes/<slug>.png, extract page title, detect login
wall keywords, record HTTP/dead status. LIVE probe is theEXECUTION_OBSERVED backbone.
S2 reviewers rescore execution_observed_1_10 + usability_1_10 with probe results in view;
update advance for finalists pool (~60).

## Stage 3 — finalist deep-dive + control comparison (Nicholai + adjudicator)
Full video review, repo history check (HACKATHON_NEW vs PRE_EXISTING boundary),
novelty analysis (closest existing product, what changed). THEN un-quarantine
HanClinto: compute agreement, dramatic movers, and whether description-only missed
category leaders.

## Deliverable
Google Sheet on the biohazardvfx account + local CSV:
all 2500 ranked with columns above + screenshot link + HanClinto deltas appended last.
