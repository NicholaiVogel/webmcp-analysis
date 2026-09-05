# CALIBRATION.md — adjudicated expected ranges (PRE-REGISTERED 2026-09-05, before any reviewer output)

Written by the orchestrator from the 12 sanitized common-core packets only. Ranges are
the adjudicator's expected per-criterion scores ±1. A reviewer whose mean deviation from
these ranges exceeds 1.5 points on 3+ anchors is DRIFT-FLAGGED → their affected batches
are re-reviewed. Calibration never normalizes scores mechanically.

Anchor-specific checks:
- blnq-studio: the submitted video is a Rick Astley track (rickroll). A reviewer who
  returns video evidence proves_product=yes/agent_invokes_tools=yes for blnq-studio has
  NOT viewed the frames — automatic drift flag for that reviewer.
- autolab-by-automoto: 49 tool registrations. A reviewer citing tool COUNT as the basis
  for a Leverage score >= 8 without judging what WebMCP changes is drift-flagged (RUBRIC:
  tool count is not leverage).
- excel-master + arrowgram: sparse/absent about text. Reviewers must score
  execution_claimed from available evidence and cap confidence, not invent detail.

## Common core (12) — expected ranges [Leverage, Execution, Impact, Creativity]

1. arrowgram-lastrevision-pro — [1-3, 1-3, 1-2, 1-3]
   Link-spam pitch (three promo domains), no repo, no video, no demo verification,
   boilerplate about text. Weak on every axis; possibly ineligible.

2. excel-master — [4-7, 3-6, 5-7, 3-5]
   Sparse but real: in-browser excel/csv editing exposed to agents; live demo + repo,
   no video. High substitution pressure (generic agents edit files) → mid leverage;
   thin evidence caps execution_claimed; broad real audience → solid impact.

3. live-layer (Live Canvas) — [4-7, 2-5, 4-6, 6-9]
   Concept-forward (BYO-UI, adaptive interfaces), zero product evidence (no repo/video/
   demo check). Creativity carries it; execution_claimed must be low without evidence.

4. agent-market-agents-negotiate-you-confirm — [6-9, 4-7, 5-8, 7-9]
   Agent-to-agent haggle with human confirmation: WebMCP-native, structured negotiation
   is hard to fake generically; repo + gallery, no video → mid execution evidence.

5. blnq-studio — [6-8, 4-7, 5-7, 5-7]
   Real idea (editor+preview+WCAG audit in one agent-visible loop), live demo; video is
   a rickroll (see anchor check); no repo. Wide execution range pending S2.

6. svgent-agent-stage — [6-8, 7-9, 5-7, 6-8]
   Fictional agent-session studio for docs/READMEs (no secret leakage, re-shootable);
   repo + live demo + real 170s video + 3 sheets. Strong execution evidence.

7. quorum-awbqyk — [5-8, 3-6, 5-7, 6-8]
   Multi-party agent scheduling negotiation with visible logging; 5 gallery images,
   no repo/video. Genuine WebMCP-native interaction; substitution pressure from plain
   text scheduling keeps leverage mid; thin product evidence caps execution.

8. agentready-network — [7-9, 4-7, 6-8, 7-9]
   User-side WebMCP adoption for un-instrumented sites ("login as API"), with measured
   grounding (522k LOC audited, 0 WebMCP registrations). High leverage + creativity IF
   real; live demo + repo, no video → execution range stays wide.

9. unfolded — [6-8, 6-8, 4-6, 7-9]
   3D→printable clay templates; deterministic geometry export solves a real AI-output
   problem; 15 gallery images + 179s video + live demo (no repo). Niche but genuine
   audience (makers/craft) — impact mid NOT low.

10. zingposts — [5-7, 6-8, 5-7, 5-7]
    WebMCP-native marketplace with deal workspace; repo + live + 165s video. Solid,
    legible, moderately novel; marketplace substitution pressure keeps leverage mid.

11. docket-lens — [5-7, 3-6, 6-8, 5-7]
    Regulations.gov evidence board with traceable citations; civic/research audience
    is real; no repo/video/demo verification → thin execution evidence, impact carries.

12. autolab-by-automoto — [4-7, 4-7, 5-7, 4-6]
    49 tool registrations across 5 contexts (see anchor check: count ≠ leverage);
    repo + configurator concept; execution evidence mid; creativity moderate unless
    the sheets show something surprising.

## Rotated anchors (28)
Selected to span the same axes (length buckets × video × repo presence). Adjudicated
ranges are NOT pre-registered for rotated anchors (orchestrator has not read them);
their role is cross-reviewer variance estimation only. Common-core ranges carry the
drift decision.
