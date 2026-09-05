# DESIGN BRIEF - WebMCP Analysis Results Site (durable identity, frozen)

Selected candidate: seed-02 attempt 2 'Archive of Evidence'
sha256: 2b37901126b88da410c317fef7c1cd23fb9ae98415491a44b1899431fb460853
Selected by user 2026-09-05 after parent visual review of all four candidates (see taste/ artifacts in run root).

## Emotional target
Calm confidence in an honest, inspectable ranking: a quiet technical publication that
trusts the reader with the machinery (two blind reviews, disagreement, provisional status)
instead of performing authority.

## Concept spine
An explorable publication of the independent WebMCP Challenge analysis. The masthead and
thesis hero carry the publication voice; the ranking ledger is the body of the work; every
score is an opening into reviewer reasoning. 'Read the score, then the reason.'

## Hierarchy and attention order
1. Masthead identity (WEBMCP slash FIELD NOTES wordmark, coral slash)
2. Thesis hero (3 short lines) + provisional status framing (Stage 1, two blind reviews, final ordering does not exist yet)
3. Ranking ledger: rank, title + REAL pitch, category, aggregate /40, four criterion scores (em-dash when null-by-disagreement), confidence
4. Controls (search, category, sort, disagreement filter) - quiet, below the hero
5. Project page carries the deep evidence (reviews side by side)

## Composition grammar
Wide editorial table on a centered max-width canvas (~1240px desktop), generous left/right
margins (24px mobile, 40-64px desktop); left alignment throughout; 8px spacing rhythm;
sections separated by whitespace first, countable rules only; alternating rgb(0 0 0 / 3%)
row fills group the ledger instead of rule grids; top ranks get richer treatment (rank
medallion, fuller pitch) WITHOUT card grids or highlight tints.

## Typography
One sans family: Inter Variable (self-hosted). Headings 500-600 (never 700-900), body 400,
labels/controls 500. Body 16-18px / 1.5-1.6 line-height, 55-68ch measure for prose. Sentence
case everywhere - NO uppercase chrome (nav, labels, table headers, buttons, status). Tabular
numbers for scores. Hierarchy through size and whitespace, not many weights (3-4 text styles
per screen). Mono allowed ONLY as the single technical voice for score slugs/category tokens,
never for prose.

## Palette (scandinavian-design neutral system)
Canvas #FFFFFF; primary ink #000000; secondary ink rgb(0 0 0 / 64%); metadata rung lifted to
rgb(0 0 0 / 56%) where it carries real reading content; border rgb(0 0 0 / 10%); strong border
rgb(0 0 0 / 18%); hover rgb(0 0 0 / 5%); selected rgb(0 0 0 / 9%). Single brand accent: coral
(masthead slash, provisional status marker, primary action only). Semantic states (disagreement
flag) keep a distinguishable non-neutral treatment. No tinted warm/cool neutrals, no gradients,
no decorative color. Charts: neutral ink + coral emphasis only.

## Material and surface language
Flat white surfaces; no shadows except behavior-evidencing elevation (barely visible, neutral);
restrained radii 6-10px on controls; no boxed cards in the ledger; rules countable per screen;
focus rings 2px; keyboard-operable everything.

## Media role
Real analysis artifacts are the visual material. Rankings page: ZERO images, zero eager loads.
Project pages: Devpost page captures (labeled 'Devpost page capture - packaging evidence, not
runtime proof') and submitted-video contact sheets (labeled as such), loaded lazily with
explicit dimensions via astro:assets. No fabricated raster, no decorative imagery.

## Motion role
Near-none: hover/press color transitions ~150ms ease; focus states instant; no entrance
animations; prefers-reduced-motion honored. Interactions must feel instant (search/filter/sort).

## Signature treatments
- The coral slash in the masthead (single identity gesture)
- 'Read the score, then the reason.' as the recurring epigraph linking rankings to evidence
- Provisional status chip present on every ranked surface
- NULL-not-zero as a visible principle (em-dash for missing, disagreement rows explicit)

## Explicit refusals and anti-patterns
- No dashboard-slop: no card grids, KPI tiles, gauge charts, decorative sparklines
- No uppercase chrome, no all-caps micro-labels, no lowercase chrome
- No warm/cream/tinted neutrals in chrome (white + alpha-black only)
- No unexplained highlight tints (the seed's lime top-two edge is rejected)
- No unexplained abbreviations: criterion names spelled out or on-visible-hover defined
- No hero so large that ranking rows fall below the fold on 1440x900 (table must enter the first viewport)
- Never render missing scores as zero; never present diagnostics as scores; never imply final ranking
- No eager images on the rankings page; no client-side analysis corpus dump
