# CALIBRATION.md — common-core anchors with ADJUDICATED expected ranges
Written by the orchestrator BEFORE any reviewer ran, from packet evidence only
(Devpost text, video transcript, repo existence). Ranges are my adjudicated guesses
and are deliberately stated with reasoning; they exist to detect reviewer drift, not
to override reviewers. A reviewer whose common-core mean falls outside these ranges
on 3+ anchors is flagged for re-review of their affected batch.

Selection (deterministic, from evidence_count in slice_batches.py):
- 12 weakest evidence_count (expected mostly low scores — thin products OR hidden gems)
- 12 around the median (expected mid clusters)
- 12 strongest evidence_count (expected high execution-claimed, varied leverage)
- 4 wildcard slugs picked by hash for category spread

Anchor packet = same sanitized packets reviewers see. Adjudicated ranges below are
assigned per anchor slug AFTER listing them, from my read of their packets.
