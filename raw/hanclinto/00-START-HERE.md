# WebMCP Challenge Evaluation

Independent AI-assisted evaluation prepared September 5, 2026, published at HanClinto's request. Not official judging results or calibrated win probabilities.

## Start Here

- [Full report](#file-report-md): revised top ten, before/after comparison, alternatives and limitations.
- [Google Sheets: all project feedback](https://docs.google.com/spreadsheets/d/1iQJsfmEKkVyRQLloUvGw6j1-d5uKGtfqi4sdkMVO-Kw/edit?gid=0#gid=0): the spreadsheet copy supplied by the owner. This publication does not update or verify that copy's contents or permissions.
- [Detailed top-ten CSV](#file-top-10-csv): final scores, four final-score explanations, strengths, weaknesses, evidence level and comparison rationale. Use the Raw/download control for import into Sheets.
- [Finalist explanations](#file-finalist-details-md): the same detailed analysis in readable Markdown.
- [Scoring rubric](#file-rubric-md) and [quality audit](#file-quality-audit-md).

## How To Sort The All-Projects Sheet

**To browse the broad assessment of all 2,500 entries:** sort `description_score_out_of_100_NOT_OFFICIAL` **Z to A (largest first)**. Filter out blank scores when you want only scored entries; seven entries deliberately lack enough evidence for a full total. Do not treat blanks as zero.

For the official tie-break order, use **Data > Sort range > Advanced range sorting options**, select the entire table, and check **Data has header row**. Sort these columns in order, all **Z to A**:

1. `description_score_out_of_100_NOT_OFFICIAL`
2. `WebMCP Leverage`
3. `Execution`
4. `Potential Impact`
5. `Creativity & Ambition`

A simpler equivalent is to filter out blank ranks and sort `description_rank_SHARED_TIES` **A to Z (smallest first)**. Identical four-score tuples share a rank; alphabetical order inside those ties has no merit significance. Sort the whole table, never a single column in isolation, so comments stay attached to their projects. If Sheets treats scores as text, convert them to numeric values before sorting.

**To see the actual revised winner prediction:** use the top-ten CSV in this Gist, ordered by `rank_SHARED_TIES` **A to Z**. `display_order_NOT_TIEBREAK` only preserves presentation order within an exact tie.

**To inspect the final comparison of 25 contenders:** in the all-projects sheet, filter `reconciled_score_out_of_100_NOT_OFFICIAL` to nonblank and sort it **Z to A**. Read `comparative_reassessment` for why a score changed. For exact ordering use the numeric criterion arrays in [RECONCILIATION.json](#file-reconciliation-json) or the top-ten export; `reconciled_L_E_I_C` is display text, not a numeric sort key. Do not mix final reconciled scores for 25 entries with first-pass scores for everyone else into a purportedly uniform global ranking.

To find the original 46 source/live inventories, filter `prior_source_review` for the value beginning `prior source inventory`. Everyone now has description feedback; prior source checking remains a separate evidence level.

## Detailed Top-Ten Export

The four columns ending **final-score rationale** explain the actual reconciled category scores. They are not the earlier first-pass explanations relabeled as final. Additional columns contain strengths, weaknesses, comparison rationale, prior evidence, and description-review confidence. The companion JSON retains first-pass rationales separately for comparison. Confidence is not a numerical win probability.

The top-ten CSV was expanded for this publication. An earlier CSV already imported into your Google Sheet will not acquire these new columns automatically; replace that tab's data by importing this version.

## Coverage And Limits

All 2,500 collected descriptions received individual AI-assisted review. There are 2,493 complete numeric totals, seven insufficient-evidence cases, a separate 20-entry semantic audit and a 25-candidate comparative pass. The earlier 46 source/live inventories are not 2,500 tested products. No new submitted test suites, videos or native WebMCP end-to-end workflows were run in the wider review. Source quotes were checked for literal presence, not factual truth. The audit found and corrected errors.

No timing penalties were applied after the owner's clarification about a 12-hour extension. Contest membership and eligibility remain unverified. The keyword search's 2,500-result cap is not a certified official entrant list. InfraTwin's Vimeo-only collected embed remains an unresolved YouTube-material caveat.

## Publication Scope

This Gist includes analyst-written summaries and focused exports, not scraped project descriptions, screenshot archives, copied repository code, or the complete local evidence collection. The full feedback spreadsheet is linked above. Source references in the audit point to pinned public repository snapshots. Links to unpublished local artifacts are explicitly labeled; they do not imply those artifacts are available in this Gist.
