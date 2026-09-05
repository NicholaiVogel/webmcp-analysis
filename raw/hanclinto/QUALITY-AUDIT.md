# Quality And Comparative Review

## Coverage

The full-description pass produced 2,500 individual AI assessments in 50 alphabetically grouped batches. Each record contains four scores/rationales, concrete strengths and weaknesses, a verdict, confidence, and source excerpts. Seven descriptions lack sufficient evidence for a complete total. Source-quote matching validates literal provenance, not truth or quality of reasoning.

The coordinator delegated the work with the user's explicit permission. Reviewers used one rubric, did not consult the old ranking, and were told not to execute submitted code or use dates. Two pilot batches preceded the larger assignment. One reviewer stopped after batch 003 because tool output appeared mismatched; a separately assigned reviewer completed batches 004-008. Final batch validation found all 2,500 unique entries exactly once.

## Semantic Sample

A separate reviewer compared 20 complete original articles/card texts to their assessments. This was a purposive high/lower-score sample, not a random sample and not a measured error rate for all 2,500.

| Batch | Higher-scored sample | Lower-scored sample |
|---|---|---|
| 001 | 0x1-expedition-vault | a-journey-together |
| 006 | asdf-co1jr6 | asterisk-4qs3ih |
| 012 | companion-5hrj83 | composable-consulting-company-website |
| 018 | finite-hxvgnd | flightclaims-instant-statutory-flight-compensation |
| 024 | kern | karimovservice |
| 030 | no-seat-without-a-route | notenova-ai-powered-learning-assistant |
| 036 | recall-me-maybe | real-me-deepmatch |
| 042 | spotcheck-usdp21 | stadtoskop-webmcp |
| 048 | vouchsafe-m3xziq | voice-enable-pizza-app |
| 050 | wellauth | what-should-i-click |

The sample found two definite factual errors: a correct compute multiplication was criticized as wrong in Asterisk, and explicit shared-state card text was overlooked in A Journey Together. Companion also needed a narrower statement about which inferred relations are excluded from retrieval. These are corrected in the published ledger and Markdown scorecards by exact-match transformations in corrections.json (local artifact, not included in this Gist). Original reviewer records remain intact for audit. No score change was required solely by those corrections; the other stated evidence gaps still support their provisional bands.

No date penalty or materially nonindividual substantive feedback was found in those 20. No null-valued assessment was in the sample, so it does not independently validate the seven unscored records. No further definite factual contradiction was found in the remaining sampled scorecards. This is not a certification that the other 2,480 records are error-free.

## Finalist Reconciliation

Two comparative reviewers read the full descriptions and scorecards of 24 candidates: nine of the original ten (all except Alza), plus Groundplan, Spatialize, Gallery 402, Interleave, InfraTwin, Deputy, LASSO, Threshold, Vouchsafe, Warrant, WebMCP Computer, WebMCP Foundry, Swagger UI WebMCP, Guild, and Paradox. The coordinator then read Alza's complete saved description and prior evidence to bring the comparison to 25, including all original ten. They evaluated delivered scope, substantive mechanisms, reported validation, and future work. Targeted read-only source inspection was used where snapshots already existed. No submitted build, tests, live exploit, or native WebMCP run was performed.

The second-stage scores deliberately differ from first-pass scores. They are calibrated comparative judgments using richer context, not new evidence that each product improved or regressed. Batch averages range from 68.5 to 76.375. This variation conflates project composition and reviewer severity; no statistical normalization was applied because it would assume equal underlying batch quality. Exact score ties remain ties; small gaps are not reliable probability differences.

Additional wording corrections qualify Roque Nights' astronomical verification, Roadway's pre-existing kernel and interoperability evidence, Groundplan's configurable approval, and Gallery 402's distinct mainnet/testnet evidence. See corrections.json (local artifact, not included in this Gist).

## Source-Level Concern: Deputy

The captured source has a consequential alternate authorization path:

- [Authorization route](https://github.com/priteshvirat24/Deputy/blob/ed77597aef7e247ad222cb09e242e7a08b8e369a/apps/server/src/routes/authorizations.ts#L10) validates a caller-provided authorization record, checks tool existence, and stores the record.
- [Authorization schema](https://github.com/priteshvirat24/Deputy/blob/ed77597aef7e247ad222cb09e242e7a08b8e369a/packages/schemas/src/authorization.schema.ts#L42) permits status AUTHORIZED and makes the WebAuthn assertion optional.
- [Authorization verifier](https://github.com/priteshvirat24/Deputy/blob/ed77597aef7e247ad222cb09e242e7a08b8e369a/packages/security/src/authorization-verifier.ts#L20) checks record status, tool/version, argument digest, expiration, revocation, and optional nonce consumption, but does not verify a passkey assertion.

The coordinator independently read these three files after the comparative reviewer flagged them. This supports concern that the separate passkey flow is not a mandatory boundary on every authorization path in the snapshot. The reviewer also found no principal-authentication middleware on the mounted route and process-local nonce consumption on the inspected execution path. Deployment-level restrictions or later fixes could change exposure. No remote exploit was attempted, and this is not a claim that all deployments are exploitable. The source concern is reflected separately in the reconciled assessment, not silently rewritten into the description-only score.

## Remaining Limits

Every entry now has substantive individual feedback, but this is an AI-assisted description review, not 2,500 independently tested applications or 2,500 human expert judgments. Source verification remains uneven. Detailed and fluent write-ups can still receive more credit than equally strong products with sparse submissions. Reported test counts, native demos, scientific accuracy and user impact need independent verification. Duplicates and related submissions were assessed separately, not combined or disqualified.

Public start/update dates were not used. The user reports a 12-hour deadline extension; no exact new cutoff was inferred or independently certified. The prior report's timing-based selection concerns are superseded.