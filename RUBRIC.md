# FROZEN SCORING RUBRIC (pre-registered before any Stage 1 review)

Scores are integers 1-10 on each of the FOUR official criteria. Every score carries:
rationale, evidence_surfaces, confidence (0-1). Reviewers use the full scale and these
band anchors verbatim. Category neutrality is absolute: a game, art piece, music tool,
CRM, weird toy, and developer tool are all eligible for 10/10 on every criterion if they
satisfy that criterion exceptionally well FOR WHAT THEY ARE TRYING TO BE.
No aesthetic penalties. Signs of hurried AI work matter only as actual product-quality
problems (incoherence, broken flow, placeholder content), never as style.

## WebMCP Leverage — what does WebMCP change for this product?
Judge the delta WebMCP makes to reliability, precision, structured state access,
shared human-agent state, repeatability, and capability. Tool COUNT is not leverage.
- 9-10 TRANSFORMATIVE: the intended experience is impractical without the structured
  agent surface; human and agent share live product state; the collaboration could not
  be replicated comparably well by a general agent driving the UI.
- 7-8 MAJOR DELTA: without WebMCP a general agent is markedly less reliable/precise
  here; the agent is central to the product, not a bolt-on.
- 5-6 MEANINGFUL DELTA: existing capability packaged into a genuinely better product
  experience via structured tools; same outcome otherwise possible with real friction.
- 3-4 MINOR DELTA: generic browser automation achieves comparable outcomes; WebMCP is
  a convenience layer.
- 1-2 COSMETIC: exposes an action a UI button already offers; no meaningful change.

## Execution — is the actual product coherent, intentional, complete for its scope?
Stage 1 scores EXECUTION_CLAIMED: coherence/intentionality/completeness as evidenced by
the packet (description + packaging + video frames/transcript). Thin evidence caps the
score (end-to-end credit requires end-to-end evidence) and lowers confidence.
Stage 2 may rescore as EXECUTION_OBSERVED; latest evidence-backed score replaces, never
sums.
- 9-10: all surfaces agree; central workflow demonstrably completes; states handled;
  feels finished for its stated scope.
- 7-8: strong coherence and intentionality; central workflow appears functional; minor
  unfinished edges.
- 5-6: plausibly real with visible gaps; scope unclear or core not demonstrated
  end-to-end.
- 3-4: thin prototype; contradictions between surfaces; placeholder content.
- 1-2: non-functional or incoherent for its claimed scope.

## Creativity & Ambition — novelty of concept and interaction model
Judge ONLY: novelty of the concept, novelty of the interaction model, originality
relative to existing concepts, ambition, memorable/surprising use of the medium, and
the depth with which the concept is pursued. WebMCP indispensability belongs under
WebMCP Leverage, NOT here: a project can be extremely creative even if another agent
API could theoretically have enabled something similar.
- 9-10: genuinely novel concept or interaction model; ambitious scope pursued deeply
  and coherently; memorable.
- 7-8: fresh synthesis or notably original interaction; ambitious for a hackathon.
- 5-6: competent take on a known category with a real new angle.
- 3-4: derivative; novelty mostly surface details.
- 1-2: clone/template with trivial changes.
"That the category exists" is never a penalty; judge the submitted concept.

## Potential Impact — credible value for the intended audience
Judge: is there a real audience; is there a real problem, desire, or use case for that
audience; does the demonstrated solution genuinely address it. NO commercial adoption,
monetization, market pull, or startup viability is required. Entertainment, play, art,
creative expression, learning, niche hobby use, experimentation, and community value
are legitimate forms of impact. A tiny audience fully justifies a top score.
- 9-10: specific real audience with a real problem/desire; solution demonstrably
  addresses it; credible value, appeal, usefulness, or meaning for that audience.
- 7-8: clear audience and problem, good fit, credible value.
- 5-6: identifiable audience, looser fit or partial address.
- 3-4: speculative audience or strained fit; impact mostly aspirational.
- 1-2: no coherent audience/problem pairing.
Audience size is NOT a multiplier.

## Aggregate & ranking
aggregate = leverage + execution + impact + creativity (4-40). Nothing else enters.
Tie-breaks: Leverage, then Execution, then Impact, then Creativity, then higher
combined evidence confidence, then slug alphabetical. See PROTOCOL.md Ranking section.
