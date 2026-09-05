# Correctness and Fairness Audit

## Audit scope

Target: `/mnt/work/webmcp-analysis/`

Audited revision: `8ec514019647573e13c48e04d6c61bd67934998e`

Audited state: current working tree, including generated analysis artifacts. The tree is not clean: `DEVIATIONS.md` and `VOLUME.md` are modified, and the generated `analysis/`, `raw/`, `probes/`, `screenshots/`, and `web/` trees are untracked. The findings below therefore describe the artifacts currently being used by the site, not only the committed source revision.

Materials inspected included the protocol, rubric, calibration and funnel documents; corpus construction, parsing, packetization, aggregation, validation, video, probing, and S2 scripts; S1/S2 artifacts; final ranking data; and the web data-loading/build path.

## Executive verdict

The project has a reasonable high-level design: frozen criteria, two blind Stage 1 reviews, evidence quarantine, calibration anchors, a separate interactive Stage 2, and explicit deviation notes. The current S1 packet cleanliness and per-file result schema checks pass.

The published result is not currently a valid implementation of that design.

The decisive defect is that the final ranking is grouped by evidence stage instead of being globally sorted by the documented aggregate. All 716 Stage 2 projects occupy ranks 1-716, and all 1,784 Stage 1-only projects occupy ranks 717-2500. This creates 731,223 cross-stage ordering inversions. For example, a Stage 2 project with aggregate 4.0 is rank 716 while a Stage 1-only project with aggregate 34.5 is rank 717. The CSV, JSON, and web site all reproduce this ordering.

Fairness is also not established because the deeper evidence regime is outcome-selected rather than population-representative, video evidence is missing non-randomly by provider/access path, and the Stage 1 consolidation mishandles calibration overlays. These issues may have changed individual scores and funnel membership even where no intentional manipulation is indicated.

Recommendation: do not describe the current output as a correct final ranking. Rebuild the ranking and repair or explicitly quarantine the affected evidence before publication.

## Severity summary

| Severity | Finding | Classification |
|---|---|---|
| Blocker | Final ranking is stage-concatenated, not globally sorted | Confirmed correctness defect affecting every stage boundary and most positions |
| High | No reproducible, tracked final-ranking builder or adjudication record | Confirmed auditability and rerun defect |
| High | Video/provider metadata failure is converted into inconsistent evidence flags | Confirmed pipeline defect with likely differential impact |
| High | Audio/music projects can be penalized for unobservable sonic quality | Confirmed measurement-validity defect in the review instructions and rationales; category-wide score depression not established |
| High | Planned Stage 3 finalist review was not run | Confirmed scope shortfall affecting most projects |
| High | Stage 2 is selected from Stage 1 outcomes and only 716 projects receive deeper evidence | Methodological selection bias; documented deviation does not remove the bias |
| High | Calibration overlays are not consolidated as the intended two independent rounds | Confirmed aggregation defect affecting 40 calibration anchors |
| High | Generated S2 packets are not reproducible from the builder's current input paths | Confirmed provenance defect affecting all 1,432 packets |
| Medium | Observer output is not schema-validated and screenshot evidence is not linked reliably | Confirmed evidence-contract defect |
| Medium | Corpus construction silently retains missing pages and truncates long evidence | Confirmed unequal-evidence defect |
| Medium | Public counts and status language disagree with the artifacts | Confirmed disclosure/traceability defect |
| Low/Medium | Repository and liveness facts are available as diagnostics but no sensitivity analysis is published | Methodological risk, not proven as a score input |

## What is working

1. The source and reviewer corpus contain 2,500 unique project slugs. The reviewer corpus matches the source set.
2. The stated official aggregate is clear: the four criteria are equally weighted and summed, with no popularity, repository, video, or probe field supposed to enter the score directly.
3. The packet quarantine is meaningful. `scripts/assert_clean.py` scans for forbidden score/judgment fields and HanClinto-related markers. The current run returned:

   `CLEAN: 40 packets, 2500 projects, all assertions pass`

4. The 600 S1 result files contain 5,648 records covering 2,500 unique projects, with 300 files per round. `scripts/validate_results.py` reported zero schema problems for every S1 file.
5. Stage 2 rescoring contains 1,432 rows: two scorer rows for each of the 716 queued projects. The two scorer rows are structurally present for the queue.
6. The rubric correctly says that lack of proof should reduce confidence and that aesthetics, audience size, and tool count should not be direct score multipliers.
7. The current web build completes successfully and generates 2,504 pages. This verifies static buildability only; it does not verify ranking semantics.

These strengths are useful controls, but they do not compensate for the final-order defect or the evidence asymmetries below.

## Confirmed correctness and pipeline findings

### 1. Blocker: the final ranking violates its own global-sort rule

The protocol and funnel documents require the latest evidence-backed score per criterion, followed by a global descending aggregate sort and the documented tie-break order.

The current `analysis/final_ranking.json` and `analysis/site_data/final_ranking.json` instead have this structure:

- ranks 1-716: all 716 Stage 2 projects;
- ranks 717-2500: all 1,784 Stage 1-only projects.

Measured consequences:

- 731,223 pairs are inverted across the Stage 2/Stage 1-only boundary: a later Stage 1-only project has a higher aggregate than an earlier Stage 2 project.
- 647 of 716 Stage 2 rows have at least one higher-scoring Stage 1-only row below them.
- Rank 716 is `recipe-radar-28hsig`, Stage 2, aggregate 4.0.
- Rank 717 is `faultline-s9f81w`, Stage 1-only, aggregate 34.5.
- 2,435 of 2,500 positions differ from a global sort by aggregate, Leverage, Execution, Impact, Creativity, and slug.
- Mean absolute displacement is 593 positions; maximum displacement is 1,782 positions.

This is not a cosmetic display problem. The same bad order is present in the final CSV, internal JSON, site data, and public rankings data. `web/src/data/load-projects.ts` explicitly treats the artifact rank as authoritative and does not re-sort. `web/src/data/schema.ts` contains a comparator consistent with the protocol, but that comparator is not used to repair or validate the final artifact.

Impact: a project’s rank is determined partly by whether it entered Stage 2, not only by its score. A lower-scoring Stage 2 project can outrank a substantially higher-scoring Stage 1-only project. The unchanged top three, if true, do not mitigate corruption of the rest of the ranking.

Required repair:

- Build one canonical score record per project.
- Use Stage 2 scores only where valid Stage 2 scoring exists; otherwise use Stage 1 scores, with an explicit stage field.
- Apply one global comparator after score selection.
- Add a fail-closed assertion that the emitted order equals `sorted(records, key=protocol_key)` and that every adjacent aggregate is non-increasing.
- Regenerate every downstream CSV, JSON, and web data artifact from that builder.

### 2. High: the final result is not reproducible from tracked source

There is no tracked final-ranking builder in `scripts/`, and the final JSON/CSV/site-data artifacts are untracked generated files in the current tree. The web loader calls the generated site data the pipeline source of truth, but there is no checked-in transformation that proves how that file was constructed from S1, S2, adjudication, and deviation inputs.

The final artifact contains 8 rows labeled `adjudication: "mean-capped"`. No adjudication-named artifact or per-project adjudication record was found. A capped mean can be a documented fallback, but it is not an independent adjudication and should not be presented as one.

Impact: a reviewer cannot rerun or independently audit the exact final ranking, determine which rows were manually repaired, or distinguish a deliberate decision from a one-off generation error.

Required repair:

- Commit the final builder and its input manifest.
- Record the audited commit, source hashes, generation parameters, score-selection rule, adjudication decisions, and output hashes.
- Make missing adjudication evidence a hard failure rather than silently accepting a label.

### 3. High: Stage 1 calibration records are consolidated incorrectly

`scripts/slice_batches2.py` intentionally adds calibration overlays:

- 12 common-core projects to every slot in both rounds;
- 28 rotated anchors to three slots per round.

The resulting S1 result set has 5,648 records, which is consistent with 2,500 base assignments plus overlays in each of two rounds. The project documentation and some volume summaries still report 5,233 S1 judgments, so the documented volume is stale or describes a different run.

`scripts/combine_s1.py` stores records by slug and reviewer filename, then does:

- sort all reviewer filenames for a slug;
- select the first two records;
- ignore any remaining records.

All 40 calibration anchors have more than two records. Because filenames sort by `r1` before `r2`, the first two selected records for all 40 anchors come from the same round rather than one record from each intended independent round. One result file, `r2-0364.jsonl`, also contains the same slug twice; the aggregation structure can silently collapse duplicate records from the same reviewer file.

`assert_clean.py` passes because it checks only that projects do not have fewer than two appearances. It does not enforce the intended base/overlay assignment, one record per reviewer per project, one record per round for consolidation, or rejection of duplicate same-file records.

Impact: calibration anchors can have the wrong pair of scores, confidence, disagreement, and advance status. Those values feed provisional aggregates and funnel selection, so the bug can affect later-stage membership and not just calibration reporting.

Required repair:

- Persist an explicit assignment ID, round, slot, reviewer, and overlay/base role in every result.
- Deduplicate only with an explicit policy; never let a dictionary overwrite a record.
- Select the intended independent observations deterministically.
- Validate the full expected assignment matrix before combining.
- Recompute provisional scores, funnel membership, and all downstream stages.

There is also a consumer mismatch: the combiner selects two lexicographically first records, while the web provisional adapter keeps the first record it encounters per round. Those are different selection rules and are not a reliable shared source of truth.

#### Competing legacy batch path

The repository contains a second tracked slicer, `scripts/slice_batches.py`, with materially different behavior from `scripts/slice_batches2.py`. The legacy path selects calibration anchors using an `evidence_count` derived from demo liveness, GitHub presence, gallery count, video duration, and about-text length. That conflicts with the protocol's stated calibration rule that anchor selection must not use evidence count. It also emits `repo_stars` and `repo_pushed`, although the protocol permits repository existence/visibility facts only and says repository statistics are diagnostics, not score inputs.

The current `r1`/`r2` artifacts appear to follow the newer slicer, so this is primarily a reproducibility and latent-bias risk rather than proof that the current scores used those fields. Both generators are tracked, however, and there is no single canonical pipeline guard preventing the legacy path from producing a materially different reviewer corpus.

#### Weak fleet completion gate

`scripts/acpx_fleet.py` and `scripts/codex_fleet.py` count any JSON object containing a slug and `leverage` as valid output. They do not enforce full schema validity, expected prompt membership, unique project slugs, or one result per assigned project before reporting completion. `validate_results.py` can catch some malformed rows if run afterward, but the launcher itself can accept a duplicated project and an omitted project when the raw object count matches the expected count.

Impact: packet generation and fleet completion can silently create project-level undercoverage or duplicate reviewer evidence. This is an additional reason the final builder must validate assignment membership and uniqueness rather than trusting file counts.

### 4. High: video/provider coverage is incomplete and mapped inconsistently

The source CSV has 2,476 project video links:

- 2,418 YouTube links;
- 58 Vimeo links.

The extracted artifacts contain:

- 2,414 slug-to-video mappings;
- 2,400 unique mapped video IDs;
- 2,398 metadata rows;
- only 261 metadata rows with a non-empty duration;
- 1,897 frame directories with contact sheets.

Among source-linked projects:

- 62 have no entry in `raw/video_ids.json` (56 Vimeo and 6 YouTube-shaped links);
- 2 mapped IDs have no metadata row;
- 1,902 have frame sheets;
- 574 source-linked projects have no usable frame-sheet artifact.

The reviewer corpus defines `has_video` as `bool(video_meta.duration)`, not as “the submission contains a source video link” or “frames were successfully captured.” The current corpus therefore has:

- 262 projects with `has_video=true`;
- 1,640 projects with frame sheets present but `has_video=false`;
- 598 projects with neither a positive duration nor frame sheets.

The code path is also provider-specific: `video_meta.py` invokes YouTube extraction, and `keyframes2.py` uses a YouTube storyboard path. Vimeo links do not receive an equivalent provider-neutral treatment.

The recorded deviation is itself consequential: `DEVIATIONS.md` says 88 Devpost videos were missing from the source sheet, that affected projects were reviewed with `has_video=false`/unclear video evidence, and that the fix was applied only to future stages. Thus at least one documented capture failure was knowingly allowed to remain in finalized S1 evidence; the current artifact-level mismatch is broader than that documented 88-project gap.

Impact: evidence availability is correlated with provider, extractor behavior, and access conditions. Video-rich projects can be treated as if they supplied no video, while some projects receive frame evidence that the corpus flag says is absent. This directly affects what reviewers see and can affect Execution scores, confidence, funnel membership, and Stage 2 packet content. It is not safe to assume the missingness is random.

Required repair:

- Maintain a source-link manifest independent of extraction success.
- Separate `submitted_video`, `metadata_fetched`, `frames_fetched`, and `transcript_fetched` states.
- Add provider-specific extraction with explicit failure reasons and retries.
- Rebuild affected packets and rerun scores where the available evidence changes.
- Publish coverage by provider and stage before calling the ranking final.

#### Transcript propagation and presentation

A layered check distinguishes two different problems. `raw/video_meta.jsonl` contains 216 non-empty transcript excerpts, and all 216 are present in `analysis/reviewer_corpus.jsonl`; no loss was found at that raw-to-reviewer join. The transcript loss is downstream and the remaining availability is uneven:

- `web/src/data/adapters/reviewer-corpus.ts:8-22,30-50` defines and loads no `video_transcript_excerpt` field, so the web project's factual corpus model drops every captured transcript.
- `scripts/make_prompt.py:86` sends only the first 4,000 characters to reviewers. The reviewer corpus stores up to 6,000 characters and `video_meta.py` stores more, so long transcripts are silently suffix-truncated at prompt time.
- Only 326 of 1,432 generated S2 packet records contain transcript text; 1,106 are empty. This is not, by itself, proof that the 1,106 values were dropped downstream: many have no upstream transcript capture. It does prove that packet evidence is not labelled clearly enough to distinguish `not captured`, `captured but omitted`, and `captured and shown`.

Impact: if the observed missing transcripts are on the site or in the corpus projection, that loss is confirmed. If they are in the reviewer packets, the current evidence supports an upstream coverage problem plus prompt truncation, not a universal raw-to-packet deletion. In either case, reviewers and readers cannot reliably tell whether a transcript was absent from the submission or lost by the pipeline.

Required repair:

- Preserve `transcript_submitted`, `transcript_fetched`, `transcript_included`, source length, and a content hash at every stage.
- Keep the transcript in the web corpus model or explicitly label the site as a non-reviewer evidence projection.
- Do not silently truncate; include a visible truncation flag and a link/hash to the immutable full artifact.
- Rebuild and rerun affected reviews if packet-visible transcript evidence changes.

#### Audio/music-centered projects are exposed to a modality-inappropriate execution test

The rubric makes the four official criteria category-neutral and does not define audio quality as a separate score. `RUBRIC.md:25-29` nevertheless defines Stage 1 Execution around what is evidenced in the packet and says thin evidence caps the score and lowers confidence. `scripts/make_prompt.py:26-29` repeats that rule and `scripts/make_prompt.py:55-58` gives the reviewer a vision workflow for images, but provides no listening-capable evaluator or audio-specific exception. `CATEGORIES.md:8` explicitly includes `music-audio` as a project category.

The current S1 rationales contain explicit cases where reviewers say they cannot hear or otherwise verify audio/music quality. A project-level mechanism is therefore confirmed for confidence: evaluator modality limitations are being turned into execution uncertainty. The same evidence appears alongside execution scores and rationales, but the stored artifacts do not support a causal estimate of how many execution points were lost specifically to this issue. Examples include `analysis/results/r2-0491.jsonl:10` (“Agent cannot hear music and relies on proxy metrics”), `analysis/results/r1-0280.jsonl:8` (“central audio outcome is unverifiable in the packet”), `analysis/results/r1-0036.jsonl:9` (“Audio quality and full graph correctness are not independently measured”), and `analysis/results/r2-0435.jsonl:7` (“Audio quality ... [is] not directly verifiable from text-only packet evidence”). Eight of the 62 projects whose primary or secondary category includes `music-audio` have mean S1 execution confidence at or below 0.50:

| Project | Mean S1 execution confidence |
|---|---:|
| `agent-mcp-beats` | 0.450 |
| `beatforge` | 0.425 |
| `cognistration-webmcp` | 0.490 |
| `hands-on-the-keys` | 0.325 |
| `loopsmith` | 0.460 |
| `mixerx` | 0.415 |
| `mysynote` | 0.450 |
| `webpod` | 0.225 |

This should not be overstated as proof of a category-wide score penalty. Across the same category union, mean S1 execution is 7.229 versus 6.839 for all projects, and mean confidence is 0.744 versus 0.727 overall. The confirmed defect is narrower and more important for individual fairness: rationales and confidence can reflect “the evaluator cannot hear this” as if it were evidence against product quality, even though sonic quality is not an official metric and the evaluator lacks that modality.

The fair rule is not to give audio projects a free execution pass. Reviewers should score observable execution: workflow coherence, state transitions, WebMCP integration, scope completeness, and any audio behavior that is demonstrated through evidence they can actually evaluate. “Not heard” must not become “sounds bad” or an execution deduction. If sonic quality is material to the claim, route the project to a human/listening-capable evaluator or an explicitly defined objective audio test. Otherwise mark sonic quality `not assessable` and exclude it from both the score and the confidence penalty; apply the same modality rule to every category.

Required repair:

- Add a prompt rule distinguishing `not observed` from `observed deficient`; inability to hear is not negative evidence.
- Separate execution of the product workflow from sonic-quality assessment.
- Re-review the affected music/audio projects, including the eight low-confidence cases, with an audio-capable evaluator or a pre-registered objective proxy.
- Publish score/rank sensitivity with audio-related deductions removed, and report category-level results without treating aggregate means as proof of fairness.

### 5. High: the Stage 2 funnel changes the comparison population

The documented funnel selected 2,358 projects across overlapping lanes, including 2,186 `RESCUED` projects. After the rescue lane collapsed the intended selective funnel, the actual Stage 2 queue contains 716 projects; 1,542 selected projects are rescue-only and were excluded.

The 716 queue is made from top aggregate, category leaders, criterion leaders, disagreement/advance conflict, and a 60-project random-control lane. The 1,784 projects outside the queue retain Stage 1-only scores.

The written plan also specifies a Stage 3 finalist deep dive covering full video review, repository-history verification, novelty analysis, and runtime verification. `VOLUME.md` records that S3 was not run. Consequently, 1,784 projects received neither Stage 2 nor Stage 3 deep review, and the current ranking cannot support claims that all finalists received the planned evidence depth.

The random-control lane is not a population-wide random audit: `FUNNEL.md` defines it as 60 projects entering no other bucket. It samples only the residual pool after top-score, category, criterion, disagreement, and rescue filtering, so it cannot estimate false negatives across the full 2,500-project population. The category-leader rule is also structurally asymmetric: categories with at least 8 reviewed projects admit 10 leaders, while smaller categories admit only 3, with no uncertainty or population-size adjustment.

This decision is documented in `DEVIATIONS.md`, which is good disclosure, but it does not remove the statistical consequence:

- Stage 2 evidence is assigned using Stage 1 scores, disagreement, and advance outcomes.
- Deeper measurement is therefore not a random sample of the 2,500 projects.
- The 60-project random control is not used as a population correction or stage-effect estimate.
- There is no published sensitivity analysis showing how much the rankings change under equal evidence, Stage 1-only, or a random Stage 2 sample.

Impact: the final score is a mixture of two measurement regimes. Stage 2 projects receive an interactive observer and two rescoring judgments, while most projects retain packet-only claimed execution. Even though the protocol says authentication should not be a penalty, live accessibility, login gates, timeouts, and demo complexity still determine how much evidence is observable. This can create selection and collider bias.

Required repair:

- Either score all projects under one evidence regime, or explicitly model/calibrate the stage effect.
- Add a random audit sample across all 2,500 projects, not only a control lane that is not used analytically.
- Report rank sensitivity and score distributions by stage, access state, provider, and evidence coverage.
- Do not use a mixed-stage artifact as a single definitive ranking without this analysis.

### 6. Medium: S2 observer data does not satisfy its own evidence contract

The observer template requires `identifiable_purpose` to be boolean `true`/`false` or `partial`. The current observer data contains 717 rows for 717 unique slugs, but 122 rows use invalid values such as string `yes`, string `false`, string `true`, or `unclear`.

The observer data also has one row outside the 716-project queue. `build_s2_packets.py` catches JSON parsing errors, selects the first observation with `obs.get(slug, [{}])[0]`, substitutes a synthetic `reachable=false` observation when none is found, and does not validate the observer schema before packet creation.

The observer template instructs testers to save before/after screenshots, but the JSON schema has no screenshot-path field. The rescore template refers to paths “noted inside the observation’s screenshots, if any”; the generated `live_observation` objects do not reliably contain those paths.

Current screenshot inventory:

- 1,308 observer screenshot files;
- 689 before files;
- 614 after files;
- 614 complete before/after pairs;
- 0 of 1,432 generated S2 packets contain a structured screenshot-path field;
- only 548 of the 716 queued projects have a complete pair;
- 168 queued projects have no complete pair.

The planned per-project deterministic probe was not completed: only 16 probe results are present for a 716-project S2 queue, and those 16 rows contain only 15 unique slugs because `seriessafe` appears twice. `build_s2_packets.py` includes `probe_triage.verdict` and its title in the rescoring packet even though the protocol describes probing as triage-only. The prompt does not add a hard machine-enforced prohibition on using that visible verdict in scoring. `probe_demo.py` also classifies generic first-3,000-character strings such as “API key,” “password,” “sign up,” and “get started free” as login markers without proving that an authentication gate blocks the workflow. This creates a false-login-wall path for otherwise public documentation, developer, and security products.

Impact: the two Stage 2 scorers are told to use evidence that is not represented in the structured observation record and is missing for a substantial part of the queue. Scorers may therefore have different effective evidence access. The two scorers also share one observer’s single attempted action, so they are not independent replications of the live workflow.

#### S2 packet provenance and independence

The tracked packet builder reads observations only from `analysis/results/obs-*.jsonl`. That path currently contains zero files. The actual 121 observer files are under `analysis/results/s2/obs-*.jsonl`. Nevertheless, all 1,432 generated S2 packets contain non-empty `live_observation` objects. Re-running the tracked builder from the current inputs would therefore substitute its synthetic `reachable=false` fallback rather than reproduce the packets being scored. This is a provenance failure, not merely a missing-file warning.

All 716 generated `a`/`b` packet pairs are byte-identical. Identical evidence can be valid for two independent scorers, but the repository does not record isolated run IDs, immutable source hashes, or controls proving that the scoring processes were independent. The packet builder also does not record the observation ID that produced each packet.

Required repair:

- Validate observer JSON against a strict schema before packet generation.
- Reject invalid enums, extra rows, missing rows, and duplicate slugs.
- Store exact screenshot paths in the observation object and verify every path exists.
- Make the packet builder fail closed on any missing required evidence.
- Use independent observers or quantify the dependence created by one shared observation.

### 7. Medium: missing pages and long-text truncation are silently retained

`raw/parsed.jsonl` has 2,498 rows for a 2,500-project source set. Two source projects have no parsed page/about artifact. `build_corpus.py` still emits both projects by defaulting missing parsed data to empty fields.

The corpus truncates about text at 24,000 characters; the reviewer corpus truncates it at 9,000 characters. Nine corpus records hit the 24,000-character cap, and 494 reviewer records are exactly at the 9,000-character cap.

Impact: the affected projects do not receive equivalent evidence. A missing page can become a low-information packet rather than a missing-data failure, and long submissions are disproportionately compressed. The rubric may correctly lower confidence for thin evidence, but the pipeline should distinguish “the project supplied little evidence” from “the pipeline failed to capture evidence.”

Required repair:

- Preserve explicit `page_fetch_status`, `parse_status`, and `truncation` fields.
- Fail or quarantine missing source pages instead of silently filling empty strings.
- Preserve full evidence in immutable artifacts and generate a reviewer projection with a visible truncation flag.
- Re-score affected projects if the evidence projection changes.

### 8. Medium: public status and counts are stale

The artifacts currently contain 2,500 final rows, 716 Stage 2 rows, and 217 `VERIFIED_RUNTIME` rows. The 1,784 S1-only rows have no explicit verification field, so “not Stage 2” and “no evidence” are conflated. `web/src/components/format.ts` still declares:

- `RANKED: '2,492'`;
- `S2: '708'`;
- `VERIFIED: '216'`.

The home, explore, and about pages also contain stale 2,492-ranked copy. `DEVIATIONS.md` and `VOLUME.md` describe the ranking/video state as provisional or stale, while the site presents a final consolidated ranking.

The volume prose has a separate schema error: README/VOLUME describe S2 values as means of two independent reviewers, but `s2_aggregate` is the sum of the four criterion scores. For example, 10 + 9 + 9 + 10 is stored as 38.0; the four-criterion arithmetic mean is 9.5. The documented total of 7,381 records also differs from the 7,797 stored-record count obtained by adding 5,648 S1 batch records, 717 observer rows, and 1,432 S2 rescore rows.

Impact: users cannot tell which scope and evidence state they are viewing. Stale counts are especially harmful here because the difference between 2,492 and 2,500, and between 708 and 716, is part of the auditability story.

Required repair:

- Generate all displayed totals from the same validated manifest as the ranking.
- Remove hardcoded stage counts.
- Make “final,” “provisional,” and “video rerun pending” mutually consistent across docs and site.
- Add a data-contract test that compares rendered counts with artifact counts.

### 9. Medium: displayed confidence is not the confidence of the displayed score

The web model keeps the Stage 1 provisional confidence while displaying the final Stage 2 score where one exists. The page-level confidence description therefore refers to the mean of the two Stage 1 blind reviews even when the score shown is a Stage 2 rescore.

Impact: users may interpret confidence as uncertainty for the displayed final score when it actually describes a different measurement stage. This is a traceability defect even if it does not change the numeric rank.

Required repair: carry stage-specific criterion confidence through final consolidation, define the final confidence rule, and label it by stage.

## Methodological risks that need sensitivity analysis

These are not all proven numeric defects, but they are plausible unfairness channels that the current artifacts do not rule out.

1. Mixed execution measurement: packet-based claimed execution at Stage 1 is not automatically comparable with observed execution at Stage 2. A six-minute, one-action cap can favor simple, quickly reachable demos over complex workflows.
2. Access asymmetry: login walls, regional/network failures, security challenges, redirects, privacy restrictions, and missing credentials determine observable evidence. “Do not penalize authentication” is not enough if inaccessible projects receive less execution evidence and lower confidence.
3. Selection on reviewer outcomes: using advance, disagreement, and Stage 1 scores to choose who gets more evidence can amplify early reviewer noise.
4. Calibration auditability: the calibration design is sensible, but there is no single checked-in artifact showing drift results, thresholds applied, or a re-review decision after the incorrect anchor consolidation.
5. Diagnostic metadata: repository archive state, liveness, gallery count, and similar facts are included as evidence/diagnostics. The protocol says they are not score inputs, but a score-provenance or sensitivity report is needed to demonstrate that they did not become hidden quality proxies through reviewer narratives or lane selection.
6. Final score fallback: the eight mean-capped cases need explicit evidence and a reproducible decision rule. Otherwise the fallback can introduce discretionary treatment precisely at disagreement boundaries.
7. Repair/re-review volume: `VOLUME.md` records repair-labeled units, but no checked-in analysis links repairs to projects, categories, evidence conditions, or reviewer types. Additional review can improve a project or expose it to a different failure mode; the direction cannot be inferred without project-level before/after comparisons.
8. Calibration interpretation: `CALIBRATION.md` says common-core expected ranges were authored from an adjudicated read, while the 28 rotated anchors have no pre-registered ranges. That can anchor reviewers toward one interpretation and leaves drift for most anchors less auditable. This is a design risk, not proof of a score shift.
9. Probe and access confounding: even a correctly implemented probe can make “reachable quickly in this environment” correlate with execution evidence. Probe status should therefore be reported separately from product quality and excluded from scoring decisions.
10. Identity blinding is incomplete: reviewer prompts print the project slug, title, Devpost URL, video title/transcript, and public evidence URLs. Prior judgments are quarantined, but recognizable project, creator, domain, or hosting identity remains visible and can produce reputation or name effects.
11. Category auditability is incomplete: category assignments appear in provisional reviewer outputs but are not preserved in the authoritative final ranking. Without the frozen category, denominators, and per-category advancement rates, the category-leader fairness rule cannot be independently reconstructed.
12. Overlapping lanes create unequal inclusion opportunities: projects can qualify through several top-score, category, disagreement, rescue, confidence, sparse, and control rules. No inclusion-probability or lane-level sensitivity analysis is published, so the union is not an interpretable random sample.

## Verification performed

The following checks were run against the current working tree:

- `python3 scripts/assert_clean.py`
  - Passed: `CLEAN: 40 packets, 2500 projects, all assertions pass`.
- `python3 scripts/validate_results.py analysis/results/r1-*.jsonl analysis/results/r2-*.jsonl`
  - Passed: every result file reported 0 problems.
- Corpus/artifact count and uniqueness checks
  - 2,500 source rows;
  - 2,500 corpus rows;
  - 2,500 reviewer-corpus rows;
  - 2,500 provisional rows;
  - 2,500 final rows;
  - 2,500 site-data rows.
- Final-order checks
  - 716 Stage 2 plus 1,784 Stage 1-only rows;
  - 731,223 cross-stage inversions;
  - 2,435 positions different from a global score sort.
- S1 checks
  - 600 result files;
  - 5,648 result records;
  - 2,500 unique slugs;
  - per-round multiplicity distribution: 2,460 projects appear once, 28 appear 4 times, and 12 appear 21 times;
  - 40 calibration anchors selected from same-round records by the current combiner;
  - one same-file duplicate slug found in `r2-0364.jsonl`.
- Video/evidence checks
  - 2,476 source video links: 2,418 YouTube and 58 Vimeo;
  - 62 source-linked slugs absent from the video-ID map;
  - 261 metadata rows with a non-empty duration;
  - 1,897 frame directories with contact sheets;
  - 1,640 reviewer-corpus rows with frames but `has_video=false`.
- Transcript checks
  - 216 non-empty transcripts in `raw/video_meta.jsonl`;
  - all 216 present in `analysis/reviewer_corpus.jsonl`;
  - reviewer-corpus web adapter exposes 0 transcript fields;
  - 326 of 1,432 S2 packet records contain transcript text;
  - reviewer prompt truncates the transcript excerpt to 4,000 characters.
- Audio/music fairness checks
  - 62 projects have `music-audio` as primary or secondary category;
  - 8 have current combined mean S1 execution confidence at or below 0.50;
  - 2 have overall provisional `confidence_mean` at or below 0.50;
  - current category-level means do not prove a broad score depression, but S1 rationales explicitly contain inability-to-hear/verify reasoning.
- S2 checks
  - 716 queue projects;
  - 1,432 rescore rows;
  - 717 observer rows;
  - 122 invalid `identifiable_purpose` values;
  - one observer row outside the queue;
  - 16 probe results for the 716-project queue;
  - 548 queued projects with complete before/after observer screenshot pairs.
- Volume reconciliation
  - stored S1 batch records + observer rows + S2 rescore rows: 5,648 + 717 + 1,432 = 7,797;
  - documented total in README/VOLUME: 7,381.
- Web build
  - `npm run build` passed;
  - 2,504 static pages generated.

The passing structural checks should not be read as a clean bill of health. The current validators do not assert global final ordering, exact S1 assignment semantics, observer schema validity, screenshot completeness, provider-neutral video coverage, or final-artifact reproducibility.

## Minimum release gate

Do not publish a corrected “final ranking” until all of the following pass:

1. A tracked builder emits exactly 2,500 unique rows from a documented input manifest.
2. The emitted order equals the protocol comparator, with a hard failure on any adjacent ordering violation.
3. Every score has a traceable source stage, reviewer set, evidence manifest, and confidence definition.
4. S1 assignments have explicit round/reviewer identities, no same-file duplicates, and validated base/overlay expectations.
5. Video status distinguishes source submission from successful metadata, transcript, and frame extraction, with provider coverage reported.
6. Transcript projections preserve availability state, source length, truncation, and hash; the web and reviewer views agree on included evidence.
7. Audio/music claims are not penalized for unobservable sonic quality. Any sonic-quality judgment uses a listening-capable evaluator or a pre-registered objective proxy, and affected ranks have sensitivity results.
8. S2 queue, observer rows, scorer rows, and screenshot paths reconcile exactly and validate against strict schemas; rerunning the packet builder from the frozen manifest reproduces byte-identical packets with source hashes.
9. Probe attempts are uniquely identified and reconciled to the queue; duplicate slugs are either rejected or represented as explicit attempts.
10. Missing pages and truncation are explicit states, not silent empty/default values.
11. Any disagreement fallback has a stored decision record; “mean-capped” is not called adjudication unless an adjudication actually occurred.
12. Site totals, status labels, stage counts, and confidence labels are generated from the validated final manifest.
13. Sensitivity tables show the effect of stage, access state, video availability/provider, evidence completeness, and modality-specific evidence on scores and ranks.

Until then, the defensible description is: “a partially validated multi-stage evaluation with a provisional, currently invalid final ordering,” not an audited global ranking.
